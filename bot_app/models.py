from django.db import models


class TelegramUser(models.Model):
    """
    Telegram orqali tizimga kiruvchi foydalanuvchilar uchun asosiy model.
    Har bir foydalanuvchi uchun yagona Telegram identifikatori (tg_id) mavjud.
    U yo‘lovchi ham, haydovchi ham bo‘lishi mumkin.
    """
    tg_id = models.BigIntegerField(
        unique=True,
        db_index=True,
        help_text="Telegram foydalanuvchisining unikal ID raqami."
    )
    full_name = models.CharField(
        max_length=150,
        help_text="Foydalanuvchining to‘liq ismi (Telegram'dan olinadi)."
    )
    username = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Foydalanuvchining Telegram username'i (@username)."
    )
    language_code = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text="Foydalanuvchining afzal tili, masalan: uz, ru, en."
    )
    is_blocked = models.BooleanField(
        default=False,
        help_text="Agar foydalanuvchi botni bloklagan bo‘lsa — True."
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Foydalanuvchi tizimga birinchi marta kirgan vaqt."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Oxirgi yangilangan vaqt."
    )

    # ==================== FOYDALANISH UCHUN QULAY METODLAR ==================== #

    @property
    def short_name(self) -> str:
        """
        Foydalanuvchini qisqa nomda qaytaradi:
        - Ism mavjud bo‘lsa, birinchi so‘zni oladi
        - Username bo‘lsa, @username qaytaradi
        - Aks holda tg_id qaytaradi
        """
        if self.full_name:
            return self.full_name.split()[0]
        if self.username:
            return f"@{self.username}"
        return str(self.tg_id)

    def __str__(self) -> str:
        """
        Admin panel yoki konsolda foydalanuvchini qulay ko‘rinishda chiqarish.
        """
        return self.full_name or self.username or str(self.tg_id)

    class Meta:
        verbose_name = "Telegram foydalanuvchi"
        verbose_name_plural = "Telegram foydalanuvchilari"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["tg_id"]),
        ]


