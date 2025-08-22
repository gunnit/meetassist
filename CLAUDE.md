# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Architecture

This is an AI-powered sales assistant MVP that provides real-time suggestions during online meetings. The system consists of two main components:

- **Backend** (`backend/`): FastAPI server with WebSocket support for real-time communication
- **Extension** (`extension/`): Chrome browser extension that captures meeting audio, displays overlay UI, and communicates with backend via WebSocket

### Key Architecture Details

- **Audio Flow**: Extension captures audio via `tabCapture` → sends to backend via WebSocket → (full version: OpenAI Whisper transcription → trigger detection → GPT-4 suggestions) → displayed in overlay
- **Real-time Communication**: WebSocket connection on `ws://localhost:8000/ws` for low-latency audio processing
- **Target Platforms**: Google Meet and Zoom (web versions only)
- **Multiple Backend Versions**: The project has three backend implementations for different use cases

### Backend Implementations

The project includes multiple backend variations:

1. **`main_working.py`** (Recommended for development): Simplified FastAPI server with working WebSocket functionality and mock AI responses. No OpenAI dependencies required.
2. **`main.py`** (Full-featured): Complete FastAPI application with OpenAI Whisper, GPT-4, and vector store integration. Requires OpenAI API key and all dependencies.
3. **`main_simple.py`** (Minimal): Basic server for connection testing with minimal endpoints.

## Common Development Commands

### Backend Development (Recommended)
```bash
# Start the working backend (no OpenAI dependencies, mock responses)
cd backend && python3 -m uvicorn main_working:app --host 0.0.0.0 --port 8000 --reload

# Start the full-featured backend (requires OpenAI setup)
cd backend && python run.py

# Start minimal backend for basic testing
cd backend && python3 -m uvicorn main_simple:app --host 0.0.0.0 --port 8000

# Test WebSocket connectivity
python3 test_websocket.py
```

### Testing and Debugging
```bash
# WebSocket connection test (verify backend is working)
python3 test_websocket.py

# Quick HTTP connectivity test
python3 simple_test.py

# Check backend health (works with all backend versions)
curl http://localhost:8000/health

# Complete system integration test (requires full backend)
python3 test_complete_system.py
```

### WebSocket Debugging
```bash
# Test WebSocket with Python client
python3 test_websocket.py

# Check if port 8000 is available
ss -tlnp | grep :8000

# Kill conflicting processes if needed
pkill -f "uvicorn"
```

### Extension Development
- Load extension: Chrome → Extensions → Developer mode → Load unpacked → Select `extension/` folder
- Debug: Browser console (F12) for content script logs, extension popup for status
- Test: Join Google Meet, check overlay appears, test with phrases like "How much does this cost?"

## Environment Setup

### Required Dependencies
- Python 3.8+ with packages from `backend/requirements.txt` (for full backend)
- Basic FastAPI dependencies: `fastapi`, `uvicorn`, `websockets` (for working backend)
- OpenAI API key in `.env` file (only needed for `main.py` full backend)
- Chrome browser for extension

### Virtual Environment (If Needed)
For development with OpenAI integration:
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r backend/requirements.txt
```

For basic development (working backend):
```bash
pip3 install --break-system-packages fastapi uvicorn websockets
```

## Key Implementation Files

- **`backend/main_working.py`**: Working FastAPI server with WebSocket, mock responses, no OpenAI dependencies
- **`backend/main.py`**: Full FastAPI application with OpenAI Whisper, GPT-4, and vector store integration
- **`backend/run.py`**: Startup script with dependency checks and OpenAI connection testing (for main.py)
- **`extension/content.js`**: Main extension logic for audio capture, UI overlay, and WebSocket communication
- **`extension/manifest.json`**: Extension configuration with required permissions for `tabCapture`
- **`test_websocket.py`**: WebSocket connection testing utility

## Common Issues and Solutions

### WebSocket Connection Issues
The project had WebSocket connection problems due to multiple servers competing for port 8000. This has been resolved with the `main_working.py` backend.

**Symptoms:**
- Extension shows "Connection failed" 
- WebSocket errors in browser console
- Backend not responding on port 8000

**Solutions:**
1. Kill all conflicting processes: `pkill -f "uvicorn"`
2. Start the working backend: `cd backend && python3 -m uvicorn main_working:app --host 0.0.0.0 --port 8000 --reload`
3. Test connection: `python3 test_websocket.py`

### Dependency Issues
If OpenAI packages fail to install:
1. Use the working backend (`main_working.py`) which doesn't require OpenAI dependencies
2. Test basic functionality first with mock responses
3. Add OpenAI integration once basic WebSocket communication works

## Trigger System

The assistant detects conversation triggers via simple keyword matching in `backend/main.py`:
- **Questions**: "?", "how much", "what about", "can you", "do you have"  
- **Pricing**: "expensive", "cost", "price", "pricing"
- **Objections**: "not sure", "think about it", "concerned about", "compared to"

Only when triggers are detected does the system generate GPT-4 suggestions to minimize API costs.

## Testing Strategy

### Development Testing (Recommended)
1. **WebSocket Connection**: `python3 test_websocket.py` - Verify backend WebSocket functionality
2. **Basic Backend**: `curl http://localhost:8000/health` - Check server health
3. **Extension Loading**: Chrome Developer mode → Load extension → Test popup interface

### Full System Testing (Requires OpenAI)
1. **System Integration**: `python3 test_complete_system.py` - Tests end-to-end audio processing pipeline
2. **Backend Unit Tests**: `cd backend && python -m pytest test_backend.py -v` - API endpoints and core functionality  
3. **Manual Extension Testing**: Load in Chrome, join test meeting, verify audio capture and overlay

### Progressive Testing Approach
Start with the working backend (`main_working.py`) to verify:
1. Server starts without errors
2. WebSocket connections work
3. Extension can connect and receive mock responses
4. UI overlay appears and functions correctly

Then upgrade to full backend (`main.py`) for:
1. OpenAI API integration
2. Real audio transcription
3. AI-generated suggestions
4. Knowledge base functionality

## Development Workflow

### Quick Development Setup
1. Start working backend: `cd backend && python3 -m uvicorn main_working:app --host 0.0.0.0 --port 8000 --reload`
2. Load Chrome extension: Extensions → Developer mode → Load unpacked → `extension/` folder
3. Test WebSocket: `python3 test_websocket.py`
4. Test extension: Visit Google Meet, verify overlay appears

### Troubleshooting WebSocket Issues
If WebSocket connections fail:
1. Check for conflicting processes: `ss -tlnp | grep :8000`
2. Kill competing servers: `pkill -f "uvicorn"`
3. Restart with working backend
4. Verify with test client: `python3 test_websocket.py`

## Important Constraints

- **Single User MVP**: No authentication, runs on localhost only
- **Chrome Extension Only**: Uses Manifest V3 with `tabCapture` API
- **OpenAI Dependency**: Full features require valid API key (working backend provides mock responses)
- **Audio Quality**: Depends on meeting platform audio sharing ("Share audio" must be enabled)
- **Memory**: In-memory storage only, conversation history lost on restart
- **Port Requirements**: Backend must run on port 8000 for extension compatibility