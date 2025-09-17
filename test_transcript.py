#!/usr/bin/env python3
"""
Simple test script for YouTube Transcript API
"""

from youtube_transcript_api import YouTubeTranscriptApi

def test_transcript_api():
    """Test the YouTube Transcript API with a sample video"""
    
    # Using a popular educational video that likely has transcripts
    # This is a TED talk video ID (replace with any video ID you want to test)
    video_id = "8S0FDjFBj8o"  # Sample TED talk video
    
    try:
        print("Testing YouTube Transcript API...")
        print(f"Video ID: {video_id}")
        print("-" * 50)
        
        # Initialize the API
        ytt_api = YouTubeTranscriptApi()
        
        # List available transcripts
        print("Available transcripts:")
        transcript_list = ytt_api.list(video_id)
        
        for transcript in transcript_list:
            print(f"  - {transcript.language} ({transcript.language_code}) - Generated: {transcript.is_generated}")
        
        print("-" * 50)
        
        # Fetch English transcript
        print("Fetching English transcript...")
        transcript = ytt_api.fetch(video_id, languages=['en'])
        
        print(f"Successfully fetched transcript!")
        print(f"Total snippets: {len(transcript)}")
        print(f"Language: {transcript.language}")
        print(f"Auto-generated: {transcript.is_generated}")
        
        print("\nFirst 3 transcript snippets:")
        for i, snippet in enumerate(transcript[:3]):
            print(f"  {i+1}. [{snippet.start:.1f}s] {snippet.text}")
        
        print("\nRaw data format (first snippet):")
        raw_data = transcript.to_raw_data()
        print(f"  {raw_data[0]}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nTry with a different video ID that has transcripts enabled")

def test_cli_functionality():
    """Test CLI functionality"""
    print("\n" + "="*60)
    print("Testing CLI functionality...")
    print("="*60)
    
    # Test with a simple video ID
    video_id = "8S0FDjFBj8o"
    
    try:
        from youtube_transcript_api._cli import YouTubeTranscriptCli
        
        # Test listing transcripts
        cli = YouTubeTranscriptCli([video_id, "--list-transcripts"])
        result = cli.run()
        print("CLI List Transcripts Result:")
        print(result[:500] + "..." if len(result) > 500 else result)
        
    except Exception as e:
        print(f"CLI Error: {e}")

if __name__ == "__main__":
    test_transcript_api()
    test_cli_functionality()
    print("\nTest completed!")