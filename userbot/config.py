import os

from dotenv import load_dotenv

load_dotenv()


def _ids(value: str):
    return [int(x) for x in value.replace(" ", "").split(",") if x.lstrip("-").isdigit()]


class Config:
    API_ID = int(os.environ.get("APP_ID") or 0)
    API_HASH = os.environ.get("API_HASH", "")
    STRING_SESSION = os.environ.get("STRING_SESSION", "")
    HANDLER = os.environ.get("COMMAND_HANDLER", ".")
    ALIVE_NAME = os.environ.get("ALIVE_NAME", "")
    ALIVE_PIC = os.environ.get("ALIVE_PIC", "")  # image URL for .alive (optional)
    TIMEZONE = os.environ.get("TIMEZONE", "UTC")  # e.g. Asia/Kolkata
    SUDO_USERS = _ids(os.environ.get("SUDO_USERS", ""))
