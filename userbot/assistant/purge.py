import asyncio
import io
import re
from collections import defaultdict
from datetime import datetime
from typing import Optional, Union

from telethon import Button, events
from telethon.errors import UserIsBlockedError
from telethon.events import CallbackQuery, StopPropagation
from telethon.utils import get_display_name

from userbot import Config, legend

from ..core import check_owner, pool
from ..core.logger import logging
from ..core.session import tgbot
from ..helpers import reply_id
from ..helpers.utils import _format
from ..sql_helper.bot_blacklists import check_is_black_list
from ..sql_helper.bot_pms_sql import (
    add_user_to_db,
    get_user_id,
    get_user_logging,
    get_user_reply,
)
from ..sql_helper.bot_starters import add_starter_to_db, get_starter_details
from ..sql_helper.globals import delgvar, gvarstatus
from ..sql_helper.idaddar import get_all_users
from . import BOTLOG, BOTLOG_CHATID
from .botmanagers import ban_user_from_bot

LOGS = logging.getLogger(__name__)

menu_category = "bot"
botusername = Config.BOT_USERNAME
from telethon import events
from telethon.errors.rpcerrorlist import MessageDeleteForbiddenError
from telethon.tl.types import ChannelParticipantsAdmins

async def is_administrator(user_id: int, message):
    admin = False
    async for user in tgbot.iter_participants(
        message.chat_id, filter=ChannelParticipantsAdmins
    ):
        if user_id == user.id or OWNER_ID or SUDO_USERS:
            admin = True
            break
    return admin

@legend.bot_cmd(
    pattern=f"^/purge({botusername})?([\s]+)?$",
    incoming=True,
)
async def purge(event):
    chat = event.chat_id
    msgs = []

    if not await is_administrator(user_id=event.sender_id, message=event):
        await event.reply("You're not an admin!")
        return
    msg = await event.get_reply_message()
    if not msg:
        await event.reply("Reply to a message to select where to start purging from.")
        return
    try:
        msg_id = msg.id
        count = 0
        to_delete = event.message.id - 1
        await tgbot.delete_messages(chat, event.message.id)
        msgs.append(event.reply_to_msg_id)
        for m_id in range(to_delete, msg_id - 1, -1):
            msgs.append(m_id)
            count += 1
            if len(msgs) == 100:
                await event.client.delete_messages(chat, msgs)
                msgs = []

        await event.client.delete_messages(chat, msgs)
        del_res = await event.client.send_message(
            event.chat_id, f"Fast Purged {count} messages."
        )

        await asyncio.sleep(4)
        await del_res.delete()

    except MessageDeleteForbiddenError:
        text = "Failed to delete messages.\n"
        text += "Messages maybe too old or I'm not admin! or dont have delete rights!"
        del_res = await respond(text, parse_mode="md")
        await asyncio.sleep(5)
        await del_res.delete()


@legend.bot_cmd(
    pattern=f"^/del({botusername})?([\s]+)?$",
    incoming=True,
)
async def delete_msg(event):
    if not await is_administrator(user_id=event.sender_id, message=event):
        await event.reply("You're not an admin!")
        return
    chat = event.chat_id
    msg = await event.get_reply_message()
    if not msg:
        await event.reply("Reply to some message to delete it.")
        return
    to_delete = event.message
    chat = await event.get_input_chat()
    rm = [msg, to_delete]
    await event.delete.delete_messages(chat, rm)






