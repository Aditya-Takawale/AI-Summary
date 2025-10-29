"""
Test the ai-video-assistant library as an end user would
This script uses ONLY the installed pip package, not local files
"""

# Import from the installed package (not local files)
from ai_video_assistant import VideoAssistant

def test_library():
    print("=" * 60)
    print("🧪 Testing ai-video-assistant Library (v1.0.0)")
    print("📦 Using pip-installed package")
    print("=" * 60)
    print()
    
    # Initialize the assistant
    print("📌 Initializing VideoAssistant...")
    assistant = VideoAssistant()
    print("✅ VideoAssistant initialized successfully!")
    print()
    
    # Process test video 6
    video_path = r"C:\Developer\ai-summary\test_video_6.mp4"
    print(f"🎬 Processing video: {video_path}")
    print()
    
    # Run the full pipeline
    print("🚀 Starting analysis pipeline...")
    print("   - Extracting audio...")
    print("   - Transcribing with Whisper...")
    print("   - Analyzing with Ollama...")
    print("   - Generating subtitles...")
    print("   - Creating Word document...")
    print()
    
    result = assistant.process_video(video_path)
    
    # Display results
    print("=" * 60)
    print("✅ PROCESSING COMPLETE!")
    print("=" * 60)
    print()
    
    print("📄 TRANSCRIPTION:")
    print("-" * 60)
    print(result['transcription'][:500] + "..." if len(result['transcription']) > 500 else result['transcription'])
    print()
    
    print("📝 SUMMARY:")
    print("-" * 60)
    print(result['summary'])
    print()
    
    print("💡 KEY INSIGHTS:")
    print("-" * 60)
    for i, insight in enumerate(result['insights'], 1):
        print(f"{i}. {insight}")
    print()
    
    print("❓ QUIZ QUESTIONS:")
    print("-" * 60)
    for i, question in enumerate(result['quiz'], 1):
        print(f"\nQ{i}: {question['question']}")
        for opt in question['options']:
            print(f"   {opt}")
        print(f"   ✓ Answer: {question['answer']}")
    print()
    
    print("📂 OUTPUT FILES:")
    print("-" * 60)
    print(f"✅ Subtitles: {result['subtitle_file']}")
    print(f"✅ Word Doc: {result['word_doc']}")
    print(f"✅ Video with Subtitles: {result['video_with_subtitles']}")
    print()
    
    print("=" * 60)
    print("🎉 Library test completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    test_library()
