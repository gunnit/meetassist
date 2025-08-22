#!/usr/bin/env python3
import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws"
    print(f"🔌 Connecting to {uri}...")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected!")
            
            # Send test message
            test_message = {
                "type": "test",
                "message": "Hello from Python client"
            }
            await websocket.send(json.dumps(test_message))
            print(f"📤 Sent: {test_message}")
            
            # Receive messages
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"📨 Received: {response}")
                
                # Try to parse JSON
                try:
                    data = json.loads(response)
                    print(f"📋 Parsed JSON: {data}")
                except:
                    print("⚠️ Response is not JSON")
                    
            except asyncio.TimeoutError:
                print("⏰ No response received within 5 seconds")
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
