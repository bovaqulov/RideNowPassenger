import json

import requests
from django.conf import settings


class Location:

    host = settings.MAIN_URL
    url = f"{host}journey/location"

    @classmethod
    def create_loc(cls, address, lat, lng):
         response = requests.post(
             url=cls.url,
             headers={"Content-Type": "application/json"},
             data=json.dumps({"address": address, "lat": lat, "lng": lng})
         )

         if response.status_code != 200:
             return None

         return {"is_available": True}
