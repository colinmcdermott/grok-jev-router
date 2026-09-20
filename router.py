#!/usr/bin/env python3
"""Jev usage router. The agent calls this BEFORE an expensive or risky action.

  python router.py --state state.json            # decide (mode from config.json)
  python router.py --state state.json --mode active
  python router.py record --id <decision id> --actual proceed --note "..."
  python router.py status | on | off | shadow | active

Prints one JSON object. In shadow mode the agent logs the decision and carries
on as it would have; in active mode it honors "action".
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import uuid

from jev import config
from jev.client import JevError, evaluate
from jev.questions import ROUTER_QUESTIONS, THRESHOLDS, decide

STATE_KEYS = ("task", "bot", "proposed_action", "attempts", "last_result", "notes")


def read_state(arg: str) -> dict:
    if arg == "-":
        raw = sys.stdin.read()
    elif os.path.exists(arg):
        with open(arg) as f:
            raw = f.read()
    else:
        raw = arg
    state = json.loads(raw)
    if not isinstance(state, dict) or not state.get("task") or not state.get("proposed_action"):
        raise SystemExit('state must be a JSON object with at least "task" and "proposed_action" (see examples/)')
    return state


def compact(state: dict, limit: int) -> dict:
    """Keep the known keys, truncate long strings so a request stays far below Jev's budget."""
    out = {}
    for k in STATE_KEYS:
        if k in state:
            v = state[k]
            if isinstance(v, str) and len(v) > 2000:
                v = v[:2000] + " …[truncated]"
            out[k] = v
    text = json.dumps(out)
    if len(text) > limit:
        for k in ("last_result", "notes"):
            if isinstance(out.get(k), str):
                out[k] = out[k][:800] + " …[truncated]"
    return out


def log_path() -> str:
    os.makedirs(config.LOG_DIR, exist_ok=True)
    return os.path.join(config.LOG_DIR, dt.date.today().isoformat() + ".jsonl")


def append_log(entry: dict) -> None:
    with open(log_path(), "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def cmd_route(args) -> int:
    cfg = config.load()
    mode = args.mode or cfg["mode"]
    state = compact(read_state(args.state), cfg["max_state_chars"])
    attempts = int(state.get("attempts", 0) or 0)
    decision_id = uuid.uuid4().hex[:12]

    if not cfg["enabled"]:
        out = {"id": decision_id, "mode": mode, "action": "bypass", "reason": "router disabled in config.json", "handoff": None}
        print(json.dumps(out, indent=2))
        return 0

    try:
        r = evaluate(state, ROUTER_QUESTIONS, model=cfg["model"])
    except JevError as e:
        # Fail safe, not open: when Jev is unreachable the agent asks a human for anything non-trivial.
        out = {"id": decision_id, "mode": mode, "action": "ask_human", "reason": f"router error: {e}", "handoff": None, "error": True}
        append_log({"ts": dt.datetime.now(dt.timezone.utc).isoformat(), **out, "state": state})
        print(json.dumps(out, indent=2))
        return 2

    d = decide(r["answers"], attempts=attempts, thresholds=THRESHOLDS)
    out = {
        "id": decision_id,
        "mode": mode,
        "action": d["action"],
        "reason": d["reason"],
        "handoff": d["handoff"],
        "advisory": mode == "shadow",
        "signals": d["signals"],
        "meter": {"ms": r["ms"], "input_tokens": r["usage"].get("input_tokens"), "cost_usd": r["cost_usd"], "model": r["model"]},
    }
    append_log({"ts": dt.datetime.now(dt.timezone.utc).isoformat(), **out, "state": state})
    print(json.dumps(out, indent=2))
    return 0


def cmd_record(args) -> int:
    append_log({"ts": dt.datetime.now(dt.timezone.utc).isoformat(), "record_for": args.id, "actual": args.actual, "note": args.note or ""})
    print(json.dumps({"recorded": args.id, "actual": args.actual}))
    return 0


def cmd_set(field: str, value) -> int:
    cfg = config.load()
    cfg[field] = value
    config.save(cfg)
    print(json.dumps({"enabled": cfg["enabled"], "mode": cfg["mode"], "config": config.CONFIG_PATH}))
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd")
    p.add_argument("--state", help="JSON string, path, or - for stdin")
    p.add_argument("--mode", choices=("shadow", "active"), help="override config mode for this call")
    rec = sub.add_parser("record", help="record what the agent actually did, for shadow-mode review")
    rec.add_argument("--id", required=True)
    rec.add_argument("--actual", required=True, choices=("proceed", "dry_run", "ask_human", "skip"))
    rec.add_argument("--note")
    for name in ("status", "on", "off", "shadow", "active"):
        sub.add_parser(name)
    args = p.parse_args(argv)

    if args.cmd == "record":
        return cmd_record(args)
    if args.cmd == "status":
        cfg = config.load()
        print(json.dumps({"enabled": cfg["enabled"], "mode": cfg["mode"], "model": cfg["model"], "config": config.CONFIG_PATH, "logs": config.LOG_DIR}))
        return 0
    if args.cmd == "on":
        return cmd_set("enabled", True)
    if args.cmd == "off":
        return cmd_set("enabled", False)
    if args.cmd in ("shadow", "active"):
        return cmd_set("mode", args.cmd)
    if not args.state:
        p.print_help()
        return 1
    return cmd_route(args)


if __name__ == "__main__":
    sys.exit(main())
