# Legal Data / Corpus Pipeline

**Verified Legal Research Assistant** – Legal Document Processing Subsystem.

---

## 1. Overview

The pipeline ingests raw legal acts (PDF or TXT), cleans extraction artifacts (soft hyphens, running headers, repeated gazette metadata, and whitespace noise), parses legal provisions into structured section units, and exports citation-ready chunks in structured JSON format for RAG ingestion.

### Non-Negotiable Corpus Invariants
- **Zero Hallucination:** Exact legal wording is strictly preserved without paraphrasing, summarizing, or generating missing sections.
- **Auditable Citation:** Every chunk tracks Act name, Section number, starting Page number, and Source attribution.
- **Null Safety:** If metadata cannot be determined deterministically (e.g. preambles without a section number), it is stored as `null`, never guessed.

---

## 2. Dataset Status

> **Current Dataset:** **SYNTHETIC TEST DATA** (`data/raw/synthetic_mock_act.pdf` & `data/raw/synthetic_mock_act.txt`).
> **Real Law Status:** **NOT REAL LAW.**
> The current files are labeled synthetic test artifacts created strictly to verify extraction, chunking, and metadata parsing without downloading unverified documents.

When real legal documents (e.g., India Code PDFs such as The Bharatiya Nyaya Sanhita, 2023) are added, place them into `data/raw/` and credit the source (e.g., `India Code / Legislative Department, Ministry of Law and Justice`).

---

## 3. Directory Structure

```
data/
├── README.md                  # Pipeline documentation
├── requirements.txt           # Dependencies (pypdf, reportlab)
├── extract.py                 # PDF/TXT extractor & noise cleaner
├── chunk.py                   # Section parser & metadata chunker
├── pipeline.py                # End-to-end CLI workflow
├── generate_mock_pdf.py       # Generates labeled synthetic PDF for testing
├── test_pipeline.py           # Verification test suite
├── raw/                       # Raw input PDFs and text files
│   ├── synthetic_mock_act.pdf
│   └── synthetic_mock_act.txt
└── processed/                 # Final structured JSON chunks
    └── legal_chunks.json
```

---

## 4. Setup & Dependencies

Install the required Python packages:

```bash
pip install -r data/requirements.txt
```

*(Or on Windows: `py -m pip install -r data/requirements.txt`)*

Dependencies:
- `pypdf`: Pure-Python PDF text extraction.
- `reportlab`: Synthetic PDF generation for testing.

---

## 5. How to Run the Pipeline

### Step 1 (Optional): Generate Synthetic Mock PDF
```bash
python data/generate_mock_pdf.py
```
*(Or `py data/generate_mock_pdf.py`)*

### Step 2: Run End-to-End Extraction & Chunking
```bash
python data/pipeline.py --input data/raw/synthetic_mock_act.pdf --output data/processed/legal_chunks.json --act MOCK_ACT --source "synthetic test data"
```
*(Or `py data/pipeline.py` with default arguments)*

### Processing Real Legal Documents (e.g. BNS 2023):
```bash
python data/pipeline.py --input data/raw/bns_2023.pdf --output data/processed/bns_chunks.json --act "BNS" --source "India Code"
```

---

## 6. Metadata Schema & Output Format

The output is saved to `data/processed/legal_chunks.json` as a JSON array of objects conforming to:

| Field | Type | Description | Example |
|---|---|---|---|
| `id` | `string` | Unique deterministic chunk identifier | `"mock_act_1_001"` |
| `act` | `string \| null` | Canonical Act name | `"MOCK_ACT"` |
| `section` | `string \| null` | Legal section number (`null` for preamble) | `"1"` |
| `text` | `string` | Verbatim extracted legal provision | `"Section 1. Short title..."` |
| `page` | `integer` | 1-indexed document page where chunk begins | `1` |
| `source` | `string \| null` | Official citation source or attribution | `"synthetic test data"` |

### Sample JSON Output

```json
[
  {
    "id": "mock_act_part_01_001",
    "act": "MOCK_ACT",
    "section": null,
    "text": "THE SYNTHETIC MOCK ACT, 2026\nAn Act for testing legal text extraction, chunking, and citation pipelines in the Verified Legal Research Assistant\nproject.",
    "page": 1,
    "source": "synthetic test data"
  },
  {
    "id": "mock_act_1_001",
    "act": "MOCK_ACT",
    "section": "1",
    "text": "Section 1. Short title, extent and commencement.—(1) This Act may be called the Synthetic Mock Act, 2026.\n(2) It extends to all testing environments of the project.\n(3) It shall come into force immediately and serves solely as mock verification data.",
    "page": 1,
    "source": "synthetic test data"
  },
  {
    "id": "mock_act_2_001",
    "act": "MOCK_ACT",
    "section": "2",
    "text": "Section 2. Definitions.—In this Act, unless the context otherwise requires,—\n(a) \"mock document\" means synthetic text generated strictly for testing;\n(b) \"pipeline\" means the verified legal text extraction and chunking workflow;\n(c) \"verifier\" means a component ensuring answers cite substantiated corpus evidence.",
    "page": 1,
    "source": "synthetic test data"
  }
]
```

---

## 7. How to Run the Tests

Execute the automated test suite:

```bash
python data/test_pipeline.py
```
*(Or `py data/test_pipeline.py`)*

The test suite verifies:
1. Multi-page PDF text extraction with page numbers.
2. Raw TXT document extraction compatibility.
3. Metadata schema invariant on every chunk.
4. Non-empty text verification.
5. Preamble null fallback without hallucinating section numbers.
6. JSON serialization and loading round-trip.
7. Noise cleaning (hyphen breaks, running headers, excessive whitespace).
