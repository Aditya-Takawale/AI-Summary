"""
AI-Powered Video Player with Background Analysis
Plays video with captions while analyzing content in the background
"""

import threading
import time
import json
from pathlib import Path
import logging
import tkinter as tk
from tkinter import ttk
import subprocess
import os

from video_player import VideoPlayer
from audio_extractor import AudioExtractor
from transcriber import AudioTranscriber
from content_analyzer_ollama import OllamaContentAnalyzer
from word_generator import generate_word_document

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIVideoPlayer(VideoPlayer):
    """Enhanced video player with AI analysis in background."""
    
    def __init__(self, video_path: str, whisper_model: str = "base", ollama_model: str = "llama3.1"):
        """
        Initialize AI video player.
        
        Args:
            video_path: Path to video file
            whisper_model: Whisper model size
            ollama_model: Ollama model name
        """
        self.video_path = video_path
        self.whisper_model = whisper_model
        self.ollama_model = ollama_model
        
        # Analysis components
        self.audio_extractor = AudioExtractor()
        self.transcriber = AudioTranscriber(model_size=whisper_model)
        self.analyzer = OllamaContentAnalyzer(model=ollama_model)
        
        # Analysis state
        self.transcription_complete = False
        self.analysis_complete = False
        self.transcription_result = None
        self.analysis_result = None
        self.segments = []
        
        # Output directory
        self.outputs_dir = Path("outputs")
        self.outputs_dir.mkdir(exist_ok=True)
        
        # Start background analysis
        self.analysis_thread = threading.Thread(target=self._background_analysis, daemon=True)
        self.analysis_thread.start()
        
        # Initialize video player (will use segments once ready)
        super().__init__(video_path, segments=[])
        
        # Add analysis status to UI
        self._add_analysis_status()
    
    def _add_analysis_status(self):
        """Add analysis status panel to UI."""
        # Analysis frame
        analysis_frame = ttk.LabelFrame(self.root, text="AI Analysis Status", padding="10")
        analysis_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=10, pady=5)
        
        # Transcription status
        self.transcription_status = ttk.Label(analysis_frame, text="⏳ Transcribing audio...")
        self.transcription_status.grid(row=0, column=0, sticky=tk.W, pady=2)
        
        # Analysis status
        self.analysis_status = ttk.Label(analysis_frame, text="⏳ Waiting for transcription...")
        self.analysis_status.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        # Results button (initially disabled)
        self.results_button = ttk.Button(
            analysis_frame,
            text="📊 View Results",
            command=self._show_results,
            state=tk.DISABLED
        )
        self.results_button.grid(row=2, column=0, pady=5)
        
        # Play with audio button
        self.audio_button = ttk.Button(
            analysis_frame,
            text="🔊 Play Video with Audio",
            command=self._play_with_audio
        )
        self.audio_button.grid(row=3, column=0, pady=5)
    
    def _play_with_audio(self):
        """Open video in default player for audio playback."""
        try:
            os.startfile(self.video_path)
            logger.info(f"Opened video in default player: {self.video_path}")
        except Exception as e:
            logger.error(f"Failed to open video: {e}")
            try:
                # Try with VLC if available
                subprocess.Popen(['vlc', self.video_path])
            except:
                # Fallback to system default
                if os.name == 'nt':  # Windows
                    os.system(f'start "" "{self.video_path}"')
                else:
                    os.system(f'xdg-open "{self.video_path}"')
    
    def _background_analysis(self):
        """Perform transcription and analysis in background."""
        try:
            video_name = Path(self.video_path).stem
            
            # Step 1: Extract audio
            logger.info("Background: Extracting audio...")
            audio_path = self.audio_extractor.extract_audio(self.video_path, output_format="wav")
            
            # Step 2: Transcribe with timestamps
            logger.info("Background: Transcribing audio...")
            self.root.after(0, lambda: self.transcription_status.config(text="⏳ Transcribing audio..."))
            
            transcription_result = self.transcriber.transcribe(audio_path)
            self.transcription_result = transcription_result
            
            # Get timestamped segments for captions
            self.segments = transcription_result.get('segments', [])
            formatted_segments = [
                {
                    'start': seg['start'],
                    'end': seg['end'],
                    'text': seg['text'].strip()
                }
                for seg in self.segments
            ]
            
            # Update player with segments
            self.segments = formatted_segments
            
            self.transcription_complete = True
            self.root.after(0, lambda: self.transcription_status.config(text="✅ Transcription complete!"))
            logger.info(f"Background: Transcription complete ({len(transcription_result['text'])} characters)")
            
            # Step 3: Analyze content
            logger.info("Background: Analyzing content with AI...")
            self.root.after(0, lambda: self.analysis_status.config(text="⏳ Analyzing content..."))
            
            self.analysis_result = self.analyzer.analyze(transcription_result['text'])
            
            # Step 4: Save results
            final_result = {
                "video_file": Path(self.video_path).name,
                "language": transcription_result.get("language", "unknown"),
                "transcription": transcription_result['text'],
                "summary": self.analysis_result["summary"],
                "insights": self.analysis_result["insights"],
                "quiz": self.analysis_result["quiz"]
            }
            
            # Save JSON
            json_path = self.outputs_dir / f"{video_name}_analysis.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(final_result, f, indent=2, ensure_ascii=False)
            
            # Generate Word document
            word_path = self.outputs_dir / f"{video_name}_analysis.docx"
            generate_word_document(final_result, str(word_path))
            
            self.analysis_complete = True
            self.root.after(0, lambda: self.analysis_status.config(text="✅ Analysis complete! Click to view results"))
            self.root.after(0, lambda: self.results_button.config(state=tk.NORMAL))
            
            logger.info(f"Background: Analysis complete! Results saved to {json_path}")
            
            # Cleanup audio file
            self.audio_extractor.cleanup(audio_path)
            
        except Exception as e:
            logger.error(f"Background analysis error: {e}")
            self.root.after(0, lambda: self.analysis_status.config(text=f"❌ Error: {str(e)}"))
    
    def _show_results(self):
        """Show analysis results in a new window."""
        if not self.analysis_complete or not self.analysis_result:
            return
        
        # Create results window
        results_window = tk.Toplevel(self.root)
        results_window.title("AI Analysis Results")
        results_window.geometry("800x600")
        
        # Main frame with scrollbar
        main_frame = ttk.Frame(results_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Text widget
        text_widget = tk.Text(
            main_frame,
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            font=('Consolas', 10),
            padx=10,
            pady=10
        )
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_widget.yview)
        
        # Format and display results
        text_widget.insert(tk.END, "=" * 60 + "\n")
        text_widget.insert(tk.END, "VIDEO LECTURE ANALYSIS RESULTS\n")
        text_widget.insert(tk.END, "=" * 60 + "\n\n")
        
        text_widget.insert(tk.END, "📝 SUMMARY:\n")
        text_widget.insert(tk.END, "-" * 60 + "\n")
        text_widget.insert(tk.END, self.analysis_result['summary'] + "\n\n")
        
        text_widget.insert(tk.END, "💡 KEY INSIGHTS:\n")
        text_widget.insert(tk.END, "-" * 60 + "\n")
        for i, insight in enumerate(self.analysis_result['insights'], 1):
            text_widget.insert(tk.END, f"{i}. {insight}\n")
        text_widget.insert(tk.END, "\n")
        
        text_widget.insert(tk.END, "❓ QUIZ QUESTIONS:\n")
        text_widget.insert(tk.END, "-" * 60 + "\n")
        for i, q in enumerate(self.analysis_result['quiz'], 1):
            text_widget.insert(tk.END, f"\nQuestion {i}: {q['question']}\n")
            for j, option in enumerate(q['options'], 1):
                marker = "[✓]" if option == q['correct_answer'] else "[ ]"
                text_widget.insert(tk.END, f"  {marker} {j}. {option}\n")
        
        text_widget.insert(tk.END, "\n" + "=" * 60 + "\n")
        
        # Make text read-only
        text_widget.config(state=tk.DISABLED)
        
        # Close button
        ttk.Button(results_window, text="Close", command=results_window.destroy).pack(pady=10)


def main():
    """Main entry point for AI video player."""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="AI-Powered Video Player with Real-time Captions")
    parser.add_argument("video_path", type=str, help="Path to video file")
    parser.add_argument("-m", "--whisper-model", type=str, default="base",
                        choices=["tiny", "base", "small", "medium", "large"],
                        help="Whisper model size (default: base)")
    parser.add_argument("--ollama-model", type=str, default="llama3.1",
                        help="Ollama model name (default: llama3.1)")
    
    args = parser.parse_args()
    
    try:
        logger.info(f"Starting AI Video Player...")
        logger.info(f"Video: {args.video_path}")
        logger.info(f"Whisper model: {args.whisper_model}")
        logger.info(f"Ollama model: {args.ollama_model}")
        
        player = AIVideoPlayer(
            video_path=args.video_path,
            whisper_model=args.whisper_model,
            ollama_model=args.ollama_model
        )
        player.run()
        
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
