**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [ACTION NEEDED] Run-marker sweep has made ZERO progress for 3 consecutive cycles: run_complete_20260921T131342Z.md is still the oldest of 1 pending run_complete marker(s). Last pub

**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has
fired **3 times without its state changing**, over **4.2h**. Under the
director's instruction of 2026-08-20 a repeating alert escalates itself into the draw rather
than being sent again, so this document exists and a 3th page does not.

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
