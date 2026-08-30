# Indian Legal AI Assistant - FastAPI backend for the React frontend.
import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.config import CORS_ORIGINS
from src.rag import answer_question
from src.vectorstore import get_vectorstore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("legal-api")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Load (or build) the FAISS index once at boot, not on the first question."""
    started = time.time()
    get_vectorstore()
    logger.info("Vector store ready in %.1fs", time.time() - started)
    yield


app = FastAPI(title="Indian Legal AI Assistant", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Turn(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    history: list[Turn] = []


class Source(BaseModel):
    source: str
    page: int
    category: str
    score: float
    excerpt: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]
    latency_ms: int


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    started = time.time()
    try:
        result = answer_question(
            request.question,
            [turn.model_dump() for turn in request.history],
        )
    except Exception as exc:
        logger.exception("chat failed")
        raise HTTPException(
            status_code=502,
            detail=f"The language model call failed: {exc}",
        ) from exc

    return ChatResponse(
        answer=result["answer"],
        sources=result["sources"],
        latency_ms=int((time.time() - started) * 1000),
    )
