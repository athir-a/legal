import re

from answer_synthesis import is_scenario_question, synthesize_scenario_answer


def generate_local_answer(question, evidence):
    """
    Generate a simple grounded answer from verified legal evidence.

    This is a temporary local answer generator used while the LLM
    layer is unavailable because of API quota limits.
    """

    if not evidence:
        return {
            "answer": (
                "I could not find enough verified information in the "
                "Consumer Protection Act, 2019 to answer this question."
            ),
            "supported": False,
            "citations": [],
        }

    # Reject questions when the retrieved legal evidence is too weak.
    max_score = max(
        float(item.get("score", item.get("retrieval_score", 0.0)))
        for item in evidence
    )

    if max_score < 0.10:
        return {
            "answer": (
                "I could not find enough verified information in the "
                "Consumer Protection Act, 2019 to answer this question. "
                "I can only provide answers supported by the legal "
                "corpus available to this system."
            ),
            "supported": False,
            "citations": [],
        }

    if is_scenario_question(question):
        scenario_evidence = [
            {
                **item,
                "text": _evidence_excerpt(item.get("text", "")),
            }
            for item in evidence
        ]
        answer = synthesize_scenario_answer(
            question,
            scenario_evidence,
            lambda items: _format_evidence_answer(
                items,
                include_lead=False,
            ),
        )
    else:
        answer = _format_evidence_answer(evidence)

    # ---------------------------------------------------------
    # Citations
    # ---------------------------------------------------------

    citations = []
    seen_citations = set()

    for item in evidence:
        act = item.get("act")
        section = item.get("section")

        if not act or section is None:
            continue

        key = (act.casefold(), str(section))
        if key in seen_citations:
            continue

        seen_citations.add(key)
        citations.append({
            "act": act,
            "section": str(section),
            "page": None,
            "source": item.get("source", "India Code"),
        })

    return {
        "answer": answer,
        "supported": len(citations) > 0,
        "citations": citations,
    }


def _format_evidence_answer(evidence, include_lead=True):
    provisions = []

    def section_order(item):
        section = str(item.get("section", ""))
        match = re.match(r"^(\d+)(?:\((\d+)\))?([A-Za-z]?)$", section)
        if match:
            return (0, int(match.group(1)), int(match.group(2) or 0), match.group(3).casefold())
        return (1, section.casefold())

    for item in sorted(evidence, key=section_order):
        section = item.get("section")
        if section is None:
            continue

        title = item.get("section_title")
        heading = f"### Section {section}"
        if title:
            heading += f" — {title}"

        provisions.append(
            f"{heading}\n"
            f"Evidence excerpt:\n"
            f"{_evidence_excerpt(item.get('text', ''))}"
        )

    if not provisions:
        return (
            "I could not find enough verified information in the "
            "Consumer Protection Act, 2019 to answer this question."
        )

    formatted_provisions = "\n\n".join(provisions)
    if not include_lead:
        return formatted_provisions

    label = "provision" if len(provisions) == 1 else "provisions"
    return f"Retrieved legal {label}:\n\n{formatted_provisions}"


def _evidence_excerpt(text, max_chars=900):
    text = text.strip()
    if len(text) <= max_chars:
        return text

    excerpt = text[:max_chars]
    paragraph_boundary = max(
        excerpt.rfind("\n\n"),
        excerpt.rfind("\n"),
    )
    if paragraph_boundary >= max_chars // 2:
        excerpt = text[:paragraph_boundary]

    return excerpt.rstrip() + "…"