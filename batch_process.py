"""
Batch Video Processor
Process multiple videos at once
"""

import sys
import logging
from pathlib import Path
from embed_subtitles import process_and_embed_subtitles
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def batch_process_videos(
    video_paths: list,
    output_dir: str = "outputs",
    whisper_model: str = "base",
    ollama_model: str = "llama3.1",
    keep_srt: bool = True
):
    """
    Process multiple videos in batch.
    
    Args:
        video_paths: List of paths to video files
        output_dir: Output directory
        whisper_model: Whisper model size
        ollama_model: Ollama model name
        keep_srt: Whether to keep SRT files
    """
    total = len(video_paths)
    successful = []
    failed = []
    
    print("\n" + "=" * 70)
    print(f"📹 BATCH VIDEO PROCESSOR - {total} videos")
    print("=" * 70 + "\n")
    
    start_time = time.time()
    
    for i, video_path in enumerate(video_paths, 1):
        video_path = Path(video_path)
        
        if not video_path.exists():
            logger.error(f"Video not found: {video_path}")
            failed.append((str(video_path), "File not found"))
            continue
        
        print(f"\n{'=' * 70}")
        print(f"Processing {i}/{total}: {video_path.name}")
        print(f"{'=' * 70}\n")
        
        try:
            output = process_and_embed_subtitles(
                video_path=str(video_path),
                output_dir=output_dir,
                whisper_model=whisper_model,
                ollama_model=ollama_model,
                keep_srt=keep_srt
            )
            
            if output:
                successful.append(str(video_path))
                logger.info(f"✅ Successfully processed {video_path.name}")
            else:
                failed.append((str(video_path), "Processing failed"))
                logger.error(f"❌ Failed to process {video_path.name}")
        
        except Exception as e:
            failed.append((str(video_path), str(e)))
            logger.error(f"❌ Error processing {video_path.name}: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary
    elapsed = time.time() - start_time
    hours = int(elapsed // 3600)
    minutes = int((elapsed % 3600) // 60)
    seconds = int(elapsed % 60)
    
    print("\n" + "=" * 70)
    print("📊 BATCH PROCESSING SUMMARY")
    print("=" * 70)
    print(f"Total videos: {total}")
    print(f"✅ Successful: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")
    print(f"⏱️  Total time: {hours}h {minutes}m {seconds}s")
    print("=" * 70)
    
    if successful:
        print("\n✅ Successfully processed:")
        for video in successful:
            print(f"   - {Path(video).name}")
    
    if failed:
        print("\n❌ Failed to process:")
        for video, error in failed:
            print(f"   - {Path(video).name}")
            print(f"     Error: {error}")
    
    print("\n" + "=" * 70 + "\n")
    
    return successful, failed


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Batch Video Processor - Process multiple videos at once",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process all MP4 files in a folder
  python batch_process.py videos/*.mp4
  
  # Process specific videos
  python batch_process.py video1.mp4 video2.mp4 video3.mp4
  
  # Use different model
  python batch_process.py *.mp4 -m small --ollama-model llama3.2
        """
    )
    
    parser.add_argument("videos", nargs='+', help="Video files to process")
    parser.add_argument("-o", "--output-dir", default="outputs",
                        help="Output directory (default: outputs)")
    parser.add_argument("-m", "--whisper-model", default="base",
                        choices=["tiny", "base", "small", "medium", "large"],
                        help="Whisper model size (default: base)")
    parser.add_argument("--ollama-model", default="llama3.1",
                        help="Ollama model name (default: llama3.1)")
    parser.add_argument("--no-srt", action="store_true",
                        help="Don't keep SRT files after embedding")
    
    args = parser.parse_args()
    
    # Expand wildcards and get all video files
    video_paths = []
    for pattern in args.videos:
        if '*' in pattern or '?' in pattern:
            # Handle wildcards
            from glob import glob
            video_paths.extend(glob(pattern))
        else:
            video_paths.append(pattern)
    
    if not video_paths:
        print("❌ No video files found!")
        return
    
    # Remove duplicates
    video_paths = list(set(video_paths))
    
    print(f"\n📹 Found {len(video_paths)} video(s) to process")
    
    # Process all videos
    successful, failed = batch_process_videos(
        video_paths=video_paths,
        output_dir=args.output_dir,
        whisper_model=args.whisper_model,
        ollama_model=args.ollama_model,
        keep_srt=not args.no_srt
    )
    
    # Exit code
    sys.exit(0 if len(failed) == 0 else 1)


if __name__ == "__main__":
    main()
