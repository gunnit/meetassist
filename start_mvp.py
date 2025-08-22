#!/usr/bin/env python3
"""
AI Sales Assistant MVP - One-Click Startup Script
This script sets up everything needed and starts the backend server.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_header():
    print("🤖 AI Sales Assistant MVP - Startup Script")
    print("=" * 50)
    print()

def check_python():
    """Check Python version"""
    print("🔍 Checking Python version...")
    
    if sys.version_info < (3, 8):
        print(f"❌ Python 3.8+ required, found {sys.version}")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    return True

def check_api_key():
    """Check OpenAI API key"""
    print("🔍 Checking OpenAI API key...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        return False
    
    # Read API key from .env
    with open(env_file) as f:
        for line in f:
            if line.startswith("OPENAI_API_KEY="):
                api_key = line.split("=", 1)[1].strip()
                if api_key and api_key.startswith("sk-"):
                    print(f"✅ API key found: {api_key[:8]}...{api_key[-8:]}")
                    # Set in environment for this process
                    os.environ["OPENAI_API_KEY"] = api_key
                    return True
    
    print("❌ Valid OpenAI API key not found in .env")
    return False

def test_openai_connection():
    """Test OpenAI API connection"""
    print("🔍 Testing OpenAI connection...")
    
    try:
        import urllib.request
        import json
        
        url = 'https://api.openai.com/v1/models'
        headers = {'Authorization': f'Bearer {os.environ["OPENAI_API_KEY"]}'}
        req = urllib.request.Request(url, headers=headers)
        
        response = urllib.request.urlopen(req, timeout=10)
        data = json.loads(response.read())
        
        models = data.get('data', [])
        gpt4_models = [m['id'] for m in models if 'gpt-4' in m['id']]
        
        print(f"✅ Connected! Found {len(models)} models, {len(gpt4_models)} GPT-4 variants")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI connection failed: {e}")
        return False

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    
    requirements = [
        "fastapi==0.104.0",
        "uvicorn==0.24.0", 
        "websockets==12.0",
        "openai==1.68.0",
        "python-multipart==0.0.6",
        "python-dotenv==1.0.0"
    ]
    
    for package in requirements:
        try:
            # Try to import the package first
            package_name = package.split("==")[0].replace("-", "_")
            if package_name == "python_multipart":
                __import__("multipart")
            elif package_name == "python_dotenv":
                __import__("dotenv")
            else:
                __import__(package_name)
            print(f"✅ {package_name} already installed")
        except ImportError:
            print(f"📥 Installing {package}...")
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "install", package, "--break-system-packages"
                ], check=True, capture_output=True)
                print(f"✅ {package} installed")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install {package}: {e}")
                return False
    
    return True

def check_files():
    """Check all required files exist"""
    print("🔍 Checking project files...")
    
    required_files = {
        "backend/main.py": "Backend server",
        "backend/requirements.txt": "Python requirements", 
        "extension/manifest.json": "Extension manifest",
        "extension/content.js": "Extension content script",
        "extension/popup.html": "Extension popup",
        ".env": "Environment variables"
    }
    
    all_good = True
    for file_path, description in required_files.items():
        if Path(file_path).exists():
            print(f"✅ {description}")
        else:
            print(f"❌ Missing: {file_path} ({description})")
            all_good = False
    
    return all_good

def start_server():
    """Start the FastAPI server"""
    print("\n🚀 Starting AI Sales Assistant Backend...")
    print("=" * 50)
    print("🌐 Server URL: http://localhost:8000")
    print("📡 WebSocket: ws://localhost:8000/ws") 
    print("🔍 Health: http://localhost:8000/health")
    print("🐛 Debug: http://localhost:8000/debug/conversation")
    print()
    print("📋 Next Steps:")
    print("1. Load Chrome extension from 'extension' folder")
    print("2. Visit https://meet.google.com")
    print("3. Start talking to test AI suggestions")
    print("4. Check logs below for debugging")
    print()
    print("⏹️ Press Ctrl+C to stop the server")
    print("=" * 50)
    print()
    
    # Change to backend directory and start server
    os.chdir("backend")
    
    try:
        # Start with uvicorn directly
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
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        return False
    
    return True

def main():
    """Main startup routine"""
    print_header()
    
    # Run all checks
    checks = [
        ("Python Version", check_python),
        ("OpenAI API Key", check_api_key), 
        ("Project Files", check_files),
        ("OpenAI Connection", test_openai_connection),
        ("Dependencies", install_dependencies)
    ]
    
    for check_name, check_func in checks:
        if not check_func():
            print(f"\n❌ {check_name} check failed. Please fix the issues above.")
            return False
        time.sleep(0.5)  # Brief pause between checks
    
    print("\n✅ All checks passed!")
    print("\n" + "="*50)
    
    # Start the server
    return start_server()

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n💡 For manual setup instructions, see README.md")
        sys.exit(1)