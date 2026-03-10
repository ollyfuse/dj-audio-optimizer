from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QColor, QPen, QFont

class WaveformWidget(QWidget):
    """Custom widget to render audio waveform"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.waveform_data = None
        self.show_clipping = True
        self.setMinimumHeight(150)
        self.setStyleSheet("background-color: #1a1a1a;")
    
    def set_waveform(self, waveform_data):
        """Set waveform data and trigger repaint"""
        self.waveform_data = waveform_data
        self.update()
    
    def clear(self):
        """Clear waveform"""
        self.waveform_data = None
        self.update()
    
    def paintEvent(self, event):
        """Render waveform"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Fill background
        painter.fillRect(self.rect(), QColor("#1a1a1a"))
        
        if not self.waveform_data or not self.waveform_data.get('success'):
            # Show "No waveform" message
            painter.setPen(QColor("#666"))
            painter.drawText(self.rect(), Qt.AlignCenter, "No waveform data")
            return
        
        peaks = self.waveform_data['peaks']
        if not peaks:
            return
        
        width = self.width()
        height = self.height()
        
        # Layer 1: Draw clipping zones (background)
        if self.show_clipping and 'clipping_zones' in self.waveform_data:
            self._draw_clipping_zones(painter, width, height)
        
        # Layer 2: Draw waveform
        self._draw_waveform(painter, peaks, width, height)
        
        # Layer 3: Draw dB markers ON TOP (foreground)
        self._draw_db_markers(painter, width, height)

    
    def _draw_waveform(self, painter, peaks, width, height):
        """Draw the main waveform - FIXED SCALING"""
        num_peaks = len(peaks)
        if num_peaks == 0:
            return
        
        x_scale = width / num_peaks
        
        # Find max peak for normalization
        max_amplitude = max(max(abs(min_val), abs(max_val)) for min_val, max_val in peaks)
        if max_amplitude == 0:
            max_amplitude = 1.0
        
        # Waveform color
        painter.setPen(QPen(QColor("#00ff88"), 1))
        
        center_y = height / 2
        
        for i, (min_val, max_val) in enumerate(peaks):
            x = int(i * x_scale)
            
            # Normalize to max peak, then scale to widget height
            # This ensures waveform fills the entire height
            normalized_min = min_val / max_amplitude
            normalized_max = max_val / max_amplitude
            
            # Scale to widget (use 95% of height for padding)
            scale = (height / 2) * 0.95
            
            y_top = int(center_y - (normalized_max * scale))
            y_bottom = int(center_y - (normalized_min * scale))
            
            # Draw vertical line
            painter.drawLine(x, y_top, x, y_bottom)
    
    def _draw_clipping_zones(self, painter, width, height):
        """Highlight clipping zones in red - FIXED THRESHOLD"""
        clipping_zones = self.waveform_data.get('clipping_zones', [])
        duration = self.waveform_data.get('duration', 1)
        
        if not clipping_zones:
            return
        
        # Brighter red with more opacity
        painter.setBrush(QColor(255, 50, 50, 80))  # More visible red
        painter.setPen(Qt.NoPen)
        
        for start, end in clipping_zones:
            x_start = int((start / duration) * width)
            x_end = int((end / duration) * width)
            width_clip = max(2, x_end - x_start)  # Minimum 2px wide
            painter.drawRect(x_start, 0, width_clip, height)
    
    def _draw_db_markers(self, painter, width, height):
        """Draw dB reference lines - ALWAYS VISIBLE ON TOP"""
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        
        # 0dB line (top) - BRIGHT RED
        painter.setPen(QPen(QColor("#ff0000"), 2, Qt.DashLine))
        painter.drawLine(0, 5, width, 5)
        
        # Text with background for visibility
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#1a1a1a"))
        painter.drawRect(5, 2, 45, 16)
        
        painter.setPen(QColor("#ff0000"))
        painter.drawText(8, 14, "0 dB")
        
        # -6dB line - BRIGHT YELLOW
        y_6db = int(height * 0.25)
        painter.setPen(QPen(QColor("#ffcc00"), 2, Qt.DashLine))
        painter.drawLine(0, y_6db, width, y_6db)
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#1a1a1a"))
        painter.drawRect(5, y_6db - 8, 50, 16)
        
        painter.setPen(QColor("#ffcc00"))
        painter.drawText(8, y_6db + 4, "-6 dB")
        
        # Center line (silence) - GRAY
        center_y = height // 2
        painter.setPen(QPen(QColor("#555"), 1, Qt.DotLine))
        painter.drawLine(0, center_y, width, center_y)
        
        # -6dB line (bottom mirror) - BRIGHT YELLOW
        y_6db_bottom = int(height * 0.75)
        painter.setPen(QPen(QColor("#ffcc00"), 2, Qt.DashLine))
        painter.drawLine(0, y_6db_bottom, width, y_6db_bottom)
        
        # 0dB line (bottom) - BRIGHT RED
        painter.setPen(QPen(QColor("#ff0000"), 2, Qt.DashLine))
        painter.drawLine(0, height - 5, width, height - 5)
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#1a1a1a"))
        painter.drawRect(5, height - 18, 45, 16)
        
        painter.setPen(QColor("#ff0000"))
        painter.drawText(8, height - 6, "0 dB")
