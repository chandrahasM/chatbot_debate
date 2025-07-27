from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
import os

def get_llm(api_key: str = None):
    """Initialize the OpenAI LLM"""
    if api_key is None:
        api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
    
    return ChatOpenAI(
        model="gpt-3.5-turbo",  # Using GPT-3.5 for cost efficiency
        api_key=api_key,
        temperature=0.7,
        max_tokens=500
    )

def get_prompt():
    """Get the debate prompt template"""
    return PromptTemplate(
        input_variables=["history", "user_message", "topic", "stance"],
        template="""You are a persuasive chatbot defending the stance: {stance} on the topic: {topic}.

Your role is to:
1. Stay firmly committed to your stance, even if it seems unconventional or controversial
2. Use logical arguments, analogies, examples, and evidence to support your position
3. Be engaging, friendly, but persistent in your viewpoint
4. If the user tries to change topics, gently redirect back to {topic}
5. Counter the user's arguments while remaining respectful
6. Ask thought-provoking questions to make the user reconsider their position

Topic: {topic}
Your stance: {stance}

Conversation history:
{history}

User's latest message: {user_message}

Respond persuasively while maintaining your stance on {topic}:"""
    )

def get_memory():
    """Get conversation memory buffer"""
    return ConversationBufferWindowMemory(
        k=5,  # Keep last 5 exchanges
        return_messages=True,
        memory_key="history"
    )
