"""FastAPI backend for the Research Paper Q&A app.

Run with: `uvicorn app.api:app --reload --port 8000`
Endpoints: /api/ingest, /api/query, /api/history, /api/aggregates, /api/status.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from typing import Any

# `uvicorn app.api:app` runs from the project root, so app.* imports resolve.
# This sys.path insert is just a safety net for direct execution.
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.evaluation.evaluator import evaluate_query
from app.evaluation.history import (
    get_aggregate_scores,
    load_history,
    save_score,
)
from app.ingestion.pdf_parser import extract_text_from_pdf
from app.rag.engine import create_rag_engine, ingest_text, query_rag

app = FastAPI(title="Research Paper Q&A API")

# Vite dev server runs on 5173. Allow it plus a couple of common alternates so
# the frontend can hit /api/* directly without a proxy if desired.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


_rag = None
_ingested_count = 0


async def _get_rag():
    """Lazy-create a single LightRAG instance shared across requests.

    Building the engine downloads the embed model and opens nano-vectordb
    storage, so we only do it on first use rather than at process start.
    """
    global _rag
    if _rag is None:
        _rag = await create_rag_engine()
    return _rag


class QueryRequest(BaseModel):
    question: str
    mode: str = "hybrid"


class QueryResponse(BaseModel):
    answer: str
    contexts: list[str]
    scores: dict[str, Any]


@app.get("/api/status")
async def status() -> dict:
    return {
        "ingested_count": _ingested_count,
        "rag_initialized": _rag is not None,
    }


@app.post("/api/ingest")
async def ingest(files: list[UploadFile] = File(...)) -> dict:
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")

    rag = await _get_rag()
    ingested = 0
    errors: list[dict] = []

    for upload in files:
        # Persist to a temp file because pypdf reads from a path. We delete
        # immediately after extraction to avoid filling disk on long sessions.
        suffix = Path(upload.filename or "doc.pdf").suffix or ".pdf"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await upload.read())
            tmp_path = Path(tmp.name)

        try:
            text = extract_text_from_pdf(str(tmp_path))
            if text.strip():
                await ingest_text(rag, text)
                ingested += 1
            else:
                errors.append({"file": upload.filename, "error": "empty after extract"})
        except Exception as e:
            errors.append({"file": upload.filename, "error": str(e)})
        finally:
            tmp_path.unlink(missing_ok=True)

    global _ingested_count
    _ingested_count += ingested

    return {"status": "ok", "ingested": ingested, "total": _ingested_count, "errors": errors}


@app.post("/api/query", response_model=QueryResponse)
async def query(req: QueryRequest) -> QueryResponse:
    if _rag is None:
        raise HTTPException(
            status_code=400,
            detail="No documents ingested yet. POST /api/ingest first.",
        )

    rag = await _get_rag()
    rag_result = await query_rag(rag, req.question, mode=req.mode)
    answer = rag_result["answer"]
    contexts = rag_result["contexts"]

    scores = await evaluate_query(req.question, answer, contexts)
    save_score(req.question, answer, scores, contexts)

    return QueryResponse(answer=answer, contexts=contexts, scores=scores)


@app.get("/api/history")
def history() -> dict:
    return {"history": load_history()}


@app.get("/api/aggregates")
def aggregates() -> dict:
    return {"aggregates": get_aggregate_scores()}
