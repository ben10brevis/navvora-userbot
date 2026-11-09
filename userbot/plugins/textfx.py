import asyncio

from userbot.core import cat_cmd, edit_delete, edit_or_reply


async def _text(event):
    args = (event.pattern_match.group(1) or "").strip()
    if not args:
        reply = await event.get_reply_message()
        args = (reply.raw_text if reply else "") or ""
    return args


async def _apply(event, fn):
    text = await _text(event)
    if not text:
        return await edit_delete(event, "`Give some text or reply to a message.`")
    await edit_or_reply(event, fn(text), parse_mode=None)


@cat_cmd("mock", command=("mock <text|reply>", "mOcKiNg tExT"))
async def mock(event):
    await _apply(event, lambda t: "".join(c.upper() if i % 2 else c.lower() for i, c in enumerate(t)))


@cat_cmd("vapor", command=("vapor <text|reply>", "ｖａｐｏｒｗａｖｅ text"))
async def vapor(event):
    def conv(t):
        return "".join(chr(ord(c) + 0xFEE0) if 0x21 <= ord(c) <= 0x7E else c for c in t)

    await _apply(event, conv)


@cat_cmd("clap", command=("clap <text|reply>", "Add 👏 between words"))
async def clap(event):
    await _apply(event, lambda t: "👏 " + " 👏 ".join(t.split()) + " 👏")


@cat_cmd("reverse", command=("reverse <text|reply>", "Reverse text"))
async def reverse(event):
    await _apply(event, lambda t: t[::-1])


@cat_cmd("owo", command=("owo <text|reply>", "owo-ify text"))
async def owo(event):
    def conv(t):
        t = t.replace("r", "w").replace("l", "w").replace("R", "W").replace("L", "W")
        return t.replace("na", "nya").replace("no", "nyo") + " owo"

    await _apply(event, conv)


@cat_cmd("type", command=("type <text>", "Typewriter effect (max 60 chars)"))
async def type_effect(event):
    text = (event.pattern_match.group(1) or "").strip()[:60]
    if not text:
        return await edit_delete(event, "`Usage: type <text>`")
    buf = ""
    for ch in text:
        buf += ch
        await event.edit(buf + "█", parse_mode=None)
        await asyncio.sleep(0.3)
    await event.edit(buf, parse_mode=None)
