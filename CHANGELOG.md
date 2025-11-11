# 📝 Changelog

All notable changes to the AI Video Assistant project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.5] - 2025-11-11

### 🌍 Added - Cross-Platform Support
- **Full cross-platform compatibility** for Windows, macOS, and Linux
- **Smart FFmpeg detection** - automatically finds system FFmpeg or uses imageio-ffmpeg as fallback
- **Platform-specific error messages** with installation instructions for each OS
- Added `check_system_ffmpeg()` function for better FFmpeg detection
- Added comprehensive cross-platform setup guide (`docs/CROSS_PLATFORM_GUIDE.md`)
- Added FFmpeg detection test script (`test_ffmpeg_detection.py`)

### 📚 Improved
- **Enhanced `ffmpeg_utils.py`** with cross-platform path handling
- **Updated README.md** with platform-specific setup instructions (Windows/macOS/Linux)
- **Added troubleshooting section** to README covering common issues on all platforms
- **Expanded system requirements** to include Apple Silicon Metal acceleration
- Added platform-specific notes for GPU acceleration (NVIDIA CUDA, Apple Metal)

### 🔧 Fixed
- FFmpeg not found error on macOS and Linux systems
- Path separator issues across different operating systems
- SSL certificate verification errors on macOS (documented fix)

### 📦 Package Updates
- Added Python 3.13 support classifier
- Added OS-specific classifiers (Windows, macOS, Linux)
- Updated package metadata for better cross-platform discovery

---

## [1.0.4] - 2025-11-10

### 🐛 Fixed
- Fixed quiz validation to handle both list and dict formats for options
- Added automatic conversion from list format to dict format with A/B/C/D keys
- Improved error handling for varying LLM response formats

### 🔨 Changed
- Enhanced quiz validation logic in `analyzer.py`
- Added warning messages for quiz option format conversion

---

## [1.0.3] - 2025-11-10

### 🐛 Fixed
- Fixed import errors when package installed from PyPI
- Changed all imports to relative imports (e.g., `from .ffmpeg_utils`)
- Improved module discovery in published package

---

## [1.0.2] - 2025-11-10

### 🐛 Fixed
- Additional module import fixes
- Package structure improvements

---

## [1.0.1] - 2025-11-10

### 🐛 Fixed
- Fixed missing modules in package distribution
- Corrected package file structure

---

## [1.0.0] - 2025-11-10

### 🎉 Initial Release

#### Features
- **AI-powered video transcription** using OpenAI Whisper
  - Support for 99+ languages
  - Multiple model sizes (tiny, base, small, medium, large)
  - GPU acceleration support (CUDA)
  
- **Content analysis** using Ollama Llama 3.1
  - Generate summaries
  - Extract key insights
  - Create quiz questions
  
- **Subtitle generation**
  - SRT format subtitles
  - Embedded subtitle tracks in video files
  - Timestamped segments
  
- **Document generation**
  - Word document (.docx) with full analysis
  - JSON export for programmatic access
  
- **100% local processing**
  - No cloud APIs
  - Complete privacy
  - Zero ongoing costs

#### Package Structure
- `ai_video_assistant/core.py` - Main VideoAssistant API
- `ai_video_assistant/transcriber.py` - Whisper integration
- `ai_video_assistant/analyzer.py` - Ollama LLM integration
- `ai_video_assistant/audio_extractor.py` - Audio extraction
- `ai_video_assistant/subtitle_generator.py` - SRT generation
- `ai_video_assistant/word_generator.py` - DOCX generation
- `ai_video_assistant/ffmpeg_utils.py` - FFmpeg utilities

#### Scripts
- `embed_subtitles.py` - Main CLI script
- `batch_process.py` - Batch video processing
- `api_server.py` - REST API server
- `process_video.bat` - Windows batch file

#### Documentation
- README.md - Project overview and quick start
- LICENSE - MIT License
- CITATION.cff - Citation information
- COPYRIGHT_ANALYSIS.md - Legal verification

---

## Release Notes

### Version 1.0.5 Highlights

This release makes the AI Video Assistant **truly cross-platform**, ensuring it works seamlessly on Windows, macOS, and Linux!

#### What's New?
✅ **Universal FFmpeg Detection** - Works on any operating system  
✅ **Smart Fallback System** - Uses system FFmpeg or imageio-ffmpeg automatically  
✅ **Better Error Messages** - Platform-specific installation instructions  
✅ **Comprehensive Documentation** - Complete setup guides for all platforms  
✅ **Test Tools** - Easy way to verify your setup works  

#### Tested On:
- ✅ Windows 10/11 (Intel + NVIDIA GPU)
- ✅ macOS 10.15+ (Intel + Apple Silicon M1/M2/M3)
- ✅ Ubuntu 18.04+, Fedora 30+, Arch Linux

#### Breaking Changes
None - fully backward compatible with 1.0.4

#### Migration Guide
No migration needed. Simply upgrade:
```bash
pip install --upgrade ai-video-assistant
```

---

## Upcoming Features (Roadmap)

### v1.1.0 (Planned)
- [ ] Better progress bars with ETA
- [ ] Resume interrupted processing
- [ ] Custom AI prompts for specialized content
- [ ] Web interface (Flask/React)

### v1.2.0 (Planned)
- [ ] Speaker diarization (identify different speakers)
- [ ] Chapter detection and timestamps
- [ ] Custom subtitle styling
- [ ] Anki flashcard export

### v2.0.0 (Future)
- [ ] Real-time processing for live streams
- [ ] Video highlight generation
- [ ] Mobile app companion
- [ ] Cloud deployment option

---

## Support

- **Report Issues:** [GitHub Issues](https://github.com/Aditya-Takawale/AI-Summary/issues)
- **Documentation:** [Project README](https://github.com/Aditya-Takawale/AI-Summary)
- **PyPI Package:** [ai-video-assistant](https://pypi.org/project/ai-video-assistant/)

---

**Author:** Aditya Takawale  
**License:** MIT  
**Repository:** https://github.com/Aditya-Takawale/AI-Summary
