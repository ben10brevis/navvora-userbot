from telethon import events
from telethon.tl.functions.contacts import BlockRequest, UnblockRequest

from userbot import Config, bot
from userbot.core import BOT_MARK, cat_cmd, db, edit_delete, get_user_from_event

MAX_WARNS = 3
_me = None


def _cfg():
    return db.get("pm", {"on": False, "approved": [], "warns": {}})


async def _my_id(client):
    global _me
    if _me is None:
        _me = (await client.get_me()).id
    return _me


async def _target(event):
    user = await get_user_from_event(event, event.pattern_match.group(1))
    if not user and event.is_private:
        user = await event.get_chat()
    return user


@cat_cmd("pmguard", command=("pmguard on|off", "Warn & block unapproved people who PM you"))
async def toggle(event):
    arg = (event.pattern_match.group(1) or "").strip().lower()
    if arg not in ("on", "off"):
        return await edit_delete(event, "`Usage: pmguard on|off`")
    cfg = _cfg()
    cfg["on"] = arg == "on"
    db.put("pm", cfg)
    await edit_delete(event, f"`PM guard {arg}.`")


@cat_cmd("approve", command=("approve [reply|@user]", "Approve a user to PM you"))
async def approve(event):
    user = await _target(event)
    if not user:
        return await edit_delete(event, "`Reply to a user, give @username, or use in their PM.`")
    cfg = _cfg()
    if user.id not in cfg["approved"]:
        cfg["approved"].append(user.id)
    cfg["warns"].pop(str(user.id), None)
    db.put("pm", cfg)
    await edit_delete(event, f"`Approved {user.first_name}.`")


@cat_cmd("disapprove", command=("disapprove [reply|@user]", "Remove a user's approval"))
async def disapprove(event):
    user = await _target(event)
    if not user:
        return await edit_delete(event, "`Reply to a user, give @username, or use in their PM.`")
    cfg = _cfg()
    if user.id in cfg["approved"]:
        cfg["approved"].remove(user.id)
    db.put("pm", cfg)
    await edit_delete(event, f"`Disapproved {user.first_name}.`")


@cat_cmd("block", command=("block [reply|@user]", "Block a user"))
async def block(event):
    user = await _target(event)
    if not user:
        return await edit_delete(event, "`Reply to a user, give @username, or use in their PM.`")
    await event.client(BlockRequest(user.id))
    await edit_delete(event, f"`Blocked {user.first_name}.`")


@cat_cmd("unblock", command=("unblock [reply|@user]", "Unblock a user"))
async def unblock(event):
    user = await _target(event)
    if not user:
        return await edit_delete(event, "`Reply to a user or give @username / ID.`")
    await event.client(UnblockRequest(user.id))
    await edit_delete(event, f"`Unblocked {user.first_name}.`")


@bot.on(events.NewMessage(incoming=True))
async def guard(event):
    if not event.is_private:
        return
    cfg = _cfg()
    if not cfg["on"]:
        return
    sender = await event.get_sender()
    if (
        not sender
        or getattr(sender, "bot", False)
        or getattr(sender, "contact", False)
        or sender.id == 777000
        or sender.id in cfg["approved"]
    ):
        return
    n = cfg["warns"].get(str(sender.id), 0) + 1
    if n >= MAX_WARNS:
        cfg["warns"].pop(str(sender.id), None)
        db.put("pm", cfg)
        await event.reply(BOT_MARK + "`Too many messages without approval. You are blocked.`")
        await event.client(BlockRequest(sender.id))
        return
    cfg["warns"][str(sender.id)] = n
    db.put("pm", cfg)
    await event.reply(
        BOT_MARK + f"**I only chat with approved people. Please wait for a reply.**\nWarning `{n}/{MAX_WARNS}`"
    )


@bot.on(events.NewMessage(outgoing=True))
async def auto_approve(event):
    """If you message someone first, approve them automatically."""
    if not event.is_private:
        return
    text = event.raw_text or ""
    if text.startswith(Config.HANDLER) or text.startswith(BOT_MARK):
        return
    cfg = _cfg()
    if not cfg["on"] or event.chat_id in cfg["approved"] or event.chat_id == await _my_id(event.client):
        return
    cfg["approved"].append(event.chat_id)
    cfg["warns"].pop(str(event.chat_id), None)
    db.put("pm", cfg)
