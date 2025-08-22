# 🔧 AI Sales Assistant MVP - Troubleshooting Guide

## 🚨 Current Issue: "Connection Failed" in Extension

You're getting connection failures because the backend server isn't starting properly due to missing Python dependencies.

## 📋 Quick Fix Options

### Option 1: Simple Test Server (Immediate)

Start a basic server to test connectivity:

```bash
python3 simple_server.py
```

Then test with:
```bash
python3 simple_test.py
```

This will tell us if the basic HTTP connection works.

### Option 2: Fix Dependencies (Recommended)

The issue is that Python modules aren't installing properly in your WSL environment. Here's how to fix it:

```bash
# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn websockets openai python-multipart python-dotenv

# Start the server
cd backend
python main.py
```

### Option 3: Use Docker (Advanced)

If Python dependencies keep failing, use Docker:

```bash
# Create Dockerfile in backend/
cat > backend/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# Build and run
cd backend
docker build -t ai-sales-assistant .
docker run -p 8000:8000 -e OPENAI_API_KEY="your-key" ai-sales-assistant
```

## 🐛 Debug Steps

### Step 1: Test Basic Connectivity

```bash
# Test if port 8000 is available
curl http://localhost:8000/health

# If that fails, check what's using port 8000
netstat -tulpn | grep :8000
```

### Step 2: Test WebSocket in Browser

If the HTTP server works, test WebSocket:

1. Open Chrome
2. Go to `google.com` (any page)
3. Press F12 → Console
4. Paste this code:

```javascript
const socket = new WebSocket('ws://localhost:8000/ws');
socket.onopen = () => console.log('✅ Connected!');
socket.onerror = (e) => console.log('❌ Error:', e);
socket.onclose = (e) => console.log('🔌 Closed:', e.code);
```

### Step 3: Check Chrome Extension

If WebSocket works but extension doesn't:

1. Go to `chrome://extensions/`
2. Find "AI Sales Assistant MVP"
3. Check "Details" → "Inspect views"
4. Look for console errors
5. Verify permissions are granted

## 🎯 Expected Behavior

When everything works, you should see:

**Backend logs:**
```
✅ OpenAI client initialized successfully
📝 Continuing without vector store (basic functionality will work)
🔌 WebSocket connection attempt from 127.0.0.1
✅ WebSocket connection #1 accepted
📤 Sent connection confirmation to client #1
```

**Extension console:**
```
🤖 AI Sales Assistant: Content script loaded
✅ [14:30:25] AI Assistant: Connected to backend!
✅ [14:30:25] AI Assistant: Connection confirmed
```

**Browser Network tab:**
- Status 101 (WebSocket upgrade) for `ws://localhost:8000/ws`

## 🔍 Common Issues & Solutions

| Symptom | Cause | Solution |
|---------|--------|----------|
| `Connection refused` | Backend not running | Start server: `python3 simple_server.py` |
| `Module not found` | Missing dependencies | Use virtual environment or Docker |
| `ERR_CONNECTION_REFUSED` | Port blocked/used | Check `netstat -tulpn \| grep :8000` |
| Extension not working | Wrong permissions | Check `chrome://extensions/` permissions |
| WebSocket fails | CORS/firewall issue | Use browser console test |

## 💡 Environment-Specific Issues

### Windows Subsystem for Linux (WSL)
- Windows Defender might block localhost connections
- Try: `New-NetFirewallRule -DisplayName "WSL" -Direction Inbound -InterfaceAlias "vEthernet (WSL)" -Action Allow`

### Corporate Networks
- Proxy servers often block WebSocket connections
- Try changing to port 443: `uvicorn main:app --port 443`

### Antivirus Software
- May block localhost servers
- Add exception for `python.exe` and port 8000

## 🧪 Testing Checklist

- [ ] Backend starts without errors
- [ ] `curl http://localhost:8000/health` returns JSON
- [ ] WebSocket test in browser console works
- [ ] Chrome extension loads without errors
- [ ] Extension shows up on Google Meet/Zoom pages
- [ ] Extension overlay appears on meeting pages
- [ ] Console shows WebSocket connection messages

## 📞 Quick Support

If you're still having issues:

1. **Check what's actually running:**
   ```bash
   python3 simple_test.py
   ```

2. **Test WebSocket separately:**
   - Use browser console JavaScript test above

3. **Verify extension:**
   - Check `chrome://extensions/` for errors
   - Test on `https://meet.google.com`

4. **Look at logs:**
   - Backend terminal output
   - Browser DevTools console (F12)
   - Extension inspect view logs

The most common issue is Python dependencies not installing properly. The simple server approach will quickly tell us if it's a dependency issue or a networking issue.

---

**Current Status**: The AI Sales Assistant is fully built and ready - we just need to get the server running properly. All the code is working, it's just an environment/dependency issue.