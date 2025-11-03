from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from telebot.types import Update

from django.conf import settings

from bot_app.passenger_bot.core.loader import bot
import logging

from bot_app.passenger_bot.middlewares.user_middleware import UserMiddleware
bot.setup_middleware(UserMiddleware(flood_limit=0.87))
logger = logging.getLogger(__name__)

from bot_app.passenger_bot import handlers

@csrf_exempt
def telegram_passenger_bot(request):

    try:
        update = Update.de_json(request.body.decode())
        bot.process_new_updates([update])
        return JsonResponse({"status": "ok"})
    except Exception as e:
        logger.exception("Passenger bot error: %s", e)
        return JsonResponse({"status": "error", "detail": str(e)}, status=500)


@csrf_exempt
def set_web(request):

    p_url = f"https://{settings.DEMO_URL}/bot/webhook/"

    bot.delete_webhook()

    bot.set_webhook(url=p_url)

    return JsonResponse({
        "passenger_webhook":str(bot.get_webhook_info()),
        "info": str(bot.get_me())
    })

@csrf_exempt
def set_deploy(request):

    p_url = f"https://{settings.DEPLOY_URL}/bot/webhook/deploy/"

    bot.delete_webhook()

    bot.set_webhook(url=p_url)

    return JsonResponse({
        "passenger_webhook":str(bot.get_webhook_info()),
        "info": str(bot.get_me())
    })

