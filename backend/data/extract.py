"""
extract.py - Legal PDF Text Extraction and Cleaning Module
Part of the Verified Legal Research Assistant Corpus Pipeline.

Extracts text from PDF or raw text files page-by-page, recording 1-indexed page
numbers and applying deterministic cleaning to eliminate extraction noise while
strictly preserving original legal wording.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    from pypdf import PdfReader
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False


def clean_page_text(raw_text: str) -> str:
    """
    Cleans extraction artifacts without altering legal wording:
    - Normalizes line endings (CRLF to LF).
    - Removes soft-hyphen line breaks (e.g., 'juris-\\ndiction' -> 'jurisdiction').
    - Removes standalone page number lines and common gazette header/footer noise.
    - Normalizes multiple horizontal spaces while preserving paragraph breaks.
    """
    if not raw_text:
        return ""

    # Normalize carriage returns
    text = raw_text.replace("\r\n", "\n").replace("\r", "\n")

    # Normalize unicode replacement character if font mapping dropped em-dash
    text = text.replace("\ufffd", "—")

    # Fix broken hyphenated words across line breaks (e.g. 'com- \nmencement' -> 'commencement')
    text = re.sub(r'([a-zA-Z]+)-\s*\n\s*([a-zA-Z]+)', r'\1\2', text)

    lines = text.split("\n")
    cleaned_lines = []

    for line in lines:
        stripped = line.strip()

        # Filter out standalone page number lines (e.g. '42', 'Page 3 of 10')
        if re.match(r'^(page\s+)?\d+(\s+of\s+\d+)?$', stripped, re.IGNORECASE):
            continue

        # Filter out common Indian gazette / publication header repetitions
        if re.match(r'^\[?\s*part\s+[ivxcdlm]+\s*[-—–]\s*sec(tion)?\.?\s*\d+\s*\]?$', stripped, re.IGNORECASE):
            continue
        if re.match(r'^the\s+gazette\s+of\s+india(\s+extraordinary)?$', stripped, re.IGNORECASE):
            continue
        if re.search(r'\((?:continued|contd\.?)\)', stripped, re.IGNORECASE):
            continue
        if re.match(r'^\[?\s*synthetic\s+test\s+corpus.*\]?$', stripped, re.IGNORECASE):
            continue

        # Replace excessive horizontal tabs/spaces with a single space
        normalized_line = re.sub(r'[ \t]+', ' ', stripped)
        cleaned_lines.append(normalized_line)

    # Reassemble and collapse 3+ consecutive newlines into 2
    cleaned_text = "\n".join(cleaned_lines)
    cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
    return cleaned_text.strip()


def extract_from_pdf(pdf_path: str) -> List[Dict[str, Any]]:
    """
    Extracts text page-by-page from a PDF file.
    Returns a list of dicts: [{'page': 1, 'text': '...'}, ...]
    """
    if not PYPDF_AVAILABLE:
        raise ImportError("pypdf is required for PDF extraction. Run `pip install pypdf`.")

    path = Path(pdf_path)
    if not path.is_file():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    reader = PdfReader(str(path))
    pages_data = []

    for idx, page in enumerate(reader.pages, start=1):
        raw_text = page.extract_text() or ""
        cleaned = clean_page_text(raw_text)
        if cleaned:
            pages_data.append({
                "page": idx,
                "text": cleaned
            })

    return pages_data


def extract_from_txt(txt_path: str) -> List[Dict[str, Any]]:
    """
    Extracts text from a plain text file.
    Page number is set to 1 or inferred if explicit form-feed/page markers exist.
    """
    path = Path(txt_path)
    if not path.is_file():
        raise FileNotFoundError(f"Text file not found: {txt_path}")

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    # If form feed characters exist, split into pages
    raw_pages = content.split("\x0c") if "\x0c" in content else [content]
    pages_data = []

    for idx, raw_page in enumerate(raw_pages, start=1):
        cleaned = clean_page_text(raw_page)
        if cleaned:
            pages_data.append({
                "page": idx,
                "text": cleaned
            })

    return pages_data


def extract_document(file_path: str) -> List[Dict[str, Any]]:
    """
    Universal extractor dispatching to PDF or TXT based on file extension.
    """
    ext = Path(file_path).suffix.lower()
    if ext == ".pdf":
        return extract_from_pdf(file_path)
    elif ext in [".txt", ".text"]:
        return extract_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}. Supported formats are .pdf, .txt")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python extract.py <path_to_pdf_or_txt>")
        sys.exit(1)

    target_file = sys.argv[1]
    results = extract_document(target_file)
    print(f"Extracted {len(results)} pages from {target_file}.")
    for page in results[:2]:
        print(f"\n--- Page {page['page']} (sample first 200 chars) ---")
        print(page['text'][:200])
