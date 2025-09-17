// Test script to verify extension functionality
console.log('YouTube Transcript Extractor - Test Script');

// Test the background script
chrome.runtime.sendMessage({
    action: 'test',
    data: 'Extension is working'
}, function(response) {
    console.log('Extension response:', response);
});

// Test video ID extraction
function testVideoIdExtraction() {
    const testUrls = [
        'https://www.youtube.com/watch?v=8S0FDjFBj8o',
        'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        'https://www.youtube.com/watch?v=abc123'
    ];
    
    testUrls.forEach(url => {
        const urlObj = new URL(url);
        const videoId = urlObj.searchParams.get('v');
        console.log(`URL: ${url} -> Video ID: ${videoId}`);
    });
}

testVideoIdExtraction();