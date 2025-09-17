#!/usr/bin/env python3
"""
Test script to verify multi-language transcript extraction
"""

import requests
import json

def test_transcript_extraction(video_id, description=""):
    """Test transcript extraction for a given video ID"""
    print(f"\n{'='*50}")
    print(f"Testing: {description}")
    print(f"Video ID: {video_id}")
    print(f"{'='*50}")
    
    try:
        # Test transcript extraction
        print("1. Testing transcript extraction...")
        response = requests.get(f"http://localhost:5000/transcript/{video_id}")
        data = response.json()
        
        if data.get('success'):
            transcript = data.get('transcript', '')
            language = data.get('language', 'Unknown')
            print(f"✅ SUCCESS: Got transcript in {language}")
            print(f"   Length: {len(transcript)} characters")
            print(f"   Preview: {transcript[:100]}...")
        else:
            print(f"❌ FAILED: {data.get('error', 'Unknown error')}")
            return False
        
        # Test summary generation
        print("\n2. Testing summary generation (1500 words)...")
        response = requests.get(f"http://localhost:5000/summary/{video_id}?words=1500")
        data = response.json()
        
        if data.get('success'):
            summary = data.get('summary', '')
            original_length = data.get('original_length', 0)
            summary_length = data.get('summary_length', 0)
            language = data.get('language', 'Unknown')
            print(f"✅ SUCCESS: Generated summary")
            print(f"   Original: {original_length} words")
            print(f"   Summary: {summary_length} words")
            print(f"   Language: {language}")
            print(f"   Preview: {summary[:150]}...")
        else:
            print(f"❌ FAILED: {data.get('error', 'Unknown error')}")
            return False
            
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to server. Make sure to run 'python simple_server.py' first!")
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def main():
    print("YouTube Transcript Multi-Language Test")
    print("Make sure the server is running: python simple_server.py")
    
    # Test cases with different languages
    test_cases = [
        # English video
        ("dQw4w9WgXcQ", "English video (Rick Roll)"),
        
        # Add more test cases here with different language videos
        # You can replace these with actual video IDs you want to test
        # ("VIDEO_ID_HERE", "Description of video language"),
    ]
    
    print(f"\nRunning {len(test_cases)} test cases...")
    
    success_count = 0
    for video_id, description in test_cases:
        if test_transcript_extraction(video_id, description):
            success_count += 1
    
    print(f"\n{'='*50}")
    print(f"RESULTS: {success_count}/{len(test_cases)} tests passed")
    print(f"{'='*50}")
    
    if success_count == len(test_cases):
        print("🎉 All tests passed! Your extension should work with any language video.")
    else:
        print("⚠️  Some tests failed. Check the server logs for details.")

if __name__ == "__main__":
    main()