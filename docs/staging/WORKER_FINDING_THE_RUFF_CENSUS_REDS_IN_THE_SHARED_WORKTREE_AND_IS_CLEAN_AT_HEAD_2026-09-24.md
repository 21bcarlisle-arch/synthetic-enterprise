**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# FINDING — the ruff census reds in the shared worktree and is clean at HEAD, because two copies on disk are behind the commit that fixed them

Found 2026-09-24 while pre-running the cheap gates for
`ask-the-landed-unbound-join-before-the-draw-not-only-after-the-sweep`. The finding is not the
census red; it is that **the red is unreachable from any commit** and the obvious repair for it
reverts an already-landed one.

## What was measured

`pytest tests/architecture/test_static_quality_ratchet.py` in the shared worktree:

```
test_ruff_no_rule_exceeds_baseline   FAILED   F401: baseline 264, now 269
test_ruff_baseline_matches_frozen_census  FAILED  changed: {'F401': (264, 269)}
```

The frozen census is an **equality**, not a ceiling, so this reds `tests/architecture/` for every
lane, not only for whoever caused it.

Attributing the +5 by diffing per-file F401 counts against the baseline's freeze commit
(`992a037fc`, `git rev-list -1 --before=2026-09-07`) named exactly one file:

```
DELTA tools/refresh_to_head.py: 1 -> 7
```

## The cause is a stale COPY, not a landed defect

`git show HEAD:tools/refresh_to_head.py | ruff check --select F401 -` → **All checks passed.**

HEAD already carries the repair. `4da626379` (2026-09-23 06:07) swapped `BASE_WINS_RULES` for
`base_wins_rules` and made the five names that were left behind into **explicit re-exports**:

```python
from tools.stale_copy_refusal import (
    BASE_WINS_RULES as BASE_WINS_RULES,  # noqa: PLC0414 -- re-export; typed by this tool's suite
)
```

The copy on disk still carries the plain `CLOCK, PARTIAL, BASE_WINS_DATA_RULES, BASE_WINS_RULES,
PREDATES` form — i.e. the pre-`4da626379` revision. So does
`tests/tools/test_refresh_to_head.py` (+104/−207 against HEAD). Both were last committed by that
same commit, and neither has been advanced in the checkout since.

## Why this is worth a finding rather than a fix

**The obvious repair is wrong and I ran it.** Deleting the five unused imports made the census
green and broke two tests (`rth.PREDATES`, `rth.BASE_WINS_RULES` reach them through the
re-export). The second repair — pointing those two call sites at `stale_copy_refusal`, which owns
them — made all 137 tests green *in the worktree* and was still wrong: it re-solves, differently,
a problem HEAD had already solved, and landing it by pathspec would have **reverted
`4da626379`'s version of both files**, because a pathspec stages the working-tree copy. Both edits
are reverted; the copies on disk are exactly as found.

The gate itself is what caught it. Landing the census "fix" was refused with `I001: baseline 1306,
now 1307` — HEAD's copy of `refresh_to_head.py` has no I001 at all, so the extra one was the stale
copy's, arriving only because that path was in my pathspec. Drop the two files from the pathspec
and the gate grades HEAD's clean copies.

## The class

This is the mirror of the recorded shape *"a control that reads a generated artefact is GREEN in
the worktree and RED in the gate"*. Here it is RED in the worktree and GREEN in the gate, and the
inversion is what makes it expensive: a worktree red **looks like work to do**, and the work is
already done. Anyone pre-running `tests/architecture/test_static_quality_ratchet.py` — which
`CLAUDE.md` tells every lane to do before committing — hits this and has no signal that the answer
is "your checkout is behind".

**Nothing in the tree asks the question that settles it in one line:**

```
git show HEAD:<path> | ruff check --select <rule> --stdin-filename <path> -
```

A census red whose subject is clean at HEAD is a checkout-drift report, not a lint report, and the
ratchet cannot tell the reader which it is holding.

## Remedy, in order

1. **Advance the checkout** for `tools/refresh_to_head.py` and
   `tests/tools/test_refresh_to_head.py`. Not by `git checkout <path>` — the disk copies may carry
   another lane's live work under the staleness (the test file differs by ±hundreds of lines).
   `python3 -m tools.refresh_to_head --survey` on both, then the judgement it returns.
2. **Then** make the ratchet able to say this itself: when a rule exceeds its baseline, ask the
   same count of `git show HEAD:` for each offending file and, where HEAD is clean, refuse with
   *"your checkout is behind on N files"* rather than *"fix the new violations"*. The census
   already computes the per-file counts; the HEAD side is one `git show` per named file, and only
   on the already-red path, so it costs nothing in the green case.

Until (1) lands, the census stays red in the shared worktree for every lane and clean at HEAD, and
the instruction printed on the refusal — *"Fix the new violations — do not raise the baseline"* —
points at work that does not exist.
