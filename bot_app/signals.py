from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from bot_app.models import TelegramUser
from bot_app.repo.user_service import BotUserService


@receiver([post_save], sender=TelegramUser)
def update_user_cache(sender, instance: TelegramUser, created: bool, **kwargs):
    """
    Foydalanuvchi yaratish yoki yangilashdan so‘ng cache'ni yangilaydi.
    """
    cache_key = f"tguser:{instance.tg_id}"
    cache.set(cache_key, instance, timeout=BotUserService.CACHE_TIMEOUT)

    action = "yaratildi" if created else "yangilandi"
    print(f"[CACHE] TelegramUser ({instance.tg_id}) {action} va cache yangilandi ✅")


@receiver([post_delete], sender=TelegramUser)
def delete_user_cache(sender, instance: TelegramUser, **kwargs):
    """
    Foydalanuvchi o‘chirilgandan keyin cache'dan ham olib tashlaydi.
    """
    cache.delete(f"tguser:{instance.tg_id}")
    print(f"[CACHE] TelegramUser ({instance.tg_id}) o‘chirildi va cache tozalandi ❌")
