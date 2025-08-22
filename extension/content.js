// AI Sales Assistant - Content Script with Enhanced Debugging
console.log('🤖 AI Sales Assistant: Content script loaded');

// Prevent multiple initialization
if (window.aiAssistant) {
  console.log('🔄 AI Sales Assistant already loaded, skipping...');
  return;
}

class SalesAssistant {
  constructor() {
    this.socket = null;
    this.isListening = false;
    this.audioStream = null;
    this.audioContext = null;
    this.processor = null;
    this.overlay = null;
    this.debugMode = true;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    
    // Initialize
    this.init();
  }

  log(message, type = 'info') {
    const timestamp = new Date().toLocaleTimeString();
    const emoji = {
      info: '💡',
      success: '✅', 
      error: '❌',
      warning: '⚠️',
      debug: '🐛'
    }[type] || '📝';
    
    console.log(`${emoji} [${timestamp}] AI Assistant: ${message}`);
    
    // Also show in overlay if available
    if (this.overlay && this.debugMode) {
      this.updateStatus(`${emoji} ${message}`);
    }
  }

  async init() {
    this.log('Initializing AI Sales Assistant...');
    
    // Wait for page to load
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => this.start());
    } else {
      this.start();
    }
  }

  async start() {
    this.log('Starting on meeting platform...');
    
    // Check if we're on a supported platform
    const hostname = window.location.hostname;
    if (!this.isSupportedPlatform(hostname)) {
      this.log(`Platform ${hostname} not supported`, 'warning');
      return;
    }
    
    this.log(`Detected platform: ${hostname}`, 'success');
    
    // Wait a bit for the meeting to load
    setTimeout(() => {
      this.connectWebSocket();
      this.createUI();
    }, 3000);
  }

  isSupportedPlatform(hostname) {
    return hostname.includes('meet.google.com') || 
           hostname.includes('zoom.us');
  }

  connectWebSocket() {
    this.log('Connecting to backend...');
    
    try {
      this.socket = new WebSocket('ws://localhost:8000/ws');
      
      this.socket.onopen = (event) => {
        this.log('Connected to backend!', 'success');
        this.reconnectAttempts = 0;
        this.updateStatus('🔗 Connected to AI backend');
        
        // Send test message
        this.sendMessage({
          type: 'test',
          message: 'Extension connected'
        });
      };

      this.socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        this.handleMessage(data);
      };

      this.socket.onclose = (event) => {
        this.log(`WebSocket closed: ${event.code} - ${event.reason}`, 'warning');
        this.updateStatus('🔌 Disconnected - trying to reconnect...');
        this.attemptReconnect();
      };

      this.socket.onerror = (error) => {
        this.log(`WebSocket error: ${error}`, 'error');
        this.updateStatus('❌ Connection error');
      };

    } catch (error) {
      this.log(`Failed to create WebSocket: ${error}`, 'error');
      this.updateStatus('❌ Backend connection failed');
    }
  }

  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
      
      this.log(`Reconnect attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts} in ${delay/1000}s`);
      
      setTimeout(() => {
        this.connectWebSocket();
      }, delay);
    } else {
      this.log('Max reconnection attempts reached', 'error');
      this.updateStatus('❌ Connection failed - please reload page');
    }
  }

  sendMessage(message) {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(message));
      return true;
    } else {
      this.log('WebSocket not ready for sending', 'warning');
      return false;
    }
  }

  handleMessage(data) {
    this.log(`Received message: ${data.type}`);
    
    switch (data.type) {
      case 'connection':
        this.log(`Backend says: ${data.message}`, 'success');
        this.updateStatus(`✅ ${data.message}`);
        // Start audio capture after successful connection
        setTimeout(() => this.startAudioCapture(), 1000);
        break;
        
      case 'suggestions':
        this.log(`Received ${data.suggestions.length} suggestions`, 'success');
        this.displaySuggestions(data.suggestions);
        break;
        
      case 'test_response':
        this.log(`Test response: ${data.message}`, 'success');
        break;
        
      default:
        this.log(`Unknown message type: ${data.type}`, 'warning');
    }
  }

  async startAudioCapture() {
    this.log('Starting audio capture...');
    
    try {
      // Check if getDisplayMedia is available
      if (!navigator.mediaDevices || !navigator.mediaDevices.getDisplayMedia) {
        throw new Error('getDisplayMedia not supported by this browser');
      }
      
      // Request screen/tab capture with audio
      this.audioStream = await navigator.mediaDevices.getDisplayMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100
        },
        video: false
      });

      this.log('Audio stream obtained', 'success');
      
      // Create audio processing pipeline
      this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
      const source = this.audioContext.createMediaStreamSource(this.audioStream);
      
      // Create processor for audio chunks
      this.processor = this.audioContext.createScriptProcessor(4096, 1, 1);
      
      this.processor.onaudioprocess = (event) => {
        if (this.isListening) {
          const audioData = event.inputBuffer.getChannelData(0);
          this.processAudioChunk(audioData);
        }
      };

      source.connect(this.processor);
      this.processor.connect(this.audioContext.destination);
      
      this.isListening = true;
      this.updateStatus('🎧 Listening to audio...');
      this.log('Audio processing started', 'success');
      
      // Handle stream end
      this.audioStream.getAudioTracks()[0].addEventListener('ended', () => {
        this.log('Audio stream ended', 'warning');
        this.stopAudioCapture();
      });
      
    } catch (error) {
      this.log(`Audio capture failed: ${error.message}`, 'error');
      
      if (error.message.includes('getDisplayMedia not supported')) {
        this.updateStatus('❌ Browser does not support screen capture');
        this.showBrowserHelp();
      } else if (error.message.includes('Permission denied')) {
        this.updateStatus('❌ Screen capture permission denied');
        this.showAudioHelp();
      } else {
        this.updateStatus('❌ Audio capture failed - check permissions');
        this.showAudioHelp();
      }
    }
  }

  processAudioChunk(audioData) {
    // Convert audio data to base64 for transmission
    const buffer = new ArrayBuffer(audioData.length * 4);
    const view = new Float32Array(buffer);
    
    for (let i = 0; i < audioData.length; i++) {
      view[i] = audioData[i];
    }
    
    // Convert to base64
    const bytes = new Uint8Array(buffer);
    let binary = '';
    for (let i = 0; i < bytes.length; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    const base64 = btoa(binary);
    
    // Send to backend (throttle to avoid spam)
    if (this.lastAudioSent && Date.now() - this.lastAudioSent < 2000) {
      return; // Wait at least 2 seconds between sends
    }
    
    this.sendMessage({
      type: 'audio',
      data: base64
    });
    
    this.lastAudioSent = Date.now();
  }

  stopAudioCapture() {
    this.log('Stopping audio capture...');
    
    this.isListening = false;
    
    if (this.audioStream) {
      this.audioStream.getTracks().forEach(track => track.stop());
      this.audioStream = null;
    }
    
    if (this.processor) {
      this.processor.disconnect();
      this.processor = null;
    }
    
    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }
    
    this.updateStatus('⏹️ Audio capture stopped');
  }

  createUI() {
    this.log('Creating UI overlay...');
    
    // Remove existing overlay
    if (this.overlay) {
      this.overlay.remove();
    }
    
    // Create main overlay
    this.overlay = document.createElement('div');
    this.overlay.id = 'ai-sales-overlay';
    this.overlay.innerHTML = `
      <div class="ai-assistant-container">
        <div class="ai-header">
          <span class="ai-title">🤖 AI Sales Assistant</span>
          <div class="ai-controls">
            <button class="ai-btn minimize-btn" title="Minimize">−</button>
            <button class="ai-btn close-btn" title="Close">×</button>
          </div>
        </div>
        
        <div class="ai-status" id="ai-status">
          🔄 Initializing...
        </div>
        
        <div class="ai-suggestions" id="ai-suggestions">
          <div class="no-suggestions">
            💡 AI suggestions will appear here when you ask questions or discuss pricing
          </div>
        </div>
        
        <div class="ai-debug" id="ai-debug" style="display: ${this.debugMode ? 'block' : 'none'}">
          <details>
            <summary>🐛 Debug Info</summary>
            <div id="debug-content">Debug info will appear here...</div>
          </details>
        </div>
      </div>
    `;
    
    // Add CSS styles
    this.addStyles();
    
    // Add event listeners
    this.overlay.querySelector('.minimize-btn').onclick = () => this.toggleMinimize();
    this.overlay.querySelector('.close-btn').onclick = () => this.closeOverlay();
    
    // Make draggable
    this.makeDraggable(this.overlay.querySelector('.ai-header'));
    
    // Add to page
    document.body.appendChild(this.overlay);
    
    this.log('UI overlay created', 'success');
  }

  addStyles() {
    const styles = `
      #ai-sales-overlay {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 999999;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 14px;
        width: 350px;
        max-height: 600px;
        background: white;
        border: 2px solid #007bff;
        border-radius: 12px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.2);
        overflow: hidden;
      }
      
      .ai-assistant-container {
        display: flex;
        flex-direction: column;
        height: 100%;
      }
      
      .ai-header {
        background: linear-gradient(135deg, #007bff, #0056b3);
        color: white;
        padding: 12px 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        cursor: move;
        user-select: none;
      }
      
      .ai-title {
        font-weight: 600;
        font-size: 16px;
      }
      
      .ai-controls {
        display: flex;
        gap: 8px;
      }
      
      .ai-btn {
        background: rgba(255,255,255,0.2);
        border: none;
        color: white;
        width: 24px;
        height: 24px;
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
      }
      
      .ai-btn:hover {
        background: rgba(255,255,255,0.3);
      }
      
      .ai-status {
        padding: 12px 16px;
        background: #f8f9fa;
        border-bottom: 1px solid #e9ecef;
        font-size: 13px;
        color: #495057;
      }
      
      .ai-suggestions {
        padding: 16px;
        max-height: 300px;
        overflow-y: auto;
      }
      
      .no-suggestions {
        color: #6c757d;
        font-style: italic;
        text-align: center;
        padding: 20px;
      }
      
      .suggestion-item {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 8px;
        position: relative;
      }
      
      .suggestion-text {
        color: #212529;
        line-height: 1.4;
        margin-bottom: 8px;
      }
      
      .suggestion-actions {
        display: flex;
        gap: 8px;
      }
      
      .copy-btn {
        background: #007bff;
        color: white;
        border: none;
        padding: 6px 12px;
        border-radius: 4px;
        cursor: pointer;
        font-size: 12px;
        transition: background 0.2s;
      }
      
      .copy-btn:hover {
        background: #0056b3;
      }
      
      .copy-btn.copied {
        background: #28a745;
      }
      
      .ai-debug {
        border-top: 1px solid #e9ecef;
        padding: 12px 16px;
        background: #f8f9fa;
        font-size: 12px;
      }
      
      .ai-debug details summary {
        cursor: pointer;
        color: #6c757d;
      }
      
      .ai-debug details[open] summary {
        margin-bottom: 8px;
      }
      
      #debug-content {
        background: white;
        padding: 8px;
        border-radius: 4px;
        border: 1px solid #dee2e6;
        font-family: monospace;
        font-size: 11px;
        max-height: 100px;
        overflow-y: auto;
      }
      
      .minimized {
        height: auto !important;
      }
      
      .minimized .ai-suggestions,
      .minimized .ai-debug {
        display: none !important;
      }
    `;
    
    // Remove existing styles
    const existingStyles = document.getElementById('ai-assistant-styles');
    if (existingStyles) {
      existingStyles.remove();
    }
    
    // Add new styles
    const styleSheet = document.createElement('style');
    styleSheet.id = 'ai-assistant-styles';
    styleSheet.textContent = styles;
    document.head.appendChild(styleSheet);
  }

  makeDraggable(header) {
    let isDragging = false;
    let currentX, currentY, initialX, initialY;
    
    header.addEventListener('mousedown', (e) => {
      isDragging = true;
      initialX = e.clientX - this.overlay.offsetLeft;
      initialY = e.clientY - this.overlay.offsetTop;
    });
    
    document.addEventListener('mousemove', (e) => {
      if (isDragging) {
        e.preventDefault();
        currentX = e.clientX - initialX;
        currentY = e.clientY - initialY;
        this.overlay.style.left = currentX + 'px';
        this.overlay.style.top = currentY + 'px';
        this.overlay.style.right = 'auto';
      }
    });
    
    document.addEventListener('mouseup', () => {
      isDragging = false;
    });
  }

  updateStatus(message) {
    const statusEl = document.getElementById('ai-status');
    if (statusEl) {
      statusEl.textContent = message;
    }
  }

  displaySuggestions(suggestions) {
    const suggestionsEl = document.getElementById('ai-suggestions');
    if (!suggestionsEl) return;
    
    suggestionsEl.innerHTML = suggestions.map((suggestion, index) => `
      <div class="suggestion-item">
        <div class="suggestion-text">${this.escapeHtml(suggestion)}</div>
        <div class="suggestion-actions">
          <button class="copy-btn" onclick="window.aiAssistant.copySuggestion('${this.escapeHtml(suggestion)}', this)">
            📋 Copy
          </button>
        </div>
      </div>
    `).join('');
    
    // Flash the overlay to draw attention
    this.overlay.style.borderColor = '#28a745';
    setTimeout(() => {
      this.overlay.style.borderColor = '#007bff';
    }, 1000);
  }

  copySuggestion(text, button) {
    navigator.clipboard.writeText(text).then(() => {
      const originalText = button.textContent;
      button.textContent = '✅ Copied!';
      button.classList.add('copied');
      
      setTimeout(() => {
        button.textContent = originalText;
        button.classList.remove('copied');
      }, 2000);
      
      this.log('Suggestion copied to clipboard', 'success');
    }).catch(err => {
      this.log('Failed to copy suggestion', 'error');
    });
  }

  toggleMinimize() {
    this.overlay.classList.toggle('minimized');
  }

  closeOverlay() {
    if (this.overlay) {
      this.overlay.style.display = 'none';
      this.stopAudioCapture();
    }
  }

  showAudioHelp() {
    const suggestionsEl = document.getElementById('ai-suggestions');
    if (!suggestionsEl) return;
    
    suggestionsEl.innerHTML = `
      <div style="padding: 20px; text-align: center; color: #dc3545;">
        <h4>🎤 Audio Capture Setup</h4>
        <p>To enable AI suggestions:</p>
        <ol style="text-align: left; margin: 16px 0;">
          <li>Click "Share your screen" when prompted</li>
          <li>Select "Chrome Tab" or "Entire Screen"</li>
          <li><strong>Make sure "Share audio" is checked</strong></li>
          <li>Click "Share"</li>
        </ol>
        <button class="copy-btn" onclick="window.aiAssistant.startAudioCapture()" style="margin-top: 12px;">
          🔄 Try Again
        </button>
      </div>
    `;
  }

  showBrowserHelp() {
    const suggestionsEl = document.getElementById('ai-suggestions');
    if (!suggestionsEl) return;
    
    suggestionsEl.innerHTML = `
      <div style="padding: 20px; text-align: center; color: #dc3545;">
        <h4>🌐 Browser Compatibility Issue</h4>
        <p>Your browser doesn't support screen capture with audio.</p>
        <div style="text-align: left; margin: 16px 0;">
          <p><strong>Requirements:</strong></p>
          <ul>
            <li>Chrome 72+ or Firefox 66+</li>
            <li>HTTPS connection (secure context)</li>
            <li>Screen capture permissions enabled</li>
          </ul>
        </div>
        <p style="color: #6c757d; font-size: 12px;">The extension will still work for UI testing without audio capture.</p>
      </div>
    `;
  }

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML.replace(/'/g, '&apos;');
  }
}

// Initialize the assistant when the content script loads
window.aiAssistant = new SalesAssistant();

// Global error handler
window.addEventListener('error', (event) => {
  console.error('🚨 AI Assistant Error:', event.error);
});

// Log when content script is ready
console.log('✅ AI Sales Assistant content script ready');