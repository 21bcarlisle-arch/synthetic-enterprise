**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** `value-arms-error-bar`

# The page states the draws the family is entitled to, and no longer prints 18 seeds as 18 draws

Landed `2ed53bcaf` (2026-09-24). Closes the named cause of
`SEAT_FINDING_THE_PINNED_SELECTION_RESIDUAL_IS_THE_CONTROL_ARM_CANCELLING_AND_THE_RE_DRAW_MISSING_THE_PRICED_DECISIONS_2026-09-24.md`,
whose STILL-OWED bullet was "`generate_value_arms_data` does not read the new block ... the page
still prints `n` seeds as `n` draws". The closure is recorded in place on that finding, beside the
claim it answers.

## What a reader now meets

On the capabilities page, in the sentence that states the seed count:

> The seed count is effort, not evidence: **those 18 seeds are between 15 and 18 distinct draws of
> it**, because the residual cannot move unless a priced decision moves. Whether the standard error
> below overstates what this family can tell you cannot be settled from what its rows record. 18 of
> this family's 18 seed rows record no decision set …

Amber. And the sentence stating the bar no longer calls the seed count a draw count: `18 draws set`
became `18 seed re-draws set`.

## The drawn brief asked for something I did not do, and why

The item asked that a distinct-fingerprint count be fed to `sems_to_state_a_sign` in place of
`selection["n"]` at two producer lines. **On every family published to date that count is a BOUND,
not a number** — no published floor records its rosters — and substituting a floor for `n` would
state a confidence the evidence does not establish, in the same direction the instrument already
errs. The sensitivity at that floor is *already* published beside the headline
(`width_if_each_value_counted_once`, since 2026-09-23): 2.4954 sems → 2.4941, bar 2.110 → 2.145,
and the family still clears. So the honest move was to publish the count, name the existing
re-grade as the re-grade at its floor, and leave the arithmetic where the evidence supports it.

The arithmetic can only move to the entitled count on a family that RECORDS its rosters. **That is
the next piece and it has a different blocker** — a re-fold or re-run of the served family carrying
`scored_decisions` — so it should be drawn on its own terms rather than inside this one.

## The defect this turn nearly shipped, recorded because it was mine

`the_published_n_overstates_the_draws` was first written `at_most < seeds`. That returns **`False`
on the published floor** — 18 seeds, 15 to 18 draws — and `False` there reads to a consumer as *the
standard error is taken over the count it is entitled to*. The honest answer is that it may be
flattered by up to three draws and nothing on the rows can settle which. **Caught by printing the
block at real inputs before shipping it, not by more thinking about it.** It is now three-valued:
`False` only for the family KNOWN clean, `True` for the one KNOWN to overstate, `None` for the one
that cannot tell — and both reachable branches are exercised on real families on disk.

The door's colour leg had the same shape one level along: `arms-errorbar` opens with an
unconditional amber heading, so `"var(--amber)" in raw` was true of **every** branch and the leg
graded the heading instead of the sentence under test. A control that could not fail, found by
running it rather than by reading it. Scoped to its own span.

## Controls

Six mutations, all proven to bite. Renderer: `drawsEntitled` returning nothing; the colour pinned
amber; the cannot-tell sentence collapsed onto the overstates one. Producer: the original
`at_most < seeds` rule; folding unknowns into one repeated draw; a re-grade witness reporting
agreement where none was formed. The three rendered readings are asserted **pairwise distinct** and
each reachable — a partition control that never reaches a branch is passed by a rule that can only
return the other two.

`priced_decision_draws/the_floor_regrade_agrees` is registered **META** in the clears-zero registry.
It is not an answer to that question; it witnesses two COUNTS coinciding. STATISTICAL would make
today's coincidence a rule and red the day a family lands that refutes it.

## Noted in passing, not repaired here

The frozen ruff census reds in the shared worktree at F401 269 against a baseline of 264. None of
it is this landing's: all five touched files carry zero F401 at HEAD and in the working copy, and
the excess is an uncommitted working copy of `tools/refresh_to_head.py` (HEAD 1, worktree 7). That
is the subject of `WORKER_FINDING_THE_RUFF_CENSUS_REDS_IN_THE_SHARED_WORKTREE_AND_IS_CLEAN_AT_HEAD_2026-09-24.md`
and it did not block this landing, because `surgical_land` gates the tree the commit *would* create
rather than the dirty worktree.

**Reversal:** `git revert 2ed53bcaf`.
