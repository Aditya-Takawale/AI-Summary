"""
Test script to verify cross-platform FFmpeg detection.
Run this to ensure FFmpeg is properly configured on your system.
"""

import sys
import platform
from ai_video_assistant.ffmpeg_utils import setup_ffmpeg, check_system_ffmpeg

def test_ffmpeg():
    """Test FFmpeg detection and setup."""
    print("=" * 60)
    print("🔍 FFmpeg Detection Test")
    print("=" * 60)
    print(f"\n📍 Platform: {platform.system()} {platform.release()}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    print()
    
    # Test system FFmpeg
    print("1️⃣ Checking for system FFmpeg...")
    system_ffmpeg = check_system_ffmpeg()
    if system_ffmpeg:
        print(f"   ✅ Found system FFmpeg: {system_ffmpeg}")
    else:
        print("   ⚠️  System FFmpeg not found in PATH")
    
    print()
    
    # Test FFmpeg setup
    print("2️⃣ Running setup_ffmpeg()...")
    try:
        ffmpeg_path = setup_ffmpeg()
        print("   ✅ FFmpeg configured successfully!")
        print(f"   📂 Path: {ffmpeg_path}")
        print()
        print("=" * 60)
        print("✨ SUCCESS! Your system is ready to process videos!")
        print("=" * 60)
        return True
    except RuntimeError as e:
        print("   ❌ FFmpeg setup failed!")
        print()
        print("=" * 60)
        print("❌ ERROR: FFmpeg not found")
        print("=" * 60)
        print(str(e))
        return False

if __name__ == "__main__":
    success = test_ffmpeg()
    sys.exit(0 if success else 1)
