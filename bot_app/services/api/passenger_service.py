import json
import requests
from django.conf import settings
from typing import Dict, List, Optional

class PassengerAPIClient:
    """
    Passenger API bilan ishlash uchun client class
    """

    def __init__(self):
        self.host = getattr(settings, 'API_HOST', 'http://127.0.0.1:8001')
        self.version = getattr(settings, 'API_VERSION', 'api/v1')
        self.base_url = f"{self.host}/{self.version}/journey/passengers/"
        self.timeout = getattr(settings, 'API_TIMEOUT', 30)

    def _make_request(self, method: str, endpoint: str = "", data: Dict = None, params: Dict = None) -> Dict:
        """API so'rovini amalga oshirish"""
        url = f"{self.base_url}{endpoint}"

        try:
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'PassengerClient/1.0'
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
            elif method.upper() == 'PUT':
                response = requests.put(
                    url,
                    json=data,
                    headers=headers,
                    timeout=self.timeout
                )
            elif method.upper() == 'PATCH':
                response = requests.patch(
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
            if response.status_code in [200, 201, 204]:
                if response.status_code == 204:  # No content
                    return {'success': True, 'message': 'Successfully deleted'}
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

    def create_passenger(
        self,
        telegram_id: int,
        name: str,
        contact: str
    ) -> Dict:
        """
        Yangi yo'lovchi yaratish

        Args:
            telegram_id: Telegram user ID
            name: Yo'lovchi ismi
            contact: Telefon raqami

        Returns:
            Dict: API response
        """
        data = {
            "telegram_id": telegram_id,
            "name": name,
            "contact": contact
        }
        return self._make_request('POST', '/', data=data)

    def get_passenger(self, telegram_id: int) -> Dict:
        """
        Telegram ID bo'yicha yo'lovchi ma'lumotlarini olish

        Args:
            telegram_id: Telegram user ID

        Returns:
            Dict: API response
        """
        return self._make_request('GET', f'{telegram_id}/')

    def update_passenger(
        self,
        telegram_id: int,
        name: Optional[str] = None,
        contact: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Dict:
        """
        Yo'lovchi ma'lumotlarini yangilash

        Args:
            telegram_id: Telegram user ID
            name: Yangi ism (optional)
            contact: Yangi telefon (optional)
            is_active: Faollik holati (optional)

        Returns:
            Dict: API response
        """
        data = {}
        if name is not None:
            data['name'] = name
        if contact is not None:
            data['contact'] = contact
        if is_active is not None:
            data['is_active'] = is_active

        return self._make_request('PATCH', f'{telegram_id}/', data=data)

    def delete_passenger(self, telegram_id: int) -> Dict:
        """
        Yo'lovchini o'chirish

        Args:
            telegram_id: Telegram user ID

        Returns:
            Dict: API response
        """
        return self._make_request('DELETE', f'{telegram_id}/')

    def get_all_passengers(
        self,
        is_active: Optional[bool] = None,
        min_rating: Optional[float] = None,
        max_rating: Optional[float] = None,
        search: Optional[str] = None,
        ordering: Optional[str] = None
    ) -> Dict:
        """
        Barcha yo'lovchilarni olish (filtrlash bilan)

        Args:
            is_active: Faol yo'lovchilar (optional)
            min_rating: Minimal reyting (optional)
            max_rating: Maksimal reyting (optional)
            search: Qidiruv matni (optional)
            ordering: Tartiblash (optional)

        Returns:
            Dict: API response
        """
        params = {}
        if is_active is not None:
            params['is_active'] = is_active
        if min_rating is not None:
            params['min_rating'] = min_rating
        if max_rating is not None:
            params['max_rating'] = max_rating
        if search:
            params['search'] = search
        if ordering:
            params['ordering'] = ordering

        return self._make_request('GET', '', params=params)

    def update_rating(self, telegram_id: int, rating: float) -> Dict:
        """
        Yo'lovchi reytingini yangilash

        Args:
            telegram_id: Telegram user ID
            rating: Yangi reyting (0-5)

        Returns:
            Dict: API response
        """
        data = {"rating": rating}
        return self._make_request('POST', f'{telegram_id}/update-rating/', data=data)

    def increment_trips(self, telegram_id: int) -> Dict:
        """
        Yo'lovchi sayohatlar sonini oshirish

        Args:
            telegram_id: Telegram user ID

        Returns:
            Dict: API response
        """
        return self._make_request('POST', f'{telegram_id}/increment-trips/')

    def toggle_active(self, telegram_id: int) -> Dict:
        """
        Yo'lovchi faollik holatini o'zgartirish

        Args:
            telegram_id: Telegram user ID

        Returns:
            Dict: API response
        """
        return self._make_request('POST', f'{telegram_id}/toggle-active/')

    def get_passenger_stats(self) -> Dict:
        """
        Yo'lovchilar statistikasini olish

        Returns:
            Dict: API response
        """
        return self._make_request('GET', 'stats/')

    def get_active_passengers(self) -> Dict:
        """
        Faol yo'lovchilarni olish

        Returns:
            Dict: API response
        """
        return self._make_request('GET', 'active/')

    def get_passenger_by_telegram_query(self, telegram_id: int) -> Dict:
        """
        Query parametri orqali yo'lovchini qidirish

        Args:
            telegram_id: Telegram user ID

        Returns:
            Dict: API response
        """
        params = {'telegram_id': telegram_id}
        return self._make_request('GET', 'by-telegram/', params=params)

    def bulk_update_status(self, telegram_ids: List[int], is_active: bool) -> Dict:
        """
        Bir nechta yo'lovchi statusini yangilash

        Args:
            telegram_ids: Telegram ID lar ro'yxati
            is_active: Yangi faollik holati

        Returns:
            Dict: API response
        """
        data = {
            "telegram_ids": telegram_ids,
            "is_active": is_active
        }
        return self._make_request('POST', 'bulk-update-status/', data=data)


# Singleton instance
passenger_client = PassengerAPIClient()