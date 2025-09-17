#!/usr/bin/env python3
import requests

def test_video(video_id):
    try:
        response = requests.get(f"http://localhost:5000/transcript/{video_id}")
        data = response.json()
        
        if data['success']:
            print(f"SUCCESS: {data['language']}")
            print(f"Method: {data['method']}")
            print(f"Words: {data.get('word_count', 'N/A')}")
        else:
            print(f"FAILED: {data['error']}")
    except Exception as e:
        print(f"Connection error: {e}")
        print("Make sure server is running: python advanced_server.py")

# Test known working video
print("Testing Rick Astley video:")
test_video("dQw4w9WgXcQ")