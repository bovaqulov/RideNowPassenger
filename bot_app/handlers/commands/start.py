from telebot.states.sync import StateContext
from telebot.types import Message

from ..pages.language_page import language
from ..pages.main_menu_page import main_menu
from bot_app.repo.user_service import BotUserService
from bot_app.core.loader import bot
from ...core.states import Registration
from ...functions.buttons.default import create_btn
from ...functions.text_sender import send_msg
from ...services.passenger_manager import passenger_manager


@bot.message_handler(commands=['start'])
def handle_start(msg: Message, state: StateContext):
    if BotUserService.get_lang(msg.from_user.id) is None:
        return language(msg, state)

    user = passenger_manager.get_passenger(msg.from_user.id)
    telegram_id = user.get("telegram_id", None)

    if not telegram_id:
        state.set(Registration.name)
        return send_msg(
            "ask_full_name",
            msg,
            [[msg.from_user.full_name]],
            markup=create_btn,
        )

    return main_menu(msg, state)