from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Qt


class RightPanel(QFrame):
    """Right panel: Preset summary and library health dashboard"""
    
    def __init__(self, preset_manager):
        super().__init__()
        self.preset_manager = preset_manager
        
        self.setFrameStyle(QFrame.StyledPanel)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup right panel UI"""
        layout = QVBoxLayout(self)
        
        # Preset summary title
        title = QLabel("📊 PRESET SUMMARY")
        title.setStyleSheet("font-weight: bold; color: #00ff88; font-size: 14px;")
        layout.addWidget(title)
        
        # Preset info
        self.preset_info = QLabel()
        self.preset_info.setStyleSheet("color: white; padding: 10px;")
        self.preset_info.setWordWrap(True)
        layout.addWidget(self.preset_info)
        
        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("background-color: #444; margin: 10px 0;")
        layout.addWidget(divider)
        
        # Health Dashboard
        health_title = QLabel("💊 LIBRARY HEALTH")
        health_title.setStyleSheet("font-weight: bold; color: #00ff88; font-size: 14px;")
        layout.addWidget(health_title)
        
        # Health score (big number)
        self.health_score_label = QLabel("--")
        self.health_score_label.setStyleSheet("""
            font-size: 36px; 
            font-weight: bold; 
            color: #00ff88;
            padding: 10px;
        """)
        self.health_score_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.health_score_label)
        
        # Health breakdown
        self.health_breakdown = QLabel()
        self.health_breakdown.setStyleSheet("color: white; padding: 5px; font-size: 11px;")
        self.health_breakdown.setWordWrap(True)
        layout.addWidget(self.health_breakdown)
        
        layout.addStretch()
        
        # Copyright section
        copyright_label = QLabel("© 2026 DJ-FUSE\nProfessional DJ Audio Optimizer\nv2.0")
        copyright_label.setStyleSheet('''
            color: #666; 
            font-size: 10px; 
            padding: 10px;
            text-align: center;
        ''')
        copyright_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(copyright_label)
        
        # Initialize displays
        self.update_preset_info(None)
        self.update_health_display([])
    
    def update_preset_info(self, preset_key):
        """Update preset summary display"""
        if not preset_key:
            self.preset_info.setText("<i>No preset selected</i>")
            return
        
        preset = self.preset_manager.get_preset(preset_key)
        if not preset:
            self.preset_info.setText("<i>Invalid preset</i>")
            return
        
        info_text = f"""
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
        """
        self.preset_info.setText(info_text)
    
    def update_health_display(self, tracks):
        """Update library health dashboard"""
        if not tracks:
            self.health_score_label.setText("--")
            self.health_breakdown.setText("<i>No tracks loaded</i>")
            return
        
        # Calculate overall health
        total_tracks = len(tracks)
        total_score = sum(t.get('health_score', 0) for t in tracks)
        avg_score = int(total_score / total_tracks) if total_tracks > 0 else 0
        
        # Update score with color
        score_color = self._get_health_color(avg_score)
        self.health_score_label.setText(str(avg_score))
        self.health_score_label.setStyleSheet(f"""
            font-size: 36px; 
            font-weight: bold; 
            color: {score_color};
            padding: 10px;
        """)
        
        # Count by status
        excellent = sum(1 for t in tracks if t.get('health_score', 0) >= 80)
        good = sum(1 for t in tracks if 60 <= t.get('health_score', 0) < 80)
        fair = sum(1 for t in tracks if 40 <= t.get('health_score', 0) < 60)
        poor = sum(1 for t in tracks if t.get('health_score', 0) < 40)
        
        # Count issues
        from collections import Counter
        all_issues = []
        for track in tracks:
            all_issues.extend(track.get('health_issues', []))
        
        issue_counts = Counter(all_issues)
        clipping = issue_counts.get('clipping', 0) + issue_counts.get('near_clipping', 0)
        quiet = issue_counts.get('too_quiet', 0)
        compressed = issue_counts.get('over_compressed', 0)
        
        # Build compact breakdown text
        breakdown_text = f"""
<b>{total_tracks} tracks loaded</b><br><br>

<span style='color: #00aa44;'>🟢 {excellent} Excellent</span><br>
<span style='color: #88aa00;'>🟡 {good} Good</span><br>
<span style='color: #ffaa00;'>🟠 {fair} Fair</span><br>
<span style='color: #aa4444;'>🔴 {poor} Poor</span><br><br>

<b>Issues:</b><br>
<span style='color: #ff4444;'>⚠️ {clipping} Clipping</span><br>
<span style='color: #ffaa00;'>🔇 {quiet} Too Quiet</span><br>
<span style='color: #ffaa00;'>📉 {compressed} Compressed</span>
        """
        
        self.health_breakdown.setText(breakdown_text)
    
    def _get_health_color(self, score):
        """Get color for health score"""
        if score >= 80:
            return "#00aa44"
        elif score >= 60:
            return "#88aa00"
        elif score >= 40:
            return "#ffaa00"
        else:
            return "#aa4444"
