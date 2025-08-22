import os
import json
import asyncio
import base64
import logging
import tempfile
import time
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from fastapi import FastAPI, WebSocket, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent / ".env")

# Configure logging for debugging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Simple in-memory storage (no database)
active_connections: List[WebSocket] = []
knowledge_base_content = []
vector_store_id = None
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

# Initialize OpenAI client
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    logger.error("OPENAI_API_KEY not found in environment variables")
    raise ValueError("OPENAI_API_KEY is required")

client = OpenAI(api_key=openai_api_key)
logger.info("OpenAI client initialized successfully")

@app.on_event("startup")
async def setup_vector_store():
    """Create a single shared vector store for MVP"""
    global vector_store_id
    try:
        logger.info("Setting up vector store...")
        # Use the correct API for vector stores
        vector_store = client.beta.vector_stores.create(
            name="mvp_sales_knowledge"
        )
        vector_store_id = vector_store.id
        logger.info(f"✅ Created vector store: {vector_store_id}")
    except AttributeError as e:
        logger.warning(f"⚠️ Vector store API not available: {e}")
        logger.info("📝 Continuing without vector store (basic functionality will work)")
        vector_store_id = None
    except Exception as e:
        logger.error(f"❌ Vector store setup failed: {e}")
        logger.info("📝 Continuing without vector store (basic functionality will work)")
        vector_store_id = None

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
            "message": "Connected to AI Sales Assistant",
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
                    # Process audio and generate suggestions
                    logger.info(f"🎵 Processing audio chunk from client #{client_id}...")
                    suggestions = await process_audio_chunk(message['data'])
                    if suggestions:
                        logger.info(f"💡 Generated {len(suggestions)} suggestions")
                        await websocket.send_text(json.dumps({
                            'type': 'suggestions',
                            'suggestions': suggestions,
                            'timestamp': datetime.now().isoformat()
                        }))
                    else:
                        logger.info("🤐 No suggestions generated (no triggers detected)")
                
                elif message['type'] == 'test':
                    # Test connection
                    logger.info(f"🧪 Test message from client #{client_id}")
                    await websocket.send_text(json.dumps({
                        'type': 'test_response',
                        'message': 'WebSocket connection working!',
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

async def process_audio_chunk(audio_base64: str) -> List[str]:
    """Convert audio to text and generate suggestions"""
    try:
        logger.info("🔊 Starting audio processing...")
        
        # Decode audio
        audio_bytes = base64.b64decode(audio_base64)
        logger.info(f"📊 Audio data size: {len(audio_bytes)} bytes")
        
        # Save to temporary file for Whisper
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_file.write(audio_bytes)
            temp_path = temp_file.name
        
        logger.info(f"💾 Saved audio to: {temp_path}")
        
        # Transcribe with Whisper
        try:
            with open(temp_path, "rb") as audio_file:
                transcription = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
            logger.info(f"🎙️ Transcription: '{transcription[:100]}...'")
        except Exception as whisper_error:
            logger.error(f"❌ Whisper transcription failed: {whisper_error}")
            return []
        
        # Clean up temp file
        os.unlink(temp_path)
        
        # Add to conversation history
        conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "transcript": transcription,
            "type": "user_speech"
        })
        
        # Keep only last 10 entries
        if len(conversation_history) > 10:
            conversation_history.pop(0)
        
        # Check if we should generate suggestions
        if should_generate_suggestions(transcription):
            logger.info("✨ Trigger detected, generating suggestions...")
            suggestions = await generate_suggestions(transcription)
            
            # Log suggestions
            conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "suggestions": suggestions,
                "type": "ai_suggestions"
            })
            
            return suggestions
        else:
            logger.info("⏸️ No triggers detected in transcript")
        
        return []
        
    except Exception as e:
        logger.error(f"❌ Audio processing error: {e}")
        return []

def should_generate_suggestions(text: str) -> bool:
    """Simple trigger detection with logging"""
    triggers = [
        "?",  # Questions
        "how much", "what about", "can you", "do you have",
        "expensive", "cost", "price", "pricing",
        "not sure", "think about it", "concerned about",
        "compared to", "alternative", "competitor"
    ]
    
    text_lower = text.lower()
    detected_triggers = [trigger for trigger in triggers if trigger in text_lower]
    
    if detected_triggers:
        logger.info(f"🎯 Triggers detected: {detected_triggers}")
        return True
    else:
        logger.info("🚫 No triggers found")
        return False

async def generate_suggestions(transcript: str) -> List[str]:
    """Generate AI suggestions using GPT-4 (fallback from GPT-5)"""
    try:
        # Simple knowledge context (if available)
        knowledge_context = "\n".join(knowledge_base_content[:3]) if knowledge_base_content else "No specific product knowledge uploaded yet."
        
        # Get recent conversation context
        recent_context = ""
        if len(conversation_history) >= 2:
            recent_entries = conversation_history[-3:-1]  # Last 2 entries before current
            recent_context = "\n".join([
                f"Previous: {entry.get('transcript', '')}" 
                for entry in recent_entries 
                if entry.get('type') == 'user_speech'
            ])
        
        logger.info(f"🧠 Generating suggestions for: '{transcript[:50]}...'")
        
        # Use GPT-4 as fallback (GPT-5 might not be available yet)
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{
                    "role": "system",
                    "content": """You are a helpful sales assistant. Generate 2-3 specific, actionable response suggestions for a sales representative based on what the customer just said.

                    Guidelines:
                    - Be concise and professional
                    - Address the customer's specific concern
                    - Use available knowledge context when relevant
                    - Provide value-focused responses
                    - Keep each suggestion under 50 words
                    
                    Return as a simple JSON array of strings."""
                }, {
                    "role": "user",
                    "content": f"""
                    Customer just said: "{transcript}"
                    
                    Recent conversation context: {recent_context}
                    
                    Available knowledge: {knowledge_context}
                    
                    Generate 2-3 helpful response suggestions as a JSON array.
                    """
                }],
                max_tokens=300,
                temperature=0.7
            )
            
            suggestions_text = response.choices[0].message.content
            logger.info(f"🤖 GPT-4 response: {suggestions_text[:100]}...")
            
        except Exception as gpt_error:
            logger.warning(f"⚠️ GPT-4 failed, using fallback: {gpt_error}")
            # Simple fallback suggestions
            return [
                "Let me provide more details about that.",
                "That's a great question. Here's what I can tell you...",
                "I understand your concern. Let me address that."
            ]
        
        # Try to parse JSON response
        try:
            suggestions = json.loads(suggestions_text)
            if isinstance(suggestions, list):
                logger.info(f"✅ Successfully parsed {len(suggestions)} suggestions")
                return suggestions[:3]  # Max 3 suggestions
        except json.JSONDecodeError:
            logger.warning("⚠️ Failed to parse JSON, extracting manually")
        
        # Manual extraction fallback
        suggestions = []
        lines = suggestions_text.split('\n')
        for line in lines:
            line = line.strip()
            if line and ('"' in line or line.startswith('-') or line.startswith('•')):
                # Clean up the line
                cleaned = line.replace('"', '').replace('-', '').replace('•', '').strip()
                if cleaned and len(cleaned) > 10:
                    suggestions.append(cleaned)
        
        logger.info(f"📝 Extracted {len(suggestions)} suggestions manually")
        return suggestions[:3]  # Max 3 suggestions
        
    except Exception as e:
        logger.error(f"❌ Suggestion generation error: {e}")
        return ["Let me get back to you with more details on that."]

@app.post("/upload-knowledge")
async def upload_knowledge(files: List[UploadFile] = File(...)):
    """Simple knowledge upload with debugging"""
    global knowledge_base_content, vector_store_id
    
    logger.info(f"📤 Uploading {len(files)} knowledge files...")
    uploaded_files = []
    
    try:
        for file in files:
            logger.info(f"📄 Processing file: {file.filename}")
            
            # Read file content
            content = await file.read()
            
            # Handle different file types
            if file.filename.endswith('.pdf'):
                # Simple PDF text extraction (basic)
                try:
                    text_content = content.decode('utf-8', errors='ignore')
                except:
                    text_content = f"PDF file: {file.filename} (content extraction not implemented)"
            else:
                text_content = content.decode('utf-8', errors='ignore')
            
            # Store in memory for simple access
            file_summary = f"From {file.filename}: {text_content[:500]}..."
            knowledge_base_content.append(file_summary)
            uploaded_files.append(file.filename)
            
            logger.info(f"✅ Processed {file.filename}: {len(text_content)} characters")
            
            # Also upload to vector store if available
            if vector_store_id:
                try:
                    # Create temporary file for upload
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
                        temp_file.write(text_content)
                        temp_path = temp_file.name
                    
                    # Upload to OpenAI
                    openai_file = client.files.create(
                        file=open(temp_path, 'rb'),
                        purpose="assistants"
                    )
                    
                    # Add to vector store
                    client.beta.vector_stores.files.create(
                        vector_store_id=vector_store_id,
                        file_id=openai_file.id
                    )
                    
                    os.unlink(temp_path)
                    logger.info(f"📚 Added {file.filename} to vector store")
                    
                except Exception as vector_error:
                    logger.warning(f"⚠️ Vector store upload failed for {file.filename}: {vector_error}")
        
        logger.info(f"🎉 Successfully uploaded {len(uploaded_files)} files")
        return {
            "message": f"Uploaded {len(files)} files successfully",
            "files": uploaded_files,
            "knowledge_base_size": len(knowledge_base_content)
        }
        
    except Exception as e:
        logger.error(f"❌ Upload failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Upload failed: {str(e)}"}
        )

@app.get("/health")
async def health_check():
    """Health check with debugging info"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "vector_store": vector_store_id,
        "active_connections": len(active_connections),
        "knowledge_base_items": len(knowledge_base_content),
        "conversation_history": len(conversation_history),
        "openai_configured": bool(openai_api_key)
    }

@app.get("/debug/conversation")
async def get_conversation_history():
    """Debug endpoint to view conversation history"""
    return {
        "conversation_history": conversation_history[-10:],  # Last 10 entries
        "total_entries": len(conversation_history)
    }

@app.get("/debug/knowledge")
async def get_knowledge_base():
    """Debug endpoint to view knowledge base"""
    return {
        "knowledge_items": knowledge_base_content,
        "total_items": len(knowledge_base_content),
        "vector_store_id": vector_store_id
    }

@app.post("/test/suggestion")
async def test_suggestion_generation(text: str):
    """Test endpoint for suggestion generation"""
    logger.info(f"🧪 Testing suggestion generation for: '{text}'")
    
    if should_generate_suggestions(text):
        suggestions = await generate_suggestions(text)
        return {
            "input": text,
            "triggered": True,
            "suggestions": suggestions
        }
    else:
        return {
            "input": text,
            "triggered": False,
            "suggestions": []
        }

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting AI Sales Assistant MVP backend...")
    uvicorn.run(app, host="0.0.0.0", port=8000)