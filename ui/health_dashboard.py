from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel,
                                QPushButton, QGridLayout)
from PySide6.QtCore import Qt, Signal
from collections import Counter


class HealthDashboard(QFrame):
    """Interactive health summary — click issue badges to filter track table"""

    filter_requested = Signal(str)  # issue key, or '' to clear filter

    def __init__(self):
        super().__init__()
        self.tracks_data = []
        self._active_filter = ''
        self._filter_buttons = {}  # issue_key: QPushButton
        self.setup_ui()

    def setup_ui(self):
        self.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(8, 8, 8, 8)

        # Title row with "Show All" reset button
        title_row = QHBoxLayout()
        title = QLabel("💊 LIBRARY HEALTH")
        title.setStyleSheet("font-weight: bold; color: #00ff88; font-size: 13px;")
        title_row.addWidget(title)
        title_row.addStretch()

        self._show_all_btn = QPushButton("Show All")
        self._show_all_btn.setFixedHeight(22)
        self._show_all_btn.setStyleSheet("""
            QPushButton {
                background: #3d3d3d; border: 1px solid #555;
                border-radius: 3px; color: #aaa; font-size: 10px; padding: 0 8px;
            }
            QPushButton:hover { border-color: #00ff88; color: white; }
        """)
        self._show_all_btn.clicked.connect(self._clear_filter)
        title_row.addWidget(self._show_all_btn)
        layout.addLayout(title_row)

        # Health score
        self._score_label = QLabel("--")
        self._score_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #00ff88;")
        self._score_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._score_label)

        # Track count
        self._total_label = QLabel("No tracks loaded")
        self._total_label.setStyleSheet("color: #888; font-size: 11px;")
        self._total_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._total_label)

        # Score tier buttons — clickable, filter by tier
        tier_grid = QGridLayout()
        tier_grid.setSpacing(4)
        tier_data = [
            ('excellent', '🟢 Excellent', '#00aa44', 0, 0),
            ('good',      '🟡 Good',      '#88aa00', 0, 1),
            ('fair',      '🟠 Fair',      '#ffaa00', 1, 0),
            ('poor',      '🔴 Poor',      '#aa4444', 1, 1),
        ]
        for key, label, color, row, col in tier_data:
            btn = self._make_filter_btn(label, color, key)
            self._filter_buttons[key] = btn
            tier_grid.addWidget(btn, row, col)
        layout.addLayout(tier_grid)

        # Issue buttons — clickable, filter by specific issue
        issues_label = QLabel("Issues — click to filter:")
        issues_label.setStyleSheet("color: #666; font-size: 10px; margin-top: 4px;")
        layout.addWidget(issues_label)

        issue_data = [
            ('clipping',     '⚠️ Clipping',       '#ff4444'),
            ('too_quiet',    '🔇 Too Quiet',       '#ffaa00'),
            ('over_compressed', '📉 Compressed',   '#ffaa00'),
            ('low_quality',  '📁 Low Quality',     '#ffaa00'),
        ]
        for key, label, color in issue_data:
            btn = self._make_filter_btn(label, color, key)
            self._filter_buttons[key] = btn
            layout.addWidget(btn)

        layout.addStretch()

    def _make_filter_btn(self, label, color, issue_key):
        """Create a styled clickable filter button"""
        btn = QPushButton(label)
        btn.setFixedHeight(26)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: 1px solid #444;
                border-radius: 4px;
                color: {color};
                font-size: 11px;
                text-align: left;
                padding: 0 8px;
            }}
            QPushButton:hover {{
                background: #3d3d3d;
                border-color: {color};
            }}
        """)
        btn.clicked.connect(lambda _, k=issue_key: self._on_filter_clicked(k))
        return btn

    def _on_filter_clicked(self, issue_key):
        """Toggle filter — clicking active filter clears it"""
        if self._active_filter == issue_key:
            self._clear_filter()
        else:
            self._active_filter = issue_key
            self._highlight_active_button(issue_key)
            self.filter_requested.emit(issue_key)

    def _clear_filter(self):
        self._active_filter = ''
        self._highlight_active_button('')
        self.filter_requested.emit('')

    def _highlight_active_button(self, active_key):
        """Give active filter button a bright border, reset all others"""
        for key, btn in self._filter_buttons.items():
            current_style = btn.styleSheet()
            if key == active_key:
                btn.setStyleSheet(current_style.replace(
                    'border: 1px solid #444;',
                    'border: 2px solid #00ff88;'
                ))
            else:
                btn.setStyleSheet(current_style.replace(
                    'border: 2px solid #00ff88;',
                    'border: 1px solid #444;'
                ))

    def update_health(self, tracks_data):
        """Update all counts and labels from track data"""
        self.tracks_data = tracks_data

        if not tracks_data:
            self._score_label.setText("--")
            self._total_label.setText("No tracks loaded")
            for btn in self._filter_buttons.values():
                btn.setText(btn.text().split('(')[0].strip())
            return

        total = len(tracks_data)
        avg_score = int(sum(t.get('health_score', 0) for t in tracks_data) / total)

        self._score_label.setText(str(avg_score))
        self._score_label.setStyleSheet(
            f"font-size: 32px; font-weight: bold; color: {self._score_color(avg_score)};"
        )
        self._total_label.setText(f"{total} track{'s' if total != 1 else ''} loaded")

        # Tier counts
        excellent = sum(1 for t in tracks_data if t.get('health_score', 0) >= 80)
        good      = sum(1 for t in tracks_data if 60 <= t.get('health_score', 0) < 80)
        fair      = sum(1 for t in tracks_data if 40 <= t.get('health_score', 0) < 60)
        poor      = sum(1 for t in tracks_data if t.get('health_score', 0) < 40)

        self._filter_buttons['excellent'].setText(f"🟢 Excellent  ({excellent})")
        self._filter_buttons['good'].setText(f"🟡 Good  ({good})")
        self._filter_buttons['fair'].setText(f"🟠 Fair  ({fair})")
        self._filter_buttons['poor'].setText(f"🔴 Poor  ({poor})")

        # Issue counts
        all_issues = []
        for t in tracks_data:
            all_issues.extend(t.get('health_issues', []))
        c = Counter(all_issues)

        clipping    = c.get('clipping', 0) + c.get('near_clipping', 0)
        too_quiet   = c.get('too_quiet', 0)
        compressed  = c.get('over_compressed', 0) + c.get('low_crest_factor', 0)
        low_quality = c.get('low_bitrate', 0) + c.get('low_sample_rate', 0)

        self._filter_buttons['clipping'].setText(f"⚠️ Clipping  ({clipping})")
        self._filter_buttons['too_quiet'].setText(f"🔇 Too Quiet  ({too_quiet})")
        self._filter_buttons['over_compressed'].setText(f"📉 Compressed  ({compressed})")
        self._filter_buttons['low_quality'].setText(f"📁 Low Quality  ({low_quality})")

    def _score_color(self, score):
        if score >= 80: return "#00aa44"
        if score >= 60: return "#88aa00"
        if score >= 40: return "#ffaa00"
        return "#aa4444"
