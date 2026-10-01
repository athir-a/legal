from pathlib import Path
import sys
import re


PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_PATH = PROJECT_ROOT / "backend"

if str(BACKEND_PATH) not in sys.path:
    sys.path.insert(0, str(BACKEND_PATH))


import os
import django

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings"
)

django.setup()

from legaldata.models import LegalDocument


def get_parent_section(section: str) -> str:
    """
    Convert a subsection such as:

        2(9)(i)
        2(9)(ii)
        12(1)
        35(2)(a)

    into its parent section number:

        2
        2
        12
        35
    """

    section = str(section).strip()

    match = re.match(r"^(\d+)", section)

    if match:
        return match.group(1)

    return section


def map_claims_to_citations(claims):
    """
    Map each answer claim to verified Act sections.

    The LLM may provide a precise subsection such as 2(9)(i),
    while the database stores the parent provision as section 2.

    The parent section is therefore used for verification, while
    the original subsection is preserved in the returned citation.
    """

    mapped_claims = []

    for item in claims:

        claim = item.get("claim", "").strip()
        citations = item.get("citations", [])

        if not claim:
            continue

        verified_citations = []

        for citation in citations:

            act = citation.get("act", "").strip()
            section = str(
                citation.get("section", "")
            ).strip()

            if not act or not section:
                continue

            parent_section = get_parent_section(section)

            exists = LegalDocument.objects.filter(
                act_title__iexact=act,
                section_number=parent_section,
            ).exists()

            if exists:

                verified_citations.append({
                    "act": act,
                    "section": section,
                    "page": citation.get("page"),
                    "source": citation.get(
                        "source",
                        "India Code"
                    ),
                })

        mapped_claims.append({
            "claim": claim,
            "citations": verified_citations,
            "supported": len(verified_citations) > 0,
        })

    return mapped_claims