import time
import json
import requests
import asyncio
from typing import Dict, Any, Optional
from threading import Lock
from django.core.cache import cache
from aiohttp import ClientSession

USER_AGENT = "RideNowBot/1.0 (admin@ridenow.uz)"
NOMINATIM_REVERSE = "https://nominatim.openstreetmap.org/reverse"
CACHE_TTL = 60 * 60  # 1 hour

_local_cache: Dict[str, tuple] = {}
_local_cache_lock = Lock()


def _cache_get(key: str) -> Optional[Dict[str, Any]]:
    # Django cache > Local cache
    val = cache.get(key)
    if val:
        return val
    with _local_cache_lock:
        item = _local_cache.get(key)
        if not item:
            return None
        ts, val = item
        if time.time() - ts > CACHE_TTL:
            del _local_cache[key]
            return None
        return val


def _cache_set(key: str, value: Dict[str, Any]):
    cache.set(key, value, CACHE_TTL)
    with _local_cache_lock:
        _local_cache[key] = (time.time(), value)


def parse_address(data: Dict[str, Any]) -> Dict[str, Any]:
    address = data.get("address", {})
    mahalla = (
        address.get("neighbourhood")
        or address.get("suburb")
        or address.get("quarter")
        or address.get("residential")
    )
    shahar_tuman = (
        address.get("city")
        or address.get("town")
        or address.get("municipality")
        or address.get("county")
        or address.get("district")
    )
    viloyat = (
        address.get("state")
        or address.get("region")
        or address.get("province")
    )

    parts = [p for p in [mahalla, shahar_tuman, viloyat] if p]
    full_address = ", ".join(parts) or data.get("display_name", "Noma'lum manzil")

    return {
        "source": "nominatim",
        "display_name": data.get("display_name", ""),
        "mahalla": mahalla,
        "shahar_tuman": shahar_tuman,
        "viloyat": viloyat,
        "full_address": full_address,
        "raw": data,
    }


def get_place_from_coords(lat: float, lon: float) -> Dict[str, Any]:
    key = f"rev:{lat:.6f}:{lon:.6f}"
    cached = _cache_get(key)
    if cached:
        return cached

    params = {
        "lat": lat,
        "lon": lon,
        "format": "jsonv2",
        "addressdetails": 1,
        "zoom": 18,
        "accept-language": "uz",
    }
    headers = {"User-Agent": USER_AGENT}

    try:
        resp = requests.get(NOMINATIM_REVERSE, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        result = parse_address(data)
    except Exception as e:
        result = {
            "source": "error",
            "display_name": f"Location at {lat:.6f}, {lon:.6f}",
            "mahalla": None,
            "shahar_tuman": None,
            "viloyat": None,
            "full_address": f"Koordinatalar: {lat:.6f}, {lon:.6f}",
            "raw": {},
        }

    _cache_set(key, result)
    return result


# --- ASYNC VERSIYA (pyTelegramBotAPI(async) yoki aiogram uchun) ---
async def aget_place_from_coords(lat: float, lon: float) -> Dict[str, Any]:
    key = f"rev:{lat:.6f}:{lon:.6f}"
    cached = _cache_get(key)
    if cached:
        return cached

    params = {
        "lat": lat,
        "lon": lon,
        "format": "jsonv2",
        "addressdetails": 1,
        "zoom": 18,
        "accept-language": "uz",
    }
    headers = {"User-Agent": USER_AGENT}

    try:
        async with ClientSession() as session:
            async with session.get(NOMINATIM_REVERSE, params=params, headers=headers, timeout=10) as resp:
                data = await resp.json()
                result = parse_address(data)
    except Exception:
        result = {
            "source": "error",
            "display_name": f"Location at {lat:.6f}, {lon:.6f}",
            "mahalla": None,
            "shahar_tuman": None,
            "viloyat": None,
            "full_address": f"Koordinatalar: {lat:.6f}, {lon:.6f}",
            "raw": {},
        }

    _cache_set(key, result)
    return result
