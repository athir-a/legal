import json
from pathlib import Path


CORPUS_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "processed"
    / "legal_chunks.json"
)


def validate_citations(citations):
    with CORPUS_PATH.open("r", encoding="utf-8") as f:
        corpus = json.load(f)

    verified_sections = {
        (
            item.get("act", "").upper(),
            str(item.get("section"))
        ): item
        for item in corpus
        if item.get("section") is not None
    }

    validated = []

    for citation in citations:
        act = citation.get("act", "")
        section = str(citation.get("section", ""))

        key = (act.upper(), section)
        source = verified_sections.get(key)

        validated.append({
            "act": act,
            "section": section,
            "page": citation.get("page"),
            "source": citation.get("source"),
            "valid": source is not None,
        })

    all_valid = (
        len(validated) > 0
        and all(item["valid"] for item in validated)
    )

    return {
        "valid": all_valid,
        "citations": validated,
    }