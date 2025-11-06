from telebot.states.sync import StateContext
from telebot.types import CallbackQuery

from ...functions.text_edit import edit_msg
from ...functions.buttons.inline import create_inl
from ...functions.text_sender import send_msg
from bot_app.repo.user_service import BotUserService


def callback_language(call: CallbackQuery, state: StateContext):
    state.delete()

    try:
        BotUserService.update(call.from_user.id, language_code=call.data)
        edit_msg("language_updated", call)
        return send_msg(
            "main_menu_greeting",
            call,
            buttons=[["order"], ["my_trips"], ["help"]],
            markup=create_inl,
            name=call.from_user.full_name
        )

    except Exception as e:
        print(f"Language change failed: {e}")
