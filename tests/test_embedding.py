import sys
from pathlib import Path

import numpy as np
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / ".env")

from app.rag.models import local_embedding_func  # noqa: E402

EMBED_DIM = 384


async def test_embedding_returns_numpy_array():
    result = await local_embedding_func(["hello world"])
    assert isinstance(result, np.ndarray)


async def test_embedding_correct_shape():
    texts = ["the cat sat on the mat", "transformers changed NLP"]
    result = await local_embedding_func(texts)
    assert result.shape == (2, EMBED_DIM)


async def test_embedding_single_text():
    result = await local_embedding_func(["just one sentence"])
    assert result.shape == (1, EMBED_DIM)


async def test_embedding_deterministic():
    text = ["deterministic check"]
    first = await local_embedding_func(text)
    second = await local_embedding_func(text)
    assert np.array_equal(first, second)
