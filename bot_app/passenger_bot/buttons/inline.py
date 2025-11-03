from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List
from msg_app.models import BotMessage


def create_inl(lang: str, buttons: List[List[str]]) -> InlineKeyboardMarkup:
    """
    Inline keyboard yaratadi.

    :param lang: Foydalanuvchi tili
    :param buttons: [['slug1','slug2'], ['slug3']] shaklida
                    Har bir ichki list bitta qatorni bildiradi
    :return: InlineKeyboardMarkup
    """
    markup = InlineKeyboardMarkup()

    for row in buttons:
        # row ichidagi tugmalarni yaratamiz
        row_buttons = []
        for slug in row:
            text_slug = slug.split("_")[0] if slug.startswith("back_") else slug
            text = BotMessage.get_txt(lang, text_slug)
            row_buttons.append(InlineKeyboardButton(text=text, callback_data=slug))

        # rowni markupga qo'shamiz
        markup.row(*row_buttons)

    return markup



def travel_control_inl(lang: str, buttons: List[str]) -> InlineKeyboardMarkup:
    """
    Safar sozlamalari uchun adaptive (moslashuvchan) inline klaviatura.
    :param lang: foydalanuvchi tili (uz, ru, en)
    :param buttons: [passenger_count, selected_class, has_female]
    """
    markup = InlineKeyboardMarkup(row_width=3)
    t = BotMessage.get_txt  # shorthand

    # Foydalanuvchi tanlovi
    count, selected_class, has_female = buttons
    check = " ✅"

    # === 🔹 YO‘LOVCHI SONI BLOKI ===
    btn_one = f"1 {check}" if count == 1 else "1"
    btn_two = f"2 {check}" if count == 2 else "2"
    free_car = f"{t(lang, 'free_car')}{check if count == 3 else ''}"
    markup.row(
        InlineKeyboardButton(btn_one, callback_data="one"),
        InlineKeyboardButton(btn_two, callback_data="two"),
        InlineKeyboardButton(free_car, callback_data="free_car"),
    )


    # === 🔹 AYOL YO‘LOVCHI BLOKI ===
    female_label = f"{t(lang, 'female_passenger')} {check if has_female else ''}"
    markup.row(
        InlineKeyboardButton(female_label, callback_data="female_passenger")
    )

    # === 🔹 XIZMAT KLASSI BLOKI ===
    travel_classes = ["economy", "standard", "business"]
    class_buttons = [
        InlineKeyboardButton(
            f"{t(lang, key)}{check if key == selected_class else ''}",
            callback_data=f"class:{key}"
        )
        for key in travel_classes
    ]
    markup.row(*class_buttons)

    # === 🔹 NAZORAT BLOKI (Boshlash / Orqaga) ===
    markup.row(
        InlineKeyboardButton(t(lang, 'start'), callback_data="start"))
    markup.row(
        InlineKeyboardButton(t(lang, 'back'), callback_data="back"),
    )

    return markup







