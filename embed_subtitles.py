"""
Embed Subtitles into Video
Creates a new video file with embedded subtitle track that can be toggled on/off in any video player
"""

import subprocess
from pathlib import Path
import logging
from typing import Optional

from audio_extractor import AudioExtractor
from transcriber import AudioTranscriber
from content_analyzer_ollama import OllamaContentAnalyzer
from subtitle_generator import generate_srt
from word_generator import generate_word_document
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def find_ffmpeg() -> Optional[str]:
    """Find FFmpeg executable."""
    try:
        # Try system ffmpeg
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, 
                              text=True,
                              timeout=5)
        if result.returncode == 0:
            return 'ffmpeg'
    except:
        pass
    
    # Try imageio ffmpeg
    try:
        import imageio_ffmpeg
        ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
        if Path(ffmpeg_path).exists():
            return ffmpeg_path
    except:
        pass
    
    return None


def embed_subtitles_in_video(video_path: str, srt_path: str, output_path: str) -> bool:
    """
    Embed SRT subtitles into video file using FFmpeg.
    Creates a new video with subtitle track that can be toggled in players.
    
    Args:
        video_path: Path to original video file
        srt_path: Path to SRT subtitle file
        output_path: Path for output video with embedded subtitles
    
    Returns:
        True if successful, False otherwise
    """
    ffmpeg_exe = find_ffmpeg()
    
    if not ffmpeg_exe:
        logger.error("FFmpeg not found. Please install FFmpeg.")
        return False
    
    logger.info(f"Using FFmpeg: {ffmpeg_exe}")
    logger.info(f"Embedding subtitles from {srt_path} into {video_path}")
    logger.info(f"Output will be saved to: {output_path}")
    
    # FFmpeg command to embed subtitles as a track (not burned in)
    # This allows toggling subtitles on/off in video players
    cmd = [
        ffmpeg_exe,
        '-i', video_path,           # Input video
        '-i', srt_path,              # Input subtitle file
        '-c:v', 'copy',              # Copy video stream (no re-encoding)
        '-c:a', 'copy',              # Copy audio stream (no re-encoding)
        '-c:s', 'mov_text',          # Subtitle codec for MP4
        '-metadata:s:s:0', 'language=eng',  # Set subtitle language
        '-metadata:s:s:0', 'title=English',  # Set subtitle title
        '-y',                        # Overwrite output file
        output_path
    ]
    
    try:
        logger.info("Running FFmpeg (this may take a moment)...")
        logger.info(f"Command: {' '.join(cmd)}")
        
        process = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if process.returncode == 0:
            logger.info(f"✅ Success! Video with embedded subtitles saved to: {output_path}")
            logger.info(f"   You can now open this video in VLC, Windows Media Player, etc.")
            logger.info(f"   and toggle subtitles on/off using the player's subtitle menu!")
            return True
        else:
            logger.error(f"FFmpeg failed with return code {process.returncode}")
            logger.error(f"Error output: {process.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("FFmpeg process timed out after 5 minutes")
        return False
    except Exception as e:
        logger.error(f"Error running FFmpeg: {e}")
        import traceback
        traceback.print_exc()
        return False


def process_and_embed_subtitles(
    video_path: str,
    output_dir: str = "outputs",
    whisper_model: str = "base",
    ollama_model: str = "llama3.1",
    keep_srt: bool = True
) -> Optional[str]:
    """
    Complete pipeline: Extract audio, transcribe, analyze, generate subtitles, and embed them.
    
    Args:
        video_path: Path to input video file
        output_dir: Directory for output files
        whisper_model: Whisper model size
        ollama_model: Ollama model name
        keep_srt: Whether to keep the SRT file after embedding
    
    Returns:
        Path to output video with embedded subtitles, or None if failed
    """
    video_path = Path(video_path)
    outputs_dir = Path(output_dir)
    outputs_dir.mkdir(exist_ok=True)
    
    video_name = video_path.stem
    
    print("\n" + "=" * 70)
    print("🎬 AI VIDEO SUBTITLE EMBEDDER")
    print("=" * 70)
    print(f"Video: {video_path.name}")
    print(f"Output directory: {outputs_dir}")
    print("=" * 70 + "\n")
    
    # Step 1: Extract audio
    print("📀 Step 1/5: Extracting audio from video...")
    extractor = AudioExtractor()
    audio_path = extractor.extract_audio(str(video_path), output_format="wav")
    print(f"   ✅ Audio extracted to: {audio_path}\n")
    
    # Step 2: Transcribe with Whisper
    print(f"🎤 Step 2/5: Transcribing audio (using Whisper '{whisper_model}' model)...")
    print("   This may take a few minutes depending on video length...")
    transcriber = AudioTranscriber(model_size=whisper_model)
    transcription_result = transcriber.transcribe(audio_path)
    
    segments = transcription_result.get('segments', [])
    language = transcription_result.get('language', 'unknown')
    
    print(f"   ✅ Transcription complete!")
    print(f"   Language detected: {language}")
    print(f"   Segments: {len(segments)}")
    print(f"   Total words: ~{len(transcription_result['text'].split())}\n")
    
    # Step 3: AI Analysis
    print(f"🤖 Step 3/5: Analyzing content with AI (using Ollama '{ollama_model}')...")
    analyzer = OllamaContentAnalyzer(model=ollama_model)
    analysis_result = analyzer.analyze(transcription_result['text'])
    print(f"   ✅ Analysis complete!")
    print(f"   Summary: {len(analysis_result['summary'])} chars")
    print(f"   Insights: {len(analysis_result['insights'])} items")
    print(f"   Quiz questions: {len(analysis_result['quiz'])} questions\n")
    
    # Save analysis results
    final_result = {
        "video_file": video_path.name,
        "language": language,
        "transcription": transcription_result['text'],
        "summary": analysis_result["summary"],
        "insights": analysis_result["insights"],
        "quiz": analysis_result["quiz"]
    }
    
    json_path = outputs_dir / f"{video_name}_analysis.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(final_result, f, indent=2, ensure_ascii=False)
    print(f"   💾 Analysis saved to: {json_path}")
    
    # Generate Word document
    word_path = outputs_dir / f"{video_name}_analysis.docx"
    generate_word_document(final_result, str(word_path))
    print(f"   📄 Word document saved to: {word_path}\n")
    
    # Step 4: Generate SRT subtitle file
    print("📝 Step 4/5: Generating SRT subtitle file...")
    srt_path = outputs_dir / f"{video_name}_subtitles.srt"
    generate_srt(segments, str(srt_path))
    print(f"   ✅ SRT file created: {srt_path}")
    print(f"   You can use this with any video player that supports external subtitles!\n")
    
    # Step 5: Embed subtitles into video
    print("🎥 Step 5/5: Embedding subtitles into video file...")
    output_video_path = outputs_dir / f"{video_name}_with_subtitles.mp4"
    
    success = embed_subtitles_in_video(
        str(video_path),
        str(srt_path),
        str(output_video_path)
    )
    
    if success:
        print("\n" + "=" * 70)
        print("✅ SUCCESS! Your video is ready!")
        print("=" * 70)
        print(f"📹 Video with embedded subtitles: {output_video_path}")
        print(f"📝 Standalone SRT file: {srt_path}")
        print(f"📄 Analysis document: {word_path}")
        print(f"📊 Analysis JSON: {json_path}")
        print("=" * 70)
        print("\n💡 HOW TO USE:")
        print("   1. Open the video in VLC, Windows Media Player, or any video player")
        print("   2. Look for 'Subtitles' or 'CC' button in the player controls")
        print("   3. Toggle subtitles ON/OFF as you prefer!")
        print("   4. Subtitles are perfectly synced with audio ✨")
        print("=" * 70 + "\n")
        
        if not keep_srt:
            srt_path.unlink()
            print(f"   🗑️  Removed temporary SRT file")
        
        return str(output_video_path)
    else:
        print("\n❌ Failed to embed subtitles into video")
        print(f"   But the SRT file is available at: {srt_path}")
        print(f"   You can manually load it in your video player!")
        return None


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="AI Video Subtitle Embedder - Transcribe, analyze, and embed subtitles into video",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process video and embed subtitles
  python embed_subtitles.py my_lecture.mp4
  
  # Use different Whisper model for better accuracy
  python embed_subtitles.py my_lecture.mp4 -m small
  
  # Specify output directory
  python embed_subtitles.py my_lecture.mp4 -o my_outputs
  
  # Keep SRT file after embedding
  python embed_subtitles.py my_lecture.mp4 --keep-srt
        """
    )
    
    parser.add_argument("video_path", type=str, help="Path to video file")
    parser.add_argument("-o", "--output-dir", type=str, default="outputs",
                        help="Output directory (default: outputs)")
    parser.add_argument("-m", "--whisper-model", type=str, default="base",
                        choices=["tiny", "base", "small", "medium", "large"],
                        help="Whisper model size (default: base)")
    parser.add_argument("--ollama-model", type=str, default="llama3.1",
                        help="Ollama model name (default: llama3.1)")
    parser.add_argument("--keep-srt", action="store_true",
                        help="Keep SRT file after embedding")
    
    args = parser.parse_args()
    
    # Check if video exists
    if not Path(args.video_path).exists():
        print(f"❌ Error: Video file not found: {args.video_path}")
        return
    
    # Process video
    output_path = process_and_embed_subtitles(
        video_path=args.video_path,
        output_dir=args.output_dir,
        whisper_model=args.whisper_model,
        ollama_model=args.ollama_model,
        keep_srt=args.keep_srt
    )
    
    if output_path:
        print(f"\n🎉 All done! Open {Path(output_path).name} in your favorite video player!")


if __name__ == "__main__":
    main()
