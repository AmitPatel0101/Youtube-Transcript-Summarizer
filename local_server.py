#!/usr/bin/env python3
"""
Local server for YouTube Transcript API
Run this to provide transcript extraction for the Chrome extension
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi
import sys

app = Flask(__name__)
CORS(app)  # Allow requests from Chrome extension

@app.route('/transcript/<video_id>')
def get_transcript(video_id):
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript = ytt_api.fetch(video_id)
        
        # Convert to simple text
        text = '\n'.join([snippet.text for snippet in transcript])
        
        return jsonify({
            'success': True,
            'transcript': text,
            'language': transcript.language,
            'video_id': video_id
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/list/<video_id>')
def list_transcripts(video_id):
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.list(video_id)
        
        languages = []
        for transcript in transcript_list:
            languages.append({
                'language': transcript.language,
                'code': transcript.language_code,
                'generated': transcript.is_generated
            })
        
        return jsonify({
            'success': True,
            'languages': languages,
            'video_id': video_id
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/health')
def health():
    return jsonify({'status': 'running'})

if __name__ == '__main__':
    print("Starting YouTube Transcript API Server...")
    print("Server will run on http://localhost:5000")
    print("Press Ctrl+C to stop")
    
    try:
        app.run(host='localhost', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\nServer stopped")
        sys.exit(0)