# grok-jev-router

Jev decides, Grok Bot executes, humans control irreversible actions.

A small, dependency-free Python toolkit that lets a [Grok Bot](https://docs.x.ai/grok-bot/overview)
use [TypeSafe AI's Jev](https://docs.typesafe.ai) as a decision layer: before an
expensive or risky action, the bot asks Jev a fixed set of typed questions and
code turns the calibrated answers into one of four actions. About a hundredth
of a cent and a few hundred milliseconds per decision.

```
prompt → Grok Bot → router.py (Jev) → action → Grok Bot executes → result
```

Install as a Grok Bot template: **[Add Jev router to Grok Bot](https://x.ai/bot/REPLACE_WITH_TEMPLATE_ID)**.
Or build your own from `grok-bot/`.

## Seven-minute setup

1. Create a TypeSafe API key at https://console.typesafe.ai/keys. Use a dedicated key with a spend cap.
2. Add the Jev router Bot to Grok Bot and say: **run jev-setup**.
3. When it asks, open Agent Computer, take control, put the key in `~/.typesafe/key`, hand control back. Never paste the key in chat.
4. The Bot clones this repo to `/workspace/jev`, runs `smoke.py`, and routes the bundled examples so you can see a decision.
5. Add the Auto-review rules it lists. The router is advice; those rules are the boundary.
6. Stay in **shadow** mode for a week. Read the Monday review.
7. When you trust it: `python3 router.py active`. Kill switch: `python3 router.py off`.

## What a decision looks like

```
$ python3 router.py --state examples/state-send.json
{
  "action": "ask_human",
  "reason": "action leaves the account (external=0.74)",
  "handoff": null,
  "advisory": true,
  "signals": { "lane": "ask_human", "lane_confidence": 0.46, "risk": 2.52, "reversible": 0.18, "external": 0.74, ... },
  "meter": { "ms": 580, "input_tokens": 1107, "cost_usd": 0.0000465, "model": "jev-1.13.0" }
}
```

The four bundled examples, measured live on 2026-09-20:

| example | action | why | ms |
| --- | --- | --- | --- |
| open a pricing page in the browser | `proceed` | safe, reversible, needed | 536 |
| DM a member confirming a refund | `ask_human` | leaves the account, risk 2.5 of 3 | 580 |
| fourth identical `whop apps deploy` retry | `ask_human` | looping 0.97; hand-off suggested | 553 |
| web search for a URL already reported | `skip` | task done 0.87 | 536 |

| action | the bot should |
| --- | --- |
| `proceed` | do it |
| `dry_run` | draft, plan, or simulate, then stop and show it |
| `ask_human` | stop and ask, with the reason |
| `skip` | not do it; the task is done or the action is pointless |
| `bypass` | router is off; normal rules apply |

Hard rules in code override Jev's lane: anything likely to leave the account,
critical risk, irreversible, looping, too many attempts, or low confidence goes
to a human. `done` is checked first so a finished task is never re-worked.

## Files

- `router.py` the decision. `--state file.json`, `record`, `status`, `on`, `off`, `shadow`, `active`.
- `jev/questions.py` **the one file to review**: every question and every threshold.
- `ask.py` ask Jev anything typed about any state. Powers the jev-ask skill.
- `smoke.py` one cheap Choice call to prove key, network, model.
- `review.py` weekly summary of the logs: actions, disagreements, cost, latency.
- `config.json` `enabled`, `mode` (shadow or active), `model`.
- `logs/` one JSONL file per day. Gitignored.
- `examples/` four states that produce four different actions, and a support-triage question set.
- `grok-bot/` the Bot profile, three skills, and the weekly routine, ready to paste.
- `tests/` `python3 -m unittest discover -s tests`

## Why shadow first

Grok Bot obeying the route is instruction-following, not enforcement. Shadow
mode lets you compare what Jev said with what the bot did before anything
depends on it. `router.py record` writes the bot's actual choice next to the
decision; `review.py` reports the disagreement rate.

## Limits and honesty

- Jev's request budget is about 32k tokens. The router truncates long fields; pass summaries, not transcripts.
- The API key on the Agent Computer is visible to every bot on that account. That is how Grok Bot's shared computer works. Use a capped key.
- Jev is early access. Pricing is $0.042 per million input tokens, output free.
- The `specialist` question names the ten bots from the [Grok Bot Business Starterpack](https://grok-bot-starterpack.whop.site). Edit `SPECIALISTS` in `jev/questions.py` for your own roster.

## Credits

Jev by [TypeSafe AI](https://typesafe.ai). Patterns: [confidence-gated routing](https://docs.typesafe.ai/patterns/confidence-routing) and [intent routing](https://docs.typesafe.ai/patterns/intent-routing). Grok Bot docs: [skills and routines](https://docs.x.ai/grok-bot/skills-routines-and-automations), [approvals](https://docs.x.ai/grok-bot/approvals-security-and-privacy).

MIT.
