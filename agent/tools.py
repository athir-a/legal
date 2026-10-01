from pathlib import Path
import sys
import re


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAG_PATH = PROJECT_ROOT / "rag"
BACKEND_PATH = PROJECT_ROOT / "backend"


if str(RAG_PATH) not in sys.path:
    sys.path.insert(0, str(RAG_PATH))

if str(BACKEND_PATH) not in sys.path:
    sys.path.insert(0, str(BACKEND_PATH))


from retriever import search


# ---------------------------------------------------------
# Django setup
# ---------------------------------------------------------

import os
import django

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings"
)

django.setup()


from legaldata.models import LegalChunk, LegalDocument


# Terms are lexical search aids only; retrieved corpus scores still determine evidence.
_CONCEPT_EXPANSIONS = (
    (
        "defective_product",
        re.compile(
            r"\b(defect(?:ive)?|malfunction\w*|faulty|damaged|broken|"
            r"does not work|doesn't work|will not work|won't work|"
            r"will not boot|won't boot|not booting|failed to boot|not working)\b"
        ),
        (
            "defective product",
            "manufacturing defect",
        ),
    ),
    (
        "product_seller",
        re.compile(
            r"\b(seller|retailer|merchant|online seller|marketplace)\b|"
            r"\bonline(?:\s+\w+)?\s+store\b"
        ),
        ("product seller",),
    ),
    (
        "service_provider",
        re.compile(
            r"\b(service provider|service cent(?:er|re)|repair cent(?:er|re)|"
            r"authorized service|authorised service|repair service)\b"
        ),
        (
            "product service provider",
            "liability of product service provider",
            "service provided faulty deficient inadequate quality nature manner performance",
        ),
    ),
    (
        "manufacturer",
        re.compile(
            r"\b(manufacturer|manufacturing|brand|company that made|maker)\b"
        ),
        (
            "product manufacturer",
        ),
    ),
    (
        "consumer_remedies",
        re.compile(
            r"\b(refund|replacement|replace|repair|compensation|remed(?:y|ies)|"
            r"redressal|relief|remove defect)\b"
        ),
        (
            "consumer redressal",
            "remove defect",
            "replace goods",
            "return price",
            "refund",
            "repair",
            "compensation",
        ),
    ),
    (
        "e_commerce",
        re.compile(
            r"\b(online purchase|online seller|marketplace|"
            r"e[ -]?commerce|internet purchase)\b"
            r"|\bonline(?:\s+\w+)?\s+store\b"
        ),
        (
            "e-commerce entity",
        ),
    ),
    (
        "product_liability",
        re.compile(
            r"\b(product liability|liability for defective product|"
            r"harm caused by (?:a )?product|manufacturer liability|"
            r"seller liability|service provider liability)\b"
        ),
        (
            "product liability action",
            "product manufacturer",
            "product seller",
            "product service provider",
            "harm caused by defective product",
        ),
    ),
    (
        "consumer_complaint",
        re.compile(
            r"\b(file a complaint|filed a complaint|filing a complaint|"
            r"who can file|who may file|submit a grievance)\b|"
            r"\bhow (?:can|may|to)\b.{0,60}\bcomplaint\b|"
            r"\bcomplaint\b.{0,60}\b(?:file|filed|submit)\b"
        ),
        (
            "consumer complaint filed by consumer",
            "recognised consumer association",
            "electronically",
        ),
    ),
    (
        "service_deficiency",
        re.compile(r"\b(deficien\w*|faulty service|inadequate service)\b"),
        (
            "deficiency in service",
            "fault imperfection shortcoming",
            "quality nature and manner of performance",
        ),
    ),
)
_MAX_EXPANSION_WORDS = 40
_DEFECT_DEFINITION_INTENT = re.compile(
    r"\bwhat does\b.{0,100}\bmean\b.{0,80}\bdefect\b|"
    r"\b(?:what is|define|definition of|meaning of)\b.{0,40}\bdefect\b"
)
_DEFECT_TERMS = re.compile(r"\b(defect|defective goods|defect in goods)\b")
_DEFECT_DEFINITION_TERMS = (
    "defect means any fault imperfection shortcoming quality quantity potency purity standard",
)
_ECOMMERCE_MEASURES_INTENT = re.compile(
    r"\b(measures?|prescrib\w*|prevent|rules?|requirements?)\b"
)
_PRODUCT_LIABILITY_TERMS = (
    "product liability action",
    "product manufacturer",
    "product seller",
    "product service provider",
    "harm caused by defective product",
)


def recognized_legal_concepts(query: str) -> dict[str, tuple[str, ...]]:
    """Return concept families detected in a query and their legal vocabulary."""
    if not isinstance(query, str) or not query.strip():
        return {}

    normalized_query = re.sub(r"[^a-z0-9\s]", " ", query.casefold())
    normalized_query = re.sub(r"\s+", " ", normalized_query).strip()
    concepts = {}

    for concept, pattern, terms in _CONCEPT_EXPANSIONS:
        if pattern.search(normalized_query):
            concepts[concept] = terms

    if (
        _DEFECT_DEFINITION_INTENT.search(normalized_query)
        and _DEFECT_TERMS.search(normalized_query)
    ):
        concepts["defect_definition"] = _DEFECT_DEFINITION_TERMS

    if (
        "e_commerce" in concepts
        and _ECOMMERCE_MEASURES_INTENT.search(normalized_query)
    ):
        concepts["ecommerce_measures"] = (
            "measures to prevent unfair trade practices in e-commerce",
        )

    if (
        "defective_product" in concepts
        and any(
            concept in concepts
            for concept in ("product_seller", "service_provider", "manufacturer")
        )
    ):
        concepts["product_liability"] = _PRODUCT_LIABILITY_TERMS

    return concepts


def expand_legal_query(query: str) -> str:
    """Append a small set of legal terms recognized from scenario language."""
    if not isinstance(query, str) or not query.strip():
        return query

    normalized_query = re.sub(r"[^a-z0-9\s]", " ", query.casefold())
    normalized_query = re.sub(r"\s+", " ", normalized_query).strip()
    additions = [
        term
        for terms in recognized_legal_concepts(query).values()
        for term in terms
    ]

    unique_additions = []
    seen_terms = set()
    added_word_count = 0
    for term in additions:
        normalized_term = re.sub(r"[^a-z0-9\s]", " ", term.casefold())
        normalized_term = re.sub(r"\s+", " ", normalized_term).strip()
        if normalized_term in normalized_query:
            continue

        if normalized_term not in seen_terms:
            term_word_count = len(term.split())
            if added_word_count + term_word_count > _MAX_EXPANSION_WORDS:
                continue
            seen_terms.add(normalized_term)
            unique_additions.append(term)
            added_word_count += term_word_count

    if not unique_additions:
        return query

    return f"{query} {' '.join(unique_additions)}"


def _search(query: str, top_k: int):
    return search(
        query,
        top_k=top_k,
        retrieval_query=expand_legal_query(query),
    )


# ---------------------------------------------------------
# Legal search
# ---------------------------------------------------------

def _fallback_tfidf_results(query: str, top_k: int):
    results = _search(query, top_k=top_k)

    fallback_results = []
    for result in results:
        fallback_results.append({
            "chunk_id": result.get("chunk_id"),
            "document_id": result.get("document_id"),
            "section_number": result.get("section_number"),
            "section_title": result.get("section_title"),
            "act_title": result.get("act_title"),
            "text": result.get("text"),
            "score": result.get("score", 0.0),
            "source": result.get("source", "India Code"),
            "source_url": result.get("source_url"),
        })

    return fallback_results


def search_legal_documents(query: str, top_k: int = 10):

    results = _search(query, top_k=top_k)

    has_corpus = (
        LegalDocument.objects.exists()
        or LegalChunk.objects.exists()
    )

    if not has_corpus:
        return {
            "query": query,
            "results": _fallback_tfidf_results(query, top_k=top_k),
        }

    enriched_results = []

    for result in results:

        chunk_id = result.get("chunk_id")

        if chunk_id is None:
            continue

        chunk = (
            LegalChunk.objects
            .select_related("document")
            .filter(id=chunk_id)
            .first()
        )

        if chunk is None:
            enriched_results.append({
                "chunk_id": result.get("chunk_id"),
                "document_id": result.get("document_id"),
                "section_number": result.get("section_number"),
                "section_title": result.get("section_title"),
                "act_title": result.get("act_title"),
                "text": result.get("text"),
                "score": result.get("score", 0.0),
                "source": result.get("source", "India Code"),
                "source_url": result.get("source_url"),
            })
            continue

        enriched_results.append({
            "chunk_id": chunk.id,
            "document_id": chunk.document.id,

            "section_number":
                chunk.document.section_number,

            "section_title":
                chunk.document.section_title,

            "act_title":
                chunk.document.act_title,

            "text":
                chunk.text,

            "score":
                result.get("score", 0.0),

            "source":
                chunk.document.source,

            "source_url":
                chunk.document.source_url,
        })

    if enriched_results:
        return {
            "query": query,
            "results": enriched_results,
        }

    return {
        "query": query,
        "results": _fallback_tfidf_results(query, top_k=top_k),
    }