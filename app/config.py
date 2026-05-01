import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY is not set. Copy .env.example to .env and add your "
        "Groq API key (get one at https://console.groq.com/keys)."
    )

GROQ_BASE_URL = "https://api.groq.com/openai/v1"

GENERATION_MODEL = os.getenv("GENERATION_MODEL", "llama-3.1-70b-versatile")
EVALUATION_MODEL = os.getenv("EVALUATION_MODEL", "gemma2-9b-it")

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "384"))

WORKING_DIR = os.getenv("LIGHTRAG_WORKING_DIR", "./data/rag_storage")
DEFAULT_QUERY_MODE = os.getenv("DEFAULT_QUERY_MODE", "hybrid")
