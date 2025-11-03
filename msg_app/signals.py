from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import BotMessage


def clear_passenger_msg_cache(instance: BotMessage):
    for lang in ["uz", "en", "ru"]:
        cache_key = f"msg:{instance.slug}:{lang}"
        cache.delete(cache_key)


@receiver(post_save, sender=BotMessage)
def passenger_message_saved(sender, instance, **kwargs):
    clear_passenger_msg_cache(instance)


@receiver(post_delete, sender=BotMessage)
def passenger_message_deleted(sender, instance, **kwargs):
    clear_passenger_msg_cache(instance)
