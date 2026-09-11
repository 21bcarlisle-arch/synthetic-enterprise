**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** H45_the_queue_is_chained_to_the_map

# The shared tree's closed map is BEHIND head, and landing it by pathspec reverts two atom closes

**Found 2026-09-07**, delivery seat, scheduled tick, while landing `W2_27`.
**Class:** `uncommitted_and_orphaned_work`. **Reproduce:** `git diff docs/design/maturity_map_closed.yaml`
in the shared tree, at or after `e4bedd260`.

---

## The state

`docs/design/maturity_map_closed.yaml` in the shared working tree carries an uncommitted edit that
**deletes 57 lines** — the whole of two rows:

| row | at HEAD | in the shared working tree |
|---|---|---|
| `A49_the_ceiling_comes_before_the_programme_on_r3_and_r4` | closed, `level_current: 2 = level_target: 2` | **absent** |
| `W2_27_how_many_household_cases_cover_demand` | closed, `level_current: 3 = level_target: 3` | **absent** |

Both were closed by `e4bedd260` (2026-09-07 10:42). The working-tree copy predates it. Alongside it,
`docs/design/maturity_map.yaml` has a **staged** hunk setting A49 `level_current: 2 → 0` and
`loop_stage: harden → build`.

So the two halves agree with each other and both disagree with HEAD, in the same direction: they are
the state *before* A49 and W2_27 were closed. **This is not another lane's new work. It is old bytes.**
Any lane that lands either map half by pathspec — the ordinary move — reverts two atom closes and
returns A49 to a level-0 row that has already been paid for once.

That last part is not hypothetical: `SEAT_FINDING_A49S_RECORDED_L2_IS_AT_HEAD_AND_THE_SHARED_WORKING_TREE_STILL_READS_LEVEL_ZERO_2026-09-07.md`
is the same bytes, found from the other end, and A49's own row records a repoint made *because* the
level-0 reading "keeps re-winning a draw this atom has already been paid for".

## Why it matters more than a stale file usually does

**It hides reds rather than causing them.** The shared tree is the tree every lane actually runs its
cheap gates in. With W2_27 deleted from the closed half locally, `tests/design/` reports
**142 passed** there. At HEAD the same suite reports **1 failed, 2 errors** —
`test_b_numeric_part_unique_per_lane_or_allowlisted`, on a `W2_27` lane+number collision across the
two halves.

I hit this directly. I minted `W2_27` into the live map to clear a wedge, ran `tests/design/` in the
shared tree, saw green, and landed. The green was measured against a tree that could not see the
duplicate I had just created. A `git worktree add --detach` at HEAD showed it immediately.

This is the two-directional version of a shape already in the record. The known one is *the shared
copy is AHEAD of HEAD, so landing it sweeps another lane's work*. This one is *the shared copy is
BEHIND HEAD, so landing it deletes work already landed, and meanwhile every gate run in that tree is
grading the wrong bytes*. The habitual check — "is my suite green before I land?" — cannot detect
either, because it runs in exactly the tree that is wrong.

## What is not established

I have not identified which process left these bytes, and I did not look hard: the file is not mine
and reading its history would not change the disposition. Two candidates worth eliminating before
anyone repairs it — a lane holding the file open across `e4bedd260`, or a daemon that rewrites a map
half from a cached parse — are guesses, and I am recording them as guesses.

I also have **not** repaired it. Restoring the shared copy to HEAD is a one-line `git checkout` on a
path, which this project forbids, and overwriting another writer's open file is the failure this
finding is about. It needs the lane that owns those bytes, or a tree-lock window.

## What is next

1. **The cheap-gate habit is measuring the wrong tree.** The pre-land instruction in `CLAUDE.md` says
   to pre-run the cheap gates; it does not say *where*. On a map-half or register change the answer
   has to be a clean extract, because those files are exactly the ones several lanes hold open. The
   smallest mechanism that would have caught this is a check that refuses a land when a **tracked
   file the commit touches is behind HEAD in the working tree** — the existing contested-path refusal
   in `surgical_land` covers ahead, not behind.
2. **A duplicate id across the two halves is caught only by a suite, and only at HEAD.** The store
   (`tools/maturity_map_store.load_atoms`) will return the id twice without complaint. That is the
   two-file-map class again, and it is the third time it has produced a defect.
3. Someone with those bytes' provenance should reconcile the closed half. Until then, treat
   `docs/design/maturity_map*.yaml` in the shared tree as **read-only for pathspec landing**;
   `--content` from a HEAD extract is the safe route and is what both of today's map commits used.
