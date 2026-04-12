import re
import os
import json


def clean_filename(filename):
    """
    Clean a filename by removing common unwanted phrases from YouTube
    and other download sources. Used by all processors consistently.
    """
    base_name = os.path.splitext(filename)[0]

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
        r'\(official\s+visualizer\)',
        r'\(visualizer\)',
        r'\[official\s+visualizer\]',
        r'\[visualizer\]',
        r'official\s+visualizer',
        r'\(official\s+clip\)',
        r'\[official\s+clip\]',
        r'official\s+clip',
        r'\(live\)',
        r'\(live\s+performance\)',
        r'\(acoustic\)',
        r'\(acoustic\s+version\)',
        r'\(studio\s+version\)',
        r'\(radio\s+edit\)',
        r'\(extended\s+version\)',
        r'\(remastered\)',
        r'\(remastered\s+\d{4}\)',
        r'\(remix\)',
        r'\(official\s+remix\)',
        r'\(cover\)',
        r'\(karaoke\)',
        r'\(instrumental\)',
        r'\(clean\)',
        r'\(explicit\)',
        r'\(vevo\)',
        r'\[vevo\]',
        r'\(exclusive\)',
        r'\(premiere\)',
        r'\(official\s+release\)',
        r'\(out\s+now\)',
        r'\(new\)',
        r'[\(\[]\s*(official.*?|lyrics?|hd|4k|live|acoustic|remix|visualizer|audio|video|clean|explicit|remastered.*?)\s*[\)\]]'
    ]

    cleaned = base_name
    for phrase in unwanted_phrases:
        cleaned = re.sub(phrase, '', cleaned, flags=re.IGNORECASE)

    cleaned = re.sub(r'\s+', ' ', cleaned)       # collapse multiple spaces
    cleaned = re.sub(r'\s*-\s*$', '', cleaned)   # trailing dash
    cleaned = re.sub(r'^\s*-\s*', '', cleaned)   # leading dash
    cleaned = cleaned.strip()

    return cleaned if cleaned else base_name


def get_output_filename(original_name, output_format, naming_convention):
    """
    Generate output filename using the shared cleaner and naming convention.
    Used by all processors and main_window consistently.
    """
    clean_name = clean_filename(original_name)

    ext = (
        ".aiff" if output_format == "aiff" else
        ".flac" if output_format == "flac" else
        ".wav"
    )

    if naming_convention == "Original - DJ OPT":
        return f"{clean_name} - DJ OPT{ext}"
    elif naming_convention == "DJ OPT - Original":
        return f"DJ OPT - {clean_name}{ext}"
    elif naming_convention == "Original (Optimized)":
        return f"{clean_name} (Optimized){ext}"
    elif naming_convention == "Original_DJ_OPT":
        return f"{clean_name}_DJ_OPT{ext}"
    else:
        return f"{clean_name} - DJ OPT{ext}"
    
def extract_loudnorm_json(ffmpeg_stderr):
    """
    Robustly extract the loudnorm JSON block from FFmpeg stderr output.

    Instead of using rfind which grabs the last { and } regardless of
    context, we find the specific loudnorm JSON block by locating the
    opening brace that precedes the 'input_i' key — a field that only
    exists in loudnorm output. This is safe even if FFmpeg prints other
    JSON-like content or warnings after the loudnorm block.

    Returns: parsed dict or None
    """
    # Find the line containing 'input_i' — unique to loudnorm output
    lines = ffmpeg_stderr.split('\n')
    block_start = -1

    for i, line in enumerate(lines):
        if '"input_i"' in line or 'input_i' in line:
            # Walk backwards to find the opening brace of this JSON block
            for j in range(i, -1, -1):
                if '{' in lines[j]:
                    block_start = j
                    break
            break

    if block_start == -1:
        return None

    # Reconstruct from block_start and find the matching closing brace
    block_lines = lines[block_start:]
    block_text = '\n'.join(block_lines)

    # Find balanced braces
    depth = 0
    end_pos = -1
    for idx, char in enumerate(block_text):
        if char == '{':
            depth += 1
        elif char == '}':
            depth -= 1
            if depth == 0:
                end_pos = idx + 1
                break

    if end_pos == -1:
        return None

    try:
        return json.loads(block_text[:end_pos])
    except (json.JSONDecodeError, ValueError):
        return None
