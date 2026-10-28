**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# Pre-registration: the desk posted the issued bill, read on a fresh full run (2026-10-28)

Item `the-desk-is-posted-the-issued-bill-not-true-kwh-revenue`. Filed before any run carrying the
fix exists. The finding is `docs/staging/SEAT_FINDING_THE_PAGE_PRINTS_MORE_OVERDUE_THAN_IT_SAYS_IS_OWED_ON_493_OF_752_HOUSEHOLDS_2026-10-28.md`.
The knowledge is `docs/market_research/debt_and_collections.md` §7.2.

## What changed

`run_phase2b._post_month_bill` now posts the triad (the household's payment and the desk's ledger)
the engine's ask over the month's issued bill: `arrears_engine.payer_ask_gbp(bill)`. Before, it
posted the month's settled revenue, true kWh before VAT. The bill comes from
`StopNoticeBoard.issued_bill_for`, which runs the supplier's assembly door over the leg's rows
through that month. A leg that left takes its closing read. Nothing in settlement changed.

## Measured before the run (no run launched)

- **In-loop bill = published bill.** A 2016 run, in process: 4,769 of 4,769 posted leg-months equal
  the engine's ask over the whole-book published bill (`/var/tmp/desk-bill-probe/inrun2.py`). On the
  1a02c46116 book, offline: 1,331 of 1,331 leg-months on 40 sampled founder legs agree
  (`inloop_vs_book.py`).
- **Cost.** The monthly rebuild took 25 s for those 40 legs over the decade. That is an upper bound
  of about 13.5 min for 1,293 legs, before the DD legs' share the stop board already paid.

## The run

A full default-book run at the origin commit that lands this, with the same
`/var/tmp/fresh-run-scripts/arm.py`, `build_ledger.py` and `grade.sh` as the 1a02c46116 book. The
comparison book is `/var/tmp/fresh-run-out-1a02c46116` (12,730 overdue breaches).

## Predictions

- **P1.** `INV_OVERDUE_WITHIN_PAGE_BALANCE` falls from 12,730 to **at most 10,230** (at least 2,500
  fewer). The floor comes from the 2,886 repriced steps measured on the 1691ec0ecd book. I cannot
  predict how much of the 6,808 unreproduced steps the price cause carries. I do not predict zero:
  written-off bills the desk still chases (C6, July 2016) are a second cause, and this does not
  touch it.
- **P2.** The desk's step amounts move. More than 90% of the non-zero collections-step amounts differ
  from the 1a02c46116 book's, because VAT alone moves every one.
- **P3.** Settlement is unchanged: `total_gross` is GBP 1,656,590.92 to the penny.
- **P4.** `total_bad_debt` is GBP 10,783.88 ± 25%. I cannot yet say its direction: the ask rises by
  VAT, and it moves both ways on estimated bills. Outside the band is a finding to trace.
- **P5.** Wall time is at most 85 min (66 on 1a02c46116) and peak memory is at most 12.5 GB (11.5).
- **P6.** No other suite row goes beyond its exception ceiling.

## What done means

Each prediction graded unedited beside its result. If P1 holds, the exception ceiling is re-based to
the measured count, with the remaining cause named. Then the claim is released.

## Addendum, filed after the launch and before any output (2026-10-28 16:50 GMT)

The run was launched at 16:01 GMT at b2fc50facf, the merge that carried the fix, after the
predictions above were on origin (15:59). At 16:47 it was at March 2023, with no book written. These
add the rows a change to the desk's input can move that P1 to P6 do not name. Baselines are the
1a02c46116 ledger as rebuilt for its grade (`/var/tmp/ebss1a02-grade/ledger.json`).

- **P7 (P1's second cause, traced this turn).** Of the 12,730 breaches on the 1a02c46116 book, **720
  steps on 112 households** are dated on or after the page's first write-off on that household
  (`/var/tmp/desk-wo-probe/probe.py`, reproducing the 12,730 exactly). The cause is three write-off
  dates for one leaver's debt:
  - the page writes it off at the final bill's due date (world `arrears_engine`, C4 convention);
  - the company's sweep writes it off a year after the final bill (`closed_balance_write_offs`),
    but only after the run, so the in-loop journey never sees it;
  - the desk's journey chases on to the six-year statute bar (C6: the page writes off on 19 Apr
    2017, and the desk is still chasing it in June 2017 and writes it off on 19 Apr 2023).
  The fix does not touch any of these. I predict **at least 500** breaches in this class on the fresh
  book.
- **P8 (collections).** There are 7,380 desk journeys and 40,005 steps on the baseline, and 64 desk
  write-offs (GBP 4,466.12). I predict journeys and steps within ±15%. Desk write-offs: count within
  ±15%, and GBP below 4,466.12. The baseline figure is built on ex-VAT true-kWh sums that run high on
  estimated months (C6: GBP 130.50 against a GBP 33.80 bill).
- **P9 (the stage-5 ledger).** Total billed on the pages is GBP 2,849,903.75, and P3 holds settlement
  fixed. I predict billed equal to within GBP 1. Total collected is GBP 2,624,823.89. I predict it
  within ±2%: the household now pays the issued ask rather than the true-kWh sum, so it moves, but I
  cannot yet say which way.
- **P10 (bad debt, read with P4).** The P&L's `total_bad_debt` comes from the world's
  `balance_write_offs` over the issued bills. The desk does not feed it, but the household's payments
  do (P9), so P4's band stands.

## Grade

*(written after the run returned, 2026-10-28 17:40 GMT. The predictions above are unedited.)*

The run at b2fc50facf finished its full window (`OUTCOME: SURVIVED`, DONE.json at 17:16 GMT).
- The ledger was rebuilt with `/var/tmp/fresh-run-scripts/build_ledger.py`.
- It was graded in a worktree at origin 2ebb0ac18 by `/var/tmp/desk-wo-probe/grade.py`. That script
  runs the whole suite over all 1,293 accounts, with page records built in memory, as the 1a02c46116
  grade did.
- Output: `/var/tmp/deskfix-grade/grade.{txt,json}`. The baseline is the 1a02c46116 ledger.

| | prediction | result | grade |
|---|---|---|---|
| P1 | overdue row at most 10,230 (from 12,730) | **9,455 of 32,726** | HOLDS |
| P2 | over 90% of non-zero step amounts differ | 32,776 of 32,789 (100.0%) | HOLDS |
| P3 | gross GBP 1,656,590.92 to the penny | GBP 1,656,637.74 (+46.82) | REFUTED |
| P4 | bad debt GBP 10,783.88 ± 25% | GBP 10,820.13 (net GBP 658,560.84) | HOLDS |
| P5 | at most 85 min, at most 12.5 GB | 73.9 min; VmHWM of the run process 5.7 GB, sampled every 5 s | HOLDS |
| P6 | no row beyond its ceiling | 0 unexcepted, 5 excepted | HOLDS |
| P7 | at least 500 breaches after the page's write-off | 723 on 112 households (720 on 112 before) | HOLDS |
| P8 | journeys, steps and desk write-offs ± 15%; write-off GBP below 4,466.12 | 7,374 / 39,985 / 63, GBP 4,423.08 | HOLDS |
| P9 | billed within GBP 1, collected ± 2% | billed +GBP 159.07; collected GBP 2,627,423.74 (+0.10%) | REFUTED (billed) |

**P3 and P9 are refuted, and the premise behind them was wrong.** "Nothing in settlement changed"
did not account for the desk's ledger also being the company's own bad-debt belief. Renewals price
from it (`LivePaymentTriad.default_belief_rate`, read at `run_phase2b` l. 3496 and l. 4269).
Posting the issued bill moved what the company learns, and so moved renewal prices by fractions of
a penny per kWh:
- 3,814 bills changed on 461 accounts, 3,406 of them fixed terms.
- Example: OCC-451a78ee1a06's July 2018 SVT rate went from 9.555p to 9.550p.
- One account, SYN-2016-045, has a different set of periods: a renewal decision went the other way.

This is the company learning from a truer book, as designed. It is not a leak.

**A row the pre-registration did not name moved: `INV_OVERDUE_WITHIN_BALANCE` went from 4 to 0.**
Its four residuals were bills the billing ledger holds for VAT review, which the desk dunned. A held
bill now posts nothing to the desk. That exception is retired.

**What remains on the overdue row: 9,455, causes by the probe's count**
(`/var/tmp/desk-wo-probe/lag.py`, 9,454; the runner's rounding counts one more):

| class | steps | households | cause |
|---|---|---|---|
| after the page's first write-off | 723 | 112 | three write-off dates for one leaver's debt (finding, "The second cause traced") |
| penny: the desk's figure is at most 2p above the page | 2,985 | — | the desk's ask and the printed bill round apart; not traced to the line |
| a payment the page posted that the desk has not yet seen | 466 | 107 | the page posts a direct debit on its due date, and the desk gets it when it crosses (1 day on 315, 7 days on 144) |
| above 2p, before any write-off | 5,280 | — | **not attributed** |

The lead for the 5,280 is one case, OCC-198d2b2c01a7 in April 2025. The page marks every bill
paid on its due date, while the desk prints GBP 102.17 and then GBP 225.97 overdue before curing on
18 May. The page reads the world engine's resolved payment outcomes, and the desk reads the payments
the triad delivered. So the two records disagree on whether the money came in, not on what was
billed.

**Verdict.** The desk-input fix holds on a run. It removes 3,275 of the 12,730 breaches, and the
second row's four. The exception ceiling is set to the measured 9,455, with the classes above
written into its reason. The correctness stretch's exit test is still not met: 5,280 breaches are
unexplained, and two named causes (the write-off dates and the payment record) are open design
changes.
