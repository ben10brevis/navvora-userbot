from userbot.core import cat_cmd, db, edit_delete, edit_or_reply


@cat_cmd("save", command=("save <name> [text|reply]", "Save a note"))
async def save(event):
    parts = (event.pattern_match.group(1) or "").split(" ", 1)
    name = parts[0].lower()
    reply = await event.get_reply_message()
    text = parts[1] if len(parts) > 1 else ((reply.raw_text if reply else "") or "")
    if not name or not text:
        return await edit_delete(event, "`Usage: save <name> <text>  (or reply to a message)`")
    notes = db.get("notes", {})
    notes[name] = text
    db.put("notes", notes)
    await edit_delete(event, f"`Saved note '{name}'.`")


@cat_cmd("get", command=("get <name>", "Show a saved note"))
async def get_note(event):
    name = (event.pattern_match.group(1) or "").strip().lower()
    text = db.get("notes", {}).get(name)
    if not text:
        return await edit_delete(event, "`Note not found.`")
    await edit_or_reply(event, text, parse_mode=None)


@cat_cmd("notes", command=("notes", "List saved notes"))
async def list_notes(event):
    notes = db.get("notes", {})
    if not notes:
        return await edit_delete(event, "`No notes saved.`")
    await edit_or_reply(event, "**Notes:**\n" + "\n".join(f"• `{n}`" for n in sorted(notes)))


@cat_cmd("clear", command=("clear <name>", "Delete a note"))
async def clear_note(event):
    name = (event.pattern_match.group(1) or "").strip().lower()
    notes = db.get("notes", {})
    if name not in notes:
        return await edit_delete(event, "`Note not found.`")
    notes.pop(name)
    db.put("notes", notes)
    await edit_delete(event, f"`Deleted note '{name}'.`")
