from telebot import State
from telebot.states import StatesGroup


class TravelState(StatesGroup):
    loc_begin = State()
    loc_end = State()
    details: State = State()
    start = State()