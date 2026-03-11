# DeckReady 🎧

**Professional DJ Audio Optimizer for macOS**

DeckReady is a powerful desktop application designed for DJs and audio professionals to optimize audio tracks for different venues and platforms. Built with professional-grade audio processing, it ensures your tracks sound perfect whether you're playing at a festival, streaming online, or spinning at an intimate lounge.

![Version](https://img.shields.io/badge/version-2.0-brightgreen)
![Platform](https://img.shields.io/badge/platform-macOS-blue)
![License](https://img.shields.io/badge/license-MIT-orange)

---

## ✨ What's New in v2.0

### 🎛️ Custom Preset Management
- **Visual Preset Editor**: Create and edit presets with intuitive sliders for LUFS, True Peak, and Highpass filters
- **Preset Manager**: Organize, duplicate, and manage unlimited custom presets
- **Real-time Validation**: Instant feedback on preset parameters with warnings and errors
- **Locked Defaults**: Built-in presets are protected while custom presets are fully editable

### 📊 Waveform Visualization
- **Before/After Comparison**: Visual waveform analysis showing optimization results
- **Clipping Detection**: Automatic detection and highlighting of audio clipping zones
- **dB Reference Markers**: Clear visual indicators for 0dB and -6dB levels
- **Smart Caching**: Fast waveform generation with intelligent file validation

### 📁 Folder Monitoring System
- **Auto-Watch Folders**: Automatically detect and process new audio files
- **Per-Folder Presets**: Configure different presets for different watch folders
- **Auto-Processing**: Optional automatic processing of detected files
- **Activity Logging**: Real-time log of detected and processed files
- **Delete Original Option**: Automatically remove source files after successful processing

### ⚡ Performance & Architecture
- **Multi-Core Processing**: Configurable CPU core usage (1 to all available cores)
- **Parallel Processing**: Process multiple tracks simultaneously
- **Modular UI Architecture**: Clean separation of concerns with panel-based design
- **Async Analysis**: Non-blocking track analysis for smooth UI experience

### 💊 Library Health Dashboard
- **Health Scoring**: Automatic quality assessment for each track
- **Issue Detection**: Identifies clipping, compression, and loudness problems
- **Visual Indicators**: Color-coded health scores and club-safe badges
- **Aggregate Statistics**: Overall library health with detailed breakdowns

---

## 🎯 Core Features

### Loudness Normalization
- **LUFS-Based Processing**: Industry-standard loudness normalization
- **True Peak Limiting**: Prevents digital clipping and distortion
- **Dynamic Range Preservation**: Maintains punch and clarity

### Built-in Venue Presets
- **🎪 Club/Festival** (-8 LUFS): Maximum loudness for large sound systems
- **🍸 Bar/Lounge** (-12 LUFS): Balanced sound for conversation-friendly environments
- **📻 Radio/Broadcast** (-16 LUFS): Broadcast-safe standards compliance
- **🎵 Streaming Safe** (-14 LUFS): Optimized for Spotify, Apple Music, YouTube

### Professional Audio Processing
- **High-Pass Filtering**: Remove sub-bass rumble (20-50 Hz configurable)
- **3-Band EQ**: Fine-tune low, mid, and high frequencies
- **Multiple Export Formats**: WAV (16/24-bit), AIFF, FLAC
- **Flexible Naming**: Multiple output filename conventions

### Intelligent Track Analysis
- **Real-time LUFS Measurement**: Accurate loudness analysis
- **Peak Detection**: True peak and sample peak monitoring
- **Duration & Format Info**: Complete track metadata
- **Auto-Optimization Detection**: Identifies already-optimized tracks

---

## 📋 Requirements

- **Operating System**: macOS 10.15 (Catalina) or later
- **Audio Engine**: FFmpeg (installed via Homebrew)
- **Python**: 3.8+ (for running from source)
- **Disk Space**: 100MB for application + cache storage

---

## 🚀 Installation

### Option 1: Standalone Application (Recommended)

1. Download the latest release from the releases page
2. Drag **DeckReady.app** to your Applications folder
3. Right-click and select "Open" on first launch (macOS security)

### Option 2: Run from Source

#### Install FFmpeg
```bash
brew install ffmpeg
```
#### Clone Repository
```bash
[Repository:](https://github.com/ollyfuse/dj-audio-optimizer.git)
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
#### Quick Start Guide
```bash
Basic Workflow

1. Launch DeckReady - Open from Applications folder

2. Add Tracks - Drag & drop audio files or click "Add Tracks"

3. Select Preset - Choose venue-specific preset from left panel

4. Configure Output - Set format, folder, and naming convention

5. Process - Click "PROCESS TRACKS" and monitor progress

6. Review - Check health dashboard and view waveforms

Supported Formats
. Input: MP3, WAV, FLAC, AIFF

. Output: WAV (16/24-bit), AIFF, FLAC


```

#### Interface Overview
```bash
Left Panel - Control Center
.  Preset selection and management

. Output format and folder settings

.  CPU core configuration

.  Progress monitoring

.  Process/cancel controls

Center Panel - Track Management
.  Track Library Tab: Drag & drop, track table, batch operations

.  Folder Monitoring Tab: Auto-watch folders, activity log

Right Panel - Information Hub
.  Preset summary with detailed settings

.  Library health dashboard

.  Track quality statistics
```
#### Tech Stack
```bash

Understanding the Display
Color Coding
LUFS Levels

🟢 Green (-14 to -8): Optimal range

🟡 Yellow (-16 to -14, -8 to -6): Acceptable

🔴 Red (< -16, > -6): Needs optimization

Health Scores

🟢 80-100: Excellent

🟡 60-79: Good

🟠 40-59: Fair

🔴 0-39: Poor

Status Indicators

⏳ Analyzing

✅ Optimized

🔵 Ready

⚡ Processing

✓ Completed

❌ Error


```
#### Tech Stack
```bash
Advanced Features
Custom Preset Creation
  1. Click "Edit" next to preset dropdown

  2. Click "New Preset" in Preset Manager

  3. Adjust LUFS (-18 to -6), True Peak (-1.5 to -0.3), Highpass (20-50 Hz)

  4. Save with custom name

Folder Monitoring
  1.  Switch to "Folder Monitoring" tab

  2.  Click "Add Watched Folder"

  3.  Configure preset, auto-process, output location

  4.  Enable monitoring for automated workflow

Waveform Analysis
  1.  Right-click any track

  2.  Select "📊 View Waveform"

  3.  View before/after comparison

  4.  Check clipping zones and peak levels

Multi-Core Processing
  . Select CPU cores from dropdown

  . Auto mode uses all cores minus one

  . More cores = faster batch processing
```
#### Tech Stack

```bash
. UI Framework: PySide6 (Qt for Python)

. Audio Processing: FFmpeg with loudnorm filter

. Audio Analysis: pyloudnorm, scipy, soundfile

. Parallel Processing: Python multiprocessing

. Waveform Generation: Custom peak detection algorithm

. Build Tool: PyInstaller

```
#### Troubleshooting
```bash

Common Issues
App Won't Launch

  . Right-click → "Open" to bypass macOS security

FFmpeg Not Found

  .  Install via Homebrew: brew install ffmpeg

Processing Fails

  . Verify file format is supported

  . Check FFmpeg installation

  . Reduce CPU core count

Waveform Not Displaying

  . Ensure track is analyzed

  . Verify file exists

  . Clear cache: delete temp/waveform_cache/
```
#### Troubleshooting
```bash
Best Practices
For DJs
  . Use Club/Festival preset for loud venues

  . Use Bar/Lounge preset for intimate settings

  . Check Club Safe badge before gigs

  . Review waveforms to verify quality

For Producers
  . Use Streaming Safe preset for releases

  . Create custom presets per platform

  . Monitor health scores

  . Keep original files

For Batch Processing
  . Use Auto CPU cores for speed

  . Enable folder monitoring for automation

  . Organize by venue/platform

  . Use consistent naming
```
#### Documentation
```bash
README.md (this file): Quick overview and installation

docs/USER_GUIDE.md: Comprehensive user manual
```
#### Contributing
```bash
Contributions welcome! Please submit pull requests or open issues for bugs and feature requests.
```
#### License
```bash
MIT License - See LICENSE file for details
```
#### Author
```bash
DJ-FUSE
Professional DJ Audio Optimizer

Repository: https://github.com/ollyfuse/dj-audio-optimizer
```
 #### Support
```bash
GitHub Issues: Report bugs and request features

User Guide: See docs/USER_GUIDE.md

Email: mailto:cyotero26@gmail.com
```
#### Acknowledgments
```bash
.  FFmpeg team for audio processing engine

.  Qt/PySide6 for UI framework

.  pyloudnorm for LUFS algorithms

.  Open source community
```
Version 2.0 | © 2026 DJ-FUSE (Rwanda) | Made with ❤️ for DJs worldwide

