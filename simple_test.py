#!/usr/bin/env python3
"""
Simple connection test without external dependencies
"""

import urllib.request
import json

def test_backend():
    """Test if backend is running"""
    print("🔍 Testing backend connection...")
    
    try:
        # Test health endpoint
        response = urllib.request.urlopen("http://localhost:8000/health", timeout=5)
        data = json.loads(response.read())
        
        print("✅ Backend is running!")
        print(f"📊 Status: {data.get('status')}")
        print(f"🔌 Active connections: {data.get('active_connections', 0)}")
        print(f"📚 Knowledge items: {data.get('knowledge_base_items', 0)}")
        print(f"🤖 OpenAI configured: {data.get('openai_configured', False)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Backend test failed: {e}")
        print("💡 Make sure the backend is running with: python3 restart_server.py")
        return False

def test_javascript_websocket():
    """Create a JavaScript test that can be pasted in browser console"""
    
    js_test = """
// === AI Sales Assistant WebSocket Test ===
// Paste this in your browser console (F12) on any webpage

console.log('🧪 Starting WebSocket test...');

const socket = new WebSocket('ws://localhost:8000/ws');
let testCompleted = false;

socket.onopen = (event) => {
    console.log('✅ WebSocket connected!');
    
    // Send test message
    const testMsg = {
        type: 'test',
        message: 'Browser console test'
    };
    
    socket.send(JSON.stringify(testMsg));
    console.log('📤 Sent test message:', testMsg);
};

socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('📥 Received:', data);
    
    if (data.type === 'connection') {
        console.log('✅ Connection confirmed:', data.message);
    }
    
    if (data.type === 'test_response') {
        console.log('✅ Test successful!', data.message);
        testCompleted = true;
        socket.close();
    }
};

socket.onclose = (event) => {
    if (testCompleted) {
        console.log('✅ WebSocket test completed successfully!');
        console.log('🎉 Your backend WebSocket is working correctly!');
    } else {
        console.log('❌ WebSocket closed unexpectedly:', event.code, event.reason);
    }
};

socket.onerror = (error) => {
    console.log('❌ WebSocket error:', error);
    console.log('💡 Check if backend is running on localhost:8000');
};

// Cleanup after 10 seconds
setTimeout(() => {
    if (socket.readyState === WebSocket.OPEN) {
        console.log('🕐 Test timeout - closing connection');
        socket.close();
    }
}, 10000);
"""
    
    return js_test

def main():
    print("🤖 AI Sales Assistant - Simple Connection Test")
    print("=" * 50)
    
    # Test backend HTTP
    backend_ok = test_backend()
    
    if backend_ok:
        print("\n🧪 WebSocket Test Instructions:")
        print("=" * 50)
        print("Since WebSocket libraries have compatibility issues,")
        print("let's test directly in the browser:")
        print()
        print("1. Open Chrome")
        print("2. Go to any webpage (like google.com)")
        print("3. Press F12 to open DevTools")
        print("4. Go to Console tab")
        print("5. Copy and paste this JavaScript code:")
        print()
        print("-" * 50)
        print(test_javascript_websocket())
        print("-" * 50)
        print()
        print("6. Press Enter to run the test")
        print("7. You should see '✅ Test successful!' if it works")
        print()
        print("💡 If the WebSocket test works in the browser,")
        print("   then the issue is specifically with the Chrome extension.")
    else:
        print("\n💡 Fix the backend first, then test WebSocket connection.")
    
    print("\n📋 Next Steps:")
    print("- If WebSocket works: Debug Chrome extension")
    print("- If WebSocket fails: Check server logs for connection attempts")
    print("- Look for firewall/antivirus blocking localhost:8000")

if __name__ == "__main__":
    main()