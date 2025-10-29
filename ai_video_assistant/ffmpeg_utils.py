"""
Audio loading utilities with ffmpeg configuration for Windows.
"""

import os
import sys
from pathlib import Path
import subprocess
import shutil

def setup_ffmpeg():
    """
    Set up ffmpeg for Whisper on Windows by creating a temporary wrapper.
    """
    try:
        import imageio_ffmpeg
        ffmpeg_exe = Path(imageio_ffmpeg.get_ffmpeg_exe())
        
        if not ffmpeg_exe.exists():
            raise FileNotFoundError(f"FFmpeg executable not found: {ffmpeg_exe}")
        
        # Add to PATH
        ffmpeg_dir = ffmpeg_exe.parent
        os.environ["PATH"] = str(ffmpeg_dir) + os.pathsep + os.environ.get("PATH", "")
        
        # For Windows, create a copy/link named 'ffmpeg.exe'
        target_name = ffmpeg_dir / "ffmpeg.exe"
        if not target_name.exists():
            try:
                # Try to create a hard link first
                shutil.copy2(ffmpeg_exe, target_name)
                print(f"Created ffmpeg.exe in {ffmpeg_dir}")
            except Exception as e:
                print(f"Warning: Could not create ffmpeg.exe: {e}")
        
        return str(ffmpeg_exe)
    
    except ImportError:
        raise RuntimeError("imageio_ffmpeg is required but not installed")
    except Exception as e:
        raise RuntimeError(f"Error setting up ffmpeg: {e}")
