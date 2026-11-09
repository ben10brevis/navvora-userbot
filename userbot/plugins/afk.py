import asyncio
import time

from telethon import events

from userbot import Config, bot
from userbot.core import BOT_MARK, cat_cmd, edit_delete, time_formatter

AFK = {"on": False, "reason": "", "since": 0.0, "replied": set()}


@cat_cmd("afk", command=("afk [reason]", "Go AFK; auto-reply to PMs and mentions until you send a message"))
async def afk_on(event):
    reason = (event.pattern_match.group(1) or "").strip()
    AFK.update(on=True, reason=reason, since=time.time(), replied=set())
    await edit_delete(event, "`I'm AFK now.`" + (f"\n**Reason:** {reason}" if reason else ""))


@bot.on(events.NewMessage(outgoing=True))
async def back_online(event):
    if AFK["on"] and not (event.raw_text or "").lower().startswith(f"{Config.HANDLER}afk"):
        AFK["on"] = False
        note = await event.respond("`I'm back online!`")
        await asyncio.sleep(3)
        await note.delete()


@bot.on(events.NewMessage(incoming=True))
async def afk_reply(event):
    if not AFK["on"] or not (event.is_private or event.mentioned):
        return
    sender = await event.get_sender()
    if not sender or getattr(sender, "bot", False) or event.chat_id in AFK["replied"]:
        return
    AFK["replied"].add(event.chat_id)
    text = BOT_MARK + f"**I'm AFK** (since `{time_formatter(time.time() - AFK['since'])}`)"
    if AFK["reason"]:
        text += f"\n**Reason:** {AFK['reason']}"
    await event.reply(text)
