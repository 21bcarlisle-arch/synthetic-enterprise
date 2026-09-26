**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# No row in the level-zero population ever reaches a runner, so both timeouts are dead dials — and `graded: 1 of 28` cannot be told from a runner that keeps failing

Answers `docs/staging/records/SEAT_PREREG_WHICH_ASSESS_LEG_HOLDS_THE_28_ROWS_UNGRADED_2026-09-25.md`,
written before the measurement. Seven predictions, **six confirmed and one refuted**, scored beside
themselves in `docs/staging/records/SEAT_RESULT_NO_ROW_IN_THE_POPULATION_REACHES_A_RUNNER_SO_THE_BUDGET_IS_NOT_THE_BOTTLENECK_2026-09-25.md`.
The refutation is the finding.

Drawn on the scheduled tick of 2026-09-25 as LANE 0 DELIVERY, claim
`the-level-grader-can-grade-none-of-its-own-population`.

## The finding

`tools/level_zero_contradicted_by_its_own_controls.assess` holds 28 candidate rows. Partitioned by
the leg that actually returns each row — measured with `budget_s=0`, which costs no pytest run
because every leg before `runner(...)` is cheap:

- **20** `NO_CONTROL_NAMED` — the row names no `test_*.py` at all
- **5** `CONTROL_PREDATES_ROW` — every named control predates the row
- **2** `NAMED_CONTROL_ABSENT`
- **1** silent via the HEAD-red register (`KNIFE3_wall_crossing_paydown`) — the only graded row
- **0** `BUDGET_EXHAUSTED`
- **0** `RUN_UNAVAILABLE`

**Not one row in the population reaches the pytest invocation.** *(CORRECTION, 2026-09-26, beside the
claim: this is no longer true and the dead-dial conclusion below is withdrawn. Re-measured on the
live map one day later, `OPS6_scoped_publish_path_suite` clears every cheap leg and reaches the
runner, where the 60s production cap times it out at a measured 109s. `_LEVEL_ZERO_TIMEOUT_S` is
the partition's only live consumer, not a dead dial. The remedy is still not to raise it — the row's
named set holds a red, so the verdict is SILENT whatever the budget. See
`SEAT_RESULT_EXACTLY_ONE_ROW_REACHES_THE_RUNNER_AND_THE_TIMEOUT_THAT_WAS_A_DEAD_DIAL_YESTERDAY_IS_ITS_ONLY_LIVE_CONSUMER_2026-09-26.md`.
The finding's OWED half is built there; what this file got right was the class, not the count.)* `DEFAULT_TIMEOUT_S` (900s) and
`background/delivery_seat._LEVEL_ZERO_TIMEOUT_S` (60s) are both live constants, both carefully
argued in comments, and **neither is consumed by any row.** They are dead dials. The module's
docstring reasons at length about `KNIFE3_wall_crossing_paydown` costing 1078s and 2.44 GB and
about the whole-pass budget not being the per-atom timeout — all true, all now unreachable, because
the 2026-09-25 register leg silences that row before the budget is ever consulted.

## Why it is a defect and not a curiosity

The census publishes `graded: 1 of 28`. Two unlike worlds produce that line: *a runner weighed the
rows and they did not all pass*, and *no runner was ever asked*. It is the second, and nothing on
the surface says so. Three lanes have now reported this census as stuck, and the work item that drew
me read the stuck number as an expensive pass — it instructs the next invocation to *"fix those
first, they are the instrument failing at rows it can already see"*, naming the PASS as the refusal's
source. An invocation obeying that would enlarge a budget nothing spends, measure no movement, and be
unable to attribute the non-result.

This is the same class the module's own `NOTHING_IN_THE_ROW` comment records paying for: a partition
published without the denominator that makes it readable. `ungradable_causes` is total over the ROW's
`file_scope`; nothing is total over the INSTRUMENT's legs, and those are the two different questions.
`NOTHING_IN_THE_ROW` says "the refusal came from the pass" for rows the pass never sees — true about
the row, and it is the sentence the item misread, because the row being blameless does not make the
runner the cause.

## What is owed

A census that states how many rows a runner ever weighed, keyed to the PROPERTY (rows reaching the
runner out of rows claimed) and not to today's zero — so "the pass is the bottleneck" becomes
falsifiable instead of inferred. It must go red when a row starts reaching the runner OR stops, which
a literal `0` cannot do.

## The adjacent repair, filed NOT built, with the measurement that decides it

The 5 `CONTROL_PREDATES_ROW` rows are the only ones a better instrument could grade.
`controls_older_than_the_row` establishes "the atom's own" from the control's BIRTH DATE, which by
construction cannot see a control the atom's build EXTENDED rather than created — the ordinary shape
the docstring itself describes for `KNIFE3`.

The obvious repair is to ask whether a commit that touched the control names the atom. Measured
across all 5 rows and 6 controls before writing any of it: commits whose subject contains the **full
atom id** number **ZERO**. That repair keyed on the full id would grade nobody. Keyed on the id's
prefix it finds real evidence for `D27_belief_window_saturates_on_this_book` — four commits reading
*"D27 pass 11 … the first pass on this atom to change a file_scope file"* — and also matches, for
`H41`, *"Unwedge publishing: the H41 caller landed, its callee did not"*, which is not H41's build at
all; and a bare prefix is unbounded, `W2` matching dozens of live atoms and `D9` matching `D90`.

`CONTRADICTED` demands work, so loosening toward it must be earned. It is not earned by a commit
subject line, and that is now measured rather than assumed. Whatever establishes "the atom's own",
it is not the message.
