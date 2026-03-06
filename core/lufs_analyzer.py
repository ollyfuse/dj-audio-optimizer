"""
Unified LUFS measurement using FFmpeg for consistency
"""
import subprocess
import json
import sys
import os
import shutil

class LUFSAnalyzer:
    """FFmpeg-based LUFS analyzer for consistent measurements"""
    
    def __init__(self):
        self.ffmpeg_path = self._find_ffmpeg()
    
    def _find_ffmpeg(self):
        """Find FFmpeg executable (bundled or system)"""
        if getattr(sys, 'frozen', False):
            bundle_dir = sys._MEIPASS
            ffmpeg_path = os.path.join(bundle_dir, 'ffmpeg')
            if os.path.exists(ffmpeg_path):
                return ffmpeg_path
        return shutil.which('ffmpeg') or 'ffmpeg'
    
    def measure_lufs(self, file_path):
        """
        Measure integrated LUFS and true peak using FFmpeg
        Returns: dict with lufs, peak_db, duration
        """
        cmd = [
            self.ffmpeg_path,
            '-i', file_path,
            '-af', 'loudnorm=print_format=json',
            '-f', 'null',
            '-'
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,  # Increased to 2 minutes
                encoding='utf-8',  # Handle special characters
                errors='replace'  # Replace invalid chars instead of failing
            )
            
            # Extract JSON from stderr
            json_start = result.stderr.rfind('{')
            json_end = result.stderr.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                return None
            
            json_str = result.stderr[json_start:json_end]
            data = json.loads(json_str)
            
            # Get duration from FFmpeg output
            duration = self._extract_duration(result.stderr)
            
            return {
                'lufs': round(float(data.get('input_i', -12.0)), 1),
                'peak_db': round(float(data.get('input_tp', -1.0)), 1),
                'duration': duration,
                'lra': round(float(data.get('input_lra', 0.0)), 1),
                'threshold': round(float(data.get('input_thresh', -70.0)), 1)
            }
            
        except subprocess.TimeoutExpired as e:
            print(f"LUFS measurement timed out for: {os.path.basename(file_path)}")
            return None
        except (json.JSONDecodeError, ValueError) as e:
            print(f"LUFS measurement failed for {os.path.basename(file_path)}: {e}")
            return None

    
    def _extract_duration(self, ffmpeg_output):
        """Extract duration from FFmpeg output"""
        try:
            for line in ffmpeg_output.split('\n'):
                if 'Duration:' in line:
                    # Format: Duration: 00:03:45.67
                    time_str = line.split('Duration:')[1].split(',')[0].strip()
                    h, m, s = time_str.split(':')
                    duration = int(h) * 3600 + int(m) * 60 + float(s)
                    return round(duration, 1)
        except:
            pass
        return 0.0
    
    def is_within_target(self, measured_lufs, target_lufs, tolerance=0.5):
        """
        Check if measured LUFS is within acceptable range of target
        tolerance: ±0.5 LUFS is acceptable
        """
        return abs(measured_lufs - target_lufs) <= tolerance
