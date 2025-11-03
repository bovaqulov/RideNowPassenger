from telebot.states.sync import StateContext
from telebot.types import Message

from .....repo.user_service import BotUserService
from ....core.loader import bot

from ..utils.pages.language_page import language
from ..utils.pages.main_menu_page import main_menu



@bot.message_handler(commands=['start'])
def handle_start(msg: Message, state: StateContext):
    if BotUserService.get_lang(msg.from_user.id) is None:
        return language(msg, state)
    return main_menu(msg, state)