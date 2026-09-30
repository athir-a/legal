from pathlib import Path
import json

import faiss
import numpy as np
from fastembed import TextEmbedding

from build_index import build_faiss_index


INDEX_DIR = Path("rag/index")
INDEX_PATH = INDEX_DIR / "legal_index.faiss"
METADATA_PATH = INDEX_DIR / "metadata.json"

MODEL_NAME = "BAAI/bge-small-en-v1.5"


class LegalRetriever:
    def __init__(self):
        self.index = None
        self.metadata = None
        self.model = None

    def _ensure_initialized(self):
        if self.index is not None:
            return

        # Build index automatically if it doesn't exist
        if not INDEX_PATH.exists() or not METADATA_PATH.exists():
            print("FAISS index not found. Building index...")
            build_faiss_index()

        print("Loading FAISS index...")
        self.index = faiss.read_index(str(INDEX_PATH))

        print("Loading metadata...")
        with METADATA_PATH.open("r", encoding="utf-8") as f:
            self.metadata = json.load(f)

        print("Loading embedding model...")
        self.model = TextEmbedding(model_name=MODEL_NAME)

    def search(self, query: str, top_k: int = 3):
        self._ensure_initialized()

        # Create query embedding
        query_embedding = np.array(
            list(self.model.embed([query])),
            dtype=np.float32,
        )

        # Normalize for cosine similarity
        faiss.normalize_L2(query_embedding)

        # Search FAISS
        scores, indices = self.index.search(query_embedding, top_k)

        results = []

        for score, index in zip(scores[0], indices[0]):
            if index == -1:
                continue

            item = self.metadata[index].copy()

            item["score"] = float(score)

            results.append(item)

        return results


# Convenient module-level search function
_retriever = None


def search(query: str, top_k: int = 3):
    global _retriever

    if _retriever is None:
        _retriever = LegalRetriever()

    return _retriever.search(query, top_k)