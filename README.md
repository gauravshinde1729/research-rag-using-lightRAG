# Research Paper Q&A — LightRAG + RAGAS

Ask questions across research PDFs. LightRAG handles retrieval, **Cerebras** generates answers, **Groq** scores them with RAGAS.

## Architecture

```
                            ┌──────────────────────┐
   PDFs ──upload──▶ INGEST ─┤  Cerebras (8B)       │──▶ entities + KG
                            │  llama3.1-8b         │
                            └──────────────────────┘
                                       │
                                       ▼
                            ┌──────────────────────┐
                            │  LightRAG storage    │
                            │  (graph + vectors)   │
                            └──────────────────────┘
                                       │
   Question ──▶ QUERY ──retrieve───────┘
       │                                
       │                ┌──────────────────────┐
       └───generate────▶│  Cerebras (70B)      │──▶ Answer + contexts
                        │  llama-3.3-70b       │           │
                        └──────────────────────┘           │
                                                           ▼
                        ┌──────────────────────┐    ┌─────────────┐
                        │  Groq judge          │◀───│  RAGAS      │
                        │  llama-3.3-70b-vers. │    │  metrics    │
                        └──────────────────────┘    └─────────────┘
                                                           │
                                                           ▼
                                                   eval_history/scores.json

   Frontend (Vite :5173) ──/api/*──▶ FastAPI (:8000) ──▶ LightRAG
```

Generation and judging run on **different providers on purpose** — the judge can't grade its own work.

## Setup

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cd frontend; npm install; cd ..
```

Copy `.env.example` → `.env`:

```env
GROQ_API_KEY=gsk_...
CEREBRAS_API_KEY=csk-...
GENERATION_MODEL=llama-3.3-70b
INGESTION_MODEL=llama3.1-8b
EVALUATION_MODEL=llama-3.3-70b-versatile
```

## Run

Two terminals:

```powershell
# Terminal 1 — API
.venv\Scripts\activate
uvicorn app.api:app --reload --port 8000
```

```powershell
# Terminal 2 — UI
cd frontend
npm run dev
```

Open http://localhost:5173.

## Test

```powershell
pytest -v
```
