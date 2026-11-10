from telethon import events

from userbot import bot
from userbot.core import cat_cmd, db, edit_delete, edit_or_reply


@cat_cmd("setwelcome", command=("setwelcome <text>", "Welcome new members here. Use {name} {mention} {chat}"))
async def set_welcome(event):
    text = (event.pattern_match.group(1) or "").strip()
    if not text:
        return await edit_delete(event, "`Usage: setwelcome Welcome {mention} to {chat}!`")
    data = db.get("welcome", {})
    data[str(event.chat_id)] = text
    db.put("welcome", data)
    await edit_delete(event, "`Welcome message set.`")


@cat_cmd("clearwelcome", command=("clearwelcome", "Remove the welcome message for this chat"))
async def clear_welcome(event):
    data = db.get("welcome", {})
    data.pop(str(event.chat_id), None)
    db.put("welcome", data)
    await edit_delete(event, "`Welcome message removed.`")


@cat_cmd("welcome", command=("welcome", "Show this chat's welcome message"))
async def show_welcome(event):
    text = db.get("welcome", {}).get(str(event.chat_id))
    await edit_or_reply(event, text or "`No welcome message set.`", parse_mode=None)


@bot.on(events.ChatAction)
async def greet(event):
    if not (event.user_joined or event.user_added):
        return
    text = db.get("welcome", {}).get(str(event.chat_id))
    if not text:
        return
    user = await event.get_user()
    if not user or user.bot:
        return
    chat = await event.get_chat()
    out = (
        text.replace("{name}", user.first_name or "")
        .replace("{mention}", f"[{user.first_name}](tg://user?id={user.id})")
        .replace("{chat}", getattr(chat, "title", "") or "")
    )
    await event.reply(out)
