from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QWidget, QProgressBar)
from PySide6.QtCore import Qt, QThread, Signal
from .waveform_widget import WaveformWidget
from core.waveform_generator import WaveformGenerator
from core.waveform_cache import WaveformCache
import numpy as np

class WaveformDialog(QDialog):
    """Dialog showing before/after waveform comparison"""
    
    def __init__(self, before_path, after_path=None, parent=None):
        super().__init__(parent)
        self.before_path = before_path
        self.after_path = after_path
        self.generator = WaveformGenerator()
        self.cache = WaveformCache()
        
        self.setup_ui()
        self.load_waveforms()
    
    def setup_ui(self):
        """Build dialog UI"""
        self.setWindowTitle("Waveform Comparison")
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("Audio Waveform Analysis")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #00ff88;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Progress bar (shown while loading)
        self.progress = QProgressBar()
        self.progress.setMaximum(0)  # Indeterminate
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        # Before waveform
        before_label = QLabel("Before (Original)")
        before_label.setStyleSheet("font-weight: bold; color: white;")
        layout.addWidget(before_label)
        
        self.before_widget = WaveformWidget()
        self.before_widget.setMinimumHeight(180)
        layout.addWidget(self.before_widget)
        
        # Stats for before
        self.before_stats = QLabel()
        self.before_stats.setStyleSheet("color: #aaa; font-size: 11px;")
        layout.addWidget(self.before_stats)
        
        # After waveform (if available)
        if self.after_path:
            after_label = QLabel("After (Optimized)")
            after_label.setStyleSheet("font-weight: bold; color: #00ff88;")
            layout.addWidget(after_label)
            
            self.after_widget = WaveformWidget()
            self.after_widget.setMinimumHeight(180)
            layout.addWidget(self.after_widget)
            
            # Stats for after
            self.after_stats = QLabel()
            self.after_stats.setStyleSheet("color: #aaa; font-size: 11px;")
            layout.addWidget(self.after_stats)
            
            # Improvement summary
            self.improvement_label = QLabel()
            self.improvement_label.setStyleSheet("color: #00ff88; font-weight: bold; font-size: 12px;")
            self.improvement_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(self.improvement_label)
        
        layout.addStretch()
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setMinimumHeight(35)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.apply_dark_theme()
    
    def load_waveforms(self):
        """Load waveforms in background thread"""
        self.progress.setVisible(True)
        
        class WaveformLoader(QThread):
            finished_signal = Signal(dict, dict)
            
            def __init__(self, generator, cache, before_path, after_path):
                super().__init__()
                self.generator = generator
                self.cache = cache
                self.before_path = before_path
                self.after_path = after_path
            
            def run(self):
                # Load before waveform
                before_data = self.cache.get(self.before_path)
                if before_data is None:
                    before_data = self.generator.generate(self.before_path)
                    if before_data.get('success'):
                        self.cache.set(self.before_path, before_data)
                
                # Load after waveform if available
                after_data = None
                if self.after_path:
                    after_data = self.cache.get(self.after_path)
                    if after_data is None:
                        after_data = self.generator.generate(self.after_path)
                        if after_data.get('success'):
                            self.cache.set(self.after_path, after_data)
                
                self.finished_signal.emit(before_data, after_data)
        
        self.loader = WaveformLoader(self.generator, self.cache, self.before_path, self.after_path)
        self.loader.finished_signal.connect(self.on_waveforms_loaded)
        self.loader.start()
    
    def on_waveforms_loaded(self, before_data, after_data):
        """Handle waveforms loaded"""
        self.progress.setVisible(False)
        
        # Display before waveform
        self.before_widget.set_waveform(before_data)
        if before_data and before_data.get('success'):
            self.before_stats.setText(self._format_stats(before_data))
        
        # Display after waveform
        if after_data and hasattr(self, 'after_widget'):
            self.after_widget.set_waveform(after_data)
            if after_data.get('success'):
                self.after_stats.setText(self._format_stats(after_data))
                self._show_improvement(before_data, after_data)
    
    def _format_stats(self, waveform_data):
        """Format waveform stats for display"""
        if not waveform_data or not waveform_data.get('success'):
            return "Failed to load waveform"
        
        duration = waveform_data.get('duration', 0)
        max_peak = waveform_data.get('max_peak', 0)
        clipping_count = len(waveform_data.get('clipping_zones', []))
        
        # Convert linear amplitude to dB (correct formula)
        if max_peak > 0:
            peak_db = 20 * np.log10(max_peak)
        else:
            peak_db = -96.0
        
        stats = f"Duration: {duration:.1f}s | Max Peak: {peak_db:.1f} dB"
        
        if clipping_count > 0:
            stats += f" | ⚠️ {clipping_count} clipping zone{'s' if clipping_count > 1 else ''}"
        else:
            stats += " | No clipping"
        
        return stats

    
    def _show_improvement(self, before_data, after_data):
        """Show improvement summary"""
        before_clips = len(before_data.get('clipping_zones', []))
        after_clips = len(after_data.get('clipping_zones', []))
        
        before_peak = before_data.get('max_peak', 0)
        after_peak = after_data.get('max_peak', 0)
        
        improvements = []
        
        if before_clips > after_clips:
            improvements.append(f" Removed {before_clips - after_clips} clipping zone(s)")
        
        if after_peak < before_peak:
            peak_reduction = ((before_peak - after_peak) / before_peak) * 100
            improvements.append(f" Reduced peak by {peak_reduction:.1f}%")
        
        if improvements:
            self.improvement_label.setText(" | ".join(improvements))
        else:
            self.improvement_label.setText("Track analyzed successfully")
    
    def apply_dark_theme(self):
        """Apply dark theme"""
        self.setStyleSheet("""
            QDialog {
                background-color: #2d2d2d;
                color: white;
            }
            QLabel {
                color: white;
                background: transparent;
            }
            QPushButton {
                background-color: #3d3d3d;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 8px 16px;
                color: white;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
                border-color: #00ff88;
            }
            QProgressBar {
                border: 1px solid #444;
                border-radius: 4px;
                background-color: #1a1a1a;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #00ff88;
            }
        """)
