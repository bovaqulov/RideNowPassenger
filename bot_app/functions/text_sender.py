from queue import Queue, Full
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
from telebot.types import Message, CallbackQuery, ReplyKeyboardRemove
from bot_app.repo.user_service import BotUserService
from msg_app.models import BotMessage
from bot_app.core.loader import bot

# ================= GLOBAL SETTINGS ================= #
MAX_QUEUE_SIZE = 3_000    # navbat xabarlar
WORKER_COUNT = 2           # minimal threadlar, resurs tejash
QUEUE_TIMEOUT = 0.01       # queue.put kutish vaqti

# ================= QUEUE & THREADPOOL ================= #
message_queue = Queue(maxsize=MAX_QUEUE_SIZE)
executor = ThreadPoolExecutor(max_workers=WORKER_COUNT)


# ================= WORKER ================= #
def worker():
    """Queue dan xabar olib, thread-safe yuboradi"""
    while True:
        try:
            user_id, text, markup = message_queue.get()
            bot.send_message(user_id, text, reply_markup=markup)
        except Exception as e:
            print(f"[❌] Worker error: {e}")
        finally:
            message_queue.task_done()


# ================= INIT WORKERS ================= #
for _ in range(WORKER_COUNT):
    t = Thread(target=worker, daemon=True)
    t.start()


# ================= SEND MSG ================= #
def send_msg(slug: str,
             msg: Message | CallbackQuery,
             buttons: list | None = None,
             markup=None,
             **kwargs):
    """
    Xabarni queue ga joylab yuboradi.
    Resursni tejash uchun sinxron, ThreadPool ishlatadi.
    """
    try:
        user_id = msg.from_user.id
        lang = BotUserService.get_lang(user_id) or "en"
        text = BotMessage.get_txt(lang, slug, **kwargs) if kwargs else BotMessage.get_txt(lang, slug)

        if not buttons:
            markup_instance = ReplyKeyboardRemove()
        else:
            markup_instance = markup(lang, buttons) if markup else None

        try:
            message_queue.put((user_id, text, markup_instance), timeout=QUEUE_TIMEOUT)
        except Full:
            # Queue to'liq bo'lsa, xabar tashlanmaydi, RAM tejaydi
            print("[⚠️] Queue is full — skipping message")

    except Exception as e:
        print(f"[❌] send_msg error: {e}")
