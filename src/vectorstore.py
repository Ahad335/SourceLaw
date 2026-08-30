# Builds (or loads) the FAISS vector store from document chunks + embeddings.
import os
from functools import lru_cache

from langchain_community.vectorstores import FAISS

from src.config import DATA_PATH, INDEX_PATH
from src.document_loader import load_all_documents, split_documents
from src.embeddings import get_embeddings


def build_vectorstore(data_path=DATA_PATH, index_path=INDEX_PATH):
    """Embed every PDF in data_path and persist the index to disk."""
    print(f"Loading PDFs from {data_path} ...")
    documents = load_all_documents(data_path)
    print(f"  {len(documents)} pages loaded")

    chunks = split_documents(documents)
    print(f"  {len(chunks)} chunks after splitting")

    print("Embedding chunks (first run downloads the model) ...")
    vectorstore = FAISS.from_documents(chunks, get_embeddings())

    vectorstore.save_local(index_path)
    print(f"Index saved to {index_path}")
    return vectorstore


@lru_cache(maxsize=1)
def get_vectorstore():
    """Load the persisted index, building it once if it isn't there yet."""
    if os.path.exists(os.path.join(INDEX_PATH, "index.faiss")):
        return FAISS.load_local(
            INDEX_PATH,
            get_embeddings(),
            allow_dangerous_deserialization=True,  # we generated this file ourselves
        )
    return build_vectorstore()
