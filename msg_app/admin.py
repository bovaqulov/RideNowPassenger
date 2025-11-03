from django.contrib import admin
from .models import BotMessage


@admin.register(BotMessage)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("slug", "get_languages", "preview_text")
    search_fields = ("slug", "msg")
    list_per_page = 25
    ordering = ("slug",)

    fieldsets = (
        (None, {
            "fields": ("slug", "msg"),
            "description": "Xabar matnlarini turli tillarda JSON shaklida kiriting. Masalan: {'uz': 'Salom', 'en': 'Hello'}"
        }),
    )

    def get_languages(self, obj):
        """JSON ichidagi tillarni ko‘rsatadi."""
        return ", ".join(obj.msg.keys()) if obj.msg else "-"
    get_languages.short_description = "Tillari"

    def preview_text(self, obj):
        """Birinchi til matnidan qisqacha preview beradi."""
        if obj.msg:
            first_lang = next(iter(obj.msg))
            return obj.msg[first_lang][:50]
        return "-"
    preview_text.short_description = "Matn namuna"


# ✅ Qo‘shimcha admin sozlamalari (optional)
admin.site.site_header = "Yo‘lovchi bot boshqaruv paneli"
admin.site.site_title = "Admin panel"
admin.site.index_title = "Xabarlarni boshqarish"
