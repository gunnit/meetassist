#!/usr/bin/env python3
"""
Quick server restart script with debugging
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def main():
    print("🔄 Restarting AI Sales Assistant with fixes...")
    print("=" * 50)
    
    # Change to backend directory
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    # Set environment variable
    env_file = Path("../.env")
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.startswith("OPENAI_API_KEY="):
                    api_key = line.split("=", 1)[1].strip()
                    os.environ["OPENAI_API_KEY"] = api_key
                    print(f"✅ API key loaded: {api_key[:8]}...{api_key[-8:]}")
                    break
    
    print("🚀 Starting server with enhanced debugging...")
    print("🌐 Server: http://localhost:8000")
    print("📡 WebSocket: ws://localhost:8000/ws")
    print("🧪 Test page: file:///path/to/test_websocket.html")
    print()
    print("📋 To debug WebSocket issues:")
    print("1. Open test_websocket.html in Chrome")
    print("2. Check the connection log")
    print("3. Look at server logs below")
    print("4. Test the Chrome extension after WebSocket works")
    print()
    print("⏹️ Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        # Install dependencies if needed
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--break-system-packages"], 
                      capture_output=True)
        
        # Start server
        subprocess.run([
            sys.executable, "-c", 
            """
import uvicorn
import sys
sys.path.insert(0, '.')
uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True, log_level='info')
            """
        ])
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    main()