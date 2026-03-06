"""
Library Health Check System
Analyzes audio files for quality, integrity, and consistency
"""
import os
from .lufs_analyzer import LUFSAnalyzer
import soundfile as sf

class HealthAnalyzer:
    """Comprehensive audio health analysis"""
    
    def __init__(self):
        self.lufs_analyzer = LUFSAnalyzer()
    
    def analyze_track_health(self, file_path):
        """
        Comprehensive health analysis of a single track
        Returns health score (0-100) and detailed metrics
        """
        issues = []
        score = 100
        
        # 1. LUFS Analysis
        lufs_data = self.lufs_analyzer.measure_lufs(file_path)
        if not lufs_data:
            return self._error_result("Analysis failed")
        
        lufs = lufs_data['lufs']
        peak = lufs_data['peak_db']
        lra = lufs_data.get('lra', 0)
        
        # 2. Check for clipping
        if peak >= 0.0:
            issues.append("clipping")
            score -= 30
        elif peak > -0.5:
            issues.append("near_clipping")
            score -= 15
        elif peak < -3.0:
            # Peak is too low - track has too much headroom (not optimized)
            issues.append("low_peak")
            score -= 15
        
        # 3. Check LUFS consistency
        if lufs <= -20:
            issues.append("too_quiet")
            score -= 20
        elif lufs > -6:
            issues.append("too_loud")
            score -= 15
        
        # 4. Check dynamic range (LRA)
        if lra < 3:
            issues.append("over_compressed")
            score -= 15
        elif lra > 15:
            issues.append("inconsistent_dynamics")
            score -= 10
        
        # 5. File quality check
        try:
            info = sf.info(file_path)
            bitrate = self._estimate_bitrate(file_path, info)
            
            if bitrate and bitrate < 192:
                issues.append("low_bitrate")
                score -= 10
            
            if info.samplerate < 44100:
                issues.append("low_sample_rate")
                score -= 10
        except:
            issues.append("file_read_error")
            score -= 20
        
        # Calculate crest factor (dynamic range indicator)
        crest_factor = self._calculate_crest_factor(lufs, peak)
        if crest_factor < 4:
            issues.append("low_crest_factor")
            score -= 10
        
        # Ensure score doesn't go below 0
        score = max(0, score)
        
        return {
            'health_score': score,
            'status': self._get_health_status(score),
            'issues': issues,
            'lufs': lufs,
            'peak': peak,
            'lra': lra,
            'crest_factor': round(crest_factor, 1),
            'bitrate': bitrate if 'bitrate' in locals() else None,
            'sample_rate': info.samplerate if 'info' in locals() else None
        }
    
    def _calculate_crest_factor(self, lufs, peak_db):
        """
        Calculate crest factor (peak to RMS ratio)
        Higher = more dynamic, Lower = more compressed
        """
        # Approximate RMS from LUFS
        rms_db = lufs + 3  # Rough approximation
        crest = peak_db - rms_db
        return max(0, crest)
    
    def _estimate_bitrate(self, file_path, info):
        """Estimate bitrate from file size and duration"""
        try:
            file_size = os.path.getsize(file_path)
            duration = info.duration
            if duration > 0:
                # Bitrate in kbps
                bitrate = (file_size * 8) / (duration * 1000)
                return int(bitrate)
        except:
            pass
        return None
    
    def _get_health_status(self, score):
        """Get health status from score"""
        if score >= 80:
            return "excellent"
        elif score >= 60:
            return "good"
        elif score >= 40:
            return "fair"
        else:
            return "poor"
    
    def _error_result(self, error_msg):
        """Return error result"""
        return {
            'health_score': 0,
            'status': 'error',
            'issues': ['analysis_failed'],
            'error': error_msg
        }
