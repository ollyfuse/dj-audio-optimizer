import numpy as np
import soundfile as sf
from pathlib import Path

class WaveformGenerator:
    """Generate downsampled waveform data for visualization"""
    
    def __init__(self, target_points=2000):
        self.target_points = target_points
    
    def generate(self, audio_path):
        """
        Generate waveform data from audio file
        Returns: {
            'peaks': [(min, max), ...],  # Downsampled peak pairs
            'duration': float,
            'sample_rate': int,
            'clipping_zones': [(start, end), ...],  # Regions with clipping
            'max_peak': float
        }
        """
        try:
            # Load audio
            audio, sr = sf.read(audio_path, dtype='float32')
            
            # Convert stereo to mono (take max of both channels)
            if len(audio.shape) > 1:
                audio = np.max(np.abs(audio), axis=1)
            else:
                audio = np.abs(audio)
            
            duration = len(audio) / sr
            
            # Downsample to target points
            peaks = self._downsample_peaks(audio, self.target_points)
            
            # Detect clipping zones (>= 0.99 to account for float precision)
            clipping_zones = self._detect_clipping(audio, sr)
            
            # Get max peak
            max_peak = float(np.max(audio))
            
            return {
                'peaks': peaks,
                'duration': duration,
                'sample_rate': sr,
                'clipping_zones': clipping_zones,
                'max_peak': max_peak,
                'success': True
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _downsample_peaks(self, audio, target_points):
        """Downsample audio to peak pairs for visualization"""
        total_samples = len(audio)
        samples_per_point = max(1, total_samples // target_points)
        
        peaks = []
        for i in range(0, total_samples, samples_per_point):
            chunk = audio[i:i + samples_per_point]
            if len(chunk) > 0:
                peaks.append((float(np.min(chunk)), float(np.max(chunk))))
        
        return peaks
    
    def _detect_clipping(self, audio, sample_rate, threshold=0.99):
        """Detect regions where audio clips"""
        clipping_mask = audio >= threshold
        
        # Find continuous clipping regions
        zones = []
        in_clip = False
        start = 0
        
        for i, is_clip in enumerate(clipping_mask):
            if is_clip and not in_clip:
                start = i / sample_rate
                in_clip = True
            elif not is_clip and in_clip:
                end = i / sample_rate
                zones.append((start, end))
                in_clip = False
        
        # Close last zone if still clipping at end
        if in_clip:
            zones.append((start, len(audio) / sample_rate))
        
        return zones
