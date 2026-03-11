from core.watch_config import WatchConfig
from core.folder_watcher import FolderWatcher
from .panels import LeftPanel, CenterPanel, RightPanel
from .preset_manager_dialog import PresetManagerDialog
from PySide6.QtWidgets import QMainWindow, QHBoxLayout, QWidget, QFileDialog
from PySide6.QtCore import Qt, QThread
from PySide6.QtGui import QColor
from core.analyzer import AudioAnalyzer
from core.presets import PresetManager
from core.processor import AudioProcessor
import os


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.analyzer = AudioAnalyzer()
        self.preset_manager = PresetManager()
        self.processor = AudioProcessor()
        self.tracks = []
        self.output_folder = os.path.expanduser("~/Desktop")

        # Initialize folder watching
        self.watch_config = WatchConfig()
        self.folder_watcher = FolderWatcher()

        self.setup_ui()
        self.setup_dark_theme()
        
        # Parallel processor
        from core.parallel_processor import ParallelProcessor
        self.parallel_processor = ParallelProcessor()
        self.parallel_processor.track_started.connect(self.on_track_started)
        self.parallel_processor.track_completed.connect(self.on_track_completed)
        self.parallel_processor.progress_updated.connect(self.on_progress_updated)
        self.parallel_processor.all_completed.connect(self.on_all_completed)
        self.bg_processor = self.parallel_processor

        # Folder watching system
        self.setup_folder_watching()

    def setup_ui(self):
        self.setWindowTitle("DeckReady - Professional DJ Audio Optimizer")
        self.setGeometry(100, 100, 1200, 800)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Create panels
        self.left_panel = LeftPanel(self.preset_manager, self.output_folder)
        self.center_panel = CenterPanel(self.preset_manager, self.watch_config)
        self.right_panel = RightPanel(self.preset_manager)
        
        # Connect signals
        self.connect_panel_signals()
        
        # Add panels to layout
        main_layout.addWidget(self.left_panel, 1)
        main_layout.addWidget(self.center_panel, 3)
        main_layout.addWidget(self.right_panel, 1)
        
        # Update initial displays
        self.on_preset_changed(self.left_panel.get_selected_preset_key())
    
    def connect_panel_signals(self):
        """Connect all panel signals to handlers"""
        # Left panel
        self.left_panel.preset_changed.connect(self.on_preset_changed)
        self.left_panel.output_folder_changed.connect(self.on_output_folder_changed)
        self.left_panel.process_clicked.connect(self.process_tracks)
        self.left_panel.cancel_clicked.connect(self.cancel_processing)
        self.left_panel.preset_manager_requested.connect(self.open_preset_manager)
        
        # Center panel
        self.center_panel.files_dropped.connect(self.handle_dropped_files)
        self.center_panel.add_tracks_clicked.connect(self.add_tracks)
        self.center_panel.clear_tracks_clicked.connect(self.clear_tracks)
        self.center_panel.skip_track_requested.connect(self.skip_track)
        self.center_panel.remove_track_requested.connect(self.remove_track)
        self.center_panel.watch_added.connect(self.on_watch_added)
        self.center_panel.watch_removed.connect(self.on_watch_removed)
        self.center_panel.watch_toggled.connect(self.on_watch_toggled)
    
    def on_preset_changed(self, preset_key):
        """Handle preset change"""
        self.right_panel.update_preset_info(preset_key)
        if preset_key:
            preset = self.preset_manager.get_preset(preset_key)
            self.center_panel.track_table.update_target_lufs(preset['target_lufs'])
    
    def on_output_folder_changed(self, folder_path):
        """Handle output folder change"""
        self.output_folder = folder_path
    
    def open_preset_manager(self):
        """Open preset manager dialog"""
        dialog = PresetManagerDialog(self.preset_manager, self)
        if dialog.exec():
            self.preset_manager.load_presets()
            self.left_panel.refresh_presets()
            self.on_preset_changed(self.left_panel.get_selected_preset_key())
    
    def add_tracks(self):
        """Add tracks via file dialog"""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Audio Files", "", 
            "Audio Files (*.mp3 *.wav *.flac *.aiff)"
        )
        
        current_preset_key = self.left_panel.get_selected_preset_key()
        target_lufs = None
        if current_preset_key:
            preset = self.preset_manager.get_preset(current_preset_key)
            target_lufs = preset['target_lufs']
        
        for file_path in files:
            self._add_track_async(file_path, target_lufs)
    
    def handle_dropped_files(self, file_paths):
        """Handle files dropped onto drag & drop area"""
        current_preset_key = self.left_panel.get_selected_preset_key()
        target_lufs = None
        if current_preset_key:
            preset = self.preset_manager.get_preset(current_preset_key)
            target_lufs = preset['target_lufs']
        
        for file_path in file_paths:
            self._add_track_async(file_path, target_lufs)
    
    def clear_tracks(self):
        """Clear all tracks"""
        self.tracks.clear()
        self.center_panel.track_table.setRowCount(0)
        self.left_panel.update_progress("Ready to process")
        self.left_panel.hide_progress()
        self.right_panel.update_health_display([])
    
    def process_tracks(self):
        """Start processing tracks"""
        if not self.tracks:
            return
        
        max_workers = self.left_panel.get_cpu_cores()
        current_preset_key = self.left_panel.get_selected_preset_key()
        output_format = self.left_panel.get_output_format()
        naming_convention = self.left_panel.get_naming_convention()
        
        # Create new processor
        from core.parallel_processor import ParallelProcessor
        self.parallel_processor = ParallelProcessor(max_workers=max_workers)
        self.parallel_processor.track_started.connect(self.on_track_started)
        self.parallel_processor.track_completed.connect(self.on_track_completed)
        self.parallel_processor.progress_updated.connect(self.on_progress_updated)
        self.parallel_processor.all_completed.connect(self.on_all_completed)
        self.bg_processor = self.parallel_processor
        
        self.parallel_processor.setup_batch(
            self.tracks, 
            current_preset_key, 
            output_format, 
            self.output_folder, 
            naming_convention
        )

        # Update UI
        self.left_panel.update_progress(
            f"Processing with {max_workers} cores...",
            value=0,
            maximum=len(self.tracks)
        )
        self.left_panel.set_processing_state(True)
        
        # Start processing
        self.parallel_processor.start()

    def cancel_processing(self):
        """Cancel all processing"""
        self.bg_processor.stop_processing()
        self.left_panel.update_progress("Cancelling...")

    def on_track_started(self, index, name):
        """Handle track processing started"""
        self.center_panel.track_table.update_track_status(index, 'processing')
        short_name = name[:20] + "..." if len(name) > 20 else name
        
        processing_count = sum(1 for i in range(self.center_panel.track_table.rowCount()) 
                            if self.center_panel.track_table.item(i, 8) and 
                            'Processing' in self.center_panel.track_table.item(i, 8).text())
        
        self.left_panel.update_progress(f"⚡ {processing_count} tracks\n{short_name}")

    def on_track_completed(self, index, success, message, after_lufs=0.0, final_peak=0.0):
        """Handle track processing completed"""
        if success:
            self.center_panel.track_table.update_track_status(index, 'completed')
            self.center_panel.track_table.update_after_processing(index, after_lufs, final_peak)
            
            # Store processed file path
            if index < len(self.tracks):
                track = self.tracks[index]
                original_name = track['name']
                output_format = self.left_panel.get_output_format()
                processed_name = self.get_output_filename(original_name, output_format)
                processed_path = os.path.join(self.output_folder, processed_name)
                
                track['processed_path'] = processed_path
                
                name_item = self.center_panel.track_table.item(index, 0)
                if name_item:
                    name_item.setData(Qt.UserRole + 1, processed_path)
        
        elif "Skipped by user" in message:
            pass
        else:
            self.center_panel.track_table.update_track_status(index, 'error')

    def on_progress_updated(self, current, total):
        """Handle progress update"""
        self.left_panel.update_progress(
            self.left_panel.progress_label.text(),
            value=current
        )

    def on_all_completed(self, processed, total):
        """Handle all processing completed"""
        self.left_panel.update_progress(f"Complete! {processed}/{total}")
        self.left_panel.hide_progress()
        self.left_panel.set_processing_state(False)

    def skip_track(self, track_index):
        """Skip individual track"""
        self.bg_processor.skip_track(track_index)
        self.center_panel.track_table.update_track_status(track_index, 'skipped')
    
    def remove_track(self, track_index):
        """Remove individual track"""
        if 0 <= track_index < len(self.tracks):
            del self.tracks[track_index]
            self.center_panel.track_table.removeRow(track_index)

    def setup_folder_watching(self):
        """Initialize folder watching"""
        for folder_config in self.watch_config.get_enabled_folders():
            self.folder_watcher.add_watch(folder_config['path'], folder_config)
        
        self.folder_watcher.file_detected.connect(self.on_file_detected)

    def on_watch_added(self, path, config):
        """Handle watch folder added"""
        self.folder_watcher.add_watch(path, config)

    def on_watch_removed(self, path):
        """Handle watch folder removed"""
        self.folder_watcher.remove_watch(path)

    def on_watch_toggled(self, path, enabled):
        """Handle watch folder toggled"""
        if enabled:
            for config in self.watch_config.watched_folders:
                if config['path'] == path:
                    self.folder_watcher.add_watch(path, config)
                    break
        else:
            self.folder_watcher.remove_watch(path)

    def on_file_detected(self, file_path, watch_folder_path):
        """Handle new file detected in watched folder"""
        config = None
        for folder_config in self.watch_config.watched_folders:
            if folder_config['path'] == watch_folder_path:
                config = folder_config
                break
        
        if not config or not config.get('enabled', True):
            return
        
        filename = os.path.basename(file_path)
        if self._is_processed_file(filename):
            self.center_panel.folder_watch_panel.log_activity(f"Ignored processed file: {filename}")
            return
        
        for track in self.tracks:
            if track['path'] == file_path:
                self.center_panel.folder_watch_panel.log_activity(f"Duplicate skipped: {os.path.basename(file_path)}")
                return
        
        self.center_panel.folder_watch_panel.log_file_detected(file_path)
        
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
            
            self.center_panel.track_table.add_track(track_data, target_lufs)
            self.right_panel.update_health_display(self.tracks)
            
            if config.get('autoProcess', True):
                self.auto_process_track(len(self.tracks) - 1, config)
        
        analyzer_thread.finished.connect(on_analysis_complete)
        analyzer_thread.start()
        
        if not hasattr(self, '_analyzer_threads'):
            self._analyzer_threads = []
        self._analyzer_threads.append(analyzer_thread)

    def _add_track_async(self, file_path, target_lufs=None):
        """Add track with background analysis"""
        filename = os.path.basename(file_path)
        
        row_index = self.center_panel.track_table.rowCount()
        self.center_panel.track_table.insertRow(row_index)
        
        # Add placeholder cells
        name_item = self.center_panel.track_table._create_item(filename)
        name_item.setData(Qt.UserRole, file_path)
        self.center_panel.track_table.setItem(row_index, 0, name_item)
        self.center_panel.track_table.setItem(row_index, 1, self.center_panel.track_table._create_item("...", center=True))
        self.center_panel.track_table.setItem(row_index, 2, self.center_panel.track_table._create_item("...", center=True))
        self.center_panel.track_table.setItem(row_index, 3, self.center_panel.track_table._create_item("--", center=True))
        self.center_panel.track_table.setItem(row_index, 4, self.center_panel.track_table._create_item("...", center=True))
        self.center_panel.track_table.setItem(row_index, 5, self.center_panel.track_table._create_item("...", center=True))
        
        analyzing_item = self.center_panel.track_table._create_item("⏳ ANALYZING", center=True)
        analyzing_item.setBackground(QColor("#ffaa00"))
        analyzing_item.setForeground(QColor("black"))
        self.center_panel.track_table.setItem(row_index, 6, analyzing_item)
        self.center_panel.track_table.setItem(row_index, 7, self.center_panel.track_table._create_item("--", center=True))
        
        status_item = self.center_panel.track_table._create_item("⏳ ANALYZING", center=True)
        status_item.setBackground(QColor("#ffaa00"))
        status_item.setForeground(QColor("black"))
        self.center_panel.track_table.setItem(row_index, 8, status_item)
        
        placeholder_data = {
            'path': file_path,
            'name': filename,
            'lufs': 0.0,
            'peak_db': 0.0,
            'duration': 0,
            'health_score': 0,
            'status': 'analyzing'
        }
        self.tracks.append(placeholder_data)
        
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
                'name': filename,
                **analysis
            }
            self.tracks[row_index] = track_data
            
            # Update cells
            duration = track_data.get('duration', 0)
            time_str = f"{int(duration//60)}:{int(duration%60):02d}" if duration > 0 else "0:00"
            self.center_panel.track_table.setItem(row_index, 1, self.center_panel.track_table._create_item(time_str, center=True))
            
            before_lufs = track_data['lufs']
            lufs_item = self.center_panel.track_table._create_item(f"{before_lufs:.1f}", center=True)
            lufs_item.setBackground(self.center_panel.track_table._get_lufs_color(before_lufs))
            if before_lufs < -16 or before_lufs > -6:
                lufs_item.setForeground(QColor("white"))
            self.center_panel.track_table.setItem(row_index, 2, lufs_item)
            
            peak = track_data['peak_db']
            is_optimized = self.center_panel.track_table._check_if_optimized(before_lufs, peak, target_lufs)
            
            if is_optimized:
                after_item = self.center_panel.track_table._create_item(f"{before_lufs:.1f}", center=True)
                after_item.setBackground(QColor("#00aa44"))
                after_item.setForeground(QColor("white"))
                self.center_panel.track_table.setItem(row_index, 3, after_item)
            else:
                if target_lufs:
                    self.center_panel.track_table.setItem(row_index, 3, self.center_panel.track_table._create_item(f"{target_lufs:.1f}", center=True))
                else:
                    self.center_panel.track_table.setItem(row_index, 3, self.center_panel.track_table._create_item("--", center=True))
            
            peak_item = self.center_panel.track_table._create_item(f"{peak:.1f}", center=True)
            if peak > -1:
                peak_item.setBackground(QColor("#ff4444"))
                peak_item.setForeground(QColor("white"))
            self.center_panel.track_table.setItem(row_index, 4, peak_item)
            
            health_score = track_data.get('health_score', 0)
            health_item = self.center_panel.track_table._create_item(f"{health_score}", center=True)
            health_item.setBackground(self.center_panel.track_table._get_health_color(health_score))
            health_item.setForeground(QColor("white"))
            self.center_panel.track_table.setItem(row_index, 5, health_item)
            
            club_safe = self.center_panel.track_table.is_club_safe(before_lufs, peak)
            if is_optimized and club_safe:
                badge_text = "🟢 OPTIMIZED"
                badge_color = "#00aa44"
            elif club_safe:
                badge_text = "🟢 SAFE"
                badge_color = "#00aa44"
            else:
                badge_text = "🔴 FIX"
                badge_color = "#aa4444"
            
            badge_item = self.center_panel.track_table._create_item(badge_text, center=True)
            badge_item.setBackground(QColor(badge_color))
            badge_item.setForeground(QColor("white"))
            self.center_panel.track_table.setItem(row_index, 6, badge_item)
            
            if is_optimized:
                gain_item = self.center_panel.track_table._create_item("✓", center=True)
                gain_item.setBackground(QColor("#00aa44"))
                gain_item.setForeground(QColor("white"))
                self.center_panel.track_table.setItem(row_index, 7, gain_item)
            else:
                self.center_panel.track_table.setItem(row_index, 7, self.center_panel.track_table._create_item("--", center=True))
            
            if is_optimized:
                status_item = self.center_panel.track_table._create_item("✅ OPTIMIZED", center=True)
                status_item.setBackground(QColor("#00aa44"))
                status_item.setForeground(QColor("white"))
            else:
                status_item = self.center_panel.track_table._create_item("READY", center=True)
                status_item.setBackground(QColor("#4444aa"))
                status_item.setForeground(QColor("white"))
            self.center_panel.track_table.setItem(row_index, 8, status_item)
            
            self.right_panel.update_health_display(self.tracks)
        
        analyzer_thread.finished.connect(on_analysis_complete)
        analyzer_thread.start()
        
        if not hasattr(self, '_analyzer_threads'):
            self._analyzer_threads = []
        self._analyzer_threads.append(analyzer_thread)

    def auto_process_track(self, track_index, config):
        """Auto-process single track from watched folder"""
        if track_index >= len(self.tracks):
            return
        
        track = self.tracks[track_index]
        output_folder = config.get('outputFolder', config['path'])
        input_path = track['path']
        filename = track['name']
        
        preset = self.preset_manager.get_preset(config['presetId'])
        output_format = preset.get('output_format', 'wav_24') if preset else 'wav_24'
        
        output_filename = self.bg_processor.get_output_filename(filename, output_format)
        output_path = os.path.join(output_folder, output_filename)
        
        self.center_panel.track_table.update_track_status(track_index, 'processing')
        
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
        
        thread = SingleTrackProcessor(
            self.processor, 
            input_path, 
            config['presetId'], 
            output_path, 
            output_format
        )
        
        def on_finished():
            result = thread.result
            
            if result and result['success']:
                self.center_panel.track_table.update_track_status(track_index, 'completed')
                after_lufs = result.get('final_lufs', -12.0)
                final_peak = -1.0
                self.center_panel.track_table.update_after_processing(track_index, after_lufs, final_peak)
                
                if config.get('deleteOriginal', False):
                    try:
                        os.remove(input_path)
                        self.center_panel.folder_watch_panel.log_activity(f"🗑 Deleted original: {filename}")
                    except Exception as e:
                        self.center_panel.folder_watch_panel.log_activity(f"⚠️ Failed to delete: {filename} - {str(e)}")
                
                self.center_panel.folder_watch_panel.log_file_processed(input_path, True)
            else:
                self.center_panel.track_table.update_track_status(track_index, 'error')
                self.center_panel.folder_watch_panel.log_file_processed(input_path, False)
        
        thread.finished.connect(on_finished)
        thread.start()
        
        if not hasattr(self, '_auto_process_threads'):
            self._auto_process_threads = []
        self._auto_process_threads.append(thread)

    def get_output_filename(self, original_name, output_format):
        """Generate output filename"""
        clean_name = self.clean_filename(original_name)
        
        if output_format == "aiff":
            ext = ".aiff"
        elif output_format == "flac":
            ext = ".flac"
        else:
            ext = ".wav"
        
        naming = self.left_panel.get_naming_convention()
        if naming == "Original - DJ OPT":
            return f"{clean_name} - DJ OPT{ext}"
        elif naming == "DJ OPT - Original":
            return f"DJ OPT - {clean_name}{ext}"
        elif naming == "Original (Optimized)":
            return f"{clean_name} (Optimized){ext}"
        elif naming == "Original_DJ_OPT":
            return f"{clean_name}_DJ_OPT{ext}"
        else:
            return f"{clean_name} - DJ OPT{ext}"

    def clean_filename(self, filename):
        """Clean filename by removing unwanted phrases"""
        import re
        
        base_name = os.path.splitext(filename)[0]
        
        unwanted_phrases = [
            r'\(official\s+video\)', r'\(official\s+audio\)',
            r'\(official\s+music\s+video\)', r'\(music\s+video\)',
            r'\(lyric\s+video\)', r'\(lyrics\)', r'\(hd\)', r'\(4k\)',
            r'\(1080p\)', r'\(720p\)', r'\[official\s+video\]',
            r'\[official\s+audio\]', r'\[official\s+music\s+video\]',
            r'\[music\s+video\]', r'\[lyric\s+video\]', r'\[lyrics\]',
            r'\[hd\]', r'\[4k\]', r'\[1080p\]', r'\[720p\]',
            r'official\s+video', r'official\s+audio',
            r'official\s+music\s+video', r'music\s+video',
            r'lyric\s+video', r'lyrics'
        ]
        
        cleaned_name = base_name
        for phrase in unwanted_phrases:
            cleaned_name = re.sub(phrase, '', cleaned_name, flags=re.IGNORECASE)
        
        cleaned_name = re.sub(r'\s+', ' ', cleaned_name)
        cleaned_name = re.sub(r'\s*-\s*$', '', cleaned_name)
        cleaned_name = re.sub(r'^\s*-\s*', '', cleaned_name)
        cleaned_name = cleaned_name.strip()
        
        return cleaned_name if cleaned_name else base_name

    def _is_processed_file(self, filename):
        """Check if filename indicates already processed"""
        processed_patterns = ['- DJ OPT', 'DJ OPT -', '(Optimized)', '_DJ_OPT']
        return any(pattern in filename for pattern in processed_patterns)
    
    def setup_dark_theme(self):
        """Apply clean dark theme"""
        self.setStyleSheet("""
            QMainWindow { background-color: #1a1a1a; color: white; }
            QWidget { background-color: #1a1a1a; color: white; }
            QFrame { background-color: #2d2d2d; border: 1px solid #444; border-radius: 8px; margin: 5px; }
            
            QLabel { 
                color: white; 
                font-size: 12px;
                background: transparent;
                border: none;
            }
            
            QPushButton {
                background-color: #3d3d3d; 
                border: 1px solid #555; 
                border-radius: 4px;
                padding: 6px 12px; 
                color: white; 
                font-size: 12px;
            }
            QPushButton:hover { 
                background-color: #4d4d4d; 
                border-color: #00ff88; 
            }
            
            QComboBox {
                background-color: #3d3d3d; 
                border: 1px solid #555; 
                border-radius: 4px;
                padding: 6px; 
                color: white;
                font-size: 12px;
            }
            QComboBox:hover {
                border-color: #00ff88;
            }
            QComboBox::drop-down { 
                border: none; 
            }
            QComboBox::down-arrow { 
                width: 0; height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid white;
            }
            
            QLineEdit {
                background-color: #3d3d3d;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 6px;
                color: white;
                font-size: 11px;
            }
            
            QProgressBar {
                border: 1px solid #444;
                border-radius: 4px;
                background-color: #2d2d2d;
                color: white;
                text-align: center;
                font-size: 10px;
            }
            QProgressBar::chunk {
                background-color: #00ff88;
                border-radius: 3px;
            }
            
            QTableWidget {
                background-color: #2d2d2d; 
                border: 1px solid #444; 
                border-radius: 6px;
                gridline-color: #444;
            }
            QTableWidget::item { 
                padding: 8px; 
                border-bottom: 1px solid #333; 
            }
            QTableWidget::item:selected { 
                background-color: #00ff88; 
                color: black; 
            }
            QHeaderView::section {
                background-color: #333; 
                color: white; 
                padding: 8px;
                border: none; 
                font-weight: bold;
            }
            
            QScrollArea { 
                border: none; 
                background-color: transparent; 
            }
            QScrollBar:vertical {
                background-color: #2d2d2d;
                width: 10px;
            }
            QScrollBar::handle:vertical {
                background-color: #555;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #00ff88;
            }
        """)

    def closeEvent(self, event):
        """Clean up when closing the app"""
        self.folder_watcher.stop()
        event.accept()
