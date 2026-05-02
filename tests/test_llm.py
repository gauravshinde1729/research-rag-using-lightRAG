"""Tests for the Cerebras LLM functions in app.rag.models.

Filename kept as test_groq_llm.py for git history; contents are Cerebras now.
Skips at collection time if CEREBRAS_API_KEY is not set so CI passes without secrets.
"""

import os
import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env")

pytestmark = pytest.mark.skipif(
    not os.getenv("CEREBRAS_API_KEY"),
    reason="CEREBRAS_API_KEY not set",
)


@pytest.mark.asyncio
async def test_cerebras_llm_complete_returns_string():
    from app.rag.models import cerebras_llm_complete

    response = await cerebras_llm_complete("Say hello in one word")
    assert isinstance(response, str)
    assert len(response.strip()) > 0


@pytest.mark.asyncio
async def test_cerebras_llm_complete_filters_lightrag_kwargs():
    """LightRAG passes extras like keyword_extraction/mode/hashing_kv.
    These must be filtered out without raising an OpenAI client error."""
    from app.rag.models import cerebras_llm_complete

    response = await cerebras_llm_complete(
        "Say hello in one word",
        keyword_extraction=False,
        mode="hybrid",
        hashing_kv=None,
    )
    assert isinstance(response, str)
    assert len(response.strip()) > 0


@pytest.mark.asyncio
async def test_cerebras_llm_for_ingestion_returns_string():
    from app.rag.models import cerebras_llm_for_ingestion

    response = await cerebras_llm_for_ingestion("Say hello in one word")
    assert isinstance(response, str)
    assert len(response.strip()) > 0
