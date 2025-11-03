from telebot import ContinueHandling
from telebot.states.sync import StateContext
from telebot.types import CallbackQuery

from .pages.help_page import func_help
from .pages.languages_pages import callback_language
from .pages.main_menu_page import main_menu
from .pages.order_page import order
from .pages.start_now_page import start_now
from bot_app.passenger_bot.core.loader import bot


@bot.callback_query_handler(func=lambda call: True)
def callback_control(call: CallbackQuery, state: StateContext):
    data = call.data
    print(data)

    actions = {
        # backs
        "back": main_menu,

        # settings
        "uz": callback_language,
        "ru": callback_language,
        "en": callback_language,

        # main menu
        "order": order,
        "help": func_help,

        # order
        "start_now": start_now,
    }

    if data in actions.keys():
        return actions[data](call, state)

    return ContinueHandling()