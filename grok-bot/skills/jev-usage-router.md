# Skill: jev-usage-router

**When to use:** before any of these, every time:

- opening a browser session or a long research task
- retrying something that already failed
- handing work to another bot or creating a bot
- anything that sends, publishes, pays, refunds, deletes, deploys, or changes settings

Cost is about a hundredth of a cent and a few hundred milliseconds, so err on
the side of calling it.

## Steps

1. Write a compact state to a temp file. Keep it under a page; summarize, never
   paste transcripts:
   ```json
   {
     "task": "what the owner asked for, one or two sentences",
     "bot": "your bot name",
     "proposed_action": {"type": "browser|research|retry|delegate|send|write|purchase|delete|publish|other",
                          "summary": "what you are about to do", "target": "URL, id, or person"},
     "attempts": 0,
     "last_result": "what the previous attempt returned, trimmed",
     "notes": "anything else that changes the decision"
   }
   ```
2. Run `cd /workspace/jev && python3 router.py --state /tmp/state.json`.
3. Read `action` and `reason`. Then:
   - **shadow mode** (`"advisory": true`): note the decision in one line, do what
     you would have done anyway, and afterwards record it:
     `python3 router.py record --id <id> --actual <proceed|dry_run|ask_human|skip>`
   - **active mode**: obey.
     - `proceed`: do it.
     - `dry_run`: produce the draft, plan, or simulation, show it, and stop.
     - `ask_human`: stop, tell the owner the proposed action and the router's
       reason, wait.
     - `skip`: do not do it; explain why in one line and move to the next step.
     - `bypass`: the router is off; follow your normal rules.
4. If `handoff` names a specialist bot and that bot is installed on this
   account, offer the hand-off to the owner rather than doing the work yourself.
5. If the router prints `"error": true`, treat the action as ask_human unless it
   is plainly trivial and reversible.

## Validate

Every routed action has a log line in /workspace/jev/logs/ with an id, and in
shadow mode a matching `record` line.

## Return

Nothing extra. The decision is one line in your normal progress update, for
example: `router: dry_run (risk 2.0, external 0.61) id 3f9a1c`.

## Requires approval

Whatever the owner's Auto-review rules say. The router never lowers that bar.
