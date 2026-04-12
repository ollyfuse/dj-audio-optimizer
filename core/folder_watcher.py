from PySide6.QtCore import QObject, Signal, QTimer
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import time
import hashlib


class AudioFileHandler(FileSystemEventHandler):
    """Handles file system events for audio files"""

    AUDIO_EXTENSIONS = {'.mp3', '.wav', '.flac', '.aiff', '.m4a', '.aac'}

    def __init__(self):
        super().__init__()
        self.pending_files = {}  # file_path: timestamp

    def on_created(self, event):
        if event.is_directory:
            return
        file_path = event.src_path
        if os.path.splitext(file_path)[1].lower() in self.AUDIO_EXTENSIONS:
            self.pending_files[file_path] = time.time()

    def on_modified(self, event):
        if event.is_directory:
            return
        file_path = event.src_path
        if os.path.splitext(file_path)[1].lower() in self.AUDIO_EXTENSIONS:
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

    file_detected = Signal(str, str)        # file_path, watch_folder_path
    duplicate_detected = Signal(str, str)   # file_path, reason — for UI logging

    def __init__(self):
        super().__init__()
        self.observer = Observer()
        self.handlers = {}       # watch_path: handler
        self.watch_handles = {}  # watch_path: watchdog watch handle
        self.watch_configs = {}  # watch_path: config

        # Session-level hash registry — content-based duplicate prevention
        # sha256 of first 64KB: fast on large audio files, reliable for dedup
        self._seen_hashes = set()

        self.debounce_timer = QTimer()
        self.debounce_timer.timeout.connect(self._check_pending_files)
        self.debounce_timer.setInterval(1000)

    def add_watch(self, folder_path, config):
        """Add a folder to watch"""
        if folder_path in self.handlers:
            return

        if not self.observer.is_alive():
            self.observer = Observer()

        handler = AudioFileHandler()
        self.handlers[folder_path] = handler
        self.watch_configs[folder_path] = config

        try:
            watch_handle = self.observer.schedule(handler, folder_path, recursive=False)
            self.watch_handles[folder_path] = watch_handle

            if not self.observer.is_alive():
                self.observer.start()
                self.debounce_timer.start()
        except Exception as e:
            print(f"Error watching folder {folder_path}: {e}")

    def remove_watch(self, folder_path):
        """Remove a folder from watching"""
        if folder_path in self.handlers:
            watch_handle = self.watch_handles.pop(folder_path, None)
            if watch_handle:
                try:
                    self.observer.unschedule(watch_handle)
                except Exception as e:
                    print(f"Error unscheduling watch for {folder_path}: {e}")

            del self.handlers[folder_path]
            del self.watch_configs[folder_path]

    def stop(self):
        """Stop watching all folders"""
        self.debounce_timer.stop()
        if self.observer.is_alive():
            self.observer.stop()
            self.observer.join()

    def clear_seen_hashes(self):
        """Reset duplicate registry — call if user wants to reprocess same files"""
        self._seen_hashes.clear()

    def _file_hash(self, file_path):
        """
        sha256 of first 64KB — fast on large audio files.
        Full-file hashing on a 50MB WAV would take ~200ms per file,
        which blocks the debounce timer. 64KB is enough to distinguish
        any two different audio files in practice.
        """
        try:
            h = hashlib.sha256()
            with open(file_path, 'rb') as f:
                h.update(f.read(65536))  # 64KB
            return h.hexdigest()
        except Exception:
            return None

    def _check_pending_files(self):
        """Check for files ready to process, with content-based duplicate filtering"""
        for folder_path, handler in self.handlers.items():
            ready_files = handler.get_ready_files()

            for file_path in ready_files:
                file_hash = self._file_hash(file_path)

                if file_hash is None:
                    # Can't hash — skip silently, file may have been deleted
                    continue

                if file_hash in self._seen_hashes:
                    # Same content already seen this session — duplicate
                    self.duplicate_detected.emit(
                        file_path,
                        f"Duplicate content: {os.path.basename(file_path)}"
                    )
                    continue

                # New file — register hash and emit for processing
                self._seen_hashes.add(file_hash)
                self.file_detected.emit(file_path, folder_path)
