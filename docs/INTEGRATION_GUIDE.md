# 🔌 Integration Guide for Developers

How to integrate AI Video Assistant into your application

---

## 📦 Method 1: Python Package (Best for Python Apps)

### Installation

```bash
# Install from PyPI (after you publish)
pip install ai-video-assistant

# Or install from source
pip install git+https://github.com/yourusername/ai-video-assistant.git
```

### Usage in Python Code

```python
from ai_video_assistant import VideoAssistant

# Initialize
assistant = VideoAssistant(
    whisper_model="base",      # tiny/base/small/medium/large
    ollama_model="llama3.1",   # Any Ollama model
    output_dir="outputs"
)

# Process a video (full pipeline)
result = assistant.process_video(
    video_path="lecture.mp4",
    generate_subtitles=True,
    generate_word_doc=True,
    embed_subtitles=True
)

# Access results
print(result['transcription'])  # Full text
print(result['summary'])        # AI summary
print(result['insights'])       # List of key points
print(result['quiz'])           # Quiz questions

# File paths
print(result['srt_path'])              # Subtitle file
print(result['docx_path'])             # Word document
print(result['video_with_subtitles'])  # Subtitled video
```

### Quick Functions

```python
from ai_video_assistant import process_video, transcribe_video, analyze_lecture

# One-liner processing
result = process_video("lecture.mp4")

# Just transcription
transcript = transcribe_video("lecture.mp4")
print(transcript['text'])

# Analyze existing text
analysis = analyze_lecture("Long lecture text here...")
print(analysis['summary'])
```

---

## 🌐 Method 2: REST API (Best for Any Language)

### Start the API Server

```bash
python api_server.py
```

Server runs at: `http://localhost:8000`

### Integration Examples

#### JavaScript/TypeScript

```javascript
// Process a video
async function processVideo(videoFile) {
    const formData = new FormData();
    formData.append('video', videoFile);
    formData.append('whisper_model', 'base');
    formData.append('embed_subtitles', 'true');
    
    // Start processing
    const response = await fetch('http://localhost:8000/api/process', {
        method: 'POST',
        body: formData
    });
    
    const { job_id } = await response.json();
    
    // Poll for status
    while (true) {
        const statusResp = await fetch(`http://localhost:8000/api/status/${job_id}`);
        const status = await statusResp.json();
        
        if (status.status === 'complete') {
            return status.result;
        }
        
        if (status.status === 'error') {
            throw new Error(status.error);
        }
        
        await new Promise(r => setTimeout(r, 2000)); // Wait 2s
    }
}

// Usage
const result = await processVideo(videoFile);
console.log(result.summary);
```

#### React Component

```jsx
import React, { useState } from 'react';

function VideoProcessor() {
    const [result, setResult] = useState(null);
    const [processing, setProcessing] = useState(false);
    
    const handleUpload = async (e) => {
        const file = e.target.files[0];
        setProcessing(true);
        
        const formData = new FormData();
        formData.append('video', file);
        
        const res = await fetch('http://localhost:8000/api/process', {
            method: 'POST',
            body: formData
        });
        
        const { job_id } = await res.json();
        
        // Poll for completion
        const interval = setInterval(async () => {
            const statusRes = await fetch(`http://localhost:8000/api/status/${job_id}`);
            const data = await statusRes.json();
            
            if (data.status === 'complete') {
                clearInterval(interval);
                setResult(data.result);
                setProcessing(false);
            }
        }, 2000);
    };
    
    return (
        <div>
            <input type="file" onChange={handleUpload} accept="video/*" />
            {processing && <p>Processing...</p>}
            {result && (
                <div>
                    <h3>Summary:</h3>
                    <p>{result.summary}</p>
                    <h3>Insights:</h3>
                    <ul>
                        {result.insights.map((insight, i) => (
                            <li key={i}>{insight}</li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}
```

#### PHP

```php
<?php
// Upload and process video
$video_path = $_FILES['video']['tmp_name'];
$ch = curl_init('http://localhost:8000/api/process');

$formData = [
    'video' => new CURLFile($video_path),
    'whisper_model' => 'base'
];

curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, $formData);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

$response = json_decode(curl_exec($ch), true);
$job_id = $response['job_id'];

// Poll for status
do {
    sleep(2);
    $ch = curl_init("http://localhost:8000/api/status/$job_id");
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    $status = json_decode(curl_exec($ch), true);
} while ($status['status'] !== 'complete');

$result = $status['result'];
echo $result['summary'];
?>
```

#### Python (using API)

```python
import requests
import time

# Upload video
with open('lecture.mp4', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/process',
        files={'video': f},
        data={'whisper_model': 'base'}
    )

job_id = response.json()['job_id']

# Wait for completion
while True:
    status = requests.get(f'http://localhost:8000/api/status/{job_id}').json()
    
    if status['status'] == 'complete':
        result = status['result']
        break
    
    time.sleep(2)

print(result['summary'])
```

#### cURL

```bash
# Upload video
curl -X POST http://localhost:8000/api/process \
  -F "video=@lecture.mp4" \
  -F "whisper_model=base"

# Returns: {"job_id": "abc-123"}

# Check status
curl http://localhost:8000/api/status/abc-123

# Download results
curl http://localhost:8000/api/download/abc-123/srt -o subtitles.srt
curl http://localhost:8000/api/download/abc-123/docx -o analysis.docx
```

---

## 📱 Method 3: Docker Container

### Dockerfile

```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "api_server.py"]
```

### Usage

```bash
# Build
docker build -t ai-video-assistant .

# Run
docker run -p 8000:8000 -v $(pwd)/outputs:/app/outputs ai-video-assistant

# Use API at http://localhost:8000
```

---

## 🔧 Method 4: Electron Desktop App

```javascript
// main.js
const { app, BrowserWindow } = require('electron');
const { spawn } = require('child_process');

let pyProcess;

app.on('ready', () => {
    // Start Python API server
    pyProcess = spawn('python', ['api_server.py']);
    
    // Create window
    const win = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            nodeIntegration: true
        }
    });
    
    win.loadFile('index.html');
});

app.on('quit', () => {
    pyProcess.kill();
});
```

---

## API Reference

### POST /api/process

Process a video file.

**Request:**
```
POST /api/process
Content-Type: multipart/form-data

video: file
whisper_model: tiny|base|small|medium|large (optional)
generate_subtitles: true|false (optional)
generate_word_doc: true|false (optional)
embed_subtitles: true|false (optional)
```

**Response:**
```json
{
    "job_id": "uuid",
    "status": "processing"
}
```

### GET /api/status/{job_id}

Get job status.

**Response:**
```json
{
    "job_id": "uuid",
    "status": "processing|complete|error",
    "progress": 0-100,
    "result": {...}
}
```

### GET /api/result/{job_id}

Get complete result.

**Response:**
```json
{
    "transcription": "Full text...",
    "summary": "Summary...",
    "insights": ["insight1", "insight2"],
    "quiz": [
        {
            "question": "...",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "B"
        }
    ],
    "files": {
        "srt": "/api/download/uuid/srt",
        "docx": "/api/download/uuid/docx",
        "video": "/api/download/uuid/video"
    }
}
```

### POST /api/transcribe

Quick transcription (no AI analysis).

**Request:**
```
POST /api/transcribe
Content-Type: multipart/form-data

video: file
```

**Response:**
```json
{
    "text": "Full transcription...",
    "language": "en",
    "segments": [...]
}
```

### POST /api/analyze

Analyze text (no video).

**Request:**
```json
{
    "text": "Long lecture text..."
}
```

**Response:**
```json
{
    "summary": "...",
    "insights": [...],
    "quiz": [...]
}
```

---

## 💡 Use Cases

### Udemy Integration

```javascript
// Add "AI Analyze" button to Udemy lectures
async function analyzeLecture() {
    const videoUrl = document.querySelector('video').src;
    
    // Download video
    const blob = await fetch(videoUrl).then(r => r.blob());
    
    // Send to API
    const formData = new FormData();
    formData.append('video', blob, 'lecture.mp4');
    
    const result = await processVideo(formData);
    
    // Show summary
    showPopup(result.summary);
}
```

### LMS Integration (Moodle, Canvas)

```python
from ai_video_assistant import VideoAssistant

# Course video processor plugin
def process_course_video(video_id):
    video_path = get_video_path(video_id)
    
    assistant = VideoAssistant()
    result = assistant.process_video(video_path)
    
    # Store in LMS database
    save_to_database({
        'video_id': video_id,
        'summary': result['summary'],
        'quiz': result['quiz']
    })
    
    # Auto-generate quiz in LMS
    create_lms_quiz(result['quiz'])
```

### Mobile App Backend

```python
from flask import Flask
from ai_video_assistant import VideoAssistant

app = Flask(__name__)

@app.route('/mobile/process', methods=['POST'])
def mobile_process():
    video = request.files['video']
    assistant = VideoAssistant(whisper_model='tiny')  # Fast for mobile
    result = assistant.process_video(video)
    return jsonify(result)
```

---

## 🚀 Publishing Your Package

### PyPI (Python Package Index)

```bash
# Build package
python setup.py sdist bdist_wheel

# Upload to PyPI
pip install twine
twine upload dist/*

# Users install with:
pip install ai-video-assistant
```

### NPM (for JavaScript wrapper)

Create Node.js wrapper:

```javascript
// npm package: ai-video-assistant-js
const axios = require('axios');

class VideoAssistant {
    constructor(apiUrl = 'http://localhost:8000') {
        this.apiUrl = apiUrl;
    }
    
    async processVideo(videoFile) {
        // Implementation...
    }
}

module.exports = VideoAssistant;
```

---

**Now developers can integrate your AI Video Assistant into any application! 🎉**
