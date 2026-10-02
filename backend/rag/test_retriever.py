"""
test_retriever.py - Tests for Legal RAG Retrieval System
Part of the Verified Legal Research Assistant RAG Pipeline.

Verifies:
1. Corpus loads successfully from data/processed/legal_chunks.json.
2. FAISS index and metadata files are cleanly built.
3. search(query) returns non-empty result list.
4. Results strictly adhere to schema: id, act, section, text, page, source, score.
5. Retrieved metadata strictly matches corpus contents without alteration.
6. Out-of-domain and unrelated queries return gracefully without crashing.
7. top_k parameter bounds result count correctly.
"""

import os
import sys
import json
import unittest
import tempfile
from pathlib import Path

# Ensure rag and project root are in sys.path
rag_dir = Path(__file__).resolve().parent
project_root = rag_dir.parent
if str(rag_dir) not in sys.path:
    sys.path.insert(0, str(rag_dir))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from build_index import load_corpus, build_faiss_index, DEFAULT_CORPUS_PATH
from retriever import LegalRetriever, search


class LegalRetrieverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus_file = project_root / DEFAULT_CORPUS_PATH
        if not cls.corpus_file.exists():
            raise FileNotFoundError(
                f"Missing corpus file: {cls.corpus_file}. Run data pipeline first."
            )

        # Build index in a temporary directory for test isolation
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.index_dir = Path(cls.temp_dir.name)
        build_faiss_index(
            corpus_path=cls.corpus_file,
            index_dir=cls.index_dir,
            model_name="all-MiniLM-L6-v2",
            show_progress=False
        )
        cls.retriever = LegalRetriever(index_dir=cls.index_dir, corpus_path=cls.corpus_file)

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def test_01_corpus_loads_successfully(self):
        """Proves data/processed/legal_chunks.json can be loaded and validated."""
        chunks = load_corpus(self.corpus_file)
        self.assertIsInstance(chunks, list)
        self.assertGreater(len(chunks), 0)
        first = chunks[0]
        self.assertIn("id", first)
        self.assertIn("text", first)

    def test_02_faiss_index_built(self):
        """Proves FAISS index and metadata files exist on disk."""
        faiss_file = self.index_dir / "legal_index.faiss"
        meta_file = self.index_dir / "metadata.json"
        info_file = self.index_dir / "index_info.json"

        self.assertTrue(faiss_file.is_file(), "FAISS index file was not created.")
        self.assertTrue(meta_file.is_file(), "Metadata JSON file was not created.")
        self.assertTrue(info_file.is_file(), "Index info JSON file was not created.")

    def test_03_search_returns_results(self):
        """Proves search(query) retrieves evidence chunks."""
        results = self.retriever.search("verification requirement evidence", top_k=2)
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)

    def test_04_results_schema_conformance(self):
        """Proves returned results strictly conform to required metadata fields + score."""
        results = self.retriever.search("What does Section 1 say about short title?", top_k=2)
        self.assertGreater(len(results), 0)

        required_keys = {"id", "act", "section", "text", "page", "source", "score"}
        for item in results:
            self.assertEqual(set(item.keys()), required_keys)
            self.assertIsInstance(item["id"], str)
            self.assertIsInstance(item["text"], str)
            self.assertGreater(len(item["text"].strip()), 0)
            self.assertIsInstance(item["score"], float)

    def test_05_metadata_matches_corpus(self):
        """Proves retrieved metadata exactly matches the corresponding entry in the original corpus."""
        with open(self.corpus_file, "r", encoding="utf-8") as f:
            corpus_lookup = {c["id"]: c for c in json.load(f)}

        results = self.retriever.search("penalty for fabricated law", top_k=3)
        for item in results:
            chunk_id = item["id"]
            self.assertIn(chunk_id, corpus_lookup)
            original = corpus_lookup[chunk_id]

            self.assertEqual(item["act"], original.get("act"))
            self.assertEqual(item["section"], original.get("section"))
            self.assertEqual(item["text"], original.get("text"))
            self.assertEqual(item["page"], original.get("page"))
            self.assertEqual(item["source"], original.get("source"))

    def test_06_unrelated_query_does_not_crash(self):
        """Proves completely nonsensical queries return gracefully without crashing."""
        gibberish = "quantum astronaut baking blueberry pancakes in zero gravity"
        results = self.retriever.search(gibberish, top_k=3)
        self.assertIsInstance(results, list)
        self.assertLessEqual(len(results), 3)

    def test_07_top_k_parameter(self):
        """Proves top_k bounds the returned results correctly."""
        results_1 = self.retriever.search("definition of mock document", top_k=1)
        results_2 = self.retriever.search("definition of mock document", top_k=2)
        self.assertEqual(len(results_1), 1)
        self.assertEqual(len(results_2), 2)


if __name__ == "__main__":
    unittest.main()
