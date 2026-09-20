from __future__ import annotations

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.environ.get("JEV_CONFIG", os.path.join(ROOT, "config.json"))
LOG_DIR = os.environ.get("JEV_LOG_DIR", os.path.join(ROOT, "logs"))

DEFAULTS = {"enabled": True, "mode": "shadow", "model": "jev-latest", "max_state_chars": 12000}


def load() -> dict:
    cfg = dict(DEFAULTS)
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            cfg.update(json.load(f))
    if cfg.get("mode") not in ("shadow", "active"):
        cfg["mode"] = "shadow"
    return cfg


def save(cfg: dict) -> None:
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)
        f.write("\n")
