"""
Desktop Video Player with Real-time Captions
AI-Powered Video Lecture Assistant
"""

import cv2
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import threading
import time
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VideoPlayer:
    """Desktop video player with real-time caption overlay."""
    
    def __init__(self, video_path: str, segments: list = None):
        """
        Initialize the video player.
        
        Args:
            video_path: Path to the video file
            segments: List of timestamped caption segments
        """
        self.video_path = video_path
        self.segments = segments or []
        
        # Video capture
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")
        
        # Video properties
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.duration = self.total_frames / self.fps if self.fps > 0 else 0
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Playback control
        self.is_playing = False
        self.current_frame = 0
        self.play_thread = None
        
        # UI setup
        self.root = tk.Tk()
        self.root.title(f"AI Video Player - {Path(video_path).name}")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self._setup_ui()
        
        logger.info(f"Video player initialized: {Path(video_path).name}")
        logger.info(f"Duration: {self.duration:.1f}s, FPS: {self.fps:.1f}, Size: {self.width}x{self.height}")
    
    def _setup_ui(self):
        """Set up the user interface."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Video display canvas
        display_width = min(self.width, 1280)
        display_height = int(display_width * self.height / self.width)
        
        self.canvas = tk.Canvas(main_frame, width=display_width, height=display_height, bg='black')
        self.canvas.grid(row=0, column=0, columnspan=4, pady=5)
        
        # Caption display
        self.caption_label = ttk.Label(
            main_frame,
            text="",
            font=('Arial', 12, 'bold'),
            background='black',
            foreground='white',
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
        self.progress_bar.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)
        
        # Time label
        self.time_label = ttk.Label(main_frame, text="00:00 / 00:00")
        self.time_label.grid(row=2, column=0, columnspan=4, pady=2)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=4, pady=5)
        
        self.play_button = ttk.Button(button_frame, text="▶ Play", command=self.toggle_play)
        self.play_button.grid(row=0, column=0, padx=5)
        
        ttk.Button(button_frame, text="⏮ Rewind 10s", command=lambda: self.skip(-10)).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Forward 10s ⏭", command=lambda: self.skip(10)).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="⏹ Stop", command=self.stop).grid(row=0, column=3, padx=5)
        
        # Status bar
        self.status_label = ttk.Label(main_frame, text="Ready to play", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.grid(row=4, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Display first frame
        self.display_frame()
    
    def get_current_subtitle(self) -> str:
        """Get subtitle for current playback position."""
        current_time = self.current_frame / self.fps
        
        for segment in self.segments:
            if segment['start'] <= current_time <= segment['end']:
                return segment['text'].strip()
        return ""
    
    def display_frame(self):
        """Display the current frame with captions."""
        ret, frame = self.cap.read()
        
        if ret:
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Resize if needed
            display_width = self.canvas.winfo_width()
            display_height = self.canvas.winfo_height()
            
            if display_width > 1:  # Canvas is ready
                frame_rgb = cv2.resize(frame_rgb, (display_width, display_height))
            
            # Convert to PIL Image and then to ImageTk
            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=img)
            
            # Update canvas
            self.canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
            self.canvas.image = imgtk  # Keep a reference
            
            # Update caption
            subtitle = self.get_current_subtitle()
            self.caption_label.config(text=subtitle)
            
            # Update time display
            current_time = self.current_frame / self.fps
            total_time = self.duration
            time_str = f"{self._format_time(current_time)} / {self._format_time(total_time)}"
            self.time_label.config(text=time_str)
            
            # Update progress bar
            self.progress_var.set(self.current_frame)
    
    def _format_time(self, seconds: float) -> str:
        """Format seconds as MM:SS."""
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02d}:{secs:02d}"
    
    def play_video(self):
        """Play video in a separate thread."""
        while self.is_playing and self.current_frame < self.total_frames:
            start_time = time.time()
            
            # Set frame position
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
            self.display_frame()
            
            self.current_frame += 1
            
            # Calculate delay to maintain FPS
            elapsed = time.time() - start_time
            delay = max(0, (1.0 / self.fps) - elapsed)
            time.sleep(delay)
        
        if self.current_frame >= self.total_frames:
            self.is_playing = False
            self.root.after(0, lambda: self.play_button.config(text="▶ Play"))
            self.root.after(0, lambda: self.status_label.config(text="Video finished"))
    
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
            self.status_label.config(text="Playing...")
            
            # Start playback thread
            self.play_thread = threading.Thread(target=self.play_video, daemon=True)
            self.play_thread.start()
    
    def pause(self):
        """Pause playback."""
        self.is_playing = False
        self.play_button.config(text="▶ Play")
        self.status_label.config(text="Paused")
    
    def stop(self):
        """Stop playback and reset."""
        self.is_playing = False
        self.current_frame = 0
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        self.display_frame()
        self.play_button.config(text="▶ Play")
        self.status_label.config(text="Stopped")
    
    def skip(self, seconds: float):
        """Skip forward or backward."""
        frames_to_skip = int(seconds * self.fps)
        new_frame = max(0, min(self.total_frames - 1, self.current_frame + frames_to_skip))
        self.current_frame = new_frame
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
        self.display_frame()
    
    def on_progress_change(self, value):
        """Handle progress bar changes."""
        if not self.is_playing:  # Only allow manual seeking when paused
            self.current_frame = int(float(value))
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
            self.display_frame()
    
    def on_closing(self):
        """Handle window closing."""
        self.is_playing = False
        if self.play_thread and self.play_thread.is_alive():
            self.play_thread.join(timeout=1.0)
        self.cap.release()
        self.root.destroy()
    
    def run(self):
        """Start the video player."""
        self.root.mainloop()


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
        
        # Sample captions (in real use, these would come from Whisper)
        sample_captions = [
            {"start": 0.0, "end": 5.0, "text": "Welcome to this video lecture."},
            {"start": 5.0, "end": 10.0, "text": "Today we'll discuss important concepts."}
        ]
        
        try:
            player = VideoPlayer(video_path, sample_captions)
            player.run()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load video: {e}")
    else:
        print("Usage: python video_player.py <video_file>")
