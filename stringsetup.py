"""Navvora UserBot - generate a Telethon StringSession for your own account.

Run:  python stringsetup.py
Your session string gives FULL access to your account. Never share it.
"""
from telethon.sessions import StringSession
from telethon.sync import TelegramClient

api_id = int(input("APP_ID: ").strip())
api_hash = input("API_HASH: ").strip()

with TelegramClient(StringSession(), api_id, api_hash) as client:
    session = client.session.save()
    client.send_message("me", f"Navvora UserBot STRING_SESSION (keep private, delete this message):\n\n`{session}`")
    print("\nSTRING_SESSION sent to your Saved Messages. Copy it into .env, then delete that message.")
