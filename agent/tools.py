from pathlib import Path
import sys

# Allow the agent to access the RAG module
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAG_PATH = PROJECT_ROOT / "rag"

if str(RAG_PATH) not in sys.path:
    sys.path.insert(0, str(RAG_PATH))

from retriever import search


def search_legal_documents(query: str, top_k: int = 3):
    """
    Search the verified legal corpus using semantic retrieval.
    """

    results = search(query, top_k=top_k)

    return {
        "query": query,
        "results": results,
    }