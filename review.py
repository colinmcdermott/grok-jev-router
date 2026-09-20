#!/usr/bin/env python3
"""Summarize the router logs: actions, shadow disagreements, cost. For the weekly routine.

  python review.py            # last 7 days
  python review.py --days 30
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import glob
import json
import os

from jev import config


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--days", type=int, default=7)
    args = p.parse_args(argv)
    since = dt.date.today() - dt.timedelta(days=args.days)
    decisions, records = {}, {}
    for path in sorted(glob.glob(os.path.join(config.LOG_DIR, "*.jsonl"))):
        day = os.path.basename(path)[:-6]
        try:
            if dt.date.fromisoformat(day) < since:
                continue
        except ValueError:
            continue
        with open(path) as f:
            for line in f:
                try:
                    e = json.loads(line)
                except ValueError:
                    continue
                if "record_for" in e:
                    records[e["record_for"]] = e
                elif "id" in e:
                    decisions[e["id"]] = e

    actions = collections.Counter(d["action"] for d in decisions.values())
    reasons = collections.Counter(d.get("reason", "").split(" (")[0] for d in decisions.values() if d["action"] == "ask_human")
    handoffs = collections.Counter(d["handoff"] for d in decisions.values() if d.get("handoff"))
    errors = sum(1 for d in decisions.values() if d.get("error"))
    cost = sum((d.get("meter") or {}).get("cost_usd", 0) or 0 for d in decisions.values())
    ms = [(d.get("meter") or {}).get("ms") for d in decisions.values() if (d.get("meter") or {}).get("ms")]
    disagreements = []
    for did, rec in records.items():
        d = decisions.get(did)
        if d and d["action"] != rec["actual"]:
            disagreements.append({"id": did, "jev": d["action"], "actual": rec["actual"], "reason": d.get("reason"), "task": (d.get("state") or {}).get("task", "")[:120]})

    out = {
        "window_days": args.days,
        "decisions": len(decisions),
        "actions": dict(actions),
        "ask_human_reasons": dict(reasons.most_common(5)),
        "handoffs_suggested": dict(handoffs),
        "router_errors": errors,
        "shadow_records": len(records),
        "disagreements": disagreements[:20],
        "disagreement_rate": round(len(disagreements) / len(records), 3) if records else None,
        "cost_usd": round(cost, 6),
        "median_ms": sorted(ms)[len(ms) // 2] if ms else None,
    }
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
