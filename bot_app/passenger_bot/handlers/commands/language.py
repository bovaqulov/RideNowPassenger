from telebot.states.sync import StateContext
from telebot.types import Message

from bot_app.passenger_bot.handlers.pages.language_page import language
from bot_app.passenger_bot.core.loader import bot


@bot.message_handler(commands=['language'])
def handle_language(msg: Message, state: StateContext):
    return language(msg, state)
