import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env")

from app.rag.models import groq_llm_complete  # noqa: E402


@pytest.mark.asyncio
async def test_groq_llm_complete_returns_string():
    response = await groq_llm_complete("Say hello in one word")
    print("Response:", response)
    assert isinstance(response, str)
    assert len(response.strip()) > 0


@pytest.mark.asyncio
async def test_groq_llm_complete_filters_lightrag_kwargs():
    """LightRAG passes extras like keyword_extraction/mode/hashing_kv.
    These must be filtered out without raising an OpenAI client error."""
    response = await groq_llm_complete(
        "Say hello in one word",
        keyword_extraction=False,
        mode="hybrid",
        hashing_kv=None,
    )
    assert isinstance(response, str)
    assert len(response.strip()) > 0
