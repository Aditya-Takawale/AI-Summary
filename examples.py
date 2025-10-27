"""
Example script demonstrating how to use individual modules.
"""

import os
from dotenv import load_dotenv

# Import the modules
from audio_extractor import AudioExtractor
from transcriber import AudioTranscriber
from content_analyzer import ContentAnalyzer

# Load environment variables
load_dotenv()


def example_audio_extraction():
    """Example: Extract audio from a video file."""
    print("\n=== Example: Audio Extraction ===")
    
    extractor = AudioExtractor(temp_dir="temp_audio")
    
    # Extract audio from video
    video_path = "path/to/your/video.mp4"
    audio_path = extractor.extract_audio(video_path, output_format="wav")
    
    print(f"Audio extracted to: {audio_path}")
    
    # Cleanup when done
    # extractor.cleanup(audio_path)


def example_transcription():
    """Example: Transcribe an audio file."""
    print("\n=== Example: Audio Transcription ===")
    
    transcriber = AudioTranscriber(model_size="base")
    
    # Transcribe audio file
    audio_path = "temp_audio/lecture_audio.wav"
    result = transcriber.transcribe(audio_path)
    
    print(f"Language detected: {result['language']}")
    print(f"Transcription length: {len(result['text'])} characters")
    print(f"First 200 characters: {result['text'][:200]}...")
    
    # Save to file
    transcription_path = transcriber.transcribe_to_file(audio_path, "transcription.txt")
    print(f"Saved to: {transcription_path}")


def example_timestamped_transcription():
    """Example: Get transcription with timestamps."""
    print("\n=== Example: Timestamped Transcription ===")
    
    transcriber = AudioTranscriber(model_size="base")
    
    audio_path = "temp_audio/lecture_audio.wav"
    segments = transcriber.get_timestamped_transcription(audio_path)
    
    # Print first 3 segments
    for i, segment in enumerate(segments[:3], 1):
        print(f"\nSegment {i}:")
        print(f"  Time: {segment['start']:.2f}s - {segment['end']:.2f}s")
        print(f"  Text: {segment['text']}")


def example_content_analysis():
    """Example: Analyze transcription with AI."""
    print("\n=== Example: Content Analysis ===")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in .env file")
        return
    
    analyzer = ContentAnalyzer(api_key=api_key)
    
    # Example transcription (replace with actual transcription)
    transcription = """
    In today's lecture, we'll discuss the fundamentals of machine learning.
    Machine learning is a subset of artificial intelligence that enables
    computers to learn from data without being explicitly programmed.
    There are three main types of machine learning: supervised learning,
    unsupervised learning, and reinforcement learning...
    """
    
    # Analyze the content
    result = analyzer.analyze(transcription)
    
    print("\nSummary:")
    print(result["summary"])
    
    print("\nInsights:")
    for i, insight in enumerate(result["insights"], 1):
        print(f"{i}. {insight}")
    
    print("\nQuiz:")
    for i, q in enumerate(result["quiz"], 1):
        print(f"\nQ{i}: {q['question']}")
        for j, opt in enumerate(q['options'], 1):
            marker = "✓" if opt == q['correct_answer'] else " "
            print(f"  [{marker}] {j}. {opt}")
    
    # Save to file
    analyzer.analyze_and_save(transcription, "analysis_result.json")


def example_complete_pipeline():
    """Example: Complete pipeline from video to analysis."""
    print("\n=== Example: Complete Pipeline ===")
    
    from main import VideoLectureAssistant
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found in .env file")
        return
    
    assistant = VideoLectureAssistant(
        gemini_api_key=api_key,
        whisper_model="base"
    )
    
    # Process a video file
    video_path = "path/to/your/video.mp4"
    result = assistant.process_video(
        video_path=video_path,
        output_name="my_lecture",
        save_transcription=True,
        cleanup_audio=True
    )
    
    # Print formatted summary
    assistant.print_summary(result)
    
    print(f"\nFull results saved to: {result['output_file']}")


if __name__ == "__main__":
    print("AI-Powered Video Lecture Assistant - Examples")
    print("=" * 60)
    
    # Uncomment the examples you want to run:
    
    # example_audio_extraction()
    # example_transcription()
    # example_timestamped_transcription()
    # example_content_analysis()
    # example_complete_pipeline()
    
    print("\n" + "=" * 60)
    print("Uncomment the examples you want to run in examples.py")
