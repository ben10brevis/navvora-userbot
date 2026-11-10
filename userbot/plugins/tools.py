import base64
import calendar
import hashlib
import secrets
import string
from datetime import datetime
from urllib.parse import quote
from zoneinfo import ZoneInfo

from userbot import Config
from userbot.core import cat_cmd, edit_delete, edit_or_reply, fetch

MORSE = {
    "a": ".-", "b": "-...", "c": "-.-.", "d": "-..", "e": ".", "f": "..-.", "g": "--.", "h": "....",
    "i": "..", "j": ".---", "k": "-.-", "l": ".-..", "m": "--", "n": "-.", "o": "---", "p": ".--.",
    "q": "--.-", "r": ".-.", "s": "...", "t": "-", "u": "..-", "v": "...-", "w": ".--", "x": "-..-",
    "y": "-.--", "z": "--..", "0": "-----", "1": ".----", "2": "..---", "3": "...--", "4": "....-",
    "5": ".....", "6": "-....", "7": "--...", "8": "---..", "9": "----.",
}


def _arg(event):
    return (event.pattern_match.group(1) or "").strip()


async def _arg_or_reply(event, usage):
    text = _arg(event)
    if not text:
        reply = await event.get_reply_message()
        text = (reply.raw_text if reply else "") or ""
    if not text:
        await edit_delete(event, f"`Usage: {usage}`")
    return text


@cat_cmd("ip", command=("ip <ip|domain>", "IP / domain lookup"), allow_sudo=True)
async def ip(event):
    q = _arg(event)
    if not q:
        return await edit_delete(event, "`Usage: ip 8.8.8.8`")
    try:
        d = await fetch(f"http://ip-api.com/json/{quote(q)}")
        if d.get("status") != "success":
            raise ValueError
    except Exception:  # noqa: BLE001
        return await edit_delete(event, "`Lookup failed.`")
    await edit_or_reply(
        event,
        f"IP: {d['query']}\nCountry: {d['country']}\nRegion: {d['regionName']}\n"
        f"City: {d['city']}\nISP: {d['isp']}\nOrg: {d['org']}",
        parse_mode=None,
    )


@cat_cmd("time", command=("time [Zone/Name]", "Current time (default: your TIMEZONE)"), allow_sudo=True)
async def time_cmd(event):
    zone = _arg(event) or Config.TIMEZONE
    try:
        now = datetime.now(ZoneInfo(zone))
    except Exception:  # noqa: BLE001
        return await edit_delete(event, "`Unknown zone. Example: Asia/Kolkata, America/New_York`")
    await edit_or_reply(event, f"🕒 {zone}\n{now:%A, %d %B %Y\n%I:%M:%S %p}", parse_mode=None)


@cat_cmd("cal", command=("cal [month year]", "Show a calendar"), allow_sudo=True)
async def cal(event):
    parts = _arg(event).split()
    now = datetime.now()
    try:
        month, year = (int(parts[0]), int(parts[1])) if len(parts) == 2 else (now.month, now.year)
        text = calendar.month(year, month)
    except Exception:  # noqa: BLE001
        return await edit_delete(event, "`Usage: cal 11 2026`")
    await edit_or_reply(event, f"```{text}```")


@cat_cmd("short", command=("short <url>", "Shorten a link (is.gd)"))
async def short(event):
    url = _arg(event)
    if not url:
        return await edit_delete(event, "`Usage: short https://example.com/long`")
    try:
        out = await fetch("https://is.gd/create.php", params={"format": "simple", "url": url}, as_json=False)
    except Exception:  # noqa: BLE001
        return await edit_delete(event, "`Could not shorten that link.`")
    await edit_or_reply(event, out.strip(), parse_mode=None)


@cat_cmd("b64e", command=("b64e <text|reply>", "Base64 encode"), allow_sudo=True)
async def b64e(event):
    text = await _arg_or_reply(event, "b64e <text>")
    if text:
        await edit_or_reply(event, f"`{base64.b64encode(text.encode()).decode()}`")


@cat_cmd("b64d", command=("b64d <text|reply>", "Base64 decode"), allow_sudo=True)
async def b64d(event):
    text = await _arg_or_reply(event, "b64d <text>")
    if not text:
        return
    try:
        out = base64.b64decode(text.encode(), validate=True).decode()
    except Exception:  # noqa: BLE001
        return await edit_delete(event, "`Invalid Base64.`")
    await edit_or_reply(event, out, parse_mode=None)


@cat_cmd("hash", command=("hash <md5|sha1|sha256|sha512> <text>", "Hash some text"), allow_sudo=True)
async def hash_cmd(event):
    algo, _, text = _arg(event).partition(" ")
    if algo.lower() not in ("md5", "sha1", "sha256", "sha512") or not text:
        return await edit_delete(event, "`Usage: hash sha256 hello`")
    await edit_or_reply(event, f"`{hashlib.new(algo.lower(), text.encode()).hexdigest()}`")


@cat_cmd("pass", command=("pass [length]", "Generate a strong password (8-64)"))
async def password(event):
    arg = _arg(event) or "16"
    if not arg.isdigit() or not 8 <= int(arg) <= 64:
        return await edit_delete(event, "`Length must be 8-64.`")
    chars = string.ascii_letters + string.digits + "!@#$%^&*-_"
    await edit_or_reply(event, f"`{''.join(secrets.choice(chars) for _ in range(int(arg)))}`")


@cat_cmd("morse", command=("morse <text|reply>", "Text to Morse code"), allow_sudo=True)
async def morse(event):
    text = await _arg_or_reply(event, "morse <text>")
    if text:
        out = " / ".join(" ".join(MORSE.get(c, "?") for c in w) for w in text.lower().split())
        await edit_or_reply(event, f"`{out}`")


@cat_cmd("bin", command=("bin <text|reply>", "Text to binary"), allow_sudo=True)
async def to_bin(event):
    text = await _arg_or_reply(event, "bin <text>")
    if text:
        await edit_or_reply(event, f"`{' '.join(format(ord(c), '08b') for c in text)[:3500]}`")


@cat_cmd("unbin", command=("unbin <binary>", "Binary to text"), allow_sudo=True)
async def from_bin(event):
    text = await _arg_or_reply(event, "unbin 01001000 01101001")
    if not text:
        return
    try:
        out = "".join(chr(int(b, 2)) for b in text.split())
    except Exception:  # noqa: BLE001
        return await edit_delete(event, "`Invalid binary.`")
    await edit_or_reply(event, out, parse_mode=None)
