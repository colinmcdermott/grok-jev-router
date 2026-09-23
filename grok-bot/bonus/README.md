# Bonus bots built on Jev

Three more Grok Bot templates that use the jev-ask skill. Each one needs the
Jev router installed first (https://x.ai/bot/lS9XaHCr9QTTHhNtb0VQX) because it
relies on /workspace/jev and the key in ~/.typesafe/key.

To create one: New Bot in Grok Bot, name it, paste the file's contents as the
first message, then Share → Create template → Public link.

- `inbox-triage.md` labels every inbound message and hands it to the right bot
- `content-grader.md` scores a draft or page against a rubric and lists what to fix
- `ad-judge.md` picks the best of several ad variants before any money is spent
