#!/usr/bin/env python3
"""
Test script for multi-language support
"""

import requests
import json

def test_video(video_id, description):
    """Test a video with both transcript and summary"""
    print(f"\n{'='*50}")
    print(f"Testing: {description}")
    print(f"Video ID: {video_id}")
    print(f"{'='*50}")
    
    # Test transcript extraction
    print("\n1. Testing transcript extraction...")
    try:
        response = requests.get(f"http://localhost:5000/transcript/{video_id}")
        data = response.json()
        
        if data['success']:
            print(f"✅ Transcript: {data['language']}")
            print(f"   Method: {data['method']}")
            print(f"   Words: {data.get('word_count', 'N/A')}")
            print(f"   Preview: {data['transcript'][:100]}...")
        else:
            print(f"❌ Transcript failed: {data['error']}")
            return
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return
    
    # Test summary generation
    print("\n2. Testing summary generation...")
    try:
        response = requests.get(f"http://localhost:5000/transcript/{video_id}?summary=true")
        data = response.json()
        
        if data['success'] and 'summary' in data:
            summary = data['summary']
            print(f"✅ Summary generated!")
            print(f"   Method: {summary.get('method', 'Unknown')}")
            print(f"   Original: {summary.get('original_words', 'N/A')} words")
            print(f"   Summary: {summary.get('summary_words', 'N/A')} words")
            print(f"   Compression: {summary.get('compression', 'N/A')}")
            print(f"   Text: {summary['text'][:200]}...")
        else:
            print(f"❌ Summary failed: {data.get('error', 'No summary in response')}")
    except Exception as e:
        print(f"❌ Summary error: {e}")

def main():
    print("🚀 ULTIMATE TRANSCRIPT SERVER - LANGUAGE TEST")
    print("Make sure the server is running on localhost:5000")
    
    # Test videos in different languages
    test_videos = [
        ("dQw4w9WgXcQ", "English - Rick Astley (Popular English video)"),
        ("9bZkp7q19f0", "Hindi - Gangnam Style (Has multiple language captions)"),
        ("kJQP7kiw5Fk", "Spanish - Despacito (Popular Spanish video)"),
        ("60ItHLz5WEA", "French - Popular French video"),
        ("hTWKbfoikeg", "German - Nena 99 Luftballons"),
    ]
    
    for video_id, description in test_videos:
        test_video(video_id, description)
        input("\nPress Enter to continue to next test...")
    
    print(f"\n{'='*50}")
    print("🎯 TESTING COMPLETE!")
    print("If any tests failed, check:")
    print("1. Server is running (python advanced_server.py)")
    print("2. Internet connection is working")
    print("3. Video IDs are correct and have captions")
    print("4. API keys are set up (for better summaries)")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()