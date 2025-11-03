from queue import Queue, Full
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
from telebot.types import Message, CallbackQuery
from bot_app.repo.user_service import BotUserService
from msg_app.models import BotMessage
from bot_app.passenger_bot.core.loader import bot

# ================= GLOBAL SETTINGS ================= #
MAX_QUEUE_SIZE = 3_000
WORKER_COUNT = 2
QUEUE_TIMEOUT = 0.01

# ================= QUEUE & THREADPOOL ================= #
edit_queue = Queue(maxsize=MAX_QUEUE_SIZE)
executor = ThreadPoolExecutor(max_workers=WORKER_COUNT)


# ================= WORKER ================= #
def edit_worker():
    while True:
        try:
            chat_id, message_id, text, markup, _ = edit_queue.get()
            try:
                bot.edit_message_text(text, chat_id, message_id, reply_markup=markup)
            except Exception as e:
                print(f"[❌] edit_message error: {e}")
        except Exception as e:
            print(f"[❌] Worker error: {e}")
        finally:
            edit_queue.task_done()


for _ in range(WORKER_COUNT):
    t = Thread(target=edit_worker, daemon=True)
    t.start()


# ================= EDIT MSG ================= #
def edit_msg(
        slug: str,
        obj: Message | CallbackQuery,
        buttons: list | None = None,
        markup=None,
        **kwargs):
    """
    Message yoki CallbackQuery obyekti asosida xabarni tahrirlash.
    Thread-safe va resursni tejaydi.
    """
    try:
        if isinstance(obj, Message):
            chat_id = obj.chat.id
            message_id = obj.message_id
        elif isinstance(obj, CallbackQuery):
            chat_id = obj.message.chat.id
            message_id = obj.message.message_id
        else:
            raise ValueError("obj must be Message or CallbackQuery")

        lang = BotUserService.get_lang(chat_id)
        text = BotMessage.get_txt(lang, slug, **kwargs) if kwargs else BotMessage.get_txt(lang, slug)
        markup_instance = markup(lang, buttons) if markup else None

        try:
            edit_queue.put((chat_id, message_id, text, markup_instance, "edit"), timeout=QUEUE_TIMEOUT)
        except Full:
            print("[⚠️] Edit queue is full — skipping message edit")

    except Exception as e:
        print(f"[❌] edit_msg error: {e}")
