import os
from pathlib import Path

from PIL import Image

from userbot.core import cat_cmd, edit_delete, edit_or_reply, get_user_from_event

TMP = "data/tmp/"


@cat_cmd("stoi", command=("stoi", "Reply to a sticker to get it as a PNG image"))
async def sticker_to_image(event):
    reply = await event.get_reply_message()
    if not reply or not reply.sticker:
        return await edit_delete(event, "`Reply to a sticker.`")
    if reply.file.mime_type != "image/webp":
        return await edit_delete(event, "`Animated/video stickers are not supported.`")
    Path(TMP).mkdir(parents=True, exist_ok=True)
    src = await reply.download_media(TMP)
    out = os.path.splitext(src)[0] + ".png"
    try:
        Image.open(src).convert("RGBA").save(out, "PNG")
        await event.client.send_file(event.chat_id, out, force_document=False, reply_to=reply.id)
    finally:
        for f in (src, out):
            if os.path.exists(f):
                os.remove(f)
    await event.delete()


@cat_cmd("itos", command=("itos", "Reply to an image to get it as a sticker"))
async def image_to_sticker(event):
    reply = await event.get_reply_message()
    if not reply or not (reply.photo or (reply.file and (reply.file.mime_type or "").startswith("image/"))):
        return await edit_delete(event, "`Reply to an image.`")
    Path(TMP).mkdir(parents=True, exist_ok=True)
    src = await reply.download_media(TMP)
    out = os.path.splitext(src)[0] + ".webp"
    try:
        img = Image.open(src).convert("RGBA")
        img.thumbnail((512, 512))
        img.save(out, "WEBP")
        await event.client.send_file(event.chat_id, out, reply_to=reply.id)
    finally:
        for f in (src, out):
            if os.path.exists(f):
                os.remove(f)
    await event.delete()


@cat_cmd("pfp", command=("pfp [reply|@user]", "Get someone's profile picture"), allow_sudo=True)
async def pfp(event):
    user = await get_user_from_event(event, event.pattern_match.group(1)) or await event.client.get_me()
    Path(TMP).mkdir(parents=True, exist_ok=True)
    path = await event.client.download_profile_photo(user, TMP)
    if not path:
        return await edit_delete(event, "`No profile picture.`")
    try:
        await event.client.send_file(event.chat_id, path, caption=f"**{user.first_name}**")
    finally:
        os.remove(path)
    await event.delete()
