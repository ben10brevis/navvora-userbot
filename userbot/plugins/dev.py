import ast
import asyncio
import contextlib
import inspect
import io
import textwrap

from userbot.core import cat_cmd, edit_delete, edit_or_reply


def _clip(text: str) -> str:
    return text[-3500:] if len(text) > 3500 else text


@cat_cmd("eval", command=("eval <python>", "Run Python (async ok). Vars: event, client, reply. OWNER ONLY"))
async def evaluate(event):
    code = (event.pattern_match.group(1) or "").strip()
    if not code:
        return await edit_delete(event, "`Usage: eval 1+1`")
    env = {"event": event, "client": event.client, "reply": await event.get_reply_message(), "asyncio": asyncio}
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out):
            try:
                result = eval(compile(ast.parse(code, mode="eval"), "<eval>", "eval"), env)
                if inspect.isawaitable(result):
                    result = await result
            except SyntaxError:
                ns = {}
                exec("async def __ex(event, client, reply, asyncio):\n" + textwrap.indent(code, "    "), ns)
                result = await ns["__ex"](event, event.client, env["reply"], asyncio)
    except Exception as e:  # noqa: BLE001
        result = f"{type(e).__name__}: {e}"
    shown = out.getvalue() + ("" if result is None else str(result))
    await edit_or_reply(event, f"**Code:**\n```{code[:800]}```\n**Output:**\n```{_clip(shown) or 'None'}```")


@cat_cmd("term", command=("term <shell cmd>", "Run a shell command (60s limit). OWNER ONLY"))
async def term(event):
    cmd = (event.pattern_match.group(1) or "").strip()
    if not cmd:
        return await edit_delete(event, "`Usage: term ls -la`")
    proc = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
    )
    try:
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=60)
    except asyncio.TimeoutError:
        proc.kill()
        return await edit_delete(event, "`Timed out after 60s.`")
    await edit_or_reply(event, f"**$** `{cmd}`\n```{_clip(stdout.decode(errors='replace')) or 'no output'}```")
