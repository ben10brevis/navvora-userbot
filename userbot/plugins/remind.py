import asyncio

from userbot.core import cat_cmd, edit_delete, parse_duration


@cat_cmd("remind", command=("remind <10m|2h|1d> <text>", "Remind you in Saved Messages (lost on restart)"))
async def remind(event):
    parts = (event.pattern_match.group(1) or "").split(" ", 1)
    seconds = parse_duration(parts[0]) if parts else None
    if not seconds or len(parts) < 2 or seconds > 7 * 86400:
        return await edit_delete(event, "`Usage: remind 10m take out the trash  (max 7d)`")
    text, client = parts[1], event.client

    async def _later():
        await asyncio.sleep(seconds)
        await client.send_message("me", f"⏰ **Reminder:** {text}")

    asyncio.create_task(_later())
    await edit_delete(event, f"`Okay, I'll remind you in {parts[0]}.`")
