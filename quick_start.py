from youtube_transcript_api import YouTubeTranscriptApi

# Replace with any YouTube video ID
video_id = "8S0FDjFBj8o"  # Example: TED talk

try:
    # Get transcript
    api = YouTubeTranscriptApi()
    transcript = api.fetch(video_id)
    
    print(f"Video ID: {video_id}")
    print(f"Language: {transcript.language}")
    print(f"Total snippets: {len(transcript)}")
    print("\nFirst 3 lines:")
    
    for i, snippet in enumerate(transcript[:3]):
        print(f"{i+1}. [{snippet.start:.1f}s] {snippet.text}")
        
except Exception as e:
    print(f"Error: {e}")