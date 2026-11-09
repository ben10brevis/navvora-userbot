import logging
import os
import time

from telethon import TelegramClient
from telethon.sessions import StringSession

from .config import Config

os.makedirs("data", exist_ok=True)
logging.basicConfig(
    format="[%(asctime)s] [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler(), logging.FileHandler("data/navvora.log")],
)
LOGS = logging.getLogger("userbot")

START_TIME = time.time()

# plugin name -> {command: description}
HELP: dict = {}

bot = TelegramClient(
    StringSession(Config.STRING_SESSION) if Config.STRING_SESSION else "navvora",
    Config.API_ID,
    Config.API_HASH,
)
