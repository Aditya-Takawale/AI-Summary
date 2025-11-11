"""
Cross-platform FFmpeg utilities for audio processing.
Supports Windows, macOS, and Linux with automatic FFmpeg detection.
"""

import os
import sys
import platform
from pathlib import Path
import subprocess
import shutil

def check_system_ffmpeg():
    """
    Check if ffmpeg is available in system PATH.
    Returns the path to ffmpeg if found, None otherwise.
    """
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            # Find the actual path
            ffmpeg_path = shutil.which('ffmpeg')
            return ffmpeg_path
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        pass
    return None

def setup_ffmpeg():
    """
    Set up ffmpeg for Whisper across all platforms (Windows, macOS, Linux).
    
    Strategy:
    1. Check if ffmpeg is already in system PATH
    2. Use imageio_ffmpeg as fallback
    3. Provide helpful error messages for installation
    
    Returns:
        str: Path to ffmpeg executable
    
    Raises:
        RuntimeError: If ffmpeg cannot be found or set up
    """
    system = platform.system()
    
    # First, check if ffmpeg is already available in system PATH
    system_ffmpeg = check_system_ffmpeg()
    if system_ffmpeg:
        print(f"✓ Using system FFmpeg: {system_ffmpeg}")
        return system_ffmpeg
    
    # Try imageio_ffmpeg as fallback
    try:
        import imageio_ffmpeg
        ffmpeg_exe = Path(imageio_ffmpeg.get_ffmpeg_exe())
        
        if not ffmpeg_exe.exists():
            raise FileNotFoundError(f"FFmpeg executable not found: {ffmpeg_exe}")
        
        # Add to PATH for all platforms
        ffmpeg_dir = ffmpeg_exe.parent
        os.environ["PATH"] = str(ffmpeg_dir) + os.pathsep + os.environ.get("PATH", "")
        
        # Windows-specific: ensure ffmpeg.exe exists
        if system == "Windows":
            target_name = ffmpeg_dir / "ffmpeg.exe"
            if not target_name.exists():
                try:
                    shutil.copy2(ffmpeg_exe, target_name)
                    print(f"✓ Created ffmpeg.exe in {ffmpeg_dir}")
                except Exception as e:
                    print(f"⚠ Warning: Could not create ffmpeg.exe: {e}")
        
        print(f"✓ Using imageio-ffmpeg: {ffmpeg_exe}")
        return str(ffmpeg_exe)
    
    except ImportError:
        # Provide platform-specific installation instructions
        _raise_ffmpeg_not_found(system)
    except Exception as e:
        raise RuntimeError(f"Error setting up ffmpeg: {e}")

def _raise_ffmpeg_not_found(system):
    """
    Raise a helpful error message with platform-specific installation instructions.
    """
    error_msg = "FFmpeg is not installed on your system.\n\n"
    
    if system == "Darwin":  # macOS
        error_msg += (
            "📦 Install FFmpeg on macOS:\n"
            "   Using Homebrew (recommended):\n"
            "   $ brew install ffmpeg\n\n"
            "   Using MacPorts:\n"
            "   $ sudo port install ffmpeg\n\n"
            "   Verify installation:\n"
            "   $ ffmpeg -version\n"
        )
    elif system == "Linux":
        error_msg += (
            "📦 Install FFmpeg on Linux:\n"
            "   Ubuntu/Debian:\n"
            "   $ sudo apt update && sudo apt install ffmpeg\n\n"
            "   Fedora/RHEL:\n"
            "   $ sudo dnf install ffmpeg\n\n"
            "   Arch Linux:\n"
            "   $ sudo pacman -S ffmpeg\n\n"
            "   Verify installation:\n"
            "   $ ffmpeg -version\n"
        )
    elif system == "Windows":
        error_msg += (
            "📦 Install FFmpeg on Windows:\n"
            "   Using Chocolatey (recommended):\n"
            "   > choco install ffmpeg\n\n"
            "   Using Scoop:\n"
            "   > scoop install ffmpeg\n\n"
            "   Manual installation:\n"
            "   1. Download from: https://ffmpeg.org/download.html\n"
            "   2. Extract and add to PATH\n\n"
            "   Verify installation:\n"
            "   > ffmpeg -version\n"
        )
    else:
        error_msg += (
            "📦 Install FFmpeg:\n"
            "   Visit: https://ffmpeg.org/download.html\n"
            "   Follow instructions for your platform.\n"
        )
    
    error_msg += "\n💡 Alternative: Install imageio-ffmpeg as a fallback:\n   $ pip install imageio-ffmpeg\n"
    
    raise RuntimeError(error_msg)
