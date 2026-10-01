from pathlib import Path
import sys
import re

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_PATH = PROJECT_ROOT / "backend"

if str(BACKEND_PATH) not in sys.path:
    sys.path.insert(0, str(BACKEND_PATH))

import os
import django

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings"
)

django.setup()

from legaldata.models import LegalChunk, LegalDocument


def extract_relevant_text(text, query, max_chars=7000):
    """
    Extract the most relevant passage from a legal section.
    """

    text_lower = text.lower()
    query_lower = query.lower()

    patterns = []

    if "consumer" in query_lower:
        patterns.extend([
            r'\(7\)\s*"consumer"\s+means',
            r'"consumer"\s+means',
        ])

    if "consumer rights" in query_lower:
        patterns.extend([
            r'\(9\)\s*"consumer rights"\s+includes',
            r'"consumer rights"\s+includes',
        ])

    if "unfair trade practice" in query_lower:
        patterns.extend([
            r'\(47\)\s*"unfair trade practice"',
            r'"unfair trade practice"',
        ])

    start = None

    for pattern in patterns:
        match = re.search(pattern, text_lower)

        if match:
            start = match.start()
            break

    if start is not None:
        return text[start:start + max_chars].strip()

    return text[:max_chars].strip()


def build_evidence(results, query="", max_sections=5):
    """
    Build focused legal evidence.

    For definition-style questions, fetch the complete legal section
    from the database and extract the relevant definition.

    For other questions, use the retrieved chunk and nearby chunks.
    """

    evidence = []
    seen_sections = set()

    for result in results:

        chunk_id = result.get("chunk_id")
        document_id = result.get("document_id")
        section_number = str(
            result.get("section_number", "")
        )

        if not chunk_id or not document_id:
            continue

        if section_number in seen_sections:
            continue

        query_lower = query.lower()

        is_definition_query = (
            "what is" in query_lower
            or "who is" in query_lower
            or "define" in query_lower
        )

        combined_text = ""

        # ---------------------------------------------------------
        # Definition queries:
        # Fetch the complete legal section.
        # ---------------------------------------------------------

        if is_definition_query:

            document = (
                LegalDocument.objects
                .filter(
                    id=document_id,
                    section_number=section_number
                )
                .first()
            )

            if document:
                combined_text = document.text

        # ---------------------------------------------------------
        # Other queries:
        # Use retrieved chunk + nearby chunks.
        # ---------------------------------------------------------

        if not combined_text:

            retrieved_chunk = (
                LegalChunk.objects
                .filter(
                    id=chunk_id,
                    document_id=document_id
                )
                .first()
            )

            if retrieved_chunk is None:
                continue

            start_index = max(
                0,
                retrieved_chunk.chunk_index - 1
            )

            end_index = retrieved_chunk.chunk_index + 1

            nearby_chunks = list(
                LegalChunk.objects
                .filter(
                    document_id=document_id,
                    chunk_index__gte=start_index,
                    chunk_index__lte=end_index,
                )
                .order_by("chunk_index")
            )

            combined_text = "\n\n".join(
                chunk.text.strip()
                for chunk in nearby_chunks
                if chunk.text.strip()
            )

        focused_text = extract_relevant_text(
            combined_text,
            query,
            max_chars=7000
        )

        if not focused_text:
            continue

        seen_sections.add(section_number)

        evidence.append({
            "act": result.get("act_title"),
            "section": section_number,
            "section_title": result.get("section_title"),
            "text": focused_text,
            "source": result.get(
                "source",
                "India Code"
            ),
            "source_url": result.get("source_url"),
            "retrieval_score": result.get(
                "score",
                0.0
            ),
        })

        if len(evidence) >= max_sections:
            break

    return evidence