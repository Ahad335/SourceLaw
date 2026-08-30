# Creates the chat LLM served by Groq.
import os
from functools import lru_cache

from langchain_groq import ChatGroq

from src.config import LLM_MODEL, MAX_NEW_TOKENS, TEMPERATURE

MISSING_KEY_MESSAGE = (
    "GROQ_API_KEY is not set. Add it to your .env file "
    "(get a key at https://console.groq.com/keys), then restart the server."
)


@lru_cache(maxsize=1)
def get_chat_model():
    # Fail with a readable message instead of a bare 401 mid-question.
    if not os.getenv("GROQ_API_KEY"):
        raise RuntimeError(MISSING_KEY_MESSAGE)

    return ChatGroq(
        model=LLM_MODEL,
        temperature=TEMPERATURE,
        max_tokens=MAX_NEW_TOKENS,
    )
