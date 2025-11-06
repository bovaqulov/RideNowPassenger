from telebot.states.sync import StateContext
from telebot.types import Message, CallbackQuery

from ...functions.buttons.inline import create_inl
from ...functions.text_edit import edit_msg
from ...functions.text_sender import send_msg


def main_menu(msg: Message | CallbackQuery, state: StateContext):
    state.delete()
    if isinstance(msg, Message):
        return send_msg(
            "main_menu_greeting",
            msg,
            [["order"], ["my_trips"], ["help"]],
            markup=create_inl,
            name=msg.from_user.full_name)
    else:
        return edit_msg(
            "main_menu_greeting",
            msg,

            [["order"], ["my_trips"], ["help"]],
            markup=create_inl,
            name=msg.from_user.full_name)