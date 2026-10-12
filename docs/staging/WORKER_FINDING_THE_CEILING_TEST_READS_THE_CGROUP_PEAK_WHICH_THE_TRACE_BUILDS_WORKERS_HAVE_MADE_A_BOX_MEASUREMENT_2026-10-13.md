**Severity:** BLOCKING (gate-red) · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`

# The ceiling test reads the cgroup peak, which the trace build's workers have made a box measurement (2026-10-13)

**Subject.** `tests/simulation/test_net_new_acquisition.py::test_the_ceiling_still_fits_the_peak_
systemds_own_journal_reports_today` reads `sim-runner.service`'s systemd-reported `memory peak`
(a cgroup aggregate) and compares it to `SETTLEMENT_CUSTOMER_YEAR_BUDGET` (5,000.0) via
`_memory_ceiling_customer_years`. Since `38f3a565f` the trace build's forked workers fill
whatever memory is free above the floor, so the cgroup peak now measures the box's free memory,
not the run. Observed on 2026-10-12/13: a 7,680 MB cgroup peak across 2 lifetimes prices a
2,924.4 customer-year ceiling against the constant's 5,000.0 — a hard FAIL, not the test's own
"UNAVAILABLE" skip, because production peak data exists and genuinely contradicts the curve.

**Why this blocks unrelated work.** `tools/pre_commit_test_gate.py` refuses any red commit
(director P0, 2026-07-17), and the nearest-test selection pulls in this test for any commit
touching `tests/simulation/test_net_new_acquisition.py` or `simulation/net_new_acquisition.py`
(and transitively `saas/growth_mandate.py`, since the two share a test file). It was first hit
2026-10-12 trying to land a capital-target correction that never touches this test.

**The fix, already designed in `9942c1fb7`'s message (a preservation commit for unrelated work)
and landed here as its own commit.** `background/sim_runner.py` now logs `ru_maxrss` over reaped
children as "Run largest process peak" after each completed run -- the run's own largest process,
not the cgroup's combined peak. `tests/simulation/test_net_new_acquisition.py`'s journal leg
(`_peaks_by_the_code_they_ran`, `_RUN_PROCESS_PEAK`) reads that line instead of the cgroup
`memory peak` line. `test_BOTH_branches_of_the_code_keyed_peak_filter_are_reachable` and
`test_BOTH_verdicts_of_the_memory_ceiling_guard_are_reachable` are rewritten to the new journal
shape, and the live-peak read (`read_unit_memory_peak_live_mb`) is dropped from the ceiling test
since a running run has no process peak until it completes.

**Prediction, filed before running anything:** the ceiling test SKIPS ("UNAVAILABLE"), because
no "Run largest process peak" line exists in the journal yet -- `sim-runner.service` has not
restarted on this code and completed a run. `test_BOTH_branches...` and
`test_BOTH_verdicts...` PASS, since they construct their own journal text.

**Measured** (fresh worktree at origin/main `c25b71d6f`, these two hunks applied, nothing else):
`test_the_ceiling_still_fits_the_peak_systemds_own_journal_reports_today` SKIPPED exactly as
predicted. `test_BOTH_branches_of_the_code_keyed_peak_filter_are_reachable` and
`test_BOTH_verdicts_of_the_memory_ceiling_guard_are_reachable` PASSED. The full file: 61 passed,
1 skipped.

**Not done here, and not this fix's to do:** `SETTLEMENT_CUSTOMER_YEAR_BUDGET` is NOT moved. The
constant's own re-pricing is `docs/staging/WORKER_FINDING_THE_SETTLEMENT_CEILING_CURVE_RETAKEN_AT_
CURRENT_CODE_2026-10-08.md`'s subject, priced at 3,100 and embargoed behind a value-arms series --
lowering it here to make the test pass would move the published book, which is a different act
from fixing what the test measures.

**What ends the "SKIPPED" state.** `sim-runner.service` must restart on this code and complete at
least one run; the first "Run largest process peak" line it writes gives the test its first
production reading. A red after that point is the correct red -- it will mean the run's own
process peak genuinely does not support the budget, which this fix cannot know yet.
