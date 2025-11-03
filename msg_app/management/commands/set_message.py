import json
from django.core.management.base import BaseCommand
from msg_app.models import BotMessage
from django.core.cache import cache
from pathlib import Path


class Command(BaseCommand):
    help = "language.json faylidagi xabarlarni Message modeliga yuklaydi yoki yangilaydi."

    def handle(self, *args, **options):
        data_path = Path(__file__).resolve().parent.parent.parent / "data" / "language.json"

        if not data_path.exists():
            self.stdout.write(self.style.ERROR(f"❌ Fayl topilmadi: {data_path}"))
            return

        with open(data_path, "r", encoding="utf-8") as f:
            messages = json.load(f)

        added, updated = 0, 0

        for slug, msg_data in messages.items():
            obj, created = BotMessage.objects.update_or_create(
                slug=slug, defaults={"msg": msg_data}
            )
            for lang in ["uz", "en", "ru"]:
                cache.delete(f"msg:{slug}:{lang}")  # eski cache ni tozalash

            if created:
                added += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(
            f"✅ Yuklash tugadi. Yangi: {added}, Yangilangan: {updated}"
        ))
