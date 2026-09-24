**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [OPERATIONAL LAYER BLOCKED] The independent-cadence operational-layer signal could not RUN for 4 consecutive check(s) (rc=2): pytest was interrupted during COLLECTION, so the marke

**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has
fired **3 times without its state changing**, over **2.2h**. Under the
director's instruction of 2026-08-20 a repeating alert escalates itself into the draw rather
than being sent again, so this document exists and a 3th page does not.

## The alarm, verbatim

```
[OPERATIONAL LAYER BLOCKED] The independent-cadence operational-layer signal could not RUN for 4 consecutive check(s) (rc=2): pytest was interrupted during COLLECTION, so the marker expression `operational or join_report_only or scale_report_only` never selected anything and NO operational test was executed. This is NOT a daemon-lifecycle regression -- nothing about the operational layer has been shown to be broken, and the published site/report is unaffected. The operational layer is UNMONITORED until these files import cleanly:
  - tests/tools/test_the_paired_floor_leg_runs_alone_in_its_own_process.py
  - tests/tools/test_the_paired_size_term_floor_cannot_report_a_contrast_it_never_ran.py

Repair the import error at those paths, not the daemons.
```

## What is known without diagnosing anything

- Signature: `operational_layer_signal` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-09-23T17:54:32+00:00
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
- `the independent-cadence operational-layer signal could not run for # consecutive check(s) (rc=#): pytest was interrupted` (first seen 2026-09-23)

## Re-asked
- **2026-09-24** — re-asked: **still_holds**. observed 2026-09-23, within the 3-day bar.
