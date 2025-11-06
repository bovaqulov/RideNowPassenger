import requests
import logging
from django.core.cache import cache
from typing import List, Dict, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
import time
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class LocationProvider(Enum):
    """Lokatsiya provayderlari"""
    LOCATIONIQ = "locationiq"
    NOMINATIM = "nominatim"
    GOOGLE_MAPS = "google_maps"
    MAPBOX = "mapbox"


@dataclass
class LocationResult:
    """Lokatsiya natijasi uchun ma'lumotlar klassi"""
    display_name: str
    latitude: float
    longitude: float
    country: str
    country_code: str
    region: str
    city: str
    type: str
    confidence: float = 0.0
    provider: str = None
    is_in_uzbekistan: bool = False


class BaseLocationProvider(ABC):
    """Asosiy lokatsiya provayderi interfeysi"""

    @abstractmethod
    def search_locations(self, query: str, limit: int = 5) -> List[LocationResult]:
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        pass


class LocationIQProvider(BaseLocationProvider):
    """LocationIQ provayderi"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://us1.locationiq.com/v1/search"
        self.rate_limit_delay = 0.1  # So'rovlar orasidagi kutish vaqti

    def search_locations(self, query: str, limit: int = 5) -> List[LocationResult]:
        """LocationIQ orqali lokatsiya qidirish"""
        params = {
            "key": self.api_key,
            "q": query,
            "format": "json",
            "addressdetails": 1,
            "limit": limit,
            "dedupe": 1,  # Takrorlanishlarni olib tashlash
            "normalizeaddress": 1
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()

            results = []
            for item in data:
                location = self._parse_location_item(item)
                if location:
                    results.append(location)

            # Rate limiting
            time.sleep(self.rate_limit_delay)
            return results

        except requests.RequestException as e:
            logger.error(f"LocationIQ API xatosi: {e}")
            return []
        except Exception as e:
            logger.error(f"LocationIQ qayta ishlash xatosi: {e}")
            return []

    def _parse_location_item(self, item: Dict) -> Optional[LocationResult]:
        """API dan qaytgan ma'lumotlarni qayta ishlash"""
        try:
            address = item.get("address", {})
            country_code = address.get("country_code", "").lower()

            location = LocationResult(
                display_name=item.get("display_name", ""),
                latitude=float(item.get("lat", 0)),
                longitude=float(item.get("lon", 0)),
                country=address.get("country", ""),
                country_code=country_code,
                region=address.get("state", "") or address.get("state_district", ""),
                city=address.get("city") or address.get("town") or address.get("village") or "",
                type=item.get("type", ""),
                provider=self.get_provider_name(),
                is_in_uzbekistan=country_code == "uz"
            )

            # Confidence ni hisoblash (soddalashtirilgan)
            location.confidence = self._calculate_confidence(item, address)

            return location

        except (ValueError, KeyError) as e:
            logger.warning(f"Location ma'lumotlarini qayta ishlash xatosi: {e}")
            return None

    def _calculate_confidence(self, item: Dict, address: Dict) -> float:
        """Natija ishonchliligini hisoblash"""
        confidence = 0.5  # Asosiy ball

        # Importance asosida
        importance = item.get("importance", 0)
        if importance > 0.7:
            confidence += 0.3
        elif importance > 0.4:
            confidence += 0.15

        # Address tafsilotlari asosida
        if address.get("city"):
            confidence += 0.1
        if address.get("state"):
            confidence += 0.05

        return min(confidence, 1.0)

    def get_provider_name(self) -> str:
        return LocationProvider.LOCATIONIQ.value


class NominatimProvider(BaseLocationProvider):
    """OpenStreetMap Nominatim provayderi (bepul)"""

    def __init__(self):
        self.base_url = "https://nominatim.openstreetmap.org/search"
        self.rate_limit_delay = 1.0  # Nominatim uchun ko'proq kutish kerak
        self.headers = {
            'User-Agent': 'TaxiBot/1.0 (contact: developer@example.com)'
        }

    def search_locations(self, query: str, limit: int = 5) -> List[LocationResult]:
        """Nominatim orqali lokatsiya qidirish"""
        params = {
            "q": query,
            "format": "json",
            "addressdetails": 1,
            "limit": limit,
            "countrycodes": "uz",  # O'zbekiston uchun optimallashtirish
            "dedupe": 1
        }

        try:
            response = requests.get(
                self.base_url,
                params=params,
                timeout=15,
                headers=self.headers
            )
            response.raise_for_status()
            data = response.json()

            results = []
            for item in data:
                location = self._parse_location_item(item)
                if location:
                    results.append(location)

            time.sleep(self.rate_limit_delay)
            return results

        except requests.RequestException as e:
            logger.error(f"Nominatim API xatosi: {e}")
            return []

    def _parse_location_item(self, item: Dict) -> Optional[LocationResult]:
        """Nominatim ma'lumotlarini qayta ishlash"""
        try:
            address = item.get("address", {})
            country_code = address.get("country_code", "").lower()

            location = LocationResult(
                display_name=item.get("display_name", ""),
                latitude=float(item.get("lat", 0)),
                longitude=float(item.get("lon", 0)),
                country=address.get("country", ""),
                country_code=country_code,
                region=address.get("state", "") or address.get("region", ""),
                city=address.get("city") or address.get("town") or address.get("village") or "",
                type=item.get("type", ""),
                provider=self.get_provider_name(),
                is_in_uzbekistan=country_code == "uz"
            )

            # Importance asosida confidence
            importance = float(item.get("importance", 0))
            location.confidence = min(importance, 1.0)

            return location

        except (ValueError, KeyError) as e:
            logger.warning(f"Nominatim ma'lumotlarini qayta ishlash xatosi: {e}")
            return None

    def get_provider_name(self) -> str:
        return LocationProvider.NOMINATIM.value


class LocationSearchService:
    """Lokatsiya qidiruv xizmati"""

    def __init__(self):
        self.providers = self._initialize_providers()
        self.cache_timeout = 60 * 60 * 24  # 24 soat

    def _initialize_providers(self) -> List[BaseLocationProvider]:
        """Provayderlarni ishga tushirish"""
        providers = []

        # LocationIQ (asosiy provayder)
        locationiq_key = "pk.e6051689e5dfa1dc43e53c153c7e824c"  # Konfiguratsiyadan olish kerak
        if locationiq_key:
            providers.append(LocationIQProvider(locationiq_key))

        # Nominatim (zaxira provayder)
        providers.append(NominatimProvider())

        return providers

    def find_possible_locations(
            self,
            query: str,
            limit: int = 5,
            prefer_uzbekistan: bool = True
    ) -> List[LocationResult]:
        """
        Lokatsiyalarni qidirish (bir nechta provayderlar orqali)

        Args:
            query: Qidiruv so'rovi
            limit: Maksimal natijalar soni
            prefer_uzbekistan: O'zbekiston lokatsiyalariga ustunlik berish

        Returns:
            Saralangan lokatsiyalar ro'yxati
        """
        query = query.strip().lower()
        if not query or len(query) < 2:
            return []

        # Cache dan tekshirish
        cache_key = f"location_search:{query}:{limit}:{prefer_uzbekistan}"
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.info(f"Cache dan topildi: {query}")
            return cached_result

        # Provayderlar orqali qidirish
        all_results = []

        for provider in self.providers:
            try:
                logger.info(f"{provider.get_provider_name()} orqali qidirilmoqda: {query}")
                results = provider.search_locations(query, limit * 2)  # Ko'proq natija olish
                all_results.extend(results)

                # Agar yetarli natija topsak, to'xtatamiz
                if len(all_results) >= limit * 2:
                    break

            except Exception as e:
                logger.error(f"{provider.get_provider_name()} xatosi: {e}")
                continue

        # Natijalarni saralash
        sorted_results = self._sort_and_filter_results(
            all_results,
            limit,
            prefer_uzbekistan
        )

        # Cache ga saqlash
        if sorted_results:
            cache.set(cache_key, sorted_results, self.cache_timeout)

        return sorted_results

    def _sort_and_filter_results(
            self,
            results: List[LocationResult],
            limit: int,
            prefer_uzbekistan: bool
    ) -> List[LocationResult]:
        """Natijalarni saralash va filtrlash"""
        if not results:
            return []

        # Takrorlanishlarni olib tashlash
        unique_results = self._remove_duplicates(results)

        # Saralash
        sorted_results = sorted(
            unique_results,
            key=lambda x: (
                # O'zbekiston lokatsiyalariga ustunlik
                -x.is_in_uzbekistan if prefer_uzbekistan else 0,
                # Confidence bo'yicha
                -x.confidence,
                # Shahar/joy nomiga
                len(x.city) > 0
            ),
            reverse=False
        )

        return sorted_results[:limit]

    def _remove_duplicates(self, results: List[LocationResult]) -> List[LocationResult]:
        """Takrorlangan lokatsiyalarni olib tashlash"""
        seen = set()
        unique_results = []

        for result in results:
            # Lokatsiya identifikatori
            location_id = f"{result.latitude:.4f},{result.longitude:.4f}"

            if location_id not in seen:
                seen.add(location_id)
                unique_results.append(result)

        return unique_results

    def search_in_uzbekistan(self, query: str, limit: int = 5) -> List[LocationResult]:
        """Faqlat O'zbekiston hududida qidirish"""
        return self.find_possible_locations(
            query, limit, prefer_uzbekistan=True
        )

    def validate_uzbekistan_location(self, lat: float, lon: float) -> bool:
        """Lokatsiya O'zbekiston hududida ekanligini tekshirish"""
        # Soddalashtirilgan tekshirish
        uzbekistan_bounds = {
            'min_lat': 37.0, 'max_lat': 45.0,
            'min_lon': 56.0, 'max_lon': 73.0
        }

        return (
                uzbekistan_bounds['min_lat'] <= lat <= uzbekistan_bounds['max_lat'] and
                uzbekistan_bounds['min_lon'] <= lon <= uzbekistan_bounds['max_lon']
        )


# Global instance
location_service = LocationSearchService()


# Orqa eshik funksiyasi (oldingi kod bilan moslik uchun)
def find_possible_locations(query: str, limit: int = 5) -> List[Dict]:
    """
    Orqa eshik funksiyasi - yangi tizim bilan moslik
    """
    results = location_service.find_possible_locations(query, limit)

    # Eski formatga o'tkazish
    legacy_results = []
    for result in results:
        legacy_results.append({
            "display_name": result.display_name,
            "latitude": result.latitude,
            "longitude": result.longitude,
            "country": result.country,
            "country_code": result.country_code,
            "state": result.region,
            "city": result.city,
            "type": result.type,
            "confidence": result.confidence,
            "is_in_uzbekistan": result.is_in_uzbekistan
        })

    return legacy_results
