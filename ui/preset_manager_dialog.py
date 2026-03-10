from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget, 
                               QListWidgetItem, QPushButton, QMessageBox, QInputDialog)
from PySide6.QtCore import Qt
from .preset_editor_dialog import PresetEditorDialog

class PresetManagerDialog(QDialog):
    """Manage presets - list, create, edit, duplicate, delete"""
    
    def __init__(self, preset_manager, parent=None):
        super().__init__(parent)
        self.preset_manager = preset_manager
        self.setup_ui()
        self.load_presets()
    
    def setup_ui(self):
        """Build the dialog UI"""
        self.setWindowTitle("⚙️ Manage Presets")
        self.setMinimumSize(600, 400)
        
        layout = QHBoxLayout(self)
        
        # Left side: Preset list
        left_layout = QVBoxLayout()
        
        self.preset_list = QListWidget()
        self.preset_list.itemDoubleClicked.connect(self.edit_preset)
        self.preset_list.itemSelectionChanged.connect(self.update_button_states)  # ADD THIS LINE
        left_layout.addWidget(self.preset_list)

        
        layout.addLayout(left_layout, 3)
        
        # Right side: Action buttons
        right_layout = QVBoxLayout()
        
        self.new_btn = QPushButton("➕ New Preset")
        self.new_btn.clicked.connect(self.new_preset)
        right_layout.addWidget(self.new_btn)
        
        self.edit_btn = QPushButton("✏️ Edit")
        self.edit_btn.clicked.connect(self.edit_preset)
        right_layout.addWidget(self.edit_btn)
        
        self.duplicate_btn = QPushButton("📋 Duplicate")
        self.duplicate_btn.clicked.connect(self.duplicate_preset)
        right_layout.addWidget(self.duplicate_btn)
        
        self.delete_btn = QPushButton("🗑 Delete")
        self.delete_btn.clicked.connect(self.delete_preset)
        right_layout.addWidget(self.delete_btn)
        
        right_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        right_layout.addWidget(close_btn)
        
        layout.addLayout(right_layout, 1)
        
        self.apply_dark_theme()
    
    def load_presets(self):
        """Load all presets into list"""
        self.preset_list.clear()
        
        presets = self.preset_manager.get_preset_list()
        
        for preset in presets:
            # Create list item
            item = QListWidgetItem()
            
            # Format: "🔒 Club / Festival (Default)" or "✏️ My Custom Preset"
            icon = "🔒" if preset['locked'] else "✏️"
            suffix = " (Default)" if preset['locked'] else ""
            text = f"{icon} {preset['label']}{suffix}"
            
            item.setText(text)
            item.setData(Qt.UserRole, preset['id'])  # Store preset ID
            item.setData(Qt.UserRole + 1, preset['locked'])  # Store locked status
            
            self.preset_list.addItem(item)
        
        # Update button states
        self.update_button_states()
    
    def update_button_states(self):
        """Enable/disable buttons based on selection"""
        current_item = self.preset_list.currentItem()
        
        if current_item:
            is_locked = current_item.data(Qt.UserRole + 1)
            self.edit_btn.setEnabled(not is_locked)
            self.delete_btn.setEnabled(not is_locked)
            self.duplicate_btn.setEnabled(True)
        else:
            self.edit_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
            self.duplicate_btn.setEnabled(False)
    
    def new_preset(self):
        """Create new preset"""
        dialog = PresetEditorDialog(self.preset_manager, parent=self)
        if dialog.exec():
            self.load_presets()
    
    def edit_preset(self):
        """Edit selected preset"""
        current_item = self.preset_list.currentItem()
        if not current_item:
            return
        
        preset_id = current_item.data(Qt.UserRole)
        is_locked = current_item.data(Qt.UserRole + 1)
        
        if is_locked:
            QMessageBox.warning(self, "Locked Preset", 
                              "Default presets cannot be edited.\nUse 'Duplicate' to create a custom version.")
            return
        
        dialog = PresetEditorDialog(self.preset_manager, preset_id, parent=self)
        if dialog.exec():
            self.load_presets()
    
    def duplicate_preset(self):
        """Duplicate selected preset"""
        current_item = self.preset_list.currentItem()
        if not current_item:
            return
        
        source_id = current_item.data(Qt.UserRole)
        source_preset = self.preset_manager.get_preset(source_id)
        
        # Ask for new name
        new_name, ok = QInputDialog.getText(
            self, "Duplicate Preset",
            f"Enter name for duplicated preset:",
            text=f"{source_preset['label']} Copy"
        )
        
        if ok and new_name.strip():
            new_id = new_name.strip().lower().replace(' ', '_')
            result = self.preset_manager.duplicate_preset(source_id, new_id, new_name.strip())
            
            if result['success']:
                self.load_presets()
                QMessageBox.information(self, "Success", f"Preset '{new_name}' created!")
            else:
                QMessageBox.warning(self, "Error", result['error'])
    
    def delete_preset(self):
        """Delete selected preset"""
        current_item = self.preset_list.currentItem()
        if not current_item:
            return
        
        preset_id = current_item.data(Qt.UserRole)
        is_locked = current_item.data(Qt.UserRole + 1)
        
        if is_locked:
            QMessageBox.warning(self, "Locked Preset", 
                              "Default presets cannot be deleted.")
            return
        
        preset = self.preset_manager.get_preset(preset_id)
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, "Delete Preset",
            f"Are you sure you want to delete '{preset['label']}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            result = self.preset_manager.delete_preset(preset_id)
            if result['success']:
                self.load_presets()
            else:
                QMessageBox.warning(self, "Error", result['error'])
    
    def apply_dark_theme(self):
        """Apply dark theme to dialog"""
        self.setStyleSheet("""
            QDialog {
                background-color: #2d2d2d;
                color: white;
            }
            QListWidget {
                background-color: #1a1a1a;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 5px;
                color: white;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 10px;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background-color: #00ff88;
                color: black;
            }
            QListWidget::item:hover {
                background-color: #3d3d3d;
            }
            QPushButton {
                background-color: #1a1a1a;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 10px 20px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border-color: #00ff88;
            }
            QPushButton:disabled {
                background-color: #1a1a1a;
                color: #666;
            }
        """)
