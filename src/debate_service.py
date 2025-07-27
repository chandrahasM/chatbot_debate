from typing import List, Dict, Tuple
import uuid
import re
from .storage import Storage
from .prompts import get_llm, get_prompt

class DebateService:
    def __init__(self, db_path: str = "chat.db", openai_api_key: str = None):
        self.storage = Storage(db_path)
        # Store API key for direct OpenAI usage
        self.openai_api_key = openai_api_key

    def parse_topic_stance(self, message: str) -> Tuple[str, str]:
        """Parse topic and stance from the initial user message"""
        message_lower = message.lower()
        
        # Look for explicit stance indicators
        if any(phrase in message_lower for phrase in ["pro side", "support", "defend", "argue for"]):
            # Extract topic after stance indicator
            for phrase in ["pro side of", "support", "defend", "argue for"]:
                if phrase in message_lower:
                    topic = message.split(phrase, 1)[-1].strip()
                    return topic, "pro"
        
        elif any(phrase in message_lower for phrase in ["against", "oppose", "argue against", "con side"]):
            # Extract topic after opposition indicator
            for phrase in ["against", "oppose", "argue against", "con side of"]:
                if phrase in message_lower:
                    topic = message.split(phrase, 1)[-1].strip()
                    return topic, "against"
        
        # Look for debate keywords and extract topic
        if "debate" in message_lower:
            # Remove "debate" and common words to extract topic
            topic = re.sub(r'\b(debate|that|the|is|are)\b', '', message, flags=re.IGNORECASE).strip()
            topic = re.sub(r'\s+', ' ', topic)  # Clean up extra spaces
            return topic, "pro"  # Default to pro stance
        
        # Default: treat entire message as topic with pro stance
        return message.strip(), "pro"

    def format_history(self, messages: List[Dict[str, str]]) -> str:
        """Format conversation history for the prompt"""
        if not messages:
            return "No previous conversation."
        
        formatted = []
        for msg in messages[-10:]:  # Last 10 messages (5 pairs)
            role = "Human" if msg["role"] == "user" else "Assistant"
            formatted.append(f"{role}: {msg['message']}")
        
        return "\n".join(formatted)

    def generate_bot_response(self, topic: str, stance: str, history: str, user_message: str) -> str:
        """Generate a persuasive bot response using OpenAI directly"""
        try:
            import os
            from openai import OpenAI
            
            # Check if API key is available
            api_key = os.getenv("OPENAI_API_KEY")
            print(f"DEBUG: API key present: {bool(api_key)}")  # Debug logging
            
            if not api_key:
                raise ValueError("OpenAI API key not found")
            
            # Create OpenAI client directly
            client = OpenAI(api_key=api_key)
            
            # Create a more focused prompt
            system_prompt = f"""You are a persuasive debater who strongly supports the {stance} side of: {topic}

Your role:
- Defend your position passionately but respectfully
- Use logical arguments and examples
- Counter the user's points while staying on topic
- Be engaging and thought-provoking
- Never back down from your stance

Topic: {topic}
Your stance: {stance}"""
            
            user_prompt = f"""Conversation history:
{history}

User's latest message: {user_message}

Respond persuasively while maintaining your {stance} stance on {topic}:"""
            
            print(f"DEBUG: Calling OpenAI API...")  # Debug logging
            print(f"DEBUG: System prompt: {system_prompt[:100]}...")  # Debug logging
            print(f"DEBUG: User prompt: {user_prompt[:100]}...")  # Debug logging
            
            # Call OpenAI API directly
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            bot_response = response.choices[0].message.content.strip()
            print(f"DEBUG: OpenAI response: {bot_response[:100]}...")  # Debug logging
            
            return bot_response
            
        except Exception as e:
            print(f"ERROR in generate_bot_response: {str(e)}")  # Debug logging
            print(f"ERROR type: {type(e).__name__}")  # Debug logging
            # Better fallback response with actual debate content
            if stance == "pro":
                return f"I absolutely believe that {topic}! Here's why: This position has strong merit and deserves serious consideration. What specific aspect would you like me to elaborate on?"
            else:
                return f"I strongly disagree with {topic}. Here's my counterargument: There are significant flaws in that reasoning that need to be addressed. What evidence are you basing your position on?"

    def handle_debate(self, conversation_id: str = None, user_message: str = "") -> Tuple[str, List[Dict[str, str]]]:
        """Main method to handle debate conversations"""
        if not user_message.strip():
            raise ValueError("Message cannot be empty")
        
        if conversation_id is None:
            # New conversation
            conversation_id = str(uuid.uuid4())
            topic, stance = self.parse_topic_stance(user_message)
            
            # Initialize with user message
            messages = [{"role": "user", "message": user_message}]
            
            # Generate bot response
            history = self.format_history([])
            bot_response = self.generate_bot_response(topic, stance, history, user_message)
            messages.append({"role": "bot", "message": bot_response})
            
            # Store new conversation
            self.storage.create_conversation(conversation_id, topic, stance, messages)
            
        else:
            # Existing conversation
            conversation_data = self.storage.get_conversation(conversation_id)
            if not conversation_data:
                raise ValueError(f"Conversation with ID '{conversation_id}' not found. Please start a new conversation by setting conversation_id to null.")
            
            topic, stance, messages = conversation_data
            
            # Add user message
            messages.append({"role": "user", "message": user_message})
            
            # Generate bot response
            history = self.format_history(messages[:-1])  # Exclude the just-added user message
            bot_response = self.generate_bot_response(topic, stance, history, user_message)
            messages.append({"role": "bot", "message": bot_response})
            
            # Update conversation
            self.storage.update_conversation(conversation_id, messages)
        
        # Return conversation_id and last 10 messages (5 pairs)
        recent_messages = messages[-10:]
        return conversation_id, recent_messages
