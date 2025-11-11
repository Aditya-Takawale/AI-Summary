# 🌍 Cross-Platform Setup Guide

This guide provides detailed instructions for setting up and running **AI Video Assistant** on Windows, macOS, and Linux.

---

## Table of Contents

1. [Windows Setup](#windows-setup)
2. [macOS Setup](#macos-setup)
3. [Linux Setup](#linux-setup)
4. [Common Issues](#common-issues)
5. [Platform-Specific Notes](#platform-specific-notes)

---

## 🪟 Windows Setup

### Prerequisites

1. **Python 3.9+**
   - Download from: https://www.python.org/downloads/
   - ✅ Check "Add Python to PATH" during installation

2. **FFmpeg**
   ```powershell
   # Option 1: Chocolatey (recommended)
   choco install ffmpeg
   
   # Option 2: Scoop
   scoop install ffmpeg
   
   # Option 3: Manual installation
   # Download from: https://ffmpeg.org/download.html
   # Extract and add to PATH
   ```

3. **Ollama**
   - Download installer from: https://ollama.ai
   - Run the installer and follow the wizard

### Installation Steps

```powershell
# 1. Clone repository
git clone https://github.com/Aditya-Takawale/AI-Summary.git
cd AI-Summary

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
.venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Verify FFmpeg
ffmpeg -version

# 6. Start Ollama (new PowerShell window)
ollama serve

# 7. Pull AI model
ollama pull llama3.1

# 8. Test installation
python -c "from ai_video_assistant import VideoAssistant; print('✓ Installation successful!')"
```

### Running on Windows

```powershell
# Activate environment
.venv\Scripts\activate

# Simple usage
python embed_subtitles.py video.mp4

# Or use the batch file
process_video.bat video.mp4
```

### Windows-Specific Notes

- Use `\` for paths: `C:\Users\Name\Videos\lecture.mp4`
- PowerShell may require execution policy changes:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```
- GPU acceleration requires NVIDIA GPU with CUDA drivers
- Antivirus may flag FFmpeg - add exception if needed

---

## 🍎 macOS Setup

### Prerequisites

1. **Install Homebrew** (if not already installed)
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install Python**
   ```bash
   # Use Homebrew Python (recommended - includes SSL certificates)
   brew install python@3.12
   
   # Verify installation
   python3 --version
   ```

3. **Install FFmpeg**
   ```bash
   brew install ffmpeg
   
   # Verify installation
   ffmpeg -version
   ```

4. **Install Ollama**
   ```bash
   brew install ollama
   
   # Or download from: https://ollama.ai
   ```

### Installation Steps

```bash
# 1. Clone repository
git clone https://github.com/Aditya-Takawale/AI-Summary.git
cd AI-Summary

# 2. Create virtual environment
python3 -m venv .venv

# 3. Activate virtual environment
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Start Ollama (new Terminal window)
ollama serve

# 6. Pull AI model
ollama pull llama3.1

# 7. Test installation
python -c "from ai_video_assistant import VideoAssistant; print('✓ Installation successful!')"
```

### SSL Certificate Fix (macOS)

If you get SSL certificate errors when downloading Whisper models:

```bash
# Option 1: Run Install Certificates (for python.org Python)
/Applications/Python\ 3.12/Install\ Certificates.command

# Option 2: Use Homebrew Python (already has certificates)
brew install python@3.12

# Option 3: Manual certificate installation
pip install --upgrade certifi
```

### Running on macOS

```bash
# Activate environment
source .venv/bin/activate

# Simple usage
python embed_subtitles.py ~/Videos/lecture.mp4

# Process with better model
python embed_subtitles.py video.mp4 -m small
```

### macOS-Specific Notes

- Use `/` for paths: `/Users/name/Videos/lecture.mp4`
- Apple Silicon (M1/M2/M3) gets Metal acceleration automatically
- First run may ask for permissions to access files/folders
- Homebrew installs to `/opt/homebrew` on Apple Silicon, `/usr/local` on Intel
- Use `python3` and `pip3` commands (not `python` or `pip`)

---

## 🐧 Linux Setup

### Prerequisites

#### Ubuntu/Debian

```bash
# Update package list
sudo apt update

# Install Python and pip
sudo apt install python3 python3-pip python3-venv

# Install FFmpeg
sudo apt install ffmpeg

# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Verify installations
python3 --version
ffmpeg -version
ollama --version
```

#### Fedora/RHEL

```bash
# Install Python
sudo dnf install python3 python3-pip

# Install FFmpeg
sudo dnf install ffmpeg

# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Verify installations
python3 --version
ffmpeg -version
ollama --version
```

#### Arch Linux

```bash
# Install Python
sudo pacman -S python python-pip

# Install FFmpeg
sudo pacman -S ffmpeg

# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Verify installations
python3 --version
ffmpeg -version
ollama --version
```

### Installation Steps

```bash
# 1. Clone repository
git clone https://github.com/Aditya-Takawale/AI-Summary.git
cd AI-Summary

# 2. Create virtual environment
python3 -m venv .venv

# 3. Activate virtual environment
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Start Ollama (new terminal)
ollama serve

# 6. Pull AI model
ollama pull llama3.1

# 7. Test installation
python -c "from ai_video_assistant import VideoAssistant; print('✓ Installation successful!')"
```

### Running on Linux

```bash
# Activate environment
source .venv/bin/activate

# Simple usage
python embed_subtitles.py ~/Videos/lecture.mp4

# Process with GPU acceleration (if NVIDIA GPU)
python embed_subtitles.py video.mp4 -m base
```

### Linux-Specific Notes

- Use `/` for paths: `/home/username/Videos/lecture.mp4`
- GPU acceleration requires NVIDIA GPU with CUDA toolkit:
  ```bash
  # Install CUDA (Ubuntu/Debian)
  sudo apt install nvidia-cuda-toolkit
  
  # Verify
  nvidia-smi
  ```
- May need to add user to video group for GPU access:
  ```bash
  sudo usermod -a -G video $USER
  # Log out and back in
  ```
- Use `python3` and `pip3` commands
- Ensure write permissions for output directories:
  ```bash
  chmod +w ./outputs ./temp_audio
  ```

---

## 🐛 Common Issues

### 1. FFmpeg Not Found

**Symptoms:**
```
[Errno 2] No such file or directory: 'ffmpeg'
```

**Solutions:**

| Platform | Solution |
|----------|----------|
| Windows | `choco install ffmpeg` or download manually |
| macOS | `brew install ffmpeg` |
| Linux | `sudo apt install ffmpeg` (Ubuntu) |

**Verify:**
```bash
ffmpeg -version
```

### 2. SSL Certificate Errors

**Symptoms:**
```
ssl.SSLCertVerificationError: [SSL: CERTIFICATE_VERIFY_FAILED]
```

**Solutions:**

| Platform | Solution |
|----------|----------|
| macOS | Run `/Applications/Python 3.12/Install Certificates.command` |
| Linux | `sudo apt install ca-certificates` |
| Windows | Usually not an issue |

### 3. Ollama Connection Refused

**Symptoms:**
```
Connection refused to localhost:11434
```

**Solution (All Platforms):**
```bash
# Start Ollama server
ollama serve

# Verify it's running
curl http://localhost:11434/api/tags

# Pull model if needed
ollama pull llama3.1
```

### 4. CUDA/GPU Issues

**Symptoms:**
```
RuntimeError: CUDA out of memory
```

**Solutions:**
```bash
# Use smaller model
python embed_subtitles.py video.mp4 -m tiny

# Or process on CPU only
python embed_subtitles.py video.mp4 -m base
```

### 5. Permission Errors

**Symptoms:**
```
PermissionError: [Errno 13]
```

**Solution (Linux/macOS):**
```bash
# Fix directory permissions
chmod +w ./outputs
chmod +w ./temp_audio

# Or run from user directory
cd ~/ai-video-assistant
```

**Solution (Windows):**
- Run as Administrator (right-click → Run as administrator)
- Or move to user directory (e.g., `C:\Users\YourName\`)

---

## 📌 Platform-Specific Notes

### Path Differences

| Platform | Home Directory | Path Separator | Example Path |
|----------|---------------|----------------|--------------|
| Windows | `C:\Users\Name` | `\` | `C:\Users\Name\Videos\video.mp4` |
| macOS | `/Users/name` | `/` | `/Users/name/Videos/video.mp4` |
| Linux | `/home/name` | `/` | `/home/name/Videos/video.mp4` |

### Command Differences

| Action | Windows | macOS/Linux |
|--------|---------|-------------|
| Python | `python` | `python3` |
| Pip | `pip` | `pip3` |
| Activate venv | `.venv\Scripts\activate` | `source .venv/bin/activate` |
| Path separator | `;` | `:` |

### GPU Acceleration

| Platform | GPU Support | Notes |
|----------|-------------|-------|
| Windows | NVIDIA (CUDA) | Install CUDA Toolkit + cuDNN |
| macOS | Apple Silicon (Metal) | Automatic with M1/M2/M3 chips |
| Linux | NVIDIA (CUDA) | Install nvidia-cuda-toolkit |

### Virtual Environment

**Create:**
```bash
# Windows
python -m venv .venv

# macOS/Linux
python3 -m venv .venv
```

**Activate:**
```bash
# Windows (PowerShell)
.venv\Scripts\activate

# Windows (cmd.exe)
.venv\Scripts\activate.bat

# macOS/Linux
source .venv/bin/activate
```

**Deactivate (all platforms):**
```bash
deactivate
```

---

## 🎯 Quick Reference

### One-Line Setup

**Windows:**
```powershell
git clone https://github.com/Aditya-Takawale/AI-Summary.git; cd AI-Summary; python -m venv .venv; .venv\Scripts\activate; pip install -r requirements.txt
```

**macOS/Linux:**
```bash
git clone https://github.com/Aditya-Takawale/AI-Summary.git && cd AI-Summary && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
```

### Quick Test

```python
# Test if everything works
python -c "
from ai_video_assistant import VideoAssistant
import whisper
import ollama
print('✓ All imports successful!')
print('✓ Ready to process videos!')
"
```

---

## 📞 Support

If you encounter issues not covered here:

1. Check [GitHub Issues](https://github.com/Aditya-Takawale/AI-Summary/issues)
2. Create a new issue with:
   - Your operating system and version
   - Python version (`python --version`)
   - Error message (full traceback)
   - Steps to reproduce

---

**Happy video processing! 🎬**
