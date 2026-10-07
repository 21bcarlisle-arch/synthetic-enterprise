**Severity:** INFO · **Lane:** H_harness · **Epoch:** 2 · **Atom:** `H50_a_run_entry_point_leaves_no_state_behind`
**Evidence:** `docs/staging/records/WORKER_RESULT_H40_THE_FULL_SUITE_POLLUTER_IS_THE_REGISTRY_EAC_REWRITE_WRITING_INTO_THE_SHARED_ROSTER_2026-10-07.md` (the filed prediction)

# H50: a second run starts from the drawn book, and the leftover moved no settled figure

**2026-10-07, autonomous worker.** Every reading was taken in a locked, detached worktree of
`origin/main` (`6957959a8`), with a copy of the shared `sim/cache`.

## 1. The filed prediction, answered first

H40 predicted that the A/B's second arm, run in one process after the first, settles the same
volumes and margins. Its only difference would be the W1_11 switch-verdict counterfactual. Before
the run I filed the opposite at 16:26Z: the digest would move, through the carried-over
`EFFECTIVE_EAC_KWH` and `ACQUIRED_CUSTOMERS`.

**The probe.** `run_phase2b.main(report_end="2018-12-31")` ran twice in one process, on the
code before this fix. Each run's `all_records` were summed per customer, over every numeric field
naming kWh, margin, revenue, cost or £, and the sums were hashed.

| | run 1 (fresh process) | run 2 (same process) |
|---|---|---|
| registry EACs that differ from the drawn band at the run's start | 0 | **164** |
| settled day-records, customers | 113,046, 176 | 113,046, 176 |
| digest | `156f4f1bdb63` | **`156f4f1bdb63`** |

**H40's prediction held, and mine is refuted.** Run 2 started on 164 rewritten EACs and settled a
byte-identical book. The reason: every reader of `eac_kwh` or `EFFECTIVE_EAC_KWH` that shapes
settlement runs *after* the rewrite, and the rewrite gives the same answer from the same reads.
The leftover reaches only what is read before the rewrite. That is the W1_11 counterfactual, which
is not in the settled records. So the A/B has not carried a settled non-policy difference since
2026-10-01. Bounds on this result: it covers one window (to 2018-12-31), phase 2b's records
only, and a window with no acquisitions in it (`ACQUIRED_CUSTOMERS` stayed empty). The full-window
A/B was not re-run.

## 2. The fix: the reset goes at the start of a run, not the end

`start_from_the_drawn_book()` is now the first line of `_main`. It restores the registry EACs
and `EFFECTIVE_EAC_KWH` from an import-time snapshot, and clears `ACQUIRED_CUSTOMERS`.

**Why not the end:** phase 4c sizes its DD openings from the rewritten records *after*
`main()` returns (`test_the_registry_eac_rewrite_reaches_the_dd_opening.py`). So does
`run_value_cycle_ab.account_class_map`. Restoring on exit would bring back the 2026-10-01 defect
(PROS-2024-0082 opened at a drawn 2,602 kWh against 41,951 billed). This follows the convention
the run already uses for its incoming-occupant book: the run's state stays readable until the
next run starts.

**Control:** `tests/simulation/test_a_second_run_in_one_process_starts_from_the_drawn_band.py`.
It reads the book at a run's first step, runs a full year, and reads the book again. It first
asserts that the run did rewrite something, so the equality cannot pass for free. With the fix:
1 passed (141 s). **Mutation, deleting the call:** red, with *164 rewritten EAC(s), e.g. C1 2500
-> 1604.4*. The acquisitions leg is **not** proven by this control, because the one-year window
wins nobody. Its clear is reasoned, not mutation-proven.

## 3. The census of module-level writes from `main()`

| write | where | verdict |
|---|---|---|
| fabric premise `eac_kwh` into the roster dicts | registry-EAC block | **reset at start** (this fix) |
| `EFFECTIVE_EAC_KWH[fab]` and `[incoming leg]` | registry-EAC block; `_admit_incoming_occupant` | **reset at start** (cleared and refilled, so incoming legs go too) |
| `ACQUIRED_CUSTOMERS.append` | fresh-market win | **reset at start**. It was never cleared, so a second run carried the first run's wins into its book and register |
| incoming-occupant book | B7 slice 3 | already cleared at start |
| `weather_inputs.adopt_book` | before settlement | ruled out: it clears, last writer wins |
| competitive-pressure ledger | `main` wrapper | ruled out: one scope per run |

## 4. What this does NOT fix: H40's two reds

`test_c1_eac_calibrated_to_ofgem_tdcv_medium` and `test_c4_solar_reduces_multiplier` read the
roster as a *non-run reader*, after another test's `main()`. By design that reader still sees the
last run's book. They stay red in census order until each in-process `main()` caller in the test
suite undoes the run's state, as `MonkeyPatch().undo()` does for its own patches. The door for
that now exists (`start_from_the_drawn_book`). Calling it in teardown of the triad test,
`test_phase40a_pass_through`, `test_phase40c_deemed_rate` and `test_phase41a_flex` is the
remaining work to L2. That is why this atom moves to L1 and not to its target.

`tests/simulation/test_net_new_acquisition.py::test_the_ceiling_still_fits_the_peak_systemds_own_journal_reports_today`
is red on unchanged `origin/main` too (it reads systemd's memory journal), so it is not this
change.
