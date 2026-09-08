**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (value-arms current-world bound)

**Knowledge:** none — this is a harness state, not domain understanding.

# A constant on origin named the bound artefact, and the artefact exists in nobody's commit

**Found 2026-09-08** while landing the lane-0 delivery item *"the value-arms merge conflicts with a
second seat's implementation of the same item"*. Fixed in `71de7a80f` before the merge that needed
it, so no tree ever existed in which the constant pointed at nothing.

## What happened

`origin/main 8e90037a5` moved `CURRENT_WORLD_NOISE_FLOOR_PATH` to
`docs/observability/value_cycle_ab_s1_noise_floor_20260908.json`, **together** with
`CURRENT_WORLD_THREE_ARM_PATH` — which is right, and is the only legal way to move either. Moving
the figure without its bound republishes the headline unbounded, and this repo has already paid for
that once.

The artefact itself was never committed. `git status` called it `??`: not ignored, just untracked.
Every other file in that series — `_20260829`, `_20260831`, `_20260903`, the `only_` and `except_`
variants — is tracked. This one sat on one machine's disk.

So a clean extract of `origin/main` read the figure constant at the 09-08 run and the bound constant
at a path that does not exist. **The pair-move rule was followed in the code and broken in the
tree**, and the result is the exact defect the rule exists to prevent, reached by a different door.

## Why nothing caught it

The lane that moved the constant had the file on disk, so every control it ran was green — including
the ones written specifically about this pairing. This is
`CLASS_UNCOMMITTED_AND_ORPHANED_WORK_2026-08-12.md` with the arrow reversed: the usual shape is
*work that is committed and unreferenced*; this is *work that is referenced and uncommitted*, and it
is the more dangerous half, because the reference is what makes it look present.

The generic statement: **a module constant naming a repo-relative path is an edge into the tree, and
nothing in this repo checks that such an edge lands on a tracked file.** The same hole admits every
path constant in `tools/`, not just this one.

## What is next

A one-leg control, and it is the smallest mechanism that can fail here: every `PROJECT / ...` path
constant in a module under `tools/` resolves to a file `git ls-files` returns. It fires on exactly
this defect, needs no register, and would have refused `8e90037a5` in the lane that wrote it rather
than one seat and fourteen commits later.

Not built in this turn — the drawn item was the merge, and this was found on the way. Minting it is
the next act on it.

## Evidence

* `71de7a80f` — the artefact landed on its own, ahead of the merge. World digest
  `39a192ce04c1eda8` and producing commit `04361d6c7`, the same world and the same commit as the
  arms it bounds; `redraw_scope.mode` `all`; stamped `2026-09-08T04:10:26Z` against the arms'
  `00:19:54Z`, so the bound is newer than the figure it bounds and the staleness guard is satisfied
  rather than bypassed.
* `490f0b7a2` — the merge that consumes it, and where the bound first reaches a reader.
