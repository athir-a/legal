from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAG_PATH = PROJECT_ROOT / "rag"
BACKEND_PATH = PROJECT_ROOT / "backend"


if str(RAG_PATH) not in sys.path:
    sys.path.insert(0, str(RAG_PATH))

if str(BACKEND_PATH) not in sys.path:
    sys.path.insert(0, str(BACKEND_PATH))


from retriever import search


# ---------------------------------------------------------
# Django setup
# ---------------------------------------------------------

import os
import django

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings"
)

django.setup()


from legaldata.models import LegalChunk


# ---------------------------------------------------------
# Legal search
# ---------------------------------------------------------

def search_legal_documents(query: str, top_k: int = 3):

    results = search(
        query,
        top_k=top_k
    )

    enriched_results = []

    for result in results:

        chunk_id = result.get("chunk_id")

        if chunk_id is None:
            continue

        chunk = (
            LegalChunk.objects
            .select_related("document")
            .filter(id=chunk_id)
            .first()
        )

        if chunk is None:
            continue

        enriched_results.append({
            "chunk_id": chunk.id,
            "document_id": chunk.document.id,

            "section_number":
                chunk.document.section_number,

            "section_title":
                chunk.document.section_title,

            "act_title":
                chunk.document.act_title,

            "text":
                chunk.text,

            "score":
                result.get("score", 0.0),

            "source":
                chunk.document.source,

            "source_url":
                chunk.document.source_url,
        })

    return {
        "query": query,
        "results": enriched_results,
    }