from django.contrib import admin
from .models import TelegramUser


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    """
    Telegram foydalanuvchilarni boshqarish uchun admin interfeysi.
    """
    list_display = (
        "id",
        "tg_id",
        "display_name",
        "username",
        "language_code",
        "is_blocked",
        "created_at",
    )
    list_display_links = ("id", "tg_id", "display_name")
    list_filter = ("is_blocked", "language_code", "created_at")
    search_fields = ("tg_id", "full_name", "username")
    ordering = ("-created_at",)
    list_per_page = 25

    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Asosiy ma'lumotlar", {
            "fields": (
                "tg_id",
                "full_name",
                "username",
                "language_code",
            ),
        }),
        ("Holat", {
            "fields": ("is_blocked",),
        }),
        ("Tizim", {
            "fields": ("created_at", "updated_at"),
        }),
    )

    def display_name(self, obj):
        """Admin panelda foydalanuvchining nomini chiroyli chiqaradi."""
        return obj.short_name

    display_name.short_description = "Ism"

    def has_add_permission(self, request):
        """
        Admin panel orqali yangi foydalanuvchi qo‘shishga ruxsat berilmaydi.
        Chunks foydalanuvchilar bot orqali avtomatik yaratiladi.
        """
        return False
