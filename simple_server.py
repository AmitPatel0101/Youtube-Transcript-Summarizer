#!/usr/bin/env python3
"""
Simple HTTP server for YouTube Transcript API with Translation
"""

import http.server
import socketserver
import json
import urllib.parse
from youtube_transcript_api import YouTubeTranscriptApi
try:
    from googletrans import Translator
    TRANSLATOR_AVAILABLE = True
except ImportError:
    TRANSLATOR_AVAILABLE = False
    print("Warning: googletrans not installed. Install with: pip install googletrans==4.0.0-rc1")

import re

def summarize_text(text, max_words=1500):
    """Simple extractive summarization without external dependencies"""
    # Clean and split into sentences
    text = re.sub(r'\s+', ' ', text.strip())
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
    
    if len(sentences) <= 2:
        words = text.split()
        return ' '.join(words[:max_words]) + ('...' if len(words) > max_words else '')
    
    # Calculate word frequencies (excluding common words)
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
    
    words = re.findall(r'\b\w+\b', text.lower())
    word_freq = {}
    for word in words:
        if len(word) > 2 and word not in stop_words:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Score sentences
    sentence_scores = []
    for sentence in sentences:
        sentence_words = re.findall(r'\b\w+\b', sentence.lower())
        score = sum(word_freq.get(word, 0) for word in sentence_words)
        if len(sentence_words) > 0:
            score = score / len(sentence_words)  # Normalize by sentence length
        sentence_scores.append((score, sentence))
    
    # Sort by score and select top sentences
    sentence_scores.sort(reverse=True)
    num_sentences = max(1, min(len(sentences) // 2, max_words // 25))
    selected_sentences = [sent for _, sent in sentence_scores[:num_sentences]]
    
    # Rebuild summary in original order
    summary_parts = []
    for sentence in sentences:
        if sentence in selected_sentences:
            summary_parts.append(sentence)
    
    summary = '. '.join(summary_parts) + '.'
    
    # Trim to word limit
    words = summary.split()
    if len(words) > max_words:
        summary = ' '.join(words[:max_words]) + '...'
    
    return summary

class TranscriptHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Parse URL
            parsed_path = urllib.parse.urlparse(self.path)
            path_parts = parsed_path.path.strip('/').split('/')
            
            # Add CORS headers
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            if len(path_parts) >= 2 and path_parts[0] == 'transcript':
                # Extract transcript
                video_id = path_parts[1]
                
                # Enhanced multi-language transcript extraction
                text = None
                original_language = "English"
                
                # Method 1: Try direct English transcript first
                try:
                    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
                    text = '\n'.join([snippet['text'] for snippet in transcript])
                    original_language = "English (direct)"
                except:
                    # Method 2: Try any available language with comprehensive fallback
                    try:
                        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                        
                        # Priority order: translatable transcripts first, then original
                        transcripts_to_try = []
                        for transcript_info in transcript_list:
                            if transcript_info.is_translatable:
                                transcripts_to_try.insert(0, transcript_info)  # Add to front
                            else:
                                transcripts_to_try.append(transcript_info)  # Add to back
                        
                        for transcript_info in transcripts_to_try:
                            try:
                                if transcript_info.is_translatable:
                                    # Try YouTube's built-in translation to English
                                    try:
                                        english_transcript = transcript_info.translate('en')
                                        transcript_data = english_transcript.fetch()
                                        text = '\n'.join([snippet['text'] for snippet in transcript_data])
                                        original_language = f"{transcript_info.language} → English (YouTube translated)"
                                        break
                                    except Exception as yt_translate_error:
                                        print(f"YouTube translation failed: {yt_translate_error}")
                                        continue
                                
                                # Get original transcript and try Google Translate
                                transcript_data = transcript_info.fetch()
                                original_text = '\n'.join([snippet['text'] for snippet in transcript_data])
                                
                                if transcript_info.language_code == 'en':
                                    # It's already English
                                    text = original_text
                                    original_language = f"{transcript_info.language} (original)"
                                    break
                                elif TRANSLATOR_AVAILABLE:
                                    # Try Google Translate
                                    try:
                                        translator = Translator()
                                        # Split into chunks if text is too long
                                        if len(original_text) > 5000:
                                            chunks = [original_text[i:i+4500] for i in range(0, len(original_text), 4500)]
                                            translated_chunks = []
                                            for chunk in chunks:
                                                translated_chunk = translator.translate(chunk, dest='en')
                                                translated_chunks.append(translated_chunk.text)
                                            text = ' '.join(translated_chunks)
                                        else:
                                            translated = translator.translate(original_text, dest='en')
                                            text = translated.text
                                        original_language = f"{transcript_info.language} → English (Google translated)"
                                        break
                                    except Exception as google_translate_error:
                                        print(f"Google translation failed: {google_translate_error}")
                                        # Use original text as fallback
                                        text = original_text
                                        original_language = f"{transcript_info.language} (original - no translation)"
                                        break
                                else:
                                    # No translation available, use original
                                    text = original_text
                                    original_language = f"{transcript_info.language} (original - no translation)"
                                    break
                                    
                            except Exception as fetch_error:
                                print(f"Failed to fetch transcript: {fetch_error}")
                                continue
                        
                        if text is None:
                            raise Exception("Could not fetch any available transcripts from any language")
                            
                    except Exception as list_error:
                        if "disabled" in str(list_error).lower():
                            raise Exception("Transcripts are disabled for this video")
                        elif "unavailable" in str(list_error).lower():
                            raise Exception("Video is unavailable or private")
                        else:
                            raise Exception(f"No transcripts available: {str(list_error)}")
                
                response = {
                    'success': True,
                    'transcript': text,
                    'language': original_language,
                    'video_id': video_id
                }
                
            elif len(path_parts) >= 2 and path_parts[0] == 'list':
                # List transcripts
                video_id = path_parts[1]
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                
                languages = []
                for transcript in transcript_list:
                    languages.append({
                        'language': transcript.language,
                        'code': transcript.language_code,
                        'generated': transcript.is_generated
                    })
                
                response = {
                    'success': True,
                    'languages': languages,
                    'video_id': video_id
                }
                
            elif len(path_parts) >= 2 and path_parts[0] == 'summary':
                # Summarize transcript
                video_id = path_parts[1]
                query_params = urllib.parse.parse_qs(parsed_path.query)
                max_words = int(query_params.get('words', [1500])[0])
                
                # Use the same enhanced transcript extraction logic
                text = None
                original_language = "English"
                
                try:
                    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
                    text = '\n'.join([snippet['text'] for snippet in transcript])
                    original_language = "English (direct)"
                except:
                    try:
                        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                        
                        # Priority order: translatable transcripts first, then original
                        transcripts_to_try = []
                        for transcript_info in transcript_list:
                            if transcript_info.is_translatable:
                                transcripts_to_try.insert(0, transcript_info)
                            else:
                                transcripts_to_try.append(transcript_info)
                        
                        for transcript_info in transcripts_to_try:
                            try:
                                if transcript_info.is_translatable:
                                    try:
                                        english_transcript = transcript_info.translate('en')
                                        transcript_data = english_transcript.fetch()
                                        text = '\n'.join([snippet['text'] for snippet in transcript_data])
                                        original_language = f"{transcript_info.language} → English (YouTube translated)"
                                        break
                                    except:
                                        continue
                                
                                transcript_data = transcript_info.fetch()
                                original_text = '\n'.join([snippet['text'] for snippet in transcript_data])
                                
                                if transcript_info.language_code == 'en':
                                    text = original_text
                                    original_language = f"{transcript_info.language} (original)"
                                    break
                                elif TRANSLATOR_AVAILABLE:
                                    try:
                                        translator = Translator()
                                        if len(original_text) > 5000:
                                            chunks = [original_text[i:i+4500] for i in range(0, len(original_text), 4500)]
                                            translated_chunks = []
                                            for chunk in chunks:
                                                translated_chunk = translator.translate(chunk, dest='en')
                                                translated_chunks.append(translated_chunk.text)
                                            text = ' '.join(translated_chunks)
                                        else:
                                            translated = translator.translate(original_text, dest='en')
                                            text = translated.text
                                        original_language = f"{transcript_info.language} → English (Google translated)"
                                        break
                                    except:
                                        text = original_text
                                        original_language = f"{transcript_info.language} (original - no translation)"
                                        break
                                else:
                                    text = original_text
                                    original_language = f"{transcript_info.language} (original - no translation)"
                                    break
                            except:
                                continue
                        
                        if text is None:
                            raise Exception("Could not fetch any available transcripts from any language")
                    except Exception as e:
                        raise Exception(f"No transcripts available: {str(e)}")
                
                # Generate summary
                print(f"Generating summary for {len(text.split())} words, target: {max_words} words")
                summary = summarize_text(text, max_words)
                print(f"Summary generated: {len(summary.split())} words")
                
                response = {
                    'success': True,
                    'summary': summary,
                    'original_length': len(text.split()),
                    'summary_length': len(summary.split()),
                    'language': original_language,
                    'video_id': video_id
                }
                
            elif path_parts[0] == 'health':
                response = {'status': 'running'}
                
            else:
                response = {'error': 'Invalid endpoint'}
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            error_msg = str(e)
            # Provide more user-friendly error messages
            if "TranscriptsDisabled" in error_msg:
                error_msg = "Transcripts are disabled for this video"
            elif "VideoUnavailable" in error_msg:
                error_msg = "Video is unavailable or private"
            elif "NoTranscriptFound" in error_msg:
                error_msg = "No transcripts found for this video"
            elif "TooManyRequests" in error_msg:
                error_msg = "Too many requests. Please wait a moment and try again"
            
            error_response = {
                'success': False,
                'error': error_msg
            }
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_OPTIONS(self):
        # Handle preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass

if __name__ == '__main__':
    PORT = 5000
    
    print("Starting YouTube Transcript Server with Translation...")
    print(f"Server running on http://localhost:{PORT}")
    print(f"Google Translate available: {TRANSLATOR_AVAILABLE}")
    print("All transcripts will be converted to English when possible")
    print("Press Ctrl+C to stop")
    
    try:
        with socketserver.TCPServer(("", PORT), TranscriptHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")
    except Exception as e:
        print(f"Server error: {e}")
        input("Press Enter to exit...")