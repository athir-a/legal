# Legal Evidence Retrieval Subsystem (RAG)

**Verified Legal Research Assistant** – Semantic Retrieval Layer.

---

## 1. Architecture Overview

The retrieval layer sits between the processed corpus and the verification agent. Its sole purpose is to retrieve substantiated legal evidence chunks matching a query, preserving original verbatim text and citations without alteration.

```
                    ┌────────────────────────────────────────┐
                    │ data/processed/legal_chunks.json       │
                    └──────────────────┬─────────────────────┘
                                       │
                                       ▼ (rag/build_index.py)
                    ┌──────────────────┴─────────────────────┐
                    │ SentenceTransformer (all-MiniLM-L6-v2)  │
                    │ Normalized Embeddings (384-d float32)  │
                    └──────────────────┬─────────────────────┘
                                       │
                        ┌──────────────┴──────────────┐
                        ▼                             ▼
              ┌─────────────────────┐       ┌───────────────────┐
              │  IndexFlatIP        │       │ Aligned Metadata  │
              │  (Cosine FAISS)     │       │ (metadata.json)   │
              │  legal_index.faiss  │       │                   │
              └─────────┬───────────┘       └─────────┬─────────┘
                        │                             │
                        └──────────────┬──────────────┘
                                       │
                                       ▼ (rag/retriever.py)
                    ┌──────────────────┴─────────────────────┐
                    │ search(query, top_k=3)                 │
                    │ -> List of Verified Evidence Chunks    │
                    └────────────────────────────────────────┘
```

### Core Design Principles
- **Evidence Only:** Retrieves matching legal passages; does **not** generate answers, invent citations, or paraphrase text.
- **Auditable Provenance:** Every retrieved chunk includes `id`, `act`, `section`, `page`, `source`, and similarity `score`.
- **Reproducible:** The index can be reconstructed deterministically at any time from the source JSON corpus.

---

## 2. Embedding Model Choice

- **Model:** `sentence-transformers/all-MiniLM-L6-v2`
- **Embedding Dimension:** 384
- **Distance Metric:** Cosine similarity via Inner Product (`IndexFlatIP`) with L2-normalized embeddings.

### Why this model was chosen:
1. **Lightweight & Fast:** Model size is ~80 MB; runs locally on CPU with millisecond latency, ideal for hackathon iteration.
2. **Zero External API Cost:** Runs completely offline without OpenAI/Anthropic/Google API keys or rate limits.
3. **High Retrieval Quality:** Proven benchmark performance for passage retrieval and semantic text matching.

---

## 3. Setup & Dependencies

Install dependencies:

```bash
pip install -r rag/requirements.txt
```

*(On Windows: `py -m pip install -r rag/requirements.txt`)*

Packages:
- `sentence-transformers`: Local text embedding generation.
- `faiss-cpu`: Dense vector similarity indexing and search.
- `numpy`: Numerical vector processing.

---

## 4. How to Build the FAISS Index

To build or refresh the vector index from `data/processed/legal_chunks.json`:

```bash
python rag/build_index.py
```
*(Or `py rag/build_index.py`)*

Optional flags:
```bash
python rag/build_index.py --corpus data/processed/legal_chunks.json --output-dir rag/index --model all-MiniLM-L6-v2
```

Artifacts generated inside `rag/index/`:
- `legal_index.faiss`: Binary FAISS vector index.
- `metadata.json`: Aligned chunk metadata for instant lookup.
- `index_info.json`: Build metadata, dimensions, and model signature.

---

## 5. How to Call `search()` (Teammate Integration)

Any teammate (Agent, API, or CLI) can import and execute semantic retrieval:

```python
from rag.retriever import search

# Query for relevant evidence
results = search("What does section 3 say?", top_k=3)

for chunk in results:
    print(f"[{chunk['act']} Sec {chunk['section']}] (Score: {chunk['score']})")
    print(f"Text: {chunk['text']}")
    print(f"Source: {chunk['source']} (Page {chunk['page']})\n")
```

*(Note: If the FAISS index has not been built yet, `search()` will automatically generate it on first invocation).*

---

## 6. Output Schema

The `search()` function returns a list of dictionaries matching this schema:

```json
[
  {
    "id": "mock_act_3_001",
    "act": "MOCK_ACT",
    "section": "3",
    "text": "Section 3. Evidence verification requirement.—(1) A legal research assistant shall deliver information only when supported by verified legal evidence in the corpus.\n(2) If a relevant provision cannot be substantiated by verified text, the system must not invent an answer.",
    "page": 2,
    "source": "synthetic test data",
    "score": 0.8124
  }
]
```

| Field | Type | Description |
|---|---|---|
| `id` | `string` | Unique chunk ID from the corpus pipeline |
| `act` | `string \| null` | Canonical Act name |
| `section` | `string \| null` | Legal section number |
| `text` | `string` | Exact verbatim legal passage from corpus |
| `page` | `integer \| null` | Page number in source document |
| `source` | `string \| null` | Citation provenance (e.g. `"India Code"`) |
| `score` | `float` | Cosine similarity score between query and chunk |

---

## 7. How to Run the Tests

Execute the automated test suite:

```bash
python rag/test_retriever.py
```
*(Or `py rag/test_retriever.py`)*

The test suite validates:
1. Corpus loads and validates against schema.
2. FAISS index and metadata files are created properly.
3. `search(query)` returns structured evidence.
4. All required metadata fields (`id`, `act`, `section`, `text`, `page`, `source`, `score`) are present.
5. Returned metadata strictly matches the source corpus.
6. Nonsensical or out-of-domain queries do not crash the system.
7. Result limits adhere to the `top_k` parameter.

---

## 8. Limitations & Status

1. **Synthetic Corpus:** The current active dataset is synthetic test data (`MOCK_ACT`). It is designed for architecture integration testing and **is not real law**. Passing search tests does not imply legal accuracy of real statutes until real statutes (e.g., BNS 2023) are ingested into `data/`.
2. **Lexical Matching:** Semantic embeddings excel at conceptual meaning but may occasionally rank semantic synonyms above exact section number references (e.g., "Section 123"). A hybrid retriever (BM25 + FAISS) can be added in future iterations if strict section keyword prioritization is needed.
