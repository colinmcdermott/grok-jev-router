"""Minimal TypeSafe System One client. Standard library only, so it runs on a
fresh Agent Computer with nothing installed.

Key lookup order: TYPESAFE_API_KEY, TYPESAFE_AI_API_KEY, then the file named by
TYPESAFE_KEY_FILE (default ~/.typesafe/key). Never print the key.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request

API_URL = os.environ.get("TYPESAFE_API_URL", "https://api.typesafe.ai/v1/systemone")
MODEL = os.environ.get("JEV_MODEL", "jev-latest")
USD_PER_INPUT_TOKEN = 0.042 / 1_000_000
DEFAULT_KEY_FILE = os.path.expanduser("~/.typesafe/key")


class JevError(RuntimeError):
    pass


def api_key() -> str:
    for name in ("TYPESAFE_API_KEY", "TYPESAFE_AI_API_KEY"):
        v = os.environ.get(name)
        if v:
            return v.strip()
    path = os.environ.get("TYPESAFE_KEY_FILE", DEFAULT_KEY_FILE)
    if os.path.exists(path):
        with open(path) as f:
            v = f.read().strip()
        if v:
            return v
    raise JevError(
        "No TypeSafe API key. Put it in ~/.typesafe/key (chmod 600) or export TYPESAFE_API_KEY. "
        "Create one at https://console.typesafe.ai/keys"
    )


def evaluate(state, questions: dict, model: str = MODEL, timeout: float = 30.0) -> dict:
    """POST state + questions, return {answers, usage, model, ms, cost_usd}."""
    body = json.dumps({"state": state, "model": model, "questions": questions}).encode()
    req = urllib.request.Request(
        API_URL,
        data=body,
        headers={"Authorization": f"Bearer {api_key()}", "Content-Type": "application/json"},
        method="POST",
    )
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:500]
        if e.code == 401:
            raise JevError("TypeSafe rejected the API key (401). Check ~/.typesafe/key.") from None
        if e.code == 429:
            raise JevError("TypeSafe rate limit (429). Wait a moment and retry.") from None
        if e.code == 402 or "credit" in detail.lower():
            raise JevError("TypeSafe credits exhausted. Top up at console.typesafe.ai (Settings > Billing).") from None
        raise JevError(f"TypeSafe HTTP {e.code}: {detail}") from None
    except urllib.error.URLError as e:
        raise JevError(f"Could not reach TypeSafe: {e.reason}") from None
    ms = (time.perf_counter() - started) * 1000
    usage = data.get("usage", {})
    tokens = int(usage.get("input_tokens", 0))
    return {
        "answers": data.get("answers", {}),
        "usage": usage,
        "model": data.get("model", model),
        "ms": round(ms),
        "cost_usd": round(tokens * USD_PER_INPUT_TOKEN, 8),
    }


# ---- answer accessors (tolerant of missing fields) ------------------------

def choice(answers: dict, key: str):
    a = answers.get(key) or {}
    probs = a.get("probabilities") or {}
    c = a.get("choice")
    return c, float(a.get("confidence", probs.get(c, 0.0)) or 0.0), probs


def score(answers: dict, key: str) -> float:
    a = answers.get(key) or {}
    return float(a.get("score", 0.0) or 0.0)


def noul(answers: dict, key: str) -> float:
    a = answers.get(key) or {}
    return float(a.get("noul", a.get("probability", 0.0)) or 0.0)
