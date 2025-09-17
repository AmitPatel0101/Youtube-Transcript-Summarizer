@echo off
echo ========================================
echo 🎵 AUDIO TRANSCRIPTION SERVER
echo ========================================
echo.
echo 📦 Installing audio transcription packages...
pip install SpeechRecognition pydub yt-dlp
pip install youtube-transcript-api googletrans==4.0.0-rc1

echo.
echo ========================================
echo 🎯 AUDIO FEATURES:
echo ✅ Works WITHOUT captions
echo ✅ Audio transcription
echo ✅ Google Speech Recognition
echo ✅ Any language support
echo ========================================
echo.
echo 🚀 Starting AUDIO server...
echo This server can handle videos WITHOUT captions!
echo Press Ctrl+C to stop
echo.

python advanced_server.py

pause