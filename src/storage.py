import sqlite3
import json
from typing import List, Dict, Optional, Tuple

class Storage:
    def __init__(self, db_path: str = "chat.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize the database with the conversations table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                conversation_id TEXT PRIMARY KEY,
                topic TEXT NOT NULL,
                stance TEXT NOT NULL,
                messages TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def create_conversation(self, conversation_id: str, topic: str, stance: str, messages: List[Dict[str, str]]):
        """Create a new conversation in the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO conversations (conversation_id, topic, stance, messages) VALUES (?, ?, ?, ?)",
            (conversation_id, topic, stance, json.dumps(messages))
        )
        conn.commit()
        conn.close()

    def get_conversation(self, conversation_id: str) -> Optional[Tuple[str, str, List[Dict[str, str]]]]:
        """Retrieve a conversation from the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT topic, stance, messages FROM conversations WHERE conversation_id = ?",
            (conversation_id,)
        )
        result = cursor.fetchone()
        conn.close()
        
        if result:
            topic, stance, messages_json = result
            return topic, stance, json.loads(messages_json)
        return None

    def update_conversation(self, conversation_id: str, messages: List[Dict[str, str]]):
        """Update the messages for an existing conversation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE conversations SET messages = ? WHERE conversation_id = ?",
            (json.dumps(messages), conversation_id)
        )
        conn.commit()
        conn.close()

    def conversation_exists(self, conversation_id: str) -> bool:
        """Check if a conversation exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM conversations WHERE conversation_id = ?",
            (conversation_id,)
        )
        result = cursor.fetchone()
        conn.close()
        return result is not None
