import pickle
from pathlib import Path

from django.core.management.base import BaseCommand
from sklearn.feature_extraction.text import TfidfVectorizer

from legaldata.models import LegalChunk


class Command(BaseCommand):
    help = "Build a TF-IDF retrieval index for legal chunks"

    def handle(self, *args, **options):
        chunks = list(
            LegalChunk.objects
            .select_related("document")
            .order_by("id")
        )

        if not chunks:
            self.stdout.write(self.style.ERROR("No chunks found."))
            return

        texts = [chunk.text for chunk in chunks]

        self.stdout.write(
            f"Building TF-IDF index for {len(chunks)} chunks..."
        )

        vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),
            max_features=50000,
        )

        matrix = vectorizer.fit_transform(texts)

        Path("rag_index").mkdir(exist_ok=True)

        with open("rag_index/tfidf_vectorizer.pkl", "wb") as f:
            pickle.dump(vectorizer, f)

        with open("rag_index/tfidf_matrix.pkl", "wb") as f:
            pickle.dump(matrix, f)

        mapping = []

        for chunk in chunks:
            mapping.append({
                "chunk_id": chunk.id,
                "document_id": chunk.document_id,
                "section_number": chunk.document.section_number,
                "section_title": chunk.document.section_title,
                "act_title": chunk.document.act_title,
            })

        with open("rag_index/tfidf_mapping.pkl", "wb") as f:
            pickle.dump(mapping, f)

        self.stdout.write(
            self.style.SUCCESS(
                f"TF-IDF index created successfully: {matrix.shape[0]} chunks, "
                f"{matrix.shape[1]} features."
            )
        )
