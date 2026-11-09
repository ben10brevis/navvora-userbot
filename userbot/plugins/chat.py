from telethon.tl.functions.messages import ExportChatInviteRequest
from telethon.tl.types import ChannelParticipantsAdmins, ChannelParticipantsBots

from userbot.core import cat_cmd, edit_delete, edit_or_reply


@cat_cmd("chatinfo", command=("chatinfo", "Info about the current chat"), allow_sudo=True)
async def chatinfo(event):
    chat = await event.get_chat()
    title = getattr(chat, "title", None) or getattr(chat, "first_name", "-")
    try:
        total = (await event.client.get_participants(chat, limit=0)).total
    except Exception:  # noqa: BLE001
        total = "?"
    await edit_or_reply(
        event,
        f"**Chat info**\n\n**Title:** {title}\n**ID:** `{event.chat_id}`\n"
        f"**Username:** @{getattr(chat, 'username', None) or '—'}\n**Members:** `{total}`",
    )


@cat_cmd("admins", command=("admins", "List admins of this group"), allow_sudo=True)
async def admins(event):
    if event.is_private:
        return await edit_delete(event, "`Use this in a group.`")
    lines = []
    async for u in event.client.iter_participants(event.chat_id, filter=ChannelParticipantsAdmins):
        lines.append(f"• [{u.first_name}](tg://user?id={u.id})" + (" 🤖" if u.bot else ""))
    await edit_or_reply(event, "**Admins:**\n" + ("\n".join(lines) or "`None`"))


@cat_cmd("bots", command=("bots", "List bots in this group"), allow_sudo=True)
async def bots(event):
    if event.is_private:
        return await edit_delete(event, "`Use this in a group.`")
    lines = []
    async for u in event.client.iter_participants(event.chat_id, filter=ChannelParticipantsBots):
        lines.append(f"• @{u.username or u.first_name}")
    await edit_or_reply(event, "**Bots:**\n" + ("\n".join(lines) or "`None`"), parse_mode=None)


@cat_cmd("link", command=("link", "Get / create an invite link for this chat"))
async def link(event):
    if event.is_private:
        return await edit_delete(event, "`Use this in a group or channel.`")
    try:
        res = await event.client(ExportChatInviteRequest(event.chat_id))
    except Exception as e:  # noqa: BLE001
        return await edit_delete(event, f"`Failed (admin rights needed?): {e}`")
    await edit_or_reply(event, res.link, parse_mode=None, link_preview=False)


@cat_cmd("leave", command=("leave", "Leave this group / channel"))
async def leave(event):
    if event.is_private:
        return await edit_delete(event, "`Use this in a group or channel.`")
    await edit_or_reply(event, "`Leaving...`")
    await event.client.delete_dialog(event.chat_id)


@cat_cmd("archive", command=("archive", "Archive this chat"))
async def archive(event):
    await event.client.edit_folder(event.chat_id, 1)
    await edit_delete(event, "`Archived.`")


@cat_cmd("unarchive", command=("unarchive", "Move this chat out of the archive"))
async def unarchive(event):
    await event.client.edit_folder(event.chat_id, 0)
    await edit_delete(event, "`Unarchived.`")


@cat_cmd("read", command=("read", "Mark this chat as read"))
async def read(event):
    await event.client.send_read_acknowledge(event.chat_id)
    await edit_delete(event, "`Marked as read.`")
