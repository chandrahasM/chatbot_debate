#!/usr/bin/env python3
"""
Simple test script to verify OpenAI API key is working
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_openai_connection():
    """Test if OpenAI API key is working"""
    try:
        from openai import OpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        print(f"API key present: {bool(api_key)}")
        
        if not api_key:
            print("❌ No OpenAI API key found in environment variables")
            print("Please set OPENAI_API_KEY in your .env file")
            return False
        
        print(f"API key starts with: {api_key[:10]}...")
        
        # Test API connection
        client = OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Say 'Hello, API is working!'"}
            ],
            max_tokens=10
        )
        
        result = response.choices[0].message.content.strip()
        print(f"✅ OpenAI API is working! Response: {result}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API test failed: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    print("Testing OpenAI API connection...")
    test_openai_connection()
