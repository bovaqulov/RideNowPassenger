from telebot.states.sync import StateContext
from telebot.types import CallbackQuery, Message

from bot_app.core.loader import bot
from bot_app.functions.buttons.inline import create_inl
from bot_app.functions.text_edit import edit_msg
from bot_app.functions.text_sender import send_msg
from bot_app.functions.utils import del_msg


def order(call: CallbackQuery | Message, state: StateContext):
    state.delete()
    if isinstance(call, CallbackQuery):
        return edit_msg(
            "select_trip_type",
            call,
            [["start_now"], ['plan_trip'], ["send_parcel"], ["back"]],
            markup=create_inl
        )
    else:
        del_msg(bot, call)
        return send_msg(
            "select_trip_type",
            call,
            [["start_now"], ['plan_trip'], ["send_parcel"], ["back"]],
            markup=create_inl
        )