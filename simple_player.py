"""
Simple AI Video Analyzer with Caption Window
Opens video in default player + shows synchronized captions + analyzes in background
"""

import threading
import time
import json
from pathlib import Path
import logging
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os

from audio_extractor import AudioExtractor
from transcriber import AudioTranscriber
from content_analyzer_ollama import OllamaContentAnalyzer
from word_generator import generate_word_document
from subtitle_generator import generate_srt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CaptionOverlay:
    """Floating caption window with background analysis."""
    
    def __init__(self, video_path: str, whisper_model: str = "base", ollama_model: str = "llama3.1"):
        """Initialize caption overlay."""
        self.video_path = video_path
        self.whisper_model = whisper_model
        self.ollama_model = ollama_model
        
        # Analysis components
        self.audio_extractor = AudioExtractor()
        self.transcriber = AudioTranscriber(model_size=whisper_model)
        self.analyzer = OllamaContentAnalyzer(model=ollama_model)
        
        # Analysis state
        self.segments = []
        self.analysis_result = None
        self.transcription_complete = False
        self.analysis_complete = False
        
        # Output directory
        self.outputs_dir = Path("outputs")
        self.outputs_dir.mkdir(exist_ok=True)
        
        # Start background analysis
        self.analysis_thread = threading.Thread(target=self._background_analysis, daemon=True)
        self.analysis_thread.start()
        
        # Setup UI
        self.root = tk.Tk()
        self.root.title(f"AI Analysis - {Path(video_path).name}")
        self.root.geometry("600x300")
        self.root.attributes('-topmost', True)  # Keep on top
        
        self._setup_ui()
        
        # Open video in default player
        self._open_video()
    
    def _setup_ui(self):
        """Setup the user interface."""
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text=f"🎬 {Path(self.video_path).name}",
            font=('Arial', 12, 'bold')
        )
        title_label.pack(pady=5)
        
        # Separator
        ttk.Separator(main_frame, orient='horizontal').pack(fill='x', pady=5)
        
        # Analysis status frame
        status_frame = ttk.LabelFrame(main_frame, text="AI Analysis Progress", padding="10")
        status_frame.pack(fill='x', pady=10)
        
        self.transcription_status = ttk.Label(status_frame, text="⏳ Transcribing audio...")
        self.transcription_status.pack(anchor='w', pady=2)
        
        self.analysis_status = ttk.Label(status_frame, text="⏳ Waiting for transcription...")
        self.analysis_status.pack(anchor='w', pady=2)
        
        # Progress bar
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress.pack(fill='x', pady=5)
        self.progress.start(10)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=10)
        
        self.results_button = ttk.Button(
            button_frame,
            text="📊 View Analysis Results",
            command=self._show_results,
            state=tk.DISABLED
        )
        self.results_button.pack(side='left', padx=5)
        
        self.srt_button = ttk.Button(
            button_frame,
            text="💾 Export Subtitles (.srt)",
            command=self._export_srt,
            state=tk.DISABLED
        )
        self.srt_button.pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="🔊 Reopen Video", command=self._open_video).pack(side='left', padx=5)
        
        # Info label
        info_label = ttk.Label(
            main_frame,
            text="Video is playing in your default player.\nAnalysis will complete in the background.",
            font=('Arial', 9, 'italic'),
            foreground='gray'
        )
        info_label.pack(pady=5)
    
    def _open_video(self):
        """Open video in default player."""
        try:
            if os.name == 'nt':  # Windows
                os.startfile(self.video_path)
            else:
                subprocess.Popen(['xdg-open', self.video_path])
            logger.info(f"Opened video in default player")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open video: {e}")
    
    def _background_analysis(self):
        """Perform analysis in background."""
        try:
            video_name = Path(self.video_path).stem
            
            # Extract audio
            logger.info("Extracting audio...")
            audio_path = self.audio_extractor.extract_audio(self.video_path, output_format="wav")
            
            # Transcribe
            logger.info("Transcribing audio...")
            self.root.after(0, lambda: self.transcription_status.config(text="⏳ Transcribing audio... (this may take a few minutes)"))
            
            transcription_result = self.transcriber.transcribe(audio_path)
            self.segments = transcription_result.get('segments', [])
            
            self.transcription_complete = True
            self.root.after(0, lambda: self.transcription_status.config(text="✅ Transcription complete!"))
            self.root.after(0, lambda: self.srt_button.config(state=tk.NORMAL))
            logger.info("Transcription complete")
            
            # Analyze
            logger.info("Analyzing content...")
            self.root.after(0, lambda: self.analysis_status.config(text="⏳ Analyzing content with AI..."))
            
            self.analysis_result = self.analyzer.analyze(transcription_result['text'])
            
            # Save results
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
            self.root.after(0, lambda: self.progress.stop())
            self.root.after(0, lambda: self.analysis_status.config(text=f"✅ Analysis complete! Saved to: {word_path.name}"))
            self.root.after(0, lambda: self.results_button.config(state=tk.NORMAL))
            
            logger.info(f"Analysis complete! Results saved.")
            
            # Cleanup
            self.audio_extractor.cleanup(audio_path)
            
        except Exception as e:
            logger.error(f"Error: {e}")
            self.root.after(0, lambda: self.analysis_status.config(text=f"❌ Error: {str(e)}"))
            self.root.after(0, lambda: self.progress.stop())
    
    def _export_srt(self):
        """Export subtitles to SRT file."""
        if not self.segments:
            messagebox.showwarning("Not Ready", "Transcription not complete yet!")
            return
        
        video_name = Path(self.video_path).stem
        srt_path = self.outputs_dir / f"{video_name}_subtitles.srt"
        
        generate_srt(self.segments, str(srt_path))
        
        messagebox.showinfo(
            "Subtitles Exported",
            f"Subtitles saved to:\n{srt_path}\n\nYou can load this file in VLC or other players!"
        )
    
    def _show_results(self):
        """Show analysis results."""
        if not self.analysis_complete:
            messagebox.showwarning("Not Ready", "Analysis not complete yet!")
            return
        
        # Create results window
        results_window = tk.Toplevel(self.root)
        results_window.title("AI Analysis Results")
        results_window.geometry("800x600")
        
        # Scrollable text
        main_frame = ttk.Frame(results_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(main_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
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
        
        # Display results
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
        
        text_widget.config(state=tk.DISABLED)
        
        ttk.Button(results_window, text="Close", command=results_window.destroy).pack(pady=10)
    
    def run(self):
        """Run the application."""
        self.root.mainloop()


def main():
    """Main entry point."""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Video Analyzer with Audio Support")
    parser.add_argument("video_path", type=str, help="Path to video file")
    parser.add_argument("-m", "--whisper-model", type=str, default="base",
                        choices=["tiny", "base", "small", "medium", "large"],
                        help="Whisper model size (default: base)")
    parser.add_argument("--ollama-model", type=str, default="llama3.1",
                        help="Ollama model name (default: llama3.1)")
    
    args = parser.parse_args()
    
    try:
        app = CaptionOverlay(
            video_path=args.video_path,
            whisper_model=args.whisper_model,
            ollama_model=args.ollama_model
        )
        app.run()
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
