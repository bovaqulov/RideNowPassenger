from django.db import models
from django.core.cache import cache

from django.conf import settings


class BotMessage(models.Model):
    slug = models.SlugField(max_length=100, unique=True, db_index=True)
    msg = models.JSONField(default=dict)

    class Meta:
        verbose_name = "Yo'lovchi xabar matni"
        verbose_name_plural = "Yo'lovchi xabar matnlari"
        indexes = [
            models.Index(fields=["slug"]),
        ]

    def __str__(self):
        return self.slug

    @classmethod
    def get_txt(cls, lang: str, slug: str, **kwargs) -> str:
        cache_key = f"msg:{slug}:{lang}"
        text = cache.get(cache_key)
        if not text:
            msg_obj = cls.objects.only("msg").filter(slug=slug).first()
            if not msg_obj:
                return slug

            text = msg_obj.msg.get(lang) or slug
            cache.set(cache_key, text, timeout=settings.CACHE_TIMEOUT)
        return text.format(**kwargs) if kwargs else text

    @classmethod
    def get_slug(cls, lang: str, text: str) -> str | None:
        """
        Berilgan lang va text asosida mos slugni topadi.
        """
        cache_key = f"msg:slug:{lang}:{text}"
        slug = cache.get(cache_key)
        if slug:
            return slug

        msg_obj = cls.objects.filter(**{f"msg__{lang}": text}).only("slug").first()
        if msg_obj:
            cache.set(cache_key, msg_obj.slug, timeout=settings.CACHE_TIMEOUT)
            return msg_obj.slug
        return None
