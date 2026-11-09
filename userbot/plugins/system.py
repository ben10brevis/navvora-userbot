import asyncio
import importlib
import os
import sys
from pathlib import Path

from userbot.core import cat_cmd, edit_delete, edit_or_reply

PLUGIN_DIR = Path(__file__).resolve().parent


@cat_cmd("restart", command=("restart", "Restart the userbot"))
async def restart(event):
    await edit_or_reply(event, "`Restarting...`")
    await event.client.disconnect()
    os.execl(sys.executable, sys.executable, *sys.argv)


@cat_cmd("shutdown", command=("shutdown", "Stop the userbot"))
async def shutdown(event):
    await edit_or_reply(event, "`Shutting down...`")
    await event.client.disconnect()


@cat_cmd("install", command=("install", "Reply to a .py file to install it as a plugin"))
async def install(event):
    reply = await event.get_reply_message()
    if not reply or not reply.file or not (reply.file.name or "").endswith(".py"):
        return await edit_delete(event, "`Reply to a .py plugin file.`")
    path = Path(await reply.download_media(file=str(PLUGIN_DIR) + os.sep))
    try:
        module = f"userbot.plugins.{path.stem}"
        if module in sys.modules:
            importlib.reload(sys.modules[module])
        else:
            importlib.import_module(module)
    except Exception as e:  # noqa: BLE001
        path.unlink(missing_ok=True)
        return await edit_delete(event, f"`Install failed:` {e}", delete_after=10)
    await edit_delete(event, f"`Installed plugin {path.stem}.`")


@cat_cmd("uninstall", command=("uninstall <plugin>", "Delete a plugin file (restart to unload)"))
async def uninstall(event):
    name = (event.pattern_match.group(1) or "").strip().replace(".py", "")
    path = PLUGIN_DIR / f"{name}.py"
    if not name or name in {"system", "help", "__init__"} or not path.exists():
        return await edit_delete(event, "`Plugin not found (or protected).`")
    path.unlink()
    await edit_delete(event, f"`Removed {name}. Restart to unload it.`")


@cat_cmd("update", command=("update", "git pull the latest code and restart (git clones only)"))
async def update(event):
    if not Path(".git").exists():
        return await edit_delete(event, "`Not a git clone, nothing to pull.`")
    proc = await asyncio.create_subprocess_shell(
        "git pull", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
    )
    out = (await proc.communicate())[0].decode(errors="replace")
    if "Already up to date" in out:
        return await edit_delete(event, "`Already up to date.`")
    await edit_or_reply(event, f"`Updated, restarting...`\n```{out[-1500:]}```")
    await event.client.disconnect()
    os.execl(sys.executable, sys.executable, *sys.argv)


@cat_cmd("logs", command=("logs", "Send the bot's log file"))
async def logs(event):
    if not Path("data/navvora.log").exists():
        return await edit_delete(event, "`No log file yet.`")
    await event.client.send_file(event.chat_id, "data/navvora.log", caption="Navvora UserBot logs")
    await event.delete()
