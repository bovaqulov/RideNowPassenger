from telebot.types import Message
from django.core.cache import cache
from django.db import transaction, IntegrityError
from bot_app.models import TelegramUser
from django.conf import settings


class BotUserService(TelegramUser):
    """
    Telegram foydalanuvchilarini boshqaruvchi service model.
    Java uslubida: Create, Update, Get, Delete metodlari alohida.
    """
    CACHE_PREFIX = "tguser:"
    CACHE_TIMEOUT = settings.CACHE_TIMEOUT

    class Meta:
        proxy = True
        verbose_name = "Bot foydalanuvchi servisi"
        verbose_name_plural = "Bot foydalanuvchi servislar"

    # ==========================================================
    # 🧩 YORDAMCHI FUNKSIYALAR
    # ==========================================================

    @classmethod
    def _get_cache_key(cls, tg_id: int) -> str:
        """Har bir foydalanuvchi uchun unique cache key."""
        return f"{cls.CACHE_PREFIX}{tg_id}"

    @classmethod
    def _set_cache(cls, user: TelegramUser):
        """Foydalanuvchini cache’ga yozadi."""
        cache.set(cls._get_cache_key(user.tg_id), user, timeout=cls.CACHE_TIMEOUT)

    @classmethod
    def _get_from_cache(cls, tg_id: int):
        """Cache’dan foydalanuvchini olish."""
        return cache.get(cls._get_cache_key(tg_id))

    @classmethod
    def _delete_cache(cls, tg_id: int):
        """Cache’dan foydalanuvchini o‘chirish."""
        cache.delete(cls._get_cache_key(tg_id))

    # ==========================================================
    # 🧱 CREATE
    # ==========================================================

    @classmethod
    def create(cls, msg: Message) -> TelegramUser:
        """Yangi foydalanuvchini yaratadi (agar mavjud bo‘lmasa)."""
        telegram_user = msg.from_user

        tg_id = telegram_user.id
        if cached := cls._get_from_cache(tg_id):
            return cached

        full_name = (telegram_user.full_name or "").strip()
        username = telegram_user.username

        try:
            with transaction.atomic():
                user, created = cls.objects.get_or_create(
                    tg_id=tg_id,
                    defaults={
                        "full_name": full_name,
                        "username": username,
                        "language_code": telegram_user.language_code,
                    },
                )
        except IntegrityError:
            user = cls.objects.filter(tg_id=tg_id).first()

        cls._set_cache(user)
        return user

    # ==========================================================
    # ✏️ UPDATE
    # ==========================================================

    @classmethod
    def update(cls, tg_id: int, **kwargs) -> TelegramUser | None:
        """Foydalanuvchini ma’lumotlarini yangilaydi."""
        user = cls._get_from_cache(tg_id) or cls.objects.filter(tg_id=tg_id).first()
        if not user:
            return None

        updated_fields = []
        for key, value in kwargs.items():
            if hasattr(user, key) and getattr(user, key) != value:
                setattr(user, key, value)
                updated_fields.append(key)

        if updated_fields:
            user.save(update_fields=updated_fields + ["updated_at"])
            cls._set_cache(user)

        return user

    # ==========================================================
    # 🔍 GET
    # ==========================================================

    @classmethod
    def get(cls, tg_id: int) -> TelegramUser | None:
        """Foydalanuvchini cache’dan yoki bazadan olish."""
        if cached := cls._get_from_cache(tg_id):
            return cached

        user = cls.objects.filter(tg_id=tg_id).first()
        if user:
            cls._set_cache(user)
        return user

    # ==========================================================
    # ❌ DELETE
    # ==========================================================

    @classmethod
    def delete_user(cls, tg_id: int) -> bool:
        """Foydalanuvchini bazadan va cache’dan o‘chirish."""
        cls._delete_cache(tg_id)
        deleted, _ = cls.objects.filter(tg_id=tg_id).delete()
        return bool(deleted)

    # ==========================================================
    # 🌍 LANGUAGE
    # ==========================================================

    @classmethod
    def get_lang(cls, tg_id: int) -> str:
        return cls.get(tg_id=tg_id).language_code or None

    @classmethod
    def get_lang_default(cls, tg_id: int) -> str | None:
        try:
            return cls.get(tg_id=tg_id).language_code
        except cls.DoesNotExist:
            return None
