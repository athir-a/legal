import pickle
import re
from pathlib import Path

from sklearn.metrics.pairwise import cosine_similarity


BASE_DIR = Path(__file__).resolve().parents[1]
INDEX_DIR = BASE_DIR / "backend" / "rag_index"


LEGAL_KEYWORDS = {
    "consumer": [
        "consumer",
        "buyer",
        "purchaser",
        "goods",
        "services",
        "consideration",
        "consumer rights",
    ],
    "consumer rights": [
        "right to safety",
        "right to information",
        "right to choose",
        "right to be heard",
        "redressal",
        "consumer protection",
    ],
    "unfair trade practice": [
        "unfair trade practice",
        "misleading advertisement",
        "false representation",
        "deceptive practice",
    ],
    "complaint": [
        "complaint",
        "complainant",
        "district commission",
        "filing",
        "manner in which complaint shall be made",
        "consumer dispute",
    ],
    "file a complaint": [
        "complaint",
        "complainant",
        "district commission",
        "manner in which complaint shall be made",
        "consumer dispute",
    ],
    "remedies": [
        "relief",
        "refund",
        "replacement",
        "repair",
        "compensation",
        "remove defects",
        "unfair trade practice",
    ],
    "product liability": [
        "product liability",
        "product manufacturer",
        "product seller",
        "product service provider",
        "defective product",
        "harm",
    ],
    "limitation period": [
        "limitation period",
        "two years",
        "period of limitation",
        "delay",
        "sufficient cause",
    ],
    "central consumer protection authority": [
        "central consumer protection authority",
        "central authority",
        "investigation",
        "unfair trade practice",
        "misleading advertisement",
    ],
}


SECTION_HINTS = {
    "consumer rights": ["2"],
    "what are consumer rights": ["2"],
    "what are the rights of consumers": ["2"],
    "what is a consumer": ["2"],
    "who is a consumer": ["2"],

    "unfair trade practice": ["2", "94"],

    "product liability": ["83", "84", "85", "86", "87"],
    "product liability action": ["83"],
    "product manufacturer": ["84"],
    "manufacturer liable": ["84"],

    "central consumer protection authority": ["10", "18"],
    "powers and functions of central consumer protection authority": ["18"],

    "limitation period": ["69"],

    "file a complaint": ["35"],
    "filing a complaint": ["35"],
    "how can a consumer file a complaint": ["35"],
    "how to file a complaint": ["35"],

    "remedies": ["39", "40", "41", "49", "59"],
    "relief": ["39"],

    "mediation": ["74", "75", "76"],
    "mediation cell": ["74"],
    "consumer mediation cell": ["74"],
}


def normalize(text):
    text = str(text or "").lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def expand_query(query):
    normalized_query = normalize(query)

    additions = []

    for phrase, keywords in LEGAL_KEYWORDS.items():
        if phrase in normalized_query:
            additions.extend(keywords)

    expanded = query

    if additions:
        expanded += " " + " ".join(dict.fromkeys(additions))

    return expanded


class LegalRetriever:

    def __init__(self):

        with open(
            INDEX_DIR / "tfidf_vectorizer.pkl",
            "rb",
        ) as file:
            self.vectorizer = pickle.load(file)

        with open(
            INDEX_DIR / "tfidf_matrix.pkl",
            "rb",
        ) as file:
            self.matrix = pickle.load(file)

        with open(
            INDEX_DIR / "tfidf_mapping.pkl",
            "rb",
        ) as file:
            self.mapping = pickle.load(file)

        if self.matrix.shape[0] != len(self.mapping):
            raise ValueError(
                "The TF-IDF matrix and mapping have different sizes. "
                "Rebuild the index with build_tfidf_index."
            )

    def search(self, query, top_k=5):

        if not isinstance(query, str) or not query.strip():
            return []

        top_k = max(1, int(top_k))

        expanded_query = expand_query(query)

        query_vector = self.vectorizer.transform(
            [expanded_query]
        )

        scores = cosine_similarity(
            query_vector,
            self.matrix,
        ).flatten()

        original_query = normalize(query)

        # Exact section-title/query matching
        for index, item in enumerate(self.mapping):

            title = normalize(
                item.get("section_title", "")
            )

            text = normalize(
                item.get("text", "")
            )

            if title and title in original_query:
                scores[index] += 0.25

            if (
                original_query
                and len(original_query) > 8
                and original_query in text
            ):
                scores[index] += 0.20

        # Query/title word overlap
        query_words = set(
            re.findall(
                r"\b[a-z]{4,}\b",
                original_query,
            )
        )

        for index, item in enumerate(self.mapping):

            title = normalize(
                item.get("section_title", "")
            )

            title_words = set(
                re.findall(
                    r"\b[a-z]{4,}\b",
                    title,
                )
            )

            overlap = query_words.intersection(
                title_words
            )

            if overlap:
                scores[index] += min(
                    0.04 * len(overlap),
                    0.16,
                )

        # Domain-specific section hints
        for topic, section_numbers in SECTION_HINTS.items():

            if topic in original_query:

                for index, item in enumerate(self.mapping):

                    if (
                        str(item.get("section_number", ""))
                        in section_numbers
                    ):
                        scores[index] += 0.30

        ranked_indices = scores.argsort()[::-1]

        results = []
        seen_sections = set()

        for index in ranked_indices:

            item = self.mapping[index]

            section_number = str(
                item.get("section_number", "")
            )

            if section_number in seen_sections:
                continue

            if scores[index] <= 0:
                continue

            seen_sections.add(section_number)

            result = item.copy()

            result["score"] = float(
                scores[index]
            )

            results.append(result)

            if len(results) >= top_k:
                break

        return results


_retriever = None


def search(query, top_k=5):

    global _retriever

    if _retriever is None:
        _retriever = LegalRetriever()

    return _retriever.search(
        query,
        top_k,
    )