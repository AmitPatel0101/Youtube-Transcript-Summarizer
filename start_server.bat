@echo off
echo ========================================
echo YouTube Transcript Extractor Server
echo ========================================
echo.
echo Installing required packages...
pip install youtube-transcript-api googletrans==4.0.0-rc1

echo.
echo ========================================
echo FEATURES:
echo - Works with videos in ANY language
echo - Automatically translates to English
echo - Supports up to 1500-word summaries
echo - Fallback to original language if translation fails
echo ========================================
echo.
echo Starting server...
echo Keep this window open while using the extension.
echo Press Ctrl+C to stop the server.
echo.

python simple_server.py

pause