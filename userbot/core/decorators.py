import inspect
import re
import traceback
from pathlib import Path

from telethon import events

from .. import HELP, LOGS, Config, bot
from .db import get as db_get


def sudo_ids() -> set:
    return set(Config.SUDO_USERS) | set(db_get("sudo", []))


def cat_cmd(pattern: str, command: tuple = None, allow_sudo: bool = False):
    """Register a command plugin handler.

    pattern     regex for the command name, e.g. "ping" (no prefix, no groups)
    command     (name, description) shown in the help menu
    allow_sudo  also let sudo users (.addsudo) run it - only use for harmless commands
    Arguments: (event.pattern_match.group(1) or "").strip()
    """
    plugin = Path(inspect.stack()[1].filename).stem
    if command:
        HELP.setdefault(plugin, {})[f"{Config.HANDLER}{command[0]}"] = command[1]

    regex = re.compile(
        rf"^{re.escape(Config.HANDLER)}(?:{pattern})(?:\s+([\s\S]*))?$",
        re.IGNORECASE,
    )

    def decorator(func):
        async def wrapper(event):
            try:
                await func(event)
            except events.StopPropagation:
                raise
            except Exception:  # noqa: BLE001
                LOGS.error("Error in plugin %s:\n%s", plugin, traceback.format_exc())
                try:
                    await event.client.send_message(
                        "me",
                        f"**Error in `{plugin}`**\n```{traceback.format_exc()[-3500:]}```",
                    )
                except Exception:  # noqa: BLE001
                    pass

        async def sudo_wrapper(event):
            if event.sender_id in sudo_ids():
                await wrapper(event)

        bot.add_event_handler(wrapper, events.NewMessage(outgoing=True, pattern=regex))
        if allow_sudo:
            bot.add_event_handler(sudo_wrapper, events.NewMessage(incoming=True, pattern=regex))
        return wrapper

    return decorator
