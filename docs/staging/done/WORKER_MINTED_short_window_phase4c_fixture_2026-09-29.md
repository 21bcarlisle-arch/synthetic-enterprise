<!-- SUPERVISOR_DRAW: self-drawable -->

**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `unminted`

# [WORKER-MINTED] Measure whether the phase4c fixture can run a short window, then cut it over (2026-09-29)

**Type:** owed work filed out of the delivery-lane claim
`time-the-merge-selection-that-costs-26-minutes-per-test`. That claim's timing is done and landed in
`bcb661031`: `docs/staging/done/WORKER_FINDING_THE_26_MINUTE_SUBJECT_GATE_IS_ONE_WORLD_RUN_AND_HALF_OF_IT_IS_144_FABRIC_PREMISES_2026-09-29.md`.
**Do not re-time.**

## Why

About 1330 s of every landing that touches `simulation/run_phase4c_on_phase2b.py` (and the subjects
that select that file) is the single `main()` behind the `main_result` fixture in
`tests/simulation/test_run_phase4c_on_phase2b.py`. Only three tests read that fixture, and they
assert per-row joins and field domains. `main()` takes `report_end`.

## Done means

1. Run one full `main()` and one `main(report_end="2018-12-31")` in a checkout that has `sim/cache`
   (the shared tree, or an extract with the overlay; a bare worktree adds about 150 s of Elexon
   fetches). Record for each: the row counts of `meter_read_log`, `contact_centre_log` and
   `credit_refund_log`, and how many churned accounts got the SLC 21B final-read override.
2. If all four counts are non-zero in the short run, move the fixture to that window. In the same
   commit, add `assert log` legs to `test_main_produces_contact_centre_log` and
   `test_main_produces_credit_refund_log` (today both pass on an empty log), plus an assertion that
   at least one churned final read is in the window.
3. If any count is zero, record it and try `2020-12-31` before concluding the lever is unavailable.

## Result (2026-09-29, worker tick) — DONE: the fixture runs `report_end="2018-12-31"`

Measured in the shared tree (which has `sim/cache`). The override count comes from wrapping
`SimulatedReadFeed.final_read_for`, so it counts overrides that fired, not final bills that happen
to be actual:

| window | seconds | peak RSS | bills = read-log rows | contacts | credit refunds | SLC 21B overrides fired | churned accounts (last bill actual) |
|---|---|---|---|---|---|---|---|
| full | 1401 | 5.6 GB | 10,681 | 1,396 | 8 | 61 | 90 (90) |
| to 2018-12-31 | 326 | 2.6 GB | 3,061 | 434 | 6 | 25 | 36 (36) |

All four counts are non-zero in the short window, so 2020-12-31 was not needed. The whole test file
now takes 433 s under pytest in an origin/main worktree (49 passed), against the ~1,400 s its one
`main()` cost before.

New legs, each mutation-proven in one process against the same short-window result (a CORRECT arm
that passes, then a mutant built by copying the result that must go red):
- `test_main_produces_contact_centre_log`: emptied `contact_centre_log`. RED.
- `test_main_produces_credit_refund_log`: emptied `credit_refund_log`. RED.
- `test_main_produces_meter_read_log_matching_bills`: emptied `bills` and read log. RED. (The join
  passed on an empty pair as well, which is why a leg was added here too.)
- new `test_main_window_holds_a_churned_accounts_final_read`: with no churned accounts, RED; with one
  churned last bill set to `estimated`, RED. Of the 36 closings in the window, 25 are forced reads,
  so removing the override would leave about 25 closings on an estimate.

Aside: run A of the five-seed level-arm pair (`longjob-ab5-runa.service`) was OOM-killed at 11:01:46
BST. That was before this measurement launched at about 11:10, so these runs did not cause it.
