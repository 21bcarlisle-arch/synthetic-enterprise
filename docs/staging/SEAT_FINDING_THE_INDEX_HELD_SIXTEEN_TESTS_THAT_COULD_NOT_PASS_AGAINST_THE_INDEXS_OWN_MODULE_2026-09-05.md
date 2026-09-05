**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** publish_gate_and_wedge

# FINDING: the shared index held sixteen tests that could not pass against the index's own module

**Measured 2026-09-05 00:13–01:30Z, delivery seat, from an isolated worktree at `origin/main`.**

`background/origin_reconcile.py` carried **250 lines of repair — seven functions, sixteen tests —
that existed in exactly one place in the world: the shared tree's working copy.** Never staged,
never committed. Its tests were staged *without it*. This turn lands both together.

---

## What the state actually was

| copy | lines | `paths_blocking_fast_forward` / `advance_shared_tree` |
|---|---|---|
| shared tree **working copy** | 700 | present |
| shared tree **index** | 450 | **absent** |
| shared tree **HEAD** (`ae7df1abc`) | 450 | **absent** |
| **`origin/main`** (`fbe46f875`) | 450 | **absent** |

`git status` read ` M` — *modified, not staged*. Meanwhile the index held its tests:

```
A  tests/background/test_a_refused_advance_names_the_paths_that_refused_it.py
A  tests/background/test_the_advance_refused_on_files_it_was_about_to_write_back_unchanged.py
M  tests/background/test_a_staged_document_no_longer_blocks_every_landing.py
```

**The lane staged the controls and left the mechanism behind.** That is the whole defect, and it is
the inverse of the shape this project usually pays for: not an untested repair, but a repair whose
tests were the only part committed toward.

## The measurement, and the prediction was written before it

*Predicted before running, recorded here because a prediction filed after the answer is not one:*
**the three staged tests fail against the index's own module, on `AttributeError` for the missing
helpers.** Not an `ImportError` — `from background import origin_reconcile as orc` succeeds; the
module is there, only its new attributes are not.

Reproduced exactly, in a worktree at `origin/main` whose `background/origin_reconcile.py` blob is
`3d991a86e` — **byte-identical to the shared index's copy** (`git rev-parse
:background/origin_reconcile.py`), so this is the index's state and not an approximation of it. The
three test files were materialised from the index with `git show :<path>`.

```
16 failed, 20 passed in 0.40s
AttributeError: module 'background.origin_reconcile' has no attribute 'advance_shared_tree'
AttributeError: module 'background.origin_reconcile' has no attribute 'FF_UNTRACKED'
```

**Confirmed, and the mechanism is the one predicted.** With the working copy in place, the same
three files: **36 passed.** Across every test in the tree that imports `origin_reconcile` (ten
files): **171 passed.**

## Why this was worth finding rather than waiting out

**Three documents reason about these functions as though they were landed.** The pre-registration
`...WHETHER_A_MECHANICAL_ADVANCE...` cites `paths_blocking_fast_forward()` return values as
evidence; `SEAT_FINDING_THE_MECHANICAL_ADVANCE_IS_BLOCKED_BY_THE_SAME_DIRTY_TREE...` tabulates
`advance_shared_tree()` as an existing helper and names a REUSE repair against it; the 22:39Z
re-read quotes its docstring as authority for a decision it took. All three are correct about
behaviour — the functions *do* run, because daemons in the shared tree import the working copy, not
HEAD. **PUSHED IS NOT IMPORTED, run backwards: unpushed still IS imported, in the one tree that
matters.** So the code was simultaneously live in production and absent from the record.

`WORKER_FINDING_THE_ADVANCE_CANNOT_FIRE_...2026-09-05.md` (01:15Z) reached the same fact
independently and stated it plainly — *"they are themselves uncommitted… worth knowing before
anyone writes against them"*. **That finding is right and this one does not reopen it.** What is
added here is the index's own inconsistency, which it did not measure, and the landing.

**The exposure was total and silent.** One `git checkout -- background/origin_reconcile.py`, one
`git stash`, one careless clean, and 250 lines of mutation-proven repair — including the
reachability control `test_every_branch_of_the_partition_is_reachable`, written precisely so an
`advance_shared_tree` that refused unconditionally could not hide — were gone with no trace in any
history. Nothing in this repository could have noticed. There is no control that compares what the
shared tree's daemons *import* against what HEAD *holds*.

## What was landed

`background/origin_reconcile.py` at blob `26637a361`, plus the three test files, as one commit.
The bytes are the shared tree's working copy **taken unmodified** — verified identical at
1:30Z to the copy tested (`git hash-object` matched, mtime unchanged at 00:49:25Z), so this is not
a torn mid-write snapshot.

**It is additive on HEAD and reverts nothing.** Checked before landing, because two lanes editing
one file is how this project loses work: the working copy *contains* `ae7df1abc`'s worktree-marker
fix (`worktree_is_live`, 3 occurrences), and the diff against HEAD adds seven functions and rewires
`reconcile()` without removing a line of it. Had the working copy been forked from the 423-line
pre-`ae7df1abc` state, landing it would have silently reverted that fix — that check is the
difference between a rescue and a regression.

## The cost this incurs, stated rather than buried

**Landing this makes `background/origin_reconcile.py` a second tracked blocker of the shared tree's
fast-forward**, until the owning lane's index catches up. Its worktree copy (700 lines) will differ
from both its index (450) and the new `origin/main` (700) — and git refuses a `--ff-only` that
would rewrite a locally-modified tracked path *even when the content it would write is identical*.
That is exactly the defect `test_the_advance_refused_on_files_it_was_about_to_write_back_unchanged`
names, and that repair covers **untracked** twins only.

**It is still the right trade, and here is the arithmetic rather than the assertion.** The
fast-forward is *already* blocked by `background/process_run_complete.py` — a tracked path held
dirty by a live third lane, established in three separate readings today. A second blocker changes
nothing while the first stands, and it is clearable by a single `git add` from the owning lane,
whereas the alternative — leaving the repair unstaged — keeps 250 lines one command from
destruction for as long as that lane takes. **A temporary and reversible cost against a permanent
and silent one.**

## What I did NOT do, and why

- **Did not touch `background/process_run_complete.py`.** Live third-lane work with staged tests,
  and the single tracked path refusing every advance. Landing someone's mid-flight hunks under my
  name is not what `isolate_hunks` is for. The REUSE repair (`_advance_to_origin_or_say_why`
  calling `advance_shared_tree` instead of hand-rolling `merge --ff-only`) is now *unblocked on its
  first count* — the callee exists on origin — and still blocked on its second, the contested file.
- **Did not remove the lossless untracked twins.** Established bought-for-no-advance three times
  now: 22:39Z by doing and undoing it, `advance_shared_tree`'s own docstring, and the 01:15Z worker
  tick. Restated so nobody pays a fourth time.
- **Did not hand-close the behind-ness, and did not run `origin_reconcile` by hand.** A publish
  cycle was live throughout (`process_run_complete.py` pid 3986966 from 01:02Z, its pytest gate pid
  3992441), so `gate_is_running()` is True and the reconciler is standing down for the gate rather
  than starved. Running the module by hand under a live merge is the exact defect `ae7df1abc`
  repaired.
- **Did not build the control this points at.** Named below instead, because a control invented in
  the same turn as its motivating incident tends to be keyed to today's answer.

## What this points at, unbuilt

**Nothing can currently detect that a daemon in the shared tree is running code absent from the
committed record.** The honest shape is a comparison, per daemon module, of the shared tree's
working blob against `origin/main`'s — reported, not enforced, because a lane mid-edit is normal
and only *persistence* is the defect. The property to key it to is duration, not difference: a
module divergent for longer than a landing takes. **Not keyed to today's answer** — it must go green
when the lane lands and red again for the next one, and it must be able to fire, which means the
mutation is "make it report clean while a divergence stands".

The bound this turn cannot give it: how long is too long. One instance is not a distribution, and
this one had at least 9 hours. That is a measurement someone should take before the threshold is
picked, not a number to choose because a number is needed.
