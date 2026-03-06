from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QComboBox, QCheckBox, QPushButton, QLineEdit,
                               QFileDialog, QFormLayout)
from PySide6.QtCore import Qt

class WatchFolderDialog(QDialog):
    """Dialog for configuring a watched folder"""
    
    def __init__(self, preset_manager, folder_path, parent=None):
        super().__init__(parent)
        self.preset_manager = preset_manager
        self.folder_path = folder_path
        self.setWindowTitle("Configure Watched Folder")
        self.setModal(True)
        self.setMinimumWidth(400)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Folder path
        form = QFormLayout()
        
        folder_label = QLabel(self.folder_path)
        folder_label.setWordWrap(True)
        folder_label.setStyleSheet("color: #00ff88; font-weight: bold;")
        form.addRow("Folder:", folder_label)
        
        # Preset selector
        self.preset_combo = QComboBox()
        for preset_key, preset in self.preset_manager.presets.items():
            self.preset_combo.addItem(preset['label'], preset_key)
        form.addRow("Preset:", self.preset_combo)
        
        # Auto-process checkbox
        self.auto_check = QCheckBox("Automatically process new files")
        self.auto_check.setChecked(True)
        form.addRow("", self.auto_check)

        # Delete original checkbox
        self.delete_original_check = QCheckBox("Delete original file after successful processing")
        self.delete_original_check.setChecked(False)  # Default to safe (keep originals)
        self.delete_original_check.setStyleSheet("color: #ff8800;")  # Orange warning color
        form.addRow("", self.delete_original_check)
        
        # Output folder
        output_layout = QHBoxLayout()
        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("Same as source folder")
        output_btn = QPushButton("Browse...")
        output_btn.clicked.connect(self.browse_output)
        output_layout.addWidget(self.output_edit)
        output_layout.addWidget(output_btn)
        form.addRow("Output Folder:", output_layout)
        
        layout.addLayout(form)
        
        # Buttons
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("Add Folder")
        ok_btn.clicked.connect(self.accept)
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #00ff88;
                color: black;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
        """)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(ok_btn)
        layout.addLayout(btn_layout)
    
    def browse_output(self):
        """Browse for output folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder:
            self.output_edit.setText(folder)
    
    def get_config(self):
        """Get the configuration"""
        output_folder = self.output_edit.text().strip()
        if not output_folder:
            output_folder = self.folder_path
        
        return {
            'presetId': self.preset_combo.currentData(),
            'autoProcess': self.auto_check.isChecked(),
            'outputFolder': output_folder,
            'deleteOriginal': self.delete_original_check.isChecked()  # NEW
        }

