#!/usr/bin/env python3
"""
ULTIMATE YouTube Transcript Server
Multi-language support with translation
"""

import http.server
import socketserver
import json
import urllib.parse
from youtube_transcript_api import YouTubeTranscriptApi
from googletrans import Translator
import re
import textwrap
import base64
import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class UltimateTranscriptHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.translator = Translator()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        try:
            parsed_path = urllib.parse.urlparse(self.path)
            path_parts = parsed_path.path.strip('/').split('/')
            
            # CORS headers
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            if len(path_parts) >= 2 and path_parts[0] == 'transcript':
                video_id = path_parts[1]
                query_params = urllib.parse.parse_qs(parsed_path.query)
                include_summary = 'summary' in query_params and query_params['summary'][0].lower() == 'true'
                summary_words = int(query_params.get('summary_words', [100])[0]) if 'summary_words' in query_params else 100
                response = self.get_ultimate_transcript(video_id, include_summary, summary_words)
                
            elif len(path_parts) >= 3 and path_parts[0] == 'download':
                video_id = path_parts[1]
                format_type = path_parts[2]  # txt, json, srt
                query_params = urllib.parse.parse_qs(parsed_path.query)
                include_summary = 'summary' in query_params and query_params['summary'][0].lower() == 'true'
                summary_words = int(query_params.get('summary_words', [100])[0]) if 'summary_words' in query_params else 100
                response = self.download_transcript(video_id, format_type, include_summary, summary_words)
                
            elif len(path_parts) >= 2 and path_parts[0] == 'share':
                video_id = path_parts[1]
                query_params = urllib.parse.parse_qs(parsed_path.query)
                include_summary = 'summary' in query_params and query_params['summary'][0].lower() == 'true'
                summary_words = int(query_params.get('summary_words', [100])[0]) if 'summary_words' in query_params else 100
                response = self.generate_share_link(video_id, include_summary, summary_words)
                
            elif len(path_parts) >= 2 and path_parts[0] == 'list':
                video_id = path_parts[1]
                response = self.list_ultimate_transcripts(video_id)
                
            elif path_parts[0] == 'health':
                response = {'status': 'ULTIMATE SERVER RUNNING', 'features': ['Multi-language', 'Translation', 'Fallbacks', 'Summary', 'Download', 'Share', 'Copy']}
                
            else:
                response = {'error': 'Invalid endpoint'}
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            error_response = {'success': False, 'error': str(e)}
            self.wfile.write(json.dumps(error_response).encode())
    
    def get_ultimate_transcript(self, video_id, include_summary=False, summary_words=100):
        """Ultimate transcript extraction with multiple fallbacks"""
        try:
            ytt_api = YouTubeTranscriptApi()
            transcript_list = ytt_api.list(video_id)
            
            # Method 1: Try to get any available transcript first
            language_priorities = [
                ['en'],  # English first
                ['hi', 'en'],  # Hindi with English fallback
                ['es', 'en'],  # Spanish with English fallback
                ['fr', 'en'],  # French with English fallback
                ['de', 'en'],  # German with English fallback
                ['ja', 'en'],  # Japanese with English fallback
                ['ko', 'en'],  # Korean with English fallback
                ['zh', 'en'],  # Chinese with English fallback
                ['ar', 'en'],  # Arabic with English fallback
                ['ru', 'en'],  # Russian with English fallback
                ['pt', 'en'],  # Portuguese with English fallback
                ['it', 'en'],  # Italian with English fallback
            ]
            
            original_transcript = None
            original_lang_code = None
            
            for langs in language_priorities:
                try:
                    transcript = ytt_api.fetch(video_id, languages=langs)
                    text = '\n'.join([snippet.text for snippet in transcript])
                    original_transcript = text
                    original_lang_code = transcript.language_code
                    
                    # If we got English directly, return it
                    if transcript.language_code == 'en':
                        result = {
                            'success': True,
                            'transcript': text,
                            'language': 'English (Direct)',
                            'method': 'Direct English',
                            'video_id': video_id,
                            'word_count': len(text.split())
                        }
                        if include_summary:
                            result['summary'] = self.generate_summary(text, 'en', summary_words)
                        return result
                    else:
                        # Got non-English, continue to translation methods
                        print(f"Got {transcript.language_code} transcript, will try translation")
                        break
                except Exception as e:
                    print(f"Failed to get transcript for {langs}: {e}")
                    continue
            
            # Method 2: YouTube Translation (try all available transcripts)
            if original_transcript is None:
                # If Method 1 failed, try to get any transcript
                for transcript_info in transcript_list:
                    try:
                        transcript_data = transcript_info.fetch()
                        original_transcript = '\n'.join([snippet.text for snippet in transcript_data])
                        original_lang_code = transcript_info.language_code
                        print(f"Got {transcript_info.language_code} transcript as fallback")
                        break
                    except Exception as e:
                        print(f"Failed to fetch {transcript_info.language}: {e}")
                        continue
            
            # Now try YouTube translation if we have a non-English transcript
            if original_transcript and original_lang_code != 'en':
                for transcript_info in transcript_list:
                    if transcript_info.language_code == original_lang_code and transcript_info.is_translatable:
                        try:
                            english_transcript = transcript_info.translate('en')
                            transcript_data = english_transcript.fetch()
                            text = '\n'.join([snippet.text for snippet in transcript_data])
                            result = {
                                'success': True,
                                'transcript': text,
                                'language': f'{transcript_info.language} → English (YouTube)',
                                'method': 'YouTube Translation',
                                'video_id': video_id,
                                'word_count': len(text.split())
                            }
                            if include_summary:
                                result['summary'] = self.generate_summary(text, 'en', summary_words)
                            return result
                        except Exception as e:
                            print(f"YouTube translation failed for {transcript_info.language}: {e}")
                            continue
            
            # Method 3: Google Translate as final fallback
            if original_transcript and original_lang_code != 'en':
                try:
                    print(f"Trying Google Translate for {original_lang_code} transcript")
                    # Split text into smaller chunks for better translation
                    max_chunk_size = 3000  # Reduced chunk size
                    chunks = [original_transcript[i:i+max_chunk_size] for i in range(0, len(original_transcript), max_chunk_size)]
                    translated_chunks = []
                    
                    for i, chunk in enumerate(chunks):
                        try:
                            print(f"Translating chunk {i+1}/{len(chunks)}")
                            # Auto-detect source language if needed
                            if original_lang_code in ['auto', 'unknown']:
                                translated = self.translator.translate(chunk, dest='en')
                            else:
                                translated = self.translator.translate(chunk, src=original_lang_code, dest='en')
                            translated_chunks.append(translated.text)
                        except Exception as chunk_error:
                            print(f"Chunk {i+1} translation failed: {chunk_error}")
                            # Keep original chunk if translation fails
                            translated_chunks.append(chunk)
                    
                    final_text = '\n'.join(translated_chunks)
                    
                    # Check if translation actually worked
                    if final_text and final_text != original_transcript:
                        result = {
                            'success': True,
                            'transcript': final_text,
                            'language': f'{original_lang_code.upper()} → English (Google)',
                            'method': 'Google Translate',
                            'video_id': video_id,
                            'word_count': len(final_text.split())
                        }
                        if include_summary:
                            result['summary'] = self.generate_summary(final_text, 'en', summary_words)
                        return result
                    
                except Exception as e:
                    print(f"Google translate failed: {e}")
            
            # Method 4: Return original transcript if all translation methods fail
            if original_transcript:
                print(f"Returning original {original_lang_code} transcript")
                result = {
                    'success': True,
                    'transcript': original_transcript,
                    'language': f'{original_lang_code.upper()} (Original - Translation Failed)',
                    'method': 'Original Language',
                    'video_id': video_id,
                    'word_count': len(original_transcript.split())
                }
                if include_summary:
                    result['summary'] = self.generate_summary(original_transcript, original_lang_code, summary_words)
                return result
            
            return {
                'success': False, 
                'error': 'No transcripts available for this video',
                'details': 'This video does not have captions/subtitles. Try a different video with captions enabled.',
                'suggestions': [
                    'Look for videos with CC (Closed Captions) icon',
                    'Try popular videos which usually have auto-generated captions',
                    'Check if the video is age-restricted or private'
                ]
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def generate_summary(self, text, language='en', target_words=100):
        """Generate intelligent summary with multi-language support and multiple methods"""
        try:
            print(f"Generating summary for {len(text.split())} words in {language}")
            
            # Method 1: Try Google Gemini API if available
            gemini_summary = self.try_openai_summary(text, language, target_words)
            if gemini_summary:
                return gemini_summary
            
            # Method 2: Try Hugging Face API if available
            hf_summary = self.try_huggingface_summary(text, language, target_words)
            if hf_summary:
                return hf_summary
            
            # Method 3: Fallback to extractive summary
            return self.extractive_summary(text, language, target_words)
            
        except Exception as e:
            print(f"Summary generation error: {e}")
            return {
                'text': f'Summary generation failed: {str(e)}',
                'error': str(e),
                'language': language,
                'method': 'error'
            }
    
    def try_openai_summary(self, text, language, target_words=100):
        """Try Google Gemini API for summary generation"""
        try:
            import requests
            import os
            
            # Check for API key
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                print("Gemini API key not found")
                return None
            
            # Truncate text if too long
            max_tokens = 3000
            if len(text.split()) > max_tokens:
                text = ' '.join(text.split()[:max_tokens]) + '...'
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": f"Please create a summary of this video transcript in exactly {target_words} words:\n\n{text}"
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.3,
                    "maxOutputTokens": min(target_words * 2, 500)
                }
            }
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if 'candidates' in result and len(result['candidates']) > 0:
                    summary_text = result['candidates'][0]['content']['parts'][0]['text'].strip()
                    
                    return {
                        'text': summary_text,
                        'original_words': len(text.split()),
                        'summary_words': len(summary_text.split()),
                        'compression': f"{len(summary_text.split())/len(text.split())*100:.1f}%",
                        'language': language,
                        'method': 'Google Gemini'
                    }
            
            print(f"Gemini API response: {response.status_code}")
            return None
            
        except Exception as e:
            print(f"Gemini summary failed: {e}")
            return None
    
    def try_huggingface_summary(self, text, language, target_words=100):
        """Try Hugging Face API for summary generation"""
        try:
            import requests
            import os
            
            # Check for HF API key
            hf_token = os.getenv('HUGGINGFACE_API_KEY') or os.getenv('HF_TOKEN')
            if not hf_token:
                print("Hugging Face API key not found")
                return None
            
            # Use different models based on language
            if language.startswith('hi') or 'hindi' in language.lower():
                model = "facebook/bart-large-cnn"  # Works well for multiple languages
            else:
                model = "facebook/bart-large-cnn"
            
            # Truncate text if too long
            max_length = 1000
            if len(text.split()) > max_length:
                text = ' '.join(text.split()[:max_length])
            
            headers = {"Authorization": f"Bearer {hf_token}"}
            
            response = requests.post(
                f"https://api-inference.huggingface.co/models/{model}",
                headers=headers,
                json={
                    "inputs": text,
                    "parameters": {
                        "max_length": min(target_words * 2, 300),
                        "min_length": max(target_words // 2, 30),
                        "do_sample": False
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    summary_text = result[0].get('summary_text', '')
                    
                    return {
                        'text': summary_text,
                        'original_words': len(text.split()),
                        'summary_words': len(summary_text.split()),
                        'compression': f"{len(summary_text.split())/len(text.split())*100:.1f}%",
                        'language': language,
                        'method': 'Hugging Face BART'
                    }
            
            print(f"HF API response: {response.status_code}")
            return None
            
        except Exception as e:
            print(f"Hugging Face summary failed: {e}")
            return None
    
    def extractive_summary(self, text, language, target_words=100):
        """Fallback extractive summary method"""
        try:
            print("Using extractive summary method")
            
            # Clean and prepare text
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Handle different sentence endings for different languages
            if language.startswith('hi') or 'hindi' in language.lower():
                sentences = re.split(r'[.!?।॥]+', text)
            elif language.startswith('ja') or 'japanese' in language.lower():
                sentences = re.split(r'[.!?。！？]+', text)
            elif language.startswith('zh') or 'chinese' in language.lower():
                sentences = re.split(r'[.!?。！？…]+', text)
            else:
                sentences = re.split(r'[.!?]+', text)
            
            sentences = [s.strip() for s in sentences if len(s.strip()) > 15]
            
            if not sentences:
                return {
                    'text': 'No sentences found for summary',
                    'error': 'No valid sentences',
                    'language': language,
                    'method': 'extractive'
                }
            
            word_count = len(text.split())
            
            # Determine summary length based on target words
            avg_words_per_sentence = 15
            summary_sentences = max(1, min(target_words // avg_words_per_sentence, len(sentences)))
            
            # Simple frequency-based scoring
            words = re.findall(r'\b\w{2,}\b', text.lower())
            word_freq = {}
            for word in words:
                if len(word) > 2:  # Skip very short words
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Score sentences
            sentence_scores = []
            for i, sentence in enumerate(sentences[:50]):  # Process more sentences
                score = 0
                sentence_words = re.findall(r'\b\w{2,}\b', sentence.lower())
                
                # Frequency score
                for word in sentence_words:
                    if word in word_freq and len(word) > 2:
                        score += word_freq[word]
                
                # Position bonus (early sentences often important)
                if i < 3:
                    score *= 1.5
                elif i < 10:
                    score *= 1.2
                
                # Length bonus for medium-length sentences
                if 10 <= len(sentence_words) <= 25:
                    score *= 1.1
                
                sentence_scores.append((score, i, sentence))
            
            # Select top sentences and trim to target word count
            sentence_scores.sort(reverse=True)
            selected = sentence_scores[:summary_sentences]
            selected.sort(key=lambda x: x[1])  # Restore original order
            
            summary_text = '. '.join([s[2].strip() for s in selected])
            
            # Trim to target word count
            words = summary_text.split()
            if len(words) > target_words:
                summary_text = ' '.join(words[:target_words]) + '...'
            
            # Clean up summary
            summary_text = re.sub(r'\s+', ' ', summary_text).strip()
            
            # Language-specific improvements
            if language.startswith('hi') or 'hindi' in language.lower():
                summary_text = summary_text.replace('।', '. ')
                summary_text = summary_text.replace('॥', '. ')
            
            return {
                'text': summary_text,
                'original_words': word_count,
                'summary_words': len(summary_text.split()),
                'compression': f"{len(summary_text.split())/word_count*100:.1f}%",
                'language': language,
                'sentences_used': len(selected),
                'total_sentences': len(sentences),
                'method': 'Extractive'
            }
            
        except Exception as e:
            print(f"Extractive summary failed: {e}")
            return {
                'text': f'Summary generation failed: {str(e)}',
                'error': str(e),
                'language': language,
                'method': 'error'
            }
    
    def download_transcript(self, video_id, format_type, include_summary=False, summary_words=100):
        """Generate downloadable transcript in various formats"""
        try:
            # Get transcript data
            transcript_data = self.get_ultimate_transcript(video_id, include_summary, summary_words)
            
            if not transcript_data.get('success'):
                return transcript_data
            
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"transcript_{video_id}_{timestamp}"
            
            if format_type.lower() == 'txt':
                content = self.format_as_txt(transcript_data)
                filename += '.txt'
                mime_type = 'text/plain'
                
            elif format_type.lower() == 'json':
                content = json.dumps(transcript_data, indent=2, ensure_ascii=False)
                filename += '.json'
                mime_type = 'application/json'
                
            elif format_type.lower() == 'srt':
                content = self.format_as_srt(transcript_data)
                filename += '.srt'
                mime_type = 'text/plain'
                
            else:
                return {'success': False, 'error': 'Invalid format. Use txt, json, or srt'}
            
            # Encode content for download
            content_b64 = base64.b64encode(content.encode('utf-8')).decode('utf-8')
            
            return {
                'success': True,
                'download': {
                    'filename': filename,
                    'content': content_b64,
                    'mime_type': mime_type,
                    'size': len(content),
                    'format': format_type.upper()
                },
                'transcript_info': {
                    'video_id': video_id,
                    'language': transcript_data.get('language'),
                    'word_count': transcript_data.get('word_count'),
                    'has_summary': include_summary
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def format_as_txt(self, transcript_data):
        """Format transcript as plain text"""
        content = f"YouTube Transcript\n"
        content += f"Video ID: {transcript_data.get('video_id')}\n"
        content += f"Language: {transcript_data.get('language')}\n"
        content += f"Method: {transcript_data.get('method')}\n"
        content += f"Word Count: {transcript_data.get('word_count')}\n"
        content += f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        content += "=" * 50 + "\n\n"
        
        if 'summary' in transcript_data:
            content += "SUMMARY:\n"
            content += transcript_data['summary'].get('text', '') + "\n\n"
            content += "=" * 50 + "\n\n"
        
        content += "FULL TRANSCRIPT:\n"
        content += transcript_data.get('transcript', '')
        
        return content
    
    def format_as_srt(self, transcript_data):
        """Format transcript as SRT subtitle file"""
        transcript_text = transcript_data.get('transcript', '')
        sentences = re.split(r'[.!?]+', transcript_text)
        
        srt_content = ""
        duration_per_sentence = 3  # seconds per sentence
        
        for i, sentence in enumerate(sentences):
            if sentence.strip():
                start_time = i * duration_per_sentence
                end_time = (i + 1) * duration_per_sentence
                
                start_srt = self.seconds_to_srt_time(start_time)
                end_srt = self.seconds_to_srt_time(end_time)
                
                srt_content += f"{i + 1}\n"
                srt_content += f"{start_srt} --> {end_srt}\n"
                srt_content += f"{sentence.strip()}\n\n"
        
        return srt_content
    
    def seconds_to_srt_time(self, seconds):
        """Convert seconds to SRT time format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"
    
    def generate_share_link(self, video_id, include_summary=False, summary_words=100):
        """Generate shareable link and copy-ready content"""
        try:
            # Get transcript data
            transcript_data = self.get_ultimate_transcript(video_id, include_summary, summary_words)
            
            if not transcript_data.get('success'):
                return transcript_data
            
            # Generate share URL
            base_url = "http://localhost:5000"
            share_url = f"{base_url}/transcript/{video_id}"
            if include_summary:
                share_url += f"?summary=true&summary_words={summary_words}"
            
            # Generate copy-ready content
            copy_content = f"YouTube Transcript - Video ID: {video_id}\n"
            copy_content += f"Language: {transcript_data.get('language')}\n"
            copy_content += f"Words: {transcript_data.get('word_count')}\n\n"
            
            if 'summary' in transcript_data:
                copy_content += "SUMMARY:\n"
                copy_content += transcript_data['summary'].get('text', '') + "\n\n"
            
            copy_content += "TRANSCRIPT:\n"
            # Limit transcript for copy (first 1000 words)
            transcript_words = transcript_data.get('transcript', '').split()
            if len(transcript_words) > 1000:
                copy_content += ' '.join(transcript_words[:1000]) + "... [truncated]"
            else:
                copy_content += transcript_data.get('transcript', '')
            
            return {
                'success': True,
                'share': {
                    'url': share_url,
                    'copy_content': copy_content,
                    'short_summary': transcript_data.get('summary', {}).get('text', '')[:200] + '...' if 'summary' in transcript_data else '',
                    'video_info': {
                        'video_id': video_id,
                        'language': transcript_data.get('language'),
                        'word_count': transcript_data.get('word_count')
                    }
                },
                'social_media': {
                    'twitter': f"Check out this YouTube transcript: {share_url}",
                    'facebook': f"YouTube Video Transcript ({transcript_data.get('word_count')} words): {share_url}",
                    'linkedin': f"YouTube Transcript Analysis - {transcript_data.get('language')} - {share_url}",
                    'email_subject': f"YouTube Transcript - Video {video_id}",
                    'email_body': copy_content
                }
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def list_ultimate_transcripts(self, video_id):
        """List all available transcripts with enhanced info"""
        try:
            ytt_api = YouTubeTranscriptApi()
            transcript_list = ytt_api.list(video_id)
            
            languages = []
            for transcript in transcript_list:
                languages.append({
                    'language': transcript.language,
                    'code': transcript.language_code,
                    'generated': transcript.is_generated,
                    'translatable': transcript.is_translatable,
                    'can_translate_to_english': transcript.is_translatable or transcript.language_code == 'en'
                })
            
            return {
                'success': True,
                'languages': languages,
                'video_id': video_id,
                'total_languages': len(languages),
                'english_available': any(lang['code'] == 'en' for lang in languages),
                'translation_possible': any(lang['translatable'] for lang in languages)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
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
    
    print("YouTube Transcript Summarizer Server Starting...")
    print("=" * 60)
    print("✓ Multi-language support")
    print("✓ YouTube translation")
    print("✓ Google Translate fallback")
    print("✓ Multiple extraction methods")
    print("✓ Intelligent video summaries with custom word count")
    print("✓ Download (TXT, JSON, SRT formats)")
    print("✓ Share & Copy functionality")
    print("✓ Hindi/English/Multi-language summaries")
    print("=" * 60)
    print(f"Server running on http://localhost:{PORT}")
    print("\nAPI Endpoints:")
    print(f"• Transcript: /transcript/{{video_id}}?summary=true&summary_words=150")
    print(f"• Download:   /download/{{video_id}}/{{format}}")
    print(f"• Share:      /share/{{video_id}}")
    print(f"• Languages:  /list/{{video_id}}")
    print(f"• Health:     /health")
    print("\nFormats: txt, json, srt")
    print("Summary words: 50-500 (default: 100)")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    try:
        with socketserver.TCPServer(("", PORT), UltimateTranscriptHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")
    except Exception as e:
        print(f"Server error: {e}")
        input("Press Enter to exit...")