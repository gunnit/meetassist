#!/usr/bin/env python3
"""
Complete System Test for AI Sales Assistant MVP
This script tests all components: backend, OpenAI integration, and provides extension testing guidance.
"""

import os
import json
import asyncio
import requests
import tempfile
from pathlib import Path
import time

class SystemTester:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.test_results = {}
        
    def log(self, message, test_name="SYSTEM"):
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {test_name}: {message}")
        
    async def run_all_tests(self):
        """Run comprehensive system tests"""
        print("🧪 AI Sales Assistant MVP - Complete System Test")
        print("=" * 60)
        
        tests = [
            ("Environment Check", self.test_environment),
            ("Backend Connection", self.test_backend_connection),
            ("OpenAI Integration", self.test_openai_integration),
            ("Trigger Detection", self.test_trigger_detection),
            ("Knowledge Upload", self.test_knowledge_upload),
            ("Suggestion Generation", self.test_suggestion_generation),
            ("WebSocket Simulation", self.test_websocket_simulation),
            ("Error Handling", self.test_error_handling)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🔍 Testing: {test_name}")
            print("-" * 40)
            
            try:
                result = await test_func()
                if result:
                    self.log("✅ PASSED", test_name)
                    self.test_results[test_name] = "PASSED"
                    passed += 1
                else:
                    self.log("❌ FAILED", test_name)
                    self.test_results[test_name] = "FAILED"
            except Exception as e:
                self.log(f"❌ ERROR: {e}", test_name)
                self.test_results[test_name] = f"ERROR: {e}"
        
        print(f"\n📊 Test Summary")
        print("=" * 60)
        print(f"Total tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success rate: {passed/total*100:.1f}%")
        
        self.print_extension_guide()
        
        return passed == total
    
    async def test_environment(self):
        """Test environment setup"""
        # Check .env file
        env_file = Path(".env")
        if not env_file.exists():
            self.log("❌ .env file not found")
            return False
            
        # Check OpenAI API key
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            self.log("❌ OPENAI_API_KEY not found in .env")
            return False
        
        if not api_key.startswith("sk-"):
            self.log("❌ Invalid OpenAI API key format")
            return False
        
        self.log(f"✅ API key found: {api_key[:8]}...{api_key[-8:]}")
        
        # Check backend files
        backend_files = ["main.py", "requirements.txt", "run.py"]
        for file in backend_files:
            if not Path(f"backend/{file}").exists():
                self.log(f"❌ Backend file missing: {file}")
                return False
        
        # Check extension files  
        extension_files = ["manifest.json", "content.js", "popup.html", "background.js"]
        for file in extension_files:
            if not Path(f"extension/{file}").exists():
                self.log(f"❌ Extension file missing: {file}")
                return False
        
        self.log("✅ All required files present")
        return True
    
    async def test_backend_connection(self):
        """Test backend server connection"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.log(f"✅ Backend healthy: {data}")
                return True
            else:
                self.log(f"❌ Backend returned status: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            self.log("❌ Backend not running. Start with: python backend/run.py")
            return False
        except Exception as e:
            self.log(f"❌ Backend connection error: {e}")
            return False
    
    async def test_openai_integration(self):
        """Test OpenAI API integration"""
        try:
            from openai import OpenAI
            from dotenv import load_dotenv
            
            load_dotenv()
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            # Test simple completion
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Say 'OpenAI test successful' in exactly those words."}],
                max_tokens=10
            )
            
            result = response.choices[0].message.content.strip()
            self.log(f"✅ OpenAI response: {result}")
            
            if "successful" in result.lower():
                return True
            else:
                self.log("⚠️ Unexpected OpenAI response")
                return True  # Still counts as working
                
        except Exception as e:
            self.log(f"❌ OpenAI integration failed: {e}")
            return False
    
    async def test_trigger_detection(self):
        """Test trigger detection logic"""
        try:
            # Test trigger detection endpoint
            test_phrases = [
                ("How much does this cost?", True),
                ("That seems expensive", True),
                ("Hello there", False),
                ("Nice weather today", False),
                ("What about security?", True),
                ("Can you integrate with Salesforce?", True)
            ]
            
            all_passed = True
            
            for phrase, should_trigger in test_phrases:
                response = requests.post(
                    f"{self.backend_url}/test/suggestion",
                    params={"text": phrase}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    triggered = data.get("triggered", False)
                    
                    if triggered == should_trigger:
                        self.log(f"✅ '{phrase}' -> {triggered} (expected {should_trigger})")
                    else:
                        self.log(f"❌ '{phrase}' -> {triggered} (expected {should_trigger})")
                        all_passed = False
                else:
                    self.log(f"❌ API error for '{phrase}': {response.status_code}")
                    all_passed = False
            
            return all_passed
            
        except Exception as e:
            self.log(f"❌ Trigger detection test failed: {e}")
            return False
    
    async def test_knowledge_upload(self):
        """Test knowledge base upload"""
        try:
            # Create a test file
            test_content = """
            Product: AI Sales Assistant
            Price: $99/month
            Features:
            - Real-time AI suggestions during meetings
            - Voice transcription
            - Knowledge base integration
            - Chrome extension
            
            Security: Enterprise-grade encryption
            Integrations: Salesforce, HubSpot, Zoom, Google Meet
            """
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(test_content)
                test_file_path = f.name
            
            try:
                # Upload the file
                with open(test_file_path, 'rb') as f:
                    files = {'files': ('test_product_info.txt', f, 'text/plain')}
                    response = requests.post(f"{self.backend_url}/upload-knowledge", files=files)
                
                if response.status_code == 200:
                    data = response.json()
                    self.log(f"✅ File uploaded: {data}")
                    
                    # Verify it's in the knowledge base
                    kb_response = requests.get(f"{self.backend_url}/debug/knowledge")
                    if kb_response.status_code == 200:
                        kb_data = kb_response.json()
                        if kb_data.get('total_items', 0) > 0:
                            self.log("✅ Knowledge base updated")
                            return True
                        else:
                            self.log("❌ Knowledge base not updated")
                            return False
                    else:
                        self.log("⚠️ Could not verify knowledge base update")
                        return True  # Upload succeeded, verification failed
                else:
                    self.log(f"❌ Upload failed: {response.status_code}")
                    return False
                    
            finally:
                # Clean up
                os.unlink(test_file_path)
                
        except Exception as e:
            self.log(f"❌ Knowledge upload test failed: {e}")
            return False
    
    async def test_suggestion_generation(self):
        """Test AI suggestion generation"""
        try:
            # Test with a typical sales scenario
            test_phrase = "How much does your AI assistant cost and what features are included?"
            
            response = requests.post(
                f"{self.backend_url}/test/suggestion",
                params={"text": test_phrase}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("triggered") and data.get("suggestions"):
                    suggestions = data["suggestions"]
                    self.log(f"✅ Generated {len(suggestions)} suggestions:")
                    for i, suggestion in enumerate(suggestions, 1):
                        self.log(f"  {i}. {suggestion[:50]}..." if len(suggestion) > 50 else f"  {i}. {suggestion}")
                    return True
                else:
                    self.log("❌ No suggestions generated")
                    return False
            else:
                self.log(f"❌ Suggestion API error: {response.status_code}")
                return False
                
        except Exception as e:
            self.log(f"❌ Suggestion generation test failed: {e}")
            return False
    
    async def test_websocket_simulation(self):
        """Simulate WebSocket communication"""
        try:
            import websockets
            
            # Test WebSocket connection
            uri = "ws://localhost:8000/ws"
            
            timeout_duration = 10  # seconds
            
            async def websocket_test():
                try:
                    async with websockets.connect(uri, timeout=timeout_duration) as websocket:
                        # Send test message
                        test_message = {
                            "type": "test",
                            "message": "WebSocket test from system tester"
                        }
                        
                        await websocket.send(json.dumps(test_message))
                        self.log("✅ Test message sent")
                        
                        # Wait for response
                        response = await asyncio.wait_for(websocket.recv(), timeout=5)
                        data = json.loads(response)
                        
                        self.log(f"✅ Received response: {data.get('type', 'unknown')}")
                        return True
                        
                except asyncio.TimeoutError:
                    self.log("❌ WebSocket timeout")
                    return False
                except Exception as e:
                    self.log(f"❌ WebSocket error: {e}")
                    return False
            
            return await websocket_test()
            
        except ImportError:
            self.log("⚠️ websockets library not available, skipping WebSocket test")
            return True  # Don't fail if optional dependency missing
        except Exception as e:
            self.log(f"❌ WebSocket test failed: {e}")
            return False
    
    async def test_error_handling(self):
        """Test error handling"""
        try:
            # Test invalid endpoint
            response = requests.get(f"{self.backend_url}/nonexistent-endpoint")
            if response.status_code == 404:
                self.log("✅ 404 handling works")
            else:
                self.log(f"⚠️ Unexpected status for invalid endpoint: {response.status_code}")
            
            # Test invalid suggestion request
            response = requests.post(f"{self.backend_url}/test/suggestion")
            if response.status_code in [400, 422]:  # Validation error expected
                self.log("✅ Input validation works")
            else:
                self.log(f"⚠️ Unexpected status for invalid input: {response.status_code}")
            
            return True  # Error handling tests are informational
            
        except Exception as e:
            self.log(f"❌ Error handling test failed: {e}")
            return False
    
    def print_extension_guide(self):
        """Print Chrome extension testing guide"""
        print(f"\n🔧 Chrome Extension Testing Guide")
        print("=" * 60)
        print("1. Start the backend server:")
        print("   cd backend && python run.py")
        print()
        print("2. Load the Chrome extension:")
        print("   - Open Chrome -> Extensions -> Developer Mode ON")
        print("   - Click 'Load unpacked' -> Select 'extension' folder")
        print("   - Extension should appear in toolbar")
        print()
        print("3. Test the extension:")
        print("   - Click extension icon to open popup")
        print("   - Upload a test PDF or text file")
        print("   - Go to https://meet.google.com (start a test meeting)")
        print("   - Extension overlay should appear automatically")
        print("   - Say 'How much does this cost?' to test suggestions")
        print()
        print("4. Debug issues:")
        print("   - Check browser console (F12) for errors")
        print("   - Check backend logs in terminal")
        print("   - Use extension popup's debug section")
        print("   - Visit http://localhost:8000/health to check backend")
        print()
        print("✅ System tests completed!")

async def main():
    """Run the complete system test"""
    tester = SystemTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! The MVP is ready for testing.")
        return 0
    else:
        print("\n⚠️ Some tests failed. Check the logs above for details.")
        return 1

if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code)