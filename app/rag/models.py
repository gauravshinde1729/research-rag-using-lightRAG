import numpy as np
from openai import AsyncOpenAI
from sentence_transformers import SentenceTransformer

from app.config import EMBEDDING_MODEL, GENERATION_MODEL, GROQ_API_KEY, GROQ_BASE_URL

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


async def groq_llm_complete(
    prompt,
    system_prompt=None,
    history_messages=None,
    **kwargs,
):
    """Async LLM completion using Groq's OpenAI-compatible API.

    LightRAG passes extra kwargs (e.g. ``keyword_extraction``, ``mode``,
    ``hashing_kv``) that the OpenAI client does not accept. We whitelist only
    valid chat-completion parameters and drop the rest.
    """
    client = AsyncOpenAI(api_key=GROQ_API_KEY, base_url=GROQ_BASE_URL)

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    if history_messages:
        messages.extend(history_messages)
    messages.append({"role": "user", "content": prompt})

    safe_kwargs = {k: v for k, v in kwargs.items() if k in _OPENAI_CHAT_PARAMS}
    safe_kwargs.setdefault("max_tokens", 4096)

    response = await client.chat.completions.create(
        model=GENERATION_MODEL,
        messages=messages,
        **safe_kwargs,
    )
    return response.choices[0].message.content


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
