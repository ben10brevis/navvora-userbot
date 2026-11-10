import os

from telethon.tl.functions.account import UpdateProfileRequest, UpdateUsernameRequest
from telethon.tl.functions.photos import UploadProfilePhotoRequest

from userbot.core import cat_cmd, edit_delete


@cat_cmd("setname", command=("setname First | Last", "Change your profile name"))
async def setname(event):
    arg = (event.pattern_match.group(1) or "").strip()
    if not arg:
        return await edit_delete(event, "`Usage: setname First | Last`")
    first, _, last = arg.partition("|")
    await event.client(UpdateProfileRequest(first_name=first.strip(), last_name=last.strip()))
    await edit_delete(event, "`Name updated.`")


@cat_cmd("setbio", command=("setbio <text>", "Change your bio"))
async def setbio(event):
    bio = (event.pattern_match.group(1) or "").strip()
    await event.client(UpdateProfileRequest(about=bio[:70]))
    await edit_delete(event, "`Bio updated.`")


@cat_cmd("setusername", command=("setusername <name>", "Change your @username"))
async def setusername(event):
    name = (event.pattern_match.group(1) or "").strip().lstrip("@")
    try:
        await event.client(UpdateUsernameRequest(name))
    except Exception as e:  # noqa: BLE001
        return await edit_delete(event, f"`Failed: {e}`")
    await edit_delete(event, f"`Username set to @{name}.`")


@cat_cmd("setpic", command=("setpic", "Reply to a photo to set it as your profile picture"))
async def setpic(event):
    reply = await event.get_reply_message()
    if not reply or not reply.photo:
        return await edit_delete(event, "`Reply to a photo.`")
    path = await reply.download_media("data/")
    try:
        await event.client(UploadProfilePhotoRequest(file=await event.client.upload_file(path)))
    finally:
        os.remove(path)
    await edit_delete(event, "`Profile picture updated.`")
