**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# Pre-registration: the gas-leg settlement fix and the part-window ledger cut, re-measured on a fresh run at 20e7d66234 (2026-10-28)

Item `the-gas-leg-settlement-fix-re-measured-on-the-next-run`. Filed before the run returned.
It is the reading the director's correctness ruling needs for this fix
(`docs/staging/advisor/DIRECTOR_RULING_CORRECTNESS_BEFORE_THE_NEXT_FEATURE_2026-10-26.md`: "re-run,
and mark every published figure that moves").

## The run, and why it can be attributed

- **The run.** A full default-book run at origin `20e7d66234`, through `launch_long_job`
  (`longjob-fresh-run-20e7d66234`). It uses the same `arm.py` as the `1691ec0ecd` book. Output:
  `/var/tmp/fresh-run-out-20e7d66234`. The run was queued behind `head_green_census` for memory.
  No other full run is in flight.
- **The comparison book** is `/var/tmp/fresh-run-out-1691ec0ecd`. Between `1691ec0ecd` and
  `20e7d66234`, the only change under `simulation/`, `company/`, `saas/`, `sim/` and `background/` is
  `f805a9483`, the settlement's leg (`live_payment_triad.py`, `world_payment_truth.py`). So **every
  run-side difference is that fix's**, or it is run-to-run nondeterminism. If a figure moves that the
  fix cannot reach, that is how nondeterminism would show.
- The part-window cut (`2bef058eb`) lives in `tools/`, the page ledgers. It is measured by rebuilding
  both books' ledgers with HEAD's code. The 1691 book is also rebuilt with its own code
  (`/var/tmp/onedue-grade-1691/ledger.json`). The probe is
  `/var/tmp/gasleg-remeasure-scripts/probe.py`.

## Baselines on the 1691ec0ecd book (read before the run, from its pickles)

`total_bad_debt` GBP 19,738.24. `provisioned_total_bad_debt` GBP 121,428.29. `total_net` GBP 649,675.93.
26 credit refunds.

**What the 20,960 figure is.** The `GBP 20,960 -> 10,824` in `f805a9483` is a rebuild on the
`5e3e9966a5` book, through the engine's walk. It is not the `total_bad_debt` of any book I hold. So the
predictions below are stated against 1691's own `total_bad_debt`, the figure the P&L publishes.

## Predictions

- **P1.** None of the five leavers (PROS-2017-0293, PROS-2021-0362, SYN-2016-070, SYN-2016-144,
  SYN-2016-406) has a credit refund.
- **P2.** Refunds fall from 26 to between 18 and 23.
- **P3.** Gas legs hold settlements. On 1691, gas legs hold 0, because every settlement went to
  electricity. Here they hold between 200 and 550, and electricity's count falls by at least the
  235 phantom ones.
- **P4.** `total_bad_debt` falls by 30% to 60%, landing between GBP 8,000 and 13,800. The rebuild
  fell 48%. Its 291 both-failed singles could go either way on a run.
- **P5.** `total_net` rises by about the bad-debt fall, within +/- GBP 3,000. Any larger move is a
  figure the fix cannot reach.
- **P6.** On part-window months, under HEAD's ledger code, `INV_EBSS_CREDIT_EACH_MONTH_OCT22_MAR23`
  breaches 0. On the full book it stays at or below 1691's 3 excepted, which are the grader's own.
- **P7.** On part-window months, `INV_DD_STEP_CHANGE` breaches 0, because the row only flags. Its
  flags there are no higher under HEAD's ledger code than under 1691's code on the same book.
  I hold no stronger prediction on its direction.

## What done means

- The run is graded against P1 to P7, unedited, with each grade written beside its prediction.
- Every published bad-debt and net figure that moves is listed, with old and new values.
- The finding carrying `f805a9483` and `2bef058eb` is marked with the measured result.

## Grade

*(written after the run returned)*
