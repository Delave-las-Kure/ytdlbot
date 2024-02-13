#!/usr/local/bin/python3
# coding: utf-8

# ytdlbot - constant.py
# 8/16/21 16:59
#

__author__ = "Benny <benny.think@gmail.com>"

import os
import io
import string
import logging

from config import (
    AFD_LINK,
    COFFEE_LINK,
    ENABLE_CELERY,
    FREE_DOWNLOAD,
    REQUIRED_MEMBERSHIP,
    TOKEN_PRICE,
)
from database import InfluxDB
from utils import get_func_queue, get_text_from_file

const_dic = {
    "AFD_LINK": AFD_LINK,
    "COFFEE_LINK": COFFEE_LINK,
    "ENABLE_CELERY": ENABLE_CELERY,
    "FREE_DOWNLOAD": FREE_DOWNLOAD,
    "REQUIRED_MEMBERSHIP": REQUIRED_MEMBERSHIP,
    "TOKEN_PRICE": TOKEN_PRICE,
}

class BotText:
    custom_text = os.getenv("CUSTOM_TEXT", "")

    start = get_text_from_file("../texts/start").format(**const_dic)
    help = get_text_from_file("../texts/help").format(**const_dic)
    about =  get_text_from_file("../texts/about").format(**const_dic)
    buy =  get_text_from_file("../texts/buy").format(**const_dic)
    private = get_text_from_file("../texts/private").format(**const_dic)
    membership_require = get_text_from_file("../texts/membership_require").format(**const_dic)
    settings = get_text_from_file("../texts/settings")
    premium_warning = get_text_from_file("../texts/premium_warning").format(**const_dic)

    @staticmethod
    def get_receive_link_text() -> str:
        reserved = get_func_queue("reserved")
        if ENABLE_CELERY and reserved:
            text = f"Your tasks was added to the reserved queue {reserved}. Processing...\n\n"
        else:
            text = "Your task was added to active queue.\nProcessing...\n\n"

        return text

    @staticmethod
    def ping_worker() -> str:
        from tasks import app as celery_app

        workers = InfluxDB().extract_dashboard_data()
        # [{'celery@BennyのMBP': 'abc'}, {'celery@BennyのMBP': 'abc'}]
        response = celery_app.control.broadcast("ping_revision", reply=True)
        revision = {}
        for item in response:
            revision.update(item)

        text = ""
        for worker in workers:
            fields = worker["fields"]
            hostname = worker["tags"]["hostname"]
            status = {True: "✅"}.get(fields["status"], "❌")
            active = fields["active"]
            load = "{},{},{}".format(fields["load1"], fields["load5"], fields["load15"])
            rev = revision.get(hostname, "")
            text += f"{status}{hostname} **{active}** {load} {rev}\n"

        return text
