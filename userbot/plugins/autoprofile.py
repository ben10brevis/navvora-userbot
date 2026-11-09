import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo

from telethon.tl.functions.account import UpdateProfileRequest

from userbot import LOGS, Config, bot
from userbot.core import cat_cmd, db, edit_delete

_tasks = {}


def _now():
    return datetime.now(ZoneInfo(Config.TIMEZONE)).strftime("%I:%M %p")


async def _run(kind: str):
    while True:
        cfg = db.get(f"auto{kind}")
        if not cfg:
            break
        try:
            if kind == "name":
                await bot(UpdateProfileRequest(first_name=f"{cfg['base']} | {_now()}"[:64]))
            else:
                await bot(UpdateProfileRequest(about=f"{cfg['base']} | {_now()}"[:70]))
        except Exception as e:  # noqa: BLE001
            LOGS.warning("auto%s update failed: %s", kind, e)
        await asyncio.sleep(60)


def _start(kind: str):
    old = _tasks.get(kind)
    if old:
        old.cancel()
    _tasks[kind] = bot.loop.create_task(_run(kind))


async def _stop(event, kind: str):
    cfg = db.get(f"auto{kind}")
    db.remove(f"auto{kind}")
    task = _tasks.pop(kind, None)
    if task:
        task.cancel()
    if cfg:
        field = {"first_name": cfg["base"]} if kind == "name" else {"about": cfg["base"]}
        await event.client(UpdateProfileRequest(**field))


@cat_cmd("autoname", command=("autoname on|off", "Show the time in your first name (updates every minute)"))
async def autoname(event):
    arg = (event.pattern_match.group(1) or "").strip().lower()
    if arg == "on":
        if not db.get("autoname"):
            me = await event.client.get_me()
            db.put("autoname", {"base": (me.first_name or "").split(" | ")[0]})
        _start("name")
        return await edit_delete(event, "`Auto name on.`")
    if arg == "off":
        await _stop(event, "name")
        return await edit_delete(event, "`Auto name off, name restored.`")
    await edit_delete(event, "`Usage: autoname on|off`")


@cat_cmd("autobio", command=("autobio on <text> | off", "Show the time in your bio (updates every minute)"))
async def autobio(event):
    arg = (event.pattern_match.group(1) or "").strip()
    if arg.lower() == "off":
        await _stop(event, "bio")
        return await edit_delete(event, "`Auto bio off, bio restored.`")
    if arg.lower().startswith("on") and arg[2:].strip():
        db.put("autobio", {"base": arg[2:].strip()[:50]})
        _start("bio")
        return await edit_delete(event, "`Auto bio on.`")
    await edit_delete(event, "`Usage: autobio on <text>  |  autobio off`")


for _kind in ("name", "bio"):
    if db.get(f"auto{_kind}"):
        _start(_kind)
