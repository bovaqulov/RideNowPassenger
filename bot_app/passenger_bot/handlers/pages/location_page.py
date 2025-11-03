from telebot.states.sync import StateContext
from telebot.types import Message, CallbackQuery

from bot_app.api.models import Location
from bot_app.repo.user_service import BotUserService
from msg_app.models import BotMessage
from ..pages.order_page import order
from ..pages.start_now_page import start_now
from bot_app.passenger_bot.core.loader import bot
from bot_app.passenger_bot.functions.buttons.default import create_btn
from bot_app.passenger_bot.functions.buttons.inline import travel_control_inl
from bot_app.passenger_bot.functions.detector import LocationDetector
from bot_app.passenger_bot.functions.distance import calc_distance
from bot_app.passenger_bot.functions.get_place import get_place_from_coords
from bot_app.passenger_bot.functions.text_sender import send_msg
from bot_app.passenger_bot.functions.utils import del_msg
from bot_app.passenger_bot.core.states import TravelState


# =========================================================
# 🔹 Yordamchi funksiya: Lokatsiyani aniqlash (universal)
# =========================================================
def detect_location(msg: Message, state: StateContext, state_key: str):
    """
    Foydalanuvchi yuborgan matn yoki GPS asosida joylashuvni aniqlaydi.
    :param msg: foydalanuvchi xabari
    :param state: StateContext
    :param state_key: 'loc_begin' yoki 'loc_end'
    """

    if msg.location:  # GPS orqali
        location = {
            "address": get_place_from_coords(msg.location.latitude, msg.location.longitude).get("region"),
            "lat": msg.location.latitude,
            "lng": msg.location.longitude
        }
    else:
        text = msg.text.strip()
        detector = LocationDetector()
        result = detector.find_location(text)
        del_msg(bot, msg, 2)

        if not result.get("found"):
            state.set(getattr(TravelState, state_key))
            return send_msg(
                "location_not_found",
                msg,
                [["send_location"], ["back_order"]],
                markup=create_btn
            )

        location = {
            "address": text,
            "lat": result["latitude"],
            "lng": result["longitude"]
        }
        try:
            available = Location.create_loc(location.get("address"), location.get("lat"), location.get("lng"))
            if not available.get("is_available"):
                state.set(getattr(TravelState, state_key))
                return send_msg(
                    "only_uzbekistan",
                    msg,
                    [["send_location"], ["back_order"]],
                    markup=create_btn
                )
        except Exception as e:
            print("Failed to create location:", e)

    # ✅ Natijani saqlash
    state.add_data(**{state_key: location})
    return location


# =========================================================
# 🔹 1. Boshlanish manzil (qayerdan)
# =========================================================
def loc_begin(msg: Message, state: StateContext):
    lang = BotUserService.get_lang(msg.from_user.id)

    # 🔙 Orqaga
    if BotMessage.get_slug(lang, msg.text) == "back":
        state.delete()
        del_msg(bot, msg, 2)
        return order(msg, state)

    location = detect_location(msg, state, "loc_begin")
    if not isinstance(location, dict):
        return

    state.set(TravelState.loc_end)
    return send_msg(
        "ask_destination",
        msg,
        [["send_location"], ["back_order"]],
        markup=create_btn
    )


# =========================================================
# 🔹 2. Boradigan manzil (qayerga)
# =========================================================
def loc_end(msg: Message | CallbackQuery, state: StateContext):
    lang = BotUserService.get_lang(msg.from_user.id)

    # 🔙 Orqaga
    if isinstance(msg, CallbackQuery):
        with state.data() as data:
            loc_begin = data.get("loc_begin")
            location_end = data.get("loc_end")

            return send_msg(
                "trip_details",
                msg,
                [1, "economy", False],
                markup=travel_control_inl,
                loc_begin=loc_begin["address"],
                loc_end=location_end["address"],
                passenger=1,
                travel_class=BotMessage.get_txt(lang, "economy"),
                has_woman="❌"
            )

    if BotMessage.get_slug(lang, msg.text) == "back":
        state.delete()
        return start_now(msg, state)

    location = detect_location(msg, state, "loc_end")

    if not isinstance(location, dict):
        return  # manzil topilmadi

    # ✅ Masofa asosida narxni hisoblaymiz
    with state.data() as data:
        loc_begin = data["loc_begin"]
        dist_km = calc_distance(
            loc_begin["lat"], loc_begin["lng"],
            location["lat"], location["lng"]
        )
        price = int(dist_km * 500)

    state.add_data(**{"price": price})
    state.set(TravelState.details)

    return send_msg(
        "trip_details",
        msg,
        [1, "economy", False],
        markup=travel_control_inl,
        loc_begin=loc_begin["address"],
        loc_end=location["address"],
        passenger=1,
        travel_class=BotMessage.get_txt(lang, "economy"),
        price=price,
        has_woman="❌"
    )
