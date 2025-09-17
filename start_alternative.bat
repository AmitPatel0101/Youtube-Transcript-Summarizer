@echo off
echo ========================================
echo Alternative YouTube Transcript Server
echo ========================================
echo.
echo Installing yt-dlp (bypasses IP blocks)...
pip install yt-dlp

echo.
echo ========================================
echo ALTERNATIVE METHOD:
echo - Uses yt-dlp instead of youtube-transcript-api
echo - Bypasses YouTube IP blocking
echo - Downloads subtitles directly
echo ========================================
echo.
echo Starting alternative server on port 5001...
echo Keep this window open while using the extension.
echo Press Ctrl+C to stop the server.
echo.

python alternative_server.py

pause