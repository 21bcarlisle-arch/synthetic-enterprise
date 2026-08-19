# WORKER FINDING — three R15 shipped-defect proofs have quietly stopped running

**Severity:** LATENT · **Lane:** H_harness · **Atom:** SITE2_two_sided_wall_exhibit
**Raised:** 2026-08-19, SITE2 worker tick (scheduled draw)
**Rank requested (P-1):** backlog

R9 labels: every claim below is `observed-with-evidence` unless marked `inferred`.

## The finding

`observed-with-evidence`, `python3 -m pytest site/customers/ -q -rs` at this tick:

```
SKIPPED [1] test_wall_exhibit.py:2945: no revision of index.html without
            __householdCollections is reachable from this checkout -- the
            shipped-defect proof did NOT run
SKIPPED [1] test_wall_exhibit.py:3268: no committed revision of index.html without
            __accountStanding is reachable -- the shipped-defect proof did NOT run
SKIPPED [1] test_wall_exhibit.py:3809: no committed index.html without this repair
            within the search window
```

These are the R15 tests whose subject is **the page as it actually shipped** — the only
direction whose subject is the real defect rather than a synthetic reversal of the repair.
All three now skip. Sections 18, 19 and 21 each still report their mutation proofs as
green, and the arm that proves the defect was ever real is no longer executing.

## Why, and why it is a class rather than three instances

`observed-with-evidence`: each locates the pre-repair revision by walking a **fixed window**
of recent commits looking for the absence of its own symbol —
`for n in range(0, 9): rev = "HEAD" if n == 0 else f"HEAD~{n}"`. That was already an
improvement on a pinned SHA (it survives the repair's own commit). It still decays: the
window is wall-clock in disguise, and this repo commits many times a day, so every such
proof has a shelf life of roughly nine commits and then silently converts to a skip.

The skip message on two of the three is honest — it says *"the shipped-defect proof did NOT
run"*. Nothing reads it. A skip is not a failure, so the suite stays green and the count
moves from `186 passed, 2 skipped` to `185 passed, 3 skipped` with no red to look at. That
is R15's **FAIL-SILENT** pattern applied to the proofs themselves, which is the same shape
section 19 already caught once inside this module (a redefined test name silently deleting
section 18's proof, visible only as the skip count moving).

`inferred`: any future section written on this template inherits the defect on the ninth
commit after it lands.

## The repair, already demonstrated in-tree

Section 22 of the same module (this tick) uses a window-free locator and **fails rather than
skips** when it cannot find its subject:

- ask git which commit introduced the symbol — `git log --format=%H -S <symbol> -- <path>` —
  and take that commit's parent. There is no window and no decay.
- if HEAD does not yet contain the symbol, HEAD *is* the pre-repair page (the uncommitted
  case), so the check still runs on the tick that writes it.
- `assert src is not None`, never `pytest.skip`: *"the proof did not run"* and *"the proof
  passed"* must not look the same to a reader of the suite.

`_pre_region_guard_index()` in `site/customers/test_wall_exhibit.py` is the reference
implementation.

## What is owed

1. Re-point `_pre_collections_index` (§18), `_pre_standing_index` (§19) and
   `_pre_governor_index` (§21) at the window-free locator, and make each **fail** rather than
   skip when the pre-repair revision cannot be found.
2. `inferred`, worth checking rather than assuming: sweep the repo for other
   `HEAD~<n>`-window searches used as evidence. This module is where the pattern was
   invented; it may not be where it stops.

## Why this was staged and not fixed on sight

SELF-INTERRUPT DISCIPLINE. It is a defect in three *other* sections' controls, discovered
while building section 22; fixing it on sight would have put four sections' R15 proofs in one
commit with the repair they are meant to be independent of. Nothing is blocked by it — the
mutation arms of all three sections still run and still pass.

## Suggested falsifier

Re-point one section, then assert that on a checkout where the repair is more than nine
commits old the proof **runs and passes**, and that deleting the introducing commit's parent
from history makes it **fail** rather than skip.
