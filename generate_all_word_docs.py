"""
Generate Word documents for all processed videos
"""
import json
from pathlib import Path
from word_generator import generate_word_document

# Define the outputs directory
outputs_dir = Path("outputs")

# List of video analysis files
video_files = [
    "test_video_1_analysis.json",
    "test_video_2_analysis.json",
    "test_video_3_analysis.json"
]

print("Generating Word documents for all videos...\n")

for video_file in video_files:
    json_path = outputs_dir / video_file
    
    if json_path.exists():
        # Read the JSON file
        with open(json_path, 'r', encoding='utf-8') as f:
            result = json.load(f)
        
        # Generate Word document
        word_path = outputs_dir / video_file.replace('_analysis.json', '_analysis.docx')
        generate_word_document(result, str(word_path))
        
        print(f"✅ Created: {word_path.name}")
    else:
        print(f"❌ Not found: {json_path.name}")

print("\n🎉 All Word documents generated successfully!")
print(f"📁 Check the 'outputs' folder for your documents.")
