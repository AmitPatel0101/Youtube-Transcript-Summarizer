document.addEventListener('DOMContentLoaded', function() {
    const videoUrlInput = document.getElementById('videoUrl');
    const extractBtn = document.getElementById('extractBtn');
    const summaryBtn = document.getElementById('summaryBtn');
    const clearBtn = document.getElementById('clearBtn');
    const status = document.getElementById('status');
    const result = document.getElementById('result');
    const videoInfo = document.getElementById('videoInfo');
    const languageBadge = document.getElementById('languageBadge');
    const methodBadge = document.getElementById('methodBadge');
    const actionControls = document.getElementById('actionControls');
    const copyBtn = document.getElementById('copyBtn');
    const downloadBtn = document.getElementById('downloadBtn');
    const shareBtn = document.getElementById('shareBtn');
    const downloadOptions = document.getElementById('downloadOptions');
    const shareModal = document.getElementById('shareModal');
    
    let currentVideoId = null;
    let currentTranscriptData = null;

    // Initialize
    init();

    async function init() {
        await loadCurrentVideo();
        setupEventListeners();
    }

    function setupEventListeners() {
        extractBtn.addEventListener('click', () => extractTranscript(false));
        summaryBtn.addEventListener('click', () => extractTranscript(true));
        clearBtn.addEventListener('click', clearResults);
        
        copyBtn.addEventListener('click', copyToClipboard);
        downloadBtn.addEventListener('click', toggleDownloadOptions);
        shareBtn.addEventListener('click', showShareModal);
        
        document.getElementById('downloadTxt').addEventListener('click', () => downloadTranscript('txt'));
        document.getElementById('downloadJson').addEventListener('click', () => downloadTranscript('json'));
        document.getElementById('downloadSrt').addEventListener('click', () => downloadTranscript('srt'));
        
        document.getElementById('copyUrlBtn').addEventListener('click', copyShareUrl);
        document.getElementById('copyContentBtn').addEventListener('click', copyShareContent);
        document.getElementById('closeShareBtn').addEventListener('click', hideShareModal);
    }

    async function loadCurrentVideo() {
        try {
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            if (tab.url && tab.url.includes('youtube.com/watch')) {
                const url = new URL(tab.url);
                currentVideoId = url.searchParams.get('v');
                
                videoUrlInput.value = tab.url;
                extractBtn.disabled = false;
                summaryBtn.disabled = false;
                
                if (videoInfo) {
                    videoInfo.style.display = 'flex';
                    languageBadge.textContent = '🌐 Auto-detect';
                    methodBadge.textContent = '🔧 Multi-API Ready';
                }
                
            } else {
                videoUrlInput.placeholder = 'Navigate to a YouTube video';
                extractBtn.disabled = true;
                summaryBtn.disabled = true;
                showStatus('🎯 Please navigate to a YouTube video', 'error');
            }
        } catch (error) {
            extractBtn.disabled = true;
            summaryBtn.disabled = true;
            showStatus('❌ Error loading video information', 'error');
        }
    }

    async function extractTranscript(includeSummary = false) {
        if (!currentVideoId) {
            showStatus('🎯 Please navigate to a YouTube video', 'error');
            return;
        }

        try {
            extractBtn.disabled = true;
            summaryBtn.disabled = true;
            clearBtn.disabled = true;
            
            if (includeSummary) {
                summaryBtn.textContent = 'Generating...';
                showStatus('🧠 Generating summary...', 'loading');
            } else {
                extractBtn.textContent = 'Extracting...';
                showStatus('📝 Extracting transcript...', 'loading');
            }
            
            const summaryLength = document.getElementById('summaryLength').value;
            const summaryParam = includeSummary ? `?summary=true&summary_words=${summaryLength}` : '';
            const response = await fetch(`http://localhost:5000/transcript/${currentVideoId}${summaryParam}`);
            const data = await response.json();
            
            if (data.success) {
                currentTranscriptData = data;
                showStatus('✅ Success!', 'success');
                showResults(data, includeSummary);
                actionControls.style.display = 'flex';
            } else {
                showStatus(`❌ Error: ${data.error}`, 'error');
            }
            
        } catch (error) {
            showStatus(`❌ Connection error. Please start the server.`, 'error');
        } finally {
            extractBtn.disabled = false;
            summaryBtn.disabled = false;
            clearBtn.disabled = false;
            extractBtn.innerHTML = '<span class="btn-icon">📝</span> Extract Transcript';
            summaryBtn.innerHTML = '<span class="btn-icon">🧠</span> Get Summary';
        }
    }

    function showResults(data, includeSummary) {
        let resultHTML = `
            <div class="transcript-info">
                <strong>Language:</strong> ${data.language}<br>
                <strong>Method:</strong> ${data.method}<br>
                <strong>Video ID:</strong> ${data.video_id}<br>
                <strong>Words:</strong> ${data.word_count || 'N/A'}
            </div>
        `;
        
        if (data.summary && includeSummary) {
            resultHTML += `
                <div class="summary-section">
                    <div class="summary-title">📝 Video Summary</div>
                    <div>${data.summary.text}</div>
                    <div class="summary-stats">
                        Original: ${data.summary.original_words} words | 
                        Summary: ${data.summary.summary_words} words | 
                        Compression: ${data.summary.compression}
                    </div>
                </div>
            `;
        }
        
        resultHTML += `
            <div class="transcript-text">
                <strong>Full Transcript:</strong><br>
                ${data.transcript.replace(/\n/g, '<br>')}
            </div>
        `;
        
        result.innerHTML = resultHTML;
        result.style.display = 'block';
        
        // Update video info badges
        if (videoInfo) {
            languageBadge.textContent = `🌐 ${data.language || 'Multi-language'}`;
            methodBadge.textContent = `🔧 ${data.method || 'Multi-API'}`;
        }
    }

    function clearResults() {
        result.style.display = 'none';
        result.innerHTML = '';
        status.style.display = 'none';
        actionControls.style.display = 'none';
        downloadOptions.style.display = 'none';
        currentTranscriptData = null;
    }
    
    async function copyToClipboard() {
        if (!currentTranscriptData) return;
        
        let content = `YouTube Transcript - Video ID: ${currentTranscriptData.video_id}\n`;
        content += `Language: ${currentTranscriptData.language}\n`;
        content += `Words: ${currentTranscriptData.word_count}\n\n`;
        
        if (currentTranscriptData.summary) {
            content += `SUMMARY:\n${currentTranscriptData.summary.text}\n\n`;
        }
        
        content += `TRANSCRIPT:\n${currentTranscriptData.transcript}`;
        
        try {
            await navigator.clipboard.writeText(content);
            showStatus('📋 Copied to clipboard!', 'success');
        } catch (error) {
            showStatus('❌ Failed to copy', 'error');
        }
    }
    
    function toggleDownloadOptions() {
        downloadOptions.style.display = downloadOptions.style.display === 'none' ? 'block' : 'none';
    }
    
    async function downloadTranscript(format) {
        if (!currentVideoId) return;
        
        try {
            const summaryLength = document.getElementById('summaryLength').value;
            const hasSummary = currentTranscriptData && currentTranscriptData.summary;
            
            let url = `http://localhost:5000/download/${currentVideoId}/${format}`;
            if (hasSummary) {
                url += `?summary=true&summary_words=${summaryLength}`;
            }
            
            const response = await fetch(url);
            const data = await response.json();
            
            if (data.success) {
                const content = atob(data.download.content);
                const blob = new Blob([content], { type: data.download.mime_type });
                const url_obj = URL.createObjectURL(blob);
                
                const a = document.createElement('a');
                a.href = url_obj;
                a.download = data.download.filename;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url_obj);
                
                showStatus(`💾 Downloaded ${format.toUpperCase()}!`, 'success');
                downloadOptions.style.display = 'none';
            } else {
                showStatus(`❌ Download failed: ${data.error}`, 'error');
            }
        } catch (error) {
            showStatus(`❌ Download error`, 'error');
        }
    }
    
    function showShareModal() {
        shareModal.style.display = 'flex';
    }
    
    function hideShareModal() {
        shareModal.style.display = 'none';
    }
    
    async function copyShareUrl() {
        if (!currentVideoId) return;
        
        const summaryLength = document.getElementById('summaryLength').value;
        const hasSummary = currentTranscriptData && currentTranscriptData.summary;
        
        let url = `http://localhost:5000/transcript/${currentVideoId}`;
        if (hasSummary) {
            url += `?summary=true&summary_words=${summaryLength}`;
        }
        
        try {
            await navigator.clipboard.writeText(url);
            showStatus('🔗 URL copied!', 'success');
            hideShareModal();
        } catch (error) {
            showStatus('❌ Failed to copy URL', 'error');
        }
    }
    
    async function copyShareContent() {
        if (!currentTranscriptData) return;
        
        try {
            const response = await fetch(`http://localhost:5000/share/${currentVideoId}`);
            const data = await response.json();
            
            if (data.success) {
                await navigator.clipboard.writeText(data.share.copy_content);
                showStatus('📋 Share content copied!', 'success');
                hideShareModal();
            } else {
                showStatus('❌ Failed to generate share content', 'error');
            }
        } catch (error) {
            showStatus('❌ Share error', 'error');
        }
    }

    function showStatus(message, type = 'loading') {
        status.textContent = message;
        status.className = `status ${type}`;
        status.style.display = 'block';
    }

    function hideStatus() {
        status.style.display = 'none';
    }
    
    function getVideoId(url) {
        const match = url.match(/[?&]v=([^&]+)/);
        return match ? match[1] : null;
    }
});