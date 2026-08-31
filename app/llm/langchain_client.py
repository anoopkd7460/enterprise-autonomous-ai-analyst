from langchain_groq import ChatGroq
from app.core.config import settings

def get_chat_model() -> ChatGroq:
    """
    Return the LangChain-compatible Groq chat model.

    this adapter keeps LangChain-specific LLM configuration separate from 
    the rest of the application
    """

    return ChatGroq(
        model=settings.LLM_MODEL,
        api_key=settings.OPENAI_API_KEY,
        temperature=0.2,
    )