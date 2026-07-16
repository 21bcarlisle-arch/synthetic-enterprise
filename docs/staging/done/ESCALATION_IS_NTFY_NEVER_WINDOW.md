# ESCALATION IS NTFY, NEVER THE WINDOW — the interactive pane is not a channel the director monitors (P0 WALL, director-decided)

**Staged:** 2026-07-16 by advisor, **director-decided**. Disposition: INTERRUPT
(this is a hard behavioural wall; it closes the channel gap the two-way-door doc
left open). Director, unambiguous: *"It keeps stopping and asking me things in
the window. This doesn't work for me ongoing. It has to be NTFY or don't stop."*

## The gap this closes
ROUTE_AROUND_BEFORE_STOPPING (5244c5d5) said escalate the irreducible core
"async." But the executor then escalated two genuine one-way doors (open Epoch 4?
restart the safety daemon?) **in the interactive window** — and the director
was not watching, so it became a silent stall (deadman fired BLOCKED at 74 min).
The rule was right that they should escalate; it was wrong about the CHANNEL.

## THE WALL (encode in CLAUDE.md as non-negotiable)
**The executor NEVER stops to ask the director in the interactive pane. EVERY
escalation goes to NTFY. Full stop.**
- The interactive window is NOT a channel the director monitors. A question
  asked there is invisible to him — indistinguishable from a crash until the
  deadman fires. It is a SILENT STALL by construction.
- There is no category of question that goes in the window. Not reversible-
  unclear (those mostly proceed-and-log per the door rule anyway), not genuine
  one-way doors (those NTFY). Nothing waits in the pane.

## The behaviour (combine with route-around + per-atom streaming)
When the executor hits something that genuinely needs the director:
1. **NTFY it** — crisp, minimal, the irreducible decision only, with enough
   context to answer from a phone (and the PIN convention for his reply).
2. **KEEP WORKING** — draw and complete other atoms while the escalation is
   outstanding. A single blocked atom must NEVER idle the loop.
3. **Only if NOTHING else is drawable** and the blocker is truly irreducible:
   NTFY and idle — but even then, the pane is silent; the deadman + health check
   are the safety net, and the NTFY is the ask. Never a window prompt.
4. Async by default: the director answers via NTFY at his cadence; the answer
   arrives as input at a turn/loop boundary. Steering is asynchronous, never a
   synchronous window-block.

## Why this is a WALL not a preference
The entire point of the autonomy work (F1, the headless loop, per-atom streaming)
is a company that runs WITHOUT the director watching a terminal. A stop-to-ask in
the window defeats all of it — it silently reintroduces the human-in-the-loop-at-
a-screen dependency the whole architecture exists to remove. This is the same
class as the banned keystroke injection: the interactive pane is the director's
console for HIM to drive when he chooses, never a channel the machine blocks on.

## What must NOT change
Genuine one-way doors still escalate (real money, values, security controls,
platform-admin, epoch opens) — they just escalate via NTFY, async, while other
work continues. The walls are unchanged; the CHANNEL is fixed to NTFY and the
loop is forbidden from idling in the pane.

## DoD
Executor escalation path hard-wired to NTFY only; the interactive pane is never
used to ask the director anything; blocked-on-irreducible-core NTFYs the minimal
decision and continues other atoms; loop never idles in the window; a check:
inject an irreducible escalation and confirm it appears as an NTFY and the loop
keeps drawing other work — and that NOTHING appears as a blocking window prompt.
