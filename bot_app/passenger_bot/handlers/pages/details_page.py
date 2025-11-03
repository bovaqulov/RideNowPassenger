from telebot.apihelper import ApiTelegramException
from telebot.types import CallbackQuery
from telebot.states.sync import StateContext

from bot_app.repo.user_service import BotUserService
from msg_app.models import BotMessage
from ...core.loader import bot
from ...core.states import TravelState
from ...functions.buttons.inline import travel_control_inl, create_inl
from ...functions.text_sender import send_msg
from ...functions.utils import del_msg
from ...functions.distance import calc_distance


# =========================================================
# 🔹 Dinamik narx hisoblovchi funksiya
# =========================================================
def calc_dynamic_price(distance_km: float, travel_class: str, passengers: int) -> int:
    """
    Masofa, klass va yo‘lovchi soni asosida narxni hisoblaydi.
    """
    base_rate = {
        "economy": 500,
        "standard": 800,
        "business": 1200
    }.get(travel_class, 500)

    return int(distance_km * base_rate * passengers)


def details_callback(call: CallbackQuery, state: StateContext):
    lang = BotUserService.get_lang(call.from_user.id)
    action = call.data

    with state.data() as data:
        loc_begin = data.get("loc_begin")
        loc_end = data.get("loc_end")
        distance = data.get("distance") or calc_distance(
            loc_begin["lat"], loc_begin["lng"],
            loc_end["lat"], loc_end["lng"]
        )
        passenger_count = data.get("passenger_count", 1)
        travel_class = data.get("travel_class", "economy")
        has_female = data.get("has_female", False)

    # === 🔹 Orqaga / Boshlash ===
    if action == "back":
        from .location_page import loc_end
        state.set(TravelState.loc_end)
        del_msg(bot, call, 1)
        return loc_end(call.message, state)

    if action == "start":
        state.set(TravelState.start)
        del_msg(bot, call)
        print(data)

        return send_msg("searching_driver", call, [["cancel"]], markup=create_inl, eta=1)

    # === 🔹 Passenger / Class / Female toggle ===
    action_map = {"one": 1, "two": 2, "free_car": 3}
    if action in action_map:
        passenger_count = action_map[action]

    elif action == "female_passenger":
        has_female = not has_female

    elif action.startswith("class:"):
        travel_class = action.split(":")[1]

    # === 🔹 Faqat o‘zgarish bo‘lganda narxni qayta hisoblash ===
    if (
            passenger_count != data.get("passenger_count")
            or travel_class != data.get("travel_class")
            or has_female != data.get("has_female")
    ):
        price = calc_dynamic_price(distance, travel_class, passenger_count)
        state.add_data(
            **{"passenger_count": passenger_count,
               "travel_class": travel_class,
               "has_female": has_female,
               "price": price,
               "distance": distance}
        )
    else:
        return bot.answer_callback_query(call.id)

    # === 🔹 Matn tayyorlash ===
    text = BotMessage.get_txt(lang, "trip_details").format(
        loc_begin=loc_begin["address"],
        loc_end=loc_end["address"],
        passenger="3+" if passenger_count > 2 else passenger_count,
        travel_class=BotMessage.get_txt(lang, travel_class),
        price=price,
        has_woman="✅" if has_female else "❌"
    )

    # === 🔹 Xabarni yangilash ===
    markup = travel_control_inl(lang, [passenger_count, travel_class, has_female])
    state.set(TravelState.details)

    try:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=markup,
            parse_mode="HTML"
        )
    except ApiTelegramException as e:
        if "message is not modified" not in str(e):
            print(f"[WARN] edit_message_text error: {e}")

    return bot.answer_callback_query(call.id)
