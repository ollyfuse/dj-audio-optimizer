from PySide6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
                               QPushButton, QLabel, QFileDialog, QComboBox, QFrame, QProgressBar, QApplication, QLineEdit)

from PySide6.QtCore import Qt
from .track_table import TrackTable
from .drag_drop_widget import DragDropWidget
from core.analyzer import AudioAnalyzer
from core.presets import PresetManager
from core.processor import AudioProcessor
from core.background_processor import BackgroundProcessor
import os


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.analyzer = AudioAnalyzer()
        self.preset_manager = PresetManager()
        self.processor = AudioProcessor()
        self.tracks = []
        self.output_folder = os.path.expanduser("~/Desktop")  # Move this line up
        self.setup_ui()
        self.setup_dark_theme()
        # Background processor
        self.bg_processor = BackgroundProcessor()
        self.bg_processor.track_started.connect(self.on_track_started)
        self.bg_processor.track_completed.connect(self.on_track_completed)
        self.bg_processor.progress_updated.connect(self.on_progress_updated)
        self.bg_processor.all_completed.connect(self.on_all_completed)

            
    def setup_ui(self):
        self.setWindowTitle("DeckReady - Professional DJ Audio Optimizer")
        self.setGeometry(100, 100, 1200, 800)
        
        # Main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # LEFT PANEL
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 1)
        
        # CENTER PANEL
        center_panel = self.create_center_panel()
        main_layout.addWidget(center_panel, 3)
        
        # RIGHT PANEL
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 1)
    
    def create_left_panel(self):
        """Left panel: Logo, Preset selector, Output format, Process button"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(panel)
        
        # App logo
        logo = QLabel("🎧 DECKREADY")
        logo.setStyleSheet("font-size: 24px; font-weight: bold; color: #00ff88; padding: 20px;")
        logo.setAlignment(Qt.AlignCenter)
        layout.addWidget(logo)
        
        # Preset selector
        layout.addWidget(QLabel("Preset:"))
        self.preset_combo = QComboBox()
        presets = self.preset_manager.get_all_presets()
        for key, preset in presets.items():
            self.preset_combo.addItem(preset['label'], key)
        self.preset_combo.currentTextChanged.connect(self.on_preset_changed)
        layout.addWidget(self.preset_combo)
        
        # Output format selector
        layout.addWidget(QLabel("Output Format:"))
        self.format_combo = QComboBox()
        self.format_combo.addItems(["WAV 24-bit", "WAV 16-bit", "AIFF", "FLAC"])
        layout.addWidget(self.format_combo)

        # Export settings section
        layout.addWidget(QLabel("📁 EXPORT SETTINGS"))

        # Output folder
        layout.addWidget(QLabel("Output Folder:"))
        folder_layout = QHBoxLayout()
        self.folder_display = QLineEdit()
        self.folder_display.setText(self.output_folder)
        self.folder_display.setReadOnly(True)
        folder_layout.addWidget(self.folder_display)

        browse_button = QPushButton("📂")
        browse_button.setMaximumWidth(40)
        browse_button.clicked.connect(self.browse_output_folder)
        folder_layout.addWidget(browse_button)

        folder_widget = QWidget()
        folder_widget.setLayout(folder_layout)
        layout.addWidget(folder_widget)

        # Naming convention
        layout.addWidget(QLabel("Naming:"))
        self.naming_combo = QComboBox()
        self.naming_combo.addItems([
            "Original - DJ OPT",
            "DJ OPT - Original", 
            "Original (Optimized)",
            "Original_DJ_OPT"
        ])
        layout.addWidget(self.naming_combo)

        
        # Progress section
        self.create_progress_section(layout)
        
        layout.addStretch()
        
        # Process button
        self.process_button = QPushButton("🔥 PROCESS TRACKS")
        self.process_button.setMinimumHeight(60)
        self.process_button.clicked.connect(self.process_tracks)
        layout.addWidget(self.process_button)
        
        return panel
    
    def create_progress_section(self, layout):
        """Add progress bar section with queue controls"""
        # Progress label
        self.progress_label = QLabel("Ready to process")
        self.progress_label.setStyleSheet("color: #00ff88; font-weight: bold;")
        layout.addWidget(self.progress_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #444;
                border-radius: 4px;
                background-color: #2d2d2d;
                color: white;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #00ff88;
                border-radius: 3px;
            }
        """)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Queue control buttons
        queue_layout = QHBoxLayout()
        self.pause_button = QPushButton("⏸ PAUSE")
        self.pause_button.setVisible(False)
        self.pause_button.clicked.connect(self.pause_processing)
        queue_layout.addWidget(self.pause_button)
        
        self.resume_button = QPushButton("▶ RESUME")
        self.resume_button.setVisible(False)
        self.resume_button.clicked.connect(self.resume_processing)
        queue_layout.addWidget(self.resume_button)
        
        queue_widget = QWidget()
        queue_widget.setLayout(queue_layout)
        layout.addWidget(queue_widget)

    def create_center_panel(self):
        """Center panel: Drag & drop area and track table"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(panel)
        
        # Drag & drop area
        drop_area = DragDropWidget("📁 Drag & Drop Audio Files Here\n\nOr click 'Add Tracks' below")
        drop_area.files_dropped.connect(self.handle_dropped_files)
        layout.addWidget(drop_area)
        
        # Button layout
        button_layout = QHBoxLayout()
        add_button = QPushButton("+ Add Tracks")
        add_button.clicked.connect(self.add_tracks)
        button_layout.addWidget(add_button)

        clear_button = QPushButton("🗑 Clear All")
        clear_button.clicked.connect(self.clear_tracks)
        button_layout.addWidget(clear_button)

        layout.addLayout(button_layout)
        
        # Track table
        self.track_table = TrackTable()
        self.track_table.skip_track_requested.connect(self.skip_track)
        self.track_table.remove_track_requested.connect(self.remove_track)
        layout.addWidget(self.track_table)
        
        return panel


    def clear_tracks(self):
        """Clear all tracks from the table"""
        self.tracks.clear()
        self.track_table.setRowCount(0)
        self.progress_label.setText("Ready to process")
        self.progress_bar.setVisible(False)

    
    def handle_dropped_files(self, file_paths):
        """Handle files dropped onto the drag & drop area"""
        for file_path in file_paths:
            analysis = self.analyzer.analyze_track(file_path)
            track_data = {
                'path': file_path,
                'name': file_path.split('/')[-1],
                **analysis
            }
            self.tracks.append(track_data)
            self.track_table.add_track(track_data)
        
        # Update target LUFS for new tracks
        self.on_preset_changed()

    
    def create_right_panel(self):
        """Right panel: Preset summary and info"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(panel)
        
        # Preset summary title
        title = QLabel("📊 PRESET SUMMARY")
        title.setStyleSheet("font-weight: bold; color: #00ff88; font-size: 14px;")
        layout.addWidget(title)
        
        # Preset info
        self.preset_info = QLabel()
        self.preset_info.setStyleSheet("color: white; padding: 10px;")
        self.preset_info.setWordWrap(True)
        layout.addWidget(self.preset_info)
        
        layout.addStretch()
        
        # Update preset info
        self.update_preset_info()

        # Copyright section
        copyright_label = QLabel("© 2026 DJ-FUSE\nProfessional DJ Audio Optimizer -")
        copyright_label.setStyleSheet('''
            color: #666; 
            font-size: 10px; 
            padding: 10px;
            text-align: center;
        ''')
        copyright_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(copyright_label)

        
        return panel
    
    def on_preset_changed(self):
        """Update preset info when preset changes"""
        self.update_preset_info()
        # Update target LUFS in table
        current_preset_key = self.preset_combo.currentData()
        if current_preset_key:
            preset = self.preset_manager.get_preset(current_preset_key)
            self.track_table.update_target_lufs(preset['target_lufs'])
    
    def update_preset_info(self):
        """Update the preset summary panel"""
        current_preset_key = self.preset_combo.currentData()
        if current_preset_key:
            preset = self.preset_manager.get_preset(current_preset_key)
            info_text = f"""
<b>{preset['label']}</b><br>
<i>{preset['description']}</i><br><br>

<b>Target LUFS:</b> {preset['target_lufs']}<br>
<b>True Peak Limit:</b> {preset['true_peak']} dB<br>
<b>High-pass Filter:</b> {preset['highpass_hz']} Hz<br>
<b>Output Format:</b> {preset['output_format'].upper()}<br><br>

<b>EQ Settings:</b><br>
• Low: {preset['eq']['low_cut_db']} dB<br>
• Mid: {preset['eq']['mid_cut_db']} dB<br>
• High: {preset['eq']['high_boost_db']} dB
            """
            self.preset_info.setText(info_text)
    
    def add_tracks(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Audio Files", "", 
            "Audio Files (*.mp3 *.wav *.flac *.aiff)"
        )
        
        for file_path in files:
            analysis = self.analyzer.analyze_track(file_path)
            track_data = {
                'path': file_path,
                'name': file_path.split('/')[-1],
                **analysis
            }
            self.tracks.append(track_data)
            self.track_table.add_track(track_data)
        
        # Update target LUFS for new tracks
        self.on_preset_changed()
    
    def get_output_format(self):
        """Get the selected output format"""
        format_map = {
            "WAV 24-bit": "wav_24",
            "WAV 16-bit": "wav_16", 
            "AIFF": "aiff",
            "FLAC": "flac"
        }
        return format_map.get(self.format_combo.currentText(), "wav_24")
    
    def browse_output_folder(self):
        """Browse for output folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select Output Folder", self.output_folder)
        if folder:
            self.output_folder = folder
            self.folder_display.setText(folder)

    def get_output_filename(self, original_name, output_format):
        """Generate output filename based on naming convention"""
        # Clean the filename first
        clean_name = self.clean_filename(original_name)
        
        # Get file extension based on format
        if output_format == "aiff":
            ext = ".aiff"
        elif output_format == "flac":
            ext = ".flac"
        else:
            ext = ".wav"
        
        # Apply naming convention
        naming = self.naming_combo.currentText()
        if naming == "Original - DJ OPT":
            return f"{clean_name} - DJ OPT{ext}"
        elif naming == "DJ OPT - Original":
            return f"DJ OPT - {clean_name}{ext}"
        elif naming == "Original (Optimized)":
            return f"{clean_name} (Optimized){ext}"
        elif naming == "Original_DJ_OPT":
            return f"{clean_name}_DJ_OPT{ext}"
        else:
            return f"{clean_name} - DJ OPT{ext}"  # Default


    def clean_filename(self, filename):
        """Clean filename by removing common unwanted phrases"""
        import re
        
        # Remove file extension first
        base_name = os.path.splitext(filename)[0]
        
        # List of phrases to remove (case insensitive)
        unwanted_phrases = [
            r'\(official\s+video\)',
            r'\(official\s+audio\)',
            r'\(official\s+music\s+video\)',
            r'\(music\s+video\)',
            r'\(lyric\s+video\)',
            r'\(lyrics\)',
            r'\(hd\)',
            r'\(4k\)',
            r'\(1080p\)',
            r'\(720p\)',
            r'\[official\s+video\]',
            r'\[official\s+audio\]',
            r'\[official\s+music\s+video\]',
            r'\[music\s+video\]',
            r'\[lyric\s+video\]',
            r'\[lyrics\]',
            r'\[hd\]',
            r'\[4k\]',
            r'\[1080p\]',
            r'\[720p\]',
            r'official\s+video',
            r'official\s+audio',
            r'official\s+music\s+video',
            r'music\s+video',
            r'lyric\s+video',
            r'lyrics'
        ]
        
        # Remove unwanted phrases
        cleaned_name = base_name
        for phrase in unwanted_phrases:
            cleaned_name = re.sub(phrase, '', cleaned_name, flags=re.IGNORECASE)
        
        # Clean up extra spaces and dashes
        cleaned_name = re.sub(r'\s+', ' ', cleaned_name)  # Multiple spaces to single
        cleaned_name = re.sub(r'\s*-\s*$', '', cleaned_name)  # Trailing dash
        cleaned_name = re.sub(r'^\s*-\s*', '', cleaned_name)  # Leading dash
        cleaned_name = cleaned_name.strip()
        
        return cleaned_name if cleaned_name else base_name  # Fallback to original if empty


    
    def process_tracks(self):
        if not self.tracks:
            return
        
        # Setup background processing
        current_preset_key = self.preset_combo.currentData()
        output_format = self.get_output_format()
        self.bg_processor.setup_batch(self.tracks, current_preset_key, output_format, self.output_folder, self.naming_combo.currentText())

        # Update UI for processing state
        self.progress_bar.setMaximum(len(self.tracks))
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.progress_label.setText("Starting batch processing...")
        
        # Show queue controls
        self.pause_button.setVisible(True)
        self.resume_button.setVisible(False)
        
        # Change button to cancel
        self.process_button.setText("⏹ CANCEL ALL")
        self.process_button.clicked.disconnect()
        self.process_button.clicked.connect(self.cancel_processing)
        
        # Start background processing
        self.bg_processor.start()


    def cancel_processing(self):
        """Cancel all processing"""
        self.bg_processor.stop_processing()
        self.progress_label.setText("Cancelling all tracks...")
        self.pause_button.setVisible(False)
        self.resume_button.setVisible(False)

    def on_all_completed(self, processed, total):
        """Handle all processing completed"""
        self.progress_label.setText(f"🎉 Complete! Processed {processed}/{total} tracks")
        self.progress_bar.setVisible(False)
        self.pause_button.setVisible(False)
        self.resume_button.setVisible(False)
        
        # Reset button
        self.process_button.setText("🔥 PROCESS TRACKS")
        self.process_button.clicked.disconnect()
        self.process_button.clicked.connect(self.process_tracks)


    def on_track_started(self, index, name):
        """Handle track processing started"""
        self.track_table.update_track_status(index, 'processing')
        short_name = name[:25] + "..." if len(name) > 25 else name
        self.progress_label.setText(f"⚡ Processing: {short_name}")

    def on_track_completed(self, index, success, message, after_lufs=0.0, final_peak=0.0):
        """Handle track processing completed with enhanced analysis data"""
        if success:
            self.track_table.update_track_status(index, 'completed')
            # Update the table with before/after comparison data
            self.track_table.update_after_processing(index, after_lufs, final_peak)
        elif "Skipped by user" in message:
            # Don't change status - it's already set to 'skipped' by skip_track method
            pass
        else:
            self.track_table.update_track_status(index, 'error')



    def on_progress_updated(self, current, total):
        """Handle progress update"""
        self.progress_bar.setValue(current)

    def pause_processing(self):
        """Pause the processing queue"""
        self.bg_processor.pause_processing()
        self.pause_button.setVisible(False)
        self.resume_button.setVisible(True)
        self.progress_label.setText("⏸ Processing paused...")

    def resume_processing(self):
        """Resume the processing queue"""
        self.bg_processor.resume_processing()
        self.pause_button.setVisible(True)
        self.resume_button.setVisible(False)
        self.progress_label.setText("▶ Processing resumed...")

    def skip_track(self, track_index):
        """Skip individual track"""
        self.bg_processor.skip_track(track_index)
        self.track_table.update_track_status(track_index, 'skipped')
    
    def remove_track(self, track_index):
        """Remove individual track from list"""
        if 0 <= track_index < len(self.tracks):
            # Remove from tracks list
            del self.tracks[track_index]
            # Remove from table
            self.track_table.removeRow(track_index)




    
    def setup_dark_theme(self):
        """Apply professional dark DJ theme"""
        self.setStyleSheet("""
            QMainWindow { background-color: #1a1a1a; color: white; }
            QWidget { background-color: #1a1a1a; color: white; }
            QFrame { background-color: #2d2d2d; border: 1px solid #444; border-radius: 8px; margin: 5px; }
            QPushButton {
                background-color: #2d2d2d; border: 1px solid #444; border-radius: 6px;
                padding: 8px 16px; color: white; font-weight: bold;
            }
            QPushButton:hover { background-color: #3d3d3d; border-color: #00ff88; }
            QPushButton:pressed { background-color: #00ff88; color: black; }
            QComboBox {
                background-color: #2d2d2d; border: 1px solid #444; border-radius: 4px;
                padding: 5px; color: white;
            }
            QComboBox::drop-down { border: none; }
            QComboBox::down-arrow { image: none; border: none; }
            QTableWidget {
                background-color: #2d2d2d; border: 1px solid #444; border-radius: 6px;
                gridline-color: #444;
            }
            QTableWidget::item { padding: 8px; border-bottom: 1px solid #333; }
            QTableWidget::item:selected { background-color: #00ff88; color: black; }
            QHeaderView::section {
                background-color: #333; color: white; padding: 8px;
                border: none; font-weight: bold;
            }
            QLabel { color: white; }
        """)
