"""Tiny JSON key-value store (data/navvora_db.json)."""
import json
import threading
from pathlib import Path

_PATH = Path("data/navvora_db.json")
_lock = threading.Lock()


def _load() -> dict:
    try:
        return json.loads(_PATH.read_text())
    except Exception:  # noqa: BLE001
        return {}


def get(key, default=None):
    return _load().get(key, default)


def put(key, value):
    with _lock:
        data = _load()
        data[key] = value
        _PATH.parent.mkdir(parents=True, exist_ok=True)
        _PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def remove(key):
    with _lock:
        data = _load()
        data.pop(key, None)
        _PATH.parent.mkdir(parents=True, exist_ok=True)
        _PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False))
