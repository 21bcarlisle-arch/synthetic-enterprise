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

**Graded 2026-10-28, about 10:40Z.** The run at `20e7d66234` finished in 3,573 s
(`/var/tmp/fresh-run-out-20e7d66234/DONE.json`). `grade.sh` wrote `probe_20e7.json`,
`report_20e7.txt` and `pages_20e7.txt` to `/var/tmp/gasleg-remeasure/`. The predictions above are
unedited.

| | 1691ec0ecd | 20e7d66234 | Prediction | Grade |
|---|---|---|---|---|
| P1: refunds among the five leavers | 4 (all but PROS-2017-0293) | **0** | none | **MET** |
| P2: credit refunds | 26 (GBP 3,030.22) | **21** (GBP 1,839.77) | 18 to 23 | **MET** |
| P3: settlements on gas legs | 0 | **522** | 200 to 550 | **MET** |
| P3: settlements on electricity or single legs | 1,244 | **722** (-522) | down by at least 235 | **MET** |
| P4: `total_bad_debt` | GBP 19,738.24 | **GBP 10,783.88** (-45.4%) | -30% to -60%, GBP 8,000 to 13,800 | **MET** |
| P5: `total_net` | GBP 649,675.93 | **GBP 658,630.29** (+8,954.36) | the bad-debt fall, +/- 3,000 | **MET, to the penny** |
| P6: EBSS breaches on part-window months, HEAD ledger | 5 of 12 | **5 of 12** | 0; full book at most 3 | **REFUTED**, as the amendment predicted |
| P7: DD-step breaches on part-window months | 0 | **0** | 0 | **MET** |
| P7: DD-step flags, HEAD ledger code against 1691's | 1,572 against 1,494 (1691 book) | 1,577 (HEAD code) | no higher under HEAD's code | **REFUTED on the full book** (+78 on 1691); **not gradeable on part-window months** |

**What the grade can and cannot attribute.**
- **The fix is the whole run-side difference.** `total_gross` (GBP 1,656,590.92) and
  `provisioned_total_bad_debt` (GBP 121,428.29) are the same to the penny on both books. 2016 is the
  same in every figure. In every year from 2017, net moves by exactly the bad-debt change. So the run
  is deterministic over everything the fix cannot reach, and nondeterminism explains none of P1 to P5.
- **The rebuild's estimate holds on the run.** It said GBP 20,960 -> 10,824 (-48%) on another book.
  The run says -45%. The 291 both-failed singles did not change the size by much. The run puts 522
  settlements on gas against the rebuild's 523.
- **P7's second clause cannot be graded as written.** The probe finds part-window months through the
  ledger's `deemed_share_gbp`. 1691's ledger code writes no such field, so its part-window count is
  0 by construction, not by measurement. I graded the full-book comparison instead, and it is
  refuted: 78 more flags under HEAD's code on the same book. Under the same HEAD code, the two books
  differ by only 5 (1,572 on 1691, 1,577 here). So the 78 come from ledger code, not from this fix.
  The part-window cut is in that ledger code, but so are other changes since 1691. I have not
  attributed the 78 to the cut.
- **P6 is the share defect, not this fix.** Same 12 breaches, and the same 5 on part-window months,
  on both books. It moves on the next run carrying `3ab3ea925`.

**Every bad-debt and net figure that moves, old -> new (1691ec0ecd -> 20e7d66234, GBP).** Only
bad debt moves; net moves by the same amount in the other direction. `provisioned_total_bad_debt`,
`provisioned_total_net` and `total_gross` do not move.

| Year | Bad debt | Net |
|---|---|---|
| 2016 | 102.91 -> 102.91 | 38,743.97 -> 38,743.97 |
| 2017 | 2,129.35 -> 1,635.99 | 60,050.62 -> 60,543.98 |
| 2018 | 1,967.89 -> 1,626.66 | 56,896.16 -> 57,237.39 |
| 2019 | 4,392.33 -> 3,002.82 | 76,923.19 -> 78,312.70 |
| 2020 | 1,291.66 -> 729.86 | 77,197.27 -> 77,759.07 |
| 2021 | 617.59 -> 325.14 | 7,978.95 -> 8,271.40 |
| 2022 | 469.03 -> 327.26 | -47,314.72 -> -47,172.95 |
| 2023 | 1,288.33 -> 819.77 | 239,064.22 -> 239,532.78 |
| 2024 | 3,912.54 -> 764.97 | 107,577.01 -> 110,724.58 |
| 2025 | 3,566.61 -> 1,448.50 | 32,559.25 -> 34,677.36 |
| **Total** | **19,738.24 -> 10,783.88** | **649,675.93 -> 658,630.29** |

**What is published, and what it means for the site.** The site publishes the 26 Oct Monday run at
`4ae8da9b0f` (`site/data/supplier.json`): bad debt GBP 18,495, net GBP 664,130. That run predates
`f805a9483`. So both published totals, and every year's `bad_debt_gbp` and `net_gbp` from 2017
onward, are figures that move. By this run, bad debt is overstated by about 45%, and net is
understated by the same pounds. The 1691 and 20e7 books are not the published book. That 4ae8 book
has other code differences, so the published figures cannot be corrected by subtraction. The next
Monday run, which carries the fix, replaces them. This record is the mark on them until then.

**State at hand-off, 05:30Z.** The run is still queued (`longjob-fresh-run-20e7d66234-queued`), waiting
on memory behind the nightly `head_green_census`, which started at 03:33 and has taken about four
hours on earlier nights. Expect the run to finish about an hour after the census ends. It does not
carry 3ab3ea925 by design, so the gas-leg attribution holds. The grade is mechanical:
`/var/tmp/gasleg-remeasure-scripts/grade.sh` writes the ledger, probe, suite report and the five
leavers' page balances to `/var/tmp/gasleg-remeasure/`, which already holds the 1691 baselines
(`probe_1691.json` under HEAD's ledger code, `probe_1691_oldcode.json` under 1691's own).

**State at 06:35Z.** The first queue was lost. At 06:24 the worktree reaper removed the run's
worktree while the run was still queued. The launch refused at 06:27 on a missing workdir. The
worktree was recreated at the same commit, locked, and the run re-queued with identical arguments.
Its output directory was empty. Cause and fix:
`SEAT_FINDING_THE_REAPER_TOOK_A_QUEUED_RUNS_WORKTREE_BECAUSE_A_QUEUED_LAUNCH_IS_NOT_YET_ITS_CWD_2026-10-28.md`.
The predictions are untouched.

## Amendment before the run returned (2026-10-28): P6 is already known to fail, and why

P6 was written while the baseline probe was still running. Its result came back afterwards. On the
1691 book rebuilt under HEAD's ledger code, `INV_EBSS_CREDIT_EACH_MONTH_OCT22_MAR23` breaches 12, not
3 or fewer. Five of the 12 fall on part-window months. The run at 20e7d66234 has the same bill
assembly, so I expect it to grade about 12 as well. **P6 stands as written and is predicted refuted.**

The cause is a share defect in bill assembly, which is not this run's fix. It is fixed in a separate
landing, and the cause is in
`SEAT_FINDING_THE_FIRST_COLD_READ_FINDS_PAGE_ARITHMETIC_THAT_DOES_NOT_RECONCILE_AND_A_MARGIN_NOBODY_DEFINED_2026-10-27.md`.
This run does not carry it, so attribution for P1 to P5 is unchanged. On the full book, P7's flags
were 1,494 under 1691's ledger code and 1,572 under HEAD's.
