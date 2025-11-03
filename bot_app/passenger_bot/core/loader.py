from telebot import TeleBot, StateMemoryStorage, custom_filters
from telebot.types import BotCommand

from django.conf import settings

state_storage = StateMemoryStorage()

bot = TeleBot(
    settings.PASSENGER_BOT_TOKEN,
    threaded=False,
    state_storage=state_storage,
    use_class_middlewares=True,
    parse_mode="HTML",
)

bot.add_custom_filter(custom_filters.StateFilter(bot))

from telebot.states.sync.middleware import StateMiddleware

bot.setup_middleware(StateMiddleware(bot))

bot.set_my_commands(commands=[
    BotCommand("start", "🚀 Перезапуск"),
    # BotCommand("travel", "🚖 Заказать водителя"),
    BotCommand("language", "✅ Изменить язык"),
    # BotCommand("register", "📝 Перерегистрация")
])