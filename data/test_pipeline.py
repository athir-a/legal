"""
test_pipeline.py - Verification Tests for Legal Corpus Pipeline
Part of the Verified Legal Research Assistant Corpus Pipeline.

Tests:
1. PDF & Text document ingestion.
2. Required metadata schema integrity on every chunk (id, act, section, text, page, source).
3. Zero empty or whitespace-only text invariant.
4. Deterministic JSON output round-tripping.
5. Proper fallback to null for non-section text (preamble) without hallucination.
6. Noise cleaning (hyphen breaks, running headers, CRLF).
"""

import json
import os
import sys
import unittest
import tempfile
from pathlib import Path

# Ensure data directory is on python import path
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from extract import clean_page_text, extract_document
from chunk import create_chunks_from_pages, save_chunks_to_json, identify_section_header
from pipeline import run_pipeline
from generate_mock_pdf import generate_synthetic_mock_pdf


class LegalCorpusPipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw_dir = current_dir / "raw"
        cls.processed_dir = current_dir / "processed"
        cls.pdf_path = cls.raw_dir / "synthetic_mock_act.pdf"
        cls.txt_path = cls.raw_dir / "synthetic_mock_act.txt"

        # Ensure synthetic PDF exists for tests
        if not cls.pdf_path.exists():
            generate_synthetic_mock_pdf(str(cls.pdf_path))

    def test_01_pdf_extraction(self):
        """Verifies PDF extraction retrieves pages and tracks 1-indexed page numbers."""
        pages = extract_document(str(self.pdf_path))
        self.assertGreaterEqual(len(pages), 2, "Expected at least 2 pages extracted from synthetic PDF.")
        self.assertEqual(pages[0]["page"], 1)
        self.assertEqual(pages[1]["page"], 2)
        self.assertIn("Section 1", pages[0]["text"])
        self.assertIn("Section 3", pages[1]["text"])

    def test_02_text_extraction(self):
        """Verifies TXT extraction functions identically for raw text inputs."""
        pages = extract_document(str(self.txt_path))
        self.assertEqual(len(pages), 1)
        self.assertEqual(pages[0]["page"], 1)
        self.assertIn("Section 1", pages[0]["text"])

    def test_03_metadata_schema_invariants(self):
        """Verifies every chunk contains all 6 required metadata fields."""
        pages = extract_document(str(self.pdf_path))
        chunks = create_chunks_from_pages(
            pages_data=pages,
            act_name="MOCK_ACT",
            source="synthetic test data"
        )
        self.assertGreater(len(chunks), 0)

        required_keys = {"id", "act", "section", "text", "page", "source"}
        for chunk in chunks:
            self.assertTrue(required_keys.issubset(chunk.keys()), f"Chunk {chunk} missing required keys.")
            self.assertEqual(chunk["act"], "MOCK_ACT")
            self.assertEqual(chunk["source"], "synthetic test data")
            self.assertIsInstance(chunk["page"], int)
            self.assertGreaterEqual(chunk["page"], 1)

    def test_04_no_empty_legal_text(self):
        """Verifies that no chunk has empty or whitespace-only text."""
        pages = extract_document(str(self.pdf_path))
        chunks = create_chunks_from_pages(pages_data=pages, act_name="MOCK_ACT")
        for chunk in chunks:
            text = chunk.get("text")
            self.assertIsNotNone(text, f"Chunk {chunk['id']} has None text.")
            self.assertIsInstance(text, str)
            self.assertTrue(len(text.strip()) > 0, f"Chunk {chunk['id']} has empty text string.")

    def test_05_preamble_and_section_identification(self):
        """Verifies sections are accurately parsed and unsectioned text falls back to null."""
        pages = extract_document(str(self.pdf_path))
        chunks = create_chunks_from_pages(pages_data=pages, act_name="MOCK_ACT")

        # First chunk should be the preamble/title with section: None (null)
        preamble_chunk = chunks[0]
        self.assertIsNone(preamble_chunk["section"], "Preamble chunk must have section=None, not invented.")

        # Following chunks must match exact section numbers
        section_nums = [c["section"] for c in chunks if c["section"] is not None]
        self.assertEqual(section_nums, ["1", "2", "3", "4"])

    def test_06_pipeline_json_roundtrip(self):
        """Verifies full CLI pipeline execution and JSON loading."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            output_file = run_pipeline(
                input_file=str(self.pdf_path),
                output_file=tmp_path,
                act_name="MOCK_ACT",
                source="synthetic test data"
            )
            self.assertTrue(os.path.exists(output_file))

            # Verify JSON can be parsed back
            with open(output_file, "r", encoding="utf-8") as f:
                loaded_chunks = json.load(f)

            self.assertIsInstance(loaded_chunks, list)
            self.assertEqual(len(loaded_chunks), 5)
            # Verify structure of first section chunk
            sec_1 = next(c for c in loaded_chunks if c["section"] == "1")
            self.assertEqual(sec_1["id"], "mock_act_1_001")
            self.assertEqual(sec_1["page"], 1)
            self.assertIn("Short title", sec_1["text"])
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_07_noise_cleaning(self):
        """Verifies cleaning of hyphenated breaks, running headers, and excess whitespace."""
        noisy_sample = (
            "THE GAZETTE OF INDIA EXTRAORDINARY\n"
            "Page 12 of 100\n"
            "This is a test of juris-\n"
            "diction and extra-\n"
            "ordinary procedure.\n"
            "[Part II—Sec. 1]\n"
        )
        cleaned = clean_page_text(noisy_sample)
        self.assertNotIn("Page 12 of 100", cleaned)
        self.assertNotIn("THE GAZETTE OF INDIA", cleaned)
        self.assertNotIn("[Part II—Sec. 1]", cleaned)
        self.assertIn("jurisdiction", cleaned)
        self.assertIn("extraordinary", cleaned)


if __name__ == "__main__":
    unittest.main()
