import time
from datetime import datetime

from telethon import __version__ as telethon_version

from userbot import START_TIME, Config
from userbot.core import cat_cmd, edit_or_reply, time_formatter


@cat_cmd("alive", command=("alive", "Check whether Navvora UserBot is running"), allow_sudo=True)
async def alive(event):
    me = await event.client.get_me()
    name = Config.ALIVE_NAME or me.first_name
    caption = (
        f"**Navvora UserBot is alive** ✅\n\n"
        f"**Owner:** {name}\n"
        f"**Uptime:** `{time_formatter(time.time() - START_TIME)}`\n"
        f"**Telethon:** `{telethon_version}`"
    )
    if Config.ALIVE_PIC and event.out:
        try:
            await event.client.send_file(event.chat_id, Config.ALIVE_PIC, caption=caption)
            return await event.delete()
        except Exception:  # noqa: BLE001
            pass  # fall back to a text reply
    await edit_or_reply(event, caption)


@cat_cmd("ping", command=("ping", "Check response latency"), allow_sudo=True)
async def ping(event):
    start = datetime.now()
    msg = await edit_or_reply(event, "`Pong!`")
    ms = (datetime.now() - start).total_seconds() * 1000
    await msg.edit(f"🏓 **Pong!** `{ms:.2f} ms`")
