from django.core.management.base import BaseCommand
from legaldata.models import LegalDocument, LegalChunk


class Command(BaseCommand):
    help = "Split legal sections into overlapping chunks"

    def handle(self, *args, **options):
        chunk_size = 800
        overlap = 150

        LegalChunk.objects.all().delete()

        total = 0

        for document in LegalDocument.objects.all().order_by("id"):
            text = document.text.strip()
            start = 0
            chunk_index = 0

            while start < len(text):
                end = start + chunk_size
                chunk_text = text[start:end].strip()

                if chunk_text:
                    LegalChunk.objects.create(
                        document=document,
                        chunk_index=chunk_index,
                        text=chunk_text,
                    )
                    total += 1
                    chunk_index += 1

                if end >= len(text):
                    break

                start = end - overlap

        self.stdout.write(self.style.SUCCESS(
            f"Chunking complete: {total} chunks created."
        ))
