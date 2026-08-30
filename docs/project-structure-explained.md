# Project Structure & Core Concepts — Explained

> A beginner-friendly walkthrough of the **Indian Legal AI Assistant**: what it is,
> the ideas behind it, how every file fits together, and the exact commands used to
> build and test it. Read this top to bottom — each section builds on the last.

---

## 1. The big picture: what does this project do?

You ask a legal question in plain English → the app finds the most relevant
passages from ~40 real Indian legal PDFs → it hands those passages to an AI model
→ the model answers **using only those passages** and cites the source + page.

This pattern has a name: **RAG (Retrieval-Augmented Generation)**.

Why not just ask ChatGPT directly? Because a raw language model:
- might **make up** laws that sound real but aren't ("hallucination"),
- doesn't know **your specific documents**,
- can't tell you **which page** an answer came from.

RAG fixes all three by forcing the model to answer from documents *you* provide.

---

## 2. Core concepts (the mental model)

Think of it as a **library + a smart librarian**.

| Concept | Plain-English meaning | Where it lives in our code |
|---|---|---|
| **Document loading** | Read the PDFs off disk into text. | `src/document_loader.py` |
| **Chunking** | Cut long documents into small pieces (~800 chars) so search is precise. A whole 200-page act is too big to feed the model; a paragraph is just right. | `src/document_loader.py` |
| **Embeddings** | Turn each chunk of text into a list of numbers (a "vector") that captures its *meaning*. Similar meanings → similar numbers. | `src/embeddings.py` |
| **Vector store (FAISS)** | A specialized database that stores those number-vectors and can instantly find the ones closest to your question. This is the "index". | `src/vectorstore.py` |
| **Retrieval** | Convert your question into a vector too, then ask FAISS "which chunks are nearest?" Those are the relevant passages. | `app.py` (the `similarity_search` call) |
| **LLM (the generator)** | The chat model (Llama 3.3 70B on Groq) that writes the final answer from the retrieved passages. | `src/llm.py` |
| **Prompt grounding** | The instructions we wrap around the passages: "Answer ONLY from this context, cite source + page." | `app.py` (the `context_message`) |

### The one-sentence flow
**Load → Chunk → Embed → Store (FAISS) → [user asks] → Retrieve → Ground → Generate → Answer.**

### Why "embeddings" are the clever part
A keyword search for "child labour age" would miss a document that says "minimum
age for employment of adolescents." Embeddings match on **meaning**, not exact
words — so the librarian finds the right passage even when the wording differs.

---

## 3. The folder structure (and why it looks like this)

```
FirstProject/
├── app.py                    # Entry point — the Streamlit web UI
├── src/                      # All the "engine" code, one file per job
│   ├── __init__.py           # Empty file. Tells Python "src is a package"
│   ├── config.py             # Every setting in ONE place (paths, model names, numbers)
│   ├── document_loader.py    # Load PDFs + chunk them
│   ├── embeddings.py         # The text→vector model
│   ├── vectorstore.py        # Build the FAISS index
│   └── llm.py                # The chat model
├── data/                     # The source PDFs (organized in sub-folders by topic)
├── docs/                     # Plans + explanations (this folder)
│   ├── completion-plan.md    # The roadmap to "CV-ready + deployed"
│   └── project-structure-explained.md  # ← you are here
├── .env                      # Your secret API token (NEVER committed to GitHub)
├── .gitignore                # List of files Git should ignore
├── requirements.txt          # The exact Python packages needed to run this
└── README.md                 # First thing a recruiter reads
```

### Why split one file into many?
The original code was **one 180-line `app.py`** with everything mixed together.
That's fine for a quick experiment but hard to read, test, and fix. Real projects
follow the **"separation of concerns"** principle:

> Each file should have **one reason to change.**

- Change the embedding model? → only `embeddings.py`.
- Change a folder path or chunk size? → only `config.py`.
- Change how the UI looks? → only `app.py`.

This makes the code easier to learn, debug, and show to an interviewer.

### Why a `src/` package + `__init__.py`?
Putting the engine code in a `src/` folder keeps the root clean (the root just has
the entry point + config files). The empty `__init__.py` is what lets us write
`from src.config import DATA_PATH` — it marks `src` as an importable **package**.

---

## 4. Every file, explained

### `src/config.py` — the control panel
Holds **all** the values you might want to tweak, as named constants:
`DATA_PATH`, `EMBEDDING_MODEL`, `LLM_MODEL`, `CHUNK_SIZE`, `CHUNK_OVERLAP`,
`TOP_K`, `SCORE_THRESHOLD`, `TEMPERATURE`, `MAX_NEW_TOKENS`.
It also calls `load_dotenv()` once, which reads your secret token from `.env`.

**Why it matters:** instead of hunting through code for a magic number like `800`,
you change it in one obvious place. Every other file *imports* from here.

### `src/document_loader.py` — the reader + the knife
Two functions:
- `load_all_documents()` — walks every sub-folder of `data/` (using `os.walk`),
  opens each `.pdf`, and tags each page with its filename + page number (so we can
  cite it later).
- `split_documents()` — cuts those pages into ~800-character chunks with 150 chars
  of overlap (overlap stops a sentence getting cut in half between two chunks).

**Key design choice:** because it scans *all* sub-folders, **you can add more PDFs
by just dropping files into `data/` — no code change needed.**

### `src/embeddings.py` — the meaning encoder
Loads the `BAAI/bge-small-en-v1.5` model and returns it. This model converts text
into 384-number vectors. It's small and runs on CPU (slowly) or GPU (fast).

### `src/vectorstore.py` — the index builder
Ties the previous three together: load docs → chunk → embed → build a **FAISS**
index from all the chunk-vectors. The result is the searchable "brain" of the app.

### `src/llm.py` — the writer
Connects to the `llama-3.3-70b-versatile` chat model via Groq's hosted
Inference API (so you don't need a giant GPU to *run* the model — HuggingFace runs
it for you). `temperature=0.5` keeps answers fairly focused, not too random.

### `app.py` — the web app (entry point)
The only file you run directly. It:
1. Draws the page title + chat input box (Streamlit).
2. Calls `get_vectorstore()` and `get_chat_model()` (cached, so they build once).
3. When you ask a question: retrieves the top matching chunks, builds the grounded
   prompt, calls the model, and displays the answer + disclaimer.

### `@st.cache_resource` — the speed trick you'll see everywhere
Building the index is expensive. This Streamlit decorator means "run this function
**once** and reuse the result" — so re-running the app on every keystroke doesn't
re-embed all the PDFs each time.

### Supporting files
- **`.env`** — `GROQ_API_KEY=gsk_xxx`. Your secret. Listed in
  `.gitignore` so it never reaches GitHub. **Format note:** no quotes around the
  key name, or `load_dotenv()` silently fails to read it.
- **`.gitignore`** — stops `venv/` (48,000 files!), `.env` (secret!), and Python
  cache from being committed.
- **`requirements.txt`** — the dependency list so anyone (or a deploy server) can
  recreate your environment with `pip install -r requirements.txt`.
- **`README.md`** — the project's front page on GitHub.

---

## 5. How the data flows (end-to-end)

```
   data/*.pdf
       │  load_all_documents()      → 2,390 pages
       ▼
   raw page text
       │  split_documents()          → 9,851 chunks (~800 chars each)
       ▼
   text chunks
       │  get_embeddings()           → each chunk becomes a 384-number vector
       ▼
   vectors  ──────────────►  FAISS index  (the searchable "brain")
                                   ▲
   your question ── embed ─────────┘   similarity_search_with_score(k=5)
       │
       ▼
   top-5 relevant chunks
       │  wrapped in a grounded prompt ("answer ONLY from this, cite source+page")
       ▼
   Llama 3.3 70B (LLM)  →  final answer + citation
```

---

## 6. How the index was built & tested (exact commands)

These are the real commands used to verify the restructured project. Run them from
the project root with the virtual environment's Python.

**a) Syntax check — does every file parse?**
```bash
./venv/Scripts/python.exe -m py_compile app.py src/config.py src/document_loader.py src/embeddings.py src/vectorstore.py src/llm.py
```

**b) Import check — do the `src` imports wire together?**
```bash
./venv/Scripts/python.exe -c "import src.config, src.document_loader, src.embeddings, src.vectorstore, src.llm; print('ALL IMPORTS OK')"
```

**c) Confirm the secret token loads from `.env`:**
```bash
./venv/Scripts/python.exe -c "from dotenv import load_dotenv; load_dotenv(); import os; print('KEY LOADED:', bool(os.environ.get('GROQ_API_KEY')))"
```

**d) Launch the app (the real end-to-end run):**
```bash
./venv/Scripts/python.exe -m streamlit run app.py
```
Then open the Local URL it prints (e.g. http://localhost:8501).

**e) Build the FAISS index directly (what actually indexes the PDFs):**
```bash
./venv/Scripts/python.exe -c "
from src.document_loader import load_all_documents, split_documents
from src.embeddings import get_embeddings
from langchain_community.vectorstores import FAISS
docs   = load_all_documents('data')          # 2,390 pages
chunks = split_documents(docs)               # 9,851 chunks
emb    = get_embeddings()                     # loads bge-small
vs     = FAISS.from_documents(chunks, emb)    # builds the index
hits   = vs.similarity_search_with_score('What are fundamental rights?', k=3)
print('hits:', len(hits))
"
```

### What we observed
- **2,390 PDF pages → 9,851 chunks.** The structure works; the embedding model
  loads fine even on Python 3.14.
- Building the index on **CPU is very slow** (embedding 9,851 chunks takes many
  minutes). This is the single biggest reason to do the next two things ↓

### How to build it *fast* (on your lab GPU)
1. Tell the embedding model to use the GPU — in `src/embeddings.py`:
   ```python
   HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL, model_kwargs={"device": "cuda"})
   ```
2. **Build once, then save the index** so the app never re-embeds on startup:
   ```python
   vs.save_local("faiss_index")   # run once after building
   ```
3. **Load the saved index** on every app start (seconds instead of minutes):
   ```python
   FAISS.load_local("faiss_index", emb, allow_dangerous_deserialization=True)
   ```
> Adding more PDFs later? Drop them anywhere under `data/`, then re-run the build
> step (e) once and re-save. No other code changes needed.

---

## 7. Known issues (intentionally left for the next step)

The restructure deliberately **kept the original logic unchanged**, so three known
bugs are still present and will be fixed in a separate pass:
1. **Retrieval filter** (`score < 0.5`) likely rejects all chunks → empty context.
2. **Chat history mixes types** → crashes on the 2nd question.
3. **`None` append** before the input check + history never displayed.

See `docs/completion-plan.md` for the full roadmap to a deployed, CV-ready project.

---

## 8. Quick glossary

- **RAG** — Retrieval-Augmented Generation: answer from retrieved docs, not memory.
- **Embedding** — a list of numbers representing text *meaning*.
- **Vector store / index** — database of embeddings you can search by similarity.
- **FAISS** — Facebook AI Similarity Search; the library that does that search.
- **Chunk** — a small slice of a document used as the unit of retrieval.
- **LLM** — Large Language Model; here, Llama 3.3 70B, which writes the answer.
- **Token (API)** — your secret key to use HuggingFace's hosted models.
- **`venv`** — an isolated Python environment so this project's packages don't
  clash with other projects.
```

