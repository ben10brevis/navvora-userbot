import time

from telethon import events

from userbot import bot
from userbot.core import cat_cmd, db, edit_delete

DEFAULT_REPLY = (
    "Thanks for your message! I've received it and will get back to you "
    "as soon as I can."
)
REPLY_COOLDOWN = 6 * 60 * 60  # one automatic reply per person every six hours


def _settings():
    return db.get(
        "pm_manager",
        {"on": False, "reply": DEFAULT_REPLY, "last_reply": {}},
    )


@cat_cmd(
    "pmmanager",
    command=("pmmanager on|off|status", "Enable, disable or check PM auto-replies"),
)
async def pmmanager(event):
    arg = (event.pattern_match.group(1) or "").strip().lower()
    cfg = _settings()

    if arg == "on":
        cfg["on"] = True
        db.put("pm_manager", cfg)
        return await edit_delete(event, "`PM Manager enabled.`")

    if arg == "off":
        cfg["on"] = False
        db.put("pm_manager", cfg)
        return await edit_delete(event, "`PM Manager disabled.`")

    if arg == "status":
        state = "ON" if cfg.get("on") else "OFF"
        reply = cfg.get("reply") or DEFAULT_REPLY
        return await edit_delete(
            event,
            f"**PM Manager:** `{state}`\n"
            f"**Reply cooldown:** `6 hours per person`\n"
            f"**Auto-reply:** {reply}",
        )

    await edit_delete(event, "`Usage: .pmmanager on|off|status`")


@cat_cmd(
    "pmreply",
    command=("pmreply <text|reset>", "Set the PM auto-reply message or reset it"),
)
async def set_pm_reply(event):
    value = (event.pattern_match.group(1) or "").strip()
    if not value:
        return await edit_delete(event, "`Usage: .pmreply <message|reset>`")

    cfg = _settings()
    if value.lower() == "reset":
        cfg["reply"] = DEFAULT_REPLY
        db.put("pm_manager", cfg)
        return await edit_delete(event, "`PM auto-reply reset to default.`")

    if len(value) > 1000:
        return await edit_delete(event, "`Keep the auto-reply under 1000 characters.`")

    cfg["reply"] = value
    db.put("pm_manager", cfg)
    await edit_delete(event, "`PM auto-reply message updated.`")


@bot.on(events.NewMessage(incoming=True))
async def pm_auto_reply(event):
    if not event.is_private:
        return

    cfg = _settings()
    if not cfg.get("on"):
        return

    sender = await event.get_sender()
    if (
        not sender
        or getattr(sender, "bot", False)
        or sender.id in (777000, (await event.client.get_me()).id)
    ):
        return

    now = time.time()
    last_reply = cfg.setdefault("last_reply", {})
    last = float(last_reply.get(str(sender.id), 0) or 0)
    if now - last < REPLY_COOLDOWN:
        return

    reply = (cfg.get("reply") or DEFAULT_REPLY).strip()
    if not reply:
        reply = DEFAULT_REPLY

    # Persist the cooldown before sending so rapid incoming messages cannot
    # trigger duplicate replies if Telegram delivers several updates together.
    last_reply[str(sender.id)] = now
    cutoff = now - (7 * 24 * 60 * 60)
    cfg["last_reply"] = {
        user_id: timestamp
        for user_id, timestamp in last_reply.items()
        if float(timestamp or 0) >= cutoff
    }
    db.put("pm_manager", cfg)
    await event.reply(reply)
