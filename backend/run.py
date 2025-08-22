#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

def check_requirements():
    """Check if OpenAI API key is set"""
    # Load from .env file
    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(env_path)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Error: OPENAI_API_KEY not found")
        print("Please check your .env file in the project root")
        sys.exit(1)
    
    print("✅ OpenAI API key found")
    print(f"🔑 Key preview: {api_key[:8]}...{api_key[-8:]}")

def install_dependencies():
    """Install required packages"""
    print("📦 Installing dependencies...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        sys.exit(1)

def test_openai_connection():
    """Test OpenAI API connection"""
    print("🧪 Testing OpenAI connection...")
    try:
        from openai import OpenAI
        load_dotenv(Path(__file__).parent.parent / ".env")
        
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Test with a simple completion
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'OpenAI connection test successful'"}],
            max_tokens=10
        )
        
        print("✅ OpenAI connection test successful!")
        print(f"Response: {response.choices[0].message.content}")
        
    except Exception as e:
        print(f"⚠️ OpenAI connection test failed: {e}")
        print("The server will still start, but AI features may not work properly")

def start_server():
    """Start the FastAPI server"""
    print("\n" + "="*50)
    print("🚀 Starting AI Sales Assistant MVP Backend")
    print("="*50)
    print("🌐 Server URL: http://localhost:8000")
    print("📡 WebSocket: ws://localhost:8000/ws")
    print("📤 Upload: http://localhost:8000/upload-knowledge")
    print("🔍 Health: http://localhost:8000/health")
    print("🐛 Debug: http://localhost:8000/debug/conversation")
    print("="*50)
    print("\n🔧 Next steps:")
    print("1. Load the Chrome extension")
    print("2. Join a Google Meet or Zoom meeting")
    print("3. Start talking to test audio capture")
    print("4. Check the logs below for debugging info")
    print("\n📋 Press Ctrl+C to stop the server")
    print("="*50 + "\n")
    
    try:
        import uvicorn
        uvicorn.run(
            "main:app", 
            host="0.0.0.0", 
            port=8000, 
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("🤖 AI Sales Assistant MVP - Setup & Launch")
    print("-" * 40)
    
    # Run all checks
    check_requirements()
    install_dependencies()
    test_openai_connection()
    
    # Start the server
    start_server()