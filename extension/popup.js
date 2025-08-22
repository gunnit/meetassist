// AI Sales Assistant - Popup Script
console.log('🤖 AI Sales Assistant: Popup script loaded');

class PopupManager {
  constructor() {
    this.backendUrl = 'http://localhost:8000';
    this.init();
  }

  async init() {
    // Set up event listeners
    this.setupEventListeners();
    
    // Load initial status
    await this.refreshStatus();
    
    // Set up periodic status updates
    setInterval(() => this.refreshStatus(), 30000); // Every 30 seconds
  }

  setupEventListeners() {
    // Refresh status button
    document.getElementById('refresh-status').addEventListener('click', () => {
      this.refreshStatus();
    });

    // File upload
    const fileInput = document.getElementById('fileInput');
    const uploadArea = document.getElementById('upload-area');
    const uploadBtn = document.getElementById('uploadBtn');

    // Click to select files
    uploadArea.addEventListener('click', () => {
      fileInput.click();
    });

    // File selection change
    fileInput.addEventListener('change', () => {
      this.updateUploadArea();
    });

    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
      e.preventDefault();
      uploadArea.classList.add('drag-over');
    });

    uploadArea.addEventListener('dragleave', () => {
      uploadArea.classList.remove('drag-over');
    });

    uploadArea.addEventListener('drop', (e) => {
      e.preventDefault();
      uploadArea.classList.remove('drag-over');
      
      const files = Array.from(e.dataTransfer.files);
      const validFiles = files.filter(file => 
        file.name.toLowerCase().endsWith('.pdf') ||
        file.name.toLowerCase().endsWith('.txt') ||
        file.name.toLowerCase().endsWith('.md')
      );
      
      if (validFiles.length > 0) {
        // Update file input
        const dt = new DataTransfer();
        validFiles.forEach(file => dt.items.add(file));
        fileInput.files = dt.files;
        this.updateUploadArea();
      }
    });

    // Upload button
    uploadBtn.addEventListener('click', () => {
      this.uploadFiles();
    });
  }

  updateUploadArea() {
    const fileInput = document.getElementById('fileInput');
    const uploadArea = document.getElementById('upload-area');
    
    if (fileInput.files.length > 0) {
      const fileNames = Array.from(fileInput.files).map(f => f.name).join(', ');
      uploadArea.innerHTML = `
        <div class="file-icon">✅</div>
        <div class="upload-text">
          ${fileInput.files.length} file(s) selected<br>
          <small>${fileNames}</small>
        </div>
      `;
    } else {
      uploadArea.innerHTML = `
        <div class="file-icon">📄</div>
        <div class="upload-text">
          Click to select files or drag & drop<br>
          <small>Supports: PDF, TXT, MD files</small>
        </div>
      `;
    }
  }

  async refreshStatus() {
    console.log('🔄 Refreshing status...');
    
    // Check backend connection
    await this.checkBackendStatus();
    
    // Check current platform
    await this.checkPlatformStatus();
    
    // Check knowledge base
    await this.checkKnowledgeStatus();
    
    // Update debug info
    await this.updateDebugInfo();
  }

  async checkBackendStatus() {
    const statusEl = document.getElementById('backend-status');
    
    try {
      const response = await fetch(`${this.backendUrl}/health`);
      if (response.ok) {
        const data = await response.json();
        statusEl.textContent = '✅ Connected';
        statusEl.className = 'status-value status-success';
        
        // Update knowledge status from health data
        const knowledgeEl = document.getElementById('knowledge-status');
        knowledgeEl.textContent = `📚 ${data.knowledge_base_items || 0} items`;
        knowledgeEl.className = 'status-value status-success';
        
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      statusEl.textContent = '❌ Disconnected';
      statusEl.className = 'status-value status-error';
      console.log('Backend connection failed:', error);
    }
  }

  async checkPlatformStatus() {
    const statusEl = document.getElementById('platform-status');
    
    try {
      // Get current tab info
      const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
      const currentTab = tabs[0];
      
      if (currentTab && currentTab.url) {
        const url = currentTab.url;
        
        if (url.includes('meet.google.com')) {
          statusEl.textContent = '✅ Google Meet';
          statusEl.className = 'status-value status-success';
        } else if (url.includes('zoom.us')) {
          statusEl.textContent = '✅ Zoom';
          statusEl.className = 'status-value status-success';
        } else {
          statusEl.textContent = '⚠️ Not on meeting platform';
          statusEl.className = 'status-value status-warning';
        }
      } else {
        statusEl.textContent = '❓ Unknown';
        statusEl.className = 'status-value status-warning';
      }
    } catch (error) {
      statusEl.textContent = '❌ Error';
      statusEl.className = 'status-value status-error';
      console.log('Platform detection failed:', error);
    }
  }

  async checkKnowledgeStatus() {
    const statusEl = document.getElementById('knowledge-status');
    
    try {
      const response = await fetch(`${this.backendUrl}/debug/knowledge`);
      if (response.ok) {
        const data = await response.json();
        const count = data.total_items || 0;
        
        if (count > 0) {
          statusEl.textContent = `📚 ${count} items`;
          statusEl.className = 'status-value status-success';
        } else {
          statusEl.textContent = '📚 Empty (upload files)';
          statusEl.className = 'status-value status-warning';
        }
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      statusEl.textContent = '❌ Error loading';
      statusEl.className = 'status-value status-error';
    }
  }

  async updateDebugInfo() {
    const debugEl = document.getElementById('debug-content');
    
    try {
      // Gather debug information
      const debugInfo = {
        timestamp: new Date().toISOString(),
        extension_version: chrome.runtime.getManifest().version,
        backend_url: this.backendUrl
      };

      // Get backend health if available
      try {
        const healthResponse = await fetch(`${this.backendUrl}/health`);
        if (healthResponse.ok) {
          debugInfo.backend_health = await healthResponse.json();
        }
      } catch (e) {
        debugInfo.backend_error = e.message;
      }

      // Get current tab info
      try {
        const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
        debugInfo.current_tab = {
          url: tabs[0]?.url,
          title: tabs[0]?.title,
          id: tabs[0]?.id
        };
      } catch (e) {
        debugInfo.tab_error = e.message;
      }

      debugEl.textContent = JSON.stringify(debugInfo, null, 2);
      
    } catch (error) {
      debugEl.textContent = `Debug info error: ${error.message}`;
    }
  }

  async uploadFiles() {
    const fileInput = document.getElementById('fileInput');
    const uploadBtn = document.getElementById('uploadBtn');
    const messageEl = document.getElementById('upload-message');
    
    if (fileInput.files.length === 0) {
      this.showMessage('Please select files to upload', 'error');
      return;
    }

    // Disable button and show progress
    uploadBtn.disabled = true;
    uploadBtn.textContent = '📤 Uploading...';
    
    try {
      const formData = new FormData();
      
      for (let file of fileInput.files) {
        formData.append('files', file);
      }
      
      const response = await fetch(`${this.backendUrl}/upload-knowledge`, {
        method: 'POST',
        body: formData
      });
      
      if (response.ok) {
        const result = await response.json();
        this.showMessage(
          `✅ Successfully uploaded ${result.files?.length || fileInput.files.length} files!`,
          'success'
        );
        
        // Clear file input
        fileInput.value = '';
        this.updateUploadArea();
        
        // Refresh status to show updated knowledge count
        setTimeout(() => this.refreshStatus(), 1000);
        
      } else {
        const error = await response.json();
        throw new Error(error.error || `HTTP ${response.status}`);
      }
      
    } catch (error) {
      console.error('Upload failed:', error);
      this.showMessage(`❌ Upload failed: ${error.message}`, 'error');
      
    } finally {
      // Re-enable button
      uploadBtn.disabled = false;
      uploadBtn.textContent = '📤 Upload Files';
    }
  }

  showMessage(text, type = 'info') {
    const messageEl = document.getElementById('upload-message');
    
    messageEl.textContent = text;
    messageEl.className = `message ${type}`;
    messageEl.style.display = 'block';
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
      messageEl.style.display = 'none';
    }, 5000);
  }
}

// Initialize popup when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  console.log('✅ Popup DOM ready, initializing...');
  window.popupManager = new PopupManager();
});

// Handle popup unload
window.addEventListener('beforeunload', () => {
  console.log('👋 Popup closing');
});