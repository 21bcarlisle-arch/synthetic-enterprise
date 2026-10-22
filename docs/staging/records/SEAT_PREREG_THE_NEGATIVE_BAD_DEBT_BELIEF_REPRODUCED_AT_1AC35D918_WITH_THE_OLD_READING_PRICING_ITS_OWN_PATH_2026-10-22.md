**Severity:** RECORDED · **Lane:** 0 delivery · **Direction item:** `reproduce-the-negative-bad-debt-belief-at-1ac35d918`

# Pre-registration: the negative bad-debt belief, reproduced at `1ac35d918` with the old reading pricing its own path

Written 22 Oct 2026, before the full run. A smoke run to 2016-09-30 (642 calls, no value below 0.02
under either reading) checked only that the probe works.

## Why

`SEAT_RESULT_THE_BAD_DEBT_BELIEF_READ_BY_VINTAGE_MOVES_THE_LOSS_INTO_THE_ARREARS_CELLS_AND_THE_OLD_READING_NEVER_WENT_NEGATIVE_ON_THIS_BOOK_2026-10-22.md`
refuted its own P1. On the `793989589` path, the old (whole-year telescoped) reading never went below 0.0010.
So the vintage fix has been exercised only on synthetic controls. The `1ac35d918` pair
(`WORKER_RESULT_THE_RETENTION_GUARD_NETTING_ITS_OWN_BAD_DEBT_BELIEF_ON_THE_CONTRIBUTION_GUARD_2026-10-22.md`)
saw three negative guard rows: GOOD −0.0083, POOR −0.0046 and −0.0053.

## The run

`tools._c29_retention_engagement_arm net`, run from a locked worktree at `1ac35d918`. The door
`PaymentObservationConsumer.default_belief_rate` is native there. It returns the **old** belief,
and the run prices with it, as the original pair did. A wrapper computes the **vintage** belief at
every call, on the same ledger, date and cell. It uses `793989589`'s `default_belief.py` with the
range refusal stubbed, so a negative shows instead of raising. The wrapper does not change what
the run decides. Probe: `/var/tmp/se-belief-probe-1ac/probe.py`.

## Predictions

- **P1, the defect reproduces.** At least 1 call reads below 0 under the old reading, and the
  arm's guard rows again include negative `belief_rate` values matching the original three to 4
  d.p. (same code, same tree, one process). Refuted if no call goes negative. Two causes would fit
  that: the run is not deterministic at this tree, or the original rows came from somewhere other
  than this door.
- **P2, the vintage reading clears it.** 0 calls read below 0 under the vintage reading,
  including every call where the old reading was negative. Refuted by any vintage call below 0.
- **P3, where it sits.** The negative calls are in thin cells, dated before 2019-01-01. Most of
  them are `in_arrears_steady`: on the `793989589` path that cell's old minimum (0.0017) sat
  closest to zero relative to its mean. Refuted if none are `in_arrears_steady`, or if any are
  dated 2019 or later.
- **P4, the whole book.** The `*|*` charge share at the last call differs between old and vintage
  by less than 0.0005, as on the `793989589` path.

## What this can and cannot attribute

If P1 holds, the earlier non-reproduction came from the path or from the 78 commits between
`1ac35d918` and `793989589`. This run cannot tell those two apart. The remaining one-variable leg
would be the old door restored at `793989589`'s tree, so that the old reading prices its own path
there. It is named here and not owed by this item. What this run does settle is whether the fix
clears a negative belief at real inputs.
