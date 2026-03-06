from PySide6.QtCore import QObject, Signal, QTimer
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import time

class AudioFileHandler(FileSystemEventHandler):
    """Handles file system events for audio files"""
    
    AUDIO_EXTENSIONS = {'.mp3', '.wav', '.flac', '.aiff', '.m4a', '.aac'}
    
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.pending_files = {}  # file_path: timestamp
        
    def on_created(self, event):
        if event.is_directory:
            return
        
        file_path = event.src_path
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext in self.AUDIO_EXTENSIONS:
            self.pending_files[file_path] = time.time()
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        file_path = event.src_path
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext in self.AUDIO_EXTENSIONS:
            self.pending_files[file_path] = time.time()
    
    def get_ready_files(self, debounce_seconds=2.0):
        """Get files that haven't been modified for debounce_seconds"""
        current_time = time.time()
        ready_files = []
        
        for file_path, timestamp in list(self.pending_files.items()):
            if current_time - timestamp >= debounce_seconds:
                if os.path.exists(file_path) and os.access(file_path, os.R_OK):
                    ready_files.append(file_path)
                del self.pending_files[file_path]
        
        return ready_files


class FolderWatcher(QObject):
    """Watches folders for new audio files"""
    
    file_detected = Signal(str, str)  # file_path, watch_folder_path
    
    def __init__(self):
        super().__init__()
        self.observer = Observer()
        self.handlers = {}  # watch_path: handler
        self.watch_configs = {}  # watch_path: config
        self.debounce_timer = QTimer()
        self.debounce_timer.timeout.connect(self._check_pending_files)
        self.debounce_timer.setInterval(1000)  # Check every second
        
    def add_watch(self, folder_path, config):
        """Add a folder to watch"""
        if folder_path in self.handlers:
            return
        
        handler = AudioFileHandler(lambda f: self.file_detected.emit(f, folder_path))
        self.handlers[folder_path] = handler
        self.watch_configs[folder_path] = config
        
        try:
            self.observer.schedule(handler, folder_path, recursive=False)
            if not self.observer.is_alive():
                self.observer.start()
                self.debounce_timer.start()
        except Exception as e:
            print(f"Error watching folder {folder_path}: {e}")
    
    def remove_watch(self, folder_path):
        """Remove a folder from watching"""
        if folder_path in self.handlers:
            del self.handlers[folder_path]
            del self.watch_configs[folder_path]
    
    def stop(self):
        """Stop watching all folders"""
        self.debounce_timer.stop()
        if self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
    
    def _check_pending_files(self):
        """Check for files ready to process"""
        for folder_path, handler in self.handlers.items():
            ready_files = handler.get_ready_files()
            for file_path in ready_files:
                self.file_detected.emit(file_path, folder_path)
