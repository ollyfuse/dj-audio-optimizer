from PySide6.QtCore import QThread, Signal
from .processor import AudioProcessor
import os

class BackgroundProcessor(QThread):
    # Signals for UI updates
    track_started = Signal(int, str)  # track_index, track_name
    track_completed = Signal(int, bool, str, float, float)  # track_index, success, message, after_lufs, final_peak
    progress_updated = Signal(int, int)  # current, total
    all_completed = Signal(int, int)  # processed_count, total_count
    
    def __init__(self):
        super().__init__()
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


    
    def stop_processing(self):
        """Stop the processing"""
        self.should_stop = True
    
    def run(self):
        """Background processing thread with pause/resume support"""
        processed = 0
        total = len(self.tracks)
        
        for i, track in enumerate(self.tracks):
            # Check for stop
            if self.should_stop:
                break
                
            # Check for skip
            if i in self.skip_tracks:
                self.track_completed.emit(i, False, "Skipped by user", 0.0, 0.0)
                self.progress_updated.emit(i + 1, total)
                continue
                
            # Handle pause
            while self.is_paused and not self.should_stop:
                self.msleep(100)  # Sleep 100ms while paused
                
            if self.should_stop:
                break
                
            # Emit track started signal
            self.track_started.emit(i, track['name'])
            
            # Process track (existing code)
            input_path = track['path']
            filename = track['name']
            output_filename = self.get_output_filename(filename, self.output_format)
            output_path = os.path.join(self.output_folder, output_filename)
            result = self.processor.process_track(input_path, self.preset_key, output_path, self.output_format)
            
            # Emit completion signal
            if result['success']:
                processed += 1
                after_lufs = result.get('final_lufs', -12.0)
                final_peak = -1.0
                self.track_completed.emit(i, True, "Completed successfully", after_lufs, final_peak)
            else:
                self.track_completed.emit(i, False, result.get('error', 'Unknown error'), 0.0, 0.0)
            
            # Update progress
            self.progress_updated.emit(i + 1, total)
        
        # Emit final completion
        self.all_completed.emit(processed, total)


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
        if self.naming_convention == "Original - DJ OPT":
            return f"{clean_name} - DJ OPT{ext}"
        elif self.naming_convention == "DJ OPT - Original":
            return f"DJ OPT - {clean_name}{ext}"
        elif self.naming_convention == "Original (Optimized)":
            return f"{clean_name} (Optimized){ext}"
        elif self.naming_convention == "Original_DJ_OPT":
            return f"{clean_name}_DJ_OPT{ext}"
        else:
            return f"{clean_name} - DJ OPT{ext}"  # Default
    def pause_processing(self):
        """Pause processing"""
        self.is_paused = True

    def resume_processing(self):
        """Resume processing"""
        self.is_paused = False

    def skip_track(self, track_index):
        """Skip a specific track"""
        self.skip_tracks.add(track_index)
