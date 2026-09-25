# RESULT -- no row in the level-zero population reaches a runner, so the pass is not the bottleneck

*Measured 2026-09-25 over the live map at `a99702336`, against the predictions in
`SEAT_PREREG_WHICH_ASSESS_LEG_HOLDS_THE_28_ROWS_UNGRADED_2026-09-25.md`, which was written
first. Scored beside itself.*

## The instrument

`assess(pop, budget_s=0)` over the 28 candidate rows. Every leg before `runner(...)` is cheap,
so a zero budget partitions the population exactly at zero pytest cost: any row that WOULD
have reached the run comes back `BUDGET_EXHAUSTED`, and every other row returns the leg that
really holds it. Zero pytest runs were spent.

## The leg partition, which nothing had published

| rows | leg |
|---|---|
| 20 | `NO_CONTROL_NAMED` -- `file_scope` names no `test_*.py` at all |
| 5 | `CONTROL_PREDATES_ROW` -- every named control was on disk before the row |
| 2 | `NAMED_CONTROL_ABSENT` -- `PB5_pounds_or_percent_resolved`, `A51_the_plain_english_report...` |
| 1 | silent via the HEAD-red register -- `KNIFE3_wall_crossing_paydown` |
| **0** | **`BUDGET_EXHAUSTED`** |
| **0** | **`RUN_UNAVAILABLE`** |

`graded == 1 of 28`, and the one graded row is the one the register silenced without a run.

## Scored predictions

1. `population == 28` -- **CONFIRMED**.
2. Six rows would reach the run -- **REFUTED, and this is the finding.** ZERO do.
3. Silent via the register `== 1`, `graded == 1` -- **CONFIRMED** (`KNIFE3_wall_crossing_paydown`).
4. `CONTROL_PREDATES_ROW >= 1` including `H41` -- **CONFIRMED**: 5 rows, `H41` among them.
5. `PROVENANCE_UNKNOWN == 0` in the shared tree -- **CONFIRMED**.
6. `NO_CONTROL_NAMED` dominates and exceeds all other legs together -- **CONFIRMED**: 20 of 28,
   against 7 for every other ungradable leg combined.
7. The headline is not mostly an instrument failure -- **CONFIRMED, more strongly than written.**

## What this refutes, and it is the item that drew me

The lane-0 work item `the-level-grader-can-grade-none-of-its-own-population` says: *"6 rows
where every named path is on disk and one is a runnable control, so the refusal came from the
PASS and not from the row -- fix those first, they are the instrument failing at rows it can
already see"*.

The first half is true and the second half does not follow. `NOTHING_IN_THE_ROW` is a statement
about the row's `file_scope` -- every path present, one of them runnable -- and it is correct for
those rows. But the PASS never runs for any of them: they are held by the DATING leg, five
commits short of a runner. `DEFAULT_TIMEOUT_S` is 900s, `background/delivery_seat.
_LEVEL_ZERO_TIMEOUT_S` is 60s, and **neither number is consumed by any row in the population.**
Raising either moves nothing. An invocation drawn on that instruction would have enlarged a
budget that is never spent and measured no change, and could not have attributed the non-result.

This is the same shape as the cause partition's own history recorded in the module: a number
that did not move for twelve briefs because two unlike things were counted as one. Here the two
unlike things are *"the runner disagreed"* and *"no runner was ever asked"*, and the published
`graded: 1 of 28` cannot distinguish them. A census that publishes what it graded, without
publishing how many rows a runner ever weighed, reads exactly like a runner that keeps failing.

## The one honest discriminator I tested and am NOT shipping

The five `CONTROL_PREDATES_ROW` rows are the only ones a better instrument could grade, and
the obvious repair is to ask whether a commit that TOUCHED the control names the atom -- direct
evidence of authorship, rather than the birth-date proxy `controls_older_than_the_row` uses,
which by construction cannot see a control the atom's build EXTENDED.

Measured before building it: across all five rows and six controls, the number of commits whose
subject contains the **full atom id** is **ZERO**. The proxy is not merely imprecise; keying on
the full id would grade nobody. Keying on the id's prefix instead finds 4 commits for
`D27_belief_window_saturates_on_this_book` whose subjects read *"D27 pass 11 ... the first pass
on this atom to change a file_scope file"* -- real evidence -- and also matches, for `H41`,
*"Unwedge publishing: the H41 caller landed, its callee did not"*, which is not H41's build.
And a bare prefix is unbounded: `W2` matches dozens of live atoms and `D9` matches `D90`.

So the repair is a real one with a genuinely unsolved discriminator, and shipping the prefix
version would be widening a detector into a false-refusal it cannot bound -- in the one
direction this module's docstring repeatedly says must be earned, because `CONTRADICTED`
DEMANDS WORK. Filed rather than built, with the measurement that makes it decidable next time:
whatever establishes "the atom's own", it cannot be the commit subject line.
