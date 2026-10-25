**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`
**Knowledge:** `home-moves` -- `docs/market_research/home_moves.md` §8.8 ("Who sets the refund day")

# Every late closure refund was the world's own latency draw, not the final bill's date

Drawn as delivery-lane direction `closure-refunds-meet-gsop-reg-6d`. Found by the grade of
`docs/reports/run_output_b2bc3d8da5_20261025T1230Z.json`.

**What.** 10 of the run's 100 `credit_refund_log` entries (all `account_closure`) were flagged late.
Each one's final bill is its last bill and was issued at that bill's period end. Its refund was paid
13 to 24 working days later. The route between the two dates is
`simulation/credit_refund_events.py`, which drew the day itself.

| Account | Final bill issued | Refund paid | Working days | Reg 6D in force? | Payment owed |
|---|---|---|---|---|---|
| OCC-371b33ca4bdf | 2017-12-31 | 2018-01-29 | 20 | no | — |
| PROS-2016-0117 | 2017-12-31 | 2018-01-25 | 18 | no | — |
| SYN-2016-018 | 2017-01-10 | 2017-02-07 | 20 | no | — |
| SYN-2016-395g | 2017-09-30 | 2017-10-18 | 13 | no | — |
| SYN-2016-037g | 2020-04-29 | 2020-06-03 | 23 | yes | £30 |
| OCC-561d240ea21a | 2020-09-02 | 2020-09-30 | 20 | yes | £30 |
| PROS-2016-0024 | 2020-12-31 | 2021-01-27 | 18 | yes | £30 |
| PROS-2020-0012 | 2024-01-08 | 2024-01-30 | 16 | yes | £30 |
| SYN-2016-353 | 2024-08-02 | 2024-09-06 | 24 | yes | £30 |
| OCC-bec72a04dec8 | 2025-04-11 | 2025-05-06 | 14 | yes | £40 |

**Cause: the company's refund path, held on the wrong side of the wall.** The final bill's date was
not the problem: every refund is measured from the same issue date the grade uses. The world held
`ON_TIME_PROBABILITY = 0.90` with ranges of 2–10 and 11–25 working days. The probability was
unsourced, and it was a supplier's operating speed treated as a property of the world. The seam module
had already named this as residual (1). All 10 late refunds are that draw's late arm. The on-time arm
never read back as late on the company's bank-holiday calendar.

There was a second defect. Reg 6D came into force on 1 May 2019 (SI 2019/218 reg 1(1)), and the book
graded 2017 refunds against it. Those 4 refunds owe no standard payment.

**Fix.** The company sets the day it pays (`company/billing/credit_refund.py`,
`scheduled_refund_date`). It pays on the 10th working day after the final bill's issue, on its own
bank-holiday calendar. The deadline is the one day the rule fixes. Paying on it holds the customer's
money longest, which errs against our thesis. `paid_date` no longer crosses the seam. A late refund
is graded a reg 6D failure and carries `reg_6d_payment_owed`. That is £30, or £40 for a failure
from 2 January 2025 (`company/regulatory/gsop.py`, `standard_payment_gbp`, citing Ofgem's GSoP
uplift decision). "SLC 14" is relabelled reg 6D in both files and in the seam. The log key is now
`breached_reg_6d_deadline`.

**Re-grade.** I replayed the run's own 100 final-bill dates and credits through the new path. Result:
0 late, every refund paid on working day 10. Under the old log, 6 late refunds would have owed £190.
This is a replay of the same inputs, not a fresh run. The next published run will carry the change.
The control is `tests/company/interfaces/test_credit_refund_requests_seam.py`. Test 4 makes a late
refund occur and grades its payment: £30, £40, and none before commencement. Test 5 makes the
company's schedule late and checks that the world's published log carries every breach with its
payment.

**Still open, named.**
- The payment is graded and not booked to cash or P&L, the same limit as the refund itself
  (§8.8a choice 10, owed with DD3).
- Ofgem's further payment, due if the first is not paid within 10 working days, is not modelled.
- The published lag distribution moves. It used to be spread across 0–24 working days and is now
  always 10. That is a stated choice, and a supplier's real lag inside the window is a GAP.
- `GSOPBook._GSOP_AMOUNT_GBP` still carries a flat £30 for every standard. It should move to
  `standard_payment_gbp` in its own commit, because that changes published GSoP totals from 2025 on.
