import os
import json
import asyncio
import logging
import time
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Configure logging for debugging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Simple in-memory storage (no database)
active_connections: List[WebSocket] = []
conversation_history = []

app = FastAPI(title="AI Sales Assistant MVP", version="0.1.0")

# Enable CORS for Chrome extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add debug middleware to log requests
@app.middleware("http")
async def log_requests(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"📨 {request.method} {request.url.path} - {response.status_code} ({process_time:.3f}s)")
    return response

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    client_ip = websocket.client.host if websocket.client else "unknown"
    logger.info(f"🔌 WebSocket connection attempt from {client_ip}")
    
    try:
        await websocket.accept()
        active_connections.append(websocket)
        client_id = len(active_connections)
        logger.info(f"✅ WebSocket connection #{client_id} accepted")
        
        # Send immediate connection confirmation
        await websocket.send_text(json.dumps({
            "type": "connection",
            "message": "Connected to AI Sales Assistant (Working Mode)",
            "client_id": client_id,
            "timestamp": datetime.now().isoformat()
        }))
        logger.info(f"📤 Sent connection confirmation to client #{client_id}")
        
        while True:
            # Receive data from extension
            try:
                data = await websocket.receive_text()
                message = json.loads(data)
                logger.info(f"📨 Client #{client_id} sent: {message.get('type', 'unknown')}")
                
                if message['type'] == 'audio':
                    # Mock AI suggestions for now
                    logger.info(f"🎵 Processing audio chunk from client #{client_id}...")
                    suggestions = [
                        "That's a great question! Let me explain our pricing structure.",
                        "I understand your concerns. Here's how we can address that.",
                        "Based on what you're describing, our premium plan would be perfect."
                    ]
                    await websocket.send_text(json.dumps({
                        'type': 'suggestions',
                        'suggestions': suggestions,
                        'timestamp': datetime.now().isoformat()
                    }))
                    logger.info(f"💡 Sent {len(suggestions)} mock suggestions")
                
                elif message['type'] == 'test':
                    # Test connection
                    logger.info(f"🧪 Test message from client #{client_id}")
                    await websocket.send_text(json.dumps({
                        'type': 'test_response',
                        'message': 'WebSocket connection working perfectly!',
                        'client_id': client_id,
                        'timestamp': datetime.now().isoformat()
                    }))
                
                else:
                    logger.warning(f"❓ Unknown message type from client #{client_id}: {message.get('type')}")
                    
            except Exception as receive_error:
                logger.error(f"❌ Error receiving data from client #{client_id}: {receive_error}")
                break
                
    except Exception as e:
        logger.error(f"❌ WebSocket connection error: {e}")
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)
            logger.info(f"🔌 Client #{client_id if 'client_id' in locals() else 'unknown'} disconnected")
        else:
            logger.info(f"🔌 Client disconnected (not in active connections)")

@app.get("/health")
async def health_check():
    """Health check with debugging info"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_connections": len(active_connections),
        "conversation_history": len(conversation_history),
        "mode": "working_without_openai",
        "websocket_endpoint": "ws://localhost:8000/ws"
    }

@app.get("/debug/conversation")
async def debug_conversation():
    """Debug endpoint to see conversation history"""
    return {
        "conversation_history": conversation_history,
        "active_connections": len(active_connections),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/")
async def root():
    return {
        "message": "AI Sales Assistant MVP Backend - Working Mode", 
        "status": "running",
        "websocket": "ws://localhost:8000/ws",
        "note": "Running without OpenAI - using mock suggestions"
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting AI Sales Assistant MVP backend (Working Mode)...")
    uvicorn.run(app, host="0.0.0.0", port=8000)