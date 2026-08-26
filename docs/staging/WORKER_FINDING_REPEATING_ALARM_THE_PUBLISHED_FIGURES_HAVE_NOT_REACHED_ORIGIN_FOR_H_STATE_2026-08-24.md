**Severity:** LATENT · **Lane:** H_harness

# [PUBLISHING DOWN] The published figures have not reached origin for 2.2h (state=stale). The tick may look healthy and the heartbeat may still be landing on origin: those are the LI

**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has
fired **3 times without its state changing**, over **0.2h**. Under the
director's instruction of 2026-08-20 a repeating alert escalates itself into the draw rather
than being sent again, so this document exists and a 3th page does not.

## The alarm, verbatim

```
[PUBLISHING DOWN] The published figures have not reached origin for 2.2h (state=stale). The tick may look healthy and the heartbeat may still be landing on origin: those are the LIVENESS surface and they do not move with the figures. Check sim-runner-log.md for the publish outcome -- a commit killed by the pre-commit hook deadline is the 2026-08-13 shape.
```

## What is known without diagnosing anything

- Signature: `content_publishing_state` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-08-24T08:38:46+00:00
- Repeats before escalation: 3 (threshold `ESCALATE_AFTER_REPEATS`)
- Paging for this signature is now SUPPRESSED. It resumes automatically the moment the
  underlying state changes — including when it clears.

## What this document is asking for

The repetition is the finding. Something is failing the same way on a loop and nothing is
converging on it, which is the shape the director named as "a symptom, not an event". Draw
this, diagnose the condition named above, and either fix it or record why the alarm is wrong.

Archive to `docs/staging/done/` when the condition is resolved. Re-escalation is not
suppressed by this file: a NEW episode on a later day files a new document, so a condition
that returns next week is not silently absorbed into today's record.

## Still live
- **2026-08-25** — still live. 3 repeats over 0.2h without the state changing. No second document filed: this condition already has one.
- **2026-08-26** — still live. 3 repeats over 0.2h without the state changing. No second document filed: this condition already has one.
