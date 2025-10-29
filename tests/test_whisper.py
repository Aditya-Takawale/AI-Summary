import os
import sys
from pathlib import Path

# Add ffmpeg to PATH
try:
    import imageio_ffmpeg
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    ffmpeg_path = Path(ffmpeg_exe).parent
    os.environ["PATH"] = str(ffmpeg_path) + os.pathsep + os.environ.get("PATH", "")
    print(f"FFmpeg exe: {ffmpeg_exe}")
    print(f"FFmpeg path added to PATH: {ffmpeg_path}")
except Exception as e:
    print(f"Error setting up ffmpeg: {e}")

# Test whisper import
try:
    import whisper
    print(f"Whisper version: {whisper.__version__}")
    
    # Try to load a small model
    print("Loading tiny model...")
    model = whisper.load_model("tiny")
    print("Model loaded successfully!")
    
    # Try transcribing the audio file
    audio_file = r"temp_audio\test_video_1_audio.wav"
    if Path(audio_file).exists():
        print(f"\nTranscribing: {audio_file}")
        result = model.transcribe(audio_file, fp16=False)
        print(f"Transcription: {result['text'][:200]}...")
    else:
        print(f"Audio file not found: {audio_file}")
        
except Exception as e:
    import traceback
    print(f"\nError: {e}")
    traceback.print_exc()
