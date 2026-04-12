"""
Library Health Check System
Analyzes audio files for quality, integrity, and consistency
"""
import os
import subprocess
import shutil
from .lufs_analyzer import LUFSAnalyzer
import soundfile as sf


class HealthAnalyzer:
    """Comprehensive audio health analysis"""

    def __init__(self):
        self.lufs_analyzer = LUFSAnalyzer()
        self.ffmpeg_path = shutil.which('ffmpeg') or 'ffmpeg'

    def analyze_track_health(self, file_path):
        issues = []
        score = 100

        # 1. LUFS Analysis
        lufs_data = self.lufs_analyzer.measure_lufs(file_path)
        if not lufs_data:
            return self._error_result("Analysis failed")

        lufs = lufs_data['lufs']
        lra  = lufs_data.get('lra', 0)

        # 2. Measure TRUE output peak using ebur128 — reads actual output samples
        # loudnorm's input_tp reports the INPUT peak before normalization,
        # so it always shows the original peak even on a processed file.
        # ebur128 with peak=true measures the actual sample peak of the file.
        peak = self._measure_true_peak(file_path)

        # 3. Check for clipping — use actual measured peak
        if peak >= 0.0:
            issues.append("clipping")
            score -= 30
        elif peak > -0.5:
            issues.append("near_clipping")
            score -= 15
        elif peak < -3.0:
            issues.append("low_peak")
            score -= 15

        # 4. Check LUFS consistency
        if lufs <= -20:
            issues.append("too_quiet")
            score -= 20
        elif lufs > -6:
            issues.append("too_loud")
            score -= 15

        # 5. Check dynamic range (LRA)
        # Threshold raised from 3 to 2 — heavily mastered club/kompa tracks
        # naturally have LRA 2-4, penalizing them is misleading for DJs
        if lra < 2:
            issues.append("over_compressed")
            score -= 15
        elif lra > 15:
            issues.append("inconsistent_dynamics")
            score -= 10

        # 6. File quality check
        bitrate = None
        sample_rate = None
        try:
            info = sf.info(file_path)
            bitrate = self._estimate_bitrate(file_path, info)
            sample_rate = info.samplerate

            if bitrate and bitrate < 192:
                issues.append("low_bitrate")
                score -= 10

            if sample_rate < 44100:
                issues.append("low_sample_rate")
                score -= 10
        except Exception:
            issues.append("file_read_error")
            score -= 20

        # 7. Crest factor — threshold lowered from 4 to 2
        # Club/DJ tracks are intentionally compressed, crest factor 2-4 is normal
        crest_factor = self._calculate_crest_factor(lufs, peak)
        if crest_factor < 2:
            issues.append("low_crest_factor")
            score -= 10

        score = max(0, score)

        return {
            'health_score': score,
            'status': self._get_health_status(score),
            'issues': issues,
            'lufs': lufs,
            'peak': peak,
            'lra': lra,
            'crest_factor': round(crest_factor, 1),
            'bitrate': bitrate,
            'sample_rate': sample_rate
        }

    def _measure_true_peak(self, file_path):
        """
        Measure actual sample peak by reading the file directly with soundfile.
        This reads the actual output samples — guaranteed to reflect what's
        in the file regardless of how FFmpeg reports it.
        Returns peak in dBFS.
        """
        try:
            import numpy as np
            audio, sr = sf.read(file_path, dtype='float32')
            max_sample = float(np.max(np.abs(audio)))
            if max_sample <= 0:
                return -96.0
            return round(20 * np.log10(max_sample), 1)
        except Exception:
            # Fallback to loudnorm if file can't be read
            lufs_data = self.lufs_analyzer.measure_lufs(file_path)
            return lufs_data['peak_db'] if lufs_data else -1.0


    def _calculate_crest_factor(self, lufs, peak_db):
        rms_db = lufs + 3
        crest = peak_db - rms_db
        return max(0, crest)

    def _estimate_bitrate(self, file_path, info):
        try:
            file_size = os.path.getsize(file_path)
            duration = info.duration
            if duration > 0:
                return int((file_size * 8) / (duration * 1000))
        except Exception:
            pass
        return None

    def _get_health_status(self, score):
        if score >= 80: return "excellent"
        if score >= 60: return "good"
        if score >= 40: return "fair"
        return "poor"

    def _error_result(self, error_msg):
        return {
            'health_score': 0,
            'status': 'error',
            'issues': ['analysis_failed'],
            'error': error_msg
        }
