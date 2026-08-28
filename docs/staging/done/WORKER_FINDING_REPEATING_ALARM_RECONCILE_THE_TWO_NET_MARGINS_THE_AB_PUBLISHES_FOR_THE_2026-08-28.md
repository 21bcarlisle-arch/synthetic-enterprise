**Severity:** LATENT · **Lane:** H_harness

# [SEAT] reconcile-the-two-net-margins-the-ab-publishes-for-the-same-arm was claimed and has not moved for 1.8h

**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has
fired **1 times without its state changing**, over **2.6h**. Under the
director's instruction of 2026-08-20 a repeating alert escalates itself into the draw rather
than being sent again, so this document exists and a 1th page does not.

## The alarm, verbatim

```
[SEAT] reconcile-the-two-net-margins-the-ab-publishes-for-the-same-arm was claimed and has not moved for 1.8h
No commit has touched its 4 claimed path(s) (docs/observability/value_cycle_ab_s1_three_arm.json, docs/staging/WORKER_FINDING_THE_PUBLISHED_TREASURY_IS_ON_A_SUPERSEDED_CLOCK_BESIDE_A_REALISED_NET_MARGIN_2026-08-28.md, tests/tools/test_run_value_cycle_ab.py, tools/run_value_cycle_ab.py) in that time. The claim is released and the work is drawable by any lane.
What the seat said it was doing: `docs/observability/value_cycle_ab_s1_three_arm.json` publishes two net margins for the SAME control arm on the SAME run and they differ by GBP 39,962.17. Observed: `control_arm.total_net_gbp` = 113,2
```

## What is known without diagnosing anything

- Signature: `seat-claim:reconcile-the-two-net-margins-the-ab-publishes-for-the-same-arm` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-08-28T00:27:35+00:00
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
