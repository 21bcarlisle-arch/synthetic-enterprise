**Severity:** LATENT · **Lane:** H_harness

# [ACTION NEEDED] Run-marker sweep has made ZERO progress for 3 consecutive cycles: run_complete_20260822T062533Z.md is still the oldest of 1 pending run_complete marker(s). Last pub

**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has
fired **3 times without its state changing**, over **5.5h**. Under the
director's instruction of 2026-08-20 a repeating alert escalates itself into the draw rather
than being sent again, so this document exists and a 3th page does not.

## The alarm, verbatim

```
[ACTION NEEDED] Run-marker sweep has made ZERO progress for 3 consecutive cycles: run_complete_20260822T062533Z.md is still the oldest of 1 pending run_complete marker(s). Last publisher outcome for it: rc=75 (lock-skipped, not attempted) at 06:13Z. The sweep IS re-attempting every pending marker each cycle (unconditional glob) — so this is the publish path failing, not the retry loop stopping. Look at the publish gate's blocking test in docs/observability/sim-runner-log.md, not at the sweep.
```

## What is known without diagnosing anything

- Signature: `auto:c22650dec5bb5cda` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-08-22T01:13:13+00:00
- Repeats before escalation: 3 (threshold `ESCALATE_AFTER_REPEATS`)
- Paging for this signature is now SUPPRESSED. It resumes automatically the moment the
  underlying state changes — including when it clears.

## What this document is asking for

The repetition is the finding. Something is failing the same way on a loop and nothing is
converging on it, which is the shape the director named as "a symptom, not an event". Draw
this, diagnose the condition named above, and either fix it or record why the alarm is wrong.

Archive to `docs/staging/done/` when the condition is resolved. Re-escalation is not
suppressed by this file: a NEW episode on a later day files a new document, so a condition
that returns next week is not silently absorbed into today's record.

## Disposition 2026-08-22T14:00Z — CONDITION RESOLVED, archived

The alarm's own text named the right place to look and the right non-cause: the sweep was
re-attempting every cycle, and the failure was in the publish path. It cleared without this
document being drawn, because the publish path itself was repaired.

Read off disk and git, not inferred:

- **Zero pending markers.** `ls docs/staging/run_complete_*.md` returns nothing. The named
  subject `run_complete_20260822T062533Z.md` is no longer the oldest of anything; the last
  three markers are all in `docs/staging/done/` (`...T133437Z`, `...T122526Z`, `...T115957Z`).
- **The publish path completes end to end.** `docs/observability/sim-runner-log.md` for the
  13:43–13:53Z cycle shows the gate scoping (6 publish-path sources → 161 blocking test
  files), then `Moved run_complete_20260822T133437Z.md to done/`, then
  `Provenance: Verified 2026-08-22T13:53:00Z`, then `Committing and pushing`. That is the
  rc=75 lock-skip replaced by a completed attempt.
- **It is landing, repeatedly.** `git log` carries an `Auto-process run complete` commit at
  11:18, 11:43, 12:53, 13:18 and 13:44 BST — the ~25-minute cycle, unbroken.

What actually fixed it is in the record already: the 2026-08-21 22:00–23:55 run of publish-gate
repairs (`0e34576d9`, `2f2aed651`, `a5c7ba79b`, `d31555c23`, `4b171cee8`, `fc1ba48f2`), which
took the gate's blocking set from six reds failing on a guard rather than on their subject to
green. The alarm's last recorded outcome (rc=75 at 06:13Z) predates the last of those landing
in a cycle that then ran.

**No code change is owed by this document.** The alarm was correct, it was pointed at the right
evidence, and its condition is gone. Paging for signature `auto:c22650dec5bb5cda` resumes
automatically on the next state change, so nothing here suppresses a recurrence.
