"""
chunk.py - Legal Document Chunking Module
Part of the Verified Legal Research Assistant Corpus Pipeline.

Splits extracted legal document pages into structured, citation-ready legal chunks.
Preserves exact extracted text without paraphrasing or hallucinating metadata.
"""

import re
import json
from typing import List, Dict, Any, Optional


# Pattern to identify legal section headings:
# Matches forms like:
# "Section 1.", "Section 123A.—", "Sec. 45:", "SECTION 12."
# "1. Short title...", "123. Definitions.—"
SECTION_HEADING_REGEX = re.compile(
    r'^(?:(?:Section|Sec\.|SECTION)\s+(\d+[A-Z]?)[.:\s\-—]|(\d+[A-Z]?)\.\s+([A-Z][\w\s,()\'\"—–-]{2,}[—–\.-]))',
    re.IGNORECASE
)


def identify_section_header(line: str) -> Optional[str]:
    """
    Checks if a given line is a legal section header.
    Returns the extracted section number (e.g. '1', '123', '45A') or None.
    Does not guess or invent section numbers.
    """
    line_clean = line.strip()
    match = SECTION_HEADING_REGEX.match(line_clean)
    if match:
        # Group 1 is from 'Section \d+'
        if match.group(1):
            return match.group(1).strip()
        # Group 2 is from '\d+\. Heading'
        if match.group(2):
            return match.group(2).strip()
    return None


def create_chunks_from_pages(
    pages_data: List[Dict[str, Any]],
    act_name: Optional[str] = None,
    source: Optional[str] = None,
    max_chunk_chars: int = 2000
) -> List[Dict[str, Any]]:
    """
    Parses extracted pages into structured legal chunks.

    Args:
        pages_data: List of dicts with 'page' and 'text'.
        act_name: Canonical name of the Act (e.g. 'BNS', 'MOCK_ACT') or None.
        source: Citation source (e.g. 'India Code', 'synthetic test data') or None.
        max_chunk_chars: Maximum character length before splitting long sections.

    Returns:
        List of structured chunk dictionaries.
    """
    # Step 1: Flatten lines with page tracking
    tokenized_lines = []
    for page_entry in pages_data:
        page_num = page_entry.get("page")
        raw_text = page_entry.get("text", "")
        for line in raw_text.split("\n"):
            tokenized_lines.append({
                "page": page_num,
                "text": line
            })

    # Step 2: Group lines into section units
    sections = []
    current_section_num: Optional[str] = None
    current_section_page: Optional[int] = None
    current_section_lines: List[str] = []

    for entry in tokenized_lines:
        line = entry["text"]
        page = entry["page"]
        stripped = line.strip()

        if not stripped:
            if current_section_lines:
                current_section_lines.append("")
            continue

        detected_sec = identify_section_header(stripped)

        if detected_sec is not None:
            # If we already have accumulated section lines, flush previous section
            if current_section_lines:
                sec_text = "\n".join(current_section_lines).strip()
                if sec_text:
                    sections.append({
                        "section": current_section_num,
                        "page": current_section_page,
                        "text": sec_text
                    })
            # Start new section
            current_section_num = detected_sec
            current_section_page = page
            current_section_lines = [stripped]
        else:
            if not current_section_lines:
                # Content before the first detected section (e.g. Preamble/Title)
                current_section_page = page
            current_section_lines.append(stripped)

    # Flush last remaining section
    if current_section_lines:
        sec_text = "\n".join(current_section_lines).strip()
        if sec_text:
            sections.append({
                "section": current_section_num,
                "page": current_section_page,
                "text": sec_text
            })

    # Step 3: Produce finalized chunks with metadata
    chunks = []
    act_slug = act_name.lower().replace(" ", "_") if act_name else "doc"

    for sec_idx, sec in enumerate(sections, start=1):
        sec_num = sec["section"]
        sec_page = sec["page"]
        full_text = sec["text"]

        # If a single section exceeds max_chunk_chars, split on paragraph breaks
        # while keeping the same section metadata
        if len(full_text) > max_chunk_chars:
            paragraphs = [p.strip() for p in full_text.split("\n\n") if p.strip()]
            sub_chunks = []
            current_sub = []
            current_len = 0

            for p in paragraphs:
                if current_len + len(p) > max_chunk_chars and current_sub:
                    sub_chunks.append("\n\n".join(current_sub))
                    current_sub = [p]
                    current_len = len(p)
                else:
                    current_sub.append(p)
                    current_len += len(p)
            if current_sub:
                sub_chunks.append("\n\n".join(current_sub))

            for sub_idx, sub_text in enumerate(sub_chunks, start=1):
                chunk_id = (
                    f"{act_slug}_{sec_num}_{sub_idx:03d}"
                    if sec_num
                    else f"{act_slug}_part_{sec_idx:02d}_{sub_idx:03d}"
                )
                chunks.append({
                    "id": chunk_id,
                    "act": act_name,
                    "section": sec_num,
                    "text": sub_text,
                    "page": sec_page,
                    "source": source
                })
        else:
            chunk_id = (
                f"{act_slug}_{sec_num}_001"
                if sec_num
                else f"{act_slug}_part_{sec_idx:02d}_001"
            )
            chunks.append({
                "id": chunk_id,
                "act": act_name,
                "section": sec_num,
                "text": full_text,
                "page": sec_page,
                "source": source
            })

    return chunks


def save_chunks_to_json(chunks: List[Dict[str, Any]], output_path: str) -> None:
    """
    Saves the list of chunks as a formatted JSON file.
    """
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
