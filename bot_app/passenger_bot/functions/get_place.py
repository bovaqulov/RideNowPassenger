import time
import requests
from threading import Lock
from typing import Optional, Dict

USER_AGENT = "YourAppName/1.0 (your-email@example.com)"  # o'zgartiring!
NOMINATIM_REVERSE = "https://nominatim.openstreetmap.org/reverse"
CACHE_TTL = 60 * 60  # 1 hour

_cache: Dict[str, tuple] = {}
_cache_lock = Lock()

def _cache_get(key: str):
    with _cache_lock:
        item = _cache.get(key)
        if not item:
            return None
        ts, val = item
        if time.time() - ts > CACHE_TTL:
            del _cache[key]
            return None
        return val

def _cache_set(key: str, value):
    with _cache_lock:
        _cache[key] = (time.time(), value)

def get_place_from_coords(lat: float, lon: float, prefer: Optional[str] = None) -> Dict:
    """
    Lat/Lon berilganda shahar yoki viloyat (region) nomini qaytaradi.
    Returns dict: { 'source': 'nominatim', 'display_name': str, 'city': str|None, 'region': str|None, 'raw': dict }
    prefer: optional, "city" or "region" to prefer one field.
    """
    key = f"rev:{lat:.6f}:{lon:.6f}"
    cached = _cache_get(key)
    if cached:
        return cached

    params = {
        "lat": str(lat),
        "lon": str(lon),
        "format": "jsonv2",
        "addressdetails": 1,
        "zoom": 10,  # detail level; can be adjusted
    }
    headers = {"User-Agent": USER_AGENT}
    resp = requests.get(NOMINATIM_REVERSE, params=params, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    address = data.get("address", {})
    # Priority for city-like field
    city = address.get("city") or address.get("town") or address.get("village") or address.get("hamlet")
    # Region/province/state
    region = address.get("state") or address.get("region") or address.get("county") or address.get("state_district")

    # If prefer is given, try to return it first
    if prefer == "region":
        primary = region or city
    elif prefer == "city":
        primary = city or region
    else:
        primary = city or region

    result = {
        "source": "nominatim",
        "display_name": data.get("display_name"),
        "city": city,
        "region": region,
        "primary": primary,
        "raw": data,
    }
    _cache_set(key, result)
    return result
