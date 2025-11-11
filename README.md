# 🎬 AI Video Lecture Assistant

**Automatically transcribe, analyze, and add subtitles to educational videos using AI**

Transform your video lectures into searchable transcripts, insightful summaries, study quizzes, and videos with professional subtitles - all running **100% locally** with no API costs!

**Created by [Aditya Takawale](https://github.com/Aditya-Takawale)**

---

## ✨ Features

- 🎤 **Accurate Transcription** - Powered by OpenAI Whisper (supports 99+ languages)
- 🤖 **AI Analysis** - Generate summaries, key insights, and quiz questions using Ollama
- � **Embedded Subtitles** - Creates video files with toggleable subtitle tracks
- 📄 **Word Documents** - Professional analysis reports in .docx format
- 🔒 **100% Local & Private** - No cloud APIs, no data leaves your computer
- 💰 **Zero Cost** - Completely free to use, no API keys required

---

## 🚀 Quick Start

### Prerequisites

1. **Python 3.9+** installed
2. **FFmpeg** installed (see platform-specific instructions below)
3. **Ollama** installed and running ([Download here](https://ollama.ai))

### Platform-Specific Setup

<details>
<summary><b>🪟 Windows Setup</b></summary>

```powershell
# 1. Install FFmpeg (choose one method)
# Method A: Using Chocolatey (recommended)
choco install ffmpeg

# Method B: Using Scoop
scoop install ffmpeg

# Method C: Manual download from https://ffmpeg.org/download.html

# 2. Verify FFmpeg installation
ffmpeg -version

# 3. Install Ollama from https://ollama.ai
# 4. Continue with "Installation" steps below
```
</details>

<details>
<summary><b>🍎 macOS Setup</b></summary>

```bash
# 1. Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Install FFmpeg
brew install ffmpeg

# 3. Install Ollama
brew install ollama

# 4. Verify installations
ffmpeg -version
ollama --version

# 5. Continue with "Installation" steps below
```
</details>

<details>
<summary><b>🐧 Linux Setup</b></summary>

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg
curl -fsSL https://ollama.ai/install.sh | sh

# Fedora/RHEL
sudo dnf install ffmpeg
curl -fsSL https://ollama.ai/install.sh | sh

# Arch Linux
sudo pacman -S ffmpeg
curl -fsSL https://ollama.ai/install.sh | sh

# Verify installations
ffmpeg -version
ollama --version

# Continue with "Installation" steps below
```
</details>

### Installation

**Windows:**
```powershell
# 1. Clone/download this repository
cd c:\Developer\ai-summary

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
.venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Start Ollama (in a separate terminal)
ollama serve

# 6. Pull the AI model
ollama pull llama3.1
```

**macOS/Linux:**
```bash
# 1. Clone/download this repository
cd ~/ai-summary

# 2. Create virtual environment
python3 -m venv .venv

# 3. Activate virtual environment
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Start Ollama (in a separate terminal)
ollama serve

# 6. Pull the AI model
ollama pull llama3.1
```

### ⚡ Easy Usage - Simple Script

**Simplest method - Just drag and drop:**
```powershell
process_video.bat "my_lecture.mp4"
```

Or **drag-and-drop** your video file onto `process_video.bat`!

### Advanced Usage

```powershell
# Full processing with all options
python embed_subtitles.py video.mp4 --keep-srt

# Use better Whisper model for higher accuracy
python embed_subtitles.py video.mp4 -m small

# Custom output directory
python embed_subtitles.py video.mp4 -o my_outputs

# Use different AI model
python embed_subtitles.py video.mp4 --ollama-model llama3.2
```

---

## 📁 Output Files

After processing `my_lecture.mp4`, you'll get:

```
outputs/
├── my_lecture_with_subtitles.mp4  ← Video with embedded subtitle track
├── my_lecture_subtitles.srt       ← Standalone subtitle file
├── my_lecture_analysis.docx       ← Word document with analysis
└── my_lecture_analysis.json       ← JSON data
```

### How to Use the Video with Subtitles

1. Open `my_lecture_with_subtitles.mp4` in **VLC**, **Windows Media Player**, or any video player
2. Look for the **"Subtitles"** or **"CC"** button in player controls
3. Toggle subtitles **ON/OFF** as needed!

---

## 📦 Distribution Options

### Option 1: Share Source Code (Recommended for Developers)

```powershell
# 1. Share the entire folder
# 2. Recipients install Python + Ollama
# 3. Recipients run: pip install -r requirements.txt
# 4. Ready to use!
```

### Option 2: Standalone Executable (For End Users)

```powershell
# Install PyInstaller
pip install pyinstaller

# Create executable
pyinstaller --onefile --name="AI-Video-Processor" embed_subtitles.py

# Distribute: dist/AI-Video-Processor.exe + include instructions to install Ollama
```

**Note:** Users will still need Ollama installed (AI models are too large to bundle ~4GB+).

### Option 3: Complete Installer Package

Use **Inno Setup** or **NSIS** to create a professional installer:
- Bundles Python runtime
- Auto-installs dependencies
- Creates desktop shortcuts
- Includes Ollama installer link

---

## ⚡ Optimizations & Improvements

### Current Performance
- **Processing Time**: ~5-10 minutes for 10-minute video (base model)
- **Accuracy**: 95-99% transcription, 75-90% AI analysis quality

### Suggested Optimizations

**1. GPU Acceleration** (Faster transcription)
```python
# Edit transcriber.py, change:
result = model.transcribe(audio_path, fp16=False)  # CPU
# To:
result = model.transcribe(audio_path, fp16=True)   # GPU (10x faster!)
```

**2. Batch Processing Script**
```powershell
# Process multiple videos at once
python batch_process_all.py videos/*.mp4
```

**3. Quality vs Speed Trade-offs**
```powershell
# Ultra-fast (2-3 min for 10-min video, lower accuracy)
python embed_subtitles.py video.mp4 -m tiny

# Balanced (default, 5-10 min)
python embed_subtitles.py video.mp4 -m base

# High quality (15-30 min, best accuracy)
python embed_subtitles.py video.mp4 -m medium
```

**4. Model Caching** (Already implemented)
- Whisper model loads once and stays in memory
- Ollama runs as persistent service

**5. Parallel Processing**
- Process video + audio analysis simultaneously
- Use multiprocessing for batch operations

---

## 🔧 Advanced Features to Add

**Low-hanging fruit:**
1. ✅ Batch processing multiple videos
2. ✅ Progress bars with estimated time remaining
3. ✅ Email/notification when long processing completes
4. ✅ Custom AI prompts for specialized content

**Medium complexity:**
5. 📹 Chapter detection and timestamps
6. 🎨 Custom subtitle styling (fonts, colors, positioning)
7. 🌐 Web interface (Flask/FastAPI + React)
8. 📱 Mobile app companion

**Advanced:**
9. 🗣️ Speaker diarization (identify different speakers)
10. 📊 Auto-generate highlight reels
11. 🃏 Anki flashcard export
12. 🔴 Real-time processing during live streams

---

## 🛠️ Technical Architecture

```
Video File (.mp4, .avi, etc.)
    ↓
1. Audio Extraction (moviepy)
    ↓
2. Speech-to-Text (Whisper AI) → Timestamped segments
    ↓
3. Content Analysis (Ollama LLM) → Summary + Insights + Quiz
    ↓
4. Subtitle Generation (SRT format)
    ↓
5. Subtitle Embedding (FFmpeg) → mov_text codec
    ↓
Output: Video with subtitles + Word doc + JSON
```

### Models & Technologies
- **Whisper** (base model ~140MB) - 99 language support
- **Ollama llama3.1** (~4.7GB) - Local LLM, no API calls
- **FFmpeg** - Video processing
- **python-docx** - Document generation

---

## 📋 System Requirements

**Minimum:**
- OS: Windows 10/11, macOS 10.15+, Linux (Ubuntu 18.04+, Fedora 30+, Arch)
- RAM: 4GB
- Storage: 8GB (models + videos)
- CPU: Any modern processor

**Recommended:**
- RAM: 8GB+
- Storage: 20GB+ SSD
- GPU: NVIDIA with CUDA support (10x faster on Windows/Linux)
- GPU: Apple Silicon M1/M2/M3 (Metal acceleration on macOS)

---

## 🐛 Troubleshooting

### FFmpeg Not Found

**Error:** `[Errno 2] No such file or directory: 'ffmpeg'`

**Solution:**
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows (Chocolatey)
choco install ffmpeg

# Verify installation
ffmpeg -version
```

### SSL Certificate Error (macOS)

**Error:** `ssl.SSLCertVerificationError: [SSL: CERTIFICATE_VERIFY_FAILED]`

**Solution:**
```bash
# Run the Install Certificates command
/Applications/Python\ 3.12/Install\ Certificates.command

# OR use Homebrew Python (includes certificates)
brew install python@3.12
```

### Ollama Connection Error

**Error:** `Connection refused to localhost:11434`

**Solution:**
```bash
# Start Ollama server
ollama serve

# In another terminal, verify model is installed
ollama list
ollama pull llama3.1
```

### Out of Memory Error

**Error:** `RuntimeError: CUDA out of memory`

**Solution:**
```python
# Use a smaller Whisper model
python embed_subtitles.py video.mp4 -m tiny  # or -m base

# Process shorter videos
# Consider splitting long videos into segments
```

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'ai_video_assistant'`

**Solution:**
```bash
# Make sure virtual environment is activated
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

# Reinstall package
pip install -r requirements.txt
```

### Permission Errors (Linux/macOS)

**Error:** `PermissionError: [Errno 13]`

**Solution:**
```bash
# Make sure you have write permissions
chmod +w ./outputs
chmod +w ./temp_audio

# Don't run with sudo unless necessary
```

---

## 👨‍💻 Author

**Aditya Takawale**
- GitHub: [@Aditya-Takawale](https://github.com/Aditya-Takawale)
- Repository: [AI-Summary](https://github.com/Aditya-Takawale/AI-Summary)

## 📜 License

MIT License - See [LICENSE](LICENSE) file for details

Copyright © 2025 Aditya Takawale

## 🙏 Acknowledgments

Built with:
- [OpenAI Whisper](https://github.com/openai/whisper) - Speech recognition (MIT License)
- [Ollama](https://ollama.ai) - Local AI models (MIT License)
- [MoviePy](https://zulko.github.io/moviepy/) - Video processing (MIT License)
- [FFmpeg](https://ffmpeg.org/) - Media processing (LGPL)

This project is an independent integration of these tools and is not affiliated with or endorsed by OpenAI, Ollama, or any of the above projects.

## ⚖️ Disclaimer

This software is provided "as is" for educational and personal use. Users are responsible for:
- Complying with copyright laws when processing videos
- Respecting terms of service of video platforms
- Using this tool ethically and legally
- Not redistributing copyrighted content without permission

The author is not responsible for misuse of this software.

## 🌟 Support

If you find this project helpful, please give it a ⭐️ on GitHub!

**Report Issues:** [GitHub Issues](https://github.com/Aditya-Takawale/AI-Summary/issues)

---

**Built with ❤️ by Aditya Takawale | 100% Local, 100% Free, 100% Private**

---