#!/usr/bin/env python3
"""
Debug script to test transcript extraction for specific videos
"""

from youtube_transcript_api import YouTubeTranscriptApi
import sys

def debug_video(video_id):
    print(f"Debugging video: {video_id}")
    print("-" * 50)
    
    try:
        # List available transcripts
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        print("Available transcripts:")
        
        for transcript in transcript_list:
            print(f"  - {transcript.language} ({transcript.language_code})")
            print(f"    Generated: {transcript.is_generated}")
            print(f"    Translatable: {transcript.is_translatable}")
        
        print("\nTrying to fetch English transcript...")
        
        # Try direct English
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
            print("✓ Found direct English transcript")
            print(f"First few lines: {transcript[0]['text'][:100]}...")
            return True
        except:
            print("✗ No direct English transcript")
        
        # Try translatable transcripts
        for transcript_info in transcript_list:
            if transcript_info.is_translatable:
                try:
                    english_transcript = transcript_info.translate('en')
                    transcript_data = english_transcript.fetch()
                    print(f"✓ Translated from {transcript_info.language} to English")
                    print(f"First few lines: {transcript_data[0]['text'][:100]}...")
                    return True
                except Exception as e:
                    print(f"✗ Failed to translate from {transcript_info.language}: {e}")
        
        # Try any available transcript
        for transcript_info in transcript_list:
            try:
                transcript_data = transcript_info.fetch()
                print(f"✓ Found transcript in {transcript_info.language}")
                print(f"First few lines: {transcript_data[0]['text'][:100]}...")
                return True
            except Exception as e:
                print(f"✗ Failed to fetch {transcript_info.language}: {e}")
        
        print("✗ No transcripts could be fetched")
        return False
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        video_id = sys.argv[1]
    else:
        video_id = input("Enter YouTube video ID (or full URL): ").strip()
        
        # Extract video ID from URL if needed
        if "youtube.com/watch?v=" in video_id:
            video_id = video_id.split("v=")[1].split("&")[0]
        elif "youtu.be/" in video_id:
            video_id = video_id.split("youtu.be/")[1].split("?")[0]
    
    debug_video(video_id)