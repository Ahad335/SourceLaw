# Indian Legal AI Assistant 🪶

Indian law is dense, scattered across PDFs, and written in language most
people weren't trained to parse. This project tries to close that gap: ask a
question in plain English, and get an answer grounded in actual Indian legal
text — the Constitution, labour laws, social security acts, and more —
retrieved live via a RAG (Retrieval-Augmented Generation) pipeline.

Nothing here is generated from thin air. Every answer points back to the
exact source PDF, the page it came from, and the excerpt that backs it up —
so you can always check the model's work.

## Tech Stack
- **Frontend:** React 18 + Vite
- **Backend:** FastAPI
- **Framework:** LangChain
- **Embeddings:** BAAI/bge-small-en-v1.5 (runs locally, CPU)
- **Vector store:** FAISS (persisted to disk)
- **LLM:** Llama 3.3 70B via the Groq API

## Project Structure
```
api.py                  # FastAPI backend (POST /api/chat, GET /api/health)
build_index.py          # one-off script: embed data/ into a FAISS index
src/
  config.py             # all settings (paths, model names, constants)
  document_loader.py    # load + split PDFs
  embeddings.py         # embedding model
  vectorstore.py        # FAISS index (build + persist + load)
  rag.py                # retrieve -> prompt -> answer
  llm.py                # chat model
frontend/               # React + Vite chat UI
data/                   # legal PDFs
faiss_index/            # generated vector index (build artifact)
```

## Getting It Running

### 1. Backend
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

You'll need a Groq API key for this to actually generate answers — grab a
free one at https://console.groq.com/keys, then drop it into a `.env` file:
```
GROQ_API_KEY=gsk_your_key_here
```

That key is only used at answer-generation time. Embeddings run locally on
CPU, so `build_index.py` doesn't need it at all.

Now build the index — this embeds all 38 source PDFs and takes a few minutes:
```powershell
python build_index.py
```

Then bring the API up:
```powershell
uvicorn api:app --reload --port 8000
```

### 2. Frontend
Open a second terminal:
```powershell
cd frontend
npm install
npm run dev
```
Head to http://localhost:5173 — Vite proxies `/api` calls through to the
backend on port 8000.

Ports already taken on your machine? Vite will quietly grab the next free
one for itself; just point it at wherever the backend actually landed:
```powershell
uvicorn api:app --reload --port 8011
$env:VITE_API_TARGET="http://127.0.0.1:8011"; npm run dev
```

## A Few Things Worth Knowing
- `faiss_index/` is a build artifact, but it's intentionally **not**
  git-ignored — committing it means deployments skip re-embedding 38 PDFs on
  every cold start. Delete and re-run `build_index.py` whenever the source
  PDFs change.
- Retrieval is scored on FAISS L2 distance, where **lower means closer**.
  Anything farther than `MAX_DISTANCE` (default `1.0`, in `src/config.py`)
  gets dropped before it ever reaches the LLM — and if nothing survives that
  filter, the assistant says so instead of guessing. That threshold isn't
  arbitrary: on this corpus, on-topic questions consistently score
  0.5–0.8, while off-topic ones land at 1.1–1.3.

## Disclaimer
This tool is for informational purposes only and does not constitute legal advice.