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


def lookup_section(act: str, section: str):
    """
    Deterministically look up an exact legal section
    from the verified MySQL legal corpus.
    """

    document = LegalDocument.objects.filter(
        act_title__iexact=act,
        section_number=str(section),
    ).first()

    if document:
        return {
            "found": True,
            "act": document.act_title,
            "section": document.section_number,
            "text": document.text,
            "page": None,
            "source": document.source,
            "source_url": document.source_url,
        }

    return {
        "found": False,
        "act": act,
        "section": str(section),
        "message": "No verified provision found in the corpus.",
    }
    