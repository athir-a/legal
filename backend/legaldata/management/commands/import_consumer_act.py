import json
from pathlib import Path
from django.core.management.base import BaseCommand
from legaldata.models import LegalDocument


class Command(BaseCommand):
    help = "Import Consumer Protection Act sections from JSON"

    def handle(self, *args, **options):
        file_path = Path(__file__).resolve().parents[3] / "data" / "raw" / "consumer_protection_act.json"

        with open(file_path, "r", encoding="utf-8") as f:
            sections = json.load(f)

        created = 0
        updated = 0

        for item in sections:
            obj, was_created = LegalDocument.objects.update_or_create(
                act_id=item["act_id"],
                section_number=item["section_number"],
                defaults={
                    "act_title": item["act_title"],
                    "section_title": item["section_title"],
                    "chapter": item.get("chapter"),
                    "text": item["text"],
                    "status": item.get("status", ""),
                    "year": item.get("year"),
                    "source": item.get("source", ""),
                    "source_url": item.get("source_url", ""),
                },
            )

            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(
            f"Import complete: {created} created, {updated} updated."
        ))
