import asyncio

import numpy as np
from openai import AsyncOpenAI, RateLimitError
from sentence_transformers import SentenceTransformer

from app.config import (
    CEREBRAS_API_KEY,
    CEREBRAS_BASE_URL,
    EMBEDDING_MODEL,
    GENERATION_MODEL,
    INGESTION_MODEL,
)

_OPENAI_CHAT_PARAMS = {
    "frequency_penalty",
    "logit_bias",
    "logprobs",
    "max_tokens",
    "max_completion_tokens",
    "n",
    "presence_penalty",
    "response_format",
    "seed",
    "stop",
    "stream",
    "temperature",
    "tool_choice",
    "tools",
    "top_logprobs",
    "top_p",
    "user",
}

_MAX_RETRIES = 5
_BACKOFF_SECONDS = (1, 2, 4, 8, 16)


async def cerebras_llm_complete(
    prompt,
    system_prompt=None,
    history_messages=None,
    model_override=None,
    **kwargs,
):
    """Async LLM completion via Cerebras's OpenAI-compatible API.

    LightRAG passes extra kwargs (e.g. ``keyword_extraction``, ``mode``,
    ``hashing_kv``) that the OpenAI client rejects — we whitelist only valid
    chat-completion params. On 429, we retry up to 5 times with exponential
    backoff (1, 2, 4, 8, 16s).
    """
    client = AsyncOpenAI(api_key=CEREBRAS_API_KEY, base_url=CEREBRAS_BASE_URL)
    model = model_override or GENERATION_MODEL

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    if history_messages:
        messages.extend(history_messages)
    messages.append({"role": "user", "content": prompt})

    safe_kwargs = {k: v for k, v in kwargs.items() if k in _OPENAI_CHAT_PARAMS}
    safe_kwargs.setdefault("max_tokens", 4096)

    for attempt in range(_MAX_RETRIES + 1):
        try:
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                **safe_kwargs,
            )
            return response.choices[0].message.content
        except RateLimitError:
            if attempt >= _MAX_RETRIES:
                raise
            delay = _BACKOFF_SECONDS[attempt]
            print(
                f"Rate limited. Retrying in {delay}s... "
                f"(attempt {attempt + 1}/{_MAX_RETRIES})"
            )
            await asyncio.sleep(delay)


async def cerebras_llm_for_ingestion(
    prompt,
    system_prompt=None,
    history_messages=None,
    model_override=None,
    **kwargs,
):
    """LLM wrapper used during LightRAG ingestion.

    Routes to a smaller/faster Cerebras model since ingestion makes many calls
    for entity/relationship extraction.
    """
    return await cerebras_llm_complete(
        prompt,
        system_prompt=system_prompt,
        history_messages=history_messages,
        model_override=model_override or INGESTION_MODEL,
        **kwargs,
    )


_embed_model = None


def get_embed_model() -> SentenceTransformer:
    """Load the SentenceTransformer once and reuse it.

    The model is heavy to construct (downloads weights on first call), so we
    cache it at module level.
    """
    global _embed_model
    if _embed_model is None:
        _embed_model = SentenceTransformer(EMBEDDING_MODEL)
    return _embed_model


async def local_embedding_func(texts: list[str]) -> np.ndarray:
    """Embed a list of strings with the cached SentenceTransformer.

    Returns a numpy array of shape (len(texts), embedding_dim). LightRAG's
    EmbeddingFunc wrapper expects a numpy array.
    """
    model = get_embed_model()
    return model.encode(texts, convert_to_numpy=True)
