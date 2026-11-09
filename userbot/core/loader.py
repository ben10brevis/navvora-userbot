import importlib
from pathlib import Path

from .. import LOGS


def load_plugins(folder: str = "plugins"):
    loaded = []
    base = Path(__file__).resolve().parent.parent / folder
    for path in sorted(base.glob("*.py")):
        name = path.stem
        if name.startswith("_"):
            continue
        try:
            importlib.import_module(f"userbot.{folder}.{name}")
            loaded.append(name)
        except Exception as e:  # noqa: BLE001
            LOGS.error("Failed to load plugin %s: %s", name, e)
    return loaded
