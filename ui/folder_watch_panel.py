from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                               QListWidget, QListWidgetItem, QLabel, QFileDialog, QTextEdit)
from PySide6.QtCore import Qt, Signal
import os

class FolderWatchPanel(QWidget):
    """Panel for managing watched folders"""
    
    watch_added = Signal(str, dict)  # path, config
    watch_removed = Signal(str)  # path
    watch_toggled = Signal(str, bool)  # path, enabled
    
    def __init__(self, preset_manager, watch_config):
        super().__init__()
        self.preset_manager = preset_manager
        self.watch_config = watch_config
        self.init_ui()
        self.load_watched_folders()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("📁 FOLDER MONITORING")
        title.setStyleSheet("font-weight: bold; color: #00ff88; font-size: 14px;")
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Automatically process new audio files added to watched folders")
        desc.setStyleSheet("color: #999; font-size: 11px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Add folder button
        add_btn = QPushButton("➕ Add Watched Folder")
        add_btn.clicked.connect(self.add_watched_folder)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #00ff88;
                color: black;
                border: none;
                padding: 8px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #00cc6a;
            }
        """)
        layout.addWidget(add_btn)
        
        # Watched folders list
        self.folder_list = QListWidget()
        self.folder_list.setStyleSheet("""
            QListWidget {
                background-color: #1e1e1e;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #333;
            }
            QListWidget::item:selected {
                background-color: #2d2d2d;
            }
        """)
        layout.addWidget(self.folder_list)
        
        # Control buttons
        btn_layout = QHBoxLayout()
        
        self.remove_btn = QPushButton("🗑 Remove")
        self.remove_btn.clicked.connect(self.remove_selected)
        self.remove_btn.setEnabled(False)
        
        self.toggle_btn = QPushButton("⏸ Disable")
        self.toggle_btn.clicked.connect(self.toggle_selected)
        self.toggle_btn.setEnabled(False)
        
        btn_layout.addWidget(self.remove_btn)
        btn_layout.addWidget(self.toggle_btn)
        layout.addLayout(btn_layout)
        
        # Activity log
        log_label = QLabel("📋 Activity Log")
        log_label.setStyleSheet("font-weight: bold; color: #00ff88; font-size: 12px; margin-top: 10px;")
        layout.addWidget(log_label)
        
        self.activity_log = QTextEdit()
        self.activity_log.setReadOnly(True)
        self.activity_log.setMaximumHeight(150)
        self.activity_log.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                border: 1px solid #444;
                border-radius: 4px;
                color: #ccc;
                font-family: monospace;
                font-size: 10px;
            }
        """)
        layout.addWidget(self.activity_log)
        
        self.folder_list.itemSelectionChanged.connect(self.on_selection_changed)
    
    def add_watched_folder(self):
        """Add a new watched folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select Folder to Watch")
        if not folder:
            return
        
        from .dialogs import WatchFolderDialog
        dialog = WatchFolderDialog(self.preset_manager, folder, self)
        if dialog.exec():
            config = dialog.get_config()
            
            if self.watch_config.add_folder(
                folder,
                config['presetId'],
                config['autoProcess'],
                config['outputFolder'],
                config.get('deleteOriginal', False)  # NEW
            ):
                config['path'] = folder
                config['enabled'] = True
                
                self.add_folder_item(folder, config)
                self.watch_added.emit(folder, config)
                self.log_activity(f"Added watch folder: {folder}")
    
    def remove_selected(self):
        """Remove selected watched folder"""
        item = self.folder_list.currentItem()
        if not item:
            return
        
        folder_path = item.data(Qt.UserRole)
        self.watch_config.remove_folder(folder_path)
        self.folder_list.takeItem(self.folder_list.row(item))
        self.watch_removed.emit(folder_path)
        self.log_activity(f"Removed watch folder: {folder_path}")
    
    def toggle_selected(self):
        """Toggle enabled/disabled for selected folder"""
        item = self.folder_list.currentItem()
        if not item:
            return
        
        folder_path = item.data(Qt.UserRole)
        
        for config in self.watch_config.watched_folders:
            if config['path'] == folder_path:
                enabled = not config.get('enabled', True)
                config['enabled'] = enabled
                self.watch_config.save()
                
                self.update_folder_item(item, config)
                self.toggle_btn.setText("▶ Enable" if not enabled else "⏸ Disable")
                self.watch_toggled.emit(folder_path, enabled)
                
                status = "enabled" if enabled else "disabled"
                self.log_activity(f"Watch folder {status}: {folder_path}")
                break
    
    def on_selection_changed(self):
        """Handle selection change"""
        has_selection = self.folder_list.currentItem() is not None
        self.remove_btn.setEnabled(has_selection)
        self.toggle_btn.setEnabled(has_selection)
        
        if has_selection:
            item = self.folder_list.currentItem()
            folder_path = item.data(Qt.UserRole)
            
            for config in self.watch_config.watched_folders:
                if config['path'] == folder_path:
                    enabled = config.get('enabled', True)
                    self.toggle_btn.setText("⏸ Disable" if enabled else "▶ Enable")
                    break
    
    def load_watched_folders(self):
        """Load watched folders from config"""
        for config in self.watch_config.watched_folders:
            self.add_folder_item(config['path'], config)
    
    def add_folder_item(self, path, config):
        """Add folder item to list"""
        item = QListWidgetItem()
        item.setData(Qt.UserRole, path)
        self.update_folder_item(item, config)
        self.folder_list.addItem(item)
    
    def update_folder_item(self, item, config):
        """Update folder item display"""
        path = config['path']
        preset_id = config.get('presetId', 'unknown')
        enabled = config.get('enabled', True)
        auto = config.get('autoProcess', True)
        delete_orig = config.get('deleteOriginal', False)  # NEW
        
        preset = self.preset_manager.get_preset(preset_id)
        preset_label = preset['label'] if preset else preset_id
        
        status = "🟢" if enabled else "🔴"
        auto_text = "AUTO" if auto else "MANUAL"
        delete_text = " | 🗑 DEL" if delete_orig else ""  # NEW
        folder_name = os.path.basename(path)
        
        text = f"{status} {folder_name}\n   Preset: {preset_label} | {auto_text}{delete_text}"
        item.setText(text)
        
        if not enabled:
            item.setForeground(Qt.gray)
    
    def log_activity(self, message):
        """Add message to activity log"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.activity_log.append(f"[{timestamp}] {message}")
    
    def log_file_detected(self, file_path):
        """Log when a file is detected"""
        filename = os.path.basename(file_path)
        self.log_activity(f"Detected: {filename}")
    
    def log_file_processed(self, file_path, success):
        """Log when a file is processed"""
        filename = os.path.basename(file_path)
        status = "✓ Processed" if success else "✗ Failed"
        self.log_activity(f"{status}: {filename}")
