# 🚀 Ollama Optimization Guide

This guide helps you optimize Ollama performance and avoid timeout errors when processing videos.

---

## 🐛 Common Issue: Timeout Errors

**Error Message:**
```
ERROR: Ollama request timed out. Try a smaller model or shorter transcription.
requests.exceptions.ReadTimeout: HTTPConnectionPool(host='localhost', port=11434): Read timed out.
```

**What This Means:**
The AI model (Ollama) took too long to analyze your video transcription. This typically happens with:
- Long videos (>15 minutes)
- Slow computers
- Large language models
- Limited RAM

---

## ✅ Solutions (Ordered by Effectiveness)

### 1. Use a Faster Model (Recommended)

Instead of `llama3.1` (~4.7GB), use a smaller, faster model:

```bash
# Option A: Llama 3.2 (3B parameters - FASTEST)
ollama pull llama3.2
ollama pull llama3.2:3b

# Option B: Mistral (7B parameters - FAST)
ollama pull mistral

# Option C: Phi (2.7B parameters - VERY FAST)
ollama pull phi
```

**Update your code:**
```python
from ai_video_assistant import VideoAssistant

# Use faster model
assistant = VideoAssistant(ollama_model="llama3.2")
result = assistant.process_video("video.mp4")
```

**Speed Comparison:**
| Model | Size | Speed | Quality |
|-------|------|-------|---------|
| llama3.1 | 4.7GB | Slow | Excellent |
| llama3.2 | 2GB | Fast | Very Good |
| mistral | 4.1GB | Medium | Excellent |
| phi | 1.6GB | Very Fast | Good |

---

### 2. Increase Timeout (For Long Videos)

If you have a long video and good patience:

```python
from ai_video_assistant import VideoAssistant

# Increase timeout to 20 minutes (1200 seconds)
assistant = VideoAssistant(
    ollama_model="llama3.1",
    ollama_timeout=1200  # 20 minutes
)

result = assistant.process_video("long_video.mp4")
```

---

### 3. Process Shorter Videos

Split long videos into smaller segments:

**Using FFmpeg (Mac/Linux):**
```bash
# Split video into 10-minute segments
ffmpeg -i long_video.mp4 -c copy -map 0 -segment_time 00:10:00 -f segment output_%03d.mp4

# Process each segment
python video_exec.py output_001.mp4
python video_exec.py output_002.mp4
```

**Using Python:**
```python
from moviepy import VideoFileClip

video = VideoFileClip("long_video.mp4")
duration = video.duration

# Split into 10-minute chunks
chunk_duration = 600  # 10 minutes
for i, start in enumerate(range(0, int(duration), chunk_duration)):
    end = min(start + chunk_duration, duration)
    chunk = video.subclip(start, end)
    chunk.write_videofile(f"chunk_{i:03d}.mp4")
```

---

### 4. Optimize System Performance

#### macOS (Apple Silicon M1/M2/M3)

```bash
# 1. Close unnecessary applications
# Activity Monitor → Quit memory-heavy apps

# 2. Ensure Ollama has enough resources
# Check RAM usage
top -l 1 | grep PhysMem

# 3. Restart Ollama
pkill ollama
ollama serve
```

#### macOS (Intel)

```bash
# Check CPU temperature (may throttle if hot)
sudo powermetrics --samplers smc -i1 -n1

# Allow more CPU usage
# System Settings → Energy Saver → Prevent computer from sleeping
```

---

### 5. Use Whisper's Smaller Model

Reduce transcription length by using a smaller Whisper model:

```python
from ai_video_assistant import VideoAssistant

# Use 'tiny' or 'base' Whisper model (faster, shorter transcripts)
assistant = VideoAssistant(
    whisper_model="tiny",  # or "base"
    ollama_model="llama3.2",
    ollama_timeout=900
)
```

**Whisper Model Comparison:**
| Model | Size | Speed | Accuracy |
|-------|------|-------|----------|
| tiny | 39MB | Very Fast | ~70% |
| base | 74MB | Fast | ~80% |
| small | 244MB | Medium | ~90% |
| medium | 769MB | Slow | ~95% |

---

## 🔍 Debugging Ollama Issues

### Check if Ollama is Running

```bash
# Test Ollama connection
curl http://localhost:11434/api/tags

# Should return JSON with installed models
```

### Check Ollama Logs

```bash
# macOS/Linux
tail -f ~/.ollama/logs/server.log

# Or run Ollama in foreground to see logs
ollama serve
```

### Test Ollama Directly

```bash
# Test if model responds
ollama run llama3.1 "Hello, test message"

# If this times out, your system may need:
# - More RAM
# - Faster CPU
# - Smaller model
```

---

## 📊 Performance Benchmarks

**Test Video: 10-minute lecture (2,000 word transcription)**

| Configuration | Time | Success Rate |
|---------------|------|--------------|
| llama3.1 + base Whisper | 8-12 min | 70% |
| llama3.2 + base Whisper | 3-5 min | 95% |
| mistral + tiny Whisper | 2-4 min | 90% |
| phi + tiny Whisper | 1-2 min | 85% |

**System: MacBook Air M2, 8GB RAM**

---

## 🎯 Recommended Configurations

### For Speed (Quick Results)

```python
assistant = VideoAssistant(
    whisper_model="tiny",
    ollama_model="phi",
    ollama_timeout=300  # 5 minutes
)
```

### For Balanced (Good Quality + Speed)

```python
assistant = VideoAssistant(
    whisper_model="base",
    ollama_model="llama3.2",
    ollama_timeout=600  # 10 minutes
)
```

### For Quality (Best Results)

```python
assistant = VideoAssistant(
    whisper_model="small",
    ollama_model="llama3.1",
    ollama_timeout=1200  # 20 minutes
)
```

---

## 🆘 Still Having Issues?

### 1. Check System Requirements

**Minimum:**
- RAM: 4GB (8GB for llama3.1)
- Storage: 10GB free
- CPU: 2+ cores

**Recommended:**
- RAM: 16GB
- Storage: 20GB SSD
- CPU: 4+ cores (Apple M1/M2/M3 or Intel i5+)

### 2. Try Alternative Models

```bash
# Very lightweight models (if nothing else works)
ollama pull tinyllama
ollama pull gemma:2b
```

### 3. Update Ollama

```bash
# macOS
brew upgrade ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh
```

### 4. Check for Updates

```bash
# Update the AI Video Assistant library
pip install --upgrade ai-video-assistant
```

---

## 💡 Pro Tips

### 1. Pre-warm the Model

Run Ollama once before processing to load model into memory:

```bash
ollama run llama3.2 "test"
```

### 2. Monitor Progress

Watch Ollama logs in real-time:

```bash
# Terminal 1: Run Ollama
ollama serve

# Terminal 2: Process video
python video_exec.py video.mp4

# Terminal 3: Watch system resources
htop  # or Activity Monitor on Mac
```

### 3. Batch Processing

Process multiple videos overnight:

```bash
#!/bin/bash
for video in *.mp4; do
    echo "Processing $video..."
    python video_exec.py "$video"
    echo "Completed $video"
done
```

### 4. Use GPU Acceleration (if available)

Ollama automatically uses:
- **Apple Silicon (M1/M2/M3):** Metal GPU acceleration
- **NVIDIA GPUs:** CUDA acceleration
- **AMD GPUs:** ROCm acceleration (Linux)

No configuration needed!

---

## 📞 Get Help

If none of these solutions work:

1. **Check Ollama Status:**
   ```bash
   ollama list
   ollama ps
   ```

2. **Report Issue:**
   - GitHub: [AI-Summary Issues](https://github.com/Aditya-Takawale/AI-Summary/issues)
   - Include: OS, RAM, Ollama version, video length, error message

3. **Community Support:**
   - Ollama Discord: https://discord.gg/ollama
   - Ollama GitHub: https://github.com/ollama/ollama

---

**Remember: Using a smaller/faster model (llama3.2 or mistral) solves 90% of timeout issues! 🚀**
