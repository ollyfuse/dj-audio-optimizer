# DeckReady User Guide 📚

**Complete Guide to Professional Audio Optimization**

Version 2.0 | Last Updated: January 2026

---

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Understanding Audio Concepts](#understanding-audio-concepts)
4. [Main Interface Overview](#main-interface-overview)
5. [Basic Operations](#basic-operations)
6. [Advanced Features](#advanced-features)
7. [Preset Management](#preset-management)
8. [Folder Monitoring](#folder-monitoring)
9. [Waveform Analysis](#waveform-analysis)
10. [Optimization Tips](#optimization-tips)
11. [Troubleshooting](#troubleshooting)
12. [FAQ](#faq)

---

## Introduction

### What is DeckReady?

DeckReady is a professional audio optimization tool designed specifically for DJs and audio professionals. It solves the common problem of inconsistent loudness across tracks in your library by normalizing audio to industry-standard LUFS (Loudness Units Full Scale) targets.

### Why Use DeckReady?

**Problem**: Different tracks have different loudness levels, causing you to constantly adjust volume during sets.

**Solution**: DeckReady normalizes all tracks to consistent loudness targets optimized for specific venues and platforms.

**Benefits**:
- ✅ Seamless transitions between tracks
- ✅ No more volume jumping
- ✅ Venue-optimized sound
- ✅ Professional audio quality
- ✅ Batch processing saves time
- ✅ Automated workflow with folder monitoring

### Who Should Use DeckReady?

- **Club DJs**: Optimize tracks for loud sound systems
- **Mobile DJs**: Prepare tracks for various venue types
- **Radio DJs**: Ensure broadcast-safe audio
- **Producers**: Prepare releases for streaming platforms
- **Audio Engineers**: Batch normalize audio libraries
- **Content Creators**: Optimize audio for podcasts and videos

---

## Getting Started

### First Launch

1. **Open DeckReady** from your Applications folder
2. **Grant Permissions** if macOS requests access to folders
3. **Familiarize Yourself** with the three-panel interface:
   - Left: Control center
   - Center: Track management
   - Right: Information hub

### Your First Track Optimization

#### Step 1: Add a Track
- **Method A**: Drag an audio file into the center panel
- **Method B**: Click "Add Tracks" button and browse

**Supported Formats**: MP3, WAV, FLAC, AIFF

#### Step 2: Wait for Analysis
- Track shows "⏳ ANALYZING" status
- Analysis completes in 2-5 seconds
- View original LUFS in "Before LUFS" column
- Health score appears automatically

#### Step 3: Select Preset
- Default preset is "Club/Festival" (-8 LUFS)
- Change preset in left panel dropdown if needed
- View preset details in right panel

#### Step 4: Configure Output (Optional)
- **Format**: WAV 24-bit (default), WAV 16-bit, AIFF, or FLAC
- **Folder**: Desktop (default) or browse to custom location
- **Naming**: Choose filename convention

#### Step 5: Process
- Click green "PROCESS TRACKS" button
- Watch progress bar and status updates
- Processing takes 10-30 seconds per track
- Multiple tracks process in parallel

#### Step 6: Verify Results
- Check "After LUFS" column shows target
- Status changes to "✅ COMPLETED"
- Health score updates if improved
- Find optimized file in output folder

---

## Understanding Audio Concepts

### What is LUFS?

**LUFS** (Loudness Units Full Scale) is the international standard for measuring audio loudness. Unlike peak levels, LUFS measures perceived loudness as humans hear it.

**Key Points**:
- Lower numbers = quieter (e.g., -16 LUFS)
- Higher numbers = louder (e.g., -8 LUFS)
- Range: -23 LUFS (very quiet) to -6 LUFS (very loud)
- Based on psychoacoustic models
- Used by streaming platforms and broadcasters

### LUFS Targets by Venue

| Venue Type | Target LUFS | Characteristics | Use Case |
|------------|-------------|-----------------|----------|
| **Club/Festival** | -8 LUFS | Maximum loudness, punchy | Large sound systems, outdoor events |
| **Bar/Lounge** | -12 LUFS | Balanced, conversation-friendly | Intimate venues, background music |
| **Radio/Broadcast** | -16 LUFS | Broadcast-safe, consistent | Radio stations, podcasts |
| **Streaming** | -14 LUFS | Platform-optimized | Spotify, Apple Music, YouTube |

### What is True Peak?

**True Peak** measures the absolute maximum level of audio, including inter-sample peaks that can cause distortion in digital-to-analog conversion.

**Why It Matters**:
- Digital audio can create peaks between samples
- These peaks cause distortion in DACs
- True peak limiting prevents this

**Recommended Limit**: -1.0 dB
- Prevents clipping on all playback systems
- Ensures compatibility with format conversion
- Maintains headroom for processing
- Industry standard for mastering

### What is High-Pass Filtering?

**High-Pass Filter** removes very low frequencies (sub-bass rumble) that:
- Waste headroom and reduce loudness
- Cause speaker damage (especially small speakers)
- Create muddy, unclear sound
- Aren't audible on most systems
- Interfere with bass frequencies

**Recommended Setting**: 30 Hz
- Removes inaudible rumble (below human hearing)
- Preserves bass punch and impact
- Improves overall clarity
- Increases available headroom

### Dynamic Range

**Dynamic Range** is the difference between the loudest and quietest parts of audio.

**Why It Matters**:
- Too much: Inconsistent volume, quiet sections
- Too little: Fatiguing, lifeless sound
- Just right: Punchy, engaging, professional

**DeckReady's Approach**:
- Preserves natural dynamics
- Applies intelligent compression
- Maintains punch and energy
- Avoids over-compression

---

## Main Interface Overview

### Left Panel: Control Center

The left panel is your command center for all processing operations.

#### Logo Section
- **DECKREADY** branding at top
- Visual identity and version indicator

#### Preset Section
- **Dropdown Menu**: Select from built-in or custom presets
- **Edit Button**: Opens Preset Manager for creating/editing presets
- Shows currently selected preset name

#### Output Format
- **WAV 24-bit**: Highest quality, large files (~50MB per track)
- **WAV 16-bit**: CD quality, smaller files (~25MB per track)
- **AIFF**: Apple format, same quality as WAV
- **FLAC**: Lossless compression, smallest files (~20MB per track)

#### Output Folder
- **Display Field**: Shows current output location
- **Browse Button**: Change output folder
- Default: Desktop (`~/Desktop`)

#### Naming Convention
Choose how processed files are named:
- **Original - DJ OPT**: `Track Name - DJ OPT.wav`
- **DJ OPT - Original**: `DJ OPT - Track Name.wav`
- **Original (Optimized)**: `Track Name (Optimized).wav`
- **Original_DJ_OPT**: `Track_Name_DJ_OPT.wav`

#### CPU Cores
Control processing power allocation:
- **Auto (N)**: Uses all cores minus one (recommended)
- **1 core**: Minimal system impact, slowest
- **2-4 cores**: Balanced performance
- **Max cores**: Maximum speed, high system load

#### Progress Display
- **Status Text**: Current operation description
- **Progress Bar**: Visual completion indicator
- **Track Count**: Number of tracks being processed
- **Current Track**: Name of track being processed

#### Process Button
- **Green "PROCESS TRACKS"**: Start processing queue
- **Red "⏹ CANCEL ALL"**: Stop all processing
- Changes dynamically based on state

### Center Panel: Track Management

The center panel is where you manage your audio library.

#### Tab Navigation
- **📚 Track Library**: Main track management
- **📁 Folder Monitoring**: Automated processing

#### Track Library Tab

**Drag & Drop Zone**
- Large area at top for dropping files
- Visual feedback on hover
- Supports multiple files simultaneously
- Accepts folders (processes all audio files inside)

**Track Table**
Comprehensive view of all tracks with 9 columns:

1. **Track** (Filename)
   - Full filename without extension
   - Cleaned of common unwanted phrases
   - Sortable alphabetically

2. **Time** (Duration)
   - Format: MM:SS
   - Calculated during analysis
   - Helps estimate processing time

3. **Before LUFS** (Original Loudness)
   - Measured during analysis
   - Color-coded by range
   - Indicates if optimization needed

4. **After LUFS** (Target/Processed)
   - Shows target before processing
   - Shows actual result after processing
   - Green background if already optimized

5. **Peak** (True Peak Level)
   - Measured in dB
   - Red background if > -1.0 dB
   - Critical for preventing clipping

6. **Health** (Quality Score)
   - Range: 0-100
   - Color-coded by quality
   - Based on multiple factors

7. **Club Safe** (Venue Readiness)
   - 🟢 SAFE: Ready for club playback
   - 🔴 FIX: Needs optimization
   - 🟢 OPTIMIZED: Already processed

8. **Gain** (Applied Adjustment)
   - Shows gain change in dB
   - Appears after processing
   - ✓ if already optimized

9. **Status** (Current State)
   - ⏳ ANALYZING: Analysis in progress
   - ✅ OPTIMIZED: Already at target
   - 🔵 READY: Waiting to process
   - ⚡ PROCESSING: Currently processing
   - ✓ COMPLETED: Successfully processed
   - ❌ ERROR: Processing failed
   - ⏭ SKIPPED: Skipped by user

**Action Buttons**
- **+ Add Tracks**: Open file browser
- **🗑 Clear All**: Remove all tracks from table

**Right-Click Context Menu**
- **📊 View Waveform**: Open waveform analysis dialog
- **⏭ Skip Track**: Skip during processing
- **🗑 Remove**: Delete from list

#### Folder Monitoring Tab

**Header Section**
- **Title**: 📁 FOLDER MONITORING
- **Description**: Explains auto-processing feature
- **Add Button**: ➕ Add Watched Folder

**Watched Folders List**
Shows all monitored folders with:
- **Status Indicator**: 🟢 enabled / 🔴 disabled
- **Folder Name**: Base name of folder
- **Preset**: Configured preset for folder
- **Mode**: AUTO or MANUAL processing
- **Delete Flag**: 🗑 DEL if delete original enabled

**Control Buttons**
- **🗑 Remove**: Delete selected watch folder
- **⏸ Disable / ▶ Enable**: Toggle monitoring

**Activity Log**
- Real-time event logging
- Timestamps for all actions
- File detection notifications
- Processing status updates
- Scrollable history
- Monospace font for readability

### Right Panel: Information Hub

The right panel provides detailed information and statistics.

#### Preset Summary Section

**Title**: 📊 PRESET SUMMARY

**Displayed Information**:
- **Preset Name**: Bold, prominent
- **Description**: Italic, explains use case
- **Target LUFS**: Loudness goal
- **True Peak Limit**: Maximum level
- **High-pass Filter**: Rumble removal frequency
- **Output Format**: File format for this preset
- **EQ Settings**: Low/Mid/High adjustments

**Updates**: Changes when preset selection changes

#### Library Health Dashboard

**Title**: 💊 LIBRARY HEALTH

**Health Score Display**
- Large number (0-100)
- Color-coded by quality:
  - Green (80-100): Excellent
  - Yellow (60-79): Good
  - Orange (40-59): Fair
  - Red (0-39): Poor

**Track Breakdown**
- 🟢 Excellent count (80-100)
- 🟡 Good count (60-79)
- 🟠 Fair count (40-59)
- 🔴 Poor count (0-39)

**Issue Statistics**
- ⚠️ Clipping: Tracks with clipping detected
- 🔇 Too Quiet: Tracks below optimal loudness
- 📉 Compressed: Over-compressed tracks

**Updates**: Refreshes when tracks added/removed/processed

#### Copyright Section
- Application branding
- Version information
- Copyright notice

---

## Basic Operations

### Adding Tracks

#### Method 1: Drag & Drop (Recommended)
1. Open Finder
2. Navigate to folder with audio files
3. Select one or more files (Cmd+Click for multiple)
4. Drag files into DeckReady center panel
5. Release mouse to add
6. Analysis begins automatically

**Tips**:
- Can drag entire folders
- Supports hundreds of files at once
- Non-audio files are ignored
- Duplicates are prevented

#### Method 2: Browse Button
1. Click "+ Add Tracks" button
2. File browser opens
3. Navigate to audio files
4. Select files (Cmd+Click for multiple, Cmd+A for all)
5. Click "Open" button
6. Files added and analyzed

**Tips**:
- Use search in file browser
- Sort by date/name/size
- Preview files before adding

#### Method 3: Folder Monitoring (Automated)
1. Set up watched folder (see Folder Monitoring section)
2. Copy/move audio files to watched folder
3. DeckReady auto-detects new files
4. Files automatically added and analyzed
5. Optionally auto-processed

**Tips**:
- Best for ongoing workflow
- Different folders for different presets
- Activity log shows all detections

### Understanding Track Analysis

When tracks are added, DeckReady analyzes them:

**Analysis Process** (2-5 seconds per track):
1. Load audio file
2. Measure integrated LUFS
3. Detect true peak level
4. Calculate dynamic range
5. Assess frequency balance
6. Compute health score
7. Identify issues
8. Determine if already optimized

**What You See**:
- Status: ⏳ ANALYZING
- Placeholder values: "..."
- Progress in status column

**After Analysis**:
- All columns populated
- Health score displayed
- Club Safe badge shown
- Status changes to READY or OPTIMIZED

### Removing Tracks

#### Remove Single Track
1. Locate track in table
2. Right-click on track row
3. Select "🗑 Remove" from menu
4. Track removed immediately
5. Health dashboard updates

**When to Remove**:
- Wrong file added
- Duplicate entry
- Don't want to process
- Already processed elsewhere

#### Clear All Tracks
1. Click "🗑 Clear All" button (below table)
2. Confirmation may appear
3. All tracks removed
4. Table cleared
5. Health dashboard resets

**When to Clear All**:
- Starting new batch
- Switching projects
- Cleaning up after processing
- Resetting workspace

### Processing Tracks

#### Before Processing Checklist
- ✅ Tracks added and analyzed
- ✅ Correct preset selected
- ✅ Output format chosen
- ✅ Output folder set
- ✅ Naming convention selected
- ✅ CPU cores configured

#### Start Processing
1. Review tracks in table
2. Verify settings in left panel
3. Click green "PROCESS TRACKS" button
4. Button changes to "⏹ CANCEL ALL"
5. Progress bar appears
6. Processing begins

**What Happens**:
- Multiple tracks process in parallel
- Status column updates per track
- Progress bar shows overall completion
- Current track name displayed
- Parallel count shown (e.g., "⚡ 4 tracks")

#### Monitor Progress
- **Progress Bar**: Overall completion percentage
- **Status Text**: Current operation details
- **Track Status**: Individual track states
- **Parallel Count**: Number of simultaneous processes

**Status Progression**:
1. 🔵 READY → ⚡ PROCESSING
2. ⚡ PROCESSING → ✓ COMPLETED (or ❌ ERROR)
3. After LUFS column updates
4. Gain column shows adjustment

#### Cancel Processing
1. Click "⏹ CANCEL ALL" button
2. Current tracks finish processing
3. Remaining tracks cancelled
4. Status shows "Cancelling..."
5. Button returns to "PROCESS TRACKS"

**Note**: Tracks already processing will complete. Only queued tracks are cancelled.

#### After Processing
- **Success**: Status shows "Complete! X/Y"
- **Files**: Saved to output folder
- **Table**: After LUFS and Gain columns updated
- **Health**: Dashboard refreshes
- **Button**: Returns to "PROCESS TRACKS"

### Changing Output Settings

#### Change Output Format
1. Click format dropdown (left panel)
2. Review options:
   - **WAV 24-bit**: Best quality, largest files
   - **WAV 16-bit**: CD quality, medium files
   - **AIFF**: Apple format, same as WAV
   - **FLAC**: Compressed, smallest files
3. Select desired format
4. Applies to all subsequent processing

**Format Comparison**:
| Format | Quality | File Size | Compatibility |
|--------|---------|-----------|---------------|
| WAV 24-bit | Highest | ~50MB | Universal |
| WAV 16-bit | CD Quality | ~25MB | Universal |
| AIFF | Highest | ~50MB | Apple/Pro |
| FLAC | Lossless | ~20MB | Modern |

#### Change Output Folder
1. Click "Browse" button (left panel)
2. Folder picker opens
3. Navigate to desired location
4. Select folder
5. Click "Choose"
6. Path updates in display field

**Common Locations**:
- Desktop: Quick access
- Music folder: Organized library
- External drive: Large batches
- Dropbox/Cloud: Backup/sync

#### Change Naming Convention
1. Click naming dropdown (left panel)
2. Review options with examples
3. Select preferred format
4. Applies to all processing

**Naming Examples** (for "Track Name.mp3"):
- Original - DJ OPT: `Track Name - DJ OPT.wav`
- DJ OPT - Original: `DJ OPT - Track Name.wav`
- Original (Optimized): `Track Name (Optimized).wav`
- Original_DJ_OPT: `Track_Name_DJ_OPT.wav`

---

## Advanced Features

### Multi-Core Processing

#### What It Does
Processes multiple tracks simultaneously using multiple CPU cores, dramatically reducing total processing time.

**Example**:
- 10 tracks, 1 core: ~5 minutes
- 10 tracks, 4 cores: ~1.5 minutes
- 10 tracks, 8 cores: ~1 minute

#### How to Use
1. Click "CPU Cores" dropdown (left panel)
2. Review options:
   - **Auto (N)**: Recommended, uses all cores minus one
   - **1 core**: Minimal impact, slowest
   - **2-4 cores**: Balanced
   - **Max cores**: Fastest, high load
3. Select desired core count
4. Setting applies immediately

#### When to Adjust

**Use Fewer Cores When**:
- Computer feels slow during processing
- Running other intensive applications
- Laptop on battery power
- Overheating concerns
- Background processing

**Use More Cores When**:
- Processing large batches (50+ tracks)
- Computer is idle
- Desktop with good cooling
- Time is critical
- Maximum performance needed

#### Performance Tips
- Auto mode is optimal for most users
- More cores = more RAM usage
- Monitor system temperature
- Close unnecessary applications
- Ensure good ventilation

### Track Health Analysis

#### What is Health Score?

A comprehensive quality metric (0-100) based on multiple audio factors.

**Calculation Factors**:
1. **Loudness** (30%): Optimal LUFS range
2. **Peak Levels** (25%): No clipping, safe peaks
3. **Dynamic Range** (20%): Preserved dynamics
4. **Frequency Balance** (15%): Even spectrum
5. **Distortion** (10%): No artifacts

#### Health Categories

**Excellent (80-100)** 🟢
- Professional quality
- Ready for any venue
- No issues detected
- Optimal loudness
- Clean peaks
- Good dynamics

**Good (60-79)** 🟡
- Acceptable quality
- Minor issues
- May need slight adjustment
- Usable as-is
- Small improvements possible

**Fair (40-59)** 🟠
- Noticeable issues
- Optimization recommended
- May have clipping
- Loudness problems
- Consider re-processing

**Poor (0-39)** 🔴
- Significant problems
- Optimization required
- Likely has clipping
- Loudness way off
- Quality concerns
- Re-process immediately

#### Health Issues Detected

**Clipping**
- Audio exceeds 0 dBFS
- Causes distortion
- Damages speakers
- Sounds harsh
- **Fix**: Process with lower target LUFS

**Near Clipping**
- Peak very close to 0 dB
- Risk of clipping
- May distort on some systems
- **Fix**: Process with -1.0 dB true peak limit

**Too Quiet**
- LUFS below -18
- Requires volume boost
- Inconsistent with other tracks
- **Fix**: Process to appropriate target LUFS

**Over Compressed**
- Dynamic range < 4 dB
- Sounds fatiguing
- Lifeless, flat
- **Fix**: Use source with more dynamics

#### Club Safe Badge

**🟢 SAFE** - Ready for Club Playback
- LUFS in range: -14 to -8
- Peak below -1.0 dB
- No clipping detected
- Good dynamic range
- **Action**: Ready to use

**🔴 FIX** - Needs Optimization
- LUFS outside optimal range
- Peak too high
- Clipping detected
- Quality issues
- **Action**: Process track

**🟢 OPTIMIZED** - Already Processed
- At target LUFS (±0.5)
- Safe peak levels
- No issues
- **Action**: No processing needed

### Auto-Optimization Detection

#### What It Does
Automatically identifies tracks that are already optimized to the target LUFS, preventing unnecessary re-processing.

#### How It Works
1. Compares track's current LUFS to target
2. Checks if within ±0.5 LUFS tolerance
3. Verifies peak levels are safe (< -1.0 dB)
4. Confirms no quality issues

#### Visual Indicators
- **After LUFS**: Shows current LUFS (not target)
- **Background**: Green color
- **Status**: "✅ OPTIMIZED"
- **Gain**: Shows "✓" checkmark
- **Club Safe**: "🟢 OPTIMIZED"

#### Benefits
- **Saves Time**: Skips unnecessary processing
- **Preserves Quality**: Avoids re-encoding
- **Prevents Over-Processing**: Maintains original dynamics
- **Smart Workflow**: Focus on tracks that need work

#### When Tracks Are Detected as Optimized
- Already processed by DeckReady
- Professionally mastered
- Correctly normalized
- At target loudness

---

## Preset Management

### Understanding Presets

A **preset** is a complete configuration defining how audio should be processed.

**Preset Components**:
- **Target LUFS**: Loudness goal (-18 to -6)
- **True Peak Limit**: Maximum level (-1.5 to -0.3 dB)
- **High-Pass Filter**: Rumble removal (20-50 Hz)
- **EQ Settings**: Low/Mid/High adjustments
- **Output Format**: File format (WAV/AIFF/FLAC)
- **Description**: Use case explanation

### Built-in Presets

DeckReady includes 4 professional presets optimized for common scenarios.

#### 🎪 Club/Festival
**Target**: -8 LUFS  
**Peak Limit**: -1.0 dB  
**Highpass**: 30 Hz  

**Characteristics**:
- Maximum loudness
- Punchy, energetic
- Cuts through noise
- Optimized for large systems

**Best For**:
- Nightclubs
- Music festivals
- Outdoor events
- Large venues
- High-energy sets

**EQ Profile**:
- Low: -1 dB (tight bass)
- Mid: 0 dB (neutral)
- High: +1 dB (presence)

#### 🍸 Bar/Lounge
**Target**: -12 LUFS  
**Peak Limit**: -1.0 dB  
**Highpass**: 30 Hz  

**Characteristics**:
- Balanced loudness
- Conversation-friendly
- Smooth, pleasant
- Not fatiguing

**Best For**:
- Bars and pubs
- Lounges
- Restaurants
- Cafes
- Background music

**EQ Profile**:
- Low: 0 dB (natural bass)
- Mid: 0 dB (neutral)
- High: 0 dB (natural)

#### 📻 Radio/Broadcast
**Target**: -16 LUFS  
**Peak Limit**: -1.0 dB  
**Highpass**: 40 Hz  

**Characteristics**:
- Broadcast-safe
- Consistent level
- Standards compliant
- Professional

**Best For**:
- Radio stations
- Podcasts
- Broadcasts
- Voice content
- Streaming shows

**EQ Profile**:
- Low: -2 dB (controlled bass)
- Mid: +1 dB (clarity)
- High: 0 dB (natural)

#### 🎵 Streaming Safe
**Target**: -14 LUFS  
**Peak Limit**: -1.0 dB  
**Highpass**: 30 Hz  

**Characteristics**:
- Platform-optimized
- Prevents normalization
- Streaming-friendly
- Quality preserved

**Best For**:
- Spotify
- Apple Music
- YouTube
- SoundCloud
- Online releases

**EQ Profile**:
- Low: 0 dB (natural)
- Mid: 0 dB (neutral)
- High: +0.5 dB (air)

### Creating Custom Presets

#### Step 1: Open Preset Manager
1. Click "Edit" button next to preset dropdown (left panel)
2. Preset Manager dialog opens
3. Shows list of all presets:
   - 🔒 Built-in (locked, cannot edit)
   - ✏️ Custom (editable)

#### Step 2: Create New Preset
1. Click "New Preset" button
2. Preset Editor dialog opens
3. Shows three sliders and preview

#### Step 3: Configure Target LUFS
**Range**: -18 to -6 LUFS  
**Recommended**: -8 to -14 LUFS  

**Slider Position Guide**:
- **-18 to -16**: Very quiet (background, ambient)
- **-16 to -14**: Quiet (streaming, broadcast)
- **-14 to -12**: Moderate (balanced, lounge)
- **-12 to -10**: Loud (bars, small clubs)
- **-10 to -8**: Very loud (clubs, festivals)
- **-8 to -6**: Maximum (extreme loudness)

**Tips**:
- Start with similar built-in preset
- Consider venue size
- Think about audience
- Test and adjust

#### Step 4: Set True Peak Limit
**Range**: -1.5 to -0.3 dB  
**Recommended**: -1.0 dB  

**Slider Position Guide**:
- **-1.5 to -1.2**: Very safe (maximum headroom)
- **-1.2 to -1.0**: Safe (recommended)
- **-1.0 to -0.8**: Moderate (less headroom)
- **-0.8 to -0.5**: Aggressive (risky)
- **-0.5 to -0.3**: Extreme (not recommended)

**Tips**:
- -1.0 dB is industry standard
- Lower = safer, more compatible
- Higher = louder, more risk
- Don't go above -0.8 dB

#### Step 5: Configure High-Pass Filter
**Range**: 20 to 50 Hz  
**Recommended**: 30 Hz  

**Slider Position Guide**:
- **20-25 Hz**: Minimal filtering (preserve deep bass)
- **25-30 Hz**: Light filtering (recommended)
- **30-35 Hz**: Moderate filtering (cleaner)
- **35-40 Hz**: Heavy filtering (broadcast)
- **40-50 Hz**: Extreme filtering (voice/podcast)

**Tips**:
- 30 Hz removes inaudible rumble
- Higher values for voice content
- Lower values for bass-heavy music
- Test on different systems

#### Step 6: Name Your Preset
1. Enter descriptive name
2. Examples:
   - "My Festival Preset"
   - "Intimate Lounge"
   - "Podcast Master"
   - "YouTube Upload"

**Naming Tips**:
- Be descriptive
- Include venue/use case
- Keep it short
- Use consistent naming

#### Step 7: Validate Settings
Preview section shows validation status:

**🟢 Green - Valid**
- All settings within safe ranges
- No conflicts detected
- Ready to save

**🟡 Yellow - Warning**
- Settings unusual but allowed
- May not be optimal
- Can still save
- Examples:
  - Very high LUFS (> -8)
  - Very low peak limit (< -1.2)
  - Extreme highpass (> 40 Hz)

**🔴 Red - Error**
- Invalid settings
- Cannot save
- Must fix before saving
- Examples:
  - LUFS out of range
  - Peak limit out of range
  - Highpass out of range

#### Step 8: Save Preset
1. Review all settings
2. Ensure validation is green or yellow
3. Click "Save Preset" button
4. Dialog closes
5. Preset appears in dropdown
6. Available immediately

### Managing Existing Presets

#### Edit Custom Preset
1. Open Preset Manager
2. Select custom preset (✏️) from list
3. Click "Edit" button
4. Preset Editor opens with current values
5. Modify settings as needed
6. Click "Save Preset"

**Note**: Built-in presets (🔒) cannot be edited. Duplicate them instead.

#### Duplicate Preset
1. Open Preset Manager
2. Select any preset (built-in or custom)
3. Click "Duplicate" button
4. Name dialog appears
5. Enter new name (e.g., "Club/Festival Copy")
6. Click OK
7. New preset created with same settings
8. Edit as needed

**Use Cases**:
- Customize built-in preset
- Create variations
- Backup before editing
- A/B testing

#### Delete Custom Preset
1. Open Preset Manager
2. Select custom preset (✏️)
3. Click "Delete" button
4. Confirmation dialog appears
5. Click "Yes" to confirm
6. Preset removed permanently

**Note**: Built-in presets (🔒) cannot be deleted.

### Preset Best Practices

#### For DJs
- Create presets for each regular venue
- Name presets after venues
- Test presets before gigs
- Keep backups of favorites

#### For Producers
- Create presets per platform
- Match streaming service targets
- Test on multiple systems
- Document your settings

#### For General Use
- Start with built-in presets
- Make small adjustments
- Test before committing
- Keep notes on what works

---

## Folder Monitoring

### What is Folder Monitoring?

Automated system that watches specified folders for new audio files and processes them according to configured presets.

**Key Features**:
- Automatic file detection
- Per-folder preset configuration
- Optional auto-processing
- Activity logging
- Delete original option

### Use Cases

**DJ Workflow**
- Drop new purchases into watch folder
- Auto-optimize for club
- Ready for next gig
- No manual processing

**Production Pipeline**
- Monitor export folder
- Auto-master for streaming
- Consistent output
- Hands-free workflow

**Batch Organization**
- Different folders for different venues
- Club folder → Club preset
- Lounge folder → Lounge preset
- Automated sorting

**Backup Processing
**Backup Processing**
- Monitor download folder
- Auto-process new purchases
- Organize automatically
- Backup workflow

### Setting Up Folder Monitoring

#### Step 1: Switch to Folder Monitoring Tab
Click "📁 Folder Monitoring" tab in center panel

#### Step 2: Add Watched Folder
1. Click "➕ Add Watched Folder" button
2. Folder picker opens
3. Navigate to folder you want to monitor
4. Select folder
5. Click "Choose"
6. Configuration dialog opens

#### Step 3: Configure Settings

**Folder Path**
- Displays selected folder path
- Read-only field (scrollable for long paths)
- Shows full absolute path

**Preset Selection**
- Choose which preset to use for this folder
- Each folder can have different preset
- Dropdown shows all available presets

**Auto-Process Checkbox**
- ✅ **Checked**: Automatically process detected files
- ☐ **Unchecked**: Only detect, don't process (manual trigger)

**Delete Original Checkbox** ⚠️
- ⚠️ **Warning**: Deletes source file after successful processing
- ☐ **Unchecked**: Keep original files (recommended)
- ✅ **Checked**: Remove originals (use with caution!)

**Output Folder**
- Leave blank: Save to same folder as source
- Or click "Browse...": Select different output location
- Useful for organizing processed files

#### Step 4: Activate Monitoring
1. Review all settings
2. Click "Add Folder" button
3. Dialog closes
4. Folder appears in list with 🟢 indicator
5. Monitoring starts immediately
6. Activity log shows activation

### Managing Watched Folders

#### Enable/Disable Monitoring
1. Select folder in list
2. Click "⏸ Disable" button
   - Status changes to 🔴
   - Monitoring stops
   - Files not detected
3. Click "▶ Enable" button
   - Status changes to 🟢
   - Monitoring resumes
   - New files detected

**Use Cases**:
- Temporarily pause monitoring
- Prevent processing during file transfers
- Control when automation runs

#### Remove Watched Folder
1. Select folder in list
2. Click "🗑 Remove" button
3. Confirmation may appear
4. Folder removed from monitoring
5. Activity log shows removal

**Note**: Removing watch folder doesn't delete files, only stops monitoring.

#### View Activity Log
- Scrollable text area at bottom
- Shows real-time events
- Timestamps for all actions
- File detection notifications
- Processing status updates
- Error messages if any

**Log Entry Types**:
- `[HH:MM:SS] Added watch folder: /path/to/folder`
- `[HH:MM:SS] Detected: filename.mp3`
- `[HH:MM:SS] ✓ Processed: filename.mp3`
- `[HH:MM:SS] ✗ Failed: filename.mp3`
- `[HH:MM:SS] Ignored processed file: filename - DJ OPT.wav`
- `[HH:MM:SS] Duplicate skipped: filename.mp3`
- `[HH:MM:SS] 🗑 Deleted original: filename.mp3`

### How Folder Monitoring Works

#### Detection Process
1. DeckReady watches folder for new files
2. Detects supported formats (MP3, WAV, FLAC, AIFF)
3. Ignores already-processed files (checks naming patterns)
4. Logs detection in Activity Log
5. Adds to track table

#### Processing Flow
1. New file detected
2. File analyzed automatically
3. Added to track table
4. If auto-process enabled:
   - Processes with configured preset
   - Saves to output folder
   - Updates Activity Log
   - Optionally deletes original
5. If auto-process disabled:
   - Waits in track table
   - Manual processing required

#### Duplicate Prevention
- Checks if file already in track list
- Skips files with processed naming patterns:
  - Contains "- DJ OPT"
  - Contains "DJ OPT -"
  - Contains "(Optimized)"
  - Contains "_DJ_OPT"
- Prevents infinite processing loops
- Logs skipped duplicates

### Folder Monitoring Best Practices

#### Safety Tips
- **Don't enable "Delete Original"** unless you have backups
- Test with small batch first
- Use separate output folder
- Monitor Activity Log regularly
- Keep originals until verified

#### Organization Tips
- Create folder structure by venue type
- Use descriptive folder names
- Separate input and output folders
- Archive processed files regularly

#### Performance Tips
- Don't monitor folders with thousands of files
- Use SSD for watched folders
- Close other file-watching apps
- Monitor system resources

---

## Waveform Analysis

### What is Waveform Analysis?

Visual representation of audio showing amplitude over time, with advanced features for quality assessment.

**Key Features**:
- Before/after comparison
- Peak level visualization
- Clipping zone detection
- dB reference markers
- Statistics display

### Opening Waveform Dialog

#### Method 1: Right-Click Menu
1. Right-click any track in table
2. Select "📊 View Waveform" from menu
3. Waveform dialog opens
4. Shows "Before" waveform
5. If processed, shows "After" waveform too

#### Method 2: After Processing
1. Process track
2. Wait for completion
3. Right-click processed track
4. Select "📊 View Waveform"
5. View before/after comparison

### Understanding the Waveform Display

#### Waveform Colors
- **Green (#00ff88)**: Normal audio signal
- **Red Overlay**: Clipping zones (audio >= 0.99)
- **Transparent Background**: Dark theme

#### dB Reference Lines
- **Red Dashed (0 dB)**: Maximum digital level
- **Yellow Dashed (-6 dB)**: Headroom reference
- **Gray Solid (center)**: Zero amplitude

#### Waveform Shape
- **Vertical Height**: Amplitude (loudness)
- **Horizontal Width**: Time (duration)
- **Peaks**: Loudest moments
- **Valleys**: Quietest moments

### Statistics Panel

Located below each waveform:

**Duration**
- Track length in MM:SS format
- Helps estimate processing time

**Peak Level**
- Maximum amplitude in dB
- Converted from linear (0.0-1.0) to dB
- Formula: 20 * log10(peak)
- Example: 0.99 = -0.09 dB

**Clipping Count**
- Number of clipping zones detected
- Zone = continuous region >= 0.99
- 0 = no clipping (good)
- >0 = clipping present (bad)

### Before/After Comparison

#### Before Waveform (Top)
- Shows original audio
- May have clipping (red zones)
- Uneven amplitude
- Natural dynamics
- Unprocessed peaks

#### After Waveform (Bottom)
- Shows processed audio
- Controlled peaks (brick-wall limiting)
- Consistent loudness
- No clipping
- Professional mastering

#### Improvement Summary
Displayed between waveforms:

**Clipping Reduction**
- Percentage decrease in clipping zones
- Example: "Clipping reduced by 100%"
- 100% = all clipping removed

**Peak Reduction**
- dB decrease in maximum level
- Example: "Peak reduced by 2.5 dB"
- Shows headroom gained

### What to Look For

#### Good Waveform Characteristics
- ✅ Consistent amplitude throughout
- ✅ No red clipping zones
- ✅ Peaks near but not at 0 dB
- ✅ Clear headroom (-1 to -3 dB)
- ✅ Smooth, controlled shape

#### Problem Waveform Characteristics
- ❌ Red clipping zones present
- ❌ Peaks touching 0 dB
- ❌ Uneven amplitude (quiet sections)
- ❌ Excessive flatness (over-compressed)
- ❌ Distorted shape

### Professional Mastering Appearance

**"Flat Top" is Normal and Correct!**

After optimization, waveforms often show a "brick-wall" or "flat top" appearance where peaks are controlled at a consistent level.

**This is NOT audio destruction** - it's professional mastering technique:

**What It Is**:
- Peak limiting (not clipping)
- Controlled loudness maximization
- Industry-standard mastering
- Used in all commercial music

**What It's NOT**:
- Clipping or distortion
- Audio damage
- Quality loss
- Over-processing

**Why It Looks Flat**:
- Limiter catches peaks
- Maintains consistent level
- Prevents clipping
- Maximizes loudness

**How to Verify Quality**:
- No red clipping zones
- Peak below 0 dB
- Sounds clean (no distortion)
- Maintains punch and energy

### Waveform Cache System

#### What is Caching?

DeckReady caches generated waveforms for fast re-display.

**Cache Location**: `temp/waveform_cache/`

**Cache Files**:
- JSON format
- Named by MD5 hash of file path
- Contains peak data and metadata

#### Cache Validation

Cache is automatically validated:
- Checks file size matches
- Checks modification time matches
- Invalidates if file changed
- Regenerates if invalid

#### Clear Cache

If waveforms display incorrectly:
1. Quit DeckReady
2. Navigate to `temp/waveform_cache/`
3. Delete all files in folder
4. Restart DeckReady
5. Waveforms regenerate on next view

---

## Optimization Tips

### For Different Venues

#### Nightclubs & Festivals
**Preset**: Club/Festival (-8 LUFS)

**Tips**:
- Maximum loudness for large systems
- Tight bass with highpass at 30 Hz
- Boost highs slightly for clarity
- Test on club monitors if possible
- Verify no clipping

**Common Issues**:
- Too quiet: Won't cut through noise
- Too loud: May distort on some systems
- Muddy bass: Increase highpass filter

#### Bars & Lounges
**Preset**: Bar/Lounge (-12 LUFS)

**Tips**:
- Balanced loudness for conversation
- Natural frequency balance
- Smooth, non-fatiguing sound
- Test at moderate volume
- Consider ambient noise

**Common Issues**:
- Too loud: Overpowering, fatiguing
- Too quiet: Gets lost in conversation
- Harsh highs: Reduce high boost

#### Radio & Broadcast
**Preset**: Radio/Broadcast (-16 LUFS)

**Tips**:
- Strict broadcast standards compliance
- Higher highpass (40 Hz) for transmission
- Consistent level crucial
- Test with broadcast equipment
- Verify true peak < -1.0 dB

**Common Issues**:
- Exceeds broadcast limits
- Inconsistent loudness
- Too much bass for transmission

#### Streaming Platforms
**Preset**: Streaming Safe (-14 LUFS)

**Tips**:
- Matches platform normalization
- Prevents volume reduction
- Quality preservation important
- Test on multiple platforms
- Check on mobile devices

**Platform Targets**:
- Spotify: -14 LUFS
- Apple Music: -16 LUFS
- YouTube: -13 to -15 LUFS
- SoundCloud: -8 to -13 LUFS

### For Different Music Genres

#### Electronic/EDM
- Use Club/Festival preset
- Tight bass (highpass 30-35 Hz)
- Maximize loudness
- Preserve transients
- Watch for over-compression

#### Hip-Hop/Rap
- Use Club/Festival or Streaming preset
- Preserve bass impact (highpass 25-30 Hz)
- Maintain vocal clarity
- Balance loudness and dynamics
- Test on subwoofer systems

#### Rock/Pop
- Use Streaming Safe or Bar/Lounge
- Natural frequency balance
- Preserve guitar/vocal clarity
- Moderate loudness
- Maintain punch

#### Jazz/Classical
- Use Bar/Lounge or lower
- Preserve wide dynamic range
- Natural sound crucial
- Lower loudness targets
- Minimal processing

### General Best Practices

#### Before Processing
- ✅ Analyze all tracks first
- ✅ Check health scores
- ✅ Identify problem tracks
- ✅ Choose appropriate preset
- ✅ Set correct output format

#### During Processing
- ✅ Monitor progress
- ✅ Check for errors
- ✅ Verify parallel processing working
- ✅ Don't interrupt mid-process
- ✅ Keep system cool

#### After Processing
- ✅ Listen to processed tracks
- ✅ Compare before/after
- ✅ Check waveforms
- ✅ Verify no clipping
- ✅ Test on target system

#### Quality Control
- ✅ A/B test with originals
- ✅ Check on multiple systems
- ✅ Verify loudness consistency
- ✅ Listen at different volumes
- ✅ Get second opinion

---

## Troubleshooting

### Application Issues

#### App Won't Launch
**Symptom**: Double-click does nothing or shows error

**Solutions**:
1. **macOS Security Block**:
   - Right-click app → "Open"
   - Click "Open" in security dialog
   - App will launch

2. **Corrupted App**:
   - Re-download from source
   - Verify download integrity
   - Re-install to Applications

3. **Permissions Issue**:
   - Check app permissions in System Preferences
   - Grant necessary access
   - Restart app

#### App Crashes on Startup
**Symptom**: App opens then immediately closes

**Solutions**:
1. **Check Console Logs**:
   - Open Console.app
   - Filter for "DeckReady"
   - Look for error messages

2. **Reset Preferences**:
   - Delete `~/Library/Preferences/com.djfuse.deckready.plist`
   - Restart app

3. **Clear Cache**:
   - Delete `temp/waveform_cache/`
   - Delete `config/settings.json`
   - Restart app

#### UI Elements Not Responding
**Symptom**: Buttons don't work, can't click things

**Solutions**:
1. **Restart App**: Quit and reopen
2. **Check System Resources**: Close other apps
3. **Update macOS**: Ensure latest version
4. **Reinstall App**: Fresh installation

### Processing Issues

#### FFmpeg Not Found
**Symptom**: "FFmpeg not found" error when processing

**Solutions**:
1. **Install FFmpeg**:
   ```bash
   brew install ffmpeg

2. **Verify Installation**:
    ```bash
    ffmpeg -version


3. **Check PATH**:

.    FFmpeg must be in system PATH

.    Restart terminal after install

.    Restart DeckReady

Processing Fails
Symptom: Tracks show ❌ ERROR status

Solutions:

    1. Check File Format:

        Ensure supported format (MP3, WAV, FLAC, AIFF)

        Try converting file

        Check file isn't corrupted

    2. Check File Permissions:

        Ensure read access to source

        Ensure write access to output folder

        Check disk space

    3. Reduce CPU Cores:

        Lower core count

        Try 1 core to isolate issue

        Check system resources

    4. Check Output Folder:

        Ensure folder exists

        Ensure write permissions

        Check disk space available

Processing Hangs
Symptom: Processing stuck, no progress

Solutions:

    Wait: Some tracks take longer

    Cancel and Retry: Click "⏹ CANCEL ALL"

    Reduce Cores: Lower parallel processing

    Check System: Monitor Activity Monitor

    Restart App: Force quit if necessary

Slow Processing
Symptom: Processing takes very long

Solutions:

    Increase CPU Cores: Use Auto mode

    Close Other Apps: Free up resources

    Check Disk Speed: Use SSD if possible

    Reduce Batch Size: Process fewer tracks

    Check File Size: Large files take longer

Audio Quality Issues
Output Sounds Distorted
Symptom: Processed audio has distortion

Solutions:

    Check Source Quality: May already be distorted

    Lower Target LUFS: Try -10 or -12 instead of -8

    Check True Peak: Ensure -1.0 dB limit

    View Waveform: Look for clipping zones

    Use Different Preset: Try less aggressive settings

Output Too Quiet
Symptom: Processed tracks quieter than expected

Solutions:

    Check Preset: Verify target LUFS

    Check Source: May be very quiet originally

    Increase Target: Use higher LUFS (e.g., -8)

    Check Output Format: Ensure not reducing bit depth

    Compare Waveforms: Verify processing applied

Output Too Loud
Symptom: Processed tracks too loud, harsh

Solutions:

    Lower Target LUFS: Try -12 or -14

    Check True Peak: May need lower limit

    Use Different Preset: Try Bar/Lounge

    Check Source: May already be loud

    Test on Different System: Verify issue

Bass Sounds Weak
Symptom: Processed tracks lack bass

Solutions:

    Lower Highpass Filter: Try 25 Hz instead of 30 Hz

    Check EQ Settings: Verify low boost/cut

    Check Source: May lack bass originally

    Create Custom Preset: Adjust bass EQ

    Test on Subwoofer: Verify bass present

Waveform Issues
Waveform Won't Display
Symptom: "Error generating waveform" message

Solutions:

    Check File Exists: Verify file not moved/deleted

    Check File Format: Ensure supported format

    Clear Cache: Delete temp/waveform_cache/

    Restart App: Fresh start

    Check Permissions: Ensure read access

Waveform Looks Wrong
Symptom: Waveform doesn't match audio

Solutions:

    Clear Cache: Delete cached waveform

    Regenerate: Close and reopen dialog

    Check File: Verify file not corrupted

    Update App: Ensure latest version

No "After" Waveform
Symptom: Only shows "Before" waveform

Solutions:

    Process Track First: Must process before comparison

    Check Output File: Verify file created

    Check File Location: Ensure in expected location

    Restart App: Refresh track data

Folder Monitoring Issues
Files Not Detected
Symptom: New files not appearing in Activity Log

Solutions:

    Check Monitoring Enabled: Verify 🟢 indicator

    Check File Format: Ensure supported format

    Check Folder Path: Verify correct folder

    Restart Monitoring: Disable and re-enable

    Check Permissions: Ensure folder access

Files Detected But Not Processing
Symptom: Files appear in log but don't process

Solutions:

    Check Auto-Process: Ensure checkbox enabled

    Check Preset: Verify valid preset selected

    Check Output Folder: Ensure write access

    Check Activity Log: Look for error messages

    Manual Process: Add to table and process manually

Duplicate Files Processed
Symptom: Same file processed multiple times

Solutions:

    Check Naming: Ensure using processed naming pattern

    Check Output Folder: Use different from source

    Enable Delete Original: Removes source after processing

    Check Activity Log: Verify duplicate detection working

FAQ
General Questions
Q: What audio formats does DeckReady support?
A: Input: MP3, WAV, FLAC, AIFF. Output: WAV (16/24-bit), AIFF, FLAC.

Q: Does DeckReady work on Windows or Linux?
A: Currently macOS only. Windows/Linux support planned for future releases.

Q: Is DeckReady free?
A: Check the project repository for current licensing and pricing information.

Q: Can I use DeckReady for commercial purposes?
A: Yes, processed tracks can be used commercially. Check license for details.

Q: Does DeckReady require internet connection?
A: No, all processing is done locally on your computer.

Technical Questions
Q: What is LUFS and why does it matter?
A: LUFS (Loudness Units Full Scale) is the international standard for measuring perceived loudness. It ensures consistent volume across tracks, unlike peak levels which don't reflect how humans hear loudness.

Q: Will processing reduce audio quality?
A: DeckReady uses professional-grade processing that preserves quality. Using WAV 24-bit output maintains maximum quality. Some re-encoding is necessary for loudness normalization, but quality loss is minimal with proper settings.

Q: What's the difference between peak limiting and clipping?
A: Peak limiting is controlled reduction of peaks using professional algorithms, preserving quality. Clipping is uncontrolled distortion when audio exceeds 0 dBFS. DeckReady uses peak limiting, not clipping.

Q: Why do my waveforms look "flat" after processing?
A: This "brick-wall" appearance is normal and correct. It indicates professional peak limiting, not clipping. This is how commercial music is mastered for maximum loudness without distortion.

Q: Can I process already-mastered tracks?
A: Yes, but DeckReady will detect if tracks are already at target loudness and skip unnecessary processing. Re-processing mastered tracks may reduce quality.

Q: How long does processing take?
A: Typically 10-30 seconds per track, depending on length and CPU cores used. Parallel processing with multiple cores significantly reduces total time for batches.

Workflow Questions
Q: What preset should I use for my venue?
A: Club/Festival (-8 LUFS) for large venues, Bar/Lounge (-12 LUFS) for intimate settings, Streaming Safe (-14 LUFS) for online platforms, Radio/Broadcast (-16 LUFS) for broadcast.

Q: Can I create my own presets?
A: Yes! Click "Edit" next to preset dropdown, then "New Preset". Adjust LUFS, true peak, and highpass filter to your needs.

Q: Should I keep original files?
A: Yes, always keep originals as backup. Only enable "Delete Original" in folder monitoring if you have backups elsewhere.

Q: Can I process tracks while DJing?
A: Yes, but reduce CPU cores to avoid system slowdown. Process tracks before gigs for best results.

Q: How do I organize processed tracks?
A: Use folder monitoring with different folders for different venues/presets. Or use naming conventions to identify processed tracks.

Troubleshooting Questions
Q: Why does processing fail with "FFmpeg not found"?
A: Install FFmpeg via Homebrew: brew install ffmpeg. Restart terminal and DeckReady after installation.

Q: Why are my processed tracks distorted?
A: Source may already be distorted, or target LUFS too high. Try lower target (-10 or -12) and verify source quality.

Q: Why doesn't folder monitoring detect my files?
A: Check monitoring is enabled (🟢), file format is supported, and folder path is correct. Check Activity Log for errors.

Q: Can I undo processing?
A: No, but original files are never modified. Processed files are saved separately. Keep originals as backup.

Q: Why is my computer slow during processing?
A: Reduce CPU cores in settings. Close other applications. Ensure good ventilation for cooling.

Appendix
Keyboard Shortcuts
Currently, DeckReady uses mouse/trackpad interaction. Keyboard shortcuts may be added in future versions.

File Locations
Application: /Applications/DeckReady.app
Config Files: ~/Library/Application Support/DeckReady/config/
Cache: ~/Library/Application Support/DeckReady/temp/waveform_cache/
Presets: ~/Library/Application Support/DeckReady/config/presets.json
Custom Presets: ~/Library/Application Support/DeckReady/config/custom_presets.json
Settings: ~/Library/Application Support/DeckReady/config/settings.json

Technical Specifications
Audio Processing:

Engine: FFmpeg with loudnorm filter

LUFS Measurement: ITU-R BS.1770-4 standard

True Peak Detection: ITU-R BS.1770-4 standard

Sample Rates: Preserves original (typically 44.1/48 kHz)

Bit Depths: 16-bit or 24-bit output

Performance:

Parallel Processing: Up to system CPU core count

Memory Usage: ~100-500MB depending on batch size

Disk Space: Minimal (cache < 10MB typically)

Compatibility:

macOS: 10.15 (Catalina) or later

Architecture: Intel and Apple Silicon (M1/M2/M3)

Dependencies: FFmpeg, Python 3.8+

Version History
Version 2.0 (Current)

Custom preset management with visual editor

Waveform visualization with before/after comparison

Folder monitoring system

Multi-core parallel processing

Library health dashboard

Modular UI architecture

Version 1.0 (Initial Release)

Basic loudness normalization

Built-in venue presets

Batch processing

Drag & drop interface

Multiple export formats

Credits
Development: DJ-FUSE
Audio Engine: FFmpeg Project
UI Framework: Qt/PySide6
LUFS Analysis: pyloudnorm
Build Tool: PyInstaller

Support & Contact
GitHub: https://github.com/ollyfuse/dj-audio-optimizer
Issues: Report bugs and request features on GitHub
Documentation: This guide and README.md
Community: Check GitHub Discussions for community support

End of User Guide

DeckReady v2.0 | © 2026 DJ-FUSE (Rwanda) | Professional DJ Audio Optimizer

Made with ❤️ for DJs worldwide


