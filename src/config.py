# Central configuration: paths, model names, and tunable constants.
import os
from pathlib import Path

from dotenv import load_dotenv

# Load variables from the .env file (e.g. GROQ_API_KEY)
load_dotenv()

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = os.getenv("DATA_PATH", str(BASE_DIR / "data"))
INDEX_PATH = os.getenv("INDEX_PATH", str(BASE_DIR / "faiss_index"))

# Models
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
LLM_MODEL = os.getenv("LLM_MODEL", "qwen/qwen3.6-27b")

# Text splitting
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150

# Retrieval
TOP_K = 5
# FAISS returns L2 distance here: LOWER is better. Measured against this
# corpus, on-topic questions land at 0.5-0.8 and clearly off-topic ones at
# 1.1-1.3, so 1.0 sits in the gap. Chunks past it are dropped as noise.
MAX_DISTANCE = float(os.getenv("MAX_DISTANCE", "1.0"))

# LLM generation
TEMPERATURE = 0.5
MAX_NEW_TOKENS = 512

# API
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
).split(",")
