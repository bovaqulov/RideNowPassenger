from telebot.types import CallbackQuery, Message
from telebot.states.sync import StateContext

from bot_app.passenger_bot.core.loader import bot
from bot_app.passenger_bot.core.states import TravelState
from bot_app.passenger_bot.functions.buttons.default import create_btn
from bot_app.passenger_bot.functions.text_sender import send_msg
from bot_app.passenger_bot.functions.utils import del_msg


def start_now(msg: CallbackQuery | Message, state: StateContext):
    state.set(TravelState.loc_begin)
    del_msg(bot, msg)
    return send_msg(
        "trip_start_prompt",
        msg,
        [["send_location"], ["back_order"]],
        markup=create_btn
    )