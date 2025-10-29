"""
Transcription module for the AI-Powered Video Lecture Assistant.
Uses OpenAI Whisper to transcribe audio files to text.
"""

import os
import whisper
import logging
from pathlib import Path
from .ffmpeg_utils import setup_ffmpeg

# Check for CUDA GPU support at module load time
try:
    import torch
    CUDA_AVAILABLE = torch.cuda.is_available()
    if CUDA_AVAILABLE:
        logging.info(f"✅ CUDA GPU detected: {torch.cuda.get_device_name(0)}")
    else:
        logging.info("⚠️  No CUDA GPU detected - will use CPU")
except ImportError:
    CUDA_AVAILABLE = False
    logging.warning("PyTorch not imported properly - using CPU mode")

# Set up ffmpeg
try:
    setup_ffmpeg()
except Exception as e:
    logging.warning(f"Could not set up ffmpeg: {e}")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AudioTranscriber:
    """Transcribes audio files using OpenAI Whisper."""
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize the AudioTranscriber.
        
        Args:
            model_size: Whisper model size. Options: tiny, base, small, medium, large
                       - tiny: fastest, least accurate
                       - base: good balance for most use cases
                       - small: better accuracy
                       - medium: high accuracy
                       - large: best accuracy, slowest
        """
        self.model_size = model_size
        self.model = None
        logger.info(f"Initializing Whisper with model size: {model_size}")
    
    def load_model(self):
        """Load the Whisper model."""
        if self.model is None:
            logger.info(f"Loading Whisper model '{self.model_size}'...")
            self.model = whisper.load_model(self.model_size)
            logger.info("Model loaded successfully")
    
    def transcribe(self, audio_path: str, language: str = None) -> dict:
        """
        Transcribe an audio file to text.
        
        Args:
            audio_path: Path to the audio file
            language: Language code (e.g., 'en', 'es', 'fr'). If None, auto-detect
        
        Returns:
            Dictionary containing:
                - text: Full transcription
                - language: Detected or specified language
                - segments: List of timestamped segments
        
        Raises:
            FileNotFoundError: If the audio file doesn't exist
        """
        audio_path = Path(audio_path)
        
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Load model if not already loaded
        self.load_model()
        
        logger.info(f"Transcribing audio file: {audio_path.name}")
        
        try:
            # Transcribe the audio with GPU acceleration if available
            if CUDA_AVAILABLE:
                logger.info("🚀 Using GPU acceleration (CUDA)")
            else:
                logger.info("🐌 Using CPU (no GPU detected)")
            
            options = {"fp16": CUDA_AVAILABLE}  # Enable FP16 only if CUDA GPU available
            if language:
                options["language"] = language
            
            result = self.model.transcribe(str(audio_path), **options)
            
            logger.info("Transcription completed successfully")
            
            return {
                "text": result["text"].strip(),
                "language": result.get("language", "unknown"),
                "segments": result.get("segments", [])
            }
        
        except Exception as e:
            logger.error(f"Error during transcription: {str(e)}")
            raise
    
    def transcribe_to_file(self, audio_path: str, output_path: str = None, language: str = None) -> str:
        """
        Transcribe audio and save to a text file.
        
        Args:
            audio_path: Path to the audio file
            output_path: Path to save the transcription. If None, uses audio filename
            language: Language code (e.g., 'en', 'es', 'fr'). If None, auto-detect
        
        Returns:
            Path to the transcription file
        """
        result = self.transcribe(audio_path, language)
        
        if output_path is None:
            audio_path = Path(audio_path)
            output_path = audio_path.parent / f"{audio_path.stem}_transcription.txt"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result["text"])
        
        logger.info(f"Transcription saved to: {output_path}")
        return str(output_path)
    
    def get_timestamped_transcription(self, audio_path: str, language: str = None) -> list:
        """
        Get transcription with timestamps for each segment.
        
        Args:
            audio_path: Path to the audio file
            language: Language code (e.g., 'en', 'es', 'fr'). If None, auto-detect
        
        Returns:
            List of dictionaries with 'start', 'end', and 'text' keys
        """
        result = self.transcribe(audio_path, language)
        
        timestamped = []
        for segment in result["segments"]:
            timestamped.append({
                "start": segment["start"],
                "end": segment["end"],
                "text": segment["text"].strip()
            })
        
        return timestamped


if __name__ == "__main__":
    # Example usage
    transcriber = AudioTranscriber(model_size="base")
    
    # Example: Transcribe an audio file
    # result = transcriber.transcribe("path/to/audio.wav")
    # print(result["text"])
