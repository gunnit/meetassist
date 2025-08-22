// AI Sales Assistant - Background Service Worker
console.log('🤖 AI Sales Assistant: Background script loaded');

// Handle extension installation
chrome.runtime.onInstalled.addListener((details) => {
  console.log('✅ AI Sales Assistant installed:', details.reason);
  
  if (details.reason === 'install') {
    // Show welcome notification
    chrome.notifications?.create({
      type: 'basic',
      iconUrl: 'icon48.png',
      title: 'AI Sales Assistant',
      message: 'Extension installed! Visit Google Meet or Zoom to start.'
    });
  }
});

// Handle tab updates to inject content script if needed
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.url) {
    const url = tab.url;
    
    // Check if this is a meeting platform
    if (url.includes('meet.google.com') || url.includes('zoom.us')) {
      console.log(`📱 Meeting platform detected: ${url}`);
      
      // Ensure content script is injected (in case it failed)
      chrome.scripting.executeScript({
        target: { tabId: tabId },
        files: ['content.js']
      }).catch(err => {
        console.log('Content script already injected or failed:', err.message);
      });
    }
  }
});

// Handle messages from content script or popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('📨 Background received message:', message);
  
  switch (message.type) {
    case 'get_tab_info':
      // Send tab information back
      sendResponse({
        tabId: sender.tab?.id,
        url: sender.tab?.url,
        title: sender.tab?.title
      });
      break;
      
    case 'test_backend':
      // Test backend connection
      testBackendConnection()
        .then(result => sendResponse(result))
        .catch(err => sendResponse({ error: err.message }));
      return true; // Keep message channel open for async response
      
    default:
      console.log('❓ Unknown message type:', message.type);
  }
});

// Test backend connection
async function testBackendConnection() {
  try {
    const response = await fetch('http://localhost:8000/health');
    if (response.ok) {
      const data = await response.json();
      return { 
        status: 'success', 
        message: 'Backend connected!',
        data: data
      };
    } else {
      throw new Error(`Backend returned ${response.status}`);
    }
  } catch (error) {
    return { 
      status: 'error', 
      message: 'Backend connection failed',
      error: error.message
    };
  }
}

// Handle extension startup
chrome.runtime.onStartup.addListener(() => {
  console.log('🚀 AI Sales Assistant: Extension startup');
});

// Handle browser action (extension icon click)
chrome.action?.onClicked.addListener((tab) => {
  console.log('🖱️ Extension icon clicked');
  
  // Open popup (this is handled automatically by manifest)
  // But we can add additional logic here if needed
});

// Periodic health check (optional)
setInterval(async () => {
  try {
    const result = await testBackendConnection();
    if (result.status === 'error') {
      console.log('⚠️ Backend health check failed:', result.message);
    }
  } catch (error) {
    // Silently ignore errors in periodic check
  }
}, 60000); // Check every minute

console.log('✅ AI Sales Assistant background script ready');