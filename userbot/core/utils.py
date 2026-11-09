import asyncio
import re

import aiohttp

# Invisible marker put at the start of the bot's own automatic messages so
# auto-approve logic can tell them apart from messages you typed yourself.
BOT_MARK = "\u2063"
HEADERS = {"User-Agent": "NavvoraUserBot/1.0"}


async def edit_or_reply(event, text, parse_mode="md", link_preview=False, delete_after=None):
    """Edit your own message, or reply if the command came from a sudo user."""
    if event.out:
        msg = await event.edit(text, parse_mode=parse_mode, link_preview=link_preview)
    else:
        msg = await event.reply(text, parse_mode=parse_mode, link_preview=link_preview)
    if delete_after:
        await asyncio.sleep(delete_after)
        await msg.delete()
    return msg


async def edit_delete(event, text, delete_after=5, **kwargs):
    return await edit_or_reply(event, text, delete_after=delete_after, **kwargs)


def time_formatter(seconds: float) -> str:
    seconds = int(seconds)
    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, secs = divmod(rem, 60)
    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    parts.append(f"{secs}s")
    return " ".join(parts)


def parse_duration(text: str):
    """'10m' -> 600, '2h' -> 7200, '45' -> 45 (seconds). None if invalid."""
    m = re.fullmatch(r"(\d+)\s*([smhd]?)", (text or "").strip().lower())
    if not m:
        return None
    return int(m.group(1)) * {"": 1, "s": 1, "m": 60, "h": 3600, "d": 86400}[m.group(2)]


async def fetch(url, params=None, as_json=True, method="GET", data=None):
    async with aiohttp.ClientSession(headers=HEADERS, timeout=aiohttp.ClientTimeout(total=20)) as s:
        async with s.request(method, url, params=params, data=data) as r:
            if r.status != 200:
                raise RuntimeError(f"HTTP {r.status}")
            return await (r.json(content_type=None) if as_json else r.text())


async def get_user_from_event(event, args: str = ""):
    """Resolve a user from a reply, or from an @username / ID in args."""
    reply = await event.get_reply_message()
    if reply and reply.sender_id:
        return await reply.get_sender()
    args = (args or "").strip().split(" ")[0]
    if not args:
        return None
    try:
        return await event.client.get_entity(int(args) if args.lstrip("-").isdigit() else args)
    except Exception:  # noqa: BLE001
        return None
