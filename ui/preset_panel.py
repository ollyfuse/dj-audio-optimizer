from PySide6.QtWidgets import QWidget, QVBoxLayout, QRadioButton, QButtonGroup, QLabel
from PySide6.QtCore import Qt

class PresetPanel(QWidget):
    def __init__(self, preset_manager):
        super().__init__()
        self.preset_manager = preset_manager
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("🎚 PRESET")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #00ff88;")
        layout.addWidget(title)
        
        self.button_group = QButtonGroup()
        presets = self.preset_manager.get_all_presets()
        
        for i, (key, preset) in enumerate(presets.items()):
            # Create preset widget
            preset_widget = QWidget()
            preset_layout = QVBoxLayout(preset_widget)
            preset_layout.setContentsMargins(10, 5, 10, 5)
            
            # Radio button with label
            radio = QRadioButton(preset['label'])
            radio.setStyleSheet("""
                QRadioButton {
                    font-weight: bold;
                    color: white;
                }
                QRadioButton::indicator::checked {
                    background-color: #00ff88;
                }
            """)
            
            # Description
            desc = QLabel(preset['description'])
            desc.setStyleSheet("color: #888; font-size: 11px; margin-left: 20px;")
            desc.setWordWrap(True)
            
            # Target info
            target_info = QLabel(f"Target: {preset['target_lufs']} LUFS")
            target_info.setStyleSheet("color: #00ff88; font-size: 10px; margin-left: 20px;")
            
            preset_layout.addWidget(radio)
            preset_layout.addWidget(desc)
            preset_layout.addWidget(target_info)
            
            if i == 0:
                radio.setChecked(True)
            
            self.button_group.addButton(radio, i)
            layout.addWidget(preset_widget)
        
        layout.addStretch()
    
    def get_selected_preset(self):
        presets = list(self.preset_manager.get_all_presets().keys())
        selected_id = self.button_group.checkedId()
        return presets[selected_id] if selected_id >= 0 else 'club_festival'

