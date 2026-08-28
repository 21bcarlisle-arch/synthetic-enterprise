**Severity:** LATENT · **Lane:** H_harness

# [OPERATIONAL LAYER RED] The independent-cadence operational-layer signal (`pytest -m operational`, deselected from the content publish gate so it can never wedge the live site) has

**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has
fired **3 times without its state changing**, over **2.2h**. Under the
director's instruction of 2026-08-20 a repeating alert escalates itself into the draw rather
than being sent again, so this document exists and a 3th page does not.

## The alarm, verbatim

```
[OPERATIONAL LAYER RED] The independent-cadence operational-layer signal (`pytest -m operational`, deselected from the content publish gate so it can never wedge the live site) has been RED for 4 consecutive check(s) (rc=1). This does NOT affect the published site/report -- it is a daemon-lifecycle test regression. Failing tests:
FAILED tests/background/test_background_worker.py::test_processing_order_is_deterministic_sorted
FAILED tests/background/test_background_worker.py::test_no_published_run_yet_retires_nothing
FAILED tests/background/test_background_worker.py::test_a_failed_cycle_is_followed_by_another_attempt_without_human_touch
```

## What is known without diagnosing anything

- Signature: `operational_layer_signal` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-08-26T04:01:24+00:00
- Repeats before escalation: 3 (threshold `ESCALATE_AFTER_REPEATS`)
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
