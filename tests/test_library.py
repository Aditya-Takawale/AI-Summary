"""
Test the published ai-video-assistant library
Using ONLY the pip-installed package, not local files
"""

from ai_video_assistant import VideoAssistant

print("=" * 70)
print("🧪 TESTING AI-VIDEO-ASSISTANT LIBRARY (from PyPI)")
print("=" * 70)
print()

# Initialize the assistant
assistant = VideoAssistant()

# Process test_video_6.mp4
video_path = r"C:\Developer\ai-summary\test_video_6.mp4"

print(f"📹 Processing: {video_path}")
print()

# Process the video
result = assistant.process_video(video_path)

print()
print("=" * 70)
print("✅ PROCESSING COMPLETE!")
print("=" * 70)
print()

# Display results
print("📝 TRANSCRIPTION:")
print("-" * 70)
print(result['transcription'][:500] + "..." if len(result['transcription']) > 500 else result['transcription'])
print()

print("📊 SUMMARY:")
print("-" * 70)
print(result['summary'])
print()

print("💡 KEY INSIGHTS:")
print("-" * 70)
for i, insight in enumerate(result['insights'], 1):
    print(f"{i}. {insight}")
print()

print("❓ QUIZ QUESTIONS:")
print("-" * 70)
for i, q in enumerate(result['quiz'], 1):
    print(f"\nQ{i}. {q['question']}")
    for opt_key, opt_val in q['options'].items():
        print(f"   {opt_key}) {opt_val}")
    print(f"   ✓ Answer: {q['correct_answer']}")
print()

print("📁 FILES GENERATED:")
print("-" * 70)
print(f"• Word Document: {result['word_doc']}")
print(f"• SRT Subtitles: {result['srt_file']}")
print(f"• Video with Subtitles: {result['video_with_subtitles']}")
print()

print("=" * 70)
print("🎉 LIBRARY TEST SUCCESSFUL!")
print("=" * 70)
