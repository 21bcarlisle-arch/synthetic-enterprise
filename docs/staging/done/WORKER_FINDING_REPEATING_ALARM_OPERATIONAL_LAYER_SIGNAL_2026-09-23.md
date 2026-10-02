**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [OPERATIONAL LAYER BLOCKED] The independent-cadence operational-layer signal could not RUN for 4 consecutive check(s) (rc=2): pytest was interrupted during COLLECTION, so the marke

<!-- counts:begin -->
**Filed automatically by `background/alarm_repetition.py`, not by a person.** This condition
has been **observed to hold on 4 separate day(s)**, between **2026-09-23** and **2026-09-29**,
and **2 member(s)** of the family `operational_layer_signal` have fired. Both counts are
DERIVED from this document's own dated lines every time the alarm fires again, so they age with
the document rather than with its first firing.

Separately, the observer that last filed reported **4 consecutive firing(s) without a state
change**, over **2.7h**. That is `notify()`'s streak counter, which resets; it is not a total
and does not combine with the two counts above.
<!-- counts:end -->

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
- `the independent-cadence operational-layer signal (`pytest -m operational`, deselected from the content publish gate so i` (first seen 2026-09-25)
## Re-asked
- **2026-09-24** — re-asked: **still_holds**. observed 2026-09-23, within the 3-day bar.
- **2026-09-25** — re-asked: **still_holds**. observed 2026-09-23, within the 3-day bar.
- **2026-09-26** — re-asked: **still_holds**. observed 2026-09-25, within the 3-day bar.
- **2026-09-27** — re-asked: **still_holds**. observed 2026-09-26, within the 3-day bar.
- **2026-09-28** — re-asked: **still_holds**. observed 2026-09-26, within the 3-day bar.
- **2026-09-29** — re-asked: **still_holds**. document last annotated 2026-09-26, but `operational_layer_signal` fired 70.5h ago in the notify transition store, which contradicts the silence.
- **2026-09-30** — re-asked: **still_holds**. observed 2026-09-29, within the 3-day bar.
- **2026-10-01** — re-asked: **still_holds**. observed 2026-09-29, within the 3-day bar.
- **2026-10-02** — re-asked: **still_holds**. document last annotated 2026-09-29, but `operational_layer_signal` fired 67.1h ago in the notify transition store, which contradicts the silence.
- **2026-10-02** — re-asked: **cleared**. no observation since 2026-09-29, past the 3-day bar; `operational_layer_signal` last fired 72.0h ago; and the machinery observed other conditions on 2026-10-02, so the silence is the observers running and not seeing it.

## Re-asked and cleared, 2026-10-02

Archived by `background/alarm_repetition.reask()`, not by a person, and not because anybody diagnosed it.

- **What was asked:** has the condition behind `operational_layer_signal` been observed to hold since it was last annotated?
- **Last observation:** 2026-09-29
- **The answer, and what carried it:** no observation since 2026-09-29, past the 3-day bar; `operational_layer_signal` last fired 72.0h ago; and the machinery observed other conditions on 2026-10-02, so the silence is the observers running and not seeing it.
- **What this does NOT claim:** that the condition was fixed, or why it stopped. Only that nothing has observed it for 3 days while the observers were demonstrably running. If it returns it files a FRESH document — `escalate()` does not search `done/` — and that fresh document is an R3 two-strike signal worth more than this one was.

