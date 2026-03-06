from core.watch_config import WatchConfig
from core.folder_watcher import FolderWatcher
from .folder_watch_panel import FolderWatchPanel
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
        self.output_folder = os.path.expanduser("~/Desktop")  

        # Initialize folder watching BEFORE setup_ui
        self.watch_config = WatchConfig()
        self.folder_watcher = FolderWatcher()

        self.setup_ui()
        self.setup_dark_theme()
        # Background processor
        self.bg_processor = BackgroundProcessor()
        self.bg_processor.track_started.connect(self.on_track_started)
        self.bg_processor.track_completed.connect(self.on_track_completed)
        self.bg_processor.progress_updated.connect(self.on_progress_updated)
        self.bg_processor.all_completed.connect(self.on_all_completed)
        # Folder watching system
        self.setup_folder_watching()

            
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
        """Center panel: Track table and folder monitoring"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(panel)
        
        # Create tab widget
        from PySide6.QtWidgets import QTabWidget
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
        
        # Drag & drop area
        drop_area = DragDropWidget("📁 Drag & Drop Audio Files Here\n\nOr click 'Add Tracks' below")
        drop_area.files_dropped.connect(self.handle_dropped_files)
        library_layout.addWidget(drop_area)
        
        # Button layout
        button_layout = QHBoxLayout()
        add_button = QPushButton("+ Add Tracks")
        add_button.clicked.connect(self.add_tracks)
        button_layout.addWidget(add_button)

        clear_button = QPushButton("🗑 Clear All")
        clear_button.clicked.connect(self.clear_tracks)
        button_layout.addWidget(clear_button)

        library_layout.addLayout(button_layout)
        
        # Track table
        self.track_table = TrackTable()
        self.track_table.skip_track_requested.connect(self.skip_track)
        self.track_table.remove_track_requested.connect(self.remove_track)
        library_layout.addWidget(self.track_table)
        
        # Folder Watch Tab
        self.folder_watch_panel = FolderWatchPanel(self.preset_manager, self.watch_config)
        self.folder_watch_panel.watch_added.connect(self.on_watch_added)
        self.folder_watch_panel.watch_removed.connect(self.on_watch_removed)
        self.folder_watch_panel.watch_toggled.connect(self.on_watch_toggled)
        
        # Add tabs
        tabs.addTab(library_widget, "📚 Track Library")
        tabs.addTab(self.folder_watch_panel, "📁 Folder Monitoring")
        
        layout.addWidget(tabs)
        
        return panel
    
    def on_watch_added(self, path, config):
        """Handle watch folder added"""
        self.folder_watcher.add_watch(path, config)

    def on_watch_removed(self, path):
        """Handle watch folder removed"""
        self.folder_watcher.remove_watch(path)

    def on_watch_toggled(self, path, enabled):
        """Handle watch folder toggled"""
        if enabled:
            # Find config and re-add watch
            for config in self.watch_config.watched_folders:
                if config['path'] == path:
                    self.folder_watcher.add_watch(path, config)
                    break
        else:
            self.folder_watcher.remove_watch(path)



    def clear_tracks(self):
        """Clear all tracks from the table"""
        self.tracks.clear()
        self.track_table.setRowCount(0)
        self.progress_label.setText("Ready to process")
        self.progress_bar.setVisible(False)
        self.update_health_display()

    def update_health_display(self):
        """Update compact health display in right panel"""
        if not self.tracks:
            self.health_score_label.setText("--")
            self.health_breakdown.setText("<i>No tracks loaded</i>")
            return
        
        # Calculate overall health
        total_tracks = len(self.tracks)
        total_score = sum(t.get('health_score', 0) for t in self.tracks)
        avg_score = int(total_score / total_tracks) if total_tracks > 0 else 0
        
        # Update score with color
        score_color = self._get_health_color(avg_score)
        self.health_score_label.setText(str(avg_score))
        self.health_score_label.setStyleSheet(f"""
            font-size: 36px; 
            font-weight: bold; 
            color: {score_color};
            padding: 10px;
        """)
        
        # Count by status
        excellent = sum(1 for t in self.tracks if t.get('health_score', 0) >= 80)
        good = sum(1 for t in self.tracks if 60 <= t.get('health_score', 0) < 80)
        fair = sum(1 for t in self.tracks if 40 <= t.get('health_score', 0) < 60)
        poor = sum(1 for t in self.tracks if t.get('health_score', 0) < 40)
        
        # Count issues
        from collections import Counter
        all_issues = []
        for track in self.tracks:
            all_issues.extend(track.get('health_issues', []))
        
        issue_counts = Counter(all_issues)
        clipping = issue_counts.get('clipping', 0) + issue_counts.get('near_clipping', 0)
        quiet = issue_counts.get('too_quiet', 0)
        compressed = issue_counts.get('over_compressed', 0)
        
        # Build compact breakdown text
        breakdown_text = f"""
    <b>{total_tracks} tracks loaded</b><br><br>

    <span style='color: #00aa44;'>🟢 {excellent} Excellent</span><br>
    <span style='color: #88aa00;'>🟡 {good} Good</span><br>
    <span style='color: #ffaa00;'>🟠 {fair} Fair</span><br>
    <span style='color: #aa4444;'>🔴 {poor} Poor</span><br><br>

    <b>Issues:</b><br>
    <span style='color: #ff4444;'>⚠️ {clipping} Clipping</span><br>
    <span style='color: #ffaa00;'>🔇 {quiet} Too Quiet</span><br>
    <span style='color: #ffaa00;'>📉 {compressed} Compressed</span>
        """
        
        self.health_breakdown.setText(breakdown_text)

    def _get_health_color(self, score):
        """Get color for health score"""
        if score >= 80:
            return "#00aa44"
        elif score >= 60:
            return "#88aa00"
        elif score >= 40:
            return "#ffaa00"
        else:
            return "#aa4444"
        
    def _is_processed_file(self, filename):
        """Check if filename indicates it's already been processed"""
        processed_patterns = [
            '- DJ OPT',
            'DJ OPT -',
            '(Optimized)',
            '_DJ_OPT'
        ]
        return any(pattern in filename for pattern in processed_patterns)
    
    def handle_dropped_files(self, file_paths):
        """Handle files dropped onto the drag & drop area"""
        # Get current target LUFS
        current_preset_key = self.preset_combo.currentData()
        target_lufs = None
        if current_preset_key:
            preset = self.preset_manager.get_preset(current_preset_key)
            target_lufs = preset['target_lufs']
        
        # Add all files asynchronously (NON-BLOCKING!)
        for file_path in file_paths:
            self._add_track_async(file_path, target_lufs)


    
    def create_right_panel(self):
        """Right panel: Preset summary, Health dashboard, and info"""
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
        
        # Divider
        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("background-color: #444; margin: 10px 0;")
        layout.addWidget(divider)
        
        # Health Dashboard (NEW - COMPACT VERSION!)
        health_title = QLabel("💊 LIBRARY HEALTH")
        health_title.setStyleSheet("font-weight: bold; color: #00ff88; font-size: 14px;")
        layout.addWidget(health_title)
        
        # Health score (big number)
        self.health_score_label = QLabel("--")
        self.health_score_label.setStyleSheet("""
            font-size: 36px; 
            font-weight: bold; 
            color: #00ff88;
            padding: 10px;
        """)
        self.health_score_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.health_score_label)
        
        # Health breakdown
        self.health_breakdown = QLabel()
        self.health_breakdown.setStyleSheet("color: white; padding: 5px; font-size: 11px;")
        self.health_breakdown.setWordWrap(True)
        layout.addWidget(self.health_breakdown)
        
        layout.addStretch()
        
        # Update preset info
        self.update_preset_info()
        self.update_health_display()

        # Copyright section
        copyright_label = QLabel("© 2026 DJ-FUSE\nProfessional DJ Audio Optimizer")
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
        
        # Get current target LUFS
        current_preset_key = self.preset_combo.currentData()
        target_lufs = None
        if current_preset_key:
            preset = self.preset_manager.get_preset(current_preset_key)
            target_lufs = preset['target_lufs']
        
        # Add all files asynchronously (NON-BLOCKING!)
        for file_path in files:
            self._add_track_async(file_path, target_lufs)

    
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

    def setup_folder_watching(self):
        """Initialize folder watching for enabled folders"""
        for folder_config in self.watch_config.get_enabled_folders():
            self.folder_watcher.add_watch(folder_config['path'], folder_config)
        
        # Connect file detection signal
        self.folder_watcher.file_detected.connect(self.on_file_detected)

    def on_file_detected(self, file_path, watch_folder_path):
        """Handle new file detected in watched folder"""
        # Find the config for this watch folder
        config = None
        for folder_config in self.watch_config.watched_folders:
            if folder_config['path'] == watch_folder_path:
                config = folder_config
                break
        
        if not config or not config.get('enabled', True):
            return
        
        # IGNORE ALREADY PROCESSED FILES (prevents infinite loop)
        filename = os.path.basename(file_path)
        if self._is_processed_file(filename):
            if hasattr(self, 'folder_watch_panel'):
                self.folder_watch_panel.log_activity(f"Ignored processed file: {filename}")
            return
        
        # Check for duplicates
        for track in self.tracks:
            if track['path'] == file_path:
                if hasattr(self, 'folder_watch_panel'):
                    self.folder_watch_panel.log_activity(f"Duplicate skipped: {os.path.basename(file_path)}")
                return
        
        # Log detection
        if hasattr(self, 'folder_watch_panel'):
            self.folder_watch_panel.log_file_detected(file_path)
        
        # Analyze in background (non-blocking)
        from PySide6.QtCore import QThread
        
        class TrackAnalyzer(QThread):
            def __init__(self, analyzer, file_path):
                super().__init__()
                self.analyzer = analyzer
                self.file_path = file_path
                self.analysis = None
            
            def run(self):
                self.analysis = self.analyzer.analyze_track(self.file_path)
        
        analyzer_thread = TrackAnalyzer(self.analyzer, file_path)
        
        def on_analysis_complete():
            analysis = analyzer_thread.analysis
            
            track_data = {
                'path': file_path,
                'name': os.path.basename(file_path),
                **analysis
            }
            
            self.tracks.append(track_data)
            
            preset = self.preset_manager.get_preset(config['presetId'])
            target_lufs = preset['target_lufs'] if preset else -12.0
            
            self.track_table.add_track(track_data, target_lufs)
            self.update_health_display()
            
            # Auto-process if enabled
            if config.get('autoProcess', True):
                self.auto_process_track(len(self.tracks) - 1, config)
        
        analyzer_thread.finished.connect(on_analysis_complete)
        analyzer_thread.start()
        
        if not hasattr(self, '_analyzer_threads'):
            self._analyzer_threads = []
        self._analyzer_threads.append(analyzer_thread)


    def _add_track_async(self, file_path, target_lufs=None):
        """Add track with background analysis (non-blocking)"""
        from PySide6.QtCore import QThread
        
        class TrackAnalyzer(QThread):
            def __init__(self, analyzer, file_path):
                super().__init__()
                self.analyzer = analyzer
                self.file_path = file_path
                self.analysis = None
            
            def run(self):
                self.analysis = self.analyzer.analyze_track(self.file_path)
        
        # Create and start analysis thread
        analyzer_thread = TrackAnalyzer(self.analyzer, file_path)
        
        # Handle completion
        def on_analysis_complete():
            analysis = analyzer_thread.analysis
            
            track_data = {
                'path': file_path,
                'name': os.path.basename(file_path),
                **analysis
            }
            
            self.tracks.append(track_data)
            self.track_table.add_track(track_data, target_lufs)
            self.update_health_display()
        
        analyzer_thread.finished.connect(on_analysis_complete)
        analyzer_thread.start()
        
        # Store thread reference
        if not hasattr(self, '_analyzer_threads'):
            self._analyzer_threads = []
        self._analyzer_threads.append(analyzer_thread)




    def auto_process_track(self, track_index, config):
        """Auto-process a single track from watched folder (non-blocking)"""
        if track_index >= len(self.tracks):
            return
        
        track = self.tracks[track_index]
        
        # Get output folder
        output_folder = config.get('outputFolder', config['path'])
        
        # Process the track
        input_path = track['path']
        filename = track['name']
        
        # Use the preset's output format
        preset = self.preset_manager.get_preset(config['presetId'])
        output_format = preset.get('output_format', 'wav_24') if preset else 'wav_24'
        
        # Generate output filename
        output_filename = self.bg_processor.get_output_filename(filename, output_format)
        output_path = os.path.join(output_folder, output_filename)
        
        # Update status
        self.track_table.update_track_status(track_index, 'processing')
        
        # Process in background thread (NON-BLOCKING!)
        from PySide6.QtCore import QThread
        
        class SingleTrackProcessor(QThread):
            def __init__(self, processor, input_path, preset_id, output_path, output_format):
                super().__init__()
                self.processor = processor
                self.input_path = input_path
                self.preset_id = preset_id
                self.output_path = output_path
                self.output_format = output_format
                self.result = None
            
            def run(self):
                self.result = self.processor.process_track(
                    self.input_path, 
                    self.preset_id, 
                    self.output_path, 
                    self.output_format
                )
        
        # Create and start thread
        thread = SingleTrackProcessor(
            self.processor, 
            input_path, 
            config['presetId'], 
            output_path, 
            output_format
        )
        
        # Handle completion
        def on_finished():
            result = thread.result
            
            if result and result['success']:
                self.track_table.update_track_status(track_index, 'completed')
                after_lufs = result.get('final_lufs', -12.0)
                final_peak = -1.0
                self.track_table.update_after_processing(track_index, after_lufs, final_peak)
                
                # DELETE ORIGINAL IF ENABLED
                if config.get('deleteOriginal', False):
                    try:
                        os.remove(input_path)
                        if hasattr(self, 'folder_watch_panel'):
                            self.folder_watch_panel.log_activity(f"🗑 Deleted original: {filename}")
                    except Exception as e:
                        if hasattr(self, 'folder_watch_panel'):
                            self.folder_watch_panel.log_activity(f"⚠️ Failed to delete: {filename} - {str(e)}")
                
                if hasattr(self, 'folder_watch_panel'):
                    self.folder_watch_panel.log_file_processed(input_path, True)
            else:
                self.track_table.update_track_status(track_index, 'error')
                if hasattr(self, 'folder_watch_panel'):
                    self.folder_watch_panel.log_file_processed(input_path, False)
        
        thread.finished.connect(on_finished)
        thread.start()
        
        # Store thread reference to prevent garbage collection
        if not hasattr(self, '_auto_process_threads'):
            self._auto_process_threads = []
        self._auto_process_threads.append(thread)

    
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
            QTableWidget::item { 
                padding: 8px; 
                border-bottom: 1px solid #333; 
            }
            QTableWidget::item:selected { background-color: #00ff88; color: black; }
            QHeaderView::section {
                background-color: #333; color: white; padding: 8px;
                border: none; font-weight: bold;
            }
            QLabel { color: white; }
        """)

    def closeEvent(self, event):
        """Clean up when closing the app"""
        self.folder_watcher.stop()
        event.accept()
