import numpy as np
import pyloudnorm as pyln
import soundfile as sf

class AudioAnalyzer:
    def __init__(self):
        self.meter = pyln.Meter(44100)
    
    def analyze_track(self, file_path):
        try:
            # Load audio
            data, rate = sf.read(file_path)
            
            # Convert to mono if stereo
            if len(data.shape) > 1:
                data = np.mean(data, axis=1)
            
            # Measure loudness
            loudness = self.meter.integrated_loudness(data)
            
            # Get peak
            peak = np.max(np.abs(data))
            peak_db = 20 * np.log10(peak) if peak > 0 else -60
            
            # Get duration
            duration = len(data) / rate
            
            return {
                'lufs': round(loudness, 1),
                'peak_db': round(peak_db, 1),
                'duration': round(duration, 1),
                'sample_rate': rate,
                'status': 'ready'
            }
        except Exception as e:
            return {
                'lufs': 0,
                'peak_db': 0,
                'duration': 0,
                'sample_rate': 0,
                'status': 'error',
                'error': str(e)
            }
