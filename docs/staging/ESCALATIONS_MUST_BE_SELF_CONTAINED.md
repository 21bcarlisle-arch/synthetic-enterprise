# ESCALATIONS MUST BE ANSWERABLE FROM THE NTFY ALONE (P1, director-decided — tightens H19)

**Staged:** 2026-07-16 by advisor, **director-decided**. Disposition: QUEUE-high.
Tightens H19 (escalation-is-NTFY). H19 fixed the CHANNEL (phone not window) but
not the CONTENT: today's executor-wall NTFY said "I hit a one-way door, decide at
your cadence" but did NOT say WHAT the door was — it pointed at
build-executor-log.md on the box. That defeats the async design: the director
cannot answer from his phone; he has to open a terminal. Half an escalation.

## The rule
**An escalation NTFY must be SELF-CONTAINED and answerable from the notification
alone.** It MUST carry, in the message body:
1. **WHAT** — the specific decision, named (the atom + the exact choice), not "a
   one-way door."
2. **OPTIONS** — the actual choices (e.g. "open Epoch 4 for B4 / defer B4 / drop
   B4"), so the reply can be a single word.
3. **CONTEXT** — the minimum needed to choose, in the message (current state,
   what each option implies at the extremes). Not a link to a log.
4. **WHY IT'S A DOOR** — which one-way-door class (values/epoch, platform-admin,
   money, security), so the director knows why it reached him and not the twin.
5. **DEFAULT / NON-BLOCKING NOTE** — confirm the loop continues meanwhile and, if
   there is a safe default on no-reply, state it.

**A link to an on-box log is NOT an escalation** — it is a promissory note for
one. The director must be able to reply "yes / no / option B" from a phone with
no terminal.

## Test
Inject an escalation; confirm the NTFY alone contains the named decision, the
options, the context, and the door-class — such that a one-word phone reply
resolves it. An escalation that requires opening a file to understand FAILS.

## Relationship to the map
Folds into H19 (escalation mechanism). H19's DoD gets this content contract added.
Same spirit as the whole escalation design: the director steers async, from his
phone, without being chained to the box — that only works if the escalation
carries its own decision.

## DoD
Escalation payload schema requires WHAT/OPTIONS/CONTEXT/WHY-DOOR/DEFAULT in the
NTFY body; log references become supplementary, never the substance; a
mutation-style check that an escalation missing the named decision or options
FAILS; folded into H19.
