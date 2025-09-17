#!/usr/bin/env python3
"""
Alternative server using yt-dlp for transcript extraction
"""

import http.server
import socketserver
import json
import urllib.parse
import subprocess
import re

def get_transcript_with_ytdlp(video_id):
    """Extract transcript using yt-dlp as fallback"""
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        cmd = ["yt-dlp", "--write-auto-sub", "--write-sub", "--sub-lang", "en", "--skip-download", "--print", "%(title)s", url]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            # Look for subtitle files
            import os
            import glob
            
            # Find subtitle files
            sub_files = glob.glob(f"*{video_id}*.vtt") + glob.glob(f"*{video_id}*.srt")
            
            if sub_files:
                with open(sub_files[0], 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Clean VTT/SRT format
                lines = content.split('\n')
                text_lines = []
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('WEBVTT') and not '-->' in line and not line.isdigit():
                        # Remove HTML tags
                        line = re.sub(r'<[^>]+>', '', line)
                        if line:
                            text_lines.append(line)
                
                # Cleanup files
                for f in sub_files:
                    try:
                        os.remove(f)
                    except:
                        pass
                
                return '\n'.join(text_lines)
        
        return None
    except Exception as e:
        print(f"yt-dlp failed: {e}")
        return None

def summarize_text(text, max_words=1500):
    """Simple text summarization"""
    text = re.sub(r'\s+', ' ', text.strip())
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    
    if len(sentences) <= 2:
        words = text.split()
        return ' '.join(words[:max_words]) + ('...' if len(words) > max_words else '')
    
    # Simple frequency-based selection
    words = text.lower().split()
    word_freq = {}
    for word in words:
        if len(word) > 3:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Score sentences
    sentence_scores = []
    for sentence in sentences:
        score = sum(word_freq.get(word.lower(), 0) for word in sentence.split())
        sentence_scores.append((score, sentence))
    
    # Select top sentences
    sentence_scores.sort(reverse=True)
    num_sentences = min(len(sentences) // 2, max_words // 25)
    selected = [sent for _, sent in sentence_scores[:num_sentences]]
    
    summary = '. '.join(selected) + '.'
    words = summary.split()
    if len(words) > max_words:
        summary = ' '.join(words[:max_words]) + '...'
    
    return summary

class AlternativeHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            parsed_path = urllib.parse.urlparse(self.path)
            path_parts = parsed_path.path.strip('/').split('/')
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            if len(path_parts) >= 2 and path_parts[0] == 'transcript':
                video_id = path_parts[1]
                text = get_transcript_with_ytdlp(video_id)
                
                if text:
                    response = {
                        'success': True,
                        'transcript': text,
                        'language': 'English (yt-dlp)',
                        'video_id': video_id
                    }
                else:
                    response = {
                        'success': False,
                        'error': 'No transcript available via yt-dlp'
                    }
                    
            elif len(path_parts) >= 2 and path_parts[0] == 'summary':
                video_id = path_parts[1]
                query_params = urllib.parse.parse_qs(parsed_path.query)
                max_words = int(query_params.get('words', [1500])[0])
                
                text = get_transcript_with_ytdlp(video_id)
                
                if text:
                    summary = summarize_text(text, max_words)
                    response = {
                        'success': True,
                        'summary': summary,
                        'original_length': len(text.split()),
                        'summary_length': len(summary.split()),
                        'language': 'English (yt-dlp)',
                        'video_id': video_id
                    }
                else:
                    response = {
                        'success': False,
                        'error': 'No transcript available via yt-dlp'
                    }
                    
            elif path_parts[0] == 'health':
                response = {'status': 'running (yt-dlp mode)'}
            else:
                response = {'error': 'Invalid endpoint'}
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            error_response = {
                'success': False,
                'error': f'Server error: {str(e)}'
            }
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        pass

if __name__ == '__main__':
    PORT = 5001
    
    print("Starting Alternative YouTube Transcript Server (yt-dlp)...")
    print(f"Server running on http://localhost:{PORT}")
    print("This server uses yt-dlp to bypass IP blocks")
    print("Press Ctrl+C to stop")
    
    try:
        with socketserver.TCPServer(("", PORT), AlternativeHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")
    except Exception as e:
        print(f"Server error: {e}")
        input("Press Enter to exit...")