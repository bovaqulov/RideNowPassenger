import time

from ...core.loader import bot
from ...functions.text_sender import send_msg
from ...functions.utils import del_msg


def search_driver(call, state):
    time.sleep(15)
    del_msg(bot, call)
    return send_msg(
        "driver_found",
        call,
        [["call_driver"], ["message_driver"],["cancel"]]

    )
