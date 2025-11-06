from typing import Dict, List, Optional, Any
from django.core.cache import cache
from .api.passenger_service import passenger_client


class PassengerManager:
    """
    Passenger API ni boshqarish uchun manager class
    Cache va error handling bilan
    """

    def __init__(self):
        self.client = passenger_client
        self.cache_timeout = 300  # 5 minutes

    def _get_cache_key(self, key: str) -> str:
        return f"passenger_{key}"

    def create_passenger(
            self,
            telegram_id: int,
            name: str,
            contact: str
    ) -> Dict[str, Any]:
        """
        Yangi yo'lovchi yaratish
        """
        result = self.client.create_passenger(telegram_id, name, contact)

        if result.get('success'):
            # Cache ni yangilash
            cache_key = self._get_cache_key(str(telegram_id))
            cache.set(cache_key, result, self.cache_timeout)

        return result

    def get_passenger(self, telegram_id: int, use_cache: bool = True) -> Dict[str, Any]:
        """
        Yo'lovchi ma'lumotlarini olish (cache bilan)
        """
        cache_key = self._get_cache_key(str(telegram_id))

        if use_cache:
            cached_data = cache.get(cache_key)
            if cached_data:
                return cached_data

        result = self.client.get_passenger(telegram_id)

        if result.get('telegram_id') and use_cache:
            cache.set(cache_key, result, self.cache_timeout)

        return result

    def update_passenger(
            self,
            telegram_id: int,
            **kwargs
    ) -> Dict[str, Any]:
        """
        Yo'lovchi ma'lumotlarini yangilash
        """
        result = self.client.update_passenger(telegram_id, **kwargs)

        if result.get('success'):
            # Cache larni yangilash
            cache_key = self._get_cache_key(str(telegram_id))
            cache.delete(cache_key)

        return result

    def delete_passenger(self, telegram_id: int) -> Dict[str, Any]:
        """
        Yo'lovchini o'chirish
        """
        result = self.client.delete_passenger(telegram_id)

        if result.get('success'):
            # Cache larni tozalash
            cache_key = self._get_cache_key(str(telegram_id))
            cache.delete(cache_key)

        return result

    def get_all_passengers(
            self,
            use_cache: bool = True,
            **filters
    ) -> Dict[str, Any]:
        """
        Barcha yo'lovchilarni olish (cache bilan)
        """
        cache_key = f"passenger_list_{hash(frozenset(filters.items()))}"

        if use_cache:
            cached_data = cache.get(cache_key)
            if cached_data:
                return cached_data

        result = self.client.get_all_passengers(**filters)

        if result.get('success') and use_cache:
            cache.set(cache_key, result, self.cache_timeout)

        return result

    def update_rating(self, telegram_id: int, rating: float) -> Dict[str, Any]:
        """
        Reyting yangilash
        """
        result = self.client.update_rating(telegram_id, rating)

        if result.get('success'):
            # Cache ni yangilash
            cache_key = self._get_cache_key(str(telegram_id))
            cache.delete(cache_key)

        return result

    def increment_trips(self, telegram_id: int) -> Dict[str, Any]:
        """
        Sayohatlar sonini oshirish
        """
        result = self.client.increment_trips(telegram_id)

        if result.get('success'):
            # Cache ni yangilash
            cache_key = self._get_cache_key(str(telegram_id))
            cache.delete(cache_key)

        return result

    def toggle_active(self, telegram_id: int) -> Dict[str, Any]:
        """
        Faollik holatini o'zgartirish
        """
        result = self.client.toggle_active(telegram_id)

        if result.get('success'):
            # Cache ni yangilash
            cache_key = self._get_cache_key(str(telegram_id))
            cache.delete(cache_key)

        return result

    def get_stats(self) -> Dict[str, Any]:
        """
        Statistikani olish
        """
        cache_key = "passenger_stats"
        cached_data = cache.get(cache_key)

        if cached_data:
            return cached_data

        result = self.client.get_passenger_stats()

        if result.get('success'):
            cache.set(cache_key, result, self.cache_timeout)

        return result

    def get_active_passengers(self, use_cache: bool = True) -> Dict[str, Any]:
        """
        Faol yo'lovchilarni olish
        """
        cache_key = "passenger_active_list"

        if use_cache:
            cached_data = cache.get(cache_key)
            if cached_data:
                return cached_data

        result = self.client.get_active_passengers()

        if result.get('success') and use_cache:
            cache.set(cache_key, result, self.cache_timeout)

        return result

    def bulk_update_status(self, telegram_ids: List[int], is_active: bool) -> Dict[str, Any]:
        """
        Bir nechta yo'lovchi statusini yangilash
        """
        result = self.client.bulk_update_status(telegram_ids, is_active)

        if result.get('success'):
            # Barcha cache larni tozalash
            for telegram_id in telegram_ids:
                cache_key = self._get_cache_key(str(telegram_id))
                cache.delete(cache_key)
            cache.delete("passenger_active_list")
            cache.delete("passenger_stats")

        return result

    def passenger_exists(self, telegram_id: int) -> bool:
        """
        Yo'lovchi mavjudligini tekshirish
        """
        result = self.get_passenger(telegram_id)
        return result.get('success', False)

    def clear_cache(self, telegram_id: Optional[int] = None):
        """
        Cache ni tozalash
        """
        if telegram_id:
            cache_key = self._get_cache_key(str(telegram_id))
            cache.delete(cache_key)


# Singleton instance
passenger_manager = PassengerManager()