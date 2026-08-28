**Severity:** LATENT · **Lane:** H_harness

# [SEAT] rerun-the-three-arm-ab-on-the-repaired-clock-and-restate-the-headline was claimed and has not moved for 1.9h

**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has
fired **1 times without its state changing**, over **2.0h**. Under the
director's instruction of 2026-08-20 a repeating alert escalates itself into the draw rather
than being sent again, so this document exists and a 1th page does not.

## The alarm, verbatim

```
[SEAT] rerun-the-three-arm-ab-on-the-repaired-clock-and-restate-the-headline was claimed and has not moved for 1.9h
No commit has touched its 2 claimed path(s) (simulation/run_phase2b.py, tests/simulation/test_run_phase2b.py) in that time. The claim is released and the work is drawable by any lane.
What the seat said it was doing: `tools/run_value_cycle_ab.py` was repaired this stretch but has not been RUN since, so `docs/observability/value_cycle_ab_s1_three_arm.json` is entirely pre-repair: its keys are `control_arm`/`value_a
```

## What is known without diagnosing anything

- Signature: `seat-claim:rerun-the-three-arm-ab-on-the-repaired-clock-and-restate-the-headline` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-08-28T02:30:54+00:00
- Repeats before escalation: 1 (threshold `ESCALATE_AFTER_REPEATS`)
- Paging for this signature is now SUPPRESSED. It resumes automatically the moment the
  underlying state changes — including when it clears.

## What this document is asking for

The repetition is the finding. Something is failing the same way on a loop and nothing is
converging on it, which is the shape the director named as "a symptom, not an event". Draw
this, diagnose the condition named above, and either fix it or record why the alarm is wrong.

Archive to `docs/staging/done/` when the condition is resolved. While this document is live
-- here or in `in_progress/` -- a continuing condition APPENDS a dated line below rather than
filing a second document (2026-08-24). A condition that returns AFTER this has been archived
files a fresh document, because that is a new episode and an R3 two-strike signal.

## Still live
