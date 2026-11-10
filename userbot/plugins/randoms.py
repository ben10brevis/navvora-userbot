from userbot.core import cat_cmd, edit_delete, edit_or_reply, fetch


async def _text(event, url, build):
    try:
        data = await fetch(url)
        text = build(data)
    except Exception:  # noqa: BLE001
        return await edit_delete(event, "`Could not fetch that right now.`")
    await edit_or_reply(event, text, parse_mode=None)


@cat_cmd("joke", command=("joke", "Random joke"), allow_sudo=True)
async def joke(event):
    await _text(event, "https://official-joke-api.appspot.com/random_joke",
                lambda d: f"{d['setup']}\n\n{d['punchline']}")


@cat_cmd("fact", command=("fact", "Random fact"), allow_sudo=True)
async def fact(event):
    await _text(event, "https://uselessfacts.jsph.pl/api/v2/facts/random?language=en", lambda d: d["text"])


@cat_cmd("quote", command=("quote", "Random quote"), allow_sudo=True)
async def quote(event):
    await _text(event, "https://zenquotes.io/api/random", lambda d: f"“{d[0]['q']}”\n— {d[0]['a']}")


@cat_cmd("advice", command=("advice", "Random advice"), allow_sudo=True)
async def advice(event):
    await _text(event, "https://api.adviceslip.com/advice", lambda d: d["slip"]["advice"])


async def _image(event, url, pick):
    try:
        link = pick(await fetch(url))
    except Exception:  # noqa: BLE001
        return await edit_delete(event, "`Could not fetch that right now.`")
    await event.delete()
    await event.client.send_file(event.chat_id, link)


@cat_cmd("cat", command=("cat", "Random cat picture"))
async def cat(event):
    await _image(event, "https://api.thecatapi.com/v1/images/search", lambda d: d[0]["url"])


@cat_cmd("dog", command=("dog", "Random dog picture"))
async def dog(event):
    await _image(event, "https://dog.ceo/api/breeds/image/random", lambda d: d["message"])
