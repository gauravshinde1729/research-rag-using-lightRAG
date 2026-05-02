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
    not os.getenv("CEREBRAS_API_KEY"),
    reason="CEREBRAS_API_KEY not set",
)


SAMPLE_TEXT = (
    "Photosynthesis is the process by which green plants convert sunlight, "
    "carbon dioxide, and water into glucose and oxygen. It takes place mainly "
    "in the chloroplasts of plant cells, where the pigment chlorophyll "
    "absorbs light energy. The overall reaction releases oxygen as a "
    "byproduct, which is essential for most life on Earth."
)


async def test_create_rag_engine(tmp_path):
    from lightrag import LightRAG

    from app.rag.engine import create_rag_engine

    rag = await create_rag_engine(working_dir=str(tmp_path / "rag_storage"))
    assert isinstance(rag, LightRAG)
    assert (tmp_path / "rag_storage").exists()


async def test_ingest_and_query(tmp_path):
    from app.rag.engine import create_rag_engine, ingest_text, query_rag

    rag = await create_rag_engine(working_dir=str(tmp_path / "rag_storage"))
    await ingest_text(rag, SAMPLE_TEXT)

    result = await query_rag(rag, "What does photosynthesis produce?", mode="naive")

    assert isinstance(result["answer"], str)
    assert len(result["answer"].strip()) > 0
    assert isinstance(result["contexts"], list)
