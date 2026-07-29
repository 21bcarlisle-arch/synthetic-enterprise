# [DIRECTOR-RULING] — Fix the double-messaging. Twice is once too many. (2026-07-29)

**Type:** [DIRECTOR-RULING] via advisor bridge. Fix this properly, not with a filter on the symptom.

## What the director sees

His single ntfy message *"Opus 5 doesn't exist on this plan…"* appears **twice** in the mirror — 17:32:19 and 17:32:27, eight seconds apart, identical text — and each was separately acked and queued as an instruction. The same doubling happened earlier today with a staged-instruction doorbell, and again with the ntfy app's own test notifications.

**This is worrying and it is not cosmetic.** One director message becoming two queued instructions means a single act could be executed twice. Most of the time that is harmless noise; occasionally it will not be.

## Diagnose the mechanism, do not filter the symptom

Find out **why**, with evidence, before adding any de-duplication:

- Is the ntfy app or the network delivering the message twice?
- Is the poller reading the same message on consecutive cycles because the read cursor advances only on success — or not at all?
- Are **two consumers** subscribed (responder and worker, or two instances of one daemon left running after a restart)?
- Is the retry path re-processing an already-handled message after a partial failure?

**A de-duplication filter added without knowing the cause hides a second daemon or a broken cursor rather than fixing it.** Say plainly which of these it is.

## Then make it correct by construction

Every inbound message gets a **stable identity** (its ntfy message id, or a hash of body plus timestamp) recorded on handling, and **processing is idempotent**: a message already handled is acknowledged and dropped, never re-queued, never re-executed. **At-most-once execution for anything that acts** — at-least-once delivery is fine, at-least-once *execution* is not.

R15 both ways: the same message delivered twice must execute once; two genuinely different messages with similar text must both execute.

## While you are in there

The ntfy app's own **test notifications were queued as instructions** and each triggered a model load. Inbound text carries no authority and is untrusted data. **Anything that is not plausibly a director instruction should be acknowledged and discarded without spawning a model** — a message costing a GPU load is a cheap way for noise, or anyone who learns the topic, to waste the day.

## Report

One line: the cause, the fix, and confirmation that a duplicate now executes once. **Do not ask permission** — this is reversible plumbing.

— Advisor bridge, carrying the director's instruction. 2026-07-29.
