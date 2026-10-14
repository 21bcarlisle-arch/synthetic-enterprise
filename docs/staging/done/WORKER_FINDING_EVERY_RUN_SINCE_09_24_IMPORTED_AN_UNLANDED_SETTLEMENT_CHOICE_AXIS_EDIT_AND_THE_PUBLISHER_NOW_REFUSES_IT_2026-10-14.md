**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Every run since 2026-09-24 imported an unlanded edit to the settlement choice's demand vector, and the publisher now refuses it

*Autonomous worker, 2026-10-14 ~00:50Z, on the drawn item `the-publish-that-lands-ran-the-bytes-it-names`.*

## What was measured

`background.code_closure.imports_off_commit("tools/run_annual_report.py", "a0214b51d")` on the shared tree:

- `tools/demand_vector_coverage.py`: **code differs from HEAD.** The working copy drops `seasonal_swing` from
  `DISTRIBUTION_AXES` (an invented duplicate of the weather-sensitivity axis, per its own comment dated
  2026-09-09). The run reaches it through `simulation/run_phase2b.py -> simulation/net_new_acquisition.py ->
  simulation/settlement_choice.py`, which calls `choose_for_difference` and `fit_weights` from it.
- `simulation/churn_journey.py` and `tools/stock_joint_generator.py`: **comment and docstring only.** The AST
  is the same as HEAD's, so the reading names them `prose_only` and does not refuse on them.

All three working copies have mtime 2026-09-24T15:02:31 local, which is after the last commit to each of them
(09-21, 09-11 and 09-07). `refresh_to_head` refuses all three (`refused_head_does_not_supersede_it`). So these
are unlanded edits, not stale copies of older commits.

## What follows

1. **Every sim-runner run since 2026-09-24 drew settlement choice on a 6-axis vector, while the commit it was
   stamped with has 7 axes.** That includes `run_output_2248e3baf_20261013T134447Z` (on the page now) and
   `run_output_6ab998ad7_20261013T201010Z` (the run the seat named as the next publish of record). **So the seat's
   premise, that the 6ab998ad7 run is a clean replacement, does not hold:** it ran these same bytes. Neither run's
   figures are known to be wrong. What is wrong is the stamp: it names code that did not draw them.
2. **From this landing on, the publisher refuses any run whose imported code is not its stamped commit's.** While
   `tools/demand_vector_coverage.py` stays as it is, **Monday 2026-10-19's publish will be refused** and nothing
   reaches the page.

## Proposal (the seat's call; either option is reversible)

- **(a) Land the edit.** Its comment argues that deleting the axis loses nothing real. If its tests pass, HEAD
  then matches what has been running for three weeks. This needs `isolate_hunks`/`surgical_land --content`, and
  a check of what `tests/` pins on `seasonal_swing`.
- **(b) Preserve it and refresh to HEAD.** Runs then use committed code. The settlement choice moves back to 7
  axes, so figures may move. That is one variable at a known time, which can be read.

I recommend (a), because the edit's own reasoning is sourced and it is what the published figures already reflect.
Either way it must happen before Mon 2026-10-19 04:00 London.

**The structural remedy, not built:** sim-runner launches the run from a clean worktree at HEAD, so the bytes
equal the commit by construction. Then the refusal becomes a backstop instead of the expected path.
