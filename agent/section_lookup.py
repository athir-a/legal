import json
from pathlib import Path


CORPUS_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "processed"
    / "legal_chunks.json"
)


def lookup_section(act: str, section: str):
    """
    Deterministically look up an exact legal section
    from the verified corpus.
    """

    with CORPUS_PATH.open("r", encoding="utf-8") as f:
        corpus = json.load(f)

    for item in corpus:
        if (
            item.get("act", "").upper() == act.upper()
            and str(item.get("section")) == str(section)
        ):
            return {
                "found": True,
                "act": item["act"],
                "section": item["section"],
                "text": item["text"],
                "page": item["page"],
                "source": item["source"],
            }

    return {
        "found": False,
        "act": act,
        "section": section,
        "message": "No verified provision found in the corpus.",
    }