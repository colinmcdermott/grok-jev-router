#!/usr/bin/env python3
"""Ask Jev any typed questions about any state. For the jev-ask skill.

  python ask.py --state '"customer message text"' --questions questions.json
  python ask.py --state state.json --questions '{"urgent":{"type":"noul","instructions":"Is this urgent?"}}'

Question types: choice (criteria: {option: description}), score (criteria:
[level descriptions, low to high]), noul (yes/no, returns a probability).
Limits: about 32k tokens per request, 1-255 choice options, 2-10 score levels.
"""
from __future__ import annotations

import argparse
import json
import os
import sys

from jev import config
from jev.client import JevError, evaluate


def load_arg(arg: str):
    if arg == "-":
        return json.loads(sys.stdin.read())
    if os.path.exists(arg):
        with open(arg) as f:
            return json.load(f)
    return json.loads(arg)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--state", required=True, help="JSON value, path, or -")
    p.add_argument("--questions", required=True, help="JSON object, path, or -")
    args = p.parse_args(argv)
    cfg = config.load()
    try:
        r = evaluate(load_arg(args.state), load_arg(args.questions), model=cfg["model"])
    except JevError as e:
        print(json.dumps({"error": str(e)}))
        return 2
    print(json.dumps(r, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
