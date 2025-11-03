from telebot.states.sync import StateContext
from telebot.types import CallbackQuery, Message

from bot_app.passenger_bot.buttons.inline import create_inl
from bot_app.passenger_bot.sender.text_sender import send_msg


def language(msg: CallbackQuery | Message, state: StateContext):
    state.delete()
    return send_msg(
        "choose_language",
        msg,
        [["uz"], ["en"], ["ru"]],
        markup=create_inl)
