**Severity:** LATENT · **Lane:** H_harness

# [SEAT] land-the-suspended-book-and-rerun-on-residential was claimed and has not moved for 1.7h

**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has
fired **1 times without its state changing**, over **4.7h**. Under the
director's instruction of 2026-08-20 a repeating alert escalates itself into the draw rather
than being sent again, so this document exists and a 1th page does not.

## The alarm, verbatim

```
[SEAT] land-the-suspended-book-and-rerun-on-residential was claimed and has not moved for 1.7h
No commit has touched its 2 claimed path(s) (docs/design/THE_VALUE_CYCLE_REALISED_AB.md, docs/staging/WORKER_FINDING_THE_AB_ARTEFACT_CANNOT_NAME_THE_BOOK_IT_RAN_ON_2026-08-26.md) in that time. The claim is released and the work is drawable by any lane.
What the seat said it was doing: Land the I&C suspension that is sitting uncommitted, then re-run the comparison on the book it creates. The suspension is finished work: `docs/design/curriculum/served_segments.json` in the working tr
```

## What is known without diagnosing anything

- Signature: `seat-claim:land-the-suspended-book-and-rerun-on-residential` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-08-26T19:03:51+00:00
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
