**Severity:** LATENT · **Lane:** H_harness

# [SEAT] land-the-widened-world-past-the-two-reds-that-refused-it was claimed and has not moved for 3.3h

**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has
fired **1 times without its state changing**, over **3.5h**. Under the
director's instruction of 2026-08-20 a repeating alert escalates itself into the draw rather
than being sent again, so this document exists and a 1th page does not.

## The alarm, verbatim

```
[SEAT] land-the-widened-world-past-the-two-reds-that-refused-it was claimed and has not moved for 3.3h
No commit has touched its 3 claimed path(s) (docs/observability/RED_DISPOSITION_TWO_REDS_THAT_REFUSED_THE_COMPOSITE_LAND_2026-08-27.md, simulation/customer_events.py, tests/simulation/test_price_sensitivity_reaches_the_price_response.py) in that time. The claim is released and the work is drawable by any lane.
What the seat said it was doing: The land is the blocker and the two reds are named, so start there rather than relaunching. `docs/observability/three_arm_composite_run.log` ends `END rc=1 PHASE=land -- gate refused, A/B deliberately
```

## What is known without diagnosing anything

- Signature: `seat-claim:land-the-widened-world-past-the-two-reds-that-refused-it` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-08-27T20:56:00+00:00
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
