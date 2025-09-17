// YouTube Transcript Extractor - Using Local Server
console.log('YouTube Transcript Extractor - Background script loaded');

class YouTubeTranscriptAPI {
    constructor() {
        this.serverUrl = 'http://localhost:5000';
    }

    async checkServer() {
        try {
            const response = await fetch(`${this.serverUrl}/health`);
            return response.ok;
        } catch (error) {
            return false;
        }
    }

    async fetchTranscript(videoId, languages = ['en'], format = 'text') {
        try {
            // Check if server is running
            const serverRunning = await this.checkServer();
            if (!serverRunning) {
                throw new Error('Local server not running. Please start simple_server.py first.');
            }

            const response = await fetch(`${this.serverUrl}/transcript/${videoId}`);
            const data = await response.json();

            if (data.success) {
                return data.transcript;
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            if (error.message.includes('fetch')) {
                throw new Error('Cannot connect to local server. Make sure to run: python simple_server.py');
            }
            throw error;
        }
    }

    async listTranscripts(videoId) {
        try {
            const serverRunning = await this.checkServer();
            if (!serverRunning) {
                throw new Error('Local server not running. Please start simple_server.py first.');
            }

            const response = await fetch(`${this.serverUrl}/list/${videoId}`);
            const data = await response.json();

            if (data.success) {
                let result = `Available transcripts for ${videoId}:\n\n`;
                data.languages.forEach((lang, index) => {
                    const type = lang.generated ? '(Auto-generated)' : '(Manual)';
                    result += `${index + 1}. ${lang.language} (${lang.code}) ${type}\n`;
                });
                return result;
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            if (error.message.includes('fetch')) {
                throw new Error('Cannot connect to local server. Make sure to run: python simple_server.py');
            }
            throw error;
        }
    }

    async generateSummary(videoId, maxWords = 1500) {
        try {
            const serverRunning = await this.checkServer();
            if (!serverRunning) {
                throw new Error('Local server not running. Please start simple_server.py first.');
            }

            const response = await fetch(`${this.serverUrl}/summary/${videoId}?words=${maxWords}`);
            const data = await response.json();

            if (data.success) {
                return data;
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            if (error.message.includes('fetch')) {
                throw new Error('Cannot connect to local server. Make sure to run: python simple_server.py');
            }
            throw error;
        }
    }
}

// Initialize API
const transcriptAPI = new YouTubeTranscriptAPI();

// Handle messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log('Background script received message:', request);
    
    if (request.action === 'extractTranscript') {
        console.log('Extracting transcript for video:', request.videoId);
        transcriptAPI.fetchTranscript(request.videoId, ['en'], request.format)
            .then(data => {
                console.log('Transcript extracted successfully');
                sendResponse({ success: true, data: data });
            })
            .catch(error => {
                console.error('Transcript extraction failed:', error);
                sendResponse({ success: false, error: error.message });
            });
        return true;
    }
    
    if (request.action === 'listTranscripts') {
        console.log('Listing transcripts for video:', request.videoId);
        transcriptAPI.listTranscripts(request.videoId)
            .then(data => {
                console.log('Transcript list retrieved successfully');
                sendResponse({ success: true, data: data });
            })
            .catch(error => {
                console.error('Transcript listing failed:', error);
                sendResponse({ success: false, error: error.message });
            });
        return true;
    }
    
    if (request.action === 'generateSummary') {
        console.log('Generating summary for video:', request.videoId);
        transcriptAPI.generateSummary(request.videoId, request.maxWords)
            .then(data => {
                console.log('Summary generated successfully');
                sendResponse({ success: true, data: data });
            })
            .catch(error => {
                console.error('Summary generation failed:', error);
                sendResponse({ success: false, error: error.message });
            });
        return true;
    }
    
    sendResponse({ success: false, error: 'Unknown action' });
});