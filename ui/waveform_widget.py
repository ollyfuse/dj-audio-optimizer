from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QPainterPath


class WaveformWidget(QWidget):
    """Custom widget to render audio waveform with RMS and energy layers"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.waveform_data = None
        self.show_clipping = True
        self.setMinimumHeight(150)
        self.setStyleSheet("background-color: #1a1a1a;")

    def set_waveform(self, waveform_data):
        self.waveform_data = waveform_data
        self.update()

    def clear(self):
        self.waveform_data = None
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), QColor("#1a1a1a"))

        if not self.waveform_data or not self.waveform_data.get('success'):
            painter.setPen(QColor("#666"))
            painter.drawText(self.rect(), Qt.AlignCenter, "No waveform data")
            return

        peaks = self.waveform_data.get('peaks', [])
        if not peaks:
            return

        width = self.width()
        height = self.height()

        # Layer 1: clipping zones
        if self.show_clipping and self.waveform_data.get('clipping_zones'):
            self._draw_clipping_zones(painter, width, height)

        # Layer 2: energy curve (macro view — orange)
        if self.waveform_data.get('energy'):
            self._draw_energy_curve(painter, self.waveform_data['energy'], width, height)

        # Layer 3: RMS fill (perceived loudness body — teal)
        if self.waveform_data.get('rms'):
            self._draw_rms_fill(painter, self.waveform_data['rms'], width, height)

        # Layer 4: peak waveform (transients — green)
        self._draw_waveform(painter, peaks, width, height)

        # Layer 5: dB markers always on top
        self._draw_db_markers(painter, width, height)

    def _draw_waveform(self, painter, peaks, width, height):
        """Peak waveform — shows transients in green"""
        num_peaks = len(peaks)
        if num_peaks == 0:
            return

        x_scale = width / num_peaks
        max_amplitude = max(max(abs(mn), abs(mx)) for mn, mx in peaks)
        if max_amplitude == 0:
            max_amplitude = 1.0

        painter.setPen(QPen(QColor("#00ff88"), 1))
        center_y = height / 2
        scale = (height / 2) * 0.95

        for i, (min_val, max_val) in enumerate(peaks):
            x = int(i * x_scale)
            y_top = int(center_y - (max_val / max_amplitude) * scale)
            y_bottom = int(center_y - (min_val / max_amplitude) * scale)
            painter.drawLine(x, y_top, x, y_bottom)

    def _draw_rms_fill(self, painter, rms, width, height):
        """
        RMS body — filled shape showing perceived loudness.
        Drawn symmetrically around center so it reads like a waveform,
        not a bar chart. Teal color sits visually between the green peaks
        and orange energy curve.
        """
        num_points = len(rms)
        if num_points == 0:
            return

        x_scale = width / num_points
        max_rms = max(rms) if max(rms) > 0 else 1.0
        center_y = height / 2
        scale = (height / 2) * 0.85  # slightly smaller than peaks so peaks show through

        # Build filled path: top half forward, bottom half backward
        path = QPainterPath()
        path.moveTo(0, center_y)

        for i, val in enumerate(rms):
            x = int(i * x_scale)
            y = center_y - (val / max_rms) * scale
            path.lineTo(x, y)

        path.lineTo(width, center_y)

        for i in range(num_points - 1, -1, -1):
            x = int(i * x_scale)
            val = rms[i]
            y = center_y + (val / max_rms) * scale
            path.lineTo(x, y)

        path.closeSubpath()

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 180, 160, 55))  # teal, semi-transparent
        painter.drawPath(path)

    def _draw_energy_curve(self, painter, energy, width, height):
        """
        Energy curve — smoothed macro envelope in orange.
        Shows the overall energy arc: drops, builds, breakdowns.
        Drawn as a mirrored line (top + bottom) so it frames the waveform.
        """
        num_points = len(energy)
        if num_points == 0:
            return

        x_scale = width / num_points
        max_energy = max(energy) if max(energy) > 0 else 1.0
        center_y = height / 2
        scale = (height / 2) * 0.90

        pen = QPen(QColor(255, 160, 40, 180), 1)  # orange, slightly transparent
        painter.setPen(pen)

        for i in range(1, num_points):
            x1 = int((i - 1) * x_scale)
            x2 = int(i * x_scale)
            e1 = (energy[i - 1] / max_energy) * scale
            e2 = (energy[i] / max_energy) * scale

            # Top mirror
            painter.drawLine(x1, int(center_y - e1), x2, int(center_y - e2))
            # Bottom mirror
            painter.drawLine(x1, int(center_y + e1), x2, int(center_y + e2))

    def _draw_clipping_zones(self, painter, width, height):
        """Clipping zones — red background highlight"""
        clipping_zones = self.waveform_data.get('clipping_zones', [])
        duration = self.waveform_data.get('duration', 1)
        if not clipping_zones:
            return

        painter.setBrush(QColor(255, 50, 50, 80))
        painter.setPen(Qt.NoPen)

        for start, end in clipping_zones:
            x_start = int((start / duration) * width)
            x_end = int((end / duration) * width)
            painter.drawRect(x_start, 0, max(2, x_end - x_start), height)

    def _draw_db_markers(self, painter, width, height):
        """dB reference lines — always rendered on top"""
        painter.setFont(QFont("Arial", 10, QFont.Bold))

        # 0 dB — red
        painter.setPen(QPen(QColor("#ff0000"), 2, Qt.DashLine))
        painter.drawLine(0, 5, width, 5)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#1a1a1a"))
        painter.drawRect(5, 2, 45, 16)
        painter.setPen(QColor("#ff0000"))
        painter.drawText(8, 14, "0 dB")

        # -6 dB — yellow
        y_6db = int(height * 0.25)
        painter.setPen(QPen(QColor("#ffcc00"), 2, Qt.DashLine))
        painter.drawLine(0, y_6db, width, y_6db)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#1a1a1a"))
        painter.drawRect(5, y_6db - 8, 50, 16)
        painter.setPen(QColor("#ffcc00"))
        painter.drawText(8, y_6db + 4, "-6 dB")

        # Center silence line — gray
        center_y = height // 2
        painter.setPen(QPen(QColor("#555"), 1, Qt.DotLine))
        painter.drawLine(0, center_y, width, center_y)

        # -6 dB bottom mirror — yellow
        y_6db_bottom = int(height * 0.75)
        painter.setPen(QPen(QColor("#ffcc00"), 2, Qt.DashLine))
        painter.drawLine(0, y_6db_bottom, width, y_6db_bottom)

        # 0 dB bottom — red
        painter.setPen(QPen(QColor("#ff0000"), 2, Qt.DashLine))
        painter.drawLine(0, height - 5, width, height - 5)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#1a1a1a"))
        painter.drawRect(5, height - 18, 45, 16)
        painter.setPen(QColor("#ff0000"))
        painter.drawText(8, height - 6, "0 dB")
