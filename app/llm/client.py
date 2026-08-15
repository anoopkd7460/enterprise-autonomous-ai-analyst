"""
Thin wrapper around the LLM provider so the rest of the app never talks
to the OpenAI SDK directly. Swap providers here later (Phase 2+) without
touching agent code.
"""
from openai import OpenAI

from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

client = OpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)


def chat(system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str:
    """Single-turn chat completion. Returns plain text."""
    response = client.chat.completions.create(
        model=settings.LLM_MODEL,
        temperature=temperature,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content.strip()