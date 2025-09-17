# YouTube Transcript Extractor - Chrome Extension

A powerful Chrome extension that allows you to extract transcripts from YouTube videos with one click.

## Features

- 🎯 **One-Click Extraction** - Extract transcripts directly from YouTube video pages
- 🌍 **Multiple Languages** - Support for all available YouTube transcript languages
- 📄 **Multiple Formats** - Export as Text, JSON, SRT, or WebVTT
- 💾 **Download & Copy** - Save transcripts to file or copy to clipboard
- 🎮 **Player Integration** - Adds transcript button directly to YouTube player
- 📱 **Responsive Design** - Works on all screen sizes

## Installation

### Method 1: Load Unpacked Extension (Developer Mode)

1. **Enable Developer Mode**
   - Open Chrome and go to `chrome://extensions/`
   - Toggle "Developer mode" in the top right corner

2. **Load the Extension**
   - Click "Load unpacked"
   - Select the `chrome-extension` folder
   - The extension will appear in your extensions list

3. **Pin the Extension**
   - Click the puzzle piece icon in Chrome toolbar
   - Pin "YouTube Transcript Extractor" for easy access

### Method 2: Create Icons (Optional)

If you want custom icons, create these files in the `icons/` folder:
- `icon16.png` (16x16 pixels)
- `icon48.png` (48x48 pixels) 
- `icon128.png` (128x128 pixels)

Or use any PNG images with those names and sizes.

## How to Use

### Method 1: Extension Popup
1. Navigate to any YouTube video
2. Click the extension icon in Chrome toolbar
3. Choose your preferred format (Text, JSON, SRT, WebVTT)
4. Click "Extract Transcript"
5. Copy or download the result

### Method 2: YouTube Player Button
1. Navigate to any YouTube video
2. Look for the transcript button (📄) in the YouTube player controls
3. Click it to extract transcript in a modal window
4. Copy or download directly

### Method 3: List Available Languages
1. Click "List Available Languages" in the popup
2. See all transcript languages available for the video
3. Choose your preferred language for extraction

## Supported Formats

- **Text**: Plain text format, one line per subtitle
- **JSON**: Structured data with timestamps and text
- **SRT**: Standard subtitle format for video players
- **WebVTT**: Web Video Text Tracks format

## Features in Detail

### 🎯 Smart Language Detection
- Automatically detects available transcript languages
- Prioritizes manually created over auto-generated transcripts
- Falls back to first available language if preferred not found

### 📱 Responsive Interface
- Clean, modern popup interface
- Mobile-friendly modal windows
- Intuitive controls and feedback

### 🔒 Privacy Focused
- No data collection or tracking
- All processing happens locally in your browser
- No external servers or APIs used

### ⚡ Performance Optimized
- Fast transcript extraction
- Minimal memory footprint
- Non-intrusive integration with YouTube

## Troubleshooting

### Common Issues

**"No transcripts available"**
- The video doesn't have transcripts enabled
- Try a different video with captions/subtitles

**"Could not extract API key"**
- YouTube may have changed their page structure
- Try refreshing the page and trying again

**Extension not working**
- Make sure you're on a YouTube video page (`youtube.com/watch?v=...`)
- Check that the extension is enabled in `chrome://extensions/`
- Try reloading the YouTube page

### Error Messages

- **"Please navigate to a YouTube video page"**: You're not on a YouTube video
- **"Could not get video ID"**: Invalid YouTube URL format
- **"Failed to fetch transcript"**: Network error or video restrictions

## Technical Details

### Architecture
- **Manifest V3** compatible
- **Content Script** for YouTube page integration
- **Background Script** for transcript processing
- **Popup Interface** for user interaction

### Permissions
- `activeTab`: Access current YouTube tab
- `storage`: Save user preferences
- `https://www.youtube.com/*`: YouTube domain access

### Browser Compatibility
- Chrome 88+
- Chromium-based browsers (Edge, Brave, etc.)

## Development

### File Structure
```
chrome-extension/
├── manifest.json          # Extension configuration
├── popup.html            # Extension popup interface
├── popup.js              # Popup functionality
├── background.js         # Background script with API
├── content.js            # YouTube page integration
├── styles.css            # Extension styles
├── icons/                # Extension icons
└── README.md            # This file
```

### Key Components

1. **Background Script** (`background.js`)
   - Implements YouTube Transcript API
   - Handles transcript extraction and formatting
   - Manages communication between components

2. **Content Script** (`content.js`)
   - Integrates with YouTube player
   - Adds transcript button to player controls
   - Shows modal windows and notifications

3. **Popup Interface** (`popup.html`, `popup.js`)
   - Main user interface
   - Format selection and controls
   - Copy/download functionality

## License

MIT License - Feel free to modify and distribute

## Contributing

1. Fork the repository
2. Make your changes
3. Test thoroughly on different YouTube videos
4. Submit a pull request

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify you're using a supported browser version
3. Test with different YouTube videos
4. Check browser console for error messages

---

**Enjoy extracting transcripts! 🎉**