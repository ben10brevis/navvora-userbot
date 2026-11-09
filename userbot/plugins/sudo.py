from userbot.core import cat_cmd, db, edit_delete, edit_or_reply, get_user_from_event


@cat_cmd("addsudo", command=("addsudo [reply|@user]", "Let someone use harmless commands (alive, ping, calc, weather...)"))
async def addsudo(event):
    user = await get_user_from_event(event, event.pattern_match.group(1))
    if not user:
        return await edit_delete(event, "`Reply to a user or give @username / ID.`")
    ids = db.get("sudo", [])
    if user.id not in ids:
        ids.append(user.id)
        db.put("sudo", ids)
    await edit_delete(event, f"`{user.first_name} is now a sudo user.`")


@cat_cmd("delsudo", command=("delsudo [reply|@user]", "Remove a sudo user"))
async def delsudo(event):
    user = await get_user_from_event(event, event.pattern_match.group(1))
    if not user:
        return await edit_delete(event, "`Reply to a user or give @username / ID.`")
    ids = db.get("sudo", [])
    if user.id in ids:
        ids.remove(user.id)
        db.put("sudo", ids)
    await edit_delete(event, f"`{user.first_name} removed from sudo.`")


@cat_cmd("sudolist", command=("sudolist", "List sudo users"))
async def sudolist(event):
    ids = db.get("sudo", [])
    await edit_or_reply(event, "**Sudo users:**\n" + ("\n".join(f"• `{i}`" for i in ids) or "`None`"))
