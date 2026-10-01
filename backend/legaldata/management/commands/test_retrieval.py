import pickle

from django.core.management.base import BaseCommand
from sklearn.metrics.pairwise import cosine_similarity


class Command(BaseCommand):
    help = "Test TF-IDF legal document retrieval"

    def handle(self, *args, **options):
        with open("rag_index/tfidf_vectorizer.pkl", "rb") as f:
            vectorizer = pickle.load(f)

        with open("rag_index/tfidf_matrix.pkl", "rb") as f:
            matrix = pickle.load(f)

        with open("rag_index/tfidf_mapping.pkl", "rb") as f:
            mapping = pickle.load(f)

        question = "What are the rights of consumers?"

        query_vector = vectorizer.transform([question])
        scores = cosine_similarity(query_vector, matrix).flatten()

        top_indices = scores.argsort()[-5:][::-1]

        print("\nQUESTION:")
        print(question)

        print("\nTOP RETRIEVED RESULTS:\n")

        for rank, index in enumerate(top_indices, start=1):
            item = mapping[index]

            print(f"{rank}. Section {item['section_number']}")
            print(f"   {item['section_title']}")
            print(f"   Score: {scores[index]:.4f}")
            print()
