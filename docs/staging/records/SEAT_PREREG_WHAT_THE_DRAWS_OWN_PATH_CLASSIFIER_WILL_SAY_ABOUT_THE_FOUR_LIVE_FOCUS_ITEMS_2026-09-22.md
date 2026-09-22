**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3

**Filed:** 2026-09-22 · **Claim id:** `the-lane-0-draw-never-asks-the-landing-door-to-classify-the-pile-it-commissions`
**Written BEFORE the measurement it predicts.** The instrument (`delivery_lane.path_note`) did not
exist when this was written; the prediction is about what it will say on the four live focus items
in `docs/direction/DIRECTION.yaml`, measured against the SHARED tree.

# Pre-registration: what the draw's own path classifier will say about the four live focus items

## The question

The Lane 0 draw names files in its items and says nothing about their state. The landing door
(`tools/stale_copy_refusal.judge` / `clock_judge`, landed `028ab23d9`) already grades exactly that
state and its census currently names 19 such paths tree-wide. The work is to make the draw ask it.

The measurement worth pre-registering is not *does the wiring run* — that is a test. It is **how
much of a live item's named file list is already not what the item thinks it is.** If the answer is
"almost none", this note is a cheap annotation and I should say so. If it is "a third", the shape
that cost three invocations is routine rather than a 2026-09-22 accident.

## The predictions, in order of how much I would be surprised to be wrong

1. **`restore-the-six-live-reverts-before-anything-regenerates-from-them` will come back with at
   least two `predates_landing` rows**, and they will be `simulation/net_new_acquisition.py` and
   `tools/generate_value_arms_data.py`. *Confidence: high — the item names those two itself, with
   mtimes, and the thesis text says the census found them. This leg is close to a self-test and is
   here to catch the instrument being wired to the wrong tree, not to learn anything.*

2. **`tools/stale_copy_refusal.py` will grade as HOLDER WORK, not already-landed and not a
   revert.** *Confidence: medium. It is ` M` on the shared tree and the lane holding it is adding a
   restore path. If it comes back `predates_landing` that is a finding about that lane, filed
   separately and immediately.*

3. **Across all four focus items, between 30% and 70% of the resolvable named paths will be
   `already-landed`** — i.e. named in the prose, tracked, and identical to HEAD, so the item's file
   list is partly a description of finished work. *Confidence: low. This is the number I actually
   want. The HDD item was 5 of 10 (50%), which is one observation; I am predicting that was not a
   fluke. A result under 30% refutes "the shape is routine" and I will say so.*

4. **At least one named path will resolve to nothing at all** — a path in prose that no longer
   exists under that name. *Confidence: low-medium. Nothing has established this; it is the failure
   mode an item's prose has that git has no opinion about, and I am guessing it is present.*

## What would refute the work, not just a prediction

If every resolvable path across all four items grades `already-landed` or ordinary-dirty and NONE
grades a revert or holder work, then the door's classifier adds nothing a `git status` would not,
and the honest outcome is to land the note anyway (it is cheap) and record that its value is the
`already-landed` column alone.

## Registered caveats about the instrument itself, before it is read

- The draw composes in the SHARED tree; a worker may run in an isolated worktree where the working
  copies are HEAD's. **The verdict is about the tree the draw ran in and the note must say so on
  its face**, or it becomes a claim about a tree the reader is not in.
- A path-shaped token in prose is not a path. Only tokens that resolve to a file on disk or a blob
  in HEAD are graded; everything else is reported as unresolved rather than silently dropped.
- The classifier reads `HEAD`, and `HEAD` in a shared checkout is routinely behind `origin/main`.
  `stale_copy_refusal.base_caveat` exists for exactly this and inverts the holder-work/rival
  reading when it fires. **If it fires, the note must carry it** rather than print a door.
