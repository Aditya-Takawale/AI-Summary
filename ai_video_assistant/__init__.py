"""
AI Video Assistant - Python SDK
Easy-to-use API for integrating video transcription and analysis into any application

Author: Aditya Takawale
GitHub: https://github.com/Aditya-Takawale/AI-Summary
License: MIT
"""

from .core import VideoAssistant
from .transcriber import AudioTranscriber
from .analyzer import OllamaContentAnalyzer
from .subtitle_generator import generate_srt

__version__ = "1.0.0"
__author__ = "Aditya Takawale"
__license__ = "MIT"
__all__ = ["VideoAssistant", "AudioTranscriber", "OllamaContentAnalyzer", "generate_srt"]


# Example usage for developers:
"""
from ai_video_assistant import VideoAssistant

# Initialize
assistant = VideoAssistant()

# Process video
result = assistant.process_video("lecture.mp4")

# Access results
print(result['transcription'])
print(result['summary'])
print(result['quiz'])

# Get subtitled video
video_path = result['video_with_subtitles']
"""
