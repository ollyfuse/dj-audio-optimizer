import os
import json
import hashlib
import soundfile as sf
from pathlib import Path
from .lufs_analyzer import LUFSAnalyzer
from .health_analyzer import HealthAnalyzer


class AudioAnalyzer:
    def __init__(self):
        self.lufs_analyzer = LUFSAnalyzer()
        self.health_analyzer = HealthAnalyzer()

        # Disk-based analysis cache — same validation pattern as WaveformCache
        self._cache_dir = Path(os.path.dirname(__file__)) / '..' / 'temp' / 'analysis_cache'
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    def analyze_track(self, file_path):
        """Analyze track — returns cached result if file unchanged, runs full analysis otherwise"""
        try:
            # Check cache first — avoids 2-5s FFmpeg call on re-load
            cached = self._cache_get(file_path)
            if cached is not None:
                return cached

            health_data = self.health_analyzer.analyze_track_health(file_path)

            if health_data.get('status') == 'error':
                return self._error_result(health_data.get('error', 'Analysis failed'))

            try:
                info = sf.info(file_path)
                sample_rate = info.samplerate
            except Exception:
                sample_rate = 44100

            result = {
                'lufs': health_data['lufs'],
                'peak_db': health_data['peak'],
                'duration': health_data.get('duration', 0),
                'sample_rate': sample_rate,
                'lra': health_data.get('lra', 0),
                'health_score': health_data['health_score'],
                'health_status': health_data['status'],
                'health_issues': health_data['issues'],
                'status': 'ready'
            }

            # Store in cache before returning
            self._cache_set(file_path, result)
            return result

        except Exception as e:
            return self._error_result(str(e))

    def invalidate(self, file_path):
        """Manually invalidate cache for a specific file — call after processing"""
        cache_file = self._cache_dir / f"{self._cache_key(file_path)}.json"
        try:
            if cache_file.exists():
                cache_file.unlink()
        except Exception:
            pass

    def _cache_key(self, file_path):
        abs_path = str(Path(file_path).resolve())
        return hashlib.sha256(abs_path.encode()).hexdigest()

    def _cache_get(self, file_path):
        """Return cached analysis if file is unchanged, else None"""
        cache_file = self._cache_dir / f"{self._cache_key(file_path)}.json"
        if not cache_file.exists():
            return None
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)

            meta = data.get('_meta')
            if not meta:
                return None

            # Invalidate if file size or mtime changed
            if (os.path.getsize(file_path) != meta['size'] or
                    os.path.getmtime(file_path) != meta['mtime']):
                cache_file.unlink()
                return None

            # Return result without the metadata key
            return {k: v for k, v in data.items() if k != '_meta'}

        except Exception:
            return None

    def _cache_set(self, file_path, result):
        """Write analysis result to disk cache with file metadata"""
        cache_file = self._cache_dir / f"{self._cache_key(file_path)}.json"
        try:
            data = dict(result)
            data['_meta'] = {
                'size': os.path.getsize(file_path),
                'mtime': os.path.getmtime(file_path)
            }
            with open(cache_file, 'w') as f:
                json.dump(data, f)
        except Exception:
            pass

    def _error_result(self, error_msg):
        return {
            'lufs': 0,
            'peak_db': 0,
            'duration': 0,
            'sample_rate': 0,
            'lra': 0,
            'health_score': 0,
            'health_status': 'error',
            'health_issues': [],
            'status': 'error',
            'error': error_msg
        }
