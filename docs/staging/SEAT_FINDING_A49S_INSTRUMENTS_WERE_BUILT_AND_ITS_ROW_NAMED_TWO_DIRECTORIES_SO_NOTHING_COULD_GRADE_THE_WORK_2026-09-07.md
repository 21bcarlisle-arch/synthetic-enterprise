**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** A49_the_ceiling_comes_before_the_programme_on_r3_and_r4

# A49's two ceiling instruments were built and landed; its row named two DIRECTORIES, so nothing in the map could grade them

**Found:** 2026-09-07, delivery seat, claim `a49-builds-the-r3-and-r4-ceiling-instruments`.

## The drawn premise was spent, and I re-measured it before starting

The item was drawn to *"build the two ceiling instruments A49 was minted for"*. The draw's own
premise check flagged its cited commit `d7b2a35d4` as already an ancestor of `origin/main`. It was
right to, and the spend goes further than the cited commit:

| what the item asked for | state at draw time |
|---|---|
| R3 ceiling instrument | `tools/r3_carbon_score_ceiling.py`, 717 lines, landed `85e1463c5` |
| R4 ceiling instrument | `tools/r4_product_ceiling.py`, 488 lines, landed `bfd232ba0` |
| its controls | 35 tests across two suites, all passing |
| on origin/main | yes — local `HEAD` == `origin/main` == `c4b9c8892` |

I did not take the filenames as evidence. I ran both instruments end to end and read their output.
Both satisfy the thing the item actually demanded — that each *"state on its own surface whether it
is a true CEILING or a handicapped FLOOR"*:

- **R3** publishes `verdict.clears_the_null: true`, `hindsight_over_null: 4.82`, headline figures of
  £6.91/household-year at perfect foreknowledge and £4.03 acting on a real forecast, and names its
  own gaps — the unestablished shiftable share is reported as a curve at share = 1.0 rather than a
  figure, which is the honest `None` the rule asks for.
- **R4** splits six products into 3 CEILINGS and 3 FLOORS, and `refuses_to_total` — deliberately, on
  the grounds that the products are not disjoint and not one currency.

**So the build half of this item is spent and I did not do it twice.** What follows is what was
NOT done, found by asking why the item was drawn at all when its work was already on `origin/main`.

## The actual defect: the row could not be graded, so the work was invisible to the map

`A49`'s row read:

    file_scope: ['tools/', 'docs/design/']

Both entries are **directories**. `tools/level_zero_contradicted_by_its_own_controls.py` is explicit
and correct that a directory is scope and never a control — grading `A49` against all of `tools/`
would grade every lane's work as this atom's evidence. So the row was reported UNGRADABLE, and:

> **the row could not be graded no matter how much of its work landed.** Both instruments existed
> and passed from 2026-09-07 05:33 onward, and the row still read `level_current: 0`,
> `loop_stage: build` — the map saying "in flight, nothing built" about finished, tested,
> pushed work.

This is not tidiness, and the tool's own docstring says why: `tools/lane_formation.py` derives
`buildable_lanes` from exactly that pair of fields and the draw ranks off it. **A row stuck at 0 is
a permanently-buildable atom that keeps winning draws it has already been paid for.** That is the
mechanism by which this item was handed out for work that was already on `origin/main` — the defect
is self-demonstrating, and this turn is the instance.

## What I changed

Two files, and they are one coupled edit rather than two:

1. `docs/design/maturity_map.yaml` — `A49.file_scope` repointed at the four files its own build
   wrote (both tools, both suites), keeping `docs/design/` for the frame documents.
2. `tests/design/test_maturity_map_contract.py` — `A49` **deleted** from
   `LEGACY_UNGRADABLE_BUILD_ROWS` (24 → 23).

**They cannot land separately, and that is the interesting part.**
`test_ungradable_build_rows_allowlist_has_no_FIXED_entries` asserts that a listed row which now
names a control has been delisted. Repointing the row without the delist turns that test red; and
because `pytest tests/design/` is a cheap pre-commit gate, it would have gone red **in every lane's
next commit, with the cause in nobody's diff**. That is the wedge shape this project has paid for
before. Verified after the edit: `tests/design/` 139 passed.

## The result, and it is not a level move

With the row gradeable, `A49` moves from UNGRADABLE to **CONTRADICTED — and FROZEN**:

    A49_the_ceiling_comes_before_the_programme_on_r3_and_r4 (lane A_strategy_governance, target L2)
        PASSES: tests/tools/test_r3_carbon_score_ceiling.py
        PASSES: tests/tools/test_r4_product_ceiling.py
        35 passed in 0.11s
        FROZEN BY: SEAT_FINDING_THE_PRODUCT_SHARE_IS_ZERO_AND_THE_SELECTOR_NOT_THE_DIAL_IS_WHY_2026-09-05.md
        FROZEN BY: SEAT_RESULT_ADMITTING_GAS_MOVED_THE_REFUSAL_AND_BOUGHT_ZERO_DECISIONS_...2026-09-07.md

**I did not move the level and could not have.** `A_strategy_governance` holds two live BLOCKING
findings, so OPS11 (`background/gate_authorization.refuse_level_raise_if_lane_blocked`) raises
`LaneBlockedError` and writes nothing; the map's own rule is that the agent proposes level-ups with
evidence and never moves a cell itself. Attempting the recording would have been the error.

**So the thing standing between A49 and its target level is now named, in view, and it is not the
instruments.** It is those two findings in its own lane. Before this change that fact was
unavailable to any reader: the row was silent, not blocked.

## What I did NOT do, and why

- **No level move.** Frozen by OPS11, above. It is a proposal, and the evidence for it is this file.
- **Did not discharge the two lane blockers.** Both are substantial and neither is in this claim's
  subject. They are what a follow-on turn on this atom should take, and the hand-off says so.
- **Did not rebuild either instrument.** Spent premise, re-measured — the point of the check.

## The general shape, for the next session

**A level-0 row's `file_scope` is checked for gradability by almost nothing, so a row can name
directories and become permanently undecidable while its work finishes underneath it.** The
partition is real: 27 rows still cannot be graded. The mint-path control added 2026-09-06 stops new
ones, and the frozen list is the backlog — each entry is an atom whose landed work the map cannot
see. Delisting one requires repointing the row and deleting the entry *in the same commit*.
