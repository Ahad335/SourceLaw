# Builds the embedding model used to turn text into vectors.
from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings

from src.config import EMBEDDING_MODEL

# bge-* models are trained with an instruction prefix on the QUERY side only.
# Without it, retrieval quality drops noticeably. Documents are embedded as-is.
QUERY_INSTRUCTION = "Represent this sentence for searching relevant passages: "


@lru_cache(maxsize=1)
def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        encode_kwargs={"normalize_embeddings": True},
        # query_encode_kwargs REPLACES encode_kwargs for queries, so repeat
        # normalize_embeddings here or query vectors come back unnormalised.
        query_encode_kwargs={
            "prompt": QUERY_INSTRUCTION,
            "normalize_embeddings": True,
        },
    )
