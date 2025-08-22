#!/usr/bin/env python3
"""
Simple WebSocket test using built-in libraries
"""

import asyncio
import websockets
import json
import sys

async def test_websocket():
    """Test WebSocket connection to backend"""
    try:
        print("🔌 Connecting to WebSocket...")
        
        # Connect to WebSocket
        uri = "ws://localhost:8000/ws"
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected!")
            
            # Wait for connection message
            response = await websocket.recv()
            data = json.loads(response)
            print(f"📥 Received connection message: {data.get('message')}")
            
            # Send test message
            test_message = {
                "type": "test",
                "message": "Python WebSocket test"
            }
            
            await websocket.send(json.dumps(test_message))
            print(f"📤 Sent test message: {test_message}")
            
            # Wait for response
            response = await websocket.recv()
            data = json.loads(response)
            print(f"📥 Received test response: {data.get('message')}")
            
            # Test audio message (mock)
            audio_message = {
                "type": "audio",
                "data": "mock_base64_audio_data"
            }
            
            await websocket.send(json.dumps(audio_message))
            print(f"📤 Sent audio message")
            
            # Wait for suggestions
            response = await websocket.recv()
            data = json.loads(response)
            suggestions = data.get('suggestions', [])
            print(f"💡 Received {len(suggestions)} suggestions:")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"  {i}. {suggestion}")
            
            print("✅ WebSocket test completed successfully!")
            return True
            
    except ConnectionRefusedError:
        print("❌ Connection refused - is the backend running on localhost:8000?")
        return False
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        return False

async def main():
    print("🤖 AI Sales Assistant - WebSocket Connection Test")
    print("=" * 50)
    
    success = await test_websocket()
    
    if success:
        print("\n🎉 WebSocket connection is working perfectly!")
        print("💡 Your backend server is ready for the Chrome extension.")
    else:
        print("\n🚫 WebSocket connection failed")
        print("💡 Check that the backend server is running and accessible.")
    
    return success

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Test interrupted by user")
        sys.exit(1)
