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

    is_consumer_rights_query = re.search(
        r"\bconsumer\s+rights\b|\brights\s+of\s+consumers?\b",
        query_lower,
    )

    if is_consumer_rights_query:
        patterns.extend([
            r'\(9\)\s*"consumer rights"\s+includes',
            r'"consumer rights"\s+includes',
        ])

    elif "consumer" in query_lower:
        patterns.extend([
            r'\(7\)\s*"consumer"\s+means',
            r'"consumer"\s+means',
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

        retrieval_score = float(result.get("score", 0.0))
        if retrieval_score < 0.10:
            continue

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

            combined_text = _join_overlapping_chunks(nearby_chunks)

        focused_text = extract_relevant_text(
            combined_text,
            query,
            max_chars=7000
        )
        focused_text = _clean_section_text(
            focused_text,
            section_number,
        )

        if not focused_text:
            continue

        seen_sections.add(section_number)

        evidence.append({
            "act": result.get("act_title"),
            "section": section_number,
            "section_title": _clean_section_title(
                result.get("section_title"),
                section_number,
            ),
            "text": focused_text,
            "source": result.get(
                "source",
                "India Code"
            ),
            "source_url": result.get("source_url"),
            "retrieval_score": retrieval_score,
        })

        if len(evidence) >= max_sections:
            break

    return evidence


def _clean_section_title(title, section_number):
    """Remove section labels and any following section heading from a title."""
    if not title:
        return title

    clean_title = re.sub(
        rf"^\s*Section\s+{re.escape(str(section_number))}\.\s*",
        "",
        str(title).strip(),
        count=1,
        flags=re.IGNORECASE,
    )
    clean_title = re.split(
        r"\s+\d{1,3}\.\s+(?=[A-Z])",
        clean_title,
        maxsplit=1,
    )[0]
    return clean_title.strip()


def _clean_section_text(text, section_number):
    """Remove the leading section-heading line from the evidence body."""
    if not text:
        return text

    return re.sub(
        rf"^\s*Section\s+{re.escape(str(section_number))}\.\s*[^\r\n]*(?:\r?\n)+",
        "",
        text.strip(),
        count=1,
        flags=re.IGNORECASE,
    ).strip()


def _join_overlapping_chunks(chunks, max_overlap=150):
    combined_text = ""
    previous_text = ""

    for chunk in chunks:
        text = chunk.text.strip()
        if not text:
            continue

        overlap_size = 0
        if previous_text:
            max_size = min(max_overlap, len(previous_text), len(text))
            overlap_size = next(
                (
                    size
                    for size in range(max_size, 0, -1)
                    if previous_text.endswith(text[:size])
                ),
                0,
            )

        if combined_text and not overlap_size:
            combined_text += "\n\n"
        combined_text += text[overlap_size:]
        previous_text = text

    return combined_text