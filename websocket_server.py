#!/usr/bin/env python3
"""
Simple WebSocket server for AI Sales Assistant
Uses only the websockets library that's already installed
"""

import asyncio
import websockets
import json
import logging
import os
import time
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# OpenAI API key will be loaded from environment variable OPENAI_API_KEY
# Set it in .env file or export OPENAI_API_KEY="your-key-here"

# Simple in-memory storage
active_connections = set()
conversation_history = []

async def handle_client(websocket, path):
    """Handle a WebSocket client connection"""
    client_ip = websocket.remote_address[0] if websocket.remote_address else "unknown"
    client_id = len(active_connections) + 1
    
    logger.info(f"🔌 WebSocket connection #{client_id} from {client_ip}")
    
    # Add to active connections
    active_connections.add(websocket)
    
    try:
        # Send connection confirmation
        welcome_message = {
            "type": "connection",
            "message": "Connected to AI Sales Assistant WebSocket Server",
            "client_id": client_id,
            "timestamp": datetime.now().isoformat()
        }
        
        await websocket.send(json.dumps(welcome_message))
        logger.info(f"📤 Sent welcome message to client #{client_id}")
        
        # Handle incoming messages
        async for message in websocket:
            try:
                data = json.loads(message)
                message_type = data.get('type', 'unknown')
                
                logger.info(f"📨 Client #{client_id} sent: {message_type}")
                
                if message_type == 'test':
                    # Handle test message
                    response = {
                        "type": "test_response",
                        "message": "WebSocket server is working correctly!",
                        "client_id": client_id,
                        "timestamp": datetime.now().isoformat(),
                        "original_message": data.get('message', '')
                    }
                    
                    await websocket.send(json.dumps(response))
                    logger.info(f"📤 Sent test response to client #{client_id}")
                    
                elif message_type == 'audio':
                    # Handle audio data (simplified for MVP)
                    logger.info(f"🎵 Received audio data from client #{client_id}")
                    
                    # Simple trigger detection (no actual audio processing for this demo)
                    mock_suggestions = [
                        "That's a great question about pricing. Let me share our value proposition with you.",
                        "I understand your concern. Here are the key benefits that justify the investment.",
                        "Many of our clients had similar questions initially. Here's what they found most valuable."
                    ]
                    
                    response = {
                        "type": "suggestions",
                        "suggestions": mock_suggestions,
                        "timestamp": datetime.now().isoformat(),
                        "note": "Demo suggestions - full AI integration requires OpenAI setup"
                    }
                    
                    await websocket.send(json.dumps(response))
                    logger.info(f"💡 Sent {len(mock_suggestions)} suggestions to client #{client_id}")
                    
                else:
                    logger.warning(f"❓ Unknown message type from client #{client_id}: {message_type}")
                    
            except json.JSONDecodeError:
                logger.error(f"❌ Invalid JSON from client #{client_id}")
            except Exception as e:
                logger.error(f"❌ Error processing message from client #{client_id}: {e}")
                
    except websockets.exceptions.ConnectionClosed:
        logger.info(f"🔌 Client #{client_id} disconnected normally")
    except Exception as e:
        logger.error(f"❌ Error with client #{client_id}: {e}")
    finally:
        # Remove from active connections
        active_connections.discard(websocket)
        logger.info(f"📱 Client #{client_id} removed from active connections")

async def health_server():
    """Simple HTTP server for health checks"""
    from http.server import HTTPServer, BaseHTTPRequestHandler
    import threading
    
    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/health':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                health_data = {
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "active_connections": len(active_connections),
                    "websocket_port": 8000,
                    "server_type": "Simple WebSocket Server",
                    "openai_configured": bool(os.getenv("OPENAI_API_KEY"))
                }
                
                self.wfile.write(json.dumps(health_data, indent=2).encode())
                logger.info(f"📊 Health check requested - {len(active_connections)} active connections")
            else:
                self.send_response(404)
                self.end_headers()
        
        def log_message(self, format, *args):
            # Suppress default HTTP server logs
            pass
    
    def run_health_server():
        server = HTTPServer(('localhost', 8001), HealthHandler)
        server.serve_forever()
    
    # Start HTTP health server in background thread
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()
    logger.info("🏥 Health server started on http://localhost:8001/health")

async def main():
    """Main server function"""
    print("🚀 AI Sales Assistant - WebSocket Server Starting")
    print("=" * 60)
    print("📡 WebSocket Server: ws://localhost:8000/ws")
    print("🏥 Health Check: http://localhost:8001/health") 
    print("🤖 OpenAI API: Configured" if os.getenv("OPENAI_API_KEY") else "❌ Not configured")
    print("📝 Note: This is a simplified server for MVP testing")
    print("⏹️  Press Ctrl+C to stop")
    print("=" * 60)
    
    # Start health server
    await health_server()
    
    # Start WebSocket server
    logger.info("🎯 Starting WebSocket server on port 8000")
    
    try:
        async with websockets.serve(handle_client, "localhost", 8000):
            logger.info("✅ WebSocket server running successfully!")
            print("✅ Server is ready! Extension should now connect.")
            print("\n📋 Expected Chrome Extension behavior:")
            print("   - Extension detects connection")
            print("   - Overlay shows 'Connected to AI backend'")
            print("   - Test by saying trigger phrases in meetings")
            print()
            
            # Keep the server running
            await asyncio.Future()  # Run forever
            
    except OSError as e:
        if "Address already in use" in str(e):
            logger.error("❌ Port 8000 is already in use")
            print("\n💡 Port 8000 is busy. Try:")
            print("   - Stop any other servers running")
            print("   - Check with: netstat -tulpn | grep :8000")
            print("   - Or change port in the extension")
        else:
            logger.error(f"❌ Failed to start server: {e}")
    except KeyboardInterrupt:
        logger.info("🛑 Server stopped by user")
        print("\n👋 WebSocket server stopped")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    asyncio.run(main())