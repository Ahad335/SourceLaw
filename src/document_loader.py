# Loads PDFs from the data folder and splits them into searchable chunks.
import os

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import CHUNK_OVERLAP, CHUNK_SIZE, DATA_PATH


def load_all_documents(data_path=DATA_PATH):
    """Walk the data folder and load every PDF page as a Document."""
    documents = []

    for root, _dirs, files in os.walk(data_path):
        for file in files:
            if not file.lower().endswith(".pdf"):
                continue

            file_path = os.path.join(root, file)
            try:
                docs = PyPDFLoader(file_path).load()
            except Exception as exc:  # a single corrupt PDF shouldn't kill the build
                print(f"  ! skipped {file}: {exc}")
                continue

            # Category = the sub-folder the PDF lives in, used for filtering/UI.
            category = os.path.basename(root) if root != data_path else "general"
            for doc in docs:
                doc.metadata["source"] = file
                doc.metadata["category"] = category
                doc.metadata["page"] = doc.metadata.get("page", 0)

            documents.extend(docs)

    return documents


def split_documents(documents):
    """Split loaded pages into overlapping chunks for retrieval."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", " "],
    )
    return text_splitter.split_documents(documents)
