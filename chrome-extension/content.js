// Simple content script for YouTube transcript extraction
(function() {
    'use strict';

    // Add transcript button to YouTube player
    function addTranscriptButton() {
        if (document.getElementById('transcript-extractor-btn')) {
            return;
        }

        const controls = document.querySelector('.ytp-chrome-controls .ytp-right-controls');
        if (!controls) {
            return;
        }

        const button = document.createElement('button');
        button.id = 'transcript-extractor-btn';
        button.className = 'ytp-button transcript-extractor-btn';
        button.title = 'Extract Transcript';
        button.innerHTML = '📄';
        button.style.fontSize = '16px';

        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            extractTranscript();
        });

        controls.insertBefore(button, controls.firstChild);
    }

    // Extract transcript using Python server
    function extractTranscript() {
        const videoId = getVideoIdFromUrl();
        if (!videoId) {
            showNotification('Could not get video ID', 'error');
            return;
        }

        showNotification('Extracting transcript...', 'loading');
        
        fetch(`http://localhost:5000/transcript/${videoId}`)
            .then(response => response.json())
            .then(data => {
                if (data.success && data.transcript) {
                    showTranscriptModal(data.transcript, data.language);
                    showNotification('Transcript extracted!', 'success');
                } else {
                    showNotification(data.error || 'No transcript available', 'error');
                }
            })
            .catch(error => {
                showNotification('Server error. Make sure the Python server is running.', 'error');
                console.error('Transcript extraction error:', error);
            });
    }

    // Get video ID from URL
    function getVideoIdFromUrl() {
        const url = new URL(window.location.href);
        return url.searchParams.get('v');
    }

    // Show notification
    function showNotification(message, type = 'info') {
        const existing = document.getElementById('transcript-notification');
        if (existing) {
            existing.remove();
        }

        const notification = document.createElement('div');
        notification.id = 'transcript-notification';
        notification.className = `transcript-notification ${type}`;
        notification.textContent = message;

        document.body.appendChild(notification);

        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 3000);
    }

    // Show transcript modal
    function showTranscriptModal(transcript, language = 'Unknown') {
        const existing = document.getElementById('transcript-modal');
        if (existing) {
            existing.remove();
        }

        const videoId = getVideoIdFromUrl();
        const modal = document.createElement('div');
        modal.id = 'transcript-modal';
        modal.className = 'transcript-modal';
        modal.innerHTML = `
            <div class="transcript-modal-content">
                <div class="transcript-modal-header">
                    <h3>Transcript - ${videoId}</h3>
                    <p style="margin: 5px 0; font-size: 12px; color: #666;">Language: ${language}</p>
                    <button class="transcript-modal-close">&times;</button>
                </div>
                <div class="transcript-modal-body">
                    <textarea readonly>${transcript}</textarea>
                </div>
                <div class="transcript-modal-footer">
                    <button class="transcript-btn transcript-btn-copy">Copy</button>
                    <button class="transcript-btn transcript-btn-download">Download</button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Event listeners
        modal.querySelector('.transcript-modal-close').addEventListener('click', () => {
            modal.remove();
        });

        modal.querySelector('.transcript-btn-copy').addEventListener('click', () => {
            const textarea = modal.querySelector('textarea');
            navigator.clipboard.writeText(textarea.value).then(() => {
                showNotification('Copied to clipboard!', 'success');
            }).catch(() => {
                textarea.select();
                document.execCommand('copy');
                showNotification('Copied to clipboard!', 'success');
            });
        });

        modal.querySelector('.transcript-btn-download').addEventListener('click', () => {
            const blob = new Blob([transcript], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `transcript_${videoId}.txt`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            showNotification('Download started!', 'success');
        });

        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }

    // Initialize
    function init() {
        const observer = new MutationObserver(() => {
            addTranscriptButton();
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });

        addTranscriptButton();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Handle navigation
    let currentUrl = window.location.href;
    setInterval(() => {
        if (window.location.href !== currentUrl) {
            currentUrl = window.location.href;
            setTimeout(addTranscriptButton, 1000);
        }
    }, 1000);
})();