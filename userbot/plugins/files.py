import os
from pathlib import Path

from userbot.core import cat_cmd, edit_delete, edit_or_reply

DL_DIR = "data/downloads/"


@cat_cmd("dl", command=("dl", "Reply to media to download it to data/downloads/"))
async def download(event):
    reply = await event.get_reply_message()
    if not reply or not reply.media:
        return await edit_delete(event, "`Reply to a media message.`")
    Path(DL_DIR).mkdir(parents=True, exist_ok=True)
    await edit_or_reply(event, "`Downloading...`")
    path = await reply.download_media(DL_DIR)
    await edit_or_reply(event, f"`Saved to {path}`")


@cat_cmd("ul", command=("ul <path>", "Upload a local file from the bot's machine"))
async def upload(event):
    path = (event.pattern_match.group(1) or "").strip()
    if not path or not os.path.isfile(path):
        return await edit_delete(event, "`File not found.`")
    await edit_or_reply(event, "`Uploading...`")
    await event.client.send_file(event.chat_id, path, force_document=True)
    await event.delete()


@cat_cmd("rename", command=("rename <new name.ext>", "Reply to a file to resend it under a new name"))
async def rename(event):
    new = (event.pattern_match.group(1) or "").strip()
    reply = await event.get_reply_message()
    if not new or not reply or not reply.media:
        return await edit_delete(event, "`Reply to a file: rename <new name.ext>`")
    new = os.path.basename(new)
    Path(DL_DIR).mkdir(parents=True, exist_ok=True)
    await edit_or_reply(event, "`Working...`")
    path = await reply.download_media(DL_DIR)
    target = os.path.join(DL_DIR, new)
    os.replace(path, target)
    try:
        await event.client.send_file(event.chat_id, target, force_document=True, reply_to=reply.id)
    finally:
        os.remove(target)
    await event.delete()


@cat_cmd("json", command=("json", "Reply to a message to get its raw JSON"))
async def to_json(event):
    reply = await event.get_reply_message()
    if not reply:
        return await edit_delete(event, "`Reply to a message.`")
    text = reply.stringify()
    if len(text) < 3500:
        return await edit_or_reply(event, f"```{text}```")
    Path("data").mkdir(exist_ok=True)
    Path("data/message.json").write_text(text)
    await event.client.send_file(event.chat_id, "data/message.json", reply_to=reply.id)
    await event.delete()
