"""
pipeline.py - Legal Corpus Extraction and Chunking Pipeline CLI
Part of the Verified Legal Research Assistant Corpus Pipeline.

Executes the end-to-end workflow:
PDF/TXT Input -> Text Extraction & Noise Cleaning -> Section Chunking & Metadata -> JSON Output
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Optional

# Ensure local data directory is on python import path
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from extract import extract_document
from chunk import create_chunks_from_pages, save_chunks_to_json


def run_pipeline(
    input_file: str,
    output_file: str,
    act_name: Optional[str] = "MOCK_ACT",
    source: Optional[str] = "synthetic test data",
    max_chunk_chars: int = 2000
) -> str:
    """
    Runs the complete extraction and chunking pipeline.
    """
    input_path = Path(input_file)
    output_path = Path(output_file)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file does not exist: {input_file}")

    print(f"[1/4] Extracting and cleaning text from: {input_path}")
    pages_data = extract_document(str(input_path))
    if not pages_data:
        raise ValueError(f"No valid text could be extracted from: {input_file}")
    print(f"      -> Extracted {len(pages_data)} page(s).")

    print(f"[2/4] Parsing legal sections and constructing metadata chunks...")
    chunks = create_chunks_from_pages(
        pages_data=pages_data,
        act_name=act_name,
        source=source,
        max_chunk_chars=max_chunk_chars
    )
    print(f"      -> Generated {len(chunks)} chunk(s).")

    print(f"[3/4] Validating chunk invariants...")
    for idx, chunk in enumerate(chunks):
        if not chunk.get("id"):
            raise ValueError(f"Chunk at index {idx} missing 'id'.")
        if not chunk.get("text") or not chunk["text"].strip():
            raise ValueError(f"Chunk {chunk.get('id')} has empty text.")
        # Ensure mandatory keys exist
        for key in ["id", "act", "section", "text", "page", "source"]:
            if key not in chunk:
                raise KeyError(f"Chunk {chunk.get('id')} missing key '{key}'.")

    print(f"[4/4] Saving structured chunks to: {output_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    save_chunks_to_json(chunks, str(output_path))
    print(f"      -> Successfully saved to {output_path}\n")

    return str(output_path)


def main():
    parser = argparse.ArgumentParser(
        description="Verified Legal Research Assistant - Legal Corpus Processing Pipeline"
    )
    parser.add_argument(
        "--input", "-i",
        default="data/raw/synthetic_mock_act.pdf",
        help="Path to input PDF or TXT file (default: data/raw/synthetic_mock_act.pdf)"
    )
    parser.add_argument(
        "--output", "-o",
        default="data/processed/legal_chunks.json",
        help="Path for output JSON file (default: data/processed/legal_chunks.json)"
    )
    parser.add_argument(
        "--act", "-a",
        default="MOCK_ACT",
        help="Canonical Act name (default: MOCK_ACT)"
    )
    parser.add_argument(
        "--source", "-s",
        default="synthetic test data",
        help="Source attribution (default: synthetic test data)"
    )
    parser.add_argument(
        "--max-chars", "-m",
        type=int,
        default=2000,
        help="Maximum characters per chunk before splitting long sections (default: 2000)"
    )

    args = parser.parse_args()

    # Fallback to TXT if PDF not found
    input_file = args.input
    if not Path(input_file).exists() and input_file.endswith(".pdf"):
        txt_alt = input_file.replace(".pdf", ".txt")
        if Path(txt_alt).exists():
            print(f"Note: {input_file} not found, falling back to {txt_alt}")
            input_file = txt_alt

    try:
        run_pipeline(
            input_file=input_file,
            output_file=args.output,
            act_name=args.act,
            source=args.source,
            max_chunk_chars=args.max_chars
        )
    except Exception as e:
        print(f"Pipeline error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
