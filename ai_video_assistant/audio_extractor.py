"""
Audio extraction module for the AI-Powered Video Lecture Assistant.
Extracts audio from video files using moviepy.
"""

import os
from pathlib import Path
from moviepy import VideoFileClip
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AudioExtractor:
    """Extracts audio from video files."""
    
    def __init__(self, temp_dir: str = "temp_audio"):
        """
        Initialize the AudioExtractor.
        
        Args:
            temp_dir: Directory to store temporary audio files
        """
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(exist_ok=True)
    
    def extract_audio(self, video_path: str, output_format: str = "wav") -> str:
        """
        Extract audio from a video file.
        
        Args:
            video_path: Path to the input video file
            output_format: Audio format (wav or mp3)
        
        Returns:
            Path to the extracted audio file
        
        Raises:
            FileNotFoundError: If the video file doesn't exist
            ValueError: If the output format is not supported
        """
        video_path = Path(video_path)
        
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        if output_format not in ["wav", "mp3"]:
            raise ValueError(f"Unsupported audio format: {output_format}")
        
        # Create output audio path
        audio_filename = f"{video_path.stem}_audio.{output_format}"
        audio_path = self.temp_dir / audio_filename
        
        logger.info(f"Extracting audio from {video_path.name}...")
        
        try:
            # Load video and extract audio
            video = VideoFileClip(str(video_path))
            audio = video.audio
            
            # Write audio to file
            audio.write_audiofile(
                str(audio_path),
                codec='pcm_s16le' if output_format == 'wav' else 'libmp3lame',
                logger=None  # Suppress moviepy's verbose output
            )
            
            # Close the clips to free resources
            audio.close()
            video.close()
            
            logger.info(f"Audio extracted successfully: {audio_path}")
            return str(audio_path)
        
        except Exception as e:
            logger.error(f"Error extracting audio: {str(e)}")
            raise
    
    def cleanup(self, audio_path: str = None):
        """
        Clean up temporary audio files.
        
        Args:
            audio_path: Specific audio file to delete. If None, deletes all files in temp_dir
        """
        if audio_path:
            audio_file = Path(audio_path)
            if audio_file.exists():
                audio_file.unlink()
                logger.info(f"Cleaned up: {audio_path}")
        else:
            for file in self.temp_dir.glob("*"):
                file.unlink()
            logger.info(f"Cleaned up all temporary audio files")


if __name__ == "__main__":
    # Example usage
    extractor = AudioExtractor()
    
    # Example: Extract audio from a video file
    # audio_file = extractor.extract_audio("path/to/your/video.mp4")
    # print(f"Audio extracted to: {audio_file}")
