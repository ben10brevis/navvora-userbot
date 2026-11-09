import asyncio

from telethon.tl.functions.messages import EditChatDefaultBannedRightsRequest
from telethon.tl.types import ChatBannedRights

from userbot.core import cat_cmd, db, edit_delete, edit_or_reply, get_user_from_event

WARN_LIMIT = 3
FIELDS = [
    "view_messages", "send_messages", "send_media", "send_stickers", "send_gifs",
    "send_games", "send_inline", "embed_links", "send_polls", "change_info",
    "invite_users", "pin_messages",
]
LOCKS = {
    "all": ["send_messages"], "media": ["send_media"], "stickers": ["send_stickers", "send_gifs"],
    "polls": ["send_polls"], "links": ["embed_links"], "invite": ["invite_users"],
    "pin": ["pin_messages"], "info": ["change_info"],
}


async def _user_and_rest(event):
    args = (event.pattern_match.group(1) or "").strip()
    reply = await event.get_reply_message()
    if reply and reply.sender_id:
        return await reply.get_sender(), args
    first, _, rest = args.partition(" ")
    return await get_user_from_event(event, first), rest


async def _need_group(event):
    if event.is_private:
        await edit_delete(event, "`Use this in a group.`")
        return False
    return True


@cat_cmd("mute", command=("mute [reply|@user]", "Stop a user from sending messages"))
async def mute(event):
    if not await _need_group(event):
        return
    user, _ = await _user_and_rest(event)
    if not user:
        return await edit_delete(event, "`Reply to a user or give @username / ID.`")
    await event.client.edit_permissions(event.chat_id, user.id, send_messages=False)
    await edit_delete(event, f"`Muted {user.first_name}.`")


@cat_cmd("unmute", command=("unmute [reply|@user]", "Let a user send messages again"))
async def unmute(event):
    if not await _need_group(event):
        return
    user, _ = await _user_and_rest(event)
    if not user:
        return await edit_delete(event, "`Reply to a user or give @username / ID.`")
    await event.client.edit_permissions(event.chat_id, user.id, send_messages=True)
    await edit_delete(event, f"`Unmuted {user.first_name}.`")


@cat_cmd("promote", command=("promote [reply|@user] [title]", "Make a user admin"))
async def promote(event):
    if not await _need_group(event):
        return
    user, title = await _user_and_rest(event)
    if not user:
        return await edit_delete(event, "`Reply to a user or give @username / ID.`")
    await event.client.edit_admin(
        event.chat_id, user.id, delete_messages=True, ban_users=True,
        invite_users=True, pin_messages=True, title=title or "Admin",
    )
    await edit_delete(event, f"`Promoted {user.first_name}.`")


@cat_cmd("demote", command=("demote [reply|@user]", "Remove admin rights"))
async def demote(event):
    if not await _need_group(event):
        return
    user, _ = await _user_and_rest(event)
    if not user:
        return await edit_delete(event, "`Reply to a user or give @username / ID.`")
    await event.client.edit_admin(event.chat_id, user.id, is_admin=False)
    await edit_delete(event, f"`Demoted {user.first_name}.`")


@cat_cmd("warn", command=("warn [reply|@user] [reason]", f"Warn a user; {WARN_LIMIT} warns = ban"))
async def warn(event):
    if not await _need_group(event):
        return
    user, reason = await _user_and_rest(event)
    if not user:
        return await edit_delete(event, "`Reply to a user or give @username / ID.`")
    key = f"warns:{event.chat_id}"
    data = db.get(key, {})
    n = data.get(str(user.id), 0) + 1
    if n >= WARN_LIMIT:
        data.pop(str(user.id), None)
        db.put(key, data)
        await event.client.edit_permissions(event.chat_id, user.id, view_messages=False)
        return await edit_or_reply(event, f"`{user.first_name} reached {WARN_LIMIT} warnings and was banned.`")
    data[str(user.id)] = n
    db.put(key, data)
    await edit_or_reply(
        event, f"⚠️ **{user.first_name}** warned (`{n}/{WARN_LIMIT}`)" + (f"\n**Reason:** {reason}" if reason else ""),
    )


@cat_cmd("warns", command=("warns [reply|@user]", "Show a user's warnings"))
async def warns(event):
    user, _ = await _user_and_rest(event)
    if not user:
        return await edit_delete(event, "`Reply to a user or give @username / ID.`")
    n = db.get(f"warns:{event.chat_id}", {}).get(str(user.id), 0)
    await edit_or_reply(event, f"**{user.first_name}** has `{n}/{WARN_LIMIT}` warnings.")


@cat_cmd("resetwarns", command=("resetwarns [reply|@user]", "Clear a user's warnings"))
async def resetwarns(event):
    user, _ = await _user_and_rest(event)
    if not user:
        return await edit_delete(event, "`Reply to a user or give @username / ID.`")
    key = f"warns:{event.chat_id}"
    data = db.get(key, {})
    data.pop(str(user.id), None)
    db.put(key, data)
    await edit_delete(event, f"`Warnings cleared for {user.first_name}.`")


@cat_cmd("setrules", command=("setrules <text>", "Set the rules for this group"))
async def setrules(event):
    text = (event.pattern_match.group(1) or "").strip()
    if not text:
        return await edit_delete(event, "`Usage: setrules <text>`")
    rules = db.get("rules", {})
    rules[str(event.chat_id)] = text
    db.put("rules", rules)
    await edit_delete(event, "`Rules saved.`")


@cat_cmd("rules", command=("rules", "Show the rules for this group"), allow_sudo=True)
async def rules(event):
    text = db.get("rules", {}).get(str(event.chat_id))
    await edit_or_reply(event, text or "`No rules set.`", parse_mode=None)


async def _set_lock(event, lock: bool):
    if not await _need_group(event):
        return
    what = (event.pattern_match.group(1) or "").strip().lower()
    if what not in LOCKS:
        return await edit_delete(event, f"`Usage: {'lock' if lock else 'unlock'} {' | '.join(LOCKS)}`")
    chat = await event.get_chat()
    current = chat.default_banned_rights
    rights = {f: bool(getattr(current, f, False)) for f in FIELDS}
    for f in LOCKS[what]:
        rights[f] = lock
    await event.client(
        EditChatDefaultBannedRightsRequest(event.chat_id, ChatBannedRights(until_date=None, **rights))
    )
    await edit_delete(event, f"`{'Locked' if lock else 'Unlocked'} {what}.`")


@cat_cmd("lock", command=("lock <all|media|stickers|polls|links|invite|pin|info>", "Restrict members"))
async def lock(event):
    await _set_lock(event, True)


@cat_cmd("unlock", command=("unlock <type>", "Lift a restriction"))
async def unlock(event):
    await _set_lock(event, False)


@cat_cmd("zombies", command=("zombies [clean]", "Find (or remove) deleted accounts in this group"))
async def zombies(event):
    if not await _need_group(event):
        return
    deleted = [u async for u in event.client.iter_participants(event.chat_id) if u.deleted]
    if not deleted:
        return await edit_delete(event, "`No deleted accounts found.`")
    if (event.pattern_match.group(1) or "").strip().lower() != "clean":
        return await edit_or_reply(event, f"`Found {len(deleted)} deleted accounts. Use zombies clean to remove them.`")
    await edit_or_reply(event, f"`Removing {len(deleted)} deleted accounts...`")
    removed = 0
    for u in deleted:
        try:
            await event.client.kick_participant(event.chat_id, u.id)
            removed += 1
        except Exception:  # noqa: BLE001
            pass
        await asyncio.sleep(1)
    await edit_or_reply(event, f"`Removed {removed} deleted accounts.`")
