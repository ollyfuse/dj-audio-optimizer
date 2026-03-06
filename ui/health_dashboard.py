"""
Health Dashboard Widget
Shows library health summary with visual indicators
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from collections import Counter

class HealthDashboard(QFrame):
    """Visual health summary dashboard"""
    
    filter_requested = Signal(str)  # Signal to filter tracks by issue
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.tracks_data = []
    
    def setup_ui(self):
        """Setup dashboard layout"""
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border: 2px solid #00ff88;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("📊 LIBRARY HEALTH")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #00ff88;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Stats row
        stats_layout = QHBoxLayout()
        
        # Overall health score
        self.health_score_label = QLabel("--")
        self.health_score_label.setStyleSheet("""
            font-size: 48px; 
            font-weight: bold; 
            color: #00ff88;
        """)
        self.health_score_label.setAlignment(Qt.AlignCenter)
        
        score_container = QVBoxLayout()
        score_container.addWidget(self.health_score_label)
        score_label = QLabel("Health Score")
        score_label.setStyleSheet("color: #888; font-size: 12px;")
        score_label.setAlignment(Qt.AlignCenter)
        score_container.addWidget(score_label)
        
        stats_layout.addLayout(score_container)
        
        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.VLine)
        divider.setStyleSheet("background-color: #444;")
        stats_layout.addWidget(divider)
        
        # Issue breakdown
        issues_layout = QVBoxLayout()
        
        self.total_tracks_label = QLabel("0 tracks")
        self.total_tracks_label.setStyleSheet("color: white; font-size: 14px;")
        issues_layout.addWidget(self.total_tracks_label)
        
        self.excellent_label = QLabel("🟢 0 Excellent")
        self.excellent_label.setStyleSheet("color: #00aa44;")
        issues_layout.addWidget(self.excellent_label)
        
        self.good_label = QLabel("🟡 0 Good")
        self.good_label.setStyleSheet("color: #88aa00;")
        issues_layout.addWidget(self.good_label)
        
        self.fair_label = QLabel("🟠 0 Fair")
        self.fair_label.setStyleSheet("color: #ffaa00;")
        issues_layout.addWidget(self.fair_label)
        
        self.poor_label = QLabel("🔴 0 Poor")
        self.poor_label.setStyleSheet("color: #aa4444;")
        issues_layout.addWidget(self.poor_label)
        
        stats_layout.addLayout(issues_layout)
        
        # Divider
        divider2 = QFrame()
        divider2.setFrameShape(QFrame.VLine)
        divider2.setStyleSheet("background-color: #444;")
        stats_layout.addWidget(divider2)
        
        # Common issues
        issues_list_layout = QVBoxLayout()
        
        issues_title = QLabel("Common Issues:")
        issues_title.setStyleSheet("color: #888; font-size: 12px; font-weight: bold;")
        issues_list_layout.addWidget(issues_title)
        
        self.clipping_label = QLabel("⚠️ 0 Clipping")
        self.clipping_label.setStyleSheet("color: #ff4444;")
        issues_list_layout.addWidget(self.clipping_label)
        
        self.quiet_label = QLabel("🔇 0 Too Quiet")
        self.quiet_label.setStyleSheet("color: #ffaa00;")
        issues_list_layout.addWidget(self.quiet_label)
        
        self.compressed_label = QLabel("📉 0 Over-compressed")
        self.compressed_label.setStyleSheet("color: #ffaa00;")
        issues_list_layout.addWidget(self.compressed_label)
        
        self.low_quality_label = QLabel("📁 0 Low Quality")
        self.low_quality_label.setStyleSheet("color: #ffaa00;")
        issues_list_layout.addWidget(self.low_quality_label)
        
        stats_layout.addLayout(issues_list_layout)
        
        layout.addLayout(stats_layout)
        
        # Initially hidden
        self.setVisible(False)
    
    def update_health(self, tracks_data):
        """Update dashboard with track health data"""
        self.tracks_data = tracks_data
        
        if not tracks_data:
            self.setVisible(False)
            return
        
        self.setVisible(True)
        
        # Calculate overall health
        total_tracks = len(tracks_data)
        total_score = sum(t.get('health_score', 0) for t in tracks_data)
        avg_score = int(total_score / total_tracks) if total_tracks > 0 else 0
        
        # Update score with color
        self.health_score_label.setText(str(avg_score))
        self.health_score_label.setStyleSheet(f"""
            font-size: 48px; 
            font-weight: bold; 
            color: {self._get_score_color(avg_score)};
        """)
        
        # Count by status
        excellent = sum(1 for t in tracks_data if t.get('health_score', 0) >= 80)
        good = sum(1 for t in tracks_data if 60 <= t.get('health_score', 0) < 80)
        fair = sum(1 for t in tracks_data if 40 <= t.get('health_score', 0) < 60)
        poor = sum(1 for t in tracks_data if t.get('health_score', 0) < 40)
        
        self.total_tracks_label.setText(f"{total_tracks} tracks loaded")
        self.excellent_label.setText(f"🟢 {excellent} Excellent")
        self.good_label.setText(f"🟡 {good} Good")
        self.fair_label.setText(f"🟠 {fair} Fair")
        self.poor_label.setText(f"🔴 {poor} Poor")
        
        # Count issues
        all_issues = []
        for track in tracks_data:
            all_issues.extend(track.get('health_issues', []))
        
        issue_counts = Counter(all_issues)
        
        clipping = issue_counts.get('clipping', 0) + issue_counts.get('near_clipping', 0)
        quiet = issue_counts.get('too_quiet', 0)
        compressed = issue_counts.get('over_compressed', 0) + issue_counts.get('low_crest_factor', 0)
        low_quality = issue_counts.get('low_bitrate', 0) + issue_counts.get('low_sample_rate', 0)
        
        self.clipping_label.setText(f"⚠️ {clipping} Clipping")
        self.quiet_label.setText(f"🔇 {quiet} Too Quiet")
        self.compressed_label.setText(f"📉 {compressed} Over-compressed")
        self.low_quality_label.setText(f"📁 {low_quality} Low Quality")
    
    def _get_score_color(self, score):
        """Get color for health score"""
        if score >= 80:
            return "#00aa44"
        elif score >= 60:
            return "#88aa00"
        elif score >= 40:
            return "#ffaa00"
        else:
            return "#aa4444"
