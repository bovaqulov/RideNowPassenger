from geopy.geocoders import Nominatim
from langdetect import detect
from rapidfuzz import fuzz, process

from functools import lru_cache


class LocationDetector:
    def __init__(self, user_agent="location_finder_bot"):
        self.geolocator = Nominatim(user_agent=user_agent)

    @staticmethod
    @lru_cache(maxsize=1000)
    def _normalize_text(text: str) -> str:
        """Matnni tozalash va normallashtirish."""
        text = text.strip().lower()
        replacements = {
            "ё": "е",
            "ў": "o",
            "қ": "k",
            "ғ": "g",
        }
        for k, v in replacements.items():
            text = text.replace(k, v)
        return text

    def detect_language(self, text: str) -> str:
        try:
            return detect(text)
        except Exception:
            return "unknown"

    def find_location(self, query: str):
        """Foydalanuvchi kiritgan matndan manzilni aniqlaydi."""
        query_norm = self._normalize_text(query)

        try:
            location = self.geolocator.geocode(query_norm, language="en", addressdetails=True)
        except Exception as e:
            return {"error": f"Geocoding failed: {e}"}

        if not location:
            return {"found": False, "query": query, "suggestion": self._suggest_correction(query_norm)}

        return {
            "found": True,
            "query": query,
            "latitude": location.latitude,
            "longitude": location.longitude,
            "display_name": location.address,
            "country": location.raw.get("address", {}).get("country", ""),
            "city": location.raw.get("address", {}).get("city", "")
                or location.raw.get("address", {}).get("town", "")
                or location.raw.get("address", {}).get("village", ""),
        }

    def _suggest_correction(self, query: str):
        """Agar topilmasa, yaqin joy nomini taklif qiladi."""
        known_cities = ["tashkent", "samarkand", "bukhara", "fergana", "namangan", "andijan", "navoi", "khiva"]
        suggestion = process.extractOne(query, known_cities, scorer=fuzz.WRatio)
        if suggestion and suggestion[1] > 60:
            return suggestion[0]
        return None

