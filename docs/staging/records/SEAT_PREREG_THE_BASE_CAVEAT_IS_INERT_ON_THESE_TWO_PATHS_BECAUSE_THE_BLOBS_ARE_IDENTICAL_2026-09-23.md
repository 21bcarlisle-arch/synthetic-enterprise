**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — a pre-registration for the `--base-wins` enactment

# Pre-registration: the base caveat is inert on these two paths

**Filed 2026-09-23, before running any `refresh_to_head` survey.** Subject:
`enact-the-base-wins-discard-on-the-two-ladder-churn-copies-from-a-tree-that-holds-the-door`.
The result is in `docs/staging/SEAT_RESULT_THE_BASE_WINS_DISCARD_IS_ENACTED_AND_THE_DOOR_REFUSED_TWICE_WITH_A_CAUSE_IT_COULD_NOT_HAVE_KNOWN_2026-09-23.md`.

## What the hand-off said I must do first

> The tree needs origin/main first; the door arrives with it.

The draw repeated it as a base caveat: the shared tree is behind origin/main, so every
`supplies N names HEAD lacks` verdict asks the wrong base, and the remedy door named against
that base could land over the trunk.

## What I found before measuring anything

That caveat is general and it is true of the tree. It is **inert for these two paths**, and
the reason is not a judgement:

    HEAD:docs/reports/ladder_churn_factors.json                      66d57f4d91a2574b37ca34595b3e7799503f9a7a
    origin/main:docs/reports/ladder_churn_factors.json               66d57f4d91a2574b37ca34595b3e7799503f9a7a
    HEAD:docs/reports/ladder_churn_factors_svt_segment_decisions.json 6c367b541a027bb19f8fd9eb751b21cc95d06f85
    origin/main:..._svt_segment_decisions.json                        6c367b541a027bb19f8fd9eb751b21cc95d06f85

Same blob both sides. The two commits the shared tree is behind by (`c85e65f0d`, `58ce30050`)
touch the *door*, not the *reports*. So `--base HEAD` and `--base origin/main` are reading the
same bytes for these paths, and advancing the shared tree — a merge into 741 dirty files with
other lanes live in it — is **not on the critical path for this item**. It is a real thing the
tree needs; it is not a precondition of this enactment.

The door itself I do not need the shared tree to carry either: `tools/refresh_to_head.py` takes
`--root`, so the post-door code runs from this worktree against the shared tree's copies.

## The prediction, before I run it

1. `--base HEAD` and `--base origin/main` return **identical verdicts** on both paths.
   (Determined by the blob identity above, not a guess — recorded so the run can refute it.)
2. `--base-wins` **admits both paths**. The tag the draw's own classifier returned is
   `predates_landing_carrying_some`, and the door's `--help` admits
   `predates_landing or predates_landing_by_clock`. If the PARTIAL carrying verdict is *not*
   in the admitted set, the door does not reach its own subject and prediction 2 is refuted —
   that is the outcome worth having, and it is why this is written down first.
3. Both copies are **still stale on arrival** (mtime 2026-08-31 16:44:43, 23 days old, and the
   hand-off said to stop and file if they were not). Confirmed at draw time; restated here so
   the enactment run is judged against it.

Result is written beside this file, refuted or not.
