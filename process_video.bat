@echo off
REM AI Video Subtitle Embedder - Simple Launcher
REM Usage: process_video.bat "path\to\video.mp4"

if "%~1"=="" (
    echo.
    echo ============================================================
    echo  AI Video Subtitle Embedder
    echo ============================================================
    echo.
    echo Usage: process_video.bat "path\to\video.mp4"
    echo.
    echo Example:
    echo   process_video.bat test_video_1.mp4
    echo   process_video.bat "C:\Videos\my_lecture.mp4"
    echo.
    echo This will:
    echo   - Transcribe the video with AI
    echo   - Generate summary, insights, and quiz
    echo   - Create video with embedded subtitles
    echo   - Save Word document with analysis
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  Processing: %~nx1
echo ============================================================
echo.

"%~dp0.venv\Scripts\python.exe" "%~dp0embed_subtitles.py" "%~1" --keep-srt

echo.
echo ============================================================
if %ERRORLEVEL% EQU 0 (
    echo  SUCCESS! Check the 'outputs' folder
) else (
    echo  ERROR occurred during processing
)
echo ============================================================
echo.
pause
