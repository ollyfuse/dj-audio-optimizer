# DeckReady 🎧

Professional DJ audio optimizer for macOS. Normalize loudness, optimize tracks for different venues, and export in multiple formats.

## Features

- **Loudness Normalization**: LUFS-based processing for consistent volume across tracks
- **Venue-Specific Presets**: 
  - Club/Festival (-8 LUFS) - Loud, punchy sound
  - Bar/Lounge (-12 LUFS) - Smooth, conversation-friendly
  - Radio/Broadcast (-16 LUFS) - Broadcast-safe standards
  - Streaming Safe (-14 LUFS) - Spotify/Apple Music compliant
- **Multiple Export Formats**: WAV (16/24-bit), AIFF, FLAC
- **Batch Processing**: Process multiple tracks simultaneously
- **Drag & Drop Interface**: Simple, intuitive workflow
- **Real-time Analysis**: View original and final LUFS measurements

## Requirements

- macOS 10.15+
- FFmpeg (installed via Homebrew)

## Installation

### Install FFmpeg
```bash
brew install ffmpeg
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Run Application
```bash
python app.py
```
#### Building Standalone App
```bash
python clean_build.py
The built app will be in dist/DeckReady/. Copy to Applications:
cp -R dist/DeckReady /Applications/
```
#### Usage
```bash
1. Launch DeckReady
2. Drag and drop audio files into the window
3. Select a preset or customize settings.
4. Click "Process" to optimize your tracks.
5. Processed files saved by default to ~/Desktop 
```

#### Tech Stack
```bash
UI: PySide6 (Qt for Python)

Audio Processing: FFmpeg with loudnorm filter

Analysis: pyloudnorm, scipy

Build: PyInstaller

License

MIT

Version
1.0 - Initial Release
```

