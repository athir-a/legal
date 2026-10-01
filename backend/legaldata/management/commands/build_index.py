import json
from pathlib import Path
import faiss
from sentence_transformers import SentenceTransformer
from django.core.management.base import BaseCommand
from legaldata.models import LegalChunk


class Command(BaseCommand):
    help = "Create embeddings and build FAISS index"

    def handle(self, *args, **options):
        chunks = list(LegalChunk.objects.select_related("document").order_by("id"))

        if not chunks:
            self.stdout.write(self.style.ERROR("No chunks found."))
            return

        self.stdout.write(f"Loading embedding model for {len(chunks)} chunks...")

        model = SentenceTransformer("all-MiniLM-L6-v2")
        texts = [chunk.text for chunk in chunks]

        embeddings = model.encode(
            texts,
            show_progress_bar=True,
            normalize_embeddings=True,
        )

        dimension = embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)
        index.add(embeddings)

        Path("rag_index").mkdir(exist_ok=True)
        faiss.write_index(index, "rag_index/legal.index")

        mapping = []
        for chunk in chunks:
            mapping.append({
                "chunk_id": chunk.id,
                "document_id": chunk.document_id,
                "section_number": chunk.document.section_number,
                "section_title": chunk.document.section_title,
                "act_title": chunk.document.act_title,
            })

        with open("rag_index/mapping.json", "w", encoding="utf-8") as f:
            json.dump(mapping, f, ensure_ascii=False, indent=2)

        self.stdout.write(self.style.SUCCESS(
            f"FAISS index created: {index.ntotal} vectors, dimension {dimension}."
        ))
