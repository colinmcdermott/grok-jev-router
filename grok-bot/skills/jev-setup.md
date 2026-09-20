# Skill: jev-setup

**When to use:** once, right after this Bot is added, or when `router.py status`
fails. Takes about five minutes.

**Required:** a TypeSafe API key from https://console.typesafe.ai/keys. Ask the
owner to create a dedicated key with a spend cap for this account. Python 3.8 or
newer on the Agent Computer (check with `python3 --version`).

## Steps

1. Get the code onto the Agent Computer:
   ```
   git clone https://github.com/colinmcdermott/grok-jev-router /workspace/jev
   ```
   If the folder exists, `cd /workspace/jev && git pull` instead.
2. Place the key. Never ask for it in chat. Say exactly this to the owner:
   "Open Agent Computer, take control, run `mkdir -p ~/.typesafe && nano ~/.typesafe/key`,
   paste your TypeSafe key, save, then run `chmod 600 ~/.typesafe/key` and hand
   control back." If a secure secret request is available for a TypeSafe
   connection, use that instead and write the value to the same file.
3. Confirm the key is in place without reading it: `test -s ~/.typesafe/key && echo present`.
4. Smoke test: `cd /workspace/jev && python3 smoke.py`. Expect `"ok": true`, a
   `choice` of `system_one`, and a time under one second. If it fails, read the
   error: 401 is a bad key, 429 is a rate limit, credits means top up at
   console.typesafe.ai.
5. Run the unit tests: `python3 -m unittest discover -s tests`. All should pass.
6. Confirm shadow mode: `python3 router.py status` should show `"mode": "shadow"`.
7. Route the bundled examples so the owner can see what a decision looks like:
   `for f in examples/state-*.json; do python3 router.py --state $f; done`
8. Recommend the owner add these Auto-review rules (Settings → General → Bot →
   Auto-review), because the router is advice and these are the boundary:
   - Ask first before sending any external message or email.
   - Ask first before any purchase, payout, transfer, or refund.
   - Ask first before publishing or deploying.
   - Ask first before deleting files outside /workspace/jev/logs.

## Validate

`python3 smoke.py` returns ok, the four examples produce four different
actions, and `~/.typesafe/key` never appears in the conversation.

## Return

A short report: key present (yes/no, not the value), smoke result and latency,
test count, current mode, and the list of Auto-review rules the owner still
needs to add.

## Requires approval

Nothing in this skill changes anything outside /workspace/jev and ~/.typesafe.
