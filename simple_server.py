#!/usr/bin/env python3
"""
Simple server that works without additional dependencies
"""

import os
import json
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import threading
import time

# OpenAI API key will be loaded from environment variable OPENAI_API_KEY
# Set it in .env file or export OPENAI_API_KEY="your-key-here"

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        print(f"📨 GET {self.path}")
        
        # Add CORS headers
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        if self.path == '/health':
            # Health check endpoint
            response = {
                "status": "healthy",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "message": "Simple server running",
                "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
                "note": "This is a simple test server - WebSocket not available"
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
        else:
            # 404 for other paths
            response = {"error": "Not found", "path": self.path}
            self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        """Handle POST requests"""
        print(f"📨 POST {self.path}")
        
        # Add CORS headers
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {"message": "POST endpoint working", "path": self.path}
        self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()

def start_simple_server():
    """Start a simple HTTP server for testing"""
    print("🚀 Starting Simple Test Server")
    print("=" * 50)
    print("🌐 Server URL: http://localhost:8000")
    print("🔍 Health: http://localhost:8000/health")
    print("⚠️  Note: This is a test server - no WebSocket support")
    print("📋 Use this to verify basic connectivity")
    print("⏹️  Press Ctrl+C to stop")
    print("=" * 50)
    
    try:
        server = HTTPServer(('localhost', 8000), SimpleHandler)
        print("✅ Simple server started successfully!")
        print("📍 You can now test:")
        print("   - Open http://localhost:8000/health in browser")
        print("   - Run: python3 simple_test.py")
        print()
        
        server.serve_forever()
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
    except Exception as e:
        print(f"❌ Server error: {e}")

if __name__ == "__main__":
    start_simple_server()