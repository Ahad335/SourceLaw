# One-off script: embed every PDF in data/ and save the FAISS index to disk.
# Run this once before starting the API:  python build_index.py
import time

from src.vectorstore import build_vectorstore

if __name__ == "__main__":
    started = time.time()
    build_vectorstore()
    print(f"Done in {time.time() - started:.1f}s")
