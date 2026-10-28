**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# Pre-registration: the part-window EBSS share fix (3ab3ea925) read on a fresh full run at 1a02c46116 (2026-10-28)

Item `the-share-fix-ebss-reading-on-a-fresh-run-carrying-3ab3ea925`. Filed before the run started.
Follows `SEAT_PREREGISTRATION_THE_GAS_LEG_SETTLEMENT_FIX_AND_THE_PART_WINDOW_CUT_ON_A_FRESH_RUN_2026-10-28.md`,
whose P6 was refuted at 12 breaches (5 on part-window months) because that run predates the share fix.

## The run

Full default-book run at origin `1a02c46116`, via `launch_long_job` (`longjob-fresh-run-1a02c46116`),
the same `/var/tmp/fresh-run-scripts/arm.py` as the 1691ec0ecd and 20e7d66234 books. Worktree
`/var/tmp/fresh-run-wt-1a02c46116` (locked: a queued launch is not yet the worktree's cwd, see the
reaper finding). Output `/var/tmp/fresh-run-out-1a02c46116`. Comparison book: `/var/tmp/fresh-run-out-20e7d66234`.

**Attribution.** Run-side files changed since 20e7d66234: `company/billing/monthly_bill_assembly.py` (the share fix 3ab3ea925) and `simulation/run_phase2b.py` (the drawn-roster fix af61df576b: a second run in one process; a single fresh process should be unaffected). Any figure these two cannot reach and that moves is nondeterminism, not the fix.

## Predictions (EBSS row and its neighbours)

- **P1.** `INV_EBSS_CREDIT_EACH_MONTH_OCT22_MAR23` breaches 6 on the full book (was 12): 3 void-month
  and 3 named-later-in-month, both covered by the exception (`max_breached: 6`). Zero on part-window
  months that are not in those two classes. Tolerance: 6 to 7; above 6 refuses the publish and is a defect to find.
- **P2.** `INV_EBSS_CREDIT_ON_THE_BILL` stays within its `max_breached: 6`.
- **P3.** Full domain-invariant suite: no row breaches beyond its recorded exception ceiling.
- **P4.** `total_bad_debt` within GBP 10,783.88 +/- 1,500 and `total_gross` GBP 1,656,590.92 +/- 1% (the
  share fix touches EBSS credit allocation, not settlement). A bigger move is other landings', not graded to this fix.

## What done means

The run graded against P1 to P4 unedited with each grade beside its prediction; the verdict on whether the
exception ceiling now holds (publish unblocked or not); the grade record landed; the claim released.
If the run does not finish this turn, land the pre-registration and the launch state and hand off.

## Grade

*(written after the run returned)*
