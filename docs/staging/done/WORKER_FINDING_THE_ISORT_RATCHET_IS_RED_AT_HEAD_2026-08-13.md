# [WORKER-FINDING] The static-quality ratchet is red at HEAD, and it is nobody's commit (2026-08-13)

**Severity:** BLOCKING · **Lane:** H_harness · **Status:** measured and reported, not fixed — the
excess is two I001 blocks in files this tick never touched.

## The measurement

`tests/architecture/test_static_quality_ratchet.py` fails two ways on the shared tree:

```
test_ruff_no_rule_exceeds_baseline      I001: baseline 1379, now 1380
test_ruff_baseline_matches_frozen_census changed: {'I001': (1379, 1380)}
```

`observed-with-evidence`, and deliberately measured against the repo rather than the desk, because
the working tree carries 224 modified paths from several lanes and "it is not mine" is exactly the
claim that needs an independent source:

* **HEAD, via `git archive HEAD | tar -x` into a clean directory, then ruff: I001 = 1381.** The
  baseline was frozen at 1379 on 2026-08-06. HEAD is +2.
* **Working tree: I001 = 1380.** One below HEAD, because another lane's uncommitted edit to
  `tests/background/test_tree_divergence.py` removes one (old=1, new=0).
* **This tick's files contribute zero.** Per-file before/after over every path in
  `git diff HEAD --name-only -- '*.py'` shows no other file's count moved, and ruff passes cleanly
  on all six files KNIFE3 step 22 added or edited.

So the ratchet has been red since some commit on or before `6045ab956`, and the count that made it
red is not in any current lane's diff.

## Why this matters more than two import blocks

The ratchet's own failure text says *"Fix the new violations — do not raise the baseline"* — correct
policy. But a ratchet that is red at HEAD for reasons no current author can attribute stops being a
ratchet and becomes weather: the next person to run the architecture suite sees two failures, cannot
tie them to their own change, and learns to read this suite's red as background noise. That is how a
control dies without anyone deciding to kill it.

It has not blocked commits — `f4b504e6c`, `6045ab956` and `357f8fa77` all landed — which means the
pre-commit gate does not select this suite for the paths those commits touched. **That is the more
interesting half of the finding:** the control is red, and the gate that is supposed to notice reds
does not reach it. A ratchet only the architecture suite runs is a ratchet that reds silently for as
long as nobody runs the architecture suite.

## Recommendation

`python3 -m ruff check --select I001 --fix` over the two offending blocks and re-freeze nothing —
the baseline is already correct at 1379 and the tree should come back to it. Identifying the two
blocks costs one scripted pass over the HEAD export (the census prints filenames); it is queued
rather than done here because fixing an unattributed lint in someone else's files during a KNIFE
commit is how a pathspec commit ends up carrying another lane's hunks, which this repo has a
standing rule against.

The second half — whether the pre-commit gate should always run the static-quality ratchet
regardless of pathspec, on the grounds that a repo-wide census is not decomposable by pathspec — is
a real design question and belongs with the existing finding of that name, not decided here.

---

## DISCHARGED 2026-08-13 (worker tick, RUNG 1c blocking draw)

**Repaired at source, baseline unmoved, verified against the committed tree.**

* `9ff64a8e2` — the two I001 blocks named by the census diff:
  `tests/tools/test_pre_commit_gate_class_checker.py` (landed in `f4b504e6c`) and
  `tests/background/test_tree_divergence.py` (isort fix existed ONLY as an uncommitted
  working-tree edit — which is why the desk read 1380 and HEAD read 1381).
* `70660179e` — **a second red this finding could not see.** Clearing I001 exposed
  `E731: baseline 19, now 20` at HEAD: `tests/background/test_gap_ledger_reconciler.py` grew an
  assigned lambda in `7a9bf56be`, and *its* repair was ALSO sitting uncommitted. The finding quoted
  the I001 lines only, so the second code was hidden behind the first in exactly the way the
  2026-08-09 episode-3 note in the ratchet's own shrink log describes.

**Consumer-verified (R1/R11 for a control): `git archive HEAD | tar -x` into a clean directory,
then the whole suite in that export — `13 passed`, I001 = 1379, E731 = 19.** Not the working tree,
which is the tree that understated both counts in the first place.

Both no-move repairs are recorded in the ratchet's SHRINK LOG with the attribution this tick had to
re-derive by census diff, plus the lesson: **re-run the WHOLE ratchet against a fresh HEAD export
after clearing one rule** — a per-rule fix proves nothing about the other codes.

**Still owed, and deliberately NOT decided here:** the finding's second half — the pre-commit gate
selects test files by path stem, so it never reaches this suite for the commits that reddened it,
and a repo-wide census is not decomposable by pathspec. That is
`WORKER_FINDING_A_REPO_WIDE_CENSUS_IS_NOT_DECOMPOSABLE_BY_PATHSPEC_2026-08-12.md`, which is live and
carries the design question. Until it is built, this class recurs silently: **two of the three
offending files here had their repair sitting uncommitted, so the desk was green while HEAD was red
in two different rules on the same day.**
