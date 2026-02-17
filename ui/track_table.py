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
        self.setColumnCount(8)
        headers = ["Track", "Time", "Before", "After", "Peak", "Club Safe", "Gain", "Status"]
        self.setHorizontalHeaderLabels(headers)
        
        # Optimized column widths
        widths = [300, 60, 80, 80, 70, 90, 70, 100]
        for i, width in enumerate(widths):
            self.setColumnWidth(i, width)
        
        # Professional styling
        self.setAlternatingRowColors(True)
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
        status_item = self.item(row, 7)
        
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
        
        # Skip option for pending/processing tracks
        if status_item and ("READY" in status_item.text() or "PROCESSING" in status_item.text()):
            skip_action = menu.addAction("🚫 Skip This Track")
        else:
            skip_action = None
        
        # Remove option for all tracks
        remove_action = menu.addAction("🗑️ Remove Track")
        
        action = menu.exec(self.mapToGlobal(position))
        
        if action == skip_action and skip_action:
            self.skip_track_requested.emit(row)
        elif action == remove_action:
            self.remove_track_requested.emit(row)


    def add_track(self, track_data):
        """Add track with professional formatting"""
        row = self.rowCount()
        self.insertRow(row)
        
        # Track name - clean truncation
        name = track_data['name']
        if len(name) > 40:
            name = name[:37] + "..."
        self.setItem(row, 0, self._create_item(name))
        
        # Duration - clean format
        duration = track_data.get('duration', 0)
        time_str = f"{int(duration//60)}:{int(duration%60):02d}"
        self.setItem(row, 1, self._create_item(time_str, center=True))
        
        # Before LUFS with color coding
        before_lufs = track_data['lufs']
        lufs_item = self._create_item(f"{before_lufs:.1f}", center=True)
        lufs_item.setBackground(self._get_lufs_color(before_lufs))
        if before_lufs < -16 or before_lufs > -6:
            lufs_item.setForeground(QColor("white"))
        self.setItem(row, 2, lufs_item)
        
        # After LUFS - placeholder
        self.setItem(row, 3, self._create_item("--", center=True))
        
        # Peak with color coding
        peak = track_data['peak_db']
        peak_item = self._create_item(f"{peak:.1f}", center=True)
        if peak > -1:
            peak_item.setBackground(QColor("#ff4444"))
            peak_item.setForeground(QColor("white"))
        self.setItem(row, 4, peak_item)
        
        # Club Safe badge
        club_safe = self.is_club_safe(before_lufs, peak)
        badge_text = "🟢 SAFE" if club_safe else "🔴 FIX"
        badge_item = self._create_item(badge_text, center=True)
        badge_item.setBackground(QColor("#00aa44") if club_safe else QColor("#aa4444"))
        badge_item.setForeground(QColor("white"))
        self.setItem(row, 5, badge_item)
        
        # Improvement placeholder
        self.setItem(row, 6, self._create_item("--", center=True))
        
        # Status
        status_item = self._create_item("READY", center=True)
        status_item.setBackground(QColor("#4444aa"))
        status_item.setForeground(QColor("white"))
        self.setItem(row, 7, status_item)

    def update_track_status(self, row, status):
        """Update status with professional styling"""
        status_configs = {
            'processing': ("⚡ PROCESSING", "#ffaa00", "black"),
            'completed': ("✅ DONE", "#00aa44", "white"),
            'skipped': ("🚫 SKIP", "#666666", "white"),
            'error': ("❌ ERROR", "#aa4444", "white")
        }
        
        if status in status_configs:
            text, bg_color, fg_color = status_configs[status]
            status_item = self._create_item(text, center=True)
            status_item.setBackground(QColor(bg_color))
            status_item.setForeground(QColor(fg_color))
            self.setItem(row, 7, status_item)

    def update_after_processing(self, row, after_lufs, final_peak):
        """Update with processing results"""
        # After LUFS
        after_item = self._create_item(f"{after_lufs:.1f}", center=True)
        after_item.setBackground(QColor("#00aa44"))
        after_item.setForeground(QColor("white"))
        self.setItem(row, 3, after_item)
        
        # Calculate improvement
        before_lufs = float(self.item(row, 2).text())
        improvement = after_lufs - before_lufs
        gain_text = f"+{improvement:.1f}" if improvement > 0 else f"{improvement:.1f}"
        gain_item = self._create_item(gain_text, center=True)
        gain_item.setBackground(QColor("#00aa44") if improvement > 0 else QColor("#ffaa00"))
        gain_item.setForeground(QColor("white"))
        self.setItem(row, 6, gain_item)
        
        # Update Club Safe
        club_safe = self.is_club_safe(after_lufs, final_peak)
        badge_text = "🟢 CLUB SAFE" if club_safe else "🟡 BETTER"
        badge_item = self._create_item(badge_text, center=True)
        badge_item.setBackground(QColor("#00aa44") if club_safe else QColor("#ffaa00"))
        badge_item.setForeground(QColor("white"))
        self.setItem(row, 5, badge_item)

    def _create_item(self, text, center=False):
        """Create styled table item"""
        item = QTableWidgetItem(str(text))
        if center:
            item.setTextAlignment(Qt.AlignCenter)
        return item

    def _get_lufs_color(self, lufs):
        """Get color for LUFS value"""
        if lufs < -16:
            return QColor("#aa4444")  # Too quiet - red
        elif lufs > -6:
            return QColor("#ffaa00")  # Too loud - orange
        else:
            return QColor("transparent")  # Good range

    def is_club_safe(self, lufs, peak_db):
        """Professional club-safe criteria"""
        return -14 <= lufs <= -8 and peak_db < -1

    def get_track_count(self):
        return self.rowCount()
    
    def update_target_lufs(self, target_lufs):
        """Update target LUFS display"""
        for row in range(self.rowCount()):
            if self.item(row, 3).text() == "--":
                self.setItem(row, 3, self._create_item(f"{target_lufs:.1f}", center=True))
