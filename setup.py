"""
Setup file for AI Video Lecture Assistant
Makes the package installable via pip
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ai-video-assistant",
    version="1.0.5",
    author="Aditya Takawale",
    author_email="adityatakawale@example.com",  # Update with your real email
    description="AI-powered video lecture transcription, analysis, and subtitle generation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Aditya-Takawale/AI-Summary",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Topic :: Education",
        "Topic :: Multimedia :: Video",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.9",
    install_requires=[
        "openai-whisper>=20231117",
        "moviepy>=1.0.3",
        "requests>=2.31.0",
        "python-docx>=1.1.0",
        "Pillow>=10.0.0",
        "opencv-python>=4.8.0",
        "torch>=2.0.0",
        "torchaudio>=2.0.0",
        "imageio-ffmpeg>=0.4.9",
    ],
    extras_require={
        "web": ["flask>=3.0.0"],
        "dev": ["pytest>=7.0.0", "black>=23.0.0"],
    },
    entry_points={
        "console_scripts": [
            "ai-video-assistant=ai_video_assistant.cli:main",
        ],
    },
)
