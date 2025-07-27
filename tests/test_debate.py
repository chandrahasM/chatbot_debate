import pytest
from src.debate_service import DebateService
from src.storage import Storage
import os
import tempfile

@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    yield db_path
    # Cleanup
    try:
        os.unlink(db_path)
    except:
        pass

def test_storage_init(temp_db):
    """Test storage initialization"""
    storage = Storage(temp_db)
    assert storage.db_path == temp_db

def test_parse_topic_stance():
    """Test topic and stance parsing"""
    # Mock service without OpenAI for testing parsing logic
    service = DebateService.__new__(DebateService)
    
    # Test pro stance
    topic, stance = service.parse_topic_stance("Debate that the Earth is flat, take the pro side")
    assert "Earth is flat" in topic
    assert stance == "pro"
    
    # Test against stance
    topic, stance = service.parse_topic_stance("Argue against climate change")
    assert "climate change" in topic
    assert stance == "against"
    
    # Test default
    topic, stance = service.parse_topic_stance("The moon landing was fake")
    assert "moon landing" in topic.lower()
    assert stance == "pro"

def test_conversation_storage(temp_db):
    """Test conversation storage operations"""
    storage = Storage(temp_db)
    
    # Test conversation creation
    conv_id = "test-123"
    topic = "Test topic"
    stance = "pro"
    messages = [{"role": "user", "message": "Hello"}]
    
    storage.create_conversation(conv_id, topic, stance, messages)
    
    # Test conversation retrieval
    result = storage.get_conversation(conv_id)
    assert result is not None
    retrieved_topic, retrieved_stance, retrieved_messages = result
    assert retrieved_topic == topic
    assert retrieved_stance == stance
    assert retrieved_messages == messages
    
    # Test conversation update
    new_messages = messages + [{"role": "bot", "message": "Hi there"}]
    storage.update_conversation(conv_id, new_messages)
    
    result = storage.get_conversation(conv_id)
    _, _, retrieved_messages = result
    assert len(retrieved_messages) == 2
    assert retrieved_messages[1]["message"] == "Hi there"
    
    # Test non-existent conversation
    result = storage.get_conversation("non-existent")
    assert result is None

def test_format_history():
    """Test history formatting"""
    # Mock service without OpenAI
    service = DebateService.__new__(DebateService)
    
    messages = [
        {"role": "user", "message": "First message"},
        {"role": "bot", "message": "First response"},
        {"role": "user", "message": "Second message"}
    ]
    
    history = service.format_history(messages)
    assert "Human: First message" in history
    assert "Assistant: First response" in history
    assert "Human: Second message" in history
    
    # Test empty history
    history = service.format_history([])
    assert history == "No previous conversation."

@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OpenAI API key not configured")
def test_debate_service_integration(temp_db):
    """Test full debate service integration"""
    service = DebateService(temp_db, os.getenv("OPENAI_API_KEY"))
    
    # Test new conversation
    conv_id, messages = service.handle_debate(None, "Debate that pineapple belongs on pizza, pro side")
    
    assert conv_id is not None
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[1]["role"] == "bot"
    assert len(messages[1]["message"]) > 0
    
    # Test continuing conversation
    conv_id2, messages2 = service.handle_debate(conv_id, "But pineapple is too sweet for pizza!")
    
    assert conv_id2 == conv_id
    assert len(messages2) == 4
    assert messages2[-1]["role"] == "bot"

def test_error_handling():
    """Test error handling in debate service"""
    # Test with invalid database path and no OpenAI key
    with pytest.raises(ValueError):
        service = DebateService("/invalid/path", None)
    
    # Test empty message
    if os.getenv("OPENAI_API_KEY"):
        service = DebateService(openai_api_key=os.getenv("OPENAI_API_KEY"))
        with pytest.raises(ValueError):
            service.handle_debate(None, "")
        
        with pytest.raises(ValueError):
            service.handle_debate(None, "   ")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
