**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [ACTION NEEDED] Run-marker sweep has made ZERO progress for 3 consecutive cycles: run_complete_20260921T131342Z.md is still the oldest of 1 pending run_complete marker(s). Last pub

<!-- counts:begin -->
**Filed automatically by `background/alarm_repetition.py`, not by a person.** This condition
has been **observed to hold on 4 separate day(s)**, between **2026-09-21** and **2026-09-24**,
and **1 member(s)** of the family `auto:c22650dec5bb5cda` have fired. Both counts are DERIVED
from this document's own dated lines every time the alarm fires again, so they age with the
document rather than with its first firing.

Separately, the observer that last filed reported **6 consecutive firing(s) without a state
change**, over **11.4h**. That is `notify()`'s streak counter, which resets; it is not a total
and does not combine with the two counts above.
<!-- counts:end -->

## The alarm, verbatim

```
[ACTION NEEDED] Run-marker sweep has made ZERO progress for 3 consecutive cycles: run_complete_20260921T131342Z.md is still the oldest of 1 pending run_complete marker(s). Last publisher outcome for it: rc=75 (lock-skipped, not attempted) at 13:48Z. The sweep IS re-attempting every pending marker each cycle (unconditional glob) — so this is the publish path failing, not the retry loop stopping. Look at the publish gate's blocking test in docs/observability/sim-runner-log.md, not at the sweep.
```

## What is known without diagnosing anything

- Signature: `auto:c22650dec5bb5cda` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-09-21T09:43:34+00:00
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
- **2026-09-22** — still live. 3 repeats over 4.3h without the state changing. No second document filed: this condition already has one.
- **2026-09-23** — still live. 3 repeats over 4.7h without the state changing. No second document filed: this condition already has one.
- **2026-09-24** — still live. 5 repeats over 9.2h without the state changing. No second document filed: this condition already has one.
## Instances seen
- `run-marker sweep has made zero progress for # consecutive cycles: run_complete_#t#z.md is still the oldest of # pending ` (first seen 2026-09-21)

## Re-asked
- **2026-09-24** — re-asked: **still_holds**. observed 2026-09-24, within the 3-day bar.
- **2026-09-25** — re-asked: **still_holds**. observed 2026-09-24, within the 3-day bar.
- **2026-09-26** — re-asked: **still_holds**. observed 2026-09-24, within the 3-day bar.
- **2026-09-27** — re-asked: **still_holds**. document last annotated 2026-09-24, but `auto:c22650dec5bb5cda` fired 7.7h ago in the notify transition store, which contradicts the silence.
- **2026-09-28** — re-asked: **still_holds**. document last annotated 2026-09-24, but `auto:c22650dec5bb5cda` fired 31.7h ago in the notify transition store, which contradicts the silence.
- **2026-09-29** — re-asked: **still_holds**. document last annotated 2026-09-24, but `auto:c22650dec5bb5cda` fired 55.7h ago in the notify transition store, which contradicts the silence.
- **2026-09-29** — re-asked: **cleared**. no observation since 2026-09-24, past the 3-day bar; `auto:c22650dec5bb5cda` last fired 72.0h ago; and the machinery observed other conditions on 2026-09-29, so the silence is the observers running and not seeing it.

## Re-asked and cleared, 2026-09-29

Archived by `background/alarm_repetition.reask()`, not by a person, and not because anybody diagnosed it.

- **What was asked:** has the condition behind `auto:c22650dec5bb5cda` been observed to hold since it was last annotated?
- **Last observation:** 2026-09-24
- **The answer, and what carried it:** no observation since 2026-09-24, past the 3-day bar; `auto:c22650dec5bb5cda` last fired 72.0h ago; and the machinery observed other conditions on 2026-09-29, so the silence is the observers running and not seeing it.
- **What this does NOT claim:** that the condition was fixed, or why it stopped. Only that nothing has observed it for 3 days while the observers were demonstrably running. If it returns it files a FRESH document — `escalate()` does not search `done/` — and that fresh document is an R3 two-strike signal worth more than this one was.

