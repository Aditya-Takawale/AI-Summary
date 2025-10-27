"""
REST API Server for AI Video Assistant
Allows any application to integrate via HTTP requests
"""

from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import sys
from pathlib import Path
import uuid
import threading

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from ai_video_assistant.core import VideoAssistant

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024  # 1GB max
app.config['UPLOAD_FOLDER'] = 'api_uploads'
app.config['OUTPUT_FOLDER'] = 'api_outputs'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Store processing jobs
jobs = {}


@app.route('/api/health', methods=['GET'])
def health_check():
    """Check if API is running and Ollama is available."""
    try:
        import requests
        response = requests.get('http://localhost:11434/api/tags', timeout=2)
        ollama_status = 'running' if response.status_code == 200 else 'error'
    except:
        ollama_status = 'not_running'
    
    return jsonify({
        'status': 'ok',
        'version': '1.0.0',
        'ollama': ollama_status,
        'gpu_available': _check_gpu()
    })


@app.route('/api/process', methods=['POST'])
def process_video_api():
    """
    Process a video file.
    
    Request:
        POST /api/process
        Content-Type: multipart/form-data
        
        Fields:
            - video: Video file
            - whisper_model: (optional) tiny/base/small/medium/large
            - generate_subtitles: (optional) true/false
            - generate_word_doc: (optional) true/false
            - embed_subtitles: (optional) true/false
    
    Response:
        {
            "job_id": "uuid",
            "status": "processing"
        }
    """
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    video = request.files['video']
    if video.filename == '':
        return jsonify({'error': 'Empty filename'}), 400
    
    # Parse options
    options = {
        'whisper_model': request.form.get('whisper_model', 'base'),
        'generate_subtitles': request.form.get('generate_subtitles', 'true').lower() == 'true',
        'generate_word_doc': request.form.get('generate_word_doc', 'true').lower() == 'true',
        'embed_subtitles': request.form.get('embed_subtitles', 'false').lower() == 'true'
    }
    
    # Save video
    job_id = str(uuid.uuid4())
    filename = secure_filename(video.filename)
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{job_id}_{filename}")
    video.save(video_path)
    
    # Start processing in background
    jobs[job_id] = {
        'status': 'processing',
        'progress': 0,
        'result': None,
        'error': None
    }
    
    thread = threading.Thread(
        target=_process_video_background,
        args=(job_id, video_path, options)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({'job_id': job_id, 'status': 'processing'}), 202


@app.route('/api/status/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """
    Get processing status.
    
    Response:
        {
            "job_id": "uuid",
            "status": "processing|complete|error",
            "progress": 0-100,
            "result": {...} (if complete),
            "error": "..." (if error)
        }
    """
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify({
        'job_id': job_id,
        **jobs[job_id]
    })


@app.route('/api/result/<job_id>', methods=['GET'])
def get_result(job_id):
    """
    Get processing result.
    
    Response:
        {
            "transcription": "...",
            "summary": "...",
            "insights": [...],
            "quiz": [...],
            "files": {
                "srt": "url",
                "docx": "url",
                "video": "url"
            }
        }
    """
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = jobs[job_id]
    
    if job['status'] != 'complete':
        return jsonify({'error': 'Job not complete'}), 400
    
    return jsonify(job['result'])


@app.route('/api/download/<job_id>/<file_type>', methods=['GET'])
def download_file(job_id, file_type):
    """
    Download generated files.
    
    file_type: srt | docx | video
    """
    if job_id not in jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = jobs[job_id]
    
    if job['status'] != 'complete':
        return jsonify({'error': 'Job not complete'}), 400
    
    result = job['result']
    
    if file_type == 'srt' and 'srt_path' in result:
        return send_file(result['srt_path'], as_attachment=True)
    elif file_type == 'docx' and 'docx_path' in result:
        return send_file(result['docx_path'], as_attachment=True)
    elif file_type == 'video' and 'video_with_subtitles' in result:
        return send_file(result['video_with_subtitles'], as_attachment=True)
    else:
        return jsonify({'error': 'File not found'}), 404


@app.route('/api/transcribe', methods=['POST'])
def transcribe_only():
    """
    Transcribe video only (no AI analysis).
    
    Response:
        {
            "text": "...",
            "language": "en",
            "segments": [...]
        }
    """
    if 'video' not in request.files:
        return jsonify({'error': 'No video file'}), 400
    
    video = request.files['video']
    job_id = str(uuid.uuid4())
    filename = secure_filename(video.filename)
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{job_id}_{filename}")
    video.save(video_path)
    
    try:
        assistant = VideoAssistant()
        result = assistant.transcribe_only(video_path)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # Cleanup
        if os.path.exists(video_path):
            os.remove(video_path)


@app.route('/api/analyze', methods=['POST'])
def analyze_text():
    """
    Analyze text only (no video).
    
    Request:
        {
            "text": "Long lecture text..."
        }
    
    Response:
        {
            "summary": "...",
            "insights": [...],
            "quiz": [...]
        }
    """
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400
    
    try:
        assistant = VideoAssistant()
        result = assistant.analyze_text(data['text'])
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def _process_video_background(job_id, video_path, options):
    """Process video in background thread."""
    try:
        jobs[job_id]['progress'] = 10
        
        assistant = VideoAssistant(
            whisper_model=options['whisper_model'],
            output_dir=app.config['OUTPUT_FOLDER']
        )
        
        jobs[job_id]['progress'] = 30
        
        result = assistant.process_video(
            video_path,
            generate_subtitles=options['generate_subtitles'],
            generate_word_doc=options['generate_word_doc'],
            embed_subtitles=options['embed_subtitles']
        )
        
        jobs[job_id]['progress'] = 90
        
        # Add download URLs
        result['files'] = {}
        if 'srt_path' in result:
            result['files']['srt'] = f"/api/download/{job_id}/srt"
        if 'docx_path' in result:
            result['files']['docx'] = f"/api/download/{job_id}/docx"
        if 'video_with_subtitles' in result:
            result['files']['video'] = f"/api/download/{job_id}/video"
        
        jobs[job_id]['status'] = 'complete'
        jobs[job_id]['progress'] = 100
        jobs[job_id]['result'] = result
        
    except Exception as e:
        jobs[job_id]['status'] = 'error'
        jobs[job_id]['error'] = str(e)


def _check_gpu():
    """Check if GPU is available."""
    try:
        import torch
        return torch.cuda.is_available()
    except:
        return False


if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("🚀 AI Video Assistant - REST API Server")
    print("=" * 70)
    print("\n📍 API Base URL: http://localhost:8000/api")
    print("\nEndpoints:")
    print("  GET  /api/health             - Health check")
    print("  POST /api/process            - Process video (async)")
    print("  GET  /api/status/<job_id>    - Get job status")
    print("  GET  /api/result/<job_id>    - Get results")
    print("  GET  /api/download/<job_id>/<type> - Download files")
    print("  POST /api/transcribe         - Quick transcribe")
    print("  POST /api/analyze            - Analyze text")
    print("\n⚠️  Make sure Ollama is running: ollama serve")
    print("=" * 70 + "\n")
    
    app.run(host='0.0.0.0', port=8000, debug=False)
