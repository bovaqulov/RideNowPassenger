from telebot import ContinueHandling
from telebot.states.sync import StateContext
from telebot.types import CallbackQuery

from .pages.details_page import details_callback
from .pages.search_driver_page import search_driver
from ..core.loader import bot
from .pages.location_page import loc_begin, loc_end


@bot.message_handler(func=lambda message: True, state="*")
@bot.callback_query_handler(func=lambda call: True, state="*")
def state_control(call: CallbackQuery, state: StateContext):
    get_state = str(state.get())
    print(get_state)

    actions = {
        "TravelState:loc_begin": loc_begin,
        "TravelState:loc_end": loc_end,
        "TravelState:details": details_callback,
        "TravelState:start": search_driver,
    }

    if get_state in actions.keys():
        return actions[get_state](call, state)

    return ContinueHandling()