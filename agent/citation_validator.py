from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_PATH = PROJECT_ROOT / "backend"

if str(BACKEND_PATH) not in sys.path:
    sys.path.insert(0, str(BACKEND_PATH))


import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from legaldata.models import LegalDocument


def validate_citations(citations):
    """
    Validate citations against the verified MySQL legal corpus.
    """

    validated = []

    for citation in citations:
        act = citation.get("act", "")
        section = str(citation.get("section", ""))

        exists = LegalDocument.objects.filter(
            act_title__iexact=act,
            section_number=section,
        ).exists()

        validated.append({
            "act": act,
            "section": section,
            "page": citation.get("page"),
            "source": citation.get("source"),
            "valid": exists,
        })

    all_valid = (
        len(validated) > 0
        and all(item["valid"] for item in validated)
    )

    return {
        "valid": all_valid,
        "citations": validated,
    }