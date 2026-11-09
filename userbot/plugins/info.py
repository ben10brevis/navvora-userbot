from telethon.tl.functions.users import GetFullUserRequest

from userbot.core import cat_cmd, edit_delete, edit_or_reply, get_user_from_event


@cat_cmd("id", command=("id", "Get chat / user / message IDs (reply for the user's ID)"), allow_sudo=True)
async def get_id(event):
    reply = await event.get_reply_message()
    text = f"**Chat ID:** `{event.chat_id}`\n"
    if reply:
        text += f"**User ID:** `{reply.sender_id}`\n**Message ID:** `{reply.id}`"
    else:
        text += f"**Your ID:** `{event.sender_id}`"
    await edit_or_reply(event, text)


@cat_cmd("info", command=("info [reply|@user|id]", "Show details about a user"), allow_sudo=True)
async def info(event):
    args = (event.pattern_match.group(1) or "").strip()
    user = await get_user_from_event(event, args) or await event.client.get_me()
    full = await event.client(GetFullUserRequest(user.id))
    about = getattr(full.full_user, "about", None) or "—"
    await edit_or_reply(
        event,
        f"**User info**\n\n"
        f"**Name:** {user.first_name or ''} {user.last_name or ''}\n"
        f"**Username:** @{user.username or '—'}\n"
        f"**ID:** `{user.id}`\n"
        f"**Bot:** `{bool(user.bot)}`\n"
        f"**Bio:** {about}",
    )
