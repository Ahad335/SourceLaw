# Completion & Polish Plan — Indian Legal AI Assistant (RAG)

> **Primary target role:** Data Scientist / ML (GenAI) · **Secondary:** SDE
> **Verdict up front:** Finish this — ~12–16 focused hours to CV-ready. It's worth it.

---

## 🔴 DO THIS FIRST (5 min, before anything else)
Your HuggingFace API token is **hardcoded in `app.py:5`** and a *second, different* token is in `.env`. Both are now leaked.
1. Go to https://huggingface.co/settings/tokens → **revoke both tokens**.
2. Create one new token (Read access is enough for Inference).
3. Put it ONLY in `.env` (never in `app.py`). Confirm `.env` is git-ignored before the first commit.

---

## 1. Current State (verified from code)

**What works right now:**
- Full RAG scaffold is present: PDF loading (`os.walk` over `data/`), recursive text splitting (800/150), `bge-small-en-v1.5` embeddings, FAISS vector store, Qwen2.5-7B HF endpoint, Streamlit chat UI.
- 38 real legal PDFs across 6 categories (constitution, child/women labour, social security, acts & policies, legal documents).
- Retrieval pulls `source` + `page` metadata for citations — good instinct.
- `@st.cache_resource` used correctly to avoid re-embedding on every rerun.

**What's stubbed / broken / incomplete:**
- **Retrieval threshold bug** (`app.py:126`): `score < 0.5` against FAISS L2 distance likely filters out *all* chunks → empty context → hallucinated/empty answers. **This is the main reason it "doesn't really work."**
- **History type collision** (`app.py:103` vs `168`): `chat_history` holds LangChain message objects *and* a raw dict; `chat.invoke()` breaks on the 2nd question.
- **`None`-append bug** (`app.py:114-116`): runs outside the `if user_input` guard; appends `None` each load. `message_history` is also never displayed.
- Secrets hardcoded (see top section).
- FAISS index is rebuilt from scratch on every cold start (slow first load; no persistence).

**What's completely missing:**
- `requirements.txt` (nothing is reproducible/deployable without it).
- `README.md` (setup, screenshot, what it does, disclaimer).
- `.gitignore` (must exclude `venv/`, `.env`, `__pycache__/`).
- Git repo (not initialized) + GitHub remote.
- Any deployment.
- Error handling / empty-result message when no relevant law is found.

---

## 2. Definition of "CV-Ready Done" for THIS project
The project is done when **all** of these are true:
- Runs end-to-end locally: ask a legal question → get a grounded answer **with source + page citation** → ask a follow-up → no crash.
- Retrieval actually returns relevant chunks (verified on 3 sample questions).
- Deployed at a **public URL** anyone can open (recruiter can click and try it).
- No secrets in code; token loaded from env/secrets manager.
- `README.md` with: one-line pitch, setup steps, **1 screenshot or GIF**, and the "not legal advice" disclaimer.
- Pushed to a clean public GitHub repo (no `venv/`, no `.env`).

Anything past this is optional (Section 5).

---

## 3. MUST-DO (to reach CV-ready) — ordered

| # | Task | File(s) | Effort | Why it matters |
|---|------|---------|--------|----------------|
| 1 | **Revoke + move token to `.env`.** Delete `os.environ[...] = "hf_..."` line; rely on `load_dotenv()`. | `app.py`, `.env` | S | A committed API key is an instant red flag to any technical reviewer. |
| 2 | **Fix retrieval filter.** Switch to relevance scores (use `vectorstore.similarity_search` with k=5, OR normalize: FAISS L2 → keep all top-k, or use `score_threshold` via a retriever with `search_type="similarity_score_threshold"`). Simplest reliable fix: drop the `< 0.5` filter, keep top-5, and only fall back to "no relevant law found" if 0 docs. | `app.py:122-127` | S | Without this the bot answers from empty context — the core feature is broken. |
| 3 | **Fix chat history.** Use ONE consistent type. Keep a single `st.session_state.messages` list of LangChain objects (`SystemMessage`/`HumanMessage`/`AIMessage`). Append `AIMessage(result.content)`, not a dict. | `app.py:101-171` | M | Currently crashes on the 2nd question — interviewers WILL ask a follow-up. |
| 4 | **Render chat history + fix `None` append.** Move the append inside `if user_input:`, and loop over history to display prior turns on each rerun. | `app.py:108-120` | S | A chat app that forgets/duplicates messages looks unfinished. |
| 5 | **Handle the empty-result + error path.** If no relevant chunk, reply: "I couldn't find this in the loaded legal documents." Wrap `chat.invoke` in try/except with a friendly message. | `app.py` | S | Demos break on edge questions; graceful handling reads as "production-minded." |
| 6 | **Persist the FAISS index.** Build once, `vectorstore.save_local("faiss_index")`; load with `FAISS.load_local(...)` if it exists. Commit the index (it's small) so deploy doesn't re-embed 38 PDFs on every cold boot. | `app.py:73-79` | M | Cold-start on a free host re-embedding 38 PDFs = timeout. This makes deploy actually work + gives you a latency metric. |
| 7 | **Add `requirements.txt`** (pin versions). Generate from the working venv, trim to what's imported. | new file | S | Nothing deploys without it. |
| 8 | **Add `.gitignore`** (`venv/`, `.env`, `__pycache__/`, `*.pyc`). | new file | S | Prevents leaking the venv (48k files) and `.env` to GitHub. |
| 9 | **Write `README.md`** — pitch, architecture line, setup, screenshot/GIF, disclaimer. | new file | M | The README is what a recruiter reads first; no README = looks abandoned. |
| 10 | **Deploy (Section 4) + smoke-test the public URL** on 3 questions. | — | M | "Deployed at a public URL" is the single biggest credibility multiplier. |
| 11 | **`git init`, commit, push to public GitHub.** | — | S | The repo link goes on your CV. |

> ⚠️ **Python 3.14 risk:** your venv is on 3.14.0 (very new). `faiss-cpu`/`torch` wheels may not exist for 3.14 on your deploy host. **Pin the deploy runtime to Python 3.11** (HF Spaces / Streamlit Cloud both let you set this). Test the build early — don't leave it to the end.

---

## 4. Deployment Plan (required)

**Recommended host: Hugging Face Spaces (Streamlit SDK).** Why: free, generous memory (16 GB) so the `bge-small` embedding model + torch fit comfortably, native HF-token secret handling, and it's the natural home for an HF-powered app. (Streamlit Community Cloud is a fine alternative but has a tighter ~1 GB memory ceiling that torch + faiss can bump against.)

**Exact steps (HF Spaces):**
1. Create a Space → SDK: **Streamlit** → name e.g. `indian-legal-ai-assistant`.
2. Add a `README.md` header block (Spaces needs the YAML front-matter) OR just push files via git.
3. Push these files: `app.py`, `requirements.txt`, `data/`, the committed `faiss_index/`, `README.md`. **Do NOT push `venv/` or `.env`.**
4. **Secrets:** In the Space → Settings → *Variables and secrets* → add `HUGGINGFACEHUB_API_TOKEN` = your new token. In code, read it via `os.environ`/`load_dotenv()` (already wired) — Spaces injects secrets as env vars. **Never hardcode.**
5. **Pin Python 3.11**: add a `runtime.txt`/use Space settings, or set in README front-matter (`python_version: 3.11`).
6. Open the public URL, run 3 sample questions, confirm citations appear.

**Secrets handling:** token lives only in (a) local `.env` (git-ignored) and (b) the host's secrets UI. Never in `app.py`, never in the repo.

**Cost:** Free tier on HF Spaces (CPU basic) is sufficient — embeddings run on CPU, the LLM is a remote HF Inference endpoint. **$0.** Only watch: HF Inference free tier rate limits; if the Qwen endpoint gets throttled, note it in the README and/or swap to a smaller served model.

**Fallback (if free CPU is too slow or rate-limited):** record a 30–60s screen GIF of a working Q→A→follow-up session, embed it in the README, and state in the README that the live demo runs on a free tier (may cold-start). But aim for live — this project *can* be deployed live.

---

## 5. NICE-TO-HAVE (only after MUST-DO + deploy ship)
Ranked by impact-per-effort. **Do not start these until the public URL works.**

1. **Show retrieved sources in an expander under each answer** (clickable "📄 Sources" with doc + page). *Adds:* visible proof it's real RAG, not a chatbot. *Impresses:* DS/ML + SDE. *Effort: S.*
2. **Category filter in sidebar** (constitution / labour / social security / …) → filter retrieval by metadata. *Adds:* a real product feature + shows you understand metadata filtering. *Impresses:* SDE/DS. *Effort: M.*
3. **Eval harness** — 8–10 hand-written Q&A pairs in a notebook measuring retrieval hit-rate / answer groundedness. *Adds:* a hard metric for your resume bullet + signals ML rigor. *Impresses:* Data Scientist most. *Effort: M.*
4. **Streaming responses** (`st.write_stream`) for a snappier demo. *Adds:* polish. *Impresses:* SDE. *Effort: S.*

---

## 6. What to CUT or DESCOPE
- **The commented-out experimentation blocks** (app.py:22-24, 45-46, 59-60, 167) — delete them; commented dead code reads as unfinished.
- **The dual history lists** (`chat_history` *and* `message_history`) — collapse to ONE list. The current split is the source of the type-collision bug.
- **Don't add auth, user accounts, or a database.** Out of scope; nobody expects it for a demo and it'll eat your week.
- **Hindi-language PDFs** in the data set (a few notifications are in Hindi) — fine to keep, but don't try to build multilingual handling now; descope.
- Don't expand the corpus or add more PDFs — 38 is plenty; polish what's there.

---

## 7. Resume Bullet Preview (primary: Data Scientist / ML)
> *Built and deployed a Retrieval-Augmented Generation (RAG) legal assistant over **[N≈38]** Indian legal documents using LangChain, `bge-small` embeddings, and a FAISS vector store, serving grounded, source-cited answers via a Streamlit app at a public URL with **[X]s** median query latency and **[Y]%** retrieval hit-rate on a hand-built eval set.*

**Metrics to instrument while building:** `N` = doc/chunk count (log it), `X` = end-to-end query latency (time the retrieve+invoke), `Y` = retrieval hit-rate (from the Section-5 eval harness, if you do it).

---

## 8. Total Effort Estimate
- MUST-DO (tasks 1–9): ~8–10 focused hours.
- Deploy + smoke test (10–11): ~2–3 hours (budget extra for the Python 3.14→3.11 wheel issue).
- **Realistic total to CV-ready: ~12–16 focused hours** (comfortably inside your 1-week window, leaving room for 1–2 NICE-TO-HAVEs).

**Worth finishing? Yes.** The hard part (a real RAG pipeline over real data) is already built — you're debugging and shipping, not starting over. A *deployed, working* legal RAG assistant with citations is a strong, differentiated GenAI portfolio piece for DS/ML and SDE roles. The remaining work is concrete and bounded.
