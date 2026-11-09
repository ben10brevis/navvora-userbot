import asyncio
from urllib.parse import quote

from deep_translator import GoogleTranslator

from userbot.core import cat_cmd, edit_delete, edit_or_reply, fetch


async def _need(event, usage):
    arg = (event.pattern_match.group(1) or "").strip()
    if not arg:
        reply = await event.get_reply_message()
        arg = (reply.raw_text if reply else "") or ""
    if not arg:
        await edit_delete(event, f"`Usage: {usage}`")
    return arg


@cat_cmd("weather", command=("weather <city>", "Current weather (wttr.in)"), allow_sudo=True)
async def weather(event):
    city = await _need(event, "weather <city>")
    if not city:
        return
    try:
        text = await fetch(f"https://wttr.in/{quote(city)}?format=4", as_json=False)
    except Exception as e:  # noqa: BLE001
        return await edit_delete(event, f"`Failed: {e}`")
    await edit_or_reply(event, f"🌤 {text.strip()}", parse_mode=None)


@cat_cmd("ud", command=("ud <term>", "Urban Dictionary lookup"), allow_sudo=True)
async def urban(event):
    term = await _need(event, "ud <term>")
    if not term:
        return
    try:
        data = await fetch("https://api.urbandictionary.com/v0/define", params={"term": term})
        item = data["list"][0]
    except Exception:  # noqa: BLE001
        return await edit_delete(event, "`No result.`")
    clean = lambda s: s.replace("[", "").replace("]", "")  # noqa: E731
    await edit_or_reply(
        event,
        f"**{term}**\n\n{clean(item['definition'])[:1500]}\n\n__{clean(item.get('example', ''))[:500]}__",
        parse_mode=None,
    )


@cat_cmd("define", command=("define <word>", "English dictionary"), allow_sudo=True)
async def define(event):
    word = await _need(event, "define <word>")
    if not word:
        return
    try:
        data = await fetch(f"https://api.dictionaryapi.dev/api/v2/entries/en/{quote(word)}")
        lines = []
        for meaning in data[0]["meanings"][:3]:
            d = meaning["definitions"][0]["definition"]
            lines.append(f"• ({meaning['partOfSpeech']}) {d}")
    except Exception:  # noqa: BLE001
        return await edit_delete(event, "`No result.`")
    await edit_or_reply(event, f"{word}\n\n" + "\n".join(lines), parse_mode=None)


@cat_cmd("wiki", command=("wiki <topic>", "Wikipedia summary"), allow_sudo=True)
async def wiki(event):
    topic = await _need(event, "wiki <topic>")
    if not topic:
        return
    try:
        data = await fetch(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(topic.replace(' ', '_'))}"
        )
        text = f"{data['title']}\n\n{data['extract'][:1800]}\n\n{data['content_urls']['desktop']['page']}"
    except Exception:  # noqa: BLE001
        return await edit_delete(event, "`No article found.`")
    await edit_or_reply(event, text, parse_mode=None)


@cat_cmd("tr", command=("tr <lang> <text|reply>", "Translate (e.g. tr te Hello)"), allow_sudo=True)
async def translate(event):
    args = (event.pattern_match.group(1) or "").strip().split(" ", 1)
    reply = await event.get_reply_message()
    if not args or not args[0]:
        return await edit_delete(event, "`Usage: tr <lang code> <text>  (or reply)`")
    lang = args[0]
    text = args[1] if len(args) > 1 else ((reply.raw_text if reply else "") or "")
    if not text:
        return await edit_delete(event, "`No text to translate.`")
    try:
        out = await asyncio.to_thread(GoogleTranslator(source="auto", target=lang).translate, text)
    except Exception as e:  # noqa: BLE001
        return await edit_delete(event, f"`Translation failed: {e}`")
    await edit_or_reply(event, f"{out}", parse_mode=None)


@cat_cmd("crypto", command=("crypto <coin id>", "Price in USD (e.g. crypto bitcoin)"), allow_sudo=True)
async def crypto(event):
    coin = (await _need(event, "crypto bitcoin")).lower()
    if not coin:
        return
    try:
        data = await fetch(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": coin, "vs_currencies": "usd", "include_24hr_change": "true"},
        )
        price, change = data[coin]["usd"], data[coin]["usd_24h_change"]
    except Exception:  # noqa: BLE001
        return await edit_delete(event, "`Coin not found (use the CoinGecko id, e.g. bitcoin).`")
    await edit_or_reply(event, f"🪙 {coin}: ${price:,} ({change:+.2f}% 24h)", parse_mode=None)


@cat_cmd("cur", command=("cur <amount> <from> <to>", "Currency convert (cur 10 usd inr)"), allow_sudo=True)
async def currency(event):
    parts = (event.pattern_match.group(1) or "").split()
    if len(parts) != 3:
        return await edit_delete(event, "`Usage: cur 10 usd inr`")
    try:
        amount, a, b = float(parts[0]), parts[1].upper(), parts[2].upper()
        data = await fetch(f"https://open.er-api.com/v6/latest/{a}")
        result = amount * data["rates"][b]
    except Exception:  # noqa: BLE001
        return await edit_delete(event, "`Conversion failed (check currency codes).`")
    await edit_or_reply(event, f"💱 {amount:g} {a} = {result:,.2f} {b}", parse_mode=None)


@cat_cmd("github", command=("github <username>", "GitHub profile info"), allow_sudo=True)
async def github(event):
    user = await _need(event, "github <username>")
    if not user:
        return
    try:
        d = await fetch(f"https://api.github.com/users/{quote(user)}")
    except Exception:  # noqa: BLE001
        return await edit_delete(event, "`User not found.`")
    await edit_or_reply(
        event,
        f"{d['login']} ({d.get('name') or '-'})\n"
        f"Bio: {d.get('bio') or '-'}\n"
        f"Repos: {d['public_repos']} | Followers: {d['followers']} | Following: {d['following']}\n"
        f"{d['html_url']}",
        parse_mode=None,
    )


@cat_cmd("qr", command=("qr <text>", "Generate a QR code"))
async def qr(event):
    text = await _need(event, "qr <text>")
    if not text:
        return
    url = f"https://api.qrserver.com/v1/create-qr-code/?size=400x400&data={quote(text)}"
    await event.delete()
    await event.client.send_file(event.chat_id, url, caption=f"QR: {text[:100]}")


@cat_cmd("paste", command=("paste <text|reply>", "Paste text to dpaste.org"))
async def paste(event):
    text = await _need(event, "paste <text> (or reply)")
    if not text:
        return
    try:
        link = await fetch(
            "https://dpaste.org/api/", method="POST",
            data={"content": text, "expiry_days": 7}, as_json=False,
        )
    except Exception as e:  # noqa: BLE001
        return await edit_delete(event, f"`Paste failed: {e}`")
    await edit_or_reply(event, f"📋 {link.strip()}", parse_mode=None, link_preview=True)
