import random

from telethon.tl.types import InputMediaDice

from userbot import Config
from userbot.core import cat_cmd, edit_delete, edit_or_reply

DICE = {"dice": "🎲", "dart": "🎯", "basket": "🏀", "football": "⚽", "slot": "🎰", "bowl": "🎳"}


@cat_cmd(
    "dice|dart|basket|football|slot|bowl",
    command=("dice | dart | basket | football | slot | bowl", "Send an animated Telegram dice"),
)
async def dice(event):
    name = event.raw_text[len(Config.HANDLER):].split()[0].lower()
    reply = await event.get_reply_message()
    await event.delete()
    await event.client.send_file(
        event.chat_id, InputMediaDice(DICE[name]), reply_to=reply.id if reply else None
    )


@cat_cmd("coin", command=("coin", "Flip a coin"), allow_sudo=True)
async def coin(event):
    await edit_or_reply(event, f"🪙 **{random.choice(['Heads', 'Tails'])}**")


@cat_cmd("roll", command=("roll [max]", "Random number from 1 to max (default 100)"), allow_sudo=True)
async def roll(event):
    arg = (event.pattern_match.group(1) or "100").strip()
    if not arg.isdigit() or int(arg) < 1:
        return await edit_delete(event, "`Usage: roll [max]`")
    await edit_or_reply(event, f"🎲 **{random.randint(1, int(arg))}** (1-{arg})")


@cat_cmd("choose", command=("choose a | b | c", "Pick a random option"), allow_sudo=True)
async def choose(event):
    options = [o.strip() for o in (event.pattern_match.group(1) or "").split("|") if o.strip()]
    if len(options) < 2:
        return await edit_delete(event, "`Usage: choose a | b | c`")
    await edit_or_reply(event, f"🎯 **{random.choice(options)}**", parse_mode=None)
