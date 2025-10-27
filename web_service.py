"""
Web Service for AI Video Lecture Assistant
Students can upload videos via browser and get analysis
"""

from flask import Flask, request, render_template, send_file, jsonify
from werkzeug.utils import secure_filename
import os
from pathlib import Path
from embed_subtitles import process_and_embed_subtitles
import threading
import uuid

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max

# Store processing status
processing_jobs = {}

os.makedirs('uploads', exist_ok=True)
os.makedirs('outputs', exist_ok=True)


@app.route('/')
def index():
    """Home page with upload form."""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Video Lecture Assistant</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 { color: #333; }
            .upload-area {
                border: 2px dashed #4CAF50;
                padding: 40px;
                text-align: center;
                border-radius: 10px;
                margin: 20px 0;
            }
            button {
                background: #4CAF50;
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
            }
            button:hover { background: #45a049; }
            .features {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin-top: 30px;
            }
            .feature {
                padding: 15px;
                background: #f9f9f9;
                border-radius: 5px;
            }
            .status {
                margin-top: 20px;
                padding: 15px;
                background: #e3f2fd;
                border-radius: 5px;
                display: none;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎬 AI Video Lecture Assistant</h1>
            <p>Upload your lecture video and get AI-powered study materials!</p>
            
            <div class="upload-area">
                <h3>📹 Upload Video</h3>
                <form id="uploadForm" enctype="multipart/form-data">
                    <input type="file" name="video" accept="video/*" required>
                    <br><br>
                    <button type="submit">🚀 Process Video</button>
                </form>
            </div>
            
            <div id="status" class="status">
                <h3>⏳ Processing...</h3>
                <p id="statusText">Uploading video...</p>
                <div style="background: #ddd; height: 20px; border-radius: 10px;">
                    <div id="progressBar" style="background: #4CAF50; height: 100%; width: 0%; border-radius: 10px; transition: width 0.3s;"></div>
                </div>
            </div>
            
            <div class="features">
                <div class="feature">
                    <h4>📝 Full Transcription</h4>
                    <p>99+ language support with timestamps</p>
                </div>
                <div class="feature">
                    <h4>📊 AI Summary</h4>
                    <p>Concise summary of key points</p>
                </div>
                <div class="feature">
                    <h4>💡 Key Insights</h4>
                    <p>5-7 important takeaways</p>
                </div>
                <div class="feature">
                    <h4>❓ Quiz Questions</h4>
                    <p>5 multiple-choice questions</p>
                </div>
                <div class="feature">
                    <h4>🎬 Subtitled Video</h4>
                    <p>Video with toggleable subtitles</p>
                </div>
                <div class="feature">
                    <h4>📄 Word Document</h4>
                    <p>Professional study guide</p>
                </div>
            </div>
        </div>
        
        <script>
            document.getElementById('uploadForm').onsubmit = async (e) => {
                e.preventDefault();
                
                const formData = new FormData(e.target);
                const statusDiv = document.getElementById('status');
                const statusText = document.getElementById('statusText');
                const progressBar = document.getElementById('progressBar');
                
                statusDiv.style.display = 'block';
                statusText.textContent = 'Uploading video...';
                progressBar.style.width = '10%';
                
                try {
                    const response = await fetch('/upload', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const data = await response.json();
                    
                    if (data.job_id) {
                        statusText.textContent = 'Processing video...';
                        progressBar.style.width = '30%';
                        
                        // Poll for status
                        const interval = setInterval(async () => {
                            const statusResp = await fetch(`/status/${data.job_id}`);
                            const statusData = await statusResp.json();
                            
                            statusText.textContent = statusData.status;
                            
                            if (statusData.progress) {
                                progressBar.style.width = statusData.progress + '%';
                            }
                            
                            if (statusData.complete) {
                                clearInterval(interval);
                                statusText.innerHTML = `
                                    <h3>✅ Processing Complete!</h3>
                                    <a href="/download/${data.job_id}/video" style="display: inline-block; margin: 10px; padding: 10px 20px; background: #4CAF50; color: white; text-decoration: none; border-radius: 5px;">📹 Download Video</a>
                                    <a href="/download/${data.job_id}/docx" style="display: inline-block; margin: 10px; padding: 10px 20px; background: #2196F3; color: white; text-decoration: none; border-radius: 5px;">📄 Download Analysis</a>
                                    <a href="/download/${data.job_id}/srt" style="display: inline-block; margin: 10px; padding: 10px 20px; background: #FF9800; color: white; text-decoration: none; border-radius: 5px;">📝 Download Subtitles</a>
                                `;
                                progressBar.style.width = '100%';
                            }
                            
                            if (statusData.error) {
                                clearInterval(interval);
                                statusText.textContent = '❌ Error: ' + statusData.error;
                            }
                        }, 2000);
                    }
                } catch (error) {
                    statusText.textContent = '❌ Upload failed: ' + error.message;
                }
            };
        </script>
    </body>
    </html>
    '''


@app.route('/upload', methods=['POST'])
def upload_video():
    """Handle video upload and start processing."""
    if 'video' not in request.files:
        return jsonify({'error': 'No video file'}), 400
    
    video = request.files['video']
    
    if video.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Generate unique job ID
    job_id = str(uuid.uuid4())
    
    # Save uploaded file
    filename = secure_filename(video.filename)
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{job_id}_{filename}")
    video.save(video_path)
    
    # Start processing in background
    processing_jobs[job_id] = {
        'status': 'Processing...',
        'progress': 0,
        'complete': False,
        'error': None,
        'video_path': video_path,
        'output_files': {}
    }
    
    thread = threading.Thread(target=process_video_job, args=(job_id, video_path))
    thread.daemon = True
    thread.start()
    
    return jsonify({'job_id': job_id})


def process_video_job(job_id, video_path):
    """Process video in background thread."""
    try:
        processing_jobs[job_id]['status'] = 'Extracting audio...'
        processing_jobs[job_id]['progress'] = 20
        
        # Process video
        output_path = process_and_embed_subtitles(
            video_path=video_path,
            output_dir='outputs',
            whisper_model='base',
            ollama_model='llama3.1',
            keep_srt=True
        )
        
        processing_jobs[job_id]['progress'] = 90
        
        # Store output paths
        video_name = Path(video_path).stem.replace(job_id + '_', '')
        processing_jobs[job_id]['output_files'] = {
            'video': f"outputs/{video_name}_with_subtitles.mp4",
            'docx': f"outputs/{video_name}_analysis.docx",
            'srt': f"outputs/{video_name}_subtitles.srt",
            'json': f"outputs/{video_name}_analysis.json"
        }
        
        processing_jobs[job_id]['status'] = 'Complete!'
        processing_jobs[job_id]['progress'] = 100
        processing_jobs[job_id]['complete'] = True
        
    except Exception as e:
        processing_jobs[job_id]['error'] = str(e)
        processing_jobs[job_id]['status'] = f'Error: {str(e)}'


@app.route('/status/<job_id>')
def get_status(job_id):
    """Get processing status."""
    if job_id not in processing_jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify(processing_jobs[job_id])


@app.route('/download/<job_id>/<file_type>')
def download_file(job_id, file_type):
    """Download processed files."""
    if job_id not in processing_jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = processing_jobs[job_id]
    
    if not job['complete']:
        return jsonify({'error': 'Processing not complete'}), 400
    
    if file_type not in job['output_files']:
        return jsonify({'error': 'File type not found'}), 404
    
    file_path = job['output_files'][file_type]
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(file_path, as_attachment=True)


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🎬 AI Video Lecture Assistant - Web Service")
    print("=" * 60)
    print("\n📍 Access at: http://localhost:5000")
    print("\n💡 Students can upload videos via browser")
    print("   and download subtitled videos + study materials!")
    print("\n⚠️  Note: Make sure Ollama is running!")
    print("=" * 60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
