"""Deterministic scenario explanations grounded in selected legal evidence."""

import re

from tools import recognized_legal_concepts


SCENARIO_TOPIC_LABELS = {
    "defective_product": "potential product-defect issues",
    "product_seller": "the product seller's role",
    "service_provider": "the product service provider's role",
    "manufacturer": "the product manufacturer's role",
    "consumer_remedies": "consumer remedies or redressal",
    "e_commerce": "an online or e-commerce transaction",
    "product_liability": "product-liability provisions",
    "consumer_complaint": "consumer complaint filing",
    "service_deficiency": "possible deficiency in service",
    "defect_definition": "the statutory definition of defect",
    "ecommerce_measures": "measures for e-commerce practices",
}

SCENARIO_SIGNALS = re.compile(
    r"\b(arrived|delivered|bought|ordered|purchased|paid|charged|sent|"
    r"refused|denied|deducted|damaged|malfunction\w*|broken|failed|"
    r"developed|honou?r\w*|would not|wouldn't|did not|didn't|"
    r"never provided|told me|wrong|service cent(?:er|re)|but|after|when)\b",
    re.IGNORECASE,
)
FIRST_PERSON = re.compile(r"\b(i|my|we|our)\b", re.IGNORECASE)
DISPUTE_SUBJECT = re.compile(
    r"\b(company|seller|store|landlord|provider|service|product|business)\b",
    re.IGNORECASE,
)


def is_scenario_question(question):
    """Recognize narratives from first-person facts or multi-event descriptions."""
    words = re.findall(r"\b\w+\b", question or "")
    signals = SCENARIO_SIGNALS.findall(question or "")
    first_person = FIRST_PERSON.search(question or "") is not None

    return (
        first_person
        and len(words) >= 6
        and bool(signals)
    ) or (
        len(words) >= 6
        and bool(signals)
        and DISPUTE_SUBJECT.search(question or "") is not None
    ) or (
        len(words) >= 28
        and len(signals) >= 2
    )


def synthesize_scenario_answer(question, evidence, format_provisions):
    """Explain selected evidence in relation to user-described facts."""
    concepts = recognized_legal_concepts(question)
    related_by_section = []

    for item in evidence:
        searchable_text = _normalize(
            f"{item.get('section_title', '')} {item.get('text', '')}"
        )
        related_concepts = [
            concept
            for concept, terms in concepts.items()
            if any(_normalize(term) in searchable_text for term in terms)
        ]
        if related_concepts:
            related_by_section.append((item, related_concepts))

    scenario_topics = []
    for _, related_concepts in related_by_section:
        for concept in related_concepts:
            label = SCENARIO_TOPIC_LABELS.get(concept)
            if label and label not in scenario_topics:
                scenario_topics.append(label)

    if scenario_topics:
        topic_summary = ", ".join(scenario_topics)
    else:
        topic_summary = "the subjects addressed by the retrieved provisions"

    fact_excerpt = question.strip()
    if len(fact_excerpt) > 900:
        fact_excerpt = fact_excerpt[:900].rstrip() + "..."

    answer_parts = [
        "### What the retrieved law means for your situation\n"
        f"You described: \"{fact_excerpt}\"\n\n"
        f"The selected passages address {topic_summary}. They are relevant to "
        "the issues raised in your account, but they do not verify what happened "
        "or determine whether any statutory conditions are met.",
        "### How the retrieved provisions relate to the facts you described",
    ]

    if related_by_section:
        for item, related_concepts in related_by_section:
            labels = [
                SCENARIO_TOPIC_LABELS[concept]
                for concept in related_concepts
                if concept in SCENARIO_TOPIC_LABELS
            ]
            label_text = ", ".join(dict.fromkeys(labels))
            title = item.get("section_title")
            provision = f"Section {item['section']}"
            if title:
                provision += f" — {title}"
            rule_summary = _summarize_retrieved_rule(item.get("text", ""))
            rule_text = f" {rule_summary}" if rule_summary else ""
            answer_parts.append(
                f"- {provision}: Your description raises questions about "
                f"{label_text}.{rule_text} This excerpt does not establish "
                "whether the statutory conditions are met."
            )
    else:
        answer_parts.append(
            "The selected provisions are shown below with their evidence excerpts. "
            "Their relevance should be assessed against the complete facts."
        )

    answer_parts.extend([
        "### What the retrieved provisions do not establish\n"
        "These excerpts do not independently verify your account, determine that "
        "a party is liable, or establish a specific outcome. They do not by "
        "themselves establish an entitlement to a refund, replacement, repair, "
        "or compensation; additional facts or provisions may matter.",
        "### Relevant legal provisions",
        format_provisions(evidence),
    ])
    return "\n\n".join(answer_parts)


def _normalize(value):
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]", " ", str(value or "").casefold())).strip()


def _summarize_retrieved_rule(text):
    """Briefly describe statutory clauses detected in the selected excerpt."""
    text = _normalize(text)
    summaries = []

    if "this chapter shall apply" in text and "defective product" in text:
        summaries.append("The text sets the chapter's scope for compensation claims involving harm from a defective product.")

    if "product liability action may be brought" in text:
        summaries.append(
            "The text describes actions that may be brought against product manufacturers, service providers, or sellers for harm caused by a defective product."
        )

    if "product manufacturer" in text and (
        "shall be liable" in text or "may be liable" in text
    ):
        conditions = []
        for phrase, label in (
            ("manufacturing defect", "a manufacturing defect"),
            ("defective in design", "a design defect"),
            ("deviation from manufacturing specifications", "a deviation from specifications"),
            ("does not conform to the express warranty", "nonconformance with an express warranty"),
        ):
            if phrase in text:
                conditions.append(label)
        if conditions:
            summaries.append(
                "The text lists circumstances in which a manufacturer may be liable, including "
                + ", ".join(conditions)
                + "."
            )

    if "product service provider" in text and (
        "shall be liable" in text or "may be liable" in text
    ):
        if "faulty or imperfect or deficient or inadequate" in text:
            summaries.append(
                "The text addresses provider liability where service is faulty, deficient, or inadequate in its required quality or performance."
            )

    if "product seller" in text and (
        "shall be liable" in text or "may be liable" in text
    ):
        conditions = []
        for phrase, label in (
            ("substantial control", "substantial control over the product"),
            ("altered or modified the product", "alteration or modification of the product"),
            ("express warranty", "an express warranty that the product failed to meet"),
            ("identity of product manufacturer", "circumstances where the manufacturer cannot be identified or reached"),
        ):
            if phrase in text:
                conditions.append(label)
        if conditions:
            summaries.append(
                "The text lists circumstances in which a seller may be liable, including "
                + ", ".join(conditions)
                + "."
            )

    return " ".join(summaries)
