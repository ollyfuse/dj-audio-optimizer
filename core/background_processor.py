from PySide6.QtCore import QThread, Signal
from .processor import AudioProcessor
from .utils import get_output_filename
import os


class BackgroundProcessor(QThread):
    """Sequential single-core audio processor"""

    track_started = Signal(int, str)
    track_completed = Signal(int, bool, str, float, float)
    progress_updated = Signal(int, int)
    all_completed = Signal(int, int)

    def __init__(self):
        super().__init__()
        # Single shared processor — reused across all tracks in the batch
        self.processor = AudioProcessor()
        self.tracks = []
        self.preset_key = ""
        self.should_stop = False
        self.output_format = "wav_24"
        self.output_folder = ""
        self.naming_convention = "Original - DJ OPT"
        self.is_paused = False
        self.skip_tracks = set()

    def setup_batch(self, tracks, preset_key, output_format="wav_24", output_folder="", naming_convention="Original - DJ OPT"):
        """Setup tracks for batch processing"""
        self.tracks = tracks
        self.preset_key = preset_key
        self.output_format = output_format
        self.output_folder = output_folder
        self.naming_convention = naming_convention
        self.should_stop = False
        self.skip_tracks = set()  # reset skips on each new batch

    def stop_processing(self):
        self.should_stop = True

    def pause_processing(self):
        self.is_paused = True

    def resume_processing(self):
        self.is_paused = False

    def skip_track(self, track_index):
        self.skip_tracks.add(track_index)

    def get_output_filename(self, original_name, output_format):
        return get_output_filename(original_name, output_format, self.naming_convention)

    def run(self):
        """Sequential processing with pause/resume support"""
        processed = 0
        total = len(self.tracks)

        for i, track in enumerate(self.tracks):
            if self.should_stop:
                break

            if i in self.skip_tracks:
                self.track_completed.emit(i, False, "Skipped by user", 0.0, 0.0)
                self.progress_updated.emit(i + 1, total)
                continue

            while self.is_paused and not self.should_stop:
                self.msleep(100)

            if self.should_stop:
                break

            self.track_started.emit(i, track['name'])

            input_path = track['path']
            output_filename = self.get_output_filename(track['name'], self.output_format)
            output_path = os.path.join(self.output_folder, output_filename)
            result = self.processor.process_track(input_path, self.preset_key, output_path, self.output_format)

            if result['success']:
                processed += 1
                self.track_completed.emit(i, True, "Completed successfully", result.get('final_lufs', -12.0), -1.0)
            else:
                self.track_completed.emit(i, False, result.get('error', 'Unknown error'), 0.0, 0.0)

            self.progress_updated.emit(i + 1, total)

        self.all_completed.emit(processed, total)
