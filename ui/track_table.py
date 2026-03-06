from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QMenu
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

class TrackTable(QTableWidget):
    skip_track_requested = Signal(int)
    remove_track_requested = Signal(int)
    
    def __init__(self):
        super().__init__()
        self.setup_table()
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
    def setup_table(self):
        """Setup professional table layout and styling"""
        self.setColumnCount(9)
        headers = ["Track", "Time", "Before", "After", "Peak", "Health", "Club Safe", "Gain", "Status"]
        self.setHorizontalHeaderLabels(headers)
        
        widths = [280, 60, 80, 80, 70, 70, 90, 70, 100]
        for i, width in enumerate(widths):
            self.setColumnWidth(i, width)
        
        # Disable alternating row colors - they override cell backgrounds
        self.setAlternatingRowColors(False)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.verticalHeader().setVisible(False)
        self.setShowGrid(False)
        self.setSortingEnabled(True)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setDefaultSectionSize(40)


    def show_context_menu(self, position):
        """Professional right-click menu"""
        item = self.itemAt(position)
        if not item:
            return
            
        row = item.row()
        status_item = self.item(row, 8)
        
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2d2d2d;
                color: white;
                border: 1px solid #444;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #00ff88;
                color: black;
            }
        """)
        
        if status_item and ("READY" in status_item.text() or "PROCESSING" in status_item.text()):
            skip_action = menu.addAction("🚫 Skip This Track")
        else:
            skip_action = None
        
        remove_action = menu.addAction("🗑️ Remove Track")
        
        action = menu.exec(self.mapToGlobal(position))
        
        if action == skip_action and skip_action:
            self.skip_track_requested.emit(row)
        elif action == remove_action:
            self.remove_track_requested.emit(row)

    def add_track(self, track_data, target_lufs=None):
        """Add track with professional formatting and optimization detection"""
        row = self.rowCount()
        self.insertRow(row)
        
        # Track name
        name = track_data['name']
        if len(name) > 40:
            name = name[:37] + "..."
        self.setItem(row, 0, self._create_item(name))
        
        # Duration
        duration = track_data.get('duration', 0)
        if duration > 0:
            time_str = f"{int(duration//60)}:{int(duration%60):02d}"
        else:
            time_str = "0:00"
        self.setItem(row, 1, self._create_item(time_str, center=True))
        
        # Before LUFS
        before_lufs = track_data['lufs']
        lufs_item = self._create_item(f"{before_lufs:.1f}", center=True)
        lufs_item.setBackground(self._get_lufs_color(before_lufs))
        if before_lufs < -16 or before_lufs > -6:
            lufs_item.setForeground(QColor("white"))
        self.setItem(row, 2, lufs_item)
        
        # After LUFS - check if already optimized
        peak = track_data['peak_db']
        is_optimized = self._check_if_optimized(before_lufs, peak, target_lufs)
        
        if is_optimized:
            after_item = self._create_item(f"{before_lufs:.1f}", center=True)
            after_item.setBackground(QColor("#00aa44"))
            after_item.setForeground(QColor("white"))
            self.setItem(row, 3, after_item)
        else:
            if target_lufs:
                self.setItem(row, 3, self._create_item(f"{target_lufs:.1f}", center=True))
            else:
                self.setItem(row, 3, self._create_item("--", center=True))
        
        # Peak
        peak_item = self._create_item(f"{peak:.1f}", center=True)
        if peak > -1:
            peak_item.setBackground(QColor("#ff4444"))
            peak_item.setForeground(QColor("white"))
        self.setItem(row, 4, peak_item)
        
        # Health Score (NEW!)
        health_score = track_data.get('health_score', 0)
        health_item = self._create_item(f"{health_score}", center=True)
        health_item.setBackground(self._get_health_color(health_score))
        health_item.setForeground(QColor("white"))
        self.setItem(row, 5, health_item)
        
        # Club Safe badge
        club_safe = self.is_club_safe(before_lufs, peak)
        if is_optimized and club_safe:
            badge_text = "🟢 OPTIMIZED"
            badge_color = "#00aa44"
        elif club_safe:
            badge_text = "🟢 SAFE"
            badge_color = "#00aa44"
        else:
            badge_text = "🔴 FIX"
            badge_color = "#aa4444"
        
        badge_item = self._create_item(badge_text, center=True)
        badge_item.setBackground(QColor(badge_color))
        badge_item.setForeground(QColor("white"))
        self.setItem(row, 6, badge_item)
        
        # Gain
        if is_optimized:
            gain_item = self._create_item("✓", center=True)
            gain_item.setBackground(QColor("#00aa44"))
            gain_item.setForeground(QColor("white"))
            self.setItem(row, 7, gain_item)
        else:
            self.setItem(row, 7, self._create_item("--", center=True))
        
        # Status
        if is_optimized:
            status_item = self._create_item("✅ OPTIMIZED", center=True)
            status_item.setBackground(QColor("#00aa44"))
            status_item.setForeground(QColor("white"))
        else:
            status_item = self._create_item("READY", center=True)
            status_item.setBackground(QColor("#4444aa"))
            status_item.setForeground(QColor("white"))
        self.setItem(row, 8, status_item)

    def _get_health_color(self, score):
        """Get color for health score"""
        if score >= 80:
            return QColor("#00aa44")  # Excellent - Green
        elif score >= 60:
            return QColor("#88aa00")  # Good - Yellow-green
        elif score >= 40:
            return QColor("#ffaa00")  # Fair - Orange
        else:
            return QColor("#aa4444")  # Poor - Red

    def _check_if_optimized(self, lufs, peak, target_lufs):
        """
        Check if track is already optimized with smart tolerance
        """
        if target_lufs is None:
            return False
        
        # Smart tolerance based on target LUFS
        if target_lufs >= -10:  # Club/Festival range
            tolerance = 2.0
        elif target_lufs >= -14:  # Bar/Streaming range
            tolerance = 1.5
        else:  # Radio/Broadcast range
            tolerance = 1.0
        
        lufs_ok = abs(lufs - target_lufs) <= tolerance
        
        # Peak should be below 0 dB (negative value)
        # -0.2 dB is safe, 0.6 dB is clipping
        peak_ok = peak < 0.0
        
        # Also check if track is already in "club safe" range
        in_club_range = -14 <= lufs <= -8 and peak_ok
        
        return lufs_ok and peak_ok



    def update_track_status(self, row, status):
        """Update status with professional styling"""
        status_configs = {
            'processing': ("⚡ PROCESSING", "#ffaa00", "black"),
            'completed': ("✅ DONE", "#00aa44", "white"),
            'skipped': ("🚫 SKIP", "#666666", "white"),
            'error': ("❌ ERROR", "#aa4444", "white"),
            'optimized': ("✅ OPTIMIZED", "#00aa44", "white")
        }
        
        if status in status_configs:
            text, bg_color, fg_color = status_configs[status]
            status_item = self._create_item(text, center=True)
            status_item.setBackground(QColor(bg_color))
            status_item.setForeground(QColor(fg_color))
            self.setItem(row, 8, status_item)

    def update_after_processing(self, row, after_lufs, final_peak):
        """Update with processing results"""
        # After LUFS
        after_item = self._create_item(f"{after_lufs:.1f}", center=True)
        after_item.setBackground(QColor("#00aa44"))
        after_item.setForeground(QColor("white"))
        self.setItem(row, 3, after_item)
        
        # Calculate improvement
        before_item = self.item(row, 2)
        if before_item:
            before_lufs = float(before_item.text())
            improvement = after_lufs - before_lufs
            gain_text = f"+{improvement:.1f}" if improvement > 0 else f"{improvement:.1f}"
            gain_item = self._create_item(gain_text, center=True)
            gain_item.setBackground(QColor("#00aa44") if improvement > 0 else QColor("#ffaa00"))
            gain_item.setForeground(QColor("white"))
            self.setItem(row, 7, gain_item)
        
        # Update Club Safe
        club_safe = self.is_club_safe(after_lufs, final_peak)
        badge_text = "🟢 CLUB SAFE" if club_safe else "🟡 BETTER"
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
        """Update target LUFS display - with null check"""
        for row in range(self.rowCount()):
            after_item = self.item(row, 3)
            # Only update if item exists and is placeholder
            if after_item and after_item.text() == "--":
                self.setItem(row, 3, self._create_item(f"{target_lufs:.1f}", center=True))
