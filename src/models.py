from pydantic import BaseModel
from typing import List, Optional

class Message(BaseModel):
    role: str  # "user" or "bot"
    message: str

class DebateRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str

class DebateResponse(BaseModel):
    conversation_id: str
    message: List[Message]
