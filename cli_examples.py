#!/usr/bin/env python3
"""
CLI Examples for YouTube Transcript API
Shows how to use the command line interface
"""

import subprocess
import sys

def run_command(cmd):
    """Run a command and return the output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), 1

def main():
    video_id = "8S0FDjFBj8o"  # Example video ID
    
    print("YouTube Transcript API - CLI Examples")
    print("=" * 50)
    
    # Example 1: Basic transcript extraction
    print("1. Basic transcript extraction:")
    cmd = f"python -m youtube_transcript_api {video_id}"
    print(f"   Command: {cmd}")
    stdout, stderr, code = run_command(cmd)
    if code == 0:
        print(f"   Output (first 200 chars): {stdout[:200]}...")
    else:
        print(f"   Error: {stderr}")
    
    print("\n" + "-" * 30)
    
    # Example 2: JSON format
    print("2. JSON format output:")
    cmd = f"python -m youtube_transcript_api {video_id} --format json"
    print(f"   Command: {cmd}")
    stdout, stderr, code = run_command(cmd)
    if code == 0:
        print(f"   Output (first 200 chars): {stdout[:200]}...")
    else:
        print(f"   Error: {stderr}")
    
    print("\n" + "-" * 30)
    
    # Example 3: List available transcripts
    print("3. List available transcripts:")
    cmd = f"python -m youtube_transcript_api --list-transcripts {video_id}"
    print(f"   Command: {cmd}")
    stdout, stderr, code = run_command(cmd)
    if code == 0:
        print(f"   Output: {stdout}")
    else:
        print(f"   Error: {stderr}")
    
    print("\n" + "-" * 30)
    
    # Example 4: Specific language
    print("4. Specific language (German):")
    cmd = f"python -m youtube_transcript_api {video_id} --languages de"
    print(f"   Command: {cmd}")
    stdout, stderr, code = run_command(cmd)
    if code == 0:
        print(f"   Output (first 200 chars): {stdout[:200]}...")
    else:
        print(f"   Error: {stderr}")
    
    print("\n" + "-" * 30)
    
    # Example 5: Translation
    print("5. Translation to Spanish:")
    cmd = f"python -m youtube_transcript_api {video_id} --languages en --translate es"
    print(f"   Command: {cmd}")
    stdout, stderr, code = run_command(cmd)
    if code == 0:
        print(f"   Output (first 200 chars): {stdout[:200]}...")
    else:
        print(f"   Error: {stderr}")
    
    print("\n" + "=" * 50)
    print("CLI examples completed!")

if __name__ == "__main__":
    main()