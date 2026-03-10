from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QSlider, QPushButton, QLineEdit, QTextEdit, QFrame, QScrollArea, QWidget)
from PySide6.QtCore import Qt

class PresetEditorDialog(QDialog):
    """Visual preset editor with sliders and validation"""
    
    def __init__(self, preset_manager, preset_id=None, parent=None):
        super().__init__(parent)
        self.preset_manager = preset_manager
        self.preset_id = preset_id
        self.is_edit_mode = preset_id is not None
        
        if self.is_edit_mode:
            self.preset_data = self.preset_manager.get_preset(preset_id).copy()
        else:
            self.preset_data = {
                'label': 'New Preset',
                'description': 'Custom preset',
                'target_lufs': -12.0,
                'true_peak': -1.0,
                'highpass_hz': 30,
                'eq': {'low_cut_db': -1.0, 'mid_cut_db': -0.5, 'high_boost_db': 0.5},
                'compression': {'low': 1.5, 'mid': 1.3, 'high': 1.2},
                'output_format': 'wav_24'
            }
        
        self.setup_ui()
        self.update_preview()
    
    def setup_ui(self):
        """Build compact scrollable UI"""
        self.setWindowTitle("Edit Preset" if self.is_edit_mode else "New Preset")
        self.setFixedSize(500, 550)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(8)
        layout.setContentsMargins(20, 15, 20, 15)
        
        # Name
        layout.addWidget(QLabel("Preset Name"))
        self.name_input = QLineEdit(self.preset_data['label'])
        self.name_input.setMinimumHeight(30)
        layout.addWidget(self.name_input)
        
        # Description
        layout.addWidget(QLabel("Description"))
        self.desc_input = QLineEdit(self.preset_data['description'])
        self.desc_input.setMinimumHeight(30)
        layout.addWidget(self.desc_input)
        
        layout.addSpacing(10)
        
        # LUFS Slider
        layout.addWidget(QLabel("Target LUFS"))
        self.lufs_slider, self.lufs_label = self._create_slider(
            -18, -6, self.preset_data['target_lufs'], 0.5, "LUFS"
        )
        self.lufs_slider.valueChanged.connect(self.on_lufs_changed)
        layout.addWidget(self.lufs_slider)
        layout.addWidget(self.lufs_label)
        
        # True Peak Slider
        layout.addWidget(QLabel("True Peak Ceiling"))
        self.peak_slider, self.peak_label = self._create_slider(
            -1.5, -0.3, self.preset_data['true_peak'], 0.1, "dB"
        )
        self.peak_slider.valueChanged.connect(self.on_peak_changed)
        layout.addWidget(self.peak_slider)
        layout.addWidget(self.peak_label)
        
        # Highpass Slider
        layout.addWidget(QLabel("Highpass Filter"))
        self.highpass_slider, self.highpass_label = self._create_slider(
            20, 50, self.preset_data['highpass_hz'], 1, "Hz"
        )
        self.highpass_slider.valueChanged.connect(self.on_highpass_changed)
        layout.addWidget(self.highpass_slider)
        layout.addWidget(self.highpass_label)
        
        layout.addSpacing(10)
        
        # Preview
        layout.addWidget(QLabel("Preview"))
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(80)
        layout.addWidget(self.preview_text)
        
        # Warning
        self.warning_label = QLabel()
        self.warning_label.setWordWrap(True)
        self.warning_label.setMinimumHeight(30)
        layout.addWidget(self.warning_label)
        
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
        
        # Buttons at bottom (fixed, not scrolling)
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(20, 10, 20, 15)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumHeight(35)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        self.save_btn = QPushButton("Save Preset")
        self.save_btn.setMinimumHeight(35)
        self.save_btn.clicked.connect(self.save_preset)
        button_layout.addWidget(self.save_btn)
        
        main_layout.addLayout(button_layout)
        
        self.apply_dark_theme()
    
    def _create_slider(self, min_val, max_val, current_val, step, unit):
        """Create slider with label"""
        steps = int((max_val - min_val) / step)
        current_step = int((current_val - min_val) / step)
        
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(0)
        slider.setMaximum(steps)
        slider.setValue(current_step)
        slider.setMinimumHeight(25)
        
        slider.setProperty('min_val', min_val)
        slider.setProperty('step', step)
        
        label = QLabel(f"{current_val:.1f} {unit}")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-weight: bold; font-size: 13px; color: #00ff88;")
        
        return slider, label
    
    def _slider_to_value(self, slider):
        """Convert slider position to actual value"""
        min_val = slider.property('min_val')
        step = slider.property('step')
        return min_val + (slider.value() * step)
    
    def on_lufs_changed(self):
        value = self._slider_to_value(self.lufs_slider)
        self.lufs_label.setText(f"{value:.1f} LUFS")
        self.preset_data['target_lufs'] = value
        self.update_preview()
    
    def on_peak_changed(self):
        value = self._slider_to_value(self.peak_slider)
        self.peak_label.setText(f"{value:.1f} dB")
        self.preset_data['true_peak'] = value
        self.update_preview()
    
    def on_highpass_changed(self):
        value = self._slider_to_value(self.highpass_slider)
        self.highpass_label.setText(f"{int(value)} Hz")
        self.preset_data['highpass_hz'] = int(value)
        self.update_preview()
    
    def update_preview(self):
        """Update preview and validation"""
        validation = self.preset_manager.validate_preset(self.preset_data)
        
        preview = f"""<b>LUFS:</b> {self.preset_data['target_lufs']:.1f} | <b>Peak:</b> {self.preset_data['true_peak']:.1f} dB | <b>Highpass:</b> {self.preset_data['highpass_hz']} Hz"""
        self.preview_text.setHtml(preview)
        
        if validation['errors']:
            self.warning_label.setText("❌ " + validation['errors'][0])
            self.warning_label.setStyleSheet("color: #ff4444; font-size: 11px;")
            self.save_btn.setEnabled(False)
        elif validation['warnings']:
            self.warning_label.setText("⚠️ " + validation['warnings'][0])
            self.warning_label.setStyleSheet("color: #ffaa00; font-size: 11px;")
            self.save_btn.setEnabled(True)
        else:
            self.warning_label.setText("✅ All settings are safe")
            self.warning_label.setStyleSheet("color: #00ff88; font-size: 11px;")
            self.save_btn.setEnabled(True)
    
    def save_preset(self):
        """Save the preset"""
        self.preset_data['label'] = self.name_input.text().strip()
        self.preset_data['description'] = self.desc_input.text().strip()
        
        if not self.preset_data['label']:
            self.warning_label.setText("❌ Preset name cannot be empty")
            self.warning_label.setStyleSheet("color: #ff4444;")
            return
        
        if not self.is_edit_mode:
            preset_id = self.preset_data['label'].lower().replace(' ', '_')
            result = self.preset_manager.create_preset(preset_id, self.preset_data)
        else:
            result = self.preset_manager.update_preset(self.preset_id, self.preset_data)
        
        if result['success']:
            self.accept()
        else:
            self.warning_label.setText(f"❌ {result['error']}")
            self.warning_label.setStyleSheet("color: #ff4444;")
    
    def apply_dark_theme(self):
        """Apply dark theme"""
        self.setStyleSheet("""
            QDialog {
                background-color: #2d2d2d;
                color: white;
            }
            QLabel {
                color: white;
                font-size: 12px;
                background: transparent;
                border: none;
            }
            QLineEdit {
                background-color: #3d3d3d;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 6px;
                color: white;
                font-size: 12px;
            }
            QTextEdit {
                background-color: #3d3d3d;
                border: 1px solid #555;
                border-radius: 4px;
                color: white;
                font-size: 11px;
            }
            QSlider::groove:horizontal {
                background: #3d3d3d;
                height: 6px;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #00ff88;
                width: 16px;
                margin: -5px 0;
                border-radius: 8px;
            }
            QPushButton {
                background-color: #3d3d3d;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 8px 16px;
                color: white;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
                border-color: #00ff88;
            }
            QPushButton:disabled {
                background-color: #2d2d2d;
                color: #666;
            }
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 10px;
            }
            QScrollBar::handle:vertical {
                background-color: #555;
                border-radius: 5px;
            }
        """)

