**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 2 · **Atom:** `unminted`

# The one-due-date fresh run died unfinished at 7 June 2025, so the second cold read has nothing to follow

Found while drawing `the-second-cold-read-on-one-fresh-full-run`. Its own precondition ("item 1's landing is on
origin AND its onedue run has finished and been graded; if either is not true, stop and release") is **not met**.

1. **Landing: met.** `9ad5af9a7` (the one due date) is an ancestor of origin/main (`a31a21033`).
2. **Run: dead, not finished.** `/var/tmp/fresh-run-onedue.log` stops at settlement period 41,572,800
   (2025-06-07 period 28, treasury £783,236.62) at 01:15:52Z on 28 Oct. There is no `exit N` line (the wrapper
   writes one even on failure), no traceback, `/var/tmp/fresh-run-out-onedue/` is empty, and the process
   (pid 1689182) is gone. A wrapper that dies without writing its exit line was killed from outside; cause not
   established (memory pressure on the guest, or a reaper, are the candidates; not tested). I cannot say which.
   *Correction (2026-10-28): "died unfinished at June 2025" is not right. 7 June 2025 is the last day
   of the SSP record the run reads ("168,026 SSP records (2015-11-07 to 2025-06-07)"), so the loop had
   finished. The log stops about 10,000 lines before the completed slc22c run's log does. The run
   therefore died in end-of-run reporting, before `arm.py` pickled anything. The cause of the kill is
   still not established.*
   Item 1 therefore has no run to grade and its two exceptions (INV_OVERDUE_WITHIN_BALANCE,
   INV_STATUTE_BARRED_WRITE_OFF_AGE) stay as they are.
3. **Pre-step, billing: green.** `tests/company/billing` at origin HEAD, 2,498 passed in 141 s.
4. **Pre-step, simulation: not completed.** `tests/simulation` is too slow to finish inside this turn (about 1% in
   40 minutes while the full run also held the CPU). Two tests showed `F` among the first ~45 in a combined run
   (collection positions 41 and 43, in `test_a_dual_fuel_movers_gas_follows_it.py`). Re-run alone on a quieter
   machine, that file and its neighbour pass (21 passed). So the two reds are either load-dependent (a timeout)
   or order-dependent; I did not establish which. Not a known red on origin.

## What follows

The base the onedue run was launched on predates `25a8be909`, and the run is dead anyway, so the next step is a
single fresh full run at origin HEAD that serves BOTH item 1's grade and the second cold read: HEAD now carries
the renewal notice, the EBSS home and the one due date. That saves the run the direction's `not_now` was trying
to save, and removes the base objection that made onedue unusable. Launch it through `launch_long_job` with the
exit line checked, not `arm.py` under a bare shell, and do not run `tests/simulation` beside it.

## Done

Resolved 2026-10-28.

The one run at origin HEAD exists. `1691ec0ecd` ran under `launch_long_job` (unit
`longjob-fresh-run-1691ec0ecd`), exited 0 in 3,268 s, peaked under 5 GB, and pickled every key
(`/var/tmp/fresh-run-out-1691ec0ecd`, base in `/var/tmp/fresh-run-1691ec0ecd.base`). Item 1 is
graded against its pre-registration, and both exceptions are lowered (4 and 3, each residual named).
The second cold read can follow this run. Its worktree, `/var/tmp/fresh-run-wt-1691ec0ecd`, is
locked so the base stays put.
