import numpy as np
import soundfile as sf
from pathlib import Path


class WaveformGenerator:
    """Generate downsampled waveform data for visualization"""

    def __init__(self, target_points=2000):
        self.target_points = target_points

    def generate(self, audio_path):
        """
        Generate waveform data from audio file.
        Returns:
            peaks          — [(min, max), ...]  peak pairs for transient display
            rms            — [float, ...]       RMS per chunk for loudness body
            energy         — [float, ...]       smoothed energy curve for macro view
            clipping_zones — [(start, end), ...]
            duration, sample_rate, max_peak
        """
        try:
            audio, sr = sf.read(audio_path, dtype='float32')

            # Stereo → mono: take max absolute value across channels
            if len(audio.shape) > 1:
                audio = np.max(np.abs(audio), axis=1)
            else:
                audio = np.abs(audio)

            duration = len(audio) / sr

            peaks = self._downsample_peaks(audio, self.target_points)
            rms = self._downsample_rms(audio, self.target_points)
            energy = self._energy_curve(rms)
            clipping_zones = self._detect_clipping(audio, sr)
            max_peak = float(np.max(audio))

            return {
                'peaks': peaks,
                'rms': rms,
                'energy': energy,
                'duration': duration,
                'sample_rate': sr,
                'clipping_zones': clipping_zones,
                'max_peak': max_peak,
                'success': True
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _downsample_peaks(self, audio, target_points):
        """Peak pairs (min, max) per chunk — captures transients"""
        total_samples = len(audio)
        samples_per_point = max(1, total_samples // target_points)

        peaks = []
        for i in range(0, total_samples, samples_per_point):
            chunk = audio[i:i + samples_per_point]
            if len(chunk) > 0:
                peaks.append((float(np.min(chunk)), float(np.max(chunk))))

        return peaks

    def _downsample_rms(self, audio, target_points):
        """RMS value per chunk — represents perceived loudness per segment"""
        total_samples = len(audio)
        samples_per_point = max(1, total_samples // target_points)

        rms = []
        for i in range(0, total_samples, samples_per_point):
            chunk = audio[i:i + samples_per_point]
            if len(chunk) > 0:
                rms.append(float(np.sqrt(np.mean(chunk ** 2))))

        return rms

    def _energy_curve(self, rms, window=20):
        """
        Smooth the RMS curve with a rolling average to produce a macro
        energy envelope — reveals drops, builds, and breakdowns clearly.
        Window size of 20 points balances smoothness vs responsiveness.
        """
        if not rms:
            return []

        rms_array = np.array(rms)
        kernel = np.ones(window) / window
        # 'same' mode keeps output length equal to input
        smoothed = np.convolve(rms_array, kernel, mode='same')
        return [float(v) for v in smoothed]

    def _detect_clipping(self, audio, sample_rate, threshold=0.99):
        """Detect continuous regions where audio clips"""
        clipping_mask = audio >= threshold

        zones = []
        in_clip = False
        start = 0

        for i, is_clip in enumerate(clipping_mask):
            if is_clip and not in_clip:
                start = i / sample_rate
                in_clip = True
            elif not is_clip and in_clip:
                zones.append((start, i / sample_rate))
                in_clip = False

        if in_clip:
            zones.append((start, len(audio) / sample_rate))

        return zones
