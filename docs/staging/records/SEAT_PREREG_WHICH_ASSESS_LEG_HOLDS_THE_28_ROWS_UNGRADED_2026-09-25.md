# PREREG -- which leg of `assess` actually holds the 28 level-zero rows ungraded

*Written 2026-09-25 BEFORE the measurement, by the delivery seat holding
`the-level-grader-can-grade-none-of-its-own-population`.*

## The question

`graded` in `tools/level_zero_contradicted_by_its_own_controls.main` is
`population - ungradable`, so a row counts as graded when it reaches EITHER verdict --
CONTRADICTED or silent. Every published account of this census so far has grouped the
ungraded rows by `ungradable_causes`, which describes the ROW's `file_scope`. That is not
the same question as which LEG OF `assess` returned the row, and only the second one says
what the instrument would have to do differently to grade it.

`ungradable_causes` says NOTHING_IN_THE_ROW for a row whose every path is on disk -- "the
refusal came from the pass". It does not say WHICH refusal. Four legs can produce it:
`CONTROL_PREDATES_ROW`, `PROVENANCE_UNKNOWN`, `RUN_UNAVAILABLE`, `BUDGET_EXHAUSTED`. The
repairs do not overlap: a predating set needs a repoint, an unavailable runner needs a
collection fix, a spent budget needs a bigger budget or a cheaper pass.

## The instrument, and why it costs nothing

Every leg in `assess` before `runner(...)` is cheap (path stats, `git log`, the HEAD-red
store). Only the pytest run is not. Calling `assess(budget_s=0)` therefore partitions the
population exactly, at zero pytest cost: every row that would have reached the run comes
back `BUDGET_EXHAUSTED` instead, and every other row returns the leg that really holds it.
`BUDGET_EXHAUSTED` under a zero budget is READ AS "would have run" and not as a defect --
that is the whole trick and it is stated here so the result cannot be read the other way.

## Predictions, before running

1. `population == 28`.
2. Rows returning `BUDGET_EXHAUSTED` (i.e. would reach the run) `== 6`. The work item asserts
   six rows "where every named path is on disk and one is a runnable control".
3. Rows silent via the HEAD-red register `== 1` (`KNIFE3_wall_crossing_paydown`), so
   `graded == 1` at budget 0 -- matching what the census published after `54a7b6242`.
4. `CONTROL_PREDATES_ROW` holds `>= 1` row, and `H41_the_map_ratchet_has_no_ongoing_drain`
   is one of them (the module docstring works that row through).
5. `PROVENANCE_UNKNOWN` holds `0` rows in the shared tree (it has full history).
6. The dominant leg is `NO_CONTROL_NAMED` -- the row names no `test_*.py` at all -- and it
   holds more rows than all the other legs put together.
7. Therefore: the headline "28 ungradable" is NOT mostly an instrument failure. Fewer than
   half the rows are ones the instrument could grade if it ran better, and the item's
   instruction to "fix those first, they are the instrument failing at rows it can already
   see" describes a minority of the population.

## What would refute the whole frame

If `BUDGET_EXHAUSTED` comes back with most of the population, the census is budget-bound
and the repair is the budget, not the rows. If it comes back `0`, then no row in the map
can reach a runner at all and every account of this census as "expensive" is wrong.
