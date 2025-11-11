"""
Core API for AI Video Assistant
Simple, clean interface for developers
"""

from pathlib import Path
from typing import Dict, Optional
import subprocess

# Use relative imports for package modules
from .audio_extractor import AudioExtractor
from .transcriber import AudioTranscriber
from .analyzer import OllamaContentAnalyzer
from .word_generator import generate_word_document
from .subtitle_generator import generate_srt


class VideoAssistant:
    """
    Main API class for video processing.
    
    Example:
        assistant = VideoAssistant()
        result = assistant.process_video("lecture.mp4")
        print(result['summary'])
    """
    
    def __init__(
        self,
        whisper_model: str = "base",
        ollama_model: str = "llama3.1",
        output_dir: str = "outputs",
        ollama_timeout: int = 600
    ):
        """
        Initialize the video assistant.
        
        Args:
            whisper_model: Whisper model size (tiny/base/small/medium/large)
            ollama_model: Ollama model name (default: llama3.1)
            output_dir: Directory for output files
            ollama_timeout: Timeout for Ollama requests in seconds (default: 600 = 10 min)
        """
        self.whisper_model = whisper_model
        self.ollama_model = ollama_model
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize components
        self.audio_extractor = AudioExtractor()
        self.transcriber = AudioTranscriber(model_size=whisper_model)
        self.analyzer = OllamaContentAnalyzer(model=ollama_model, timeout=ollama_timeout)
    
    def process_video(
        self,
        video_path: str,
        generate_subtitles: bool = True,
        generate_word_doc: bool = True,
        embed_subtitles: bool = False
    ) -> Dict:
        """
        Process a video and generate all learning aids.
        
        Args:
            video_path: Path to video file
            generate_subtitles: Whether to generate SRT file
            generate_word_doc: Whether to generate Word document
            embed_subtitles: Whether to embed subtitles into video
        
        Returns:
            Dictionary with all results:
            {
                'transcription': str,
                'language': str,
                'summary': str,
                'insights': list,
                'quiz': list,
                'srt_path': str (if generate_subtitles),
                'docx_path': str (if generate_word_doc),
                'video_with_subtitles': str (if embed_subtitles)
            }
        """
        video_path = Path(video_path)
        video_name = video_path.stem
        
        # Step 1: Extract audio
        audio_path = self.audio_extractor.extract_audio(str(video_path))
        
        # Step 2: Transcribe
        transcription_result = self.transcriber.transcribe(audio_path)
        
        # Step 3: Analyze with AI
        analysis = self.analyzer.analyze(transcription_result['text'])
        
        # Build result
        result = {
            'video_file': video_path.name,
            'transcription': transcription_result['text'],
            'language': transcription_result.get('language', 'unknown'),
            'segments': transcription_result.get('segments', []),
            'summary': analysis['summary'],
            'insights': analysis['insights'],
            'quiz': analysis['quiz']
        }
        
        # Step 4: Generate SRT subtitles (optional)
        if generate_subtitles:
            srt_path = self.output_dir / f"{video_name}_subtitles.srt"
            generate_srt(transcription_result['segments'], str(srt_path))
            result['srt_path'] = str(srt_path)
        
        # Step 5: Generate Word document (optional)
        if generate_word_doc:
            docx_path = self.output_dir / f"{video_name}_analysis.docx"
            generate_word_document(result, str(docx_path))
            result['docx_path'] = str(docx_path)
        
        # Step 6: Embed subtitles in video (optional)
        if embed_subtitles and generate_subtitles:
            output_video = self.output_dir / f"{video_name}_with_subtitles.mp4"
            self._embed_subtitles(str(video_path), result['srt_path'], str(output_video))
            result['video_with_subtitles'] = str(output_video)
        
        return result
    
    def transcribe_only(self, video_path: str) -> Dict:
        """
        Only transcribe video (no AI analysis).
        
        Returns:
            {
                'text': str,
                'language': str,
                'segments': list
            }
        """
        audio_path = self.audio_extractor.extract_audio(video_path)
        return self.transcriber.transcribe(audio_path)
    
    def analyze_text(self, text: str) -> Dict:
        """
        Analyze pre-existing text (no video processing).
        
        Returns:
            {
                'summary': str,
                'insights': list,
                'quiz': list
            }
        """
        return self.analyzer.analyze(text)
    
    def generate_subtitles_from_video(self, video_path: str, output_path: str = None) -> str:
        """
        Generate SRT subtitle file from video.
        
        Returns:
            Path to SRT file
        """
        audio_path = self.audio_extractor.extract_audio(video_path)
        transcription = self.transcriber.transcribe(audio_path)
        
        if not output_path:
            video_name = Path(video_path).stem
            output_path = self.output_dir / f"{video_name}_subtitles.srt"
        
        generate_srt(transcription['segments'], str(output_path))
        return str(output_path)
    
    def _embed_subtitles(self, video_path: str, srt_path: str, output_path: str):
        """Embed SRT subtitles into video using FFmpeg."""
        try:
            import imageio_ffmpeg
            ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        except:
            ffmpeg_exe = 'ffmpeg'
        
        cmd = [
            ffmpeg_exe,
            '-i', video_path,
            '-i', srt_path,
            '-c:v', 'copy',
            '-c:a', 'copy',
            '-c:s', 'mov_text',
            '-metadata:s:s:0', 'language=eng',
            '-y',
            output_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)


# Convenience functions for quick usage

def process_video(video_path: str, **kwargs) -> Dict:
    """
    Quick function to process a video with default settings.
    
    Example:
        result = process_video("lecture.mp4")
    """
    assistant = VideoAssistant()
    return assistant.process_video(video_path, **kwargs)


def transcribe_video(video_path: str) -> Dict:
    """
    Quick function to transcribe a video.
    
    Example:
        result = transcribe_video("lecture.mp4")
        print(result['text'])
    """
    assistant = VideoAssistant()
    return assistant.transcribe_only(video_path)


def analyze_lecture(text: str) -> Dict:
    """
    Quick function to analyze text.
    
    Example:
        result = analyze_lecture("Long lecture text here...")
        print(result['summary'])
    """
    assistant = VideoAssistant()
    return assistant.analyze_text(text)
