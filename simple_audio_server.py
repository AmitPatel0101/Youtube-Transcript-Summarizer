#!/usr/bin/env python3
"""
Simple Audio Transcription Server for Videos WITHOUT Captions
"""

import http.server
import socketserver
import json
import urllib.parse
import subprocess
import os
import time
from youtube_transcript_api import YouTubeTranscriptApi

try:
    from googletrans import Translator
    GOOGLE_TRANSLATE = True
except ImportError:
    GOOGLE_TRANSLATE = False

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION = True
except ImportError:
    SPEECH_RECOGNITION = False

def download_and_transcribe_audio(video_id):
    """Download audio and transcribe it"""
    try:
        print(f"🎵 Processing video without captions: {video_id}")
        
        # Step 1: Download audio
        url = f"https://www.youtube.com/watch?v={video_id}"
        audio_file = f"temp_{video_id}.wav"
        
        cmd = [
            "yt-dlp", 
            "-x", 
            "--audio-format", "wav",
            "--audio-quality", "5",
            "-o", audio_file,
            "--no-warnings",
            url
        ]
        
        print("📥 Downloading audio...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if not os.path.exists(audio_file):
            print("❌ Audio download failed")
            return None
        
        print("✅ Audio downloaded successfully")
        
        # Step 2: Transcribe audio
        if not SPEECH_RECOGNITION:
            cleanup_file(audio_file)
            return "Speech recognition not available. Install: pip install SpeechRecognition"
        
        print("🎤 Transcribing audio...")
        transcript = transcribe_audio_file(audio_file)
        
        # Cleanup
        cleanup_file(audio_file)
        
        if transcript:
            print(f"✅ Transcription successful: {len(transcript)} characters")
            return transcript
        else:
            print("❌ Transcription failed")
            return None
            
    except Exception as e:
        print(f"❌ Audio processing error: {e}")
        return None

def transcribe_audio_file(audio_file):
    """Transcribe audio file using speech recognition"""
    try:
        r = sr.Recognizer()
        
        # Load audio file
        with sr.AudioFile(audio_file) as source:
            # Adjust for noise and record
            r.adjust_for_ambient_noise(source, duration=1)
            audio_data = r.record(source, duration=300)  # Max 5 minutes
            
            # Recognize speech
            text = r.recognize_google(audio_data, language='en-US')
            return text
            
    except sr.UnknownValueError:
        print("⚠️ Could not understand audio")
        return None
    except sr.RequestError as e:
        print(f"❌ Speech recognition error: {e}")
        return None
    except Exception as e:
        print(f"❌ Transcription error: {e}")
        return None

def cleanup_file(filename):
    """Remove temporary file"""
    try:
        if os.path.exists(filename):
            os.remove(filename)
    except:
        pass

def try_normal_transcript(video_id):
    """Try normal transcript extraction first"""
    try:
        # Try English first
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        text = '\n'.join([item['text'] for item in transcript])
        return text, "English (captions)"
    except:
        try:
            # Try any language
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            for transcript_info in transcript_list:
                try:
                    if transcript_info.is_translatable:
                        english_transcript = transcript_info.translate('en')
                        data = english_transcript.fetch()
                        text = '\n'.join([item['text'] for item in data])
                        return text, f"{transcript_info.language} → English (captions)"
                except:
                    continue
        except:
            pass
    
    return None, None

def simple_summarize(text, max_words=300):
    """Simple text summarization"""
    if not text:
        return ""
    
    sentences = text.split('.')
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    
    if len(sentences) <= 3:
        words = text.split()
        return ' '.join(words[:max_words])
    
    # Take first, middle, and last parts
    total_sentences = len(sentences)
    selected = []
    
    # First part
    selected.extend(sentences[:total_sentences//3])
    # Middle part  
    selected.extend(sentences[total_sentences//3:2*total_sentences//3])
    # Last part
    selected.extend(sentences[2*total_sentences//3:])
    
    summary = '. '.join(selected)
    words = summary.split()
    
    if len(words) > max_words:
        summary = ' '.join(words[:max_words]) + '...'
    
    return summary

class SimpleAudioHandler(http.server.BaseHTTPRequestHandler):
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
                
                # Try normal transcript first
                text, method = try_normal_transcript(video_id)
                
                # If no captions, try audio transcription
                if not text:
                    print("🎵 No captions found, trying audio transcription...")
                    text = download_and_transcribe_audio(video_id)
                    method = "Audio Transcription" if text else None
                
                if text:
                    response = {
                        'success': True,
                        'transcript': text,
                        'language': method or 'Unknown',
                        'video_id': video_id
                    }
                else:
                    response = {
                        'success': False,
                        'error': 'Could not extract transcript. Video may be private or audio unclear.'
                    }
                    
            elif len(path_parts) >= 2 and path_parts[0] == 'summary':
                video_id = path_parts[1]
                query_params = urllib.parse.parse_qs(parsed_path.query)
                max_words = int(query_params.get('words', [300])[0])
                
                # Try normal transcript first
                text, method = try_normal_transcript(video_id)
                
                # If no captions, try audio transcription
                if not text:
                    print("🎵 No captions found, trying audio transcription...")
                    text = download_and_transcribe_audio(video_id)
                    method = "Audio Transcription" if text else None
                
                if text:
                    summary = simple_summarize(text, max_words)
                    response = {
                        'success': True,
                        'summary': summary,
                        'original_length': len(text.split()),
                        'summary_length': len(summary.split()),
                        'language': method or 'Unknown',
                        'video_id': video_id
                    }
                else:
                    response = {
                        'success': False,
                        'error': 'Could not extract transcript for summarization'
                    }
                    
            elif path_parts[0] == 'health':
                response = {
                    'status': 'running',
                    'audio_transcription': SPEECH_RECOGNITION,
                    'google_translate': GOOGLE_TRANSLATE
                }
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
    PORT = 5000
    
    print("🎵 Simple Audio Transcription Server")
    print("=" * 40)
    print(f"🌐 Server: http://localhost:{PORT}")
    print(f"🎤 Speech Recognition: {'✅' if SPEECH_RECOGNITION else '❌'}")
    print(f"🔤 Google Translate: {'✅' if GOOGLE_TRANSLATE else '❌'}")
    print("=" * 40)
    print("🎯 FEATURES:")
    print("  • Normal captions (any language)")
    print("  • Audio transcription (no captions)")
    print("  • Simple summarization")
    print("=" * 40)
    print("Press Ctrl+C to stop")
    
    try:
        with socketserver.TCPServer(("", PORT), SimpleAudioHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
    except Exception as e:
        print(f"❌ Server error: {e}")
        input("Press Enter to exit...")