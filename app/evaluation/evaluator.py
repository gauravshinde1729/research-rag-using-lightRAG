"""RAGAS v0.4 evaluation using Groq's OpenAI-compatible API as the judge."""

from __future__ import annotations

import asyncio
import typing as t

import numpy as np
from openai import AsyncOpenAI
from ragas.embeddings.base import BaseRagasEmbedding
from ragas.llms import llm_factory
from ragas.metrics.collections import (
    AnswerRelevancy as _ResponseRelevancy,
)
from ragas.metrics.collections import (
    ContextPrecisionWithoutReference as _ContextPrecision,
)
from ragas.metrics.collections import (
    Faithfulness,
)

from app.config import EVALUATION_MODEL, GROQ_API_KEY, GROQ_BASE_URL
from app.rag.models import get_embed_model


class _LocalSentenceTransformerEmbedding(BaseRagasEmbedding):
    """Wraps the cached SentenceTransformer in RAGAS's modern embedding interface.

    AnswerRelevancy needs an embeddings model to compare generated questions
    against the original. We reuse the same local model that LightRAG indexed
    with so judge-side similarity stays consistent with retrieval.
    """

    def embed_text(self, text: str, **kwargs: t.Any) -> list[float]:
        return get_embed_model().encode([text], convert_to_numpy=True)[0].tolist()

    async def aembed_text(self, text: str, **kwargs: t.Any) -> list[float]:
        return await asyncio.to_thread(self.embed_text, text)

    def embed_texts(self, texts: list[str], **kwargs: t.Any) -> list[list[float]]:
        arr: np.ndarray = get_embed_model().encode(texts, convert_to_numpy=True)
        return arr.tolist()

    async def aembed_texts(self, texts: list[str], **kwargs: t.Any) -> list[list[float]]:
        return await asyncio.to_thread(self.embed_texts, texts)


async def create_judge_llm():
    """Build the RAGAS judge LLM backed by Groq's OpenAI-compatible endpoint."""
    client = AsyncOpenAI(api_key=GROQ_API_KEY, base_url=GROQ_BASE_URL)
    return llm_factory(EVALUATION_MODEL, provider="openai", client=client)


async def evaluate_query(
    question: str, answer: str, contexts: list[str]
) -> dict:
    """Score a single RAG query with Faithfulness, ResponseRelevancy, ContextPrecision.

    Each metric runs independently — a failure in one does not block the others.
    Failed metrics return None and an `<name>_error` entry holds the message.
    """
    judge_llm = await create_judge_llm()
    embeddings = _LocalSentenceTransformerEmbedding()

    scores: dict = {}

    # Faithfulness: is every claim in the answer supported by the contexts?
    try:
        scorer = Faithfulness(llm=judge_llm)
        result = await scorer.ascore(
            user_input=question,
            response=answer,
            retrieved_contexts=contexts,
        )
        scores["faithfulness"] = float(result.value)
    except Exception as e:
        scores["faithfulness"] = None
        scores["faithfulness_error"] = str(e)

    # ResponseRelevancy: does the answer actually address the question?
    try:
        scorer = _ResponseRelevancy(llm=judge_llm, embeddings=embeddings)
        result = await scorer.ascore(user_input=question, response=answer)
        scores["response_relevancy"] = float(result.value)
    except Exception as e:
        scores["response_relevancy"] = None
        scores["response_relevancy_error"] = str(e)

    # ContextPrecision: WithoutReference variant — uses the response as the
    # comparison target since we have no ground-truth reference at query time.
    try:
        scorer = _ContextPrecision(llm=judge_llm)
        result = await scorer.ascore(
            user_input=question,
            response=answer,
            retrieved_contexts=contexts,
        )
        scores["context_precision"] = float(result.value)
    except Exception as e:
        scores["context_precision"] = None
        scores["context_precision_error"] = str(e)

    return scores
