import numpy as np
from .lufs_analyzer import LUFSAnalyzer
from .health_analyzer import HealthAnalyzer
import soundfile as sf

class AudioAnalyzer:
    def __init__(self):
        self.lufs_analyzer = LUFSAnalyzer()
        self.health_analyzer = HealthAnalyzer()
    
    def analyze_track(self, file_path):
        """Analyze track with health check"""
        try:
            # Get health analysis (includes LUFS)
            health_data = self.health_analyzer.analyze_track_health(file_path)
            
            if health_data.get('status') == 'error':
                return self._error_result(health_data.get('error', 'Analysis failed'))
            
            # Get sample rate
            try:
                info = sf.info(file_path)
                sample_rate = info.samplerate
            except:
                sample_rate = 44100
            
            return {
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
            
        except Exception as e:
            return self._error_result(str(e))
    
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
