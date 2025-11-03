from telebot import TeleBot
from telebot.types import CallbackQuery, Message
import requests

def get_data(call: CallbackQuery):
    return call.data.split(":", 1)[-1]

def del_msg(bot: TeleBot, call: CallbackQuery | Message, count: int = 1):
    """
    So‘nggi `count` ta xabarni o‘chiradi.
    call — CallbackQuery yoki Message bo‘lishi mumkin.
    """
    try:
        if isinstance(call, CallbackQuery):
            chat_id = call.message.chat.id
            last_message_id = call.message.message_id
        else:
            chat_id = call.chat.id
            last_message_id = call.message_id

        # Har bir xabarni alohida o‘chiradi
        for msg_id in range(last_message_id, last_message_id - count, -1):
            try:
                bot.delete_message(chat_id, msg_id)
            except Exception:
                continue  # agar ba'zilari allaqachon o‘chgan bo‘lsa — davom et

    except Exception as e:
        print(f"[❌] del_msg xatosi: {e}")



def get_address_from_coords(latitude: float, longitude: float) -> str:
    """
    Koordinatalardan manzil aniqlovchi funksiya (OpenStreetMap Nominatim orqali).
    API key talab qilmaydi.
    """
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            "lat": latitude,
            "lon": longitude,
            "format": "json",
            "addressdetails": 1,
            "zoom": 18,
        }
        headers = {"User-Agent": "GeoLocator/1.0"}
        response = requests.get(url, params=params, headers=headers, timeout=10)

        if response.status_code == 200:
            data = response.json()
            address = data.get("display_name", "Manzil topilmadi")
            return address
        else:
            return f"Xato: {response.status_code} – javob olinmadi."

    except Exception as e:
        return f"Xatolik yuz berdi: {e}"


