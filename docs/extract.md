# Project Profile — Extract for CV & Portfolio

> **Last verified against the code:** 2026-07-17.
> **Tagging rule:** `[DONE]` = verified in the current code today. `[PLANNED]` = only in
> `docs/completion-plan.md`, not yet built. `NOT FOUND` = couldn't verify either way.
> **Write CV bullets ONLY from `[DONE]` items.**
>
> **State as of this update:** code is unchanged since the last profile — the RAG pipeline
> builds and the app launches, the **3 known logic bugs and the hardcoded token remain**,
> and there are **still 0 commits**. `.gitignore` is present and correct (covers `venv/`,
> `.env`, `__pycache__/`, `*.pyc`, `.streamlit/secrets.toml`, `faiss_index/`).

---

## 1. Identity
- **Project name:** Indian Legal AI Assistant
- **One-line description:** A RAG chatbot that answers Indian legal questions in plain English with source-cited document passages.
- **Type:** Personal project
- **Current completion %:** ~60% `[DONE]` — full RAG pipeline is coded and the app launches, but it is **not yet verified to answer correctly end-to-end** (3 known logic bugs remain) and is **not deployed**.
- **Target completion per plan:** 100% = runs end-to-end with correct cited answers + deployed at a public URL + README with screenshot. `[PLANNED]`

---

## 2. The Problem
- **What it solves:** Indian legal documents (the Constitution, labour laws, social-security acts) are long, scattered, and hard for non-lawyers to read. This tool lets a user ask a plain-English question and get a simple answer grounded in the actual legal text, with the source document and page cited — reducing hallucination versus asking a general chatbot.
- **Target user/audience:** Students, gig/informal-sector workers, and ordinary citizens who need a quick, sourced starting point on basic Indian legal rights (explicitly *not* a substitute for legal advice).

---

## 3. Technical Stack

### `[DONE]` — currently wired up in the code
- **Language:** Python (running on Python 3.14 in the local venv)
- **UI:** Streamlit (chat interface — `app.py`)
- **RAG framework:** LangChain — `langchain`, `langchain-core`, `langchain-community`, `langchain-huggingface`, `langchain-text-splitters`
- **PDF loading:** `pypdf` via LangChain `PyPDFLoader`
- **Embeddings:** `sentence-transformers` running `BAAI/bge-small-en-v1.5` (384-dim)
- **Vector store:** `faiss-cpu` (FAISS)
- **LLM:** `Qwen/Qwen2.5-7B-Instruct` via HuggingFace Inference API (`huggingface-hub`)
- **Config/secrets:** `python-dotenv` (`.env`)
- ⚠️ **Gap:** `requirements.txt` lists package **names only — no pinned versions.** Pin them before deploy for reproducibility.

### `[PLANNED]` — per completion-plan.md, not in code yet
- Persisted FAISS index (`save_local`/`load_local`) instead of rebuilding on every start
- GPU embedding (`model_kwargs={"device":"cuda"}`) for fast rebuilds
- Deployment runtime pinned to **Python 3.11** (3.14 has a Pydantic-v1 incompatibility warning)
- Hosting layer (Hugging Face Spaces / Streamlit Cloud)

---

## 4. Architecture & Key Decisions

### `[DONE]` — how it's currently built
- **Modular `src/` package** (refactored from a single script): `config.py` (all settings), `document_loader.py` (load + chunk), `embeddings.py`, `vectorstore.py`, `llm.py`, with `app.py` as the thin Streamlit entry point.
- **Pipeline (verified to run):** `load_all_documents()` walks every sub-folder of `data/` and tags each page with `source` + `page` → `split_documents()` chunks at 800 chars / 150 overlap → `bge-small` embeddings → `FAISS.from_documents()` builds the index (`src/vectorstore.py`).
- **Retrieval + grounding (coded):** `app.py:39` `similarity_search_with_score(k=5)`, then a system prompt (`app.py:62`) instructing "answer ONLY from context, cite source + page."
- **Caching:** `@st.cache_resource` on all heavy builders so they run once.
- ⚠️ **Honest caveat:** the retrieval filter `score < 0.5` (`app.py:43`) likely rejects all chunks (FAISS L2 distance), and chat history mixes types (`app.py:84`) — so while the code runs, **correct multi-turn answers are not yet verified.** These are the bugs the plan fixes.

### `[PLANNED]` — architecture changes in the plan
- Fix retrieval scoring, unify chat-history type, render history, add empty-result/error handling
- Persist the FAISS index; load it on startup
- Deploy with secrets via the host's secret manager

### Scale indicators that exist NOW `[DONE]`
- **Source code:** 379 lines total across 7 `.py` files (`app.py` 274 incl. ~180 lines of commented-out dead code to be removed → ~95 real lines; `src/` ~105 lines).
- **Knowledge base:** **39 legal PDFs**, ~**91 MB**, across 5 topic folders (Acts &
  policies, Child and women labour, Constitution of India, Legal documents, Social securities).
- **Indexed corpus (measured in testing):** **2,390 pages → 9,851 chunks** embedded into FAISS.
- **Commits:** 0 (git initialized on branch `master`, first commit still pending as of 2026-07-17).

---

## 5. Results / Metrics

### `[DONE]` — real numbers that exist today
- Dataset size: **39 PDFs / ~91 MB across 5 topic folders** (Acts & policies, Child and
  women labour, Constitution of India, Legal documents, Social securities); **2,390 pages
  → 9,851 chunks** (measured during a real index build).
- Embedding dimension: 384 (`bge-small-en-v1.5`).
- **No accuracy, latency, or retrieval-quality metric has been measured yet.**

### `[PLANNED]` — metrics achievable once the plan ships, and what to instrument
| Metric | How to capture it (instrument while building) | Unlocked by plan task |
|---|---|---|
| Query latency (median, s) | `time.time()` around retrieve + `chat.invoke` | Tasks 2–3 (working pipeline) |
| Retrieval hit-rate (%) | Hand-build 8–10 Q→expected-doc pairs; measure top-k hits | Nice-to-have #3 (eval harness) |
| Cold-start vs warm-start time | Time index build vs `load_local` | Task 6 (persist index) |
| Corpus size (N chunks/pages) | Already have it: 9,851 / 2,390 | `[DONE]` |

> **Start capturing now:** wrap the query path in a timer and log chunk count — those two give you latency + corpus-size numbers for free as soon as the bugs are fixed.

---

## 6. CV Material — STRICT

### Resume bullets from `[DONE]` work only
- **Data Scientist / ML:**
  *Built a Retrieval-Augmented Generation (RAG) pipeline over **2,390 pages (9,851 chunks)** of Indian legal documents using LangChain, `bge-small` embeddings, and a FAISS vector store, with prompt-grounded, source-cited responses.*
  *(Every number here is verified. Safe to use.)*
- **SDE:**
  *Refactored a 180-line prototype into a modular Python package (config / loaders / embeddings / vector store / LLM) behind a Streamlit app, with environment-based secret management and a reproducible dependency setup.*
- **Data Analyst:**
  *Not enough built yet for a DA bullet — this project has no data-analysis/visualization or metrics layer. Needs the eval harness (plan Nice-to-have #3) before it tells a DA story, and even then it's a weak DA fit. Use a different project for DA.*

### Future bullets (DO NOT use yet — tied to a plan task)
| Future bullet | Unlocked by |
|---|---|
| "Deployed the assistant to a public URL serving grounded legal answers with **[X]s** median latency." | Plan Task 10 (deploy) + Task 2–3 (fix pipeline) |
| "Improved answer reliability to **[Y]%** retrieval hit-rate on a hand-built eval set." | Nice-to-have #3 (eval harness) |
| "Cut app cold-start from minutes to **[Z]s** by persisting the FAISS index." | Task 6 (persist index) |
| "Supported multi-turn legal Q&A with full conversation history." | Tasks 3–4 (fix + render history) |

> **Highest CV payoff:** deploying (Task 10) + fixing the retrieval/history bugs (Tasks 2–4) converts three of the four future bullets into usable ones.

---

## 7. For the Portfolio Website
- **Card title:** *Indian Legal AI Assistant — RAG over Indian Law*
- **2-sentence summary:** An AI assistant that answers everyday Indian legal questions in plain English, grounding every answer in real legal documents and citing the exact source and page. Built with a LangChain + FAISS retrieval pipeline and a Qwen2.5-7B model behind a Streamlit chat UI. *(Note: the first live version may show fewer features than this description until the bug-fix + deploy tasks land.)*
- **Live demo:** `[PLANNED]` — per the plan, **Hugging Face Spaces (Streamlit SDK), free tier.** It **is** deployable on a free tier: embeddings run on CPU and the LLM is a remote HF Inference endpoint (no local GPU needed). Watch only for HF free-tier rate limits. Pin Python 3.11 on the host.
- **Screenshot/visual to capture once built:** a Q→A exchange showing the answer **with the cited source + page** visible (that citation is the project's differentiator). A short GIF of one question→answer is ideal.
- **README status:** Usable but **needs minor work** — the Project Structure and Setup code blocks have broken/unclosed markdown fences, and there's no screenshot yet. Good enough to link after a 15-min cleanup.

---

## 8. Build Priority Signal
- **High-CV-value vs polish:** Of the remaining planned work, the **high-value** slice is small and concrete — fix retrieval + history (Tasks 2–4) and deploy (Task 10). Persisting the index (Task 6) is value + needed for deploy. The rest (README polish, descoping) is polish.
- **Honest take:** **Worth finishing.** The hard part (a real RAG pipeline over real data) already runs; you're debugging + shipping, not rebuilding. A *deployed, citation-grounded* legal RAG app is a differentiated GenAI portfolio piece for DS/ML and SDE. It is **not** a Data Analyst project — don't spend DA effort here.
- **Effort to first CV-usable state:** ~**6–9 focused hours** (fix 3 bugs + persist index + deploy + capture latency number). Full polish per plan: ~12–16h.

---

## 9. Cleanup / Secrets Check
- 🔴 **URGENT — hardcoded token in code that will be pushed:** `app.py:100`, inside a large commented-out dead-code block (lines ~96–274), contains `HUGGINGFACEHUB_API_TOKEN = "hf_DQDE…"`. Comments are committed to GitHub. **This block must be deleted before the first push, and that token rotated.**
- 🔴 **Second leaked token in `.env`** (`hf_Wtay…`). `.env` is correctly git-ignored so it won't be pushed, **but it was exposed in plaintext earlier — rotate it** at huggingface.co/settings/tokens.
- 🟡 **Dead code to cut:** the entire commented-out old script at the bottom of `app.py` (~180 lines). It's a duplicate of the refactored modules, adds noise, and holds the secret above. Delete it.
- 🟡 **README markdown fences** are unclosed/broken in the Structure and Setup sections — fix so GitHub renders them cleanly.
- 🟡 **Pin dependency versions** in `requirements.txt` before deploy.
- ✅ **`.gitignore` is in place and correct** — excludes `venv/`, `.env`, `__pycache__/`,
  `*.pyc`, `.streamlit/secrets.toml`, and `faiss_index/`. (No action needed here; the
  secret risk is the *hardcoded* token in `app.py:100`, not `.env`.)

---

### Summary (for chat)
- **DONE:** modular RAG pipeline (load→chunk→embed→FAISS→retrieve→ground→generate) that builds an index over 39 PDFs / 2,390 pages / 9,851 chunks, Streamlit UI launches, env-based secrets, requirements + .gitignore + README present.
- **PLANNED:** fix 3 logic bugs (retrieval filter, chat-history types, history rendering), persist FAISS index, deploy to HF Spaces, capture latency/hit-rate metrics.
- **Secrets:** one token in `.env` (ignored — rotate) and one **hardcoded in `app.py:100` that will be pushed (delete + rotate now).**
