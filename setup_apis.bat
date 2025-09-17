@echo off
echo ========================================
echo 🔧 SETTING UP ULTIMATE TRANSCRIPT SERVER
echo ========================================
echo.

echo 📦 Installing required packages...
pip install youtube-transcript-api
pip install googletrans==4.0.0-rc1
pip install requests
pip install openai
pip install transformers
pip install torch

echo.
echo ========================================
echo 🔑 API KEY SETUP
echo ========================================
echo.
echo You can use multiple AI services for better summaries:
echo.
echo 1. OpenAI (GPT-3.5/GPT-4) - Best quality summaries
echo    - Get API key from: https://platform.openai.com/api-keys
echo    - Cost: ~$0.002 per 1K tokens
echo.
echo 2. Hugging Face (Free tier available)
echo    - Get API key from: https://huggingface.co/settings/tokens
echo    - Free tier: 1000 requests/month
echo.
echo 3. Extractive Summary (Always available as fallback)
echo    - No API key needed
echo    - Uses frequency-based sentence selection
echo.

set /p setup_openai="Do you want to set up OpenAI API key? (y/n): "
if /i "%setup_openai%"=="y" (
    set /p openai_key="Enter your OpenAI API key: "
    echo OPENAI_API_KEY=!openai_key! >> .env
    echo ✅ OpenAI API key saved to .env file
)

echo.
set /p setup_hf="Do you want to set up Hugging Face API key? (y/n): "
if /i "%setup_hf%"=="y" (
    set /p hf_key="Enter your Hugging Face API key: "
    echo HUGGINGFACE_API_KEY=!hf_key! >> .env
    echo ✅ Hugging Face API key saved to .env file
)

echo.
echo ========================================
echo 🚀 SETUP COMPLETE!
echo ========================================
echo.
echo Your server now supports:
echo ✅ Multi-language transcript extraction
echo ✅ AI-powered summaries (OpenAI + Hugging Face)
echo ✅ Extractive summaries (fallback)
echo ✅ Hindi, Spanish, French, German, Japanese, etc.
echo.
echo To start the server, run: python advanced_server.py
echo.
pause