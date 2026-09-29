**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `unminted`

# FINDING — the 26-minute subject gate is one world run, and half of that run is 144 fabric premises

Lane 0 `time-the-merge-selection-that-costs-26-minutes-per-test`, 2026-09-29. Measured in a detached
worktree at origin/main `b9c9092e6`, 16 cores, load 3–5 from other lanes. Nothing profiled with
cProfile.

## Where f997f8bf7's 1570 s goes

`pre_commit_test_gate.select_targets` on f997f8bf7's four code paths picks **52 files**. The gate runs
them serially in one pytest; there is no xdist here.

| part of the selection | tests | wall |
|---|---|---|
| the other 51 files, one pytest, `--durations=12` | 1379 passed, 2 skipped | **242 s** |
| `tests/simulation/test_run_phase4c_on_phase2b.py` | 48 | ≈1330 s by difference (1404 s measured 2026-09-28) |

1379 + 48 = 1427, which is exactly the receipt's count. **85 % of the subject gate is one file. In
that file, 45 of the 48 tests are cheap. The other 3 share the module fixture `main_result`, which
is one `run_phase4c_on_phase2b.main()`.**

The seven other files the item named, timed one at a time:

| file | tests | wall |
|---|---|---|
| tests/simulation/test_arrears_engine.py | 57 | 1 s |
| tests/tools/test_decided_differently_counts_roster_differences_apart.py | 5 | 10 s (import) |
| tests/tools/test_the_arrears_lines_reconcile_each_accounts_net_to_the_penny.py | 12 | 9 s (import) |
| tests/simulation/test_the_drawn_eac_sets_the_settled_level.py | 19 | 10 s |
| tests/simulation/test_every_settling_domestic_premise_reads_a_complete_stored_cell.py | 2 | 15 s |
| tests/tools/test_the_level_arm_in_the_ab_runner.py | 11 | 11 s |
| tests/tools/test_run_value_cycle_ab.py | 218 | 20 s |

The eight files "finished 15 tests in 1500 s" at e297d1169 because the phase4c fixture was blocking
the run. None of the other seven is slow. The slowest single tests in the rest of the selection are
`test_every_published_link_is_in_the_manifest` at 39 s and `test_the_floor_holds_and_no_row_is_stale`
at 24 s.

## Inside the one `main()`

A timed wrapper around `run_phase2b` gave: **`run_phase2b.main` 1842 s; the 4c billing pass after it
11.7 s**. The world run is 99.4 %, and the company billing pass is not the cost. The total was 1853 s,
not 1404 s, because a second instance was running alongside it (below).

A thread sampling the main thread's stack every 0.25 s (`sys._current_frames`, 7,246 samples, 1855 s)
gave these inclusive shares:

- **44.9 % `fabric_demand_path.fabric_providers_for_book`**. Of that, `reconstruct_ambient_profile`
  is 22.3 % and `simulate_day` 15.7 %. The leaves are `_diurnal_shape` 13.7 %, `simulate_day` 10.4 %
  and `mean_at` 7.3 %.
- 10.1 % `background.live_payment_triad.measure_and_write` (`expected_collection_misses`,
  `account_ledger.allocate`)
- 9.2 % `forward_book.settle_period`
- 7.8 % `renewals.build_renewal_schedule`, 6.5 % `risk_engine.calculate_sigma_recent`
- 8.3 % was HTTPS to Elexon (`sim/system_prices_history.get_system_prices_range`, one request per day).
  **This is my instrument, not the gate:** `sim/cache/` is gitignored, so a bare worktree misses
  `elexon_ssp_full.json`. `surgical_land.UNTRACKED_DATA_OVERLAY` puts `sim/cache` into the gate's
  checkout, so the gate hits the cache. Discount this share.

**This run lists 144 fabric-driven premises** (the `Fabric-driven premises (W1_11 settlement switch)`
line; 149 electricity and 95 gas accounts in the book). The negative result recorded at
`simulation/fabric_physics.py` "THE CACHE THAT WAS NOT THERE" (2026-08-24) rested on about **3.8
fabric-eligible customers**, a number it said "did NOT grow" with the book. That premise is spent.
Fabric is now the largest single cost in the world run, and it is linear in a book that is mostly
fabric-eligible.

## What I cannot yet say

- **Why one `main()` went from the 150–480 s that `PUBLISH_GATE_HEAVY_IGNORES` catalogues to 1404 s.**
  The 144-premise fabric volume is the obvious candidate, but it is unattributed. `f0ba399a4` (every
  domestic premise resolves to a stored cell) landed on 09-29 02:25, *after* the 1404 s reading, so
  it is not that reading's cause. It may have added to today's figure; that has not been measured.
- **Whether a `reconstruct_ambient_profile` cache now pays.** PREDICTION, filed before any run: the
  cells are shared (55 cells serve the book, per
  `WORKER_RESULT_THE_WEATHER_PARTITION_IS_JOINT_NOW_AND_55_CELLS_DO_WHAT_987_COULD_NOT_2026-09-22.md`).
  So a within-run cache keyed on (cell, day) hits on **≥ 50 %** of calls and saves **≤ 12 %** of
  `main()`. `simulate_day` is per premise and cannot be shared. If the hit rate comes in under 50 %,
  this prediction is refuted and the August record stands.

## The lever for the gate, and why it is not pulled here

`main()` takes `report_end`. The three fixture tests assert per-row joins and field domains, which
hold over any window, so a short-window fixture would take most of the ≈1330 s off every landing
that touches the phase4c subject. Two things stop me doing it in this turn:

1. `test_main_produces_contact_centre_log` and `test_main_produces_credit_refund_log` are
   `for entry in log:` with no non-empty assertion. Both pass on an empty log, today and under any
   window. A shorter window can only make that likelier. Each needs `assert log` first (the
   rare-branch rule), and that has to be checked against a full run's counts.
2. The join test's value includes the churned-account SLC 21B final-read override. The window has
   to contain at least one such churn, so asserting that is part of the change.

Next step: take the row counts of `meter_read_log`, `contact_centre_log` and `credit_refund_log`,
and the churn count, from one full run and from one run ending 2018-12-31. If all four are non-zero
in the short run, cut the fixture over with the non-empty assertions and the churn assertion in the
same commit.
