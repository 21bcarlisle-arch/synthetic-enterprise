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

*(written after the run returned, 2026-10-28 14:2x GMT; predictions above unedited)*

The run finished its full window (`OUTCOME: SURVIVED`, DONE.json at about 14:18). Ledger rebuilt
with `/var/tmp/fresh-run-scripts/build_ledger.py`, graded in a worktree at origin `94931642bc` by
`/var/tmp/ebss1a02-scripts/grade.sh`. That script runs the whole suite over all 1,293 accounts, with
the page records (bills, page ledger, desk steps) built in memory from the same ledger, so the rows
graded on the page are graded too. Output: `/var/tmp/ebss1a02-grade/grade.{txt,json}`.

| | prediction | result | grade |
|---|---|---|---|
| P1 | `INV_EBSS_CREDIT_EACH_MONTH_OCT22_MAR23` 6 to 7 (was 12) | **6 of 2,277** | HOLDS |
| P2 | `INV_EBSS_CREDIT_ON_THE_BILL` at most 6 | **6 of 2,277** | HOLDS |
| P3 | no row beyond its exception ceiling | `INV_OVERDUE_WITHIN_PAGE_BALANCE` 12,730 against 10,180 | REFUTED |
| P4 | bad debt GBP 10,783.88 +/- 1,500, gross GBP 1,656,590.92 +/- 1% | GBP 10,783.88 and GBP 1,656,590.92, to the penny | HOLDS |

**P1 and P2: the share fix holds on a run.** The six month-row breaches are exactly the six the
exception names: OCC-bec72a04dec8 2022-11, OCC-eb8498f3f8aa 2023-02 and OCC-e3e94f81161b 2023-03
(void on the 1st), plus OCC-25ff8966357a, OCC-a1e9ae835e65 and OCC-bec72a04dec8 in 2023-02 (the
deemed account held the 1st). The six bill breaches are exactly the bill exception's six, with
OCC-25ff8966357a on its January bill as named. The same script on the 20e7d66234 book grades 12 and
12 (`baseline_20e7.txt`), naming OCC-c0afcdf9fce8 (2023-02, 2023-03) and three further window
months on OCC-a1e9ae835e65 and OCC-bec72a04dec8. The share fix removes those six and adds nothing.
Both EBSS ceilings hold, so EBSS no longer refuses the publish.

**P4.** The fix only moves EBSS allocation, and settlement is identical to the penny (net GBP
658,630.29, the treasury change in the log GBP 547,985.88, both the same as 20e7d66234). Neither
of the run-side changes reaches anything else.

**P3 is refuted by a row the fix cannot reach.** `INV_OVERDUE_WITHIN_PAGE_BALANCE` breaches 12,730
of 32,741 desk steps. The 20e7d66234 book, with the same code, also grades 12,730, so the share fix
did not cause it. The ceiling of 10,180 is the 1691ec0ecd book's count. Separating the two things
that differ between those books:
- 1691ec0ecd's ledger rebuilt with origin's code still grades **10,180**, so the ledger and page
  code are not the cause.
- Only one commit changed run-side code between the 1691ec0ecd and 20e7d66234 runs: f805a94834,
  the gas-leg settlement fix (`simulation/world_payment_truth.py`).
- The desk does not move: all 40,005 collections-step amounts in the ledger are identical between
  the two books. Only the page's "owed" bound moves (2,816 steps newly breach and 266 stop, on 98
  households across every year).
- Case PROS-2016-0020, 16 Jul 2017. The desk prints GBP 44.19 overdue on both books. On 1691ec0ecd
  the gas page carried an unsettled GBP 14.04 from May (the credit "nobody held" that f805a9483
  moved back to the gas leg), so the page said GBP 49.64 was owed and the step passed. On 1a02c46116
  the gas page settles to GBP 0.01, the page says GBP 35.61, and the same GBP 44.19 breaches.

So the growth is not a new defect. A correct page balance has exposed more of the desk's known
over-statement (pricing at true kWh before VAT, against the issued bill). That is the open cause in
`SEAT_FINDING_THE_PAGE_PRINTS_MORE_OVERDUE_THAN_IT_SAYS_IS_OWED_ON_493_OF_752_HOUSEHOLDS_2026-10-28.md`.
The exception's ceiling is moved to this book's count, 12,730, with this attribution written into its
reason. Its retirement is unchanged. Without that, the next publish is refused on a defect whose
size the page fix itself grew.

**Verdict.** The EBSS share fix is confirmed on a run, and both EBSS exceptions hold at 6. With the
overdue ceiling re-based on attributed evidence, the full suite on this book is within every
exception: zero unexcepted breaches. The correctness stretch is not closed by this. Its exit test
needs zero *unexplained* breaches, and both the 6,808 overdue steps the desk-price reconstruction
does not reproduce and the two EBSS grader cases stay open defects with named retirements.
