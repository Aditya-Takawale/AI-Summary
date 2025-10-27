"""
AI-Powered Video Lecture Assistant - Main Application
Extracts audio, transcribes, and generates learning aids from video lectures.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from dotenv import load_dotenv
import logging

from audio_extractor import AudioExtractor
from transcriber import AudioTranscriber
from content_analyzer_ollama import OllamaContentAnalyzer
from word_generator import generate_word_document

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VideoLectureAssistant:
    """Main orchestrator for the video lecture analysis pipeline."""
    
    def __init__(self, ollama_model: str = "llama3.1", whisper_model: str = "base"):
        """
        Initialize the Video Lecture Assistant.
        
        Args:
            ollama_model: Ollama model name (e.g., 'llama3.1', 'mistral', 'llama2')
            whisper_model: Whisper model size (tiny, base, small, medium, large)
        """
        self.audio_extractor = AudioExtractor()
        self.transcriber = AudioTranscriber(model_size=whisper_model)
        self.analyzer = OllamaContentAnalyzer(model=ollama_model)
        
        # Create outputs directory
        self.outputs_dir = Path("outputs")
        self.outputs_dir.mkdir(exist_ok=True)
    
    def process_video(
        self,
        video_path: str,
        output_name: str = None,
        save_transcription: bool = True,
        cleanup_audio: bool = True,
        generate_word: bool = False
    ) -> dict:
        """
        Process a video file through the complete pipeline.
        
        Args:
            video_path: Path to the input video file
            output_name: Base name for output files (default: video filename)
            save_transcription: Whether to save the transcription to a text file
            cleanup_audio: Whether to delete the temporary audio file after processing
            generate_word: Whether to generate a Word document with the results
        
        Returns:
            Dictionary containing:
                - transcription: Full text transcription
                - language: Detected language
                - summary: Concise summary
                - insights: List of key insights
                - quiz: List of quiz questions
                - output_file: Path to the saved JSON output
                - word_file: Path to the Word document (if generated)
        """
        video_path = Path(video_path)
        
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        # Determine output name
        if output_name is None:
            output_name = video_path.stem
        
        logger.info(f"Processing video: {video_path.name}")
        logger.info("=" * 60)
        
        # Step 1: Extract audio
        logger.info("Step 1/3: Extracting audio from video...")
        audio_path = self.audio_extractor.extract_audio(str(video_path), output_format="wav")
        
        # Step 2: Transcribe audio
        logger.info("Step 2/3: Transcribing audio to text...")
        transcription_result = self.transcriber.transcribe(audio_path)
        transcription_text = transcription_result["text"]
        detected_language = transcription_result.get("language", "unknown")
        
        logger.info(f"Transcription completed: {len(transcription_text)} characters")
        logger.info(f"Detected language: {detected_language}")
        
        # Save transcription if requested
        if save_transcription:
            transcription_path = self.outputs_dir / f"{output_name}_transcription.txt"
            with open(transcription_path, 'w', encoding='utf-8') as f:
                f.write(transcription_text)
            logger.info(f"Transcription saved: {transcription_path}")
        
        # Step 3: Analyze content
        logger.info("Step 3/3: Analyzing content with AI...")
        analysis_result = self.analyzer.analyze(transcription_text)
        
        # Prepare final result
        final_result = {
            "video_file": video_path.name,
            "language": detected_language,
            "transcription": transcription_text,
            "summary": analysis_result["summary"],
            "insights": analysis_result["insights"],
            "quiz": analysis_result["quiz"]
        }
        
        # Save complete results to JSON
        output_file = self.outputs_dir / f"{output_name}_analysis.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_result, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Complete analysis saved: {output_file}")
        
        # Generate Word document if requested
        if generate_word:
            word_file = self.outputs_dir / f"{output_name}_analysis.docx"
            generate_word_document(final_result, str(word_file))
            final_result["word_file"] = str(word_file)
            logger.info(f"Word document saved: {word_file}")
        
        logger.info("=" * 60)
        logger.info("Processing completed successfully!")
        
        # Cleanup temporary audio file
        if cleanup_audio:
            self.audio_extractor.cleanup(audio_path)
        
        # Add output file path to result
        final_result["output_file"] = str(output_file)
        
        return final_result
    
    def print_summary(self, result: dict):
        """
        Print a formatted summary of the analysis results.
        
        Args:
            result: Result dictionary from process_video
        """
        print("\n" + "=" * 60)
        print("VIDEO LECTURE ANALYSIS RESULTS")
        print("=" * 60)
        
        print("\n📝 SUMMARY:")
        print("-" * 60)
        print(result["summary"])
        
        print("\n💡 KEY INSIGHTS:")
        print("-" * 60)
        for i, insight in enumerate(result["insights"], 1):
            print(f"{i}. {insight}")
        
        print("\n❓ QUIZ QUESTIONS:")
        print("-" * 60)
        for i, question in enumerate(result["quiz"], 1):
            print(f"\nQuestion {i}: {question['question']}")
            for j, option in enumerate(question['options'], 1):
                marker = "✓" if option == question['correct_answer'] else " "
                print(f"  [{marker}] {j}. {option}")
        
        print("\n" + "=" * 60)


def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description="AI-Powered Video Lecture Assistant - Generate summaries, insights, and quizzes from video lectures"
    )
    parser.add_argument(
        "video_path",
        type=str,
        help="Path to the video file to process"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Base name for output files (default: video filename)"
    )
    parser.add_argument(
        "-m", "--model",
        type=str,
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size (default: base)"
    )
    parser.add_argument(
        "--ollama-model",
        type=str,
        default="llama3.1",
        help="Ollama model name (default: llama3.1)"
    )
    parser.add_argument(
        "--no-cleanup",
        action="store_true",
        help="Keep temporary audio files after processing"
    )
    parser.add_argument(
        "--no-transcription-file",
        action="store_true",
        help="Don't save transcription to a separate text file"
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Print summary to console instead of full results"
    )
    parser.add_argument(
        "--word",
        action="store_true",
        help="Generate a Word document (.docx) with formatted results"
    )
    
    args = parser.parse_args()
    
    # No API key needed for Ollama (runs locally)
    
    try:
        # Initialize assistant
        assistant = VideoLectureAssistant(
            ollama_model=args.ollama_model,
            whisper_model=args.model
        )
        
        # Process video
        result = assistant.process_video(
            video_path=args.video_path,
            output_name=args.output,
            save_transcription=not args.no_transcription_file,
            cleanup_audio=not args.no_cleanup,
            generate_word=args.word
        )
        
        # Print results
        if args.summary_only:
            assistant.print_summary(result)
        else:
            print(f"\n✅ Analysis complete! Results saved to: {result['output_file']}")
            if 'word_file' in result:
                print(f"📄 Word document saved to: {result['word_file']}")
    
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
