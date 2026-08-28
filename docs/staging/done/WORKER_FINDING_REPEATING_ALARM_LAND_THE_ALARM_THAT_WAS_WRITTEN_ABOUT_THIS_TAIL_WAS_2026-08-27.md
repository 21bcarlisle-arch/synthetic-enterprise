**Severity:** LATENT · **Lane:** H_harness

# [SEAT] land-the-alarm-that-was-written-about-this-tail was claimed and has not moved for 1.9h

**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has
fired **1 times without its state changing**, over **11.7h**. Under the
director's instruction of 2026-08-20 a repeating alert escalates itself into the draw rather
than being sent again, so this document exists and a 1th page does not.

## The alarm, verbatim

```
[SEAT] land-the-alarm-that-was-written-about-this-tail was claimed and has not moved for 1.9h
No commit has touched its 15 claimed path(s) (docs/context-handshake-latest.md, docs/staging/done/WORKER_FINDING_REPEATING_ALARM_DOCS_LEFT_UNCOMMITTED_BY_A_SESSION_THAT_STOPPED_MID_WORK_2026-08-26.md, docs/staging/done/run_complete_20260826T201941Z.md, docs/staging/done/run_complete_20260826T205458Z.md, docs/staging/done/run_complete_20260826T210700Z.md…) in that time. The claim is released and the work is drawable by any lane.
What the seat said it was doing: Land the remaining 31 diverged files by walking them, starting with the two that are about this defect itself. `background/tree_divergence.py` has 52 uncommitted lines adding `severity()` and `ESCALAT
```

## What is known without diagnosing anything

- Signature: `seat-claim:land-the-alarm-that-was-written-about-this-tail` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-08-26T23:13:54+00:00
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
