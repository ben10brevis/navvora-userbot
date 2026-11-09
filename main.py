import sys

from userbot import LOGS, Config, bot
from userbot.core.loader import load_plugins
from userbot.keepalive import start_keepalive

if not Config.API_ID or not Config.API_HASH:
    LOGS.error("APP_ID / API_HASH missing. Fill in your .env file (see .env.example).")
    sys.exit(1)

bot.loop.run_until_complete(start_keepalive())  # only if PORT is set (Render etc.)
bot.start()
me = bot.loop.run_until_complete(bot.get_me())
LOGS.info("Logged in as %s (%s)", me.first_name, me.id)

loaded = load_plugins("plugins")
LOGS.info("Loaded %d plugins: %s", len(loaded), ", ".join(loaded))

try:
    bot.loop.run_until_complete(
        bot.send_message(
            "me",
            f"**Navvora UserBot started** ✅\nPlugins: `{len(loaded)}` | Type `{Config.HANDLER}help`",
        )
    )
except Exception as e:  # noqa: BLE001
    LOGS.warning("Could not send start message: %s", e)

bot.run_until_disconnected()
