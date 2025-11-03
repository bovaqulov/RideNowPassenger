from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from typing import List
from msg_app.models import BotMessage


def create_btn(lang: str, buttons: List[List[str]]) -> ReplyKeyboardMarkup:
    """
    keyboard yaratadi.

    :param lang: Foydalanuvchi tili
    :param buttons: [['slug1','slug2'], ['slug3']] shaklida
                    Har bir ichki list bitta qatorni bildiradi
    :return: ReplyKeyboardMarkup
    """
    markup = ReplyKeyboardMarkup(resize_keyboard=True)

    for row in buttons:
        row_buttons = []
        for slug in row:
            slug = slug.split("_")[0] if slug.startswith("back_") else slug
            text = BotMessage.get_txt(lang, slug)
            if slug == "send_location":
                row_buttons.append(KeyboardButton(text=text, request_location=True))
            else:
                row_buttons.append(KeyboardButton(text=text))
        markup.row(*row_buttons)
    return markup

def request_contact_btn(lang: str, buttons: List[List[str]]) -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    text = BotMessage.get_txt(lang, "send_number")
    markup.add(KeyboardButton(text=text, request_contact=True))
    return markup
