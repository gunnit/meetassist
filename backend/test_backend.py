#!/usr/bin/env python3
"""
Test suite for the AI Sales Assistant MVP backend
Run with: python -m pytest test_backend.py -v
"""

import pytest
import asyncio
import json
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from main import app, should_generate_suggestions, generate_suggestions

client = TestClient(app)

class TestHealthEndpoint:
    def test_health_check(self):
        """Test the health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "openai_configured" in data

class TestTriggerDetection:
    def test_question_triggers(self):
        """Test that questions trigger suggestions"""
        test_cases = [
            "How much does this cost?",
            "What about the security features?",
            "Can you integrate with Salesforce?",
            "Do you have enterprise pricing?"
        ]
        
        for text in test_cases:
            assert should_generate_suggestions(text), f"Should trigger for: {text}"
    
    def test_objection_triggers(self):
        """Test that objections trigger suggestions"""
        test_cases = [
            "That seems expensive",
            "I'm not sure about this",
            "We need to think about it",
            "How does this compare to competitors?"
        ]
        
        for text in test_cases:
            assert should_generate_suggestions(text), f"Should trigger for: {text}"
    
    def test_no_trigger_cases(self):
        """Test that normal conversation doesn't trigger"""
        test_cases = [
            "Hello there",
            "Nice weather today",
            "Let me introduce the team",
            "How was your weekend"
        ]
        
        for text in test_cases:
            assert not should_generate_suggestions(text), f"Should NOT trigger for: {text}"

class TestSuggestionGeneration:
    @pytest.mark.asyncio
    async def test_generate_suggestions_with_mock(self):
        """Test suggestion generation with mocked OpenAI"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '["Great question!", "Let me explain that", "Here are the details"]'
        
        with patch('main.client.chat.completions.create', return_value=mock_response):
            suggestions = await generate_suggestions("How much does this cost?")
            
            assert isinstance(suggestions, list)
            assert len(suggestions) <= 3
            assert all(isinstance(s, str) for s in suggestions)

class TestKnowledgeUpload:
    def test_upload_endpoint_structure(self):
        """Test the knowledge upload endpoint structure"""
        # Test with empty upload (should handle gracefully)
        response = client.post("/upload-knowledge", files=[])
        # Should not crash, may return error but endpoint should exist
        assert response.status_code in [200, 400, 422]  # Various acceptable responses

class TestDebugEndpoints:
    def test_conversation_history_endpoint(self):
        """Test conversation history debug endpoint"""
        response = client.get("/debug/conversation")
        assert response.status_code == 200
        data = response.json()
        assert "conversation_history" in data
        assert "total_entries" in data
    
    def test_knowledge_base_endpoint(self):
        """Test knowledge base debug endpoint"""
        response = client.get("/debug/knowledge")
        assert response.status_code == 200
        data = response.json()
        assert "knowledge_items" in data
        assert "total_items" in data

class TestSuggestionTestEndpoint:
    def test_suggestion_test_with_trigger(self):
        """Test the suggestion test endpoint with trigger text"""
        response = client.post("/test/suggestion?text=How much does this cost?")
        assert response.status_code == 200
        data = response.json()
        assert data["triggered"] == True
        assert "suggestions" in data
    
    def test_suggestion_test_without_trigger(self):
        """Test the suggestion test endpoint without trigger text"""
        response = client.post("/test/suggestion?text=Hello there")
        assert response.status_code == 200
        data = response.json()
        assert data["triggered"] == False
        assert data["suggestions"] == []

def run_manual_tests():
    """Run manual tests that require user interaction"""
    print("\n🧪 Running Manual Tests")
    print("=" * 40)
    
    print("1. Testing health endpoint...")
    response = client.get("/health")
    health_data = response.json()
    print(f"   Status: {health_data['status']}")
    print(f"   OpenAI configured: {health_data['openai_configured']}")
    
    print("\n2. Testing trigger detection...")
    test_phrases = [
        "How much does this cost?",
        "That seems expensive",
        "Hello there",
        "What about security?"
    ]
    
    for phrase in test_phrases:
        triggered = should_generate_suggestions(phrase)
        print(f"   '{phrase}' -> Triggered: {triggered}")
    
    print("\n3. Testing suggestion endpoint...")
    response = client.post("/test/suggestion?text=How much does this cost?")
    if response.status_code == 200:
        data = response.json()
        print(f"   Triggered: {data['triggered']}")
        print(f"   Suggestions: {len(data.get('suggestions', []))}")
    
    print("\n✅ Manual tests completed!")
    print("\nTo run automated tests, use:")
    print("python -m pytest test_backend.py -v")

if __name__ == "__main__":
    # Run manual tests if called directly
    run_manual_tests()