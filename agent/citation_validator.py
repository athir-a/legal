import json
from pathlib import Path


CORPUS_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "processed"
    / "legal_chunks.json"
)


def validate_citations(citations):
    """
    Verify that every cited Act + section exists
    in the verified legal corpus.
    """

    with CORPUS_PATH.open("r", encoding="utf-8") as f:
        corpus = json.load(f)

    valid_sections = {
        (
            item.get("act", "").upper(),
            str(item.get("section"))
        )
        for item in corpus
        if item.get("section") is not None
    }

    validated = []

    for citation in citations:
        act = citation.get("act", "")
        section = str(citation.get("section", ""))

        key = (act.upper(), section)

        validated.append({
            "act": act,
            "section": section,
            "valid": key in valid_sections,
        })

    all_valid = all(item["valid"] for item in validated)

    return {
        "valid": all_valid,
        "citations": validated,
    }