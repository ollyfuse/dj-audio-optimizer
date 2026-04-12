from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QMenu
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from .waveform_dialog import WaveformDialog
import os

class TrackTable(QTableWidget):
    skip_track_requested = Signal(int)
    remove_track_requested = Signal(int)
    
    def __init__(self):
        super().__init__()
        self.setup_table()
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
    def setup_table(self):
        self.setColumnCount(7)
        headers = ["Track", "Time", "Before", "After", "Peak", "Health", "Status"]
        self.setHorizontalHeaderLabels(headers)

        # Fixed widths for columns 0-5, column 6 (Status) stretches to fill
        widths = [0, 55, 70, 70, 60, 60]  # col 0 handled by stretch
        self.setColumnWidth(1, 55)
        self.setColumnWidth(2, 70)
        self.setColumnWidth(3, 70)
        self.setColumnWidth(4, 60)
        self.setColumnWidth(5, 60)

        self.setAlternatingRowColors(False)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        self.setSortingEnabled(False)
        self.horizontalHeader().setStretchLastSection(True)  
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch) 
        self.verticalHeader().setDefaultSectionSize(32)  
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def set_sorting_allowed(self, allowed):
        """Enable or disable sorting — must be off during processing"""
        self.setSortingEnabled(allowed)

    def show_context_menu(self, position):
        """Professional right-click menu"""
        item = self.itemAt(position)
        if not item:
            return
            
        row = item.row()
        status_item = self.item(row, 6)
        name_item = self.item(row, 0)
        track_path = name_item.data(Qt.UserRole) if name_item else None
                
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2d2d2d;
                color: white;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 20px;
            }
            QMenu::item:selected {
                background-color: #00ff88;
                color: black;
            }
        """)
        
        waveform_action = None
        if track_path:
            waveform_action = menu.addAction("📊 View Waveform")
            menu.addSeparator()
        
        skip_action = None
        if status_item and ("READY" in status_item.text() or "PROCESSING" in status_item.text()):
            skip_action = menu.addAction("🚫 Skip This Track")
        
        remove_action = menu.addAction("🗑 Remove Track")
        
        action = menu.exec(self.mapToGlobal(position))
        
        if action is not None:
            if waveform_action is not None and action == waveform_action:
                self.view_waveform(track_path)
            elif skip_action is not None and action == skip_action:
                self.skip_track_requested.emit(row)
            elif action == remove_action:
                self.remove_track_requested.emit(row)

    def view_waveform(self, track_path):
        """Open waveform dialog with before/after if processed"""
        for row in range(self.rowCount()):
            name_item = self.item(row, 0)
            if name_item and name_item.data(Qt.UserRole) == track_path:
                processed_path = name_item.data(Qt.UserRole + 1)
                if processed_path and os.path.exists(processed_path):
                    dialog = WaveformDialog(track_path, processed_path, parent=self)
                else:
                    dialog = WaveformDialog(track_path, parent=self)
                dialog.exec()
                return
        
        dialog = WaveformDialog(track_path, parent=self)
        dialog.exec()

    def add_track(self, track_data, target_lufs=None):
        row = self.rowCount()
        self.insertRow(row)

        name = track_data['name']
        if len(name) > 45:
            name = name[:42] + "..."
        name_item = self._create_item(name)
        name_item.setData(Qt.UserRole, track_data.get('path'))
        name_item.setData(Qt.UserRole + 2, track_data.get('health_issues', []))
        self.setItem(row, 0, name_item)

        duration = track_data.get('duration', 0)
        time_str = f"{int(duration//60)}:{int(duration%60):02d}" if duration > 0 else "0:00"
        self.setItem(row, 1, self._create_item(time_str, center=True))

        before_lufs = track_data['lufs']
        lufs_item = self._create_item(f"{before_lufs:.1f}", center=True)
        lufs_item.setData(Qt.UserRole, before_lufs)
        lufs_item.setBackground(self._get_lufs_color(before_lufs))
        if before_lufs < -16 or before_lufs > -6:
            lufs_item.setForeground(QColor("white"))
        self.setItem(row, 2, lufs_item)

        peak = track_data['peak_db']
        is_optimized = self._check_if_optimized(before_lufs, peak, target_lufs)

        if is_optimized:
            after_item = self._create_item(f"{before_lufs:.1f}", center=True)
            after_item.setBackground(QColor("#00aa44"))
            after_item.setForeground(QColor("white"))
            self.setItem(row, 3, after_item)
        else:
            self.setItem(row, 3, self._create_item(f"{target_lufs:.1f}" if target_lufs else "--", center=True))

        peak_item = self._create_item(f"{peak:.1f}", center=True)
        if peak > -1:
            peak_item.setBackground(QColor("#ff4444"))
            peak_item.setForeground(QColor("white"))
        self.setItem(row, 4, peak_item)

        health_score = track_data.get('health_score', 0)
        health_item = self._create_item(f"{health_score}", center=True)
        health_item.setBackground(self._get_health_color(health_score))
        health_item.setForeground(QColor("white"))
        self.setItem(row, 5, health_item)

        # Col 6 — combined status badge
        club_safe = self.is_club_safe(before_lufs, peak)
        if is_optimized:
            badge_text, badge_color = "✅ OPTIMIZED", "#00aa44"
        elif club_safe:
            badge_text, badge_color = "🟢 READY", "#00aa44"
        else:
            badge_text, badge_color = "⚠️ NEEDS FIX", "#aa4444"

        badge_item = self._create_item(badge_text, center=True)
        badge_item.setBackground(QColor(badge_color))
        badge_item.setForeground(QColor("white"))
        self.setItem(row, 6, badge_item)


    def _get_health_color(self, score):
        """Get color for health score"""
        if score >= 80:
            return QColor("#00aa44")
        elif score >= 60:
            return QColor("#88aa00")
        elif score >= 40:
            return QColor("#ffaa00")
        else:
            return QColor("#aa4444")

    def _check_if_optimized(self, lufs, peak, target_lufs):
        """Check if track is already optimized with smart tolerance"""
        if target_lufs is None:
            return False
        
        if target_lufs >= -10:
            tolerance = 2.0
        elif target_lufs >= -14:
            tolerance = 1.5
        else:
            tolerance = 1.0
        
        return abs(lufs - target_lufs) <= tolerance and peak < 0.0

    def update_track_status(self, row, status):
        status_configs = {
            'processing': ("⚡ PROCESSING", "#ffaa00", "black"),
            'completed':  ("✅ DONE",       "#00aa44", "white"),
            'skipped':    ("⏭ SKIPPED",    "#666666", "white"),
            'error':      ("❌ ERROR",      "#aa4444", "white"),
        }
        if status in status_configs:
            text, bg, fg = status_configs[status]
            item = self._create_item(text, center=True)
            item.setBackground(QColor(bg))
            item.setForeground(QColor(fg))
            self.setItem(row, 6, item)


    def update_after_processing(self, row, after_lufs, final_peak):
        after_item = self._create_item(f"{after_lufs:.1f}", center=True)
        after_item.setBackground(QColor("#00aa44"))
        after_item.setForeground(QColor("white"))

        before_item = self.item(row, 2)
        if before_item:
            try:
                before_lufs = before_item.data(Qt.UserRole)
                if before_lufs is not None:
                    improvement = after_lufs - float(before_lufs)
                    sign = "+" if improvement > 0 else ""
                    after_item.setToolTip(f"Gain: {sign}{improvement:.1f} dB")
            except (TypeError, ValueError):
                pass

        self.setItem(row, 3, after_item)

        club_safe = self.is_club_safe(after_lufs, final_peak)
        badge_text = "✅ CLUB SAFE" if club_safe else "🟡 IMPROVED"
        badge_item = self._create_item(badge_text, center=True)
        badge_item.setBackground(QColor("#00aa44") if club_safe else QColor("#ffaa00"))
        badge_item.setForeground(QColor("white"))
        self.setItem(row, 6, badge_item)


    def _create_item(self, text, center=False):
        """Create styled table item"""
        item = QTableWidgetItem(str(text))
        if center:
            item.setTextAlignment(Qt.AlignCenter)
        return item

    def _get_lufs_color(self, lufs):
        """Get color for LUFS value"""
        if lufs < -16:
            return QColor("#aa4444")
        elif lufs > -6:
            return QColor("#ffaa00")
        else:
            return QColor("transparent")

    def is_club_safe(self, lufs, peak_db):
        """Professional club-safe criteria"""
        return -14 <= lufs <= -8 and peak_db < 0.0

    def get_track_count(self):
        return self.rowCount()
    
    def update_target_lufs(self, target_lufs):
        if target_lufs is None:
            return
        for row in range(self.rowCount()):
            after_item = self.item(row, 3)
            if after_item and after_item.text() == "--":
                self.setItem(row, 3, self._create_item(f"{target_lufs:.1f}", center=True))


    def apply_filter(self, issue_key):
        tier_ranges = {
            'excellent': (80, 101),
            'good':      (60, 80),
            'fair':      (40, 60),
            'poor':      (0,  40),
        }
        for row in range(self.rowCount()):
            name_item   = self.item(row, 0)
            health_item = self.item(row, 5)
            if not name_item:
                continue
            if issue_key in tier_ranges:
                try:
                    score = int(health_item.text()) if health_item else 0
                except ValueError:
                    score = 0
                low, high = tier_ranges[issue_key]
                self.setRowHidden(row, not (low <= score < high))
            else:
                issues = name_item.data(Qt.UserRole + 2) or []
                if issue_key == 'clipping':
                    match = 'clipping' in issues or 'near_clipping' in issues
                elif issue_key == 'low_quality':
                    match = 'low_bitrate' in issues or 'low_sample_rate' in issues
                elif issue_key == 'over_compressed':
                    match = 'over_compressed' in issues or 'low_crest_factor' in issues
                else:
                    match = issue_key in issues
                self.setRowHidden(row, not match)


    def clear_filter(self):
        """Show all rows"""
        for row in range(self.rowCount()):
            self.setRowHidden(row, False)

