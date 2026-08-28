**Severity:** LATENT · **Lane:** H_harness

# [SEAT] land-the-widened-world-then-run-the-three-arm-ab-once was claimed and has not moved for 2.5h

**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has
fired **1 times without its state changing**, over **5.3h**. Under the
director's instruction of 2026-08-20 a repeating alert escalates itself into the draw rather
than being sent again, so this document exists and a 1th page does not.

## The alarm, verbatim

```
[SEAT] land-the-widened-world-then-run-the-three-arm-ab-once was claimed and has not moved for 2.5h
No commit has touched its 4 claimed path(s) (docs/staging/done/WORKER_FINDING_REPEATING_ALARM_RE_RUN_THE_THREE_ARM_AB_ON_THE_S_WORLD_2026-08-27.md, docs/staging/done/WORKER_FINDING_THE_OOM_VICTIM_COUNTER_IS_THE_HARNESS_READING_ITS_OWN_SELFTEST_BACK_2026-08-27.md, docs/staging/done/WORKER_FINDING_THE_PASS_THROUGH_IC_CUSTOMER_PRODUCES_NO_RECORDS_AND_NO_GATE_CAN_SEE_IT_2026-08-27.md, docs/staging/in_progress/LANE0_THREE_ARM_AB_ON_THE_S1_WORLD_2026-08-27.md) in that time. The claim is released and the work is drawable by any lane.
What the seat said it was doing: Two acts, in order. FIRST, dispose of the dead run honestly. `docs/observability/three_arm_s1_run.log` has its `START pid=1128717 pgid=1128717 sess=1128717 at=2026-08-27T15:08:25Z` line, 56,229 lines
```

## What is known without diagnosing anything

- Signature: `seat-claim:land-the-widened-world-then-run-the-three-arm-ab-once` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-08-27T19:11:37+00:00
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
