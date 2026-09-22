**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [SIM] PUBLISH REFUSED, ORIGIN AHEAD -- origin/main is 7 commit(s) AHEAD of HEAD (collides with 2 of ours: docs/status/LATEST.md), so a commit here could only be rejected non-fast-f

**Filed automatically by `background/alarm_repetition.py`, not by a person.** This alarm has
fired **3 times without its state changing**, over **3.7h**. Under the
director's instruction of 2026-08-20 a repeating alert escalates itself into the draw rather
than being sent again, so this document exists and a 3th page does not.

## The alarm, verbatim

```
[SIM] PUBLISH REFUSED, ORIGIN AHEAD -- origin/main is 7 commit(s) AHEAD of HEAD (collides with 2 of ours: docs/status/LATEST.md), so a commit here could only be rejected non-fast-forward and would widen the fork by one more. Reconcile first: `python3 -m background.origin_reconcile` -- the gated merge, in an ISOLATED worktree. Never `surgical_land --merge origin/main` in the shared tree: it opens the shared index that three lanes routinely hold work in -- no commit was created, so the fork is not one wider than it was. The mechanical advance was tried first and did not clear it: this tree holds 3 commit(s) of its own, so the fork is REAL and closing it is a judgement: it needs the gated merge door, which is longer than a publish cycle. OWNED BY `python3 -m background.origin_reconcile` on the deadman cadence, which merges in an ISOLATED worktree -- measured 2026-09-04, it closed 41 real forks unaided, so this is a state with an owner and not a state waiting on a reader. Nothing is wrong with the run or the suite, and this is NOT a call to action: `background/origin_reconcile` owns a real fork and closes it in an isolated worktree on the deadman cadence. If it CANNOT, the deadman pages separately ([ORIGIN FORK]) and that is the alarm to act on.
```

## What is known without diagnosing anything

- Signature: `auto:c731770f65ab5c82` — the alarm text with elapsed times, counters, hashes and timestamps
  normalised away, so this is the same CONDITION recurring, not the same string.
- First seen in this episode: 2026-09-20T02:28:44+00:00
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
- **2026-09-21** — still live. 3 repeats over 4.3h without the state changing. No second document filed: this condition already has one.
## Instances seen
- `publish refused, origin ahead -- origin/main is # commit(s) ahead of head (collides with # of ours: docs/status/latest.m` (first seen 2026-09-20)
