from userbot.core import cat_cmd, edit_delete, get_user_from_event


@cat_cmd("pin", command=("pin", "Reply to a message to pin it (silently)"))
async def pin(event):
    reply = await event.get_reply_message()
    if not reply:
        return await edit_delete(event, "`Reply to a message to pin it.`")
    await event.client.pin_message(event.chat_id, reply.id, notify=False)
    await edit_delete(event, "`Pinned.`")


@cat_cmd("unpin", command=("unpin", "Reply to unpin one message; no reply unpins all"))
async def unpin(event):
    reply = await event.get_reply_message()
    await event.client.unpin_message(event.chat_id, reply.id if reply else None)
    await edit_delete(event, "`Unpinned.`")


@cat_cmd("kick", command=("kick [reply|@user]", "Kick a user from the group"))
async def kick(event):
    user = await get_user_from_event(event, event.pattern_match.group(1))
    if not user:
        return await edit_delete(event, "`Reply to a user or give @username / ID.`")
    await event.client.kick_participant(event.chat_id, user.id)
    await edit_delete(event, f"`Kicked {user.first_name}.`")


@cat_cmd("ban", command=("ban [reply|@user]", "Ban a user from the group"))
async def ban(event):
    user = await get_user_from_event(event, event.pattern_match.group(1))
    if not user:
        return await edit_delete(event, "`Reply to a user or give @username / ID.`")
    await event.client.edit_permissions(event.chat_id, user.id, view_messages=False)
    await edit_delete(event, f"`Banned {user.first_name}.`")


@cat_cmd("unban", command=("unban [reply|@user]", "Unban a user"))
async def unban(event):
    user = await get_user_from_event(event, event.pattern_match.group(1))
    if not user:
        return await edit_delete(event, "`Reply to a user or give @username / ID.`")
    await event.client.edit_permissions(event.chat_id, user.id, view_messages=True)
    await edit_delete(event, f"`Unbanned {user.first_name}.`")
