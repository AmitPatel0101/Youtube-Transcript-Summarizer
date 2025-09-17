@echo off
echo ========================================
echo 🚀 ULTIMATE YouTube Transcript Extractor
echo ========================================
echo.
echo 📦 Installing ALL required packages...
pip install youtube-transcript-api googletrans==4.0.0-rc1 requests python-dotenv
pip install transformers torch
pip install openai
pip install yt-dlp
pip install beautifulsoup4 lxml 
pip install SpeechRecognition pydub
pip install openai-whisper
pip install ffmpeg-python

echo.
echo ========================================
echo 🎯 ULTIMATE FEATURES:
echo ✅ Multiple extraction methods
echo ✅ Any language support  
echo ✅ AI-powered summarization
echo ✅ Hugging Face transformers
echo ✅ Google Translate integration
echo ✅ yt-dlp fallback
echo ✅ Advanced text processing
echo ✅ Multiple API fallbacks
echo 🎵 AUDIO TRANSCRIPTION (NEW!)
echo ✅ OpenAI Whisper integration
echo ✅ Google Speech Recognition
echo ✅ AssemblyAI support
echo ✅ Works WITHOUT captions!
echo ========================================
echo.
echo 🌟 Starting ULTIMATE server...
echo Keep this window open while using extension
echo Press Ctrl+C to stop server
echo.

python advanced_server.py

pause