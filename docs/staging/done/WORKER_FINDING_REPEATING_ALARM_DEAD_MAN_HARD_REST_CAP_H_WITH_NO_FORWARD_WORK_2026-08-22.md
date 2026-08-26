**Severity:** LATENT · **Lane:** H_harness

# [ACT] Dead-man HARD REST CAP: 6.2h with no forward-WORK commit (liveness / chore / planner-rest-proof commits excluded). Rest exceeding 6h must raise an [ACT] in ANY circumstance -

**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has
fired **3 times without its state changing**, over **0.2h**. Under the
director's instruction of 2026-08-20 a repeating alert escalates itself into the draw rather
than being sent again, so this document exists and a 3th page does not.

## The alarm, verbatim

```
[ACT] Dead-man HARD REST CAP: 6.2h with no forward-WORK commit (liveness / chore / planner-rest-proof commits excluded). Rest exceeding 6h must raise an [ACT] in ANY circumstance -- proven-rest or not; 42h of quiet rest is itself the defect. Check the tick: is the authorized set genuinely empty at every level, or is a gate / mint batch deadlocked (EIGHTH CLASS 2026-07-27)?
```

## What is known without diagnosing anything

- Signature: `deadman_hard_rest_cap` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-08-22T16:15:44+00:00
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

- **Consolidated 2026-08-24.** This condition re-filed itself as a separate document on each of 2026-08-23. Those copies said the same thing about the same unchanged condition and are deleted, not archived — there was nothing in them this document does not carry. The mechanism that produced them is fixed in `background/alarm_repetition.py`: idempotence was keyed on a path containing the DATE, so an unchanged alarm refiled at every midnight. It is now keyed on the signature, and a continuing condition appends a line here instead.

## RESOLVED 2026-08-24 (worker tick, staging triage)

`git log` shows forward-work commits at 06:36, 07:11, 07:35, 07:39 and 08:09 today (pass-ceiling
build, 19-atom deletion, PB3 book growth, growth-mandate activation) — the condition (no
forward-WORK commit for 6.2h) no longer holds; the gap the alarm fired on has been filled by
several tick's worth of real landed work since. Archived as resolved, not fixed (there was
nothing to fix — the machine was never actually stuck; the alarm just outlived the episode it
described, consistent with `alarm_repetition.py`'s own note that paging resumes automatically the
moment the underlying state changes).

