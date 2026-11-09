# Navvora UserBot

A plugin-based Telegram userbot for **your own account**, built on [Telethon](https://github.com/LonamiWebs/Telethon) and structured like [catuserbot](https://github.com/TgCatUB/catuserbot): a core with a command decorator + help registry, and one file per plugin in `userbot/plugins/`.

Type `.help` in any chat for the plugin list and `.help <plugin>` for its commands.

---

## 1. What you need first (all deploy methods)

1. **APP_ID and API_HASH**: log in at <https://my.telegram.org> → *API development tools* → create an app.
2. **STRING_SESSION**: generate it once on any computer or phone:
   ```bash
   pip install -r requirements.txt
   python stringsetup.py
   ```
   Log in with your phone number; the session string is sent to your *Saved Messages*. Copy it, then delete that message.
3. **Config**: copy `.env.example` to `.env` and fill in `APP_ID`, `API_HASH`, `STRING_SESSION` (for hosting dashboards, add them as environment variables instead of a file).

| Variable | Required | Meaning |
|---|---|---|
| `APP_ID`, `API_HASH`, `STRING_SESSION` | yes | Telegram credentials |
| `COMMAND_HANDLER` | no | Command prefix, default `.` |
| `ALIVE_NAME`, `ALIVE_PIC` | no | Name / image URL for `.alive` |
| `TIMEZONE` | no | e.g. `Asia/Kolkata` (for `.time`, `.autoname`, `.autobio`) |
| `SUDO_USERS` | no | Comma separated user IDs allowed to run harmless commands |

> Never commit `.env` or share your `STRING_SESSION`: it gives full access to your account.

---

## 2. How to deploy

### A. Run locally (quick test)

```bash
python -m venv venv && source venv/bin/activate     # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### B. VPS / Linux server (recommended for 24/7)

```bash
sudo apt update && sudo apt install -y python3 python3-venv git
sudo adduser --disabled-password --gecos "" navvora
sudo mkdir -p /opt/navvora-userbot && sudo chown navvora: /opt/navvora-userbot
sudo -u navvora -i
cd /opt/navvora-userbot
# upload or git clone your project here, then:
python3 -m venv venv && ./venv/bin/pip install -r requirements.txt
cp .env.example .env && nano .env
exit
```

Run it as a service so it restarts on crash and on reboot:

```bash
sudo cp /opt/navvora-userbot/deploy/navvora-userbot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now navvora-userbot
sudo journalctl -u navvora-userbot -f        # live logs
```

Quick alternative without systemd: `tmux new -s navvora` → `./venv/bin/python main.py` → detach with `Ctrl+B` then `D`.

### C. Docker / Docker Compose

```bash
cp .env.example .env && nano .env
docker compose up -d --build
docker compose logs -f
```

`./data` is mounted into the container, so notes, filters and approvals survive restarts and rebuilds.

### D. Termux (Android phone)

```bash
pkg update && pkg upgrade -y
pkg install -y python git libjpeg-turbo libpng freetype
pip install -r requirements.txt
cp .env.example .env && nano .env
termux-wake-lock
python main.py
```

Use `pkg install tmux` and run inside `tmux` so it keeps going when you close the session. Android may kill background apps; disable battery optimisation for Termux.

### E. Heroku

Heroku has no free plan; a paid worker dyno is needed.

```bash
heroku login
heroku create my-navvora-bot
heroku config:set APP_ID=... API_HASH=... STRING_SESSION=... TIMEZONE=Asia/Kolkata
git init && git add . && git commit -m "deploy"
heroku git:remote -a my-navvora-bot
git push heroku HEAD:main
heroku ps:scale web=0 worker=1
heroku logs -t
```

`Procfile`, `.python-version` and `app.json` are already included. If you push the project to your own GitHub repo you can also use a Heroku "Deploy" button pointing at it.

### F. Railway

1. Push the project to a private GitHub repo.
2. Railway → **New Project → Deploy from GitHub repo** (the included `Dockerfile` is detected).
3. Open **Variables** and add `APP_ID`, `API_HASH`, `STRING_SESSION` (and any optional ones).
4. No port or domain is needed. Check **Deployments → Logs** for `Logged in as ...`.
5. Optional: add a **Volume** mounted at `/app/data` to keep notes/filters across redeploys.

### G. Render (paid worker)

1. Push to a private GitHub repo.
2. **New → Background Worker**, connect the repo, runtime **Docker**.
3. Add the environment variables, then deploy. (Background workers are a paid service type; do not use a "Web Service", it needs an open port.)
4. Optional: attach a **Disk** mounted at `/app/data`.

### Free: Render + UptimeRobot

Render's free plan only offers **web services**, and they sleep after 15 minutes without incoming visits. The bot now ships with a tiny built-in web page (it starts automatically when Render sets `PORT`), and UptimeRobot visits it every 5 minutes so the service never sleeps.

1. **Push the project to a private GitHub repo.** `.env` is git-ignored; never commit it.
2. On <https://render.com>: **New → Web Service** → connect the repo → Runtime **Docker** → Instance type **Free**.
   (Or use **New → Blueprint**, which reads the included `render.yaml`.)
3. Under **Environment**, add `APP_ID`, `API_HASH`, `STRING_SESSION` (and `TIMEZONE`, e.g. `Asia/Kolkata`). Click **Create Web Service**.
4. Wait until the logs show `Logged in as ...`, then open your URL (`https://your-service.onrender.com`). You should see **Navvora UserBot is running**.
5. On <https://uptimerobot.com>: sign up → **Add New Monitor** → type **HTTP(s)** → paste your Render URL → interval **5 minutes** → **Create Monitor**.
6. Send `.alive` from your Telegram account to confirm.

Things to know:
- The free tier gives about 750 instance hours per month, enough for **one** service running 24/7. Don't create a second free service.
- Render may ask for a card on signup, and free-tier rules change, so check Render's current pricing page.
- Free instances restart now and then; the bot reconnects by itself. Local files in `data/` (notes, filters, PM approvals) reset on restart; your login does not.
- If the bot stops replying, check Render logs, and make sure the same `STRING_SESSION` is not running anywhere else.

### H. Koyeb (or any Docker host)

1. Create a service from your GitHub repo using the **Dockerfile**, service type **Worker** (no port).
2. Add the environment variables and deploy.

On any free web-service host the built-in keep-alive page starts when `PORT` is set, so pair it with UptimeRobot as above.

Any host that can run `python main.py` or the Docker image works the same way.

### Keeping data on hosts with temporary disks

Heroku, and Railway/Render/Koyeb without a volume, wipe local files on every restart. Your **login survives** (it is in `STRING_SESSION`), but notes, filters, welcome messages and PM approvals in `data/navvora_db.json` reset. Use a volume/disk mounted at `data/` if you want them kept.

### Updating

- Git clone on a VPS/Termux: send `.update` (runs `git pull`, then restarts), or `git pull && sudo systemctl restart navvora-userbot`.
- Docker: `git pull && docker compose up -d --build`.
- PaaS: push or redeploy.

---

## 3. Plugins (default prefix `.`)

| Plugin | Commands |
|---|---|
| alive | `.alive` `.ping` |
| help | `.help [plugin]` |
| purge | `.purge` `.del` `.sd <sec> <text>` |
| afk | `.afk [reason]` |
| info | `.id` `.info [reply/@user/id]` |
| admin | `.pin` `.unpin` `.kick` `.ban` `.unban` |
| groupadmin | `.mute` `.unmute` `.promote` `.demote` `.warn` `.warns` `.resetwarns` `.setrules` `.rules` `.lock` `.unlock` `.zombies [clean]` |
| chat | `.chatinfo` `.admins` `.bots` `.link` `.leave` `.archive` `.unarchive` `.read` |
| profile | `.setname First \| Last` `.setbio` `.setusername` `.setpic` |
| autoprofile | `.autoname on\|off` `.autobio on <text>\|off` |
| pmpermit | `.pmguard on\|off` `.approve` `.disapprove` `.block` `.unblock` |
| notes | `.save` `.get` `.notes` `.clear` |
| filters | `.filter <word> <reply>` `.stop <word>` `.filters` |
| welcome | `.setwelcome` `.clearwelcome` `.welcome` |
| textfx | `.mock` `.vapor` `.clap` `.reverse` `.owo` `.type` |
| fun | `.dice` `.dart` `.basket` `.football` `.slot` `.bowl` `.coin` `.roll` `.choose` |
| randoms | `.joke` `.fact` `.quote` `.advice` `.cat` `.dog` |
| calc | `.calc <expr>` |
| web | `.weather` `.ud` `.define` `.wiki` `.tr` `.crypto` `.cur` `.github` `.qr` `.paste` |
| tools | `.ip` `.time` `.cal` `.short` `.b64e` `.b64d` `.hash` `.pass` `.morse` `.bin` `.unbin` |
| media | `.stoi` `.itos` `.pfp` |
| files | `.dl` `.ul` `.rename` `.json` |
| remind | `.remind 10m <text>` |
| sysinfo | `.sysd` |
| sudo | `.addsudo` `.delsudo` `.sudolist` |
| system | `.restart` `.shutdown` `.update` `.logs` `.install` `.uninstall` |
| dev | `.eval` `.term` (owner only) |

Sudo users can only run commands marked `allow_sudo=True` (harmless lookups such as alive, ping, calc, weather, wiki). Group admin, profile, dev and system commands are always owner-only.

## 4. Writing a plugin

```python
from userbot.core import cat_cmd, edit_or_reply

@cat_cmd("hello", command=("hello [name]", "Say hello"))
async def hello(event):
    name = (event.pattern_match.group(1) or "world").strip()
    await edit_or_reply(event, f"Hello, {name}!")
```

Drop it in `userbot/plugins/` (auto-loaded on start) or reply to the file with `.install`.

## 5. Safety

- `STRING_SESSION` = full access to your account. Never share it or commit `.env`.
- `.eval`, `.term` and `.install` run code with your account's power; only use files you've read.
- Telegram can ban accounts for spam, mass tagging/adding or scraping. Those plugins are intentionally not included.
