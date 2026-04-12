import subprocess
import os
import sys
from .presets import PresetManager
from .utils import extract_loudnorm_json


class AudioProcessor:
    def __init__(self):
        self.preset_manager = PresetManager()
        self.ffmpeg_path = self._find_ffmpeg()

    def _find_ffmpeg(self):
        """Find FFmpeg executable (bundled or system)"""
        if getattr(sys, 'frozen', False):
            bundle_dir = sys._MEIPASS
            ffmpeg_path = os.path.join(bundle_dir, 'ffmpeg')
            if os.path.exists(ffmpeg_path):
                return ffmpeg_path
        return 'ffmpeg'

    def process_track(self, input_path, preset_name, output_path, output_format="wav_24"):
        """Process with LUFS correction loop and final peak safety pass"""
        try:
            preset = self.preset_manager.get_preset(preset_name)

            loudness_data = self._measure_loudness(input_path, preset)
            if not loudness_data:
                return {'success': False, 'error': 'Failed to measure loudness'}

            success, final_output_path = self._apply_processing(
                input_path, output_path, preset, loudness_data, output_format
            )

            if not success:
                return {'success': False, 'error': 'Processing failed'}

            final_lufs = self._measure_final_lufs(final_output_path)
            target_lufs = preset['target_lufs']
            attempts = 0

            while abs(final_lufs - target_lufs) > 0.5 and attempts < 2:
                trim_db = target_lufs - final_lufs
                trim_db = max(-6.0, min(6.0, trim_db))

                print(f"LUFS correction: output={final_lufs:.1f}, target={target_lufs}, trim={trim_db:+.1f}dB")

                success, final_output_path = self._apply_trim(
                    final_output_path, trim_db, preset, output_format
                )
                if not success:
                    break

                final_lufs = self._measure_final_lufs(final_output_path)
                attempts += 1

            # Peak safety only needed if trim passes ran — they add gain after the limiter
            if attempts > 0:
                self._apply_peak_safety(final_output_path, preset, output_format)

            return {
                'success': True,
                'output_path': final_output_path,
                'original_lufs': loudness_data.get('input_i', -12.0),
                'final_lufs': final_lufs
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

        
    def _apply_peak_safety(self, audio_path, preset, output_format):
        """
        Final true-peak safety pass — always runs after correction loop.
        attack=1ms catches inter-sample peaks that slower limiters miss.
        Overwrites the file in place atomically.
        """
        base_path = os.path.splitext(audio_path)[0]

        if output_format == "wav_24":
            codec_args = ['-c:a', 'pcm_s24le', '-ar', '44100']
            ext = '.wav'
        elif output_format == "wav_16":
            codec_args = ['-c:a', 'pcm_s16le', '-ar', '44100']
            ext = '.wav'
        elif output_format == "aiff":
            codec_args = ['-c:a', 'pcm_s24be', '-ar', '44100']
            ext = '.aiff'
        elif output_format == "flac":
            codec_args = ['-c:a', 'flac', '-ar', '44100']
            ext = '.flac'
        else:
            codec_args = ['-c:a', 'pcm_s24le', '-ar', '44100']
            ext = '.wav'

        tmp_path = base_path + '_peak' + ext
        limit_linear = 10 ** (preset['true_peak'] / 20)

        # attack=1ms — tightest possible, catches every inter-sample peak
        # level=false — no input gain compensation, just ceiling enforcement
        filter_chain = (
            f"alimiter=limit={limit_linear:.6f}:"
            f"attack=1:"
            f"release=50:"
            f"level=false"
        )

        cmd = [self.ffmpeg_path, '-i', audio_path, '-af', filter_chain] + codec_args + ['-y', tmp_path]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                os.replace(tmp_path, audio_path)
        except Exception:
            pass  # non-fatal — file already processed, peak safety is best-effort



    def _apply_trim(self, audio_path, trim_db, preset, output_format):
        """Apply a small gain trim + limiter pass to correct LUFS overshoot/undershoot"""
       
        base_path = os.path.splitext(audio_path)[0]

        if output_format == "wav_24":
            codec_args = ['-c:a', 'pcm_s24le', '-ar', '44100']
            ext = '.wav'
        elif output_format == "wav_16":
            codec_args = ['-c:a', 'pcm_s16le', '-ar', '44100']
            ext = '.wav'
        elif output_format == "aiff":
            codec_args = ['-c:a', 'pcm_s24be', '-ar', '44100']
            ext = '.aiff'
        elif output_format == "flac":
            codec_args = ['-c:a', 'flac', '-ar', '44100']
            ext = '.flac'
        else:
            codec_args = ['-c:a', 'pcm_s24le', '-ar', '44100']
            ext = '.wav'

        # Write to a temp file then replace — avoids reading/writing same file
        tmp_path = base_path + '_trim' + ext
        limit_linear = 10 ** (preset['true_peak'] / 20)

        filter_chain = (
            f"volume={trim_db}dB,"
            f"alimiter=limit={limit_linear:.6f}:attack=5:release=50:level=false"
        )

        cmd = [self.ffmpeg_path, '-i', audio_path, '-af', filter_chain] + codec_args + ['-y', tmp_path]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                os.replace(tmp_path, audio_path)  # atomic replace
                return True, audio_path
            return False, audio_path
        except subprocess.TimeoutExpired:
            return False, audio_path
        except Exception:
            return False, audio_path

    def _measure_final_lufs(self, audio_path):
        """
        Measure integrated LUFS using ebur128 — 3-4x faster than loudnorm.
        loudnorm does a full dynamic analysis pass; ebur128 just measures loudness.
        """
        cmd = [
            self.ffmpeg_path, '-i', audio_path,
            '-af', 'ebur128=framelog=quiet',
            '-f', 'null', '-'
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            for line in reversed(result.stderr.split('\n')):
                if 'I:' in line and 'LUFS' in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == 'I:' and i + 1 < len(parts):
                            return round(float(parts[i + 1]), 1)
        except subprocess.TimeoutExpired:
            print(f"LUFS measurement timed out for: {os.path.basename(audio_path)}")
        except Exception:
            pass
        return -12.0


    def _measure_loudness(self, input_path, preset):
        """Pass 1: measure loudness characteristics for 2-pass normalization"""
        cmd = [
            self.ffmpeg_path, '-i', input_path,
            '-af', f"loudnorm=I={preset['target_lufs']}:TP={preset['true_peak']}:LRA=11:print_format=json",
            '-f', 'null', '-'
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            data = extract_loudnorm_json(result.stderr)

            if data is None:
                print(f"No loudnorm JSON found for: {os.path.basename(input_path)}")
                return None

            # Validate all 5 fields required for 2-pass loudnorm are present and numeric
            required = ['input_i', 'input_tp', 'input_lra', 'input_thresh', 'target_offset']
            for field in required:
                if field not in data:
                    print(f"Missing loudnorm field '{field}' for: {os.path.basename(input_path)}")
                    return None
                try:
                    float(data[field])
                except (ValueError, TypeError):
                    print(f"Non-numeric loudnorm field '{field}': {data[field]}")
                    return None

            return data

        except subprocess.TimeoutExpired:
            print(f"Loudness measurement timed out for: {os.path.basename(input_path)}")
            return None
        except Exception:
            return None

    def _apply_processing(self, input_path, output_path, preset, loudness_data, output_format="wav_24"):
        """Pass 2: apply hybrid loudnorm pipeline with precision normalization"""
        filter_chain = self._build_filter_chain(preset, loudness_data)

        base_path = os.path.splitext(output_path)[0]

        if output_format == "wav_24":
            codec_args = ['-c:a', 'pcm_s24le', '-ar', '44100']
            output_path = base_path + '.wav'
        elif output_format == "wav_16":
            codec_args = ['-c:a', 'pcm_s16le', '-ar', '44100']
            output_path = base_path + '.wav'
        elif output_format == "aiff":
            codec_args = ['-c:a', 'pcm_s24be', '-ar', '44100']
            output_path = base_path + '.aiff'
        elif output_format == "flac":
            codec_args = ['-c:a', 'flac', '-ar', '44100']
            output_path = base_path + '.flac'
        else:
            codec_args = ['-c:a', 'pcm_s24le', '-ar', '44100']
            output_path = base_path + '.wav'

        cmd = [self.ffmpeg_path, '-i', input_path, '-af', filter_chain] + codec_args + ['-y', output_path]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            return result.returncode == 0, output_path
        except subprocess.TimeoutExpired:
            print(f"Processing timed out for: {os.path.basename(input_path)}")
            return False, output_path

    def _build_filter_chain(self, preset, loudness_data):
        """
        Dual-mode chain — automatically selects processing based on track dynamics.

        Mode A (loudnorm): dynamic tracks with LRA >= 6
        Mode B (gain+limiter): compressed/clipped tracks with LRA < 6

        Chain: pre-limiter (conditional) → highpass → [loudnorm OR gain] → final limiter
        """
        filters = []

        input_peak_db = float(loudness_data.get('input_tp', -1.0))
        input_lra     = float(loudness_data.get('input_lra', 0.0))
        input_lufs    = float(loudness_data['input_i'])
        target_lufs   = preset['target_lufs']
        gain_needed   = target_lufs - input_lufs
        safe_gain     = max(-6.0, min(6.0, gain_needed))

        # 1. Pre-limiter — only on clipped sources (peak > -1 dBFS)
        if input_peak_db > -1.0:
            pre_limit_linear = 10 ** (-1.0 / 20)
            filters.append(
                f"alimiter=limit={pre_limit_linear:.6f}:"
                f"attack=3:"
                f"release=25:"
                f"level=false"
            )

        # 2. Highpass — sub-rumble removal
        filters.append(f"highpass=f={preset['highpass_hz']}:poles=1")

        # 3. Mode selection based on LRA
        if input_lra < 6.0:
            # Mode B — compressed/brick-walled track
            # loudnorm pumps trying to expand dynamics that don't exist
            # simple gain correction is cleaner and more transparent
            if abs(safe_gain) > 0.3:
                filters.append(f"volume={safe_gain}dB")
        else:
            # Mode A — dynamic track, loudnorm operates cleanly
            target_offset = loudness_data.get('target_offset', '0.0')
            filters.append(
                f"loudnorm=I={preset['target_lufs']}:"
                f"TP={preset['true_peak']}:"
                f"LRA=11:"
                f"measured_I={loudness_data['input_i']}:"
                f"measured_TP={loudness_data['input_tp']}:"
                f"measured_LRA={loudness_data['input_lra']}:"
                f"measured_thresh={loudness_data['input_thresh']}:"
                f"offset={target_offset}:"
                f"linear=false:"
                f"print_format=none"
            )

        # 4. Final true-peak limiter — safety ceiling for both modes
        limit_linear = 10 ** (preset['true_peak'] / 20)
        filters.append(
            f"alimiter=limit={limit_linear:.6f}:"
            f"attack=5:"
            f"release=50:"
            f"level=false"
        )

        return ",".join(filters)
