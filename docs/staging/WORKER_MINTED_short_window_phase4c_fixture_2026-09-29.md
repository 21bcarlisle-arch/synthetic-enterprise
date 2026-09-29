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
