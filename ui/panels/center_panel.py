from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QWidget, QTabWidget)
from PySide6.QtCore import Signal
from ..drag_drop_widget import DragDropWidget
from ..track_table import TrackTable
from ..folder_watch_panel import FolderWatchPanel


class CenterPanel(QFrame):
    """Center panel: Track library and folder monitoring"""
    
    # Signals
    files_dropped = Signal(list)  # file_paths
    add_tracks_clicked = Signal()
    clear_tracks_clicked = Signal()
    skip_track_requested = Signal(int)  # track_index
    remove_track_requested = Signal(int)  # track_index
    watch_added = Signal(str, dict)  # path, config
    watch_removed = Signal(str)  # path
    watch_toggled = Signal(str, bool)  # path, enabled
    
    def __init__(self, preset_manager, watch_config):
        super().__init__()
        self.preset_manager = preset_manager
        self.watch_config = watch_config
        
        self.setFrameStyle(QFrame.StyledPanel)
        self.setContentsMargins(0, 0, 0, 0)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup center panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Create tab widget
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #444;
                background-color: #2d2d2d;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: white;
                padding: 8px 16px;
                border: 1px solid #444;
            }
            QTabBar::tab:selected {
                background-color: #00ff88;
                color: black;
            }
        """)
        
        # Track Library Tab
        library_widget = QWidget()
        library_layout = QVBoxLayout(library_widget)
        library_layout.setContentsMargins(5, 5, 5, 5)
        library_layout.setSpacing(5)
        
        # Drag & drop area
        drop_area = DragDropWidget("📁 Drag & Drop Audio Files Here\n\nOr click 'Add Tracks' below")
        drop_area.files_dropped.connect(self.files_dropped.emit)
        library_layout.addWidget(drop_area)
        
        # Button layout
        button_layout = QHBoxLayout()
        add_button = QPushButton("+ Add Tracks")
        add_button.clicked.connect(self.add_tracks_clicked.emit)
        button_layout.addWidget(add_button)

        clear_button = QPushButton("🗑 Clear All")
        clear_button.clicked.connect(self.clear_tracks_clicked.emit)
        button_layout.addWidget(clear_button)

        library_layout.addLayout(button_layout)
        
        # Track table
        self.track_table = TrackTable()
        self.track_table.skip_track_requested.connect(self.skip_track_requested.emit)
        self.track_table.remove_track_requested.connect(self.remove_track_requested.emit)
        self.track_table.setContentsMargins(0, 0, 0, 0)
        library_layout.addWidget(self.track_table)

        # Folder Watch Tab
        self.folder_watch_panel = FolderWatchPanel(self.preset_manager, self.watch_config)
        self.folder_watch_panel.watch_added.connect(self.watch_added.emit)
        self.folder_watch_panel.watch_removed.connect(self.watch_removed.emit)
        self.folder_watch_panel.watch_toggled.connect(self.watch_toggled.emit)
        
        # Add tabs
        tabs.addTab(library_widget, "📚 Track Library")
        tabs.addTab(self.folder_watch_panel, "📁 Folder Monitoring")
        
        layout.addWidget(tabs)
    
    def get_track_table(self):
        """Get track table widget"""
        return self.track_table
    
    def get_folder_watch_panel(self):
        """Get folder watch panel widget"""
        return self.folder_watch_panel
