import pytest
from fastapi.testclient import TestClient
from src.main import app
import os

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "openai_configured" in data

def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Debate Chatbot API"
    assert data["version"] == "1.0.0"
    assert "endpoints" in data
    assert "usage" in data

@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OpenAI API key not configured")
def test_new_conversation():
    """Test starting a new conversation"""
    request_data = {
        "conversation_id": None,
        "message": "Debate that the Earth is flat, take the pro side"
    }
    
    response = client.post("/debate", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "conversation_id" in data
    assert len(data["message"]) == 2  # User message + bot response
    assert data["message"][0]["role"] == "user"
    assert data["message"][1]["role"] == "bot"
    assert data["message"][0]["message"] == "Debate that the Earth is flat, take the pro side"
    assert len(data["message"][1]["message"]) > 0

@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OpenAI API key not configured")
def test_continue_conversation():
    """Test continuing an existing conversation"""
    # Start a conversation
    start_request = {
        "conversation_id": None,
        "message": "Debate that vaccines are harmful, take the pro side"
    }
    
    start_response = client.post("/debate", json=start_request)
    assert start_response.status_code == 200
    
    conversation_id = start_response.json()["conversation_id"]
    
    # Continue the conversation
    continue_request = {
        "conversation_id": conversation_id,
        "message": "But vaccines have saved millions of lives!"
    }
    
    continue_response = client.post("/debate", json=continue_request)
    assert continue_response.status_code == 200
    
    data = continue_response.json()
    assert data["conversation_id"] == conversation_id
    assert len(data["message"]) == 4  # 2 previous + 2 new messages

def test_empty_message():
    """Test sending an empty message"""
    request_data = {
        "conversation_id": None,
        "message": ""
    }
    
    response = client.post("/debate", json=request_data)
    assert response.status_code == 400

def test_invalid_conversation_id():
    """Test using an invalid conversation ID"""
    request_data = {
        "conversation_id": "invalid-id-12345",
        "message": "Hello there"
    }
    
    # This will fail if OpenAI is not configured, but for different reason
    response = client.post("/debate", json=request_data)
    assert response.status_code in [400, 500]  # Either invalid ID or service unavailable

def test_missing_openai_key():
    """Test behavior when OpenAI API key is missing"""
    # This test assumes the key might not be set in test environment
    if not os.getenv("OPENAI_API_KEY"):
        request_data = {
            "conversation_id": None,
            "message": "Test message"
        }
        
        response = client.post("/debate", json=request_data)
        assert response.status_code == 500
        assert "OPENAI_API_KEY" in response.json()["detail"]

@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OpenAI API key not configured")
def test_multiple_messages_same_conversation():
    """Test multiple messages in the same conversation"""
    # Start conversation
    request1 = {
        "conversation_id": None,
        "message": "Debate that climate change is a hoax, take the pro side"
    }
    
    response1 = client.post("/debate", json=request1)
    conversation_id = response1.json()["conversation_id"]
    
    # Send multiple follow-up messages
    messages = [
        "That's an interesting point, tell me more",
        "I disagree with your assessment",
        "Can you provide some evidence?",
        "What about the scientific consensus?"
    ]
    
    for i, message in enumerate(messages):
        request = {
            "conversation_id": conversation_id,
            "message": message
        }
        
        response = client.post("/debate", json=request)
        assert response.status_code == 200
        
        data = response.json()
        assert data["conversation_id"] == conversation_id
        # Should have at most 10 messages (5 pairs)
        assert len(data["message"]) <= 10
        # Should have at least the current exchange
        assert len(data["message"]) >= 2

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
