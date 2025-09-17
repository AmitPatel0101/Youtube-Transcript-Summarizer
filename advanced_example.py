#!/usr/bin/env python3
"""
Advanced YouTube Transcript API Example
Shows proxy usage, formatters, and error handling
"""

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import JSONFormatter, SRTFormatter, WebVTTFormatter
from youtube_transcript_api.proxies import GenericProxyConfig
import json

def save_transcript_to_file(transcript, filename, format_type='text'):
    """Save transcript to file in different formats"""
    try:
        if format_type == 'json':
            formatter = JSONFormatter()
            content = formatter.format_transcript(transcript, indent=2)
        elif format_type == 'srt':
            formatter = SRTFormatter()
            content = formatter.format_transcript(transcript)
        elif format_type == 'webvtt':
            formatter = WebVTTFormatter()
            content = formatter.format_transcript(transcript)
        else:  # text
            content = '\n'.join([snippet.text for snippet in transcript])
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"   Saved to {filename}")
        return True
    except Exception as e:
        print(f"   Error saving to {filename}: {e}")
        return False

def main():
    video_id = "8S0FDjFBj8o"  # Example video ID
    
    print("Advanced YouTube Transcript API Example")
    print("=" * 50)
    
    try:
        # 1. Basic API usage
        print("1. Basic transcript extraction:")
        ytt_api = YouTubeTranscriptApi()
        transcript = ytt_api.fetch(video_id)
        print(f"   Successfully fetched {len(transcript)} transcript segments")
        
        # 2. Save in different formats
        print("\n2. Saving transcript in different formats:")
        save_transcript_to_file(transcript, f'transcript_{video_id}.txt', 'text')
        save_transcript_to_file(transcript, f'transcript_{video_id}.json', 'json')
        save_transcript_to_file(transcript, f'transcript_{video_id}.srt', 'srt')
        save_transcript_to_file(transcript, f'transcript_{video_id}.vtt', 'webvtt')
        
        # 3. Multiple languages with fallback
        print("\n3. Multiple language support:")
        try:
            # Try German first, then English as fallback
            transcript_de = ytt_api.fetch(video_id, languages=['de', 'en'])
            print(f"   Retrieved transcript in: {transcript_de.language}")
        except Exception as e:
            print(f"   Language fallback failed: {e}")
        
        # 4. Preserve formatting
        print("\n4. Preserve HTML formatting:")
        try:
            formatted_transcript = ytt_api.fetch(video_id, preserve_formatting=True)
            # Show first snippet with potential formatting
            first_snippet = formatted_transcript[0].text
            print(f"   First snippet with formatting: {first_snippet}")
        except Exception as e:
            print(f"   Formatting preservation failed: {e}")
        
        # 5. List and filter transcripts
        print("\n5. Advanced transcript filtering:")
        transcript_list = ytt_api.list(video_id)
        
        # Find manually created transcripts
        try:
            manual_transcript = transcript_list.find_manually_created_transcript(['en'])
            print(f"   Found manual transcript: {manual_transcript.language}")
        except:
            print("   No manual transcripts found")
        
        # Find auto-generated transcripts
        try:
            auto_transcript = transcript_list.find_generated_transcript(['en'])
            print(f"   Found auto-generated transcript: {auto_transcript.language}")
        except:
            print("   No auto-generated transcripts found")
        
        # 6. Translation capabilities
        print("\n6. Translation example:")
        try:
            en_transcript = transcript_list.find_transcript(['en'])
            if en_transcript.is_translatable:
                print(f"   Available translation languages: {len(en_transcript.translation_languages)}")
                
                # Translate to Spanish
                es_transcript = en_transcript.translate('es')
                es_data = es_transcript.fetch()
                print(f"   Translated first snippet: {es_data[0].text}")
                
                # Save translated version
                save_transcript_to_file(es_data, f'transcript_{video_id}_es.txt', 'text')
            else:
                print("   Translation not available for this transcript")
        except Exception as e:
            print(f"   Translation failed: {e}")
        
        # 7. Error handling examples
        print("\n7. Error handling:")
        
        # Try invalid video ID
        try:
            ytt_api.fetch("invalid_video_id")
        except Exception as e:
            print(f"   Invalid video ID error (expected): {type(e).__name__}")
        
        # Try unavailable language
        try:
            ytt_api.fetch(video_id, languages=['xyz'])
        except Exception as e:
            print(f"   Unavailable language error (expected): {type(e).__name__}")
        
        # 8. Custom HTTP client example
        print("\n8. Custom HTTP client:")
        from requests import Session
        
        custom_session = Session()
        custom_session.headers.update({"User-Agent": "Custom YouTube Transcript Bot"})
        
        custom_api = YouTubeTranscriptApi(http_client=custom_session)
        custom_transcript = custom_api.fetch(video_id)
        print(f"   Custom client fetched {len(custom_transcript)} segments")
        
        print("\n" + "=" * 50)
        print("Advanced example completed successfully!")
        print(f"Check the generated files:")
        print(f"  - transcript_{video_id}.txt")
        print(f"  - transcript_{video_id}.json") 
        print(f"  - transcript_{video_id}.srt")
        print(f"  - transcript_{video_id}.vtt")
        print(f"  - transcript_{video_id}_es.txt (if translation worked)")
        
    except Exception as e:
        print(f"Main error: {e}")
        print("Make sure you have a working internet connection and the video has transcripts")

if __name__ == "__main__":
    main()