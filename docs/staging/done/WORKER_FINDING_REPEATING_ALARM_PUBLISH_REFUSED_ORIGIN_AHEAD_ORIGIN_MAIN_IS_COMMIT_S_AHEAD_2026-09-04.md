**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [SIM] PUBLISH REFUSED, ORIGIN AHEAD -- origin/main is 4 commit(s) AHEAD of HEAD, so a commit created here could only be rejected non-fast-forward and would widen the fork by one mo

**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has
fired **3 times without its state changing**, over **1.4h**. Under the
director's instruction of 2026-08-20 a repeating alert escalates itself into the draw rather
than being sent again, so this document exists and a 3th page does not.

## The alarm, verbatim

```
[SIM] PUBLISH REFUSED, ORIGIN AHEAD -- origin/main is 4 commit(s) AHEAD of HEAD, so a commit created here could only be rejected non-fast-forward and would widen the fork by one more. Reconcile first: `python3 -m tools.surgical_land --merge origin/main` -- no commit was created, so the fork is not one wider than it was. Nothing is wrong with the run or the suite; the tree needs reconciling.
```

## What is known without diagnosing anything

- Signature: `auto:76dbcc7f5f569c55` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-09-04T13:05:16+00:00
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
- **2026-09-05** — still live. 3 repeats over 3.5h without the state changing. No second document filed: this condition already has one.
## Instances seen
- `publish refused, origin ahead -- origin/main is # commit(s) ahead of head, so a commit created here could only be reject` (first seen 2026-09-04)
