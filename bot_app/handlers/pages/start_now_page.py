from telebot.types import CallbackQuery, Message
from telebot.states.sync import StateContext

from .previous_locations_page import previous_location
from ...core.loader import bot
from ...core.states import TravelState
from ...functions.buttons.default import create_btn
from ...functions.text_sender import send_msg
from ...functions.utils import del_msg


def start_now(msg: CallbackQuery | Message, state: StateContext):
    # 🔹 Boshlang'ich state-ni set qilish
    state.set(TravelState.loc_begin)
    del_msg(bot, msg)

    # 🔹 Oldingi manzillarni olish
    text, button_rows = previous_location(msg)

    if not text and not button_rows:
        # Oldingi manzillar yo'q bo'lsa
        return send_msg(
            "trip_start_prompt",
            msg,
            [["send_location"], ["back_order"]],
            markup=create_btn
        )

    # 🔹 Oldingi manzillar mavjud bo'lsa
    # Buttonlarni tugma qatorlari shaklida yuboramiz
    # ["send_location"] tugmasi birinchi qator, oldingi manzillar tugmalari keyingi qatorlar, ["back_order"] oxirgi qator
    keyboard = [["send_location"]] + button_rows + [["back_order"]]

    return send_msg(
        "start_location_with_history",
        msg,
        keyboard,
        markup=create_btn,
        info=text
    )
