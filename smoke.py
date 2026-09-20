#!/usr/bin/env python3
"""One cheap Choice question to prove the key, network and model work."""
from __future__ import annotations

import json
import sys

from jev.client import JevError, evaluate

QUESTIONS = {
    "system": {
        "type": "choice",
        "instructions": "Which kind of thinking does this request call for?",
        "criteria": {
            "system_one": "a fast, narrow, structured judgement software can act on",
            "system_two": "slow open-ended reasoning or generating new text",
        },
    }
}

if __name__ == "__main__":
    try:
        r = evaluate("Decide in under a second whether this support ticket needs a human.", QUESTIONS)
    except JevError as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        sys.exit(2)
    a = r["answers"].get("system", {})
    print(json.dumps({"ok": True, "model": r["model"], "choice": a.get("choice"), "confidence": a.get("confidence"), "ms": r["ms"], "input_tokens": r["usage"].get("input_tokens"), "cost_usd": r["cost_usd"]}, indent=2))
