# [WORKER-FINDING] The ruff baseline has an entry that is green only because of uncommitted work

**Found:** 2026-08-09, while unwedging publish episode 3 (commit `8a8ee4d40`).
**Disposition:** QUEUED per SELF_INTERRUPT_DISCIPLINE. Not fixed on sight — the machine is
**not** blocked (the gate lints the working tree, which is green).
**Rank:** backlog, but promote the moment anyone touches `saas/reporting/annual_report.py`.
**Supersedes:** `WORKER_FINDING_RUFF_RATCHET_RED_ON_COMMITTED_HEAD_2026-08-09.md` — that
finding's three named rules (F401, F811, I001) are all resolved; this carries forward the one
half that is still live, under the correct cause.

## Observed, with evidence

`RUFF_BASELINE["E402"] = 193` matches the working tree and **not** committed `HEAD`:

```
$ git archive HEAD | tar -x -C /tmp/headtree2
HEAD census : E402 194   I001 1386   TOTAL 2413
WORK census : E402 193   I001 1386   TOTAL 2412
per-file diff: saas/reporting/annual_report.py  HEAD=18  WORK=17
```

The single missing E402 is inside the **uncommitted** KNIFE1 edit to
`saas/reporting/annual_report.py` (`git diff --stat` = 39 insertions, 62 deletions — an
in-flight change, not a one-line import removal, which is why it was left alone rather than
opportunistically committed by the unwedge tick).

The shrink log entry that set this floor says so almost in as many words — it recorded
`E402 194 -> 193 (KNIFE pass 1, atom KNIFE1_reporting_cycle)` as though the fix had landed.
It had not. The file's own docstring already warns against exactly this shape: *"a baseline
that depends on one concurrent writer's unsaved work."* It then did it.

## Why this is the wedge class, one step removed

The known class is *"the gate lints the WORKING TREE, so one uncommitted lint error wedges
publishing for everyone."* This is its **mirror image**: an uncommitted lint *fix* holds the
baseline up. It is invisible while the work sits in the tree and reds the moment the work
goes away — a revert, an abandoned atom, a fresh clone, or any worktree-isolated agent. The
failure would surface as a publish wedge with no attributable cause in any commit, which is
the most expensive possible way to find it (episode 2 cost ~7 hours and ten markers under a
directly analogous mis-attribution).

Note the asymmetry with the half that was fixed this tick: `I001 = 1386` is now identical on
HEAD and in the working tree, so it is robust to either outcome. `E402` is not.

## What closing it needs

Either is acceptable; both are reversible:

1. **Land the KNIFE1 edit** (its owner's call — it is mid-flight), after which HEAD and the
   working tree agree at 193 and nothing else is needed; or
2. **Re-freeze `E402` to 194** to match committed HEAD, and let the KNIFE1 landing shrink it
   to 193 in the same commit that removes the violation — which is the discipline the file
   already asks for ("re-freeze in the SAME PR").

**Do not** simply raise E402 while the working tree still reads 193 — that would red the
`test_ruff_no_stale_baseline_entries` check instead, trading one wedge for the other.

## The general defect worth mechanising (the reason this is filed, not just fixed)

`real_ruff_counts()` reads `REPO_ROOT` — the working tree — so **no ratchet test can currently
tell a committed floor from a borrowed one.** A cheap, R15-shaped control would be a test that
censuses a `git archive HEAD` extraction and asserts it equals the working-tree census, failing
loudly with the per-file diff when they diverge. That control would have caught this entry on
the day it was frozen, and would have caught the I001 half of episode 3 as well. It is testable
against its own defect in both directions (dirty tree with an extra violation; dirty tree with
a missing one), so it can be mutation-proven rather than asserted.
