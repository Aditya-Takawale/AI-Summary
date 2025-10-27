"""
Subtitle/Caption generator for the AI-Powered Video Lecture Assistant.
Generates SRT subtitle files from Whisper timestamped transcriptions.
"""

import logging
from pathlib import Path
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def format_timestamp(seconds: float) -> str:
    """
    Convert seconds to SRT timestamp format (HH:MM:SS,mmm).
    
    Args:
        seconds: Time in seconds
    
    Returns:
        Formatted timestamp string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millisecs = int((seconds % 1) * 1000)
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"


def generate_srt(segments: List[Dict], output_path: str) -> str:
    """
    Generate an SRT subtitle file from timestamped segments.
    
    Args:
        segments: List of segments with 'start', 'end', and 'text' keys
        output_path: Path to save the SRT file
    
    Returns:
        Path to the created SRT file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, segment in enumerate(segments, 1):
            start_time = format_timestamp(segment['start'])
            end_time = format_timestamp(segment['end'])
            text = segment['text'].strip()
            
            # SRT format:
            # Sequence number
            # Start --> End
            # Subtitle text
            # Blank line
            f.write(f"{i}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{text}\n")
            f.write("\n")
    
    logger.info(f"SRT subtitle file created: {output_path}")
    return str(output_path)


def get_current_subtitle(segments: List[Dict], current_time: float) -> str:
    """
    Get the subtitle text for a given timestamp.
    
    Args:
        segments: List of timestamped segments
        current_time: Current playback time in seconds
    
    Returns:
        Subtitle text or empty string if no subtitle at this time
    """
    for segment in segments:
        if segment['start'] <= current_time <= segment['end']:
            return segment['text'].strip()
    return ""


if __name__ == "__main__":
    # Example usage
    sample_segments = [
        {"start": 0.0, "end": 3.5, "text": "Welcome to this video lecture."},
        {"start": 3.5, "end": 7.2, "text": "Today we'll be discussing machine learning."},
        {"start": 7.2, "end": 11.0, "text": "Machine learning is a subset of artificial intelligence."}
    ]
    
    srt_file = generate_srt(sample_segments, "outputs/sample_subtitles.srt")
    print(f"SRT file created: {srt_file}")
    
    # Test getting current subtitle
    print(f"\nSubtitle at 2.0s: '{get_current_subtitle(sample_segments, 2.0)}'")
    print(f"Subtitle at 5.0s: '{get_current_subtitle(sample_segments, 5.0)}'")
    print(f"Subtitle at 8.0s: '{get_current_subtitle(sample_segments, 8.0)}'")
