#!/usr/bin/env python3
"""
Quick test to check if a video has transcripts
"""

import requests
import sys

def test_video(video_id):
    try:
        response = requests.get(f"http://localhost:5000/transcript/{video_id}")
        data = response.json()
        
        if data['success']:
            print(f"✅ SUCCESS: {data['language']}")
            print(f"Method: {data['method']}")
            print(f"Words: {data.get('word_count', 'N/A')}")
        else:
            print(f"❌ FAILED: {data['error']}")
            if 'details' in data:
                print(f"Details: {data['details']}")
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    # Test with a known working video
    print("Testing with Rick Astley (known to have captions):")
    test_video("dQw4w9WgXcQ")
    
    print("\nTesting with your video:")
    if len(sys.argv) > 1:
        test_video(sys.argv[1])
    else:
        print("Usage: python test_video.py VIDEO_ID")