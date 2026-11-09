import platform
import sys
import time

import psutil

from userbot import START_TIME
from userbot.core import cat_cmd, edit_or_reply, time_formatter


@cat_cmd("sysd", command=("sysd", "System stats of the machine running the bot"))
async def sysd(event):
    mem, disk = psutil.virtual_memory(), psutil.disk_usage("/")
    await edit_or_reply(
        event,
        f"**System**\n\n**OS:** `{platform.system()} {platform.release()}`\n"
        f"**Python:** `{sys.version.split()[0]}`\n"
        f"**CPU:** `{psutil.cpu_percent(interval=0.5)}%` ({psutil.cpu_count()} cores)\n"
        f"**RAM:** `{mem.percent}%` of `{mem.total // 2**20} MB`\n"
        f"**Disk:** `{disk.percent}%` of `{disk.total // 2**30} GB`\n"
        f"**Bot uptime:** `{time_formatter(time.time() - START_TIME)}`",
    )
