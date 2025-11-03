from telebot import BaseMiddleware, ContinueHandling
from telebot.types import Message, CallbackQuery
from django.core.cache import cache
from django.db import transaction
from django.conf import settings
from bot_app.models import TelegramUser
import time

from bot_app.passenger_bot.functions.text_sender import send_msg


class UserMiddleware(BaseMiddleware):
    """
    Har bir xabarda foydalanuvchini yaratadi yoki yangilaydi.
    Shu bilan birga, flood (tezkash yozish) nazoratini amalga oshiradi.
    """

    def __init__(self, flood_limit: float):
        """
        :param flood_limit: nechta sekundda foydalanuvchi bittadan ortiq so‘rov yuborolmaydi
        """
        super().__init__()
        self.update_types = ['message', 'callback_query']
        self.cache_timeout = settings.CACHE_TIMEOUT  # masalan 3600 sekund
        self.cache_prefix = "tguser:"
        self.flood_prefix = "flood:"
        self.flood_limit = flood_limit  # sekundlarda

    # =====================================================
    #                   PRE PROCESS
    # =====================================================
    def pre_process(self, update, data):
        tg_user = None
        if isinstance(update, Message):
            tg_user = update.from_user
        elif isinstance(update, CallbackQuery):
            tg_user = update.from_user
        else:
            return

        # 1️⃣ Flood nazorat
        if self._is_flooding(tg_user.id):
            chat_id = getattr(update, "chat", None)
            if chat_id:
                send_msg("too_many_requests", update)
            return  # handler ishlamaydi

        # 2️⃣ Foydalanuvchini olish yoki yaratish
        user = self._get_or_create_user(tg_user)
        data["user"] = user
        return ContinueHandling()

    def post_process(self, message, data, exception):
        if exception:
            print(f"[UserMiddleware Error] {exception}")

    # =====================================================
    #                   PRIVATE METHODS
    # =====================================================

    def _cache_key(self, tg_id: int) -> str:
        return f"{self.cache_prefix}{tg_id}"

    def _flood_key(self, tg_id: int) -> str:
        return f"{self.flood_prefix}{tg_id}"

    def _is_flooding(self, tg_id: int) -> bool:
        """
        Foydalanuvchi juda tez xabar yuboryaptimi — shuni aniqlaydi.
        """
        key = self._flood_key(tg_id)
        last_time = cache.get(key)
        current_time = time.time()

        if last_time and current_time - last_time < self.flood_limit:
            return True  # flood aniqlangan

        cache.set(key, current_time, timeout=self.flood_limit)
        return False

    def _get_or_create_user(self, tg_user):
        """
        Cache orqali foydalanuvchini topish yoki bazadan olish/yaratish.
        """
        tg_id = tg_user.id
        cache_key = self._cache_key(tg_id)

        cached_user = cache.get(cache_key)
        if cached_user:
            return cached_user

        full_name = (tg_user.full_name or "").strip()
        username = tg_user.username

        with transaction.atomic():
            user, created = TelegramUser.objects.get_or_create(
                tg_id=tg_id,
                defaults={
                    "full_name": full_name,
                    "username": username,
                },
            )

            updated_fields = []
            if user.full_name != full_name:
                user.full_name = full_name
                updated_fields.append("full_name")
            if user.username != username:
                user.username = username
                updated_fields.append("username")

            if updated_fields:
                user.save(update_fields=updated_fields + ["updated_at"])

        cache.set(cache_key, user, timeout=self.cache_timeout)
        return user
