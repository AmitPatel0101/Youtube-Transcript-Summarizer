#!/usr/bin/env python3
"""
YouTube Transcript API Demo
Demonstrates various features of the API
"""

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter, JSONFormatter, SRTFormatter

def main():
    print("YouTube Transcript API Demo")
    print("=" * 40)
    
    # Sample video ID (TED talk)
    video_id = "8S0FDjFBj8o"
    
    try:
        # Initialize API
        api = YouTubeTranscriptApi()
        
        # 1. List available transcripts
        print("1. Available transcripts:")
        transcript_list = api.list(video_id)
        for transcript in transcript_list:
            status = "Auto-generated" if transcript.is_generated else "Manual"
            translatable = "Translatable" if transcript.is_translatable else "Not translatable"
            print(f"   - {transcript.language} ({transcript.language_code}) - {status}, {translatable}")
        
        print("\n" + "-" * 40)
        
        # 2. Fetch English transcript
        print("2. Fetching English transcript...")
        transcript = api.fetch(video_id, languages=['en'])
        print(f"   Language: {transcript.language}")
        print(f"   Total snippets: {len(transcript)}")
        print(f"   Auto-generated: {transcript.is_generated}")
        
        # Show first few snippets
        print("\n   First 3 snippets:")
        for i, snippet in enumerate(transcript[:3]):
            print(f"   {i+1}. [{snippet.start:.1f}s - {snippet.start + snippet.duration:.1f}s] {snippet.text[:50]}...")
        
        print("\n" + "-" * 40)
        
        # 3. Different output formats
        print("3. Different output formats:")
        
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
        
        print("\n" + "-" * 40)
        
        # 4. Translation example
        print("4. Translation example:")
        transcript_obj = transcript_list.find_transcript(['en'])
        if transcript_obj.is_translatable:
            # Translate to Spanish
            spanish_transcript = transcript_obj.translate('es')
            spanish_data = spanish_transcript.fetch()
            print(f"   Translated to Spanish: {spanish_data.language}")
            print(f"   First snippet: {spanish_data[0].text}")
        else:
            print("   Transcript is not translatable")
        
        print("\n" + "=" * 40)
        print("Demo completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()