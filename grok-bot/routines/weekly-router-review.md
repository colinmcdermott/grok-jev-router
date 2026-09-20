# Routine: Weekly router review

Ask the Jev router Bot to create this routine:

> Every Monday at 08:00 (owner's time zone), run `cd /workspace/jev && python3 review.py --days 7`
> and post the result in this conversation as a short report: number of
> decisions, split by action, the top reasons for ask_human, hand-offs suggested,
> shadow-mode disagreement rate with three examples, router errors, total cost in
> USD, and median latency. If disagreement rate is under 10 percent for two
> weeks running and the owner has not switched to active, recommend switching
> and say exactly what changes. If a threshold in jev/questions.py looks wrong
> from the disagreements, propose the new value and the reason. Do not change
> config.json or thresholds yourself. If the logs folder is empty or missing,
> say so instead of inventing numbers.
