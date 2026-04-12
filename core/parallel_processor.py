from PySide6.QtCore import QThread, Signal
from concurrent.futures import ThreadPoolExecutor, as_completed
from .processor import AudioProcessor
from .utils import get_output_filename
import os
import multiprocessing


class ParallelProcessor(QThread):
    """Multi-core parallel audio processor with shared processor pool"""

    track_started = Signal(int, str)
    track_completed = Signal(int, bool, str, float, float)
    progress_updated = Signal(int, int)
    all_completed = Signal(int, int)

    def __init__(self, max_workers=None):
        super().__init__()
        cpu_count = multiprocessing.cpu_count()

        # Cap at 4 — FFmpeg is CPU-heavy, more workers = system freeze not speed
        self.max_workers = min(max_workers or (cpu_count - 1), 4)
        self.max_workers = max(1, self.max_workers)

        # Pre-build processor pool — one instance per worker, reused across all tracks
        # Avoids creating AudioProcessor (+ PresetManager + disk reads) per track
        self.processor_pool = [AudioProcessor() for _ in range(self.max_workers)]

        self.tracks = []
        self.preset_key = ""
        self.output_format = "wav_24"
        self.output_folder = ""
        self.naming_convention = "Original - DJ OPT"
        self.should_stop = False
        self.skip_tracks = set()

    def setup_batch(self, tracks, preset_key, output_format="wav_24", output_folder="", naming_convention="Original - DJ OPT"):
        """Setup tracks for parallel processing"""
        self.tracks = tracks
        self.preset_key = preset_key
        self.output_format = output_format
        self.output_folder = output_folder
        self.naming_convention = naming_convention
        self.should_stop = False
        self.skip_tracks = set()

    def stop_processing(self):
        self.should_stop = True

    def skip_track(self, track_index):
        self.skip_tracks.add(track_index)

    def get_output_filename(self, original_name, output_format):
        return get_output_filename(original_name, output_format, self.naming_convention)

    def process_single_track(self, index, track, processor):
        """Process a single track using an assigned processor from the pool"""
        if self.should_stop or index in self.skip_tracks:
            return (index, False, "Skipped", 0.0, 0.0)

        try:
            input_path = track['path']
            filename = track['name']
            output_filename = self.get_output_filename(filename, self.output_format)
            output_path = os.path.join(self.output_folder, output_filename)

            self.track_started.emit(index, filename)

            result = processor.process_track(input_path, self.preset_key, output_path, self.output_format)

            if result['success']:
                return (index, True, "Success", result.get('final_lufs', -12.0), -1.0)
            else:
                return (index, False, result.get('error', 'Unknown error'), 0.0, 0.0)

        except Exception as e:
            return (index, False, str(e), 0.0, 0.0)

    def run(self):
        """Run parallel processing with pooled processors"""
        total = len(self.tracks)
        processed = 0
        completed_count = 0

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Assign each track a processor from the pool using round-robin
            futures = {
                executor.submit(
                    self.process_single_track,
                    i,
                    track,
                    self.processor_pool[i % self.max_workers]
                ): i
                for i, track in enumerate(self.tracks)
            }

            for future in as_completed(futures):
                if self.should_stop:
                    break

                try:
                    index, success, message, lufs, peak = future.result()
                    if success:
                        processed += 1
                    completed_count += 1
                    self.track_completed.emit(index, success, message, lufs, peak)
                    self.progress_updated.emit(completed_count, total)
                except Exception as e:
                    print(f"Error processing track: {e}")

        self.all_completed.emit(processed, total)
