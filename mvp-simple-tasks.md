# AI Sales Assistant MVP - Simple Task List for Friends Testing

## Task Status Legend
- ⏳ **pending**: Not started
- 🔄 **in_progress**: Currently being worked on  
- ✅ **completed**: Finished successfully

---

## Quick Setup Tasks (Day 1: 2-3 hours)

### 1. Environment Setup
- **Status**: ⏳ pending
- **Time**: 30 minutes
- **Description**: Set up basic development environment
- **Steps**:
  - [ ] Install Python 3.8+ on your computer
  - [ ] Get OpenAI API key from platform.openai.com
  - [ ] Create project folder `ai-sales-assistant-mvp`
  - [ ] Set environment variable: `export OPENAI_API_KEY="your-key"`
- **Test**: Run `python --version` and `echo $OPENAI_API_KEY`

### 2. Create Backend Files
- **Status**: ⏳ pending  
- **Time**: 45 minutes
- **Description**: Create the 3 backend files
- **Steps**:
  - [ ] Create `backend/main.py` (copy from mvp-simple-plan.md)
  - [ ] Create `backend/requirements.txt` (copy from plan)
  - [ ] Create `backend/run.py` (copy from plan)
  - [ ] Test by running: `cd backend && python run.py`
- **Test**: Backend starts at http://localhost:8000, shows "healthy" status

### 3. Create Chrome Extension  
- **Status**: ⏳ pending
- **Time**: 45 minutes
- **Description**: Create the Chrome extension files
- **Steps**:
  - [ ] Create `extension/manifest.json` (copy from plan)
  - [ ] Create `extension/content.js` (copy from plan)  
  - [ ] Create `extension/popup.html` (copy from plan)
  - [ ] Create empty `extension/background.js` file
- **Test**: Files created and ready to load

### 4. Load Extension in Chrome
- **Status**: ⏳ pending
- **Time**: 15 minutes  
- **Description**: Install extension in Chrome for testing
- **Steps**:
  - [ ] Open Chrome → More Tools → Extensions
  - [ ] Toggle "Developer mode" ON (top right)
  - [ ] Click "Load unpacked" → Select `extension/` folder
  - [ ] Extension appears in toolbar with AI icon
  - [ ] Click extension icon to see popup
- **Test**: Extension loads without errors in Chrome

### 5. First Test Run
- **Status**: ⏳ pending
- **Time**: 15 minutes
- **Description**: Basic end-to-end test
- **Steps**:
  - [ ] Start backend: `python run.py`
  - [ ] Open Google Meet or Zoom test meeting
  - [ ] Extension should auto-start (overlay appears)
  - [ ] Say "How much does this cost?" 
  - [ ] Check if suggestions appear in overlay
- **Test**: Suggestions appear and can be copied

---

## Core Development Tasks (Day 2-3: 4-6 hours)

### 6. Improve Audio Capture
- **Status**: ⏳ pending
- **Time**: 90 minutes
- **Description**: Make audio capture more reliable
- **Steps**:
  - [ ] Test audio capture on different meeting platforms
  - [ ] Add error handling for audio permissions
  - [ ] Improve audio quality and format conversion
  - [ ] Add visual indicator when audio is capturing
  - [ ] Test with different microphone setups
- **Test**: Audio captures clearly for 30+ minutes without issues

### 7. Enhance Trigger Detection
- **Status**: ⏳ pending
- **Time**: 60 minutes
- **Description**: Improve when suggestions appear
- **Steps**:
  - [ ] Add more trigger phrases (questions, objections)
  - [ ] Implement simple confidence scoring
  - [ ] Add delay to avoid too-frequent suggestions
  - [ ] Test trigger accuracy with sample conversations
  - [ ] Fine-tune sensitivity based on testing
- **Test**: Suggestions appear for relevant statements, not random chatter

### 8. Better Knowledge Base Processing
- **Status**: ⏳ pending
- **Time**: 75 minutes
- **Description**: Improve how uploaded documents are used
- **Steps**:
  - [ ] Add support for PDF file parsing
  - [ ] Implement simple text chunking for long documents
  - [ ] Improve knowledge search relevance
  - [ ] Add visual feedback for successful uploads
  - [ ] Test with different document types and sizes
- **Test**: Uploaded PDFs contribute to relevant suggestions

### 9. Improve Suggestion Quality
- **Status**: ⏳ pending
- **Time**: 90 minutes
- **Description**: Make AI suggestions more helpful and specific
- **Steps**:
  - [ ] Refine GPT-5 prompts for better responses
  - [ ] Add conversation context to suggestion generation
  - [ ] Implement suggestion ranking by relevance
  - [ ] Add variety to avoid repetitive suggestions
  - [ ] Test with real sales conversation scenarios
- **Test**: Friends rate suggestions as helpful 70%+ of the time

### 10. Polish User Interface
- **Status**: ⏳ pending
- **Time**: 75 minutes  
- **Description**: Make UI more user-friendly and attractive
- **Steps**:
  - [ ] Improve overlay styling and positioning
  - [ ] Add smooth animations for suggestions appearing/disappearing
  - [ ] Make overlay draggable and resizable
  - [ ] Add keyboard shortcuts (Ctrl+C to copy top suggestion)
  - [ ] Improve visual feedback for copy actions
- **Test**: UI feels smooth and doesn't interfere with meetings

---

## Testing & Validation Tasks (Day 4-5: 3-4 hours)

### 11. Friends Testing Coordination
- **Status**: ⏳ pending
- **Time**: 60 minutes
- **Description**: Set up testing with friends
- **Steps**:
  - [ ] Create simple setup instructions for friends
  - [ ] Share backend code and extension files
  - [ ] Help friends with initial setup (screen share if needed)
  - [ ] Create test scenarios for friends to try
  - [ ] Set up feedback collection method (shared doc/form)
- **Test**: 3+ friends can successfully set up and use the system

### 12. Create Test Scenarios
- **Status**: ⏳ pending
- **Time**: 45 minutes
- **Description**: Design realistic testing scenarios
- **Steps**:
  - [ ] Write 5 realistic sales conversation scenarios
  - [ ] Include different types of triggers (questions, objections, technical)
  - [ ] Create sample knowledge base documents for testing
  - [ ] Prepare expected suggestion examples
  - [ ] Create testing checklist for friends
- **Test**: Friends can follow scenarios and evaluate results

### 13. Performance Testing  
- **Status**: ⏳ pending
- **Time**: 45 minutes
- **Description**: Test system performance and reliability
- **Steps**:
  - [ ] Test 60+ minute meeting sessions
  - [ ] Check WebSocket connection stability
  - [ ] Measure suggestion response times
  - [ ] Test with multiple users simultaneously
  - [ ] Monitor OpenAI API usage and costs
- **Test**: System runs smoothly for full-length meetings

### 14. Bug Fixes & Improvements
- **Status**: ⏳ pending
- **Time**: 90 minutes
- **Description**: Fix issues found during testing
- **Steps**:
  - [ ] Fix audio capture issues on different platforms
  - [ ] Resolve WebSocket disconnection problems
  - [ ] Improve suggestion relevance based on feedback
  - [ ] Fix UI positioning and visibility issues
  - [ ] Address any OpenAI API integration problems
- **Test**: Major bugs resolved, system stable for demo

### 15. Feedback Collection & Analysis
- **Status**: ⏳ pending
- **Time**: 60 minutes
- **Description**: Gather and analyze friend feedback
- **Steps**:
  - [ ] Collect structured feedback from all testers
  - [ ] Analyze suggestion acceptance rates
  - [ ] Document common issues and feature requests
  - [ ] Identify most valuable use cases
  - [ ] Plan improvements for next iteration
- **Test**: Clear understanding of what works and what needs improvement

---

## Simple Code Templates

### Quick Audio Test
```javascript
// Test audio capture in browser console
navigator.mediaDevices.getDisplayMedia({audio: true, video: false})
  .then(stream => {
    console.log('✅ Audio capture working!', stream)
    // Stop the stream
    stream.getTracks().forEach(track => track.stop())
  })
  .catch(err => console.error('❌ Audio capture failed:', err))
```

### Quick OpenAI Test
```python
# Test OpenAI connection
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Test GPT-5
response = client.responses.create(
    model="gpt-5",
    reasoning_effort="low", 
    verbosity="low",
    input="Generate 3 sales suggestions for: 'How much does this cost?'"
)

print("✅ OpenAI GPT-5 working!")
print("Response:", response.output_text)
```

### Quick WebSocket Test
```python
# Test WebSocket connection
import asyncio
import websockets

async def test_connection():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        await websocket.send('{"type": "test", "message": "hello"}')
        response = await websocket.recv()
        print(f"✅ WebSocket working: {response}")

asyncio.run(test_connection())
```

---

## Troubleshooting Guide

### Common Issues & Fixes

#### Problem: "OpenAI API key not found"
**Solution**: 
```bash
export OPENAI_API_KEY="sk-your-key-here"
python run.py
```

#### Problem: "Extension won't load in Chrome"
**Solution**:
1. Check Developer mode is ON
2. Verify all 4 extension files exist
3. Check manifest.json syntax
4. Reload extension after changes

#### Problem: "No audio captured in meetings"  
**Solution**:
1. Give Chrome microphone permissions
2. Test with: chrome://settings/content/microphone
3. Try different meeting platforms
4. Check browser console for errors

#### Problem: "WebSocket connection failed"
**Solution**:
1. Ensure backend is running on port 8000
2. Check firewall isn't blocking localhost:8000
3. Test connection with: http://localhost:8000/health

#### Problem: "Suggestions are irrelevant"
**Solution**:
1. Upload better knowledge base documents
2. Test trigger phrases more clearly
3. Check OpenAI API usage logs
4. Try different conversation contexts

---

## MVP Feature Checklist

### Core Functionality
- [ ] **Audio Capture**: Records meeting audio from browser tab
- [ ] **Speech Recognition**: Converts audio to text with Whisper
- [ ] **Trigger Detection**: Detects questions and objections
- [ ] **AI Suggestions**: Generates 2-3 relevant responses with GPT-5
- [ ] **UI Overlay**: Shows suggestions in floating window
- [ ] **Copy Function**: One-click copy suggestions to clipboard
- [ ] **Knowledge Upload**: Upload PDFs for context

### Technical Requirements
- [ ] **Chrome Extension**: Loads and runs without errors
- [ ] **Backend API**: Processes requests and integrates with OpenAI
- [ ] **WebSocket**: Real-time communication between extension and backend
- [ ] **OpenAI Integration**: GPT-5, Whisper, and Vector Store working
- [ ] **Error Handling**: Basic error messages for common failures
- [ ] **Performance**: <5 second response time for suggestions

### User Experience
- [ ] **Easy Setup**: Friends can install and configure in <15 minutes
- [ ] **Intuitive Use**: No training required, works automatically
- [ ] **Non-disruptive**: Doesn't interfere with meeting experience
- [ ] **Helpful Output**: Suggestions are actionable and relevant
- [ ] **Reliable**: Works for full meeting duration without crashes

---

## Friend Testing Instructions

### What to Test
1. **Installation**: Can you set it up easily?
2. **Audio**: Does it capture your meeting audio?
3. **Suggestions**: Do helpful suggestions appear when you ask questions?
4. **Usability**: Is the interface intuitive and non-disruptive?
5. **Reliability**: Does it work for a full meeting without issues?

### How to Test
1. **Pre-meeting**: Upload a sample PDF (product info, FAQ, etc.)
2. **During meeting**: Have normal conversation, ask questions, mention concerns
3. **Post-meeting**: Rate the suggestions and overall experience

### What to Report
- **What worked well?** 
- **What was confusing or broken?**
- **How useful were the suggestions?** (rate 1-10)
- **Would you use this regularly?** (yes/no/maybe)
- **What features are missing?**

---

**Total MVP Development Time**: 8-12 hours
**Friend Testing Period**: 1-2 weeks  
**Expected Cost**: $30-50 for testing
**Files Created**: 7 total files (~400 lines of code)

This simplified MVP focuses purely on validating the core concept with minimal complexity, perfect for getting honest feedback from friends before investing in the full production system!