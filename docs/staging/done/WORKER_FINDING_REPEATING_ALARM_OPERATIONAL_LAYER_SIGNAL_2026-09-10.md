**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [OPERATIONAL LAYER RECOVERED] The independent-cadence operational-layer signal (`pytest -m operational`, deselected from the content publish gate) is GREEN again after a persistent

**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has
fired **3 times without its state changing**, over **63.3h**. Under the
director's instruction of 2026-08-20 a repeating alert escalates itself into the draw rather
than being sent again, so this document exists and a 3th page does not.

## The alarm, verbatim

```
[OPERATIONAL LAYER RECOVERED] The independent-cadence operational-layer signal (`pytest -m operational`, deselected from the content publish gate) is GREEN again after a persistent red. Daemon-lifecycle tests recovered; the live site/report was never affected by the prior red.
```

## What is known without diagnosing anything

- Signature: `operational_layer_signal` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-09-07T17:51:22+00:00
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

## Instances seen
- `the independent-cadence operational-layer signal (`pytest -m operational`, deselected from the content publish gate) is ` (first seen 2026-09-10)
- `the independent-cadence operational-layer signal (`pytest -m operational`, deselected from the content publish gate so i` (first seen 2026-09-10)
