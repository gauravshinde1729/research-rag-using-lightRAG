"""Tests for app.evaluation.evaluator. Requires GROQ_API_KEY (live judge calls)."""

import os
import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env")

# Skip the entire module at collection time if no API key — this prevents
# `from app.config import ...` (which raises on missing key) from blowing up.
pytestmark = pytest.mark.skipif(
    not os.getenv("GROQ_API_KEY"),
    reason="GROQ_API_KEY not set",
)


@pytest.mark.asyncio
async def test_evaluate_query_returns_dict():
    from app.evaluation.evaluator import evaluate_query

    scores = await evaluate_query(
        question="What is machine learning?",
        answer=(
            "Machine learning is a subset of AI that enables systems to learn "
            "from data."
        ),
        contexts=[
            "Machine learning is a branch of artificial intelligence that "
            "allows computer systems to learn and improve from experience and "
            "data without being explicitly programmed."
        ],
    )

    assert isinstance(scores, dict)
    for key in ("faithfulness", "response_relevancy", "context_precision"):
        assert key in scores, f"missing {key} in {scores}"
        value = scores[key]
        assert value is None or (isinstance(value, float) and 0.0 <= value <= 1.0), (
            f"{key} should be None or a float in [0, 1], got {value!r}"
        )


@pytest.mark.asyncio
async def test_evaluate_unfaithful_answer():
    from app.evaluation.evaluator import evaluate_query

    scores = await evaluate_query(
        question="What is machine learning?",
        answer="Machine learning was invented in 2025 by Elon Musk.",
        contexts=[
            "Machine learning is a branch of artificial intelligence that has "
            "been developed since the 1950s."
        ],
    )

    faithfulness = scores.get("faithfulness")
    if faithfulness is not None:
        assert faithfulness < 0.5, (
            f"unfaithful answer should score below 0.5, got {faithfulness}"
        )
