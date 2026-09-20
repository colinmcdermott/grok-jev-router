# Skill: jev-ask

**When to use:** whenever you need a fast, calibrated judgement about some
text or data and the answer is a label, a rating, or yes/no. Classify a support
message, rate urgency, decide if a draft is on-brand, pick which of the ten
starterpack bots owns an inbound event, score ten ad variants in one call.
Do not use it to write text; Jev does not generate.

## Steps

1. Put the thing to judge in a JSON value (a string, or an object with named
   fields). Under about 30k tokens.
2. Write the questions. Three types:
   - `choice`: `{"type":"choice","instructions":"...","criteria":{"option":"what it means", ...}}` (1 to 255 options)
   - `score`: `{"type":"score","instructions":"...","criteria":["lowest level", ..., "highest level"]}` (2 to 10 levels)
   - `noul`: `{"type":"noul","instructions":"yes/no question"}` (returns a probability)
   Ask several at once; one request answers them all in parallel.
   Start from `/workspace/jev/examples/questions-support.json`.
3. Run `cd /workspace/jev && python3 ask.py --state /tmp/state.json --questions /tmp/q.json`.
4. Use probabilities and confidence, not just the top answer. Below 0.5
   confidence, say you are unsure. Put any threshold you rely on in the message
   so the owner can see it.

## Validate

The output has an `answers` object with one entry per question and a `usage`
block. Cost is `input_tokens * 0.042 / 1,000,000` USD.

## Return

The answers in a short table, then what you did with them.

## Requires approval

None. This skill only reads.
