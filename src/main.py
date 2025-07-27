from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .models import DebateRequest, DebateResponse, Message
from .debate_service import DebateService
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Debate Chatbot API",
    description="A REST API for a chatbot that engages in debates and maintains specified stances",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize debate service
try:
    debate_service = DebateService(
        db_path="chat.db", 
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
except Exception as e:
    print(f"Warning: Could not initialize DebateService: {e}")
    debate_service = None

@app.post("/debate", response_model=DebateResponse)
async def debate(request: DebateRequest):
    """
    Main debate endpoint that handles conversation requests.
    
    - **conversation_id**: null for new conversations, existing ID to continue
    - **message**: The user's message to debate about
    
    Returns the conversation_id and last 5 message pairs.
    """
    # Check for empty message first
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    if debate_service is None:
        raise HTTPException(
            status_code=500, 
            detail="Service not available. Please check OPENAI_API_KEY environment variable."
        )
    
    try:
        conversation_id, messages = debate_service.handle_debate(
            request.conversation_id, 
            request.message
        )
        
        # Convert to response format
        message_objects = [
            Message(role=msg["role"], message=msg["message"]) 
            for msg in messages
        ]
        
        return DebateResponse(
            conversation_id=conversation_id,
            message=message_objects
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "openai_configured": os.getenv("OPENAI_API_KEY") is not None
    }

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Debate Chatbot API",
        "version": "1.0.0",
        "description": "A REST API for engaging in persuasive debates",
        "endpoints": {
            "POST /debate": "Main debate endpoint",
            "GET /health": "Health check",
            "GET /docs": "API documentation"
        },
        "usage": {
            "new_conversation": {
                "conversation_id": None,
                "message": "Debate that the Earth is flat, take the pro side"
            },
            "continue_conversation": {
                "conversation_id": "your-conversation-id",
                "message": "But what about satellite images?"
            }
        },
        "note": "Always start with conversation_id: null for new conversations. Use the returned conversation_id for follow-up messages."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
