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


def verify_citations(citations):
    """
    Verify that every citation in an answer refers to an actual
    provision in the verified legal corpus.
    """

    verified = []

    for citation in citations:
        act = citation.get("act", "")
        section = str(citation.get("section", ""))

        document = LegalDocument.objects.filter(
            act_title__iexact=act,
            section_number=section,
        ).first()

        verified.append({
            "act": act,
            "section": section,
            "valid": document is not None,
            "source": document.source if document else None,
            "source_url": document.source_url if document else None,
        })

    all_valid = (
        len(verified) > 0
        and all(item["valid"] for item in verified)
    )

    return {
        "valid": all_valid,
        "citations": verified,
    }
