import math
from typing import Literal

def calc_distance(
    lat1: float, lon1: float,
    lat2: float, lon2: float,
    unit: Literal["km", "m"] = "km"
) -> float:
    """
    Yer sferasi bo'ylab 2 nuqta orasidagi masofani hisoblaydi.
    Haversine formula asosida (aniq, global radiusga asoslangan).

    :param lat1: 1-nuqta kengligi (latitude)
    :param lon1: 1-nuqta uzunligi (longitude)
    :param lat2: 2-nuqta kengligi
    :param lon2: 2-nuqta uzunligi
    :param unit: 'km' yoki 'm' (default: km)
    :return: masofa float qiymat (km yoki m)
    """
    R = 6371.0  # Yer radiusi (km)

    lat1_r, lon1_r = math.radians(lat1), math.radians(lon1)
    lat2_r, lon2_r = math.radians(lat2), math.radians(lon2)

    dlat = lat2_r - lat1_r
    dlon = lon2_r - lon1_r

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance_km = R * c

    if unit == "m":
        return distance_km * 1000
    return distance_km


# 🔹 Misol:
if __name__ == "__main__":
    t1 = (41.311081, 69.240562)  # Toshkent
    t2 = (39.6542, 66.9597)      # Samarqand
    print(f"Toshkent → Samarqand: {calc_distance(*t1, *t2):.2f} km")
