from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QComboBox, QLineEdit, QProgressBar,
                               QScrollArea, QWidget, QFileDialog)
from PySide6.QtCore import Qt, Signal
import multiprocessing


class LeftPanel(QFrame):
    """Left panel: Preset selection, output settings, and processing controls"""
    
    # Signals
    preset_changed = Signal(str)  # preset_key
    output_folder_changed = Signal(str)  # folder_path
    process_clicked = Signal()
    cancel_clicked = Signal()
    preset_manager_requested = Signal()
    
    def __init__(self, preset_manager, output_folder):
        super().__init__()
        self.preset_manager = preset_manager
        self.output_folder = output_folder
        self.is_processing = False
        
        self.setFrameStyle(QFrame.StyledPanel)
        self.setMinimumWidth(260)
        self.setMaximumWidth(300)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup left panel UI"""
        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(12)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Logo
        logo = QLabel("DECKREADY")
        logo.setStyleSheet("font-size: 18px; font-weight: bold; color: #00ff88;")
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)
        
        # Preset
        layout.addWidget(QLabel("Preset"))
        preset_row = QHBoxLayout()
        preset_row.setSpacing(5)
        self.preset_combo = QComboBox()
        self.preset_combo.setMinimumHeight(30)
        self.refresh_presets()
        self.preset_combo.currentTextChanged.connect(self._on_preset_changed)
        preset_row.addWidget(self.preset_combo, 1)
        
        manage_btn = QPushButton("Edit")
        manage_btn.setFixedHeight(30)
        manage_btn.setFixedWidth(50)
        manage_btn.clicked.connect(self.preset_manager_requested.emit)
        preset_row.addWidget(manage_btn)
        layout.addLayout(preset_row)
        
        # Output Format
        layout.addWidget(QLabel("Output Format"))
        self.format_combo = QComboBox()
        self.format_combo.setMinimumHeight(30)
        self.format_combo.addItems(["WAV 24-bit", "WAV 16-bit", "AIFF", "FLAC"])
        layout.addWidget(self.format_combo)
        
        layout.addSpacing(10)
        
        # Output Folder
        layout.addWidget(QLabel("Output Folder"))
        folder_row = QHBoxLayout()
        folder_row.setSpacing(5)
        self.folder_display = QLineEdit()
        self.folder_display.setText(self.output_folder)
        self.folder_display.setReadOnly(True)
        self.folder_display.setMinimumHeight(30)
        folder_row.addWidget(self.folder_display, 1)
        
        browse_btn = QPushButton("Browse")
        browse_btn.setFixedHeight(30)
        browse_btn.setFixedWidth(70)
        browse_btn.clicked.connect(self._browse_output_folder)
        folder_row.addWidget(browse_btn)
        layout.addLayout(folder_row)
        
        # Naming
        layout.addWidget(QLabel("Naming"))
        self.naming_combo = QComboBox()
        self.naming_combo.setMinimumHeight(30)
        self.naming_combo.addItems([
            "Original - DJ OPT",
            "DJ OPT - Original", 
            "Original (Optimized)",
            "Original_DJ_OPT"
        ])
        layout.addWidget(self.naming_combo)
        
        # CPU Cores
        layout.addWidget(QLabel("CPU Cores"))
        self.cores_combo = QComboBox()
        self.cores_combo.setMinimumHeight(30)
        cpu_count = multiprocessing.cpu_count()
        self.cores_combo.addItem(f"Auto ({cpu_count-1})", cpu_count-1)
        for i in range(1, cpu_count + 1):
            self.cores_combo.addItem(f"{i} core{'s' if i > 1 else ''}", i)
        layout.addWidget(self.cores_combo)
        
        layout.addSpacing(10)
        
        # Progress
        self.progress_label = QLabel("Ready")
        self.progress_label.setStyleSheet("color: #00ff88; font-size: 11px;")
        self.progress_label.setWordWrap(True)
        layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(18)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        layout.addStretch()
        
        # Process Button
        self.process_button = QPushButton("PROCESS TRACKS")
        self.process_button.setMinimumHeight(45)
        self.process_button.setStyleSheet("""
            QPushButton {
                background-color: #00ff88;
                color: black;
                font-weight: bold;
                font-size: 13px;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #00dd77;
            }
        """)
        self.process_button.clicked.connect(self._on_process_button_clicked)
        layout.addWidget(self.process_button)
        
        scroll.setWidget(content)
        panel_layout = QVBoxLayout(self)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.addWidget(scroll)
    
    def refresh_presets(self):
        """Refresh preset dropdown"""
        current_selection = self.preset_combo.currentData()
        self.preset_combo.clear()
        
        presets = self.preset_manager.get_all_presets()
        for key, preset in presets.items():
            self.preset_combo.addItem(preset['label'], key)
        
        if current_selection:
            index = self.preset_combo.findData(current_selection)
            if index >= 0:
                self.preset_combo.setCurrentIndex(index)
    
    def _on_preset_changed(self):
        """Handle preset selection change"""
        preset_key = self.preset_combo.currentData()
        if preset_key:
            self.preset_changed.emit(preset_key)
    
    def _browse_output_folder(self):
        """Browse for output folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder", self.output_folder)
        if folder:
            self.output_folder = folder
            self.folder_display.setText(folder)
            self.output_folder_changed.emit(folder)
    
    def _on_process_button_clicked(self):
        """Handle process button click"""
        if self.is_processing:
            self.cancel_clicked.emit()
        else:
            self.process_clicked.emit()
    
    def set_processing_state(self, processing):
        """Update UI for processing state"""
        self.is_processing = processing
        if processing:
            self.process_button.setText("⏹ CANCEL ALL")
        else:
            self.process_button.setText("PROCESS TRACKS")
    
    def update_progress(self, text, value=None, maximum=None):
        """Update progress display"""
        self.progress_label.setText(text)
        if value is not None:
            self.progress_bar.setValue(value)
        if maximum is not None:
            self.progress_bar.setMaximum(maximum)
            self.progress_bar.setVisible(True)
    
    def hide_progress(self):
        """Hide progress bar"""
        self.progress_bar.setVisible(False)
    
    def get_selected_preset_key(self):
        """Get currently selected preset key"""
        return self.preset_combo.currentData()
    
    def get_output_format(self):
        """Get selected output format"""
        format_map = {
            "WAV 24-bit": "wav_24",
            "WAV 16-bit": "wav_16", 
            "AIFF": "aiff",
            "FLAC": "flac"
        }
        return format_map.get(self.format_combo.currentText(), "wav_24")
    
    def get_naming_convention(self):
        """Get selected naming convention"""
        return self.naming_combo.currentText()
    
    def get_cpu_cores(self):
        """Get selected CPU core count"""
        return self.cores_combo.currentData()
