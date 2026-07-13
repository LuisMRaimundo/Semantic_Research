"""Load shared config pointing at the legacy lexicon databases and engines."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config.json"
CLASSES_DIR = ROOT / "classes"


def load_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Missing config.json at {CONFIG_PATH}")
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def save_config(data: dict[str, Any]) -> None:
    CONFIG_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def path_from_config(key: str) -> Path:
    cfg = load_config()
    raw = cfg.get(key)
    if not raw:
        raise KeyError(f"config.json missing key: {key}")
    return Path(raw)
