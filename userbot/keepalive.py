"""Tiny web server so free web hosts (Render, Koyeb...) see an open port.

It only starts when the host sets a PORT environment variable. Point an uptime
monitor (UptimeRobot) at the service URL so the host never puts the bot to sleep.
"""
import os

from aiohttp import web

from . import LOGS


async def start_keepalive():
    port = os.environ.get("PORT")
    if not port:
        return None

    async def alive(_request):
        return web.Response(text="Navvora UserBot is running")

    app = web.Application()
    app.router.add_get("/", alive)  # HEAD is allowed too (UptimeRobot uses it)
    app.router.add_get("/health", alive)
    runner = web.AppRunner(app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", int(port)).start()
    LOGS.info("Keep-alive server listening on port %s", port)
    return runner
