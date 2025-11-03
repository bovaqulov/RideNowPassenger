from telebot.states.sync import StateContext
from telebot.types import Message

from ..pages.language_page import language
from ..pages.main_menu_page import main_menu
from bot_app.repo.user_service import BotUserService
from bot_app.passenger_bot.core.loader import bot


@bot.message_handler(commands=['start'])
def handle_start(msg: Message, state: StateContext):
    if BotUserService.get_lang(msg.from_user.id) is None:
        return language(msg, state)
    return main_menu(msg, state)