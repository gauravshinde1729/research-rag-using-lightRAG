from pathlib import Path

from lightrag import LightRAG, QueryParam
from lightrag.utils import EmbeddingFunc

from app.config import EMBEDDING_DIM, WORKING_DIR
from app.rag.models import groq_llm_complete, local_embedding_func


async def create_rag_engine(working_dir: str | None = None) -> LightRAG:
    """Build and initialize a LightRAG instance wired to our Groq LLM and
    local sentence-transformers embedder.

    LightRAG requires `initialize_storages()` to be awaited before any query
    or ingest call (auto_manage_storages_states defaults to False).
    """
    wd = working_dir or WORKING_DIR
    Path(wd).mkdir(parents=True, exist_ok=True)

    rag = LightRAG(
        working_dir=wd,
        llm_model_func=groq_llm_complete,
        embedding_func=EmbeddingFunc(
            embedding_dim=EMBEDDING_DIM,
            max_token_size=8192,
            func=local_embedding_func,
        ),
    )
    await rag.initialize_storages()
    return rag


async def query_rag(rag: LightRAG, question: str, mode: str = "hybrid") -> dict:
    """Query LightRAG and return both the answer and the retrieved contexts.

    Uses `aquery_llm` (not the legacy `aquery`) because it returns the
    structured retrieval data alongside the LLM response in a single pass —
    we need the raw chunk text for RAGAS metrics.
    """
    param = QueryParam(mode=mode)
    result = await rag.aquery_llm(question, param=param)

    answer = result.get("llm_response", {}).get("content") or ""
    chunks = result.get("data", {}).get("chunks", []) or []
    contexts = [c.get("content", "") for c in chunks if c.get("content")]

    return {"answer": answer, "contexts": contexts}


async def ingest_text(rag: LightRAG, text: str) -> None:
    """Insert a single document. LightRAG handles chunking, entity/relationship
    extraction, and KG construction internally — these involve many LLM calls,
    so this is slow on first ingestion.
    """
    await rag.ainsert(text)
