from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal
from ..health_dashboard import HealthDashboard


class RightPanel(QFrame):
    """Right panel: Preset summary and library health dashboard"""

    filter_requested = Signal(str)  # bubbles up to MainWindow

    def __init__(self, preset_manager):
        super().__init__()
        self.preset_manager = preset_manager
        self.setFrameStyle(QFrame.StyledPanel)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("📊 PRESET SUMMARY")
        title.setStyleSheet("font-weight: bold; color: #00ff88; font-size: 14px;")
        layout.addWidget(title)

        self.preset_info = QLabel()
        self.preset_info.setStyleSheet("color: white; padding: 10px;")
        self.preset_info.setWordWrap(True)
        layout.addWidget(self.preset_info)

        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("background-color: #444; margin: 10px 0;")
        layout.addWidget(divider)

        # Real interactive dashboard — replaces inline HTML labels
        self.health_dashboard = HealthDashboard()
        self.health_dashboard.filter_requested.connect(self.filter_requested.emit)
        layout.addWidget(self.health_dashboard)

        layout.addStretch()

        copyright_label = QLabel("© 2025 DJ-FUSE Audio Solutions\nDeckReady v2.0\nwww.github.com/ollyfuse")
        copyright_label.setStyleSheet("color: #666; font-size: 10px; padding: 10px;")
        copyright_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(copyright_label)

        self.update_preset_info(None)

    def update_preset_info(self, preset_key):
        if not preset_key:
            self.preset_info.setText("<i>No preset selected</i>")
            return
        preset = self.preset_manager.get_preset(preset_key)
        if not preset:
            self.preset_info.setText("<i>Invalid preset</i>")
            return
        self.preset_info.setText(f"""
<b>{preset['label']}</b><br>
<i>{preset['description']}</i><br><br>
<b>Target LUFS:</b> {preset['target_lufs']}<br>
<b>True Peak Limit:</b> {preset['true_peak']} dB<br>
<b>High-pass Filter:</b> {preset['highpass_hz']} Hz<br>
<b>Output Format:</b> {preset['output_format'].upper()}<br><br>
<b>EQ Settings:</b><br>
• Low: {preset['eq']['low_cut_db']} dB<br>
• Mid: {preset['eq']['mid_cut_db']} dB<br>
• High: {preset['eq']['high_boost_db']} dB
        """)

    def update_health_display(self, tracks):
        """Delegate to the real dashboard"""
        self.health_dashboard.update_health(tracks)
