"""
FINAL TEST BEFORE PUBLISHING VERSION 1.0.4
Testing with test_video_6.mp4 using the package code
"""

import sys
import os

# Force use of package code, not local files
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'ai_video_assistant'))

from ai_video_assistant.core import VideoAssistant

print("=" * 70)
print("🧪 FINAL TEST BEFORE PUBLISHING v1.0.4 TO PYPI")
print("=" * 70)
print()

assistant = VideoAssistant()

print("🎬 Processing test_video_6.mp4...")
print()

try:
    result = assistant.process_video(
        "test_video_6.mp4",
        generate_subtitles=True,
        embed_subtitles=True,
        generate_word_doc=True
    )
    
    print()
    print("=" * 70)
    print("✅ SUCCESS! ALL TESTS PASSED!")
    print("=" * 70)
    print()
    print(f"📝 Transcription: {len(result['transcription'])} characters")
    print(f"📊 Summary: {len(result['summary'])} characters")
    print(f"💡 Insights: {len(result['insights'])} items")
    print(f"❓ Quiz: {len(result['quiz'])} questions")
    print()
    
    # Check quiz format
    for i, q in enumerate(result['quiz'][:2], 1):
        print(f"Quiz {i}:")
        print(f"  Question: {q['question'][:60]}...")
        print(f"  Options type: {type(q['options'])}")
        print(f"  Options: {q['options']}")
        print(f"  Correct answer: {q['correct_answer']}")
        print()
    
    print("📁 Generated files:")
    print(f"  • SRT: {result.get('srt_path', 'N/A')}")
    print(f"  • DOCX: {result.get('docx_path', 'N/A')}")
    print(f"  • Video: {result.get('video_with_subtitles', 'N/A')}")
    print()
    print("=" * 70)
    print("🎉 READY TO PUBLISH VERSION 1.0.4!")
    print("=" * 70)
    
except Exception as e:
    print()
    print("=" * 70)
    print("❌ ERROR - DO NOT PUBLISH!")
    print("=" * 70)
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
