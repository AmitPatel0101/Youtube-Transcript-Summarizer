#!/usr/bin/env python3
"""
Simple YouTube Transcript API Example
Based on the official documentation
"""

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter, JSONFormatter, SRTFormatter

def main():
    # Example video ID (replace with any YouTube video ID)
    video_id = "8S0FDjFBj8o"  # TED talk example
    
    print("YouTube Transcript API Example")
    print("=" * 40)
    
    try:
        # Initialize API
        ytt_api = YouTubeTranscriptApi()
        
        # 1. Basic transcript fetch
        print("1. Fetching transcript...")
        transcript = ytt_api.fetch(video_id)
        
        print(f"   Video ID: {transcript.video_id}")
        print(f"   Language: {transcript.language}")
        print(f"   Generated: {transcript.is_generated}")
        print(f"   Total snippets: {len(transcript)}")
        
        # 2. Show first few snippets
        print("\n2. First 3 snippets:")
        for i, snippet in enumerate(transcript[:3]):
            print(f"   {i+1}. [{snippet.start:.1f}s] {snippet.text}")
        
        # 3. List available transcripts
        print("\n3. Available transcripts:")
        transcript_list = ytt_api.list(video_id)
        for transcript_info in transcript_list:
            status = "Auto" if transcript_info.is_generated else "Manual"
            translatable = "Yes" if transcript_info.is_translatable else "No"
            print(f"   - {transcript_info.language} ({transcript_info.language_code}) - {status}, Translatable: {translatable}")
        
        # 4. Different languages
        print("\n4. Trying German transcript...")
        try:
            german_transcript = ytt_api.fetch(video_id, languages=['de'])
            print(f"   German transcript found: {german_transcript.language}")
            print(f"   First line: {german_transcript[0].text}")
        except:
            print("   German transcript not available")
        
        # 5. Translation example
        print("\n5. Translation example:")
        try:
            en_transcript = transcript_list.find_transcript(['en'])
            if en_transcript.is_translatable:
                spanish_transcript = en_transcript.translate('es')
                spanish_data = spanish_transcript.fetch()
                print(f"   Translated to Spanish: {spanish_data[0].text}")
            else:
                print("   Translation not available")
        except Exception as e:
            print(f"   Translation failed: {e}")
        
        # 6. Different formats
        print("\n6. Different output formats:")
        
        # Text format
        text_formatter = TextFormatter()
        text_output = text_formatter.format_transcript(transcript)
        print(f"   Text format (first 100 chars): {text_output[:100]}...")
        
        # JSON format
        json_formatter = JSONFormatter()
        json_output = json_formatter.format_transcript(transcript)
        print(f"   JSON format (first 100 chars): {json_output[:100]}...")
        
        # SRT format
        srt_formatter = SRTFormatter()
        srt_output = srt_formatter.format_transcript(transcript)
        print(f"   SRT format (first 200 chars): {srt_output[:200]}...")
        
        # 7. Raw data access
        print("\n7. Raw data access:")
        raw_data = transcript.to_raw_data()
        print(f"   First snippet raw: {raw_data[0]}")
        
        print("\n" + "=" * 40)
        print("Example completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nTry with a different video ID that has transcripts enabled")

if __name__ == "__main__":
    main()