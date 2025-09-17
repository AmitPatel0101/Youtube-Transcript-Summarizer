# 🚀 YouTube Transcript Extractor - Chrome Extension

## 📦 What You Get

A complete Chrome extension that extracts YouTube transcripts with:
- ✅ One-click transcript extraction
- ✅ Multiple formats (Text, JSON, SRT, WebVTT)
- ✅ Direct YouTube player integration
- ✅ Copy/Download functionality
- ✅ Multi-language support

## 🛠️ Installation Steps

### Step 1: Prepare Icons (Optional)
```bash
cd chrome-extension/icons
python create_icons.py
```
*Or create your own 16x16, 48x48, 128x128 PNG files named icon16.png, icon48.png, icon128.png*

### Step 2: Install Extension
1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (top right toggle)
3. Click "Load unpacked"
4. Select the `chrome-extension` folder
5. Pin the extension to toolbar

## 🎯 How to Use

### Method 1: Extension Popup
1. Go to any YouTube video
2. Click extension icon in toolbar
3. Select format and click "Extract Transcript"

### Method 2: YouTube Player Button
1. Go to any YouTube video  
2. Look for transcript button (📄) in player controls
3. Click to extract in modal window

## 📁 File Structure
```
chrome-extension/
├── manifest.json     # Extension config
├── popup.html        # Main interface
├── popup.js          # Popup logic
├── background.js     # Core API
├── content.js        # YouTube integration
├── styles.css        # Styling
├── icons/            # Extension icons
└── README.md         # Documentation
```

## 🔧 Features

- **Smart Detection**: Auto-finds available languages
- **Multiple Formats**: Text, JSON, SRT, WebVTT
- **Player Integration**: Button in YouTube controls
- **Privacy First**: No data collection
- **Offline Processing**: Works without external APIs

## 🐛 Troubleshooting

**Extension not working?**
- Ensure you're on `youtube.com/watch?v=...`
- Check extension is enabled in `chrome://extensions/`
- Refresh YouTube page

**No transcripts found?**
- Video may not have captions/subtitles
- Try different video with transcripts

## 🎉 Ready to Use!

Your extension is now ready. Test it on any YouTube video with captions!