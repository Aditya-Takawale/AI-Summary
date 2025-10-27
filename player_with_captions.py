"""
AI Video Player - Process First, Then Play with Captions
Transcribes video first, then plays it with synchronized captions and audio
"""

import cv2
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import threading
import time
from pathlib import Path
import logging
import json
import pygame

from audio_extractor import AudioExtractor
from transcriber import AudioTranscriber
from content_analyzer_ollama import OllamaContentAnalyzer
from word_generator import generate_word_document
from subtitle_generator import get_current_subtitle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProcessThenPlayPlayer:
    """Video player that processes first, then plays with captions and audio."""
    
    def __init__(self, video_path: str, whisper_model: str = "base", ollama_model: str = "llama3.1"):
        """Initialize the player."""
        self.video_path = video_path
        self.whisper_model = whisper_model
        self.ollama_model = ollama_model
        
        # Analysis components
        self.audio_extractor = AudioExtractor()
        self.transcriber = AudioTranscriber(model_size=whisper_model)
        self.analyzer = OllamaContentAnalyzer(model=ollama_model)
        
        # State
        self.segments = []
        self.analysis_result = None
        self.processing_complete = False
        self.audio_path = None
        
        # Video properties (set later)
        self.cap = None
        self.fps = 0
        self.total_frames = 0
        self.duration = 0
        
        # Playback control
        self.is_playing = False
        self.current_frame = 0
        self.start_time = 0
        
        # Output directory
        self.outputs_dir = Path("outputs")
        self.outputs_dir.mkdir(exist_ok=True)
        
        # Setup UI
        self.root = tk.Tk()
        self.root.title(f"AI Video Player - {Path(video_path).name}")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self._setup_processing_ui()
        
        # Start processing
        self.process_thread = threading.Thread(target=self._process_video, daemon=True)
        self.process_thread.start()
    
    def _setup_processing_ui(self):
        """Setup UI for processing phase."""
        frame = ttk.Frame(self.root, padding="30")
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(
            frame,
            text=f"🎬 Processing Video...",
            font=('Arial', 14, 'bold')
        )
        title.pack(pady=10)
        
        # Video name
        ttk.Label(
            frame,
            text=Path(self.video_path).name,
            font=('Arial', 10)
        ).pack(pady=5)
        
        ttk.Separator(frame, orient='horizontal').pack(fill='x', pady=15)
        
        # Status messages
        self.status_label = ttk.Label(
            frame,
            text="⏳ Extracting audio...",
            font=('Arial', 11)
        )
        self.status_label.pack(pady=10)
        
        # Progress bar
        self.progress = ttk.Progressbar(frame, length=400, mode='indeterminate')
        self.progress.pack(pady=10)
        self.progress.start(10)
        
        # Details
        self.detail_label = ttk.Label(
            frame,
            text="Please wait while we prepare your video with captions...",
            font=('Arial', 9, 'italic'),
            foreground='gray'
        )
        self.detail_label.pack(pady=10)
        
        # Info
        info_frame = ttk.LabelFrame(frame, text="Processing Steps", padding="10")
        info_frame.pack(pady=20, fill='x')
        
        self.step1 = ttk.Label(info_frame, text="⏳ 1. Extract audio from video")
        self.step1.pack(anchor='w', pady=2)
        
        self.step2 = ttk.Label(info_frame, text="⏳ 2. Transcribe audio with timestamps")
        self.step2.pack(anchor='w', pady=2)
        
        self.step3 = ttk.Label(info_frame, text="⏳ 3. Generate AI analysis (summary, insights, quiz)")
        self.step3.pack(anchor='w', pady=2)
        
        self.step4 = ttk.Label(info_frame, text="⏳ 4. Prepare video player with captions")
        self.step4.pack(anchor='w', pady=2)
    
    def _process_video(self):
        """Process video in background."""
        try:
            video_name = Path(self.video_path).stem
            
            # Step 1: Extract audio
            logger.info("Step 1: Extracting audio...")
            self.root.after(0, lambda: self.status_label.config(text="⏳ Extracting audio from video..."))
            
            self.audio_path = self.audio_extractor.extract_audio(self.video_path, output_format="wav")
            
            self.root.after(0, lambda: self.step1.config(text="✅ 1. Extract audio from video"))
            
            # Step 2: Transcribe
            logger.info("Step 2: Transcribing audio...")
            self.root.after(0, lambda: self.status_label.config(text="⏳ Transcribing audio (this may take a few minutes)..."))
            self.root.after(0, lambda: self.detail_label.config(text="Generating captions with timestamps..."))
            
            transcription_result = self.transcriber.transcribe(self.audio_path)
            self.segments = transcription_result.get('segments', [])
            
            # Format segments
            self.segments = [
                {
                    'start': seg['start'],
                    'end': seg['end'],
                    'text': seg['text'].strip()
                }
                for seg in self.segments
            ]
            
            self.root.after(0, lambda: self.step2.config(text="✅ 2. Transcribe audio with timestamps"))
            logger.info(f"Transcription complete: {len(self.segments)} segments")
            
            # Step 3: Analyze
            logger.info("Step 3: Analyzing content...")
            self.root.after(0, lambda: self.status_label.config(text="⏳ Analyzing content with AI..."))
            self.root.after(0, lambda: self.detail_label.config(text="Generating summary, insights, and quiz questions..."))
            
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
            
            json_path = self.outputs_dir / f"{video_name}_analysis.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(final_result, f, indent=2, ensure_ascii=False)
            
            word_path = self.outputs_dir / f"{video_name}_analysis.docx"
            generate_word_document(final_result, str(word_path))
            
            self.root.after(0, lambda: self.step3.config(text="✅ 3. Generate AI analysis (summary, insights, quiz)"))
            logger.info("Analysis complete")
            
            # Step 4: Prepare player
            logger.info("Step 4: Preparing video player...")
            self.root.after(0, lambda: self.status_label.config(text="⏳ Preparing video player..."))
            self.root.after(0, lambda: self.detail_label.config(text="Setting up video with captions and audio..."))
            
            # Initialize pygame mixer for audio
            pygame.mixer.init()
            
            # Open video
            self.cap = cv2.VideoCapture(self.video_path)
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.duration = self.total_frames / self.fps if self.fps > 0 else 0
            self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            self.root.after(0, lambda: self.step4.config(text="✅ 4. Prepare video player with captions"))
            
            self.processing_complete = True
            
            # Switch to player UI
            self.root.after(0, self._switch_to_player)
            
        except Exception as e:
            logger.error(f"Processing error: {e}")
            import traceback
            traceback.print_exc()
            self.root.after(0, lambda: self.status_label.config(text=f"❌ Error: {str(e)}"))
            self.root.after(0, lambda: self.progress.stop())
    
    def _switch_to_player(self):
        """Switch from processing UI to player UI."""
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Setup player UI
        self._setup_player_ui()
        
        logger.info("Ready to play!")
    
    def _setup_player_ui(self):
        """Setup the video player UI."""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Video canvas
        display_width = min(self.width, 1280)
        display_height = int(display_width * self.height / self.width)
        
        self.canvas = tk.Canvas(main_frame, width=display_width, height=display_height, bg='black')
        self.canvas.pack(pady=5)
        
        # Caption overlay
        self.caption_label = ttk.Label(
            main_frame,
            text="",
            font=('Arial', 12, 'bold'),
            background='black',
            foreground='yellow',
            wraplength=display_width - 40,
            justify='center'
        )
        self.caption_label.place(in_=self.canvas, relx=0.5, rely=0.9, anchor='center')
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Scale(
            main_frame,
            from_=0,
            to=self.total_frames,
            orient='horizontal',
            variable=self.progress_var,
            command=self.on_progress_change
        )
        self.progress_bar.pack(fill='x', pady=5)
        
        # Time label
        self.time_label = ttk.Label(main_frame, text="00:00 / 00:00")
        self.time_label.pack(pady=2)
        
        # Controls
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=5)
        
        self.play_button = ttk.Button(button_frame, text="▶ Play", command=self.toggle_play)
        self.play_button.pack(side='left', padx=5)
        
        ttk.Button(button_frame, text="⏮ -10s", command=lambda: self.skip(-10)).pack(side='left', padx=5)
        ttk.Button(button_frame, text="+10s ⏭", command=lambda: self.skip(10)).pack(side='left', padx=5)
        ttk.Button(button_frame, text="⏹ Stop", command=self.stop).pack(side='left', padx=5)
        ttk.Button(button_frame, text="📊 Results", command=self._show_results).pack(side='left', padx=5)
        
        # Status
        self.player_status = ttk.Label(main_frame, text="✅ Ready to play with captions!", relief=tk.SUNKEN, anchor=tk.W)
        self.player_status.pack(fill='x', pady=5)
        
        # Display first frame
        self.display_frame()
    
    def get_current_subtitle(self) -> str:
        """Get subtitle for current position."""
        current_time = self.current_frame / self.fps
        return get_current_subtitle(self.segments, current_time)
    
    def display_frame(self):
        """Display current frame with caption."""
        ret, frame = self.cap.read()
        
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            display_width = self.canvas.winfo_width()
            display_height = self.canvas.winfo_height()
            
            if display_width > 1:
                frame_rgb = cv2.resize(frame_rgb, (display_width, display_height))
            
            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            
            self.canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
            self.canvas.image = imgtk
            
            # Update caption
            subtitle = self.get_current_subtitle()
            self.caption_label.config(text=subtitle)
            
            # Update time
            current_time = self.current_frame / self.fps
            time_str = f"{self._format_time(current_time)} / {self._format_time(self.duration)}"
            self.time_label.config(text=time_str)
            
            self.progress_var.set(self.current_frame)
    
    def _format_time(self, seconds: float) -> str:
        """Format time as MM:SS."""
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02d}:{secs:02d}"
    
    def play_video(self):
        """Play video with audio."""
        # Load and play audio
        try:
            pygame.mixer.music.load(self.audio_path)
            pygame.mixer.music.play(start=self.current_frame / self.fps)
            self.start_time = time.time() - (self.current_frame / self.fps)
        except:
            logger.warning("Audio playback failed, continuing without audio")
        
        while self.is_playing and self.current_frame < self.total_frames:
            # Sync with audio time
            if pygame.mixer.music.get_busy():
                current_time = pygame.mixer.music.get_pos() / 1000.0 + (self.current_frame / self.fps - time.time() + self.start_time)
                self.current_frame = int(current_time * self.fps)
            
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
            self.display_frame()
            
            self.current_frame += 1
            time.sleep(1.0 / self.fps)
        
        if self.current_frame >= self.total_frames:
            self.is_playing = False
            pygame.mixer.music.stop()
            self.root.after(0, lambda: self.play_button.config(text="▶ Play"))
    
    def toggle_play(self):
        """Toggle play/pause."""
        if self.is_playing:
            self.pause()
        else:
            self.play()
    
    def play(self):
        """Start playback."""
        if not self.is_playing:
            self.is_playing = True
            self.play_button.config(text="⏸ Pause")
            self.player_status.config(text="Playing with captions...")
            threading.Thread(target=self.play_video, daemon=True).start()
    
    def pause(self):
        """Pause playback."""
        self.is_playing = False
        pygame.mixer.music.pause()
        self.play_button.config(text="▶ Play")
        self.player_status.config(text="Paused")
    
    def stop(self):
        """Stop playback."""
        self.is_playing = False
        pygame.mixer.music.stop()
        self.current_frame = 0
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        self.display_frame()
        self.play_button.config(text="▶ Play")
    
    def skip(self, seconds: float):
        """Skip forward/backward."""
        frames_to_skip = int(seconds * self.fps)
        self.current_frame = max(0, min(self.total_frames - 1, self.current_frame + frames_to_skip))
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
        
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.set_pos(self.current_frame / self.fps)
        
        self.display_frame()
    
    def on_progress_change(self, value):
        """Handle progress bar change."""
        if not self.is_playing:
            self.current_frame = int(float(value))
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
            self.display_frame()
    
    def _show_results(self):
        """Show analysis results."""
        if not self.analysis_result:
            return
        
        # Pause if playing
        if self.is_playing:
            self.pause()
        
        # Create results window
        results_window = tk.Toplevel(self.root)
        results_window.title("AI Analysis Results")
        results_window.geometry("800x600")
        
        main_frame = ttk.Frame(results_window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(main_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget = tk.Text(main_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set, font=('Consolas', 10))
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
    
    def on_closing(self):
        """Handle window close."""
        self.is_playing = False
        if self.cap:
            self.cap.release()
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        self.root.destroy()
    
    def run(self):
        """Run the application."""
        self.root.mainloop()


def main():
    """Main entry point."""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Video Player - Process First, Play with Captions")
    parser.add_argument("video_path", type=str, help="Path to video file")
    parser.add_argument("-m", "--whisper-model", type=str, default="base",
                        choices=["tiny", "base", "small", "medium", "large"])
    parser.add_argument("--ollama-model", type=str, default="llama3.1")
    
    args = parser.parse_args()
    
    try:
        player = ProcessThenPlayPlayer(
            video_path=args.video_path,
            whisper_model=args.whisper_model,
            ollama_model=args.ollama_model
        )
        player.run()
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
