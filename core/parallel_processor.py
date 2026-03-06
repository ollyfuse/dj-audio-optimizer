from PySide6.QtCore import QThread, Signal
from concurrent.futures import ThreadPoolExecutor, as_completed
from .processor import AudioProcessor
import os
import multiprocessing

class ParallelProcessor(QThread):
    """Multi-core parallel audio processor"""
    
    # Signals
    track_started = Signal(int, str)  # track_index, track_name
    track_completed = Signal(int, bool, str, float, float)  # index, success, message, lufs, peak
    progress_updated = Signal(int, int)  # current, total
    all_completed = Signal(int, int)  # processed_count, total_count
    
    def __init__(self, max_workers=None):
        super().__init__()
        # Auto-detect CPU cores, leave 1 core free for system
        cpu_count = multiprocessing.cpu_count()
        self.max_workers = max_workers or max(1, cpu_count - 1)
        
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
        """Stop processing"""
        self.should_stop = True
    
    def skip_track(self, track_index):
        """Skip a specific track"""
        self.skip_tracks.add(track_index)
    
    def get_output_filename(self, original_name, output_format):
        """Generate output filename"""
        import re
        base_name = os.path.splitext(original_name)[0]
        
        # Clean filename
        unwanted = [
            r'\(official\s+video\)', r'\(official\s+audio\)',
            r'\[official\s+video\]', r'\[official\s+audio\]',
            r'official\s+video', r'official\s+audio'
        ]
        for phrase in unwanted:
            base_name = re.sub(phrase, '', base_name, flags=re.IGNORECASE)
        base_name = re.sub(r'\s+', ' ', base_name).strip()
        
        # Extension
        ext = ".aiff" if output_format == "aiff" else ".flac" if output_format == "flac" else ".wav"
        
        # Apply naming convention
        if self.naming_convention == "Original - DJ OPT":
            return f"{base_name} - DJ OPT{ext}"
        elif self.naming_convention == "DJ OPT - Original":
            return f"DJ OPT - {base_name}{ext}"
        elif self.naming_convention == "Original (Optimized)":
            return f"{base_name} (Optimized){ext}"
        elif self.naming_convention == "Original_DJ_OPT":
            return f"{base_name}_DJ_OPT{ext}"
        else:
            return f"{base_name} - DJ OPT{ext}"
    
    def process_single_track(self, index, track):
        """Process a single track (runs in thread pool)"""
        if self.should_stop or index in self.skip_tracks:
            return (index, False, "Skipped", 0.0, 0.0)
        
        try:
            # Create processor instance (each thread needs its own)
            processor = AudioProcessor()
            
            input_path = track['path']
            filename = track['name']
            output_filename = self.get_output_filename(filename, self.output_format)
            output_path = os.path.join(self.output_folder, output_filename)
            
            # Emit started signal
            self.track_started.emit(index, filename)
            
            # Process track
            result = processor.process_track(input_path, self.preset_key, output_path, self.output_format)
            
            if result['success']:
                after_lufs = result.get('final_lufs', -12.0)
                final_peak = -1.0
                return (index, True, "Success", after_lufs, final_peak)
            else:
                return (index, False, result.get('error', 'Unknown error'), 0.0, 0.0)
        
        except Exception as e:
            return (index, False, str(e), 0.0, 0.0)
    
    def run(self):
        """Run parallel processing"""
        total = len(self.tracks)
        processed = 0
        completed_count = 0
        
        # Create thread pool
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            futures = {
                executor.submit(self.process_single_track, i, track): i 
                for i, track in enumerate(self.tracks)
            }
            
            # Process results as they complete
            for future in as_completed(futures):
                if self.should_stop:
                    break
                
                try:
                    index, success, message, lufs, peak = future.result()
                    
                    if success:
                        processed += 1
                    
                    completed_count += 1
                    
                    # Emit completion signal
                    self.track_completed.emit(index, success, message, lufs, peak)
                    
                    # Update progress
                    self.progress_updated.emit(completed_count, total)
                
                except Exception as e:
                    print(f"Error processing track: {e}")
        
        # Emit final completion
        self.all_completed.emit(processed, total)
