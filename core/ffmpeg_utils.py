import os
import sys
import shutil
import subprocess

class FFmpegManager:
    """Centralized FFmpeg management for bundled and system installations"""
    
    def __init__(self):
        self.ffmpeg_path = self._find_ffmpeg()
    
    def _find_ffmpeg(self):
        """Find FFmpeg executable in order of preference"""
        # 1. Check if running as PyInstaller bundle
        if getattr(sys, 'frozen', False):
            bundle_dir = sys._MEIPASS
            ffmpeg_path = os.path.join(bundle_dir, 'ffmpeg')
            if os.path.exists(ffmpeg_path) and os.access(ffmpeg_path, os.X_OK):
                return ffmpeg_path
        
        # 2. Check system PATH
        system_ffmpeg = shutil.which('ffmpeg')
        if system_ffmpeg:
            return system_ffmpeg
        
        # 3. Check common macOS locations
        common_paths = [
            '/usr/local/bin/ffmpeg',
            '/opt/homebrew/bin/ffmpeg',
            '/usr/bin/ffmpeg'
        ]
        
        for path in common_paths:
            if os.path.exists(path) and os.access(path, os.X_OK):
                return path
        
        raise RuntimeError("FFmpeg not found. Please install FFmpeg or ensure it's bundled correctly.")
    
    def run_command(self, args, **kwargs):
        """Run FFmpeg command with proper error handling"""
        cmd = [self.ffmpeg_path] + args
        try:
            return subprocess.run(cmd, **kwargs)
        except Exception as e:
            raise RuntimeError(f"FFmpeg execution failed: {e}")
    
    def is_available(self):
        """Check if FFmpeg is available and working"""
        try:
            result = self.run_command(['-version'], capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False

# Global instance
ffmpeg_manager = FFmpegManager()
