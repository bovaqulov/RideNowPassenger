from telebot import ContinueHandling
from telebot.states.sync import StateContext
from telebot.types import CallbackQuery

from .pages.help_page import func_help
from .pages.languages_pages import callback_language
from .pages.main_menu_page import main_menu
from .pages.order_page import order
from .pages.start_now_page import start_now
from ..core.loader import bot
from ..core.states import Registration
from ..functions.buttons.default import create_btn
from ..functions.text_sender import send_msg
from ..services.passenger_manager import passenger_manager


@bot.callback_query_handler(func=lambda call: True)
def callback_control(call: CallbackQuery, state: StateContext):
    data = call.data
    print(data)

    user = passenger_manager.get_passenger(call.from_user.id)
    telegram_id = user.get("telegram_id", None)

    if not telegram_id:
        state.set(Registration.name)
        return send_msg(
            "ask_full_name",
            call,
            [[call.from_user.full_name]],
            markup=create_btn,
        )

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