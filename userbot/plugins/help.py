from userbot import HELP, Config
from userbot.core import cat_cmd, edit_delete, edit_or_reply


@cat_cmd("help", command=("help [plugin]", "Show plugins, or the commands of one plugin"), allow_sudo=True)
async def help_cmd(event):
    arg = (event.pattern_match.group(1) or "").strip().lower()
    if not arg:
        names = ", ".join(f"`{n}`" for n in sorted(HELP))
        return await edit_or_reply(
            event,
            f"**Plugins ({len(HELP)}):**\n{names}\n\nUse `{Config.HANDLER}help <plugin>` for commands.",
        )
    if arg not in HELP:
        return await edit_delete(event, f"`No plugin named {arg}.`")
    lines = "\n".join(f"• `{cmd}` — {desc}" for cmd, desc in HELP[arg].items())
    await edit_or_reply(event, f"**{arg}**\n\n{lines}")
