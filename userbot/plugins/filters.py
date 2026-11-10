import re

from telethon import events

from userbot import bot
from userbot.core import BOT_MARK, cat_cmd, db, edit_delete, edit_or_reply


def _key(chat_id):
    return f"filters:{chat_id}"


@cat_cmd("filter", command=("filter <word> <reply text>", "Auto-reply when someone says <word> in this chat"))
async def add_filter(event):
    parts = (event.pattern_match.group(1) or "").split(" ", 1)
    reply = await event.get_reply_message()
    word = parts[0].lower()
    text = parts[1] if len(parts) > 1 else ((reply.raw_text if reply else "") or "")
    if not word or not text:
        return await edit_delete(event, "`Usage: filter <word> <reply text>`")
    data = db.get(_key(event.chat_id), {})
    data[word] = text
    db.put(_key(event.chat_id), data)
    await edit_delete(event, f"`Filter '{word}' added.`")


@cat_cmd("stop", command=("stop <word>", "Remove a filter from this chat"))
async def stop_filter(event):
    word = (event.pattern_match.group(1) or "").strip().lower()
    data = db.get(_key(event.chat_id), {})
    if word not in data:
        return await edit_delete(event, "`Filter not found.`")
    data.pop(word)
    db.put(_key(event.chat_id), data)
    await edit_delete(event, f"`Filter '{word}' removed.`")


@cat_cmd("filters", command=("filters", "List filters in this chat"))
async def list_filters(event):
    data = db.get(_key(event.chat_id), {})
    if not data:
        return await edit_delete(event, "`No filters in this chat.`")
    await edit_or_reply(event, "**Filters:**\n" + "\n".join(f"• `{w}`" for w in sorted(data)))


@bot.on(events.NewMessage(incoming=True))
async def trigger(event):
    data = db.get(_key(event.chat_id))
    if not data or not event.raw_text:
        return
    text = event.raw_text.lower()
    for word, reply in data.items():
        if re.search(rf"(?<!\w){re.escape(word)}(?!\w)", text):
            await event.reply(BOT_MARK + reply)
            break
