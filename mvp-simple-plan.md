# AI Sales Assistant - Simple MVP for Friends Testing

## Overview
A minimal viable product for testing the core concept with friends - no authentication, no billing, just the essential AI suggestion functionality during online meetings.

## Simplified Architecture
```
Chrome Extension ←→ Simple Backend ←→ OpenAI APIs
     (React)          (FastAPI)        (GPT-5 + Whisper)
```

## Core Features (MVP Only)
1. **Audio Capture**: Listen to meeting audio from browser tabs
2. **Speech-to-Text**: Convert audio to text using Whisper
3. **AI Suggestions**: Generate helpful responses using GPT-5
4. **Simple UI**: Floating overlay with copy-paste suggestions
5. **Basic Knowledge**: Upload a few PDFs for context

## Technology Stack (Minimal)

### Frontend (Chrome Extension)
- **React** + **TypeScript** (simple setup)
- **Chrome Tab Capture API** for audio
- **WebSocket** for backend communication
- **No authentication** - just start using

### Backend (Simple API)
- **FastAPI** (Python) - minimal setup
- **WebSocket** for real-time communication
- **OpenAI Python SDK** for all AI features
- **No database** - everything in memory/files

### OpenAI Services
- **GPT-5** for suggestion generation
- **Whisper** for speech transcription
- **Vector Store** for knowledge base (1 shared store)

---

## Simplified Implementation

### 1. Chrome Extension (4 files total)

#### `manifest.json`
```json
{
  "manifest_version": 3,
  "name": "AI Sales Assistant MVP",
  "version": "0.1.0",
  "permissions": ["tabCapture", "activeTab"],
  "host_permissions": [
    "https://meet.google.com/*",
    "https://zoom.us/*"
  ],
  "background": {
    "service_worker": "background.js"
  },
  "content_scripts": [{
    "matches": ["https://meet.google.com/*", "https://zoom.us/*"],
    "js": ["content.js"]
  }],
  "action": {
    "default_popup": "popup.html"
  }
}
```

#### `content.js` (Audio Capture)
```javascript
// Simple audio capture and WebSocket communication
class SimpleSalesAssistant {
  constructor() {
    this.socket = new WebSocket('ws://localhost:8000/ws')
    this.isListening = false
    this.audioStream = null
  }

  async startListening() {
    try {
      // Capture tab audio
      this.audioStream = await navigator.mediaDevices.getDisplayMedia({
        audio: true,
        video: false
      })
      
      // Create audio processor
      const audioContext = new AudioContext()
      const source = audioContext.createMediaStreamSource(this.audioStream)
      const processor = audioContext.createScriptProcessor(4096, 1, 1)
      
      processor.onaudioprocess = (event) => {
        const audioData = event.inputBuffer.getChannelData(0)
        this.sendAudioToBackend(audioData)
      }
      
      source.connect(processor)
      processor.connect(audioContext.destination)
      
      this.isListening = true
      this.showUI()
      
    } catch (error) {
      console.error('Audio capture failed:', error)
    }
  }

  sendAudioToBackend(audioData) {
    if (this.socket.readyState === WebSocket.OPEN) {
      // Convert audio to base64 and send
      const buffer = audioData.buffer
      const base64 = btoa(String.fromCharCode(...new Uint8Array(buffer)))
      this.socket.send(JSON.stringify({
        type: 'audio',
        data: base64
      }))
    }
  }

  showUI() {
    // Create simple floating UI
    const overlay = document.createElement('div')
    overlay.id = 'ai-sales-overlay'
    overlay.innerHTML = `
      <div style="position: fixed; top: 20px; right: 20px; z-index: 10000; 
                  background: white; border: 2px solid #007bff; border-radius: 8px; 
                  padding: 16px; max-width: 300px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
        <h3>🤖 AI Sales Assistant</h3>
        <div id="status">🎧 Listening...</div>
        <div id="suggestions"></div>
        <button onclick="this.parentElement.style.display='none'">Hide</button>
      </div>
    `
    document.body.appendChild(overlay)

    // Handle suggestions from backend
    this.socket.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'suggestions') {
        this.displaySuggestions(data.suggestions)
      }
    }
  }

  displaySuggestions(suggestions) {
    const suggestionsDiv = document.getElementById('suggestions')
    suggestionsDiv.innerHTML = suggestions.map((suggestion, index) => `
      <div style="margin: 8px 0; padding: 8px; background: #f8f9fa; border-radius: 4px;">
        <p style="margin: 0; font-size: 14px;">${suggestion}</p>
        <button onclick="navigator.clipboard.writeText('${suggestion}')" 
                style="margin-top: 4px; padding: 4px 8px; background: #007bff; 
                       color: white; border: none; border-radius: 3px; cursor: pointer;">
          Copy
        </button>
      </div>
    `).join('')
  }
}

// Auto-start when on meeting page
if (window.location.hostname.includes('meet.google.com') || 
    window.location.hostname.includes('zoom.us')) {
  const assistant = new SimpleSalesAssistant()
  
  // Start listening after 3 seconds (let meeting load)
  setTimeout(() => assistant.startListening(), 3000)
}
```

#### `popup.html` (Simple Settings)
```html
<!DOCTYPE html>
<html>
<head>
  <style>
    body { width: 300px; padding: 16px; }
    .upload-area { border: 2px dashed #ccc; padding: 20px; text-align: center; }
  </style>
</head>
<body>
  <h2>AI Sales Assistant</h2>
  
  <h3>Upload Knowledge Base</h3>
  <div class="upload-area">
    <input type="file" id="fileInput" accept=".pdf,.txt,.md" multiple>
    <p>Drop PDF/TXT files here</p>
  </div>
  
  <button id="uploadBtn">Upload Files</button>
  <div id="status"></div>
  
  <script>
    document.getElementById('uploadBtn').onclick = async () => {
      const files = document.getElementById('fileInput').files
      if (files.length === 0) return
      
      const formData = new FormData()
      for (let file of files) {
        formData.append('files', file)
      }
      
      try {
        const response = await fetch('http://localhost:8000/upload-knowledge', {
          method: 'POST',
          body: formData
        })
        
        if (response.ok) {
          document.getElementById('status').innerHTML = '✅ Files uploaded!'
        } else {
          document.getElementById('status').innerHTML = '❌ Upload failed'
        }
      } catch (error) {
        document.getElementById('status').innerHTML = '❌ Connection error'
      }
    }
  </script>
</body>
</html>
```

### 2. Simple Backend (3 files total)

#### `main.py` (Complete Backend)
```python
import os
import json
import asyncio
import base64
from typing import List
from fastapi import FastAPI, WebSocket, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import tempfile

# Simple in-memory storage (no database)
active_connections: List[WebSocket] = []
knowledge_base_content = []
vector_store_id = None

app = FastAPI(title="AI Sales Assistant MVP")

# Enable CORS for Chrome extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.on_event("startup")
async def setup_vector_store():
    """Create a single shared vector store for MVP"""
    global vector_store_id
    try:
        vector_store = await client.vector_stores.create(
            name="mvp_sales_knowledge"
        )
        vector_store_id = vector_store.id
        print(f"Created vector store: {vector_store_id}")
    except Exception as e:
        print(f"Vector store setup failed: {e}")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:
            # Receive audio data from extension
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message['type'] == 'audio':
                # Process audio and generate suggestions
                suggestions = await process_audio_chunk(message['data'])
                if suggestions:
                    await websocket.send_text(json.dumps({
                        'type': 'suggestions',
                        'suggestions': suggestions
                    }))
                    
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        active_connections.remove(websocket)

async def process_audio_chunk(audio_base64: str) -> List[str]:
    """Convert audio to text and generate suggestions"""
    try:
        # Decode audio
        audio_bytes = base64.b64decode(audio_base64)
        
        # Save to temporary file for Whisper
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_file.write(audio_bytes)
            temp_path = temp_file.name
        
        # Transcribe with Whisper
        with open(temp_path, "rb") as audio_file:
            transcription = await client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
        
        # Clean up temp file
        os.unlink(temp_path)
        
        # Check if we should generate suggestions
        if should_generate_suggestions(transcription):
            return await generate_suggestions(transcription)
        
        return []
        
    except Exception as e:
        print(f"Audio processing error: {e}")
        return []

def should_generate_suggestions(text: str) -> bool:
    """Simple trigger detection"""
    triggers = [
        "?",  # Questions
        "how much", "what about", "can you", "do you have",
        "expensive", "cost", "price",
        "not sure", "think about it"
    ]
    
    text_lower = text.lower()
    return any(trigger in text_lower for trigger in triggers)

async def generate_suggestions(transcript: str) -> List[str]:
    """Generate AI suggestions using GPT-5"""
    try:
        # Simple knowledge context (if available)
        knowledge_context = "\n".join(knowledge_base_content[:3]) if knowledge_base_content else ""
        
        response = await client.responses.create(
            model="gpt-5",
            reasoning_effort="low",  # Fast responses
            verbosity="low",         # Concise suggestions
            input=[{
                "role": "user",
                "content": f"""
                You are a sales assistant. The customer just said: "{transcript}"
                
                Knowledge context: {knowledge_context}
                
                Provide 2-3 helpful, specific response suggestions for the sales rep.
                Return as simple numbered list:
                1. [suggestion]
                2. [suggestion] 
                3. [suggestion]
                """
            }]
        )
        
        # Parse numbered suggestions
        suggestions_text = response.output_text
        suggestions = []
        for line in suggestions_text.split('\n'):
            if line.strip() and (line.strip().startswith('1.') or 
                               line.strip().startswith('2.') or 
                               line.strip().startswith('3.')):
                suggestion = line.strip()[2:].strip()  # Remove "1. "
                suggestions.append(suggestion)
        
        return suggestions[:3]  # Max 3 suggestions
        
    except Exception as e:
        print(f"Suggestion generation error: {e}")
        return ["Let me get back to you with more details on that."]

@app.post("/upload-knowledge")
async def upload_knowledge(files: List[UploadFile] = File(...)):
    """Simple knowledge upload - no auth needed"""
    global knowledge_base_content, vector_store_id
    
    try:
        for file in files:
            # Read file content
            content = await file.read()
            text_content = content.decode('utf-8')
            
            # Store in memory for simple access
            knowledge_base_content.append(f"From {file.filename}: {text_content[:1000]}...")
            
            # Also upload to vector store if available
            if vector_store_id:
                # Create temporary file for upload
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
                    temp_file.write(text_content)
                    temp_path = temp_file.name
                
                # Upload to OpenAI
                openai_file = await client.files.create(
                    file=open(temp_path, 'rb'),
                    purpose="assistants"
                )
                
                # Add to vector store
                await client.vector_stores.files.create(
                    vector_store_id=vector_store_id,
                    file_id=openai_file.id
                )
                
                os.unlink(temp_path)
        
        return {"message": f"Uploaded {len(files)} files successfully"}
        
    except Exception as e:
        return {"error": f"Upload failed: {str(e)}"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "vector_store": vector_store_id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### `requirements.txt`
```
fastapi==0.104.0
uvicorn==0.24.0
websockets==12.0
openai==1.68.0
python-multipart==0.0.6
```

#### `run.py` (Simple Startup Script)
```python
#!/usr/bin/env python3
import os
import sys
import subprocess

def check_requirements():
    """Check if OpenAI API key is set"""
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("Set it like: export OPENAI_API_KEY='your-key-here'")
        sys.exit(1)
    print("✅ OpenAI API key found")

def install_dependencies():
    """Install required packages"""
    print("📦 Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    print("✅ Dependencies installed")

def start_server():
    """Start the FastAPI server"""
    print("🚀 Starting AI Sales Assistant backend...")
    print("🌐 Server will run at: http://localhost:8000")
    print("📡 WebSocket endpoint: ws://localhost:8000/ws")
    print("📤 Knowledge upload: http://localhost:8000/upload-knowledge")
    print("\n🔧 Load the Chrome extension and start a meeting to test!")
    
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    check_requirements()
    install_dependencies()
    start_server()
```

---

## Quick Setup Instructions for Friends

### Prerequisites
1. **Chrome browser** (latest version)
2. **Python 3.8+** installed
3. **OpenAI API key** (get from platform.openai.com)

### Setup Steps (10 minutes)

#### Step 1: Download & Setup Backend
```bash
# 1. Create project folder
mkdir ai-sales-assistant-mvp
cd ai-sales-assistant-mvp

# 2. Create the 3 backend files above (main.py, requirements.txt, run.py)

# 3. Set OpenAI API key
export OPENAI_API_KEY="your-openai-api-key-here"

# 4. Run the backend
python run.py
```

#### Step 2: Load Chrome Extension  
1. Open Chrome → Extensions → Developer Mode ON
2. Create extension folder with the 4 files above
3. Click "Load Unpacked" → Select extension folder
4. Extension appears in toolbar

#### Step 3: Test It Out
1. Join a Google Meet or Zoom meeting
2. Extension automatically starts listening
3. Say something like "How much does this cost?"
4. AI suggestions appear in floating overlay
5. Click "Copy" to use suggestions

### Usage Tips
- **Upload Knowledge**: Click extension icon → Upload PDFs about your product
- **Trigger Suggestions**: Ask questions, mention pricing, or express concerns
- **Copy & Paste**: One-click copy suggestions to use in meeting chat
- **Hide UI**: Click "Hide" button if overlay blocks content

---

## Simple File Structure
```
ai-sales-assistant-mvp/
├── backend/
│   ├── main.py              # Complete backend (200 lines)
│   ├── requirements.txt     # Dependencies
│   └── run.py              # Startup script
└── extension/
    ├── manifest.json        # Extension config
    ├── content.js          # Audio capture & UI (150 lines)
    ├── popup.html          # Upload interface
    └── background.js       # Service worker (minimal)
```

**Total Code**: ~400 lines for complete working system

---

## Testing Scenarios for Friends

### Test Case 1: Basic Question Detection
1. **Setup**: Upload a product PDF
2. **Test**: In meeting, say "How does your security work?"
3. **Expected**: AI suggests specific security-related responses

### Test Case 2: Pricing Objection
1. **Test**: Say "That seems expensive compared to competitors"
2. **Expected**: AI suggests value proposition and ROI information

### Test Case 3: Technical Questions  
1. **Test**: Ask "Can this integrate with Salesforce?"
2. **Expected**: AI provides integration details from knowledge base

### Test Case 4: General Conversation
1. **Test**: Normal conversation without triggers
2. **Expected**: No suggestions appear (system stays quiet)

---

## Limitations of MVP

### What's NOT Included
- ❌ User authentication or accounts
- ❌ Subscription billing or limits  
- ❌ Advanced conversation context
- ❌ Team features or sharing
- ❌ Analytics or reporting
- ❌ Advanced security measures
- ❌ Production deployment
- ❌ Error recovery or fallbacks
- ❌ Performance optimization
- ❌ Multi-browser support

### MVP Constraints
- **Single shared knowledge base** (all users see same context)
- **No conversation history** (each suggestion is independent)
- **Basic trigger detection** (simple keyword matching)
- **Local development only** (runs on localhost)
- **Manual setup** (friends need to configure themselves)
- **Limited error handling** (may break on edge cases)

---

## Success Criteria for MVP Testing

### Technical Validation
- [ ] Extension loads without errors in Chrome
- [ ] Audio capture works on Google Meet and Zoom
- [ ] Backend processes audio and generates suggestions
- [ ] WebSocket communication is stable for 30+ minutes
- [ ] Suggestions are relevant to conversation context
- [ ] Copy functionality works reliably

### User Experience Validation  
- [ ] Friends can set up system in <15 minutes
- [ ] UI doesn't interfere with meeting experience
- [ ] Suggestions appear within 5 seconds of triggers
- [ ] At least 50% of suggestions are useful/relevant
- [ ] System feels helpful, not distracting

### Feedback Collection
- [ ] **Usefulness**: How often do suggestions help?
- [ ] **Accuracy**: Are suggestions relevant to context?
- [ ] **Timing**: Do suggestions appear at right moments?
- [ ] **Interface**: Is UI intuitive and non-disruptive?
- [ ] **Performance**: Any lag or technical issues?

---

## Next Steps After MVP Validation

### If MVP Tests Well
1. **Add Authentication**: Simple user accounts
2. **Improve AI**: Better conversation context
3. **Enhanced UI**: More professional interface
4. **Knowledge Management**: Better document processing
5. **Deploy to Cloud**: Make it accessible online

### If MVP Needs Iteration
1. **Fix Core Issues**: Address fundamental problems
2. **Simplify Further**: Remove complexity
3. **Focus on One Platform**: Just Google Meet or Zoom
4. **Improve Accuracy**: Better trigger detection
5. **Enhance Setup**: Easier installation process

---

## Cost Estimation for MVP Testing

### OpenAI API Costs (per hour of testing)
- **Whisper**: ~$0.36/hour (60 min × $0.006/min)
- **GPT-5**: ~$0.15/hour (avg 10 suggestions × 500 tokens × $1.25/1M)
- **Vector Store**: ~$0.10/day (storage)

**Total**: ~$0.50/hour per user testing

### Recommended Testing Budget
- **5 friends × 10 hours each = $25 total**
- **Add $10 buffer for experimentation = $35**

---

This simplified MVP removes all complexity while keeping the core AI functionality intact. Perfect for validating the concept with friends before building the full production system!