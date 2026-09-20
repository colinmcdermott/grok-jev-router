"""THE ONE FILE TO REVIEW. Every question Jev is asked and every threshold the
router uses lives here. Change wording or numbers here, nowhere else.

Jev returns calibrated probabilities. The decision is made by code (decide()),
so the risk tolerance is explicit and auditable.
"""
from __future__ import annotations

from .client import choice, noul, score

# The ten starterpack bots a task can be handed to, plus "none".
SPECIALISTS = {
    "business_ops": "general coordination across store, ads, pages, affiliates, retention, P&L, partners, bounties",
    "store_setup_from_zero": "creating a new product, plans and checkout links from nothing",
    "store_from_template": "cloning an existing working store and customizing it",
    "landing_page_generator": "writing and shipping a sales or landing page",
    "paid_ads_manager": "paid ad creative, launch, daily triage, kill and scale rules",
    "affiliate_program_manager": "affiliate terms, ranking performers, cutting bad actors",
    "ugc_bounty_manager": "clipping and UGC bounties: briefs, review, payout recommendations",
    "partner_referral_outreach": "finding fit businesses, sending partner links, tracking referral earnings",
    "churn_retention_manager": "cancellations, failed payments, save offers, exit reasons",
    "weekly_pl_analyst": "read-only weekly P&L: revenue, retention, leakage, ad efficiency",
    "none": "no specialist applies; the current bot should handle it",
}

ROUTER_QUESTIONS = {
    "lane": {
        "type": "choice",
        "instructions": "Given the task, the proposed next action and what has happened so far, which lane should the agent take for this action?",
        "criteria": {
            "proceed": "the action is safe, reversible and clearly needed; do it now",
            "dry_run": "the action is probably useful but uncertain or expensive; draft, simulate or produce a plan first",
            "ask_human": "the action is consequential, external, irreversible, ambiguous, or the agent has been going in circles",
            "skip": "the action is unnecessary: the task is already done, or this action would not move it forward",
        },
    },
    "risk": {
        "type": "score",
        "instructions": "How much harm could this action cause if it is wrong?",
        "criteria": [
            "none or trivial: internal, easily undone (reading, drafting, local files)",
            "low: visible to others but easy to correct (a message in a shared workspace, an internal doc)",
            "high: leaves the account or changes something others rely on (an external message, a publish, a config or code change)",
            "critical: money, deletion, permissions, legal terms, or production systems",
        ],
    },
    "reversible": {"type": "noul", "instructions": "Could the action be fully undone afterwards with no lasting effect?"},
    "external": {"type": "noul", "instructions": "Does the action send, publish, purchase, or otherwise leave the agent's own account?"},
    "necessary": {"type": "noul", "instructions": "Does this action materially advance the task, compared with what has already been done?"},
    "done": {"type": "noul", "instructions": "Based on the results so far, is the task already complete or as complete as it can be?"},
    "looping": {"type": "noul", "instructions": "Is the agent repeating an approach that has already failed, rather than changing approach?"},
    "specialist": {
        "type": "choice",
        "instructions": "Which specialist bot, if any, should own this task?",
        "criteria": SPECIALISTS,
    },
}

# ---- thresholds -------------------------------------------------------------
# Hard rules override the lane Jev picked. Tune here; keep the comments honest.
THRESHOLDS = {
    "done": 0.80,            # skip when Jev is this sure the task is finished
    "external": 0.50,        # anything likely to leave the account needs a human
    "risk_critical": 2.5,    # score at or above this needs a human
    "reversible_min": 0.30,  # below this, treat as irreversible -> human
    "lane_confidence": 0.50, # below this Jev is telling us it does not know -> human
    "necessary_min": 0.30,   # below this the action is pointless -> skip
    "looping": 0.70,         # likely stuck in a loop -> human
    "max_attempts": 3,       # retries beyond this -> human
    "specialist_min": 0.60,  # only suggest a hand-off when Jev is this sure
}

ACTIONS = ("proceed", "dry_run", "ask_human", "skip", "bypass")


def decide(answers: dict, attempts: int = 0, thresholds: dict = THRESHOLDS) -> dict:
    """Turn Jev's answers into one action plus a one-line reason."""
    t = thresholds
    lane, lane_conf, lane_probs = choice(answers, "lane")
    risk = score(answers, "risk")
    p_rev = noul(answers, "reversible")
    p_ext = noul(answers, "external")
    p_nec = noul(answers, "necessary")
    p_done = noul(answers, "done")
    p_loop = noul(answers, "looping")
    spec, spec_conf, _ = choice(answers, "specialist")

    if p_done >= t["done"]:
        action, reason = "skip", f"task looks complete (done={p_done:.2f})"
    elif p_ext >= t["external"]:
        action, reason = "ask_human", f"action leaves the account (external={p_ext:.2f})"
    elif risk >= t["risk_critical"]:
        action, reason = "ask_human", f"risk is critical (risk={risk:.1f})"
    elif p_rev < t["reversible_min"]:
        action, reason = "ask_human", f"action looks irreversible (reversible={p_rev:.2f})"
    elif p_loop >= t["looping"] or attempts >= t["max_attempts"]:
        action, reason = "ask_human", f"repeating a failed approach (looping={p_loop:.2f}, attempts={attempts})"
    elif lane_conf < t["lane_confidence"]:
        action, reason = "ask_human", f"Jev is unsure which lane applies (confidence={lane_conf:.2f})"
    elif p_nec < t["necessary_min"]:
        action, reason = "skip", f"action does not advance the task (necessary={p_nec:.2f})"
    elif lane in ("proceed", "dry_run", "ask_human", "skip"):
        action, reason = lane, f"Jev chose {lane} (confidence={lane_conf:.2f})"
    else:
        action, reason = "ask_human", "no usable lane answer"

    handoff = spec if (spec and spec != "none" and spec_conf >= t["specialist_min"]) else None
    return {
        "action": action,
        "reason": reason,
        "handoff": handoff,
        "signals": {
            "lane": lane, "lane_confidence": round(lane_conf, 3), "lane_probabilities": lane_probs,
            "risk": risk, "reversible": round(p_rev, 3), "external": round(p_ext, 3),
            "necessary": round(p_nec, 3), "done": round(p_done, 3), "looping": round(p_loop, 3),
            "specialist": spec, "specialist_confidence": round(spec_conf, 3),
        },
    }
