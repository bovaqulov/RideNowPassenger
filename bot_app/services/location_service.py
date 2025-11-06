import json

import requests
from django.conf import settings
from typing import Dict, Optional


class LocationAPIClient:
    """
    Location API bilan ishlash uchun client class
    """

    def __init__(self):
        self.host = getattr(settings, 'API_HOST', 'http://127.0.0.1:8001')
        self.version = getattr(settings, 'API_VERSION', 'api/v1')
        self.base_url = f"{self.host}/{self.version}/journey/locations/"
        self.timeout = getattr(settings, 'API_TIMEOUT', 3600)

    def _make_request(self, method: str, endpoint: str = "", data: Dict = None, params: Dict = None) -> Dict:
        """API so'rovini amalga oshirish"""
        url = f"{self.base_url}{endpoint}"

        try:
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'LocationClient/1.0'
            }

            if method.upper() == 'GET':
                response = requests.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=self.timeout
                )
            elif method.upper() == 'POST':
                response = requests.post(
                    url,
                    json=data,
                    headers=headers,
                    timeout=self.timeout
                )
            elif method.upper() == 'DELETE':
                response = requests.delete(
                    url,
                    headers=headers,
                    timeout=self.timeout
                )
            else:
                return {'success': False, 'error': f'Unsupported method: {method}'}

            # Response ni tekshirish
            if response.status_code in [200, 201]:
                return response.json()
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}',
                    'status_code': response.status_code
                }

        except requests.exceptions.Timeout:
            return {'success': False, 'error': 'Request timeout'}
        except requests.exceptions.ConnectionError:
            return {'success': False, 'error': 'Connection error'}
        except requests.exceptions.RequestException as e:
            return {'success': False, 'error': f'Request exception: {str(e)}'}
        except json.JSONDecodeError:
            return {'success': False, 'error': 'Invalid JSON response'}
        except Exception as e:
            return {'success': False, 'error': f'Unexpected error: {str(e)}'}

    def create_user_location(
            self,
            telegram_id: int,
            address: str,
            lat: float,
            lng: float,
            accuracy: Optional[float] = None,
            live_period: Optional[int] = None,
            heading: Optional[int] = None
    ) -> Dict:
        """
        Foydalanuvchi uchun yangi lokatsiya yaratish

        Args:
            telegram_id: Foydalanuvchi Telegram ID
            lat: Latitude
            lng: Longitude
            address: Address
            accuracy: Lokatsiya aniqligi (optional)
            live_period: Live location period (optional)
            heading: Yo'nalish (optional)

        Returns:
            Dict: API response
        """
        data = {
            "telegram_id": telegram_id,
            "coordinate": {"lat": lat, "lng": lng},
            "name": address
        }

        # Qo'shimcha parametrlarni qo'shish
        if accuracy is not None:
            data["accuracy"] = accuracy
        if live_period is not None:
            data["live_period"] = live_period
        if heading is not None:
            data["heading"] = heading

        return self._make_request('POST', 'create-user-location/', data=data)


    def get_user_locations(self, telegram_id: int) -> Dict:
        """
        Foydalanuvchining barcha joylashuvlarini olish

        Args:
            telegram_id: Foydalanuvchi Telegram ID

        Returns:
            Dict: API response
        """
        return self._make_request('GET', f'user-locations/{telegram_id}/')

    def get_user_latest_location(self, telegram_id: int) -> Dict:
        """
        Foydalanuvchining oxirgi joylashuvini olish

        Args:
            telegram_id: Foydalanuvchi Telegram ID

        Returns:
            Dict: API response
        """
        return self._make_request('GET', f'user-latest/{telegram_id}/')

    def search_by_coordinates(self, lat: float, lng: float) -> Dict:
        """
        Koordinatalar orqali joylashuvni qidirish

        Args:
            lat: Latitude
            lng: Longitude

        Returns:
            Dict: API response
        """
        data = {"coordinate": {"lat": lat, "lng": lng}}
        return self._make_request('POST', 'search-by-coordinates/', data=data)

    def delete_user_locations(self, telegram_id: int) -> Dict:
        """
        Foydalanuvchining barcha joylashuvlarini o'chirish

        Args:
            telegram_id: Foydalanuvchi Telegram ID

        Returns:
            Dict: API response
        """
        return self._make_request('DELETE', f'delete-user-locations/{telegram_id}/')


    def get_latest_location_coordinates(self, telegram_id: int) -> Optional[Dict]:
        """
        Foydalanuvchining oxirgi lokatsiya koordinatalarini olish

        Args:
            telegram_id: Foydalanuvchi Telegram ID

        Returns:
            Dict: {"lat": float, "lng": float} yoki None
        """
        result = self.get_user_latest_location(telegram_id)

        if result.get('success') and result.get('location'):
            location_data = result['location'].get('location', {})
            if location_data:
                return {
                    "lat": location_data.get('lat'),
                    "lng": location_data.get('lng')
                }
        return None

    def get_user_locations_count(self, telegram_id: int) -> int:

        result = self.get_user_locations(telegram_id)
        return result.get('total_count', 0) if result.get('success') else 0


# Singleton instance
location_client = LocationAPIClient()
