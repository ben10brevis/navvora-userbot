import asyncio

from userbot.core import BOT_MARK, cat_cmd, edit_delete


@cat_cmd("purge", command=("purge", "Reply to a message: delete everything from it to the latest"))
async def purge(event):
    reply = await event.get_reply_message()
    if not reply:
        return await edit_delete(event, "`Reply to the message to start purging from.`")
    ids = [m.id async for m in event.client.iter_messages(event.chat_id, min_id=reply.id - 1)]
    await event.client.delete_messages(event.chat_id, ids)
    note = await event.respond(BOT_MARK + f"`Purged {len(ids)} messages.`")
    await asyncio.sleep(3)
    await note.delete()


@cat_cmd("del", command=("del", "Reply to a message to delete it"))
async def delete_msg(event):
    reply = await event.get_reply_message()
    if not reply:
        return await edit_delete(event, "`Reply to a message to delete it.`")
    await reply.delete()
    await event.delete()


@cat_cmd("sd", command=("sd <seconds> <text>", "Send a self-destructing message"))
async def self_destruct(event):
    args = (event.pattern_match.group(1) or "").split(" ", 1)
    if len(args) < 2 or not args[0].isdigit():
        return await edit_delete(event, "`Usage: sd <seconds> <text>`")
    seconds, text = int(args[0]), args[1]
    await event.edit(text)
    await asyncio.sleep(seconds)
    await event.delete()
