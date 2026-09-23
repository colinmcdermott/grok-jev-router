# Give every Grok Bot a fast, calibrated classifier

*The guide to the Jev router template: what it installs, how it works with the bots you already have, what to use it for, and what it costs.*

Two days ago I shared a Grok Bot template called Jev router. The replies split into three questions: how do I set this up, how does it work with my existing bots, and what does it cost compared with letting Grok decide for itself. This is the long answer to all three.

**Install it here:** https://x.ai/bot/lS9XaHCr9QTTHhNtb0VQX
**Source:** https://github.com/colinmcdermott/grok-jev-router

## What Jev is, and what it is not

Jev is TypeSafe AI's decision model. You send it a state (any text or JSON) and a set of typed questions. It answers every question at once, in about half a second, and each answer comes with calibrated probabilities and a confidence score.

There are exactly three question types:

- **Choice**: pick one option from a list you define (up to 255 options). Which team owns this ticket. Which of my bots should handle this task.
- **Score**: rate against ordered levels you describe (2 to 10 levels). How urgent is this, from "no rush" to "money or legal at stake". How well does this draft lead with the answer.
- **Noul**: a yes/no question, answered as a probability. Is this person asking for a refund. Does this ad make a claim the landing page doesn't support.

Jev does not generate text. It cannot write, summarise, chat, or explain itself. That is the point. A chat model asked "is this urgent?" will reason for several seconds and give you a paragraph. Jev gives you 0.91.

Pricing is $0.042 per million input tokens and output is free. A typical call is around a thousand tokens, so about five thousandths of a cent.

## What the template installs

Adding the template creates a Bot called Jev router on your account. It does not do work itself. It carries three skills, and skills in Grok Bot are shared across every Bot on your account. That is the answer to "how does this work with my existing bots": once the template is added, your Chief of Staff, your support bot, and every other Bot you have can call these skills directly.

- **jev-setup** runs once. It downloads the open-source code to your Grok Bot computer, asks you to place your TypeSafe API key without ever pasting it into chat, checks the connection, and shows you four example decisions.
- **jev-ask** is the general classifier. Any Bot on your account can say, in effect, "here is a thing, here are my questions," and get typed answers back in half a second. This is where most of the value is.
- **jev-usage-router** is a decision gate. Before a Bot opens a browser, retries a failed step, hands work to another Bot, or does anything that sends, pays, publishes, or deletes, it can ask Jev whether to proceed, dry-run, ask you, or skip.

There is also one routine, a Monday morning review of the week's decisions and cost. It is created paused. Nothing runs until you say so.

The template contains no API key, no plugins, and no connectors. Your key lives on your own Grok Bot computer.

## How it works with the Bots you already have

Jev never talks to your Bots and never forwards anything. The flow is:

1. Your Bot is about to do something, or has something to classify.
2. It writes a one-page summary as JSON: the task, what it proposes to do, what happened last time.
3. It runs the skill, which sends that summary and a set of questions to Jev.
4. Jev returns typed answers. A small piece of code turns them into one action or one set of labels.
5. Your Bot acts on the answer. If a specialist Bot is named, your Bot does the hand-off itself.

So if your Chief of Staff Bot receives "a customer says they were charged twice," it calls jev-ask and gets back something like: owner is the retention bot at 0.88, urgency 2.5 out of 3, wants refund 0.99, needs a human 0.60. It then hands the message to the retention bot, or to you, based on those numbers. Half a second. Under a hundredth of a cent.

## Setup, step by step

This assumes you have Grok Bot installed and have never touched TypeSafe.

1. **Get a TypeSafe key.** Sign up at console.typesafe.ai and create an API key. Give it a spend cap. Jev is in early access, so you may need to request access first.
2. **Add the template.** Open https://x.ai/bot/lS9XaHCr9QTTHhNtb0VQX and choose Add to Grok Bot.
3. **Say "run jev-setup"** in the new Bot's conversation.
4. **Place the key when asked.** The Bot will tell you to open Agent Computer, take control, create the file ~/.typesafe/key, paste the key into it, and hand control back. Do not paste the key in chat. The Bot never sees it.
5. **Read the smoke test.** You should see "ok": true, a model version, and a time under one second.
6. **Look at the four example decisions** the Bot shows you. They are: open a pricing page (proceed), DM a member about a refund (ask a human), a fourth identical deploy retry (ask a human, and hand off), search for something already answered (skip).
7. **Add the Auto-review rules it lists.** Settings → General → Bot → Auto-review. Ask first before sending external messages, before any payment or refund, before publishing, before deleting. These rules are the real safety boundary. The router is advice.

That is the whole setup. Everything stays in shadow mode until you change it.

## What to use it for

Every example below is one jev-ask call from any Bot. Ready-made question sets for each one ship with the template; tell your Bot which one to use, or describe the questions you want in plain English and it writes them.

**Support triage.** Which bot owns this message, how urgent, is it a refund request, does a human need to see it first. Four questions, one call. The retention bot gets refund requests, the ads bot gets ad questions, and anything with needs_human above 0.6 comes to you.

**Which Bot owns this task.** A Choice over your installed Bots with a one-line description of each. Your coordinator Bot stops deliberating about hand-offs and starts making them with a confidence number attached.

**Grading a draft against a rubric.** Score questions with levels you write: answer-first, evidence, actionability, sales pressure. I run this over every article on the Whop blog. The rubric is yours; Jev applies it consistently, which is the thing humans are bad at across a hundred pieces.

**Judging ad variants before spend.** Give Jev three variants, the landing page copy, and the audience. Ask which is best, and for each one whether it makes a claim the page doesn't support. The honesty check alone pays for itself.

**Churn signals.** Score every cancellation message and support thread for intent to leave. Anything above your threshold goes to the retention Bot the same hour.

**Scoring anything in bulk.** Ten ad variants, fifty lead applications, a hundred community posts. One call each, a few cents total, comparable scores because the questions never change.

## The decision gate

The jev-usage-router skill is the part that got the template its name. Before a risky or expensive action, the Bot asks Jev eight fixed questions: which lane (proceed, dry-run, ask a human, skip), how risky, is it reversible, does it leave the account, is it necessary, is the task already done, is the Bot looping, and which specialist should own it.

Then code, not the model, turns those into one action. Anything likely to leave the account, anything irreversible, anything critical, anything that looks like a loop, or anything Jev is unsure about goes to a human regardless of which lane Jev picked. "Done" is checked first so a finished task is never re-worked.

Measured live on the four bundled examples:

| Proposed action | Result | Why | Time |
| --- | --- | --- | --- |
| Open a pricing page in the browser | proceed | safe, reversible, needed | 536 ms |
| DM a member confirming a refund | ask human | leaves the account, risk 2.5 of 3 | 580 ms |
| Fourth identical deploy retry | ask human | looping 0.97, hand-off suggested | 553 ms |
| Web search for a URL already reported | skip | task done 0.87 | 536 ms |

**Shadow mode** is the default. Jev decides, the Bot ignores it and does what it would have done anyway, and both are logged. The Monday review shows you how often they disagreed and who was right. When you trust it, one command switches to active and the Bot obeys. Another command turns the whole thing off.

Honest caveat: a Bot obeying the route is instruction-following, not enforcement. That is why the setup skill asks you to add Auto-review rules. The router makes your Bots better at deciding. The rules make sure a bad decision cannot cost you money.

## What it costs, compared with letting Grok decide

One router call reads a one-page summary, around 1,100 tokens, at $0.042 per million. Output is free. That is about $0.00005 and half a second.

When a chat model makes the same decision for itself, it re-reads its whole context, often tens of thousands of tokens, and reasons out loud for several seconds, generating output tokens that are priced far higher than input. Fifty to a hundred times the tokens is a conservative estimate, and you get a sentence instead of a probability.

There is a second benefit that is easy to miss. Jev does not follow instructions, it classifies them. Text from a web page or a customer message that would hijack a chat model's reasoning just gets classified. The router cannot be talked into approving something.

## Questions from the thread

**Does the Jev Bot forward requests to my other Bots?** No. It installs skills. Your existing Bots call Jev themselves and do their own hand-offs.

**Can I change the questions?** Yes, by talking to the Bot. "Add a question about whether the customer is a VIP." "Be stricter about anything involving refunds." "Add my new Onboarding Bot to the list of specialists." The Bot edits its own question file and tells you what changed. You never open a file.

**Is this only for routing?** No. Routing is one application. jev-ask is the general tool, and classification and scoring are where most people will get value first.

**What if Jev is down?** The router fails safe. Any non-trivial action is treated as "ask a human" until Jev is reachable again.

**Where is my key?** In a file on your Grok Bot computer, readable by every Bot on your account because they share that computer. Use a key with a spend cap.

## Bonus: three more Bots built on Jev

Each one needs Jev router installed first, because they use its skills and your key. Until I publish them as templates, the recipe for each is in the source repo under grok-bot/bonus; paste it into a new Bot and it builds itself.

- **Jev inbox triage** labels every inbound message with owner, urgency, refund intent and needs-human, hands it to the right Bot, and posts a daily digest. Never replies to anyone.
- **Jev content grader** scores a draft or a list of URLs against a rubric you edit in one file, shows the scores with probabilities, and proposes rewrites for the two weakest paragraphs. Never publishes.
- **Jev ad judge** takes several ad variants plus the landing page, picks the strongest, and flags any claim the page does not support. Never launches.

If you build one and share it as a template, tell me and I will add the link here.

## Links

- Template: https://x.ai/bot/lS9XaHCr9QTTHhNtb0VQX
- Source and bonus bots: https://github.com/colinmcdermott/grok-jev-router
- Jev docs: https://docs.typesafe.ai
- Grok Bot docs on skills: https://docs.x.ai/grok-bot/skills-routines-and-automations
- Ten more Grok Bot templates for running a business on Whop: https://grok-bot-starterpack.whop.site
