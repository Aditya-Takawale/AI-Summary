# 📝 Quick Reference Guide

## Simple Usage Commands

### 🎯 Easiest Way - Batch Script
```powershell
# Just run this!
process_video.bat "my_video.mp4"

# Or drag-and-drop video onto process_video.bat
```

### 📹 Full Command (if you want control)
```powershell
python embed_subtitles.py "my_video.mp4" --keep-srt
```

### 🔢 Batch Processing Multiple Videos
```powershell
# Process all MP4 files in current folder
python batch_process.py *.mp4

# Process specific videos
python batch_process.py video1.mp4 video2.mp4 video3.mp4
```

---

## 📁 What You Get

After processing `lecture.mp4`:

```
outputs/
├── lecture_with_subtitles.mp4  ← Play in VLC/Media Player (subtitles toggleable!)
├── lecture_subtitles.srt       ← Subtitle file
├── lecture_analysis.docx       ← Word document with analysis
└── lecture_analysis.json       ← JSON data
```

---

## ⚙️ Model Options

### Whisper (Transcription Quality)
```powershell
python embed_subtitles.py video.mp4 -m tiny     # Fastest, lower accuracy
python embed_subtitles.py video.mp4 -m base     # Balanced (DEFAULT)
python embed_subtitles.py video.mp4 -m small    # Better accuracy
python embed_subtitles.py video.mp4 -m medium   # High accuracy (slower)
```

### Ollama (AI Analysis)
```powershell
# Default model
python embed_subtitles.py video.mp4 --ollama-model llama3.1

# Better model (if you downloaded it)
python embed_subtitles.py video.mp4 --ollama-model llama3.2
```

---

## 🚀 Sharing Your Application

### Quick Share (Source Code)
1. Zip the entire `ai-summary` folder
2. Share with others
3. They run:
   ```powershell
   pip install -r requirements.txt
   ollama pull llama3.1
   process_video.bat my_video.mp4
   ```

### Professional Distribution (Executable)
```powershell
pip install pyinstaller
pyinstaller --onefile --name="VideoSubtitler" embed_subtitles.py
# Share: dist/VideoSubtitler.exe
```

---

## 🔧 Performance Tips

### Speed Up Processing
1. **Use GPU** - Edit `transcriber.py`, set `fp16=True`
2. **Smaller model** - Use `-m tiny` for faster processing
3. **Close other apps** - Free up RAM/CPU

### Improve Accuracy
1. **Larger model** - Use `-m medium` or `-m large`
2. **Clean audio** - Remove background noise first
3. **Better AI model** - Use `llama3.2` instead of `llama3.1`

---

## ❗ Troubleshooting

### "Cannot connect to Ollama"
```powershell
# Start Ollama in another terminal
ollama serve
```

### "FFmpeg not found"
```powershell
# Already bundled, but if needed:
choco install ffmpeg
```

### "Out of memory"
```powershell
# Use smaller model
python embed_subtitles.py video.mp4 -m tiny
```

### Video has no audio
- Check if original video has audio track
- Try different video format

---

## 📊 Expected Processing Times

**10-minute video (base model):**
- Audio extraction: ~30 seconds
- Transcription: ~3-5 minutes
- AI analysis: ~1-2 minutes
- Subtitle embedding: ~30 seconds
- **Total: ~5-8 minutes**

**With GPU acceleration:**
- Transcription: ~30-60 seconds
- **Total: ~2-3 minutes**

---

## 🎯 Best Practices

1. **Test with short video first** (1-2 minutes)
2. **Keep Ollama running** - Don't close the terminal
3. **Check outputs folder** - All results saved there
4. **Use process_video.bat** - Simplest method
5. **Backup important videos** - Before processing

---

## 📦 Files in Your Project

**Main scripts:**
- `embed_subtitles.py` - Full processing pipeline
- `process_video.bat` - Simple launcher
- `batch_process.py` - Process multiple videos

**Helper modules:**
- `audio_extractor.py` - Extract audio from video
- `transcriber.py` - Speech-to-text with Whisper
- `content_analyzer_ollama.py` - AI analysis with Ollama
- `word_generator.py` - Create Word documents
- `subtitle_generator.py` - Generate SRT files
- `ffmpeg_utils.py` - FFmpeg setup utilities

**Documentation:**
- `README.md` - Full documentation
- `DEPLOYMENT_GUIDE.md` - How to share/distribute
- `ACCURACY_AND_LIMITS.md` - Model accuracy info
- `QUICK_REFERENCE.md` - This file!

---

## ✅ Your App is Ready!

**Three ways to use:**

1. **Simple:** `process_video.bat my_video.mp4`
2. **Advanced:** `python embed_subtitles.py my_video.mp4 -m small`
3. **Batch:** `python batch_process.py *.mp4`

**All videos get:**
✅ Perfect subtitles  
✅ AI-generated summary  
✅ Key insights  
✅ Quiz questions  
✅ Word document  

**100% local, 100% free, 100% private!** 🎉
