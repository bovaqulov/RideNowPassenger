from django.conf import settings
from telebot.states.sync import StateContext
from telebot.types import CallbackQuery

from ....buttons.inline import create_inl
from ....core.loader import bot
from ....editor.text_edit import edit_msg
from ....sender.text_sender import send_msg
from .....repo.user_service import BotUserService



@bot.callback_query_handler(func=lambda call: call.data in settings.BOT_LANGUAGE)
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
