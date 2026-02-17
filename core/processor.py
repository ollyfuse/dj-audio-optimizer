import subprocess
import os
import tempfile
import json
import sys
from .presets import PresetManager

class AudioProcessor:
    def __init__(self):
        self.preset_manager = PresetManager()
        self.ffmpeg_path = self._find_ffmpeg()
    
    def _find_ffmpeg(self):
        """Find FFmpeg executable (bundled or system)"""
        # If running as bundled app, look for bundled FFmpeg
        if getattr(sys, 'frozen', False):
            bundle_dir = sys._MEIPASS
            ffmpeg_path = os.path.join(bundle_dir, 'ffmpeg')
            if os.path.exists(ffmpeg_path):
                return ffmpeg_path
        
        # Fallback to system FFmpeg
        return 'ffmpeg'
    
    def process_track(self, input_path, preset_name, output_path, output_format="wav_24"):
        """Process a single track with gentle, professional processing"""
        try:
            preset = self.preset_manager.get_preset(preset_name)
            
            # Step 1: Measure loudness (first pass)
            loudness_data = self._measure_loudness(input_path, preset)
            if not loudness_data:
                return {'success': False, 'error': 'Failed to measure loudness'}
            
            # Step 2: Apply gentle processing
            success, final_output_path = self._apply_gentle_processing(input_path, output_path, preset, loudness_data, output_format)

            if success:
                # Step 3: Measure ACTUAL final LUFS
                final_lufs = self._measure_final_lufs(final_output_path)
                
                return {
                    'success': True,
                    'output_path': final_output_path,
                    'original_lufs': loudness_data.get('input_i', -12.0),
                    'final_lufs': final_lufs
                }
            else:
                return {'success': False, 'error': 'Processing failed'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _measure_final_lufs(self, audio_path):
        """Measure the actual LUFS of processed audio"""
        cmd = [
            self.ffmpeg_path, '-i', audio_path,
            '-af', 'loudnorm=print_format=json',
            '-f', 'null', '-'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        try:
            json_start = result.stderr.rfind('{')
            json_end = result.stderr.rfind('}') + 1
            json_str = result.stderr[json_start:json_end]
            data = json.loads(json_str)
            return float(data.get('input_i', -12.0))
        except:
            return -12.0

    def _measure_loudness(self, input_path, preset):
        """First pass: measure loudness characteristics"""
        cmd = [
            self.ffmpeg_path, '-i', input_path,
            '-af', f"loudnorm=I={preset['target_lufs']}:TP={preset['true_peak']}:LRA=11:print_format=json",
            '-f', 'null', '-'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            return None
        
        try:
            json_start = result.stderr.rfind('{')
            json_end = result.stderr.rfind('}') + 1
            json_str = result.stderr[json_start:json_end]
            return json.loads(json_str)
        except:
            return None
    
    def _apply_gentle_processing(self, input_path, output_path, preset, loudness_data, output_format="wav_24"):
        """Apply gentle, professional processing with format options"""
        filter_chain = self._build_gentle_filter_chain(preset, loudness_data)
        
        if output_format == "wav_24":
            codec_args = ['-c:a', 'pcm_s24le', '-ar', '44100']
        elif output_format == "wav_16":
            codec_args = ['-c:a', 'pcm_s16le', '-ar', '44100']
        elif output_format == "aiff":
            codec_args = ['-c:a', 'pcm_s24be', '-ar', '44100']
            output_path = output_path.replace('.wav', '.aiff')
        elif output_format == "flac":
            codec_args = ['-c:a', 'flac', '-ar', '44100']
            output_path = output_path.replace('.wav', '.flac')
        else:
            codec_args = ['-c:a', 'pcm_s24le', '-ar', '44100']
        
        cmd = [self.ffmpeg_path, '-i', input_path, '-af', filter_chain] + codec_args + ['-y', output_path]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0, output_path

    def _build_gentle_filter_chain(self, preset, loudness_data):
        """Simple, artifact-free processing"""
        filters = []

        input_lufs = float(loudness_data['input_i'])
        target_lufs = preset['target_lufs']
        gain_needed = target_lufs - input_lufs
        safe_gain = max(-6.0, min(6.0, gain_needed))
        
        if preset['highpass_hz'] > 30:
            filters.append(f"highpass=f={preset['highpass_hz']}:poles=1")
        
        if abs(safe_gain) > 0.5:
            filters.append(f"volume={safe_gain}dB")
        
        limit_linear = 10 ** (preset['true_peak'] / 20)
        filters.append(
            f"alimiter=limit={limit_linear}:"
            f"attack=30:"
            f"release=300:"
            f"level=false"
        )

        return ",".join(filters) if filters else "anull"
