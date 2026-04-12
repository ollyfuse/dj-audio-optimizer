import json
import os
import hashlib
from pathlib import Path

class WaveformCache:
    """Cache waveform data to avoid regenerating"""
    
    def __init__(self, cache_dir=None):
        if cache_dir is None:
            # Use temp directory in project
            cache_dir = os.path.join(os.path.dirname(__file__), '..', 'temp', 'waveform_cache')
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get(self, audio_path):
        """
        Get cached waveform data
        Returns: waveform_data dict or None if not cached/invalid
        """
        cache_key = self._get_cache_key(audio_path)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r') as f:
                cached_data = json.load(f)
            
            # Validate cache (check if file was modified)
            if self._is_cache_valid(audio_path, cached_data):
                return cached_data
            else:
                # Cache invalid, delete it
                cache_file.unlink()
                return None
        
        except Exception:
            return None
    
    def set(self, audio_path, waveform_data):
        """Save waveform data to cache"""
        try:
            cache_key = self._get_cache_key(audio_path)
            cache_file = self.cache_dir / f"{cache_key}.json"
            
            # Add metadata for validation
            waveform_data['_cache_metadata'] = {
                'file_path': str(audio_path),
                'file_size': os.path.getsize(audio_path),
                'modified_time': os.path.getmtime(audio_path)
            }
            
            with open(cache_file, 'w') as f:
                json.dump(waveform_data, f)
            
            return True
        
        except Exception:
            return False
    
    def clear(self):
        """Clear all cached waveforms"""
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
            return True
        except Exception:
            return False
    
    def _get_cache_key(self, audio_path):
        """Generate unique cache key from file path"""
        # Use hash of absolute path for consistent key
        abs_path = str(Path(audio_path).resolve())
        return hashlib.sha256(abs_path.encode()).hexdigest()

    
    def _is_cache_valid(self, audio_path, cached_data):
        """Check if cached data is still valid"""
        if '_cache_metadata' not in cached_data:
            return False
        
        metadata = cached_data['_cache_metadata']
        
        try:
            # Check if file still exists
            if not os.path.exists(audio_path):
                return False
            
            # Check if file size changed
            if os.path.getsize(audio_path) != metadata['file_size']:
                return False
            
            # Check if file was modified
            if os.path.getmtime(audio_path) != metadata['modified_time']:
                return False
            
            return True
        
        except Exception:
            return False
