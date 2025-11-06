import re

from telebot.states.sync import StateContext
from telebot.types import Message

from ...core.loader import bot
from ...core.states import Registration
from ...functions.buttons.default import create_btn
from bot_app.functions.text_sender import send_msg
from bot_app.functions.utils import del_msg
from bot_app.handlers.pages.main_menu_page import main_menu
from bot_app.services.passenger_manager import passenger_manager


def ask_name(msg: Message, state: StateContext):
    del_msg(bot, msg, 2)
    state.add_data(**{"name": msg.text})
    state.set(Registration.contact)
    return send_msg(
        "ask_contact",
        msg,
        [["send_number"]],
        markup=create_btn,
        name=msg.text
    )


def ask_contact(msg: Message, state: StateContext):
    del_msg(bot, msg, 2)
    if msg.contact:
        contact = msg.contact.phone_number
    else:
        if msg.text.isdigit() and \
            re.match(
                r"^\+998([- ])?(90|91|93|94|95|98|99|33|97|71)([- ])?(\d{3})([- ])?(\d{2})([- ])?(\d{2})$",
                msg.text):

            contact = msg.text
        else:
            return send_msg(
                "invalid_phone",
                msg,
                [["send_number"]],
                markup=create_btn,
            )

    with state.data() as data:
        name = data.get("name")

    passenger_manager.create_passenger(
        telegram_id=msg.from_user.id,
        name=name,
        contact=contact,
    )

    state.delete()
    return main_menu(msg, state)
