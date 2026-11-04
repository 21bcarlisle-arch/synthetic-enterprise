**Severity:** RECORDED · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** none — focus `grade-the-b3ce2a4e73-book`

# The b3ce2a4e73 book graded against the predictions of N13, N14, N15, N16 and the debt-slot fix: 9 rows held, 2 missed, and the invariant gate would refuse the book (2026-11-04)

Under the correctness stretch (`docs/staging/advisor/DIRECTOR_RULING_CORRECTNESS_BEFORE_THE_NEXT_FEATURE_2026-10-26.md`),
leg one of the exit test on a fresh book. Nothing was published: the publisher offers this book itself when the window
opens (Mon 2026-11-09 04:00 GMT).

**The book.** `docs/reports/run_output_b3ce2a4e73_20261103T175203Z.json` (finished 2026-11-03T19:14Z; 1,291 accounts,
52,715 invoices, 6,434 applied catch-ups). The code under test is HEAD of this worktree, which has no difference from
b3ce2a4e73 in `company/ saas/ simulation/ sim/ tools/`. Scratch: `/var/tmp/fresh-grade-b3ce2a4e73/` (`ledger.json`,
`grade.json`, `tree/` with the pages built by the publisher's own chain, `pages.log`); scripts `/var/tmp/b3ce-grade-scripts/`.
Five more run files sit beside it with the same producing commit and the same byte size (143,151,996); only the first
was graded.

**Two departures from the chain that graded 85b044be54, named so nobody reads them as the same grade.**
1. That chain read the sim_runner's pickles; this book exists only as the run JSON, so the in-memory page records
   take revenue from `per_customer_lifetime` (what `generate_customer_data` reads) instead of summing
   `p2b__all_records`, and bills/meter reads from the JSON. `INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE` (5) is the one row
   this could move; **I cannot yet say** whether it is the book or the substitution (see finding 3).
2. Payments for (b) are joined by billing account (`Cxxx`/`Cxxxg` share one), from the ledger, not from the desk's own
   ledger book. The definition is the commit's: cash from issue to due date inclusive covers the bill.

## Prediction by prediction

| | Commit | Predicted | b3ce2a4e73 | |
|---|---|---:|---|---|
| (a) uncapped domestic catch-ups, window > 12 months, on a bill paid on receipt, from May 2018 | c6e1a29e1 (N14); 11 on 0a6391d186 | 0 | **5** (+2 gas legs with no payment on their own invoice, DD basis) | **missed** |
| (b) "a further bill missed" re-offers on a day when every bill falling due was paid in its window | 6a3da3e48 (N15); 4,742 of 6,599 | 0 | **0 of 2,224** | held |
| (b) control: re-offers after a truly unpaid bill | same | > 0 | **2,220** (102 accounts); 4 on days with no bill falling due | held (partition is open both ways) |
| (c) gas month-pairs on actual/prepayment reads repeating last year's month to 0.1 kWh | 7ec8b1030 (N13 cause 2); 1,635 of 4,413 on 85b044be54 | the blind row grades no world-side repeats | **9 of 4,362** page-definition; **10 of 2,387** census-definition (world 10, billed 10) | held, with a residual (below) |
| (d) desk cures on a due date still held | P1; 0 of 1,078 on 85b044be54 | 0 | **0 of 1,075** run journeys; 0 of 1,917 ledger journeys | held |
| (e) debt slot, "overdue notice dated before the miss" | e28089f99; 2 -> 0 | 0 | **0 of 374** matched households | held |
| (e) debt slot, "cleared while still owed" | 85b044be54 record: both survivors stay, no new one | PROS-2020-0191 and PROS-2025-0013 only | **3** refused: PROS-2020-0191, SYN-2016-066, SYN-2016-380 | **missed** (two new, PROS-2025-0013 gone; the book differs) |
| (f) Explore slots | d14ff599e; 7 of 8, EV honestly empty | 7 filled, EV empty with the failing check named | 7 filled, EV empty; EV names "did not rise by 1,750-3,300 kWh" (4 of 6), "stated effect not 1,750-3,300" (4 of 6), "no full year either side" (1 of 6), "no electricity supply" (1 of 6) | held |
| (f) tariff label agrees with the covering bill | d14ff599e; 20 of 21 | all but the renewal day | **20 of 20** graded moments, 0 disagree | held |
| (f) storage slot | d14ff599e; night share >= 53%, actual-read winter bill | PROS-2020-0189 | PROS-2020-0189 | held |
| (g) compact billing ledger | 58d49405e2; 91.2 MB committed from the 08f267b666 book | below GitHub's 100 MiB | **84.19 MB (80.3 MiB)**; the same builder wrote 91.17 MB for 85b044be54's 1,293 accounts | held, 19.7 MiB of headroom |

The eight slots: switch_in PROS-2025-0022, renewal SYN-2016-592, estimate_trap PROS-2017-0264, mover SYN-2016-368,
debt SYN-2016-217, ev (empty), storage_heating PROS-2020-0189, shock_2022 PROS-2019-0246. Book breach census on the cast:
`above_cap` 22 of 751 households (19 of 752 before).

## What the misses are

- **(a) is a different cause from the one fixed.** Of the 180 domestic catch-ups from May 2018 whose window starts more
  than 365 days before the bill's issue date, 146 are uncapped, 139 of them on DD (the deferred basis, not graded).
  The N14 fix works: the basis on the 30 pay-on-receipt rows is now `pay_on_bill_true_vs_billed`, not the DD basis. The
  5 that stay uncapped are all 366-583 days from issue and 365 days or fewer from the bill's **period end**
  (SYN-2016-048 2025-01-31 vs window 2024-02-01; SYN-2016-240, SYN-2016-334, PROS-2020-0016 the same; SYN-2016-207's
  April 2018 bill has a period end of 2018-04-30, before the 1 May 2018 start of the domestic rule). `_resolve_catchup`
  receives `bill["period_end"]` as `billing_date_iso`, and the cap tests the window against it. The demand is the issued
  bill, 7 to 14 days later. Filed: `SEAT_FINDING_THE_CATCH_UP_CAP_IS_TESTED_AGAINST_THE_PERIOD_END_NOT_THE_DAY_THE_BILL_WAS_ISSUED_2026-11-04.md`.
- **(e) "cleared while still owed" is not tied to a fix, so the prediction was only "no new one".** Two new households
  carry it. Not traced. Filed: `SEAT_FINDING_THE_DEBT_SLOT_STILL_REFUSES_THREE_HOUSEHOLDS_FOR_CLEARED_WHILE_OWED_2026-11-04.md`.

## N13 holds on this book, and what is left

The world no longer repeats gas use: 1,311 of 2,423 billed pairs repeated on the 08f267b666 census (1,163 world-side);
10 of 2,387 now, 10 world-side and 10 billed, so the bill still prints the world faithfully. By cohort (census): OCC 3
of 445, PROS 0 of 728, SYN 7 of 1,213. On the page definition (prepayment statements included): OCC 1 of 624, PROS 0 of
1,112, SYN 8 of 2,625. One leg with six or more pairs repeats on 10% or more (SYN-2016-131g, the N13 noise leg) against
46 of 79 before. The PROS-2019-0208g flat-4.5-kWh residual is not among them. This is the evidence the blocking finding
asked for: `INV_GAS_MONTHLY_USE_DOES_NOT_REPEAT_LAST_YEAR` still has no evaluator in the runner, so the figure above is
the census script's, not the invariant's, and the finding stays open until the row can fail.

## The domain-invariant grade: not clean, and mostly not the rows the fixes were about

`grade.txt`: **203 unexcepted breaches across 7 invariants; the publish would be refused** (enforcement is on). Against the
85b044be54 grade (9 on 4 rows), the four named there are 0, 0, 0 and 1:

| Row | 85b044be54 | now |
|---|---:|---:|
| INV_E7_METER_BILLED_ON_TWO_REGISTERS | 2 | 0 |
| INV_READ_MONOTONIC | 2 | 0 |
| INV_TOU_BANDS_SUM_TO_THE_TOTAL | 2 | 0 |
| INV_ESTIMATE_FOLLOWS_THE_LATEST_ACTUAL_READS | 3 | 1 (SYN-2016-110 2018-11) |
| INV_ESTIMATED_RUN_CONSISTENT_WITH_THE_METER | 4 (excepted, ceiling 3) | **53** unexcepted, 58 flagged |
| INV_OVERDUE_WITHIN_PAGE_BALANCE | 0 (clean) | **128** (the five kept examples are all OCC-75d17c23c1da, on `arrangement_offered` and `repayment_plan_reoffer` steps; N15 touched exactly that step, candidate not attribution) |
| INV_CARBON_PANEL_KWH_MATCHES_USAGE_PANEL | 6 | 14 (ceiling 6) |
| INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE | 0 | 5 (ceiling 1; see departure 1) |
| INV_PERIODS_CONTIGUOUS / INV_OPENING_IS_THE_PREVIOUS_CLOSING | 0 / 0 | 1 / 1, both SYN-2016-604g gas, 2017-06-30 -> 2017-08-01 (a 32-day period; opening 253.6 kWh above the previous close) |
| INV_UNIT_RATE_EPG_HOUSEHOLD, INV_PPM_NOT_CREDIT_BILLED, INV_EBSS x2 | 350, 12, 6, 6 | 307, 12, 6, 6 (excepted) |

**I cannot yet say** which of these the three supplier fixes or the weather-store rebuild moved. More than one thing
changed between the two books (8cf2ecb744, 1b709ac0e9, N13 cause 1 and 2, N14, N15, N16, the draw), and the 53 are
OCC electricity runs on legs the world change cannot have touched directly. Prediction filed for whoever draws it, before
the measurement: the 53 are concentrated on the 63 accounts N14 re-billed (`rebill_catchups_off_direct_debit`), because
that second pass rewrites the very estimated runs the row bounds. If they are not, the cause is elsewhere. Filed:
`SEAT_FINDING_THE_B3CE2A4E73_BOOK_FAILS_THE_DOMAIN_INVARIANT_GATE_ON_SEVEN_ROWS_2026-11-04.md`.

## Is the ruling's exit readable from this?

Not yet. The three named supplier fixes hold on a fresh book except for the edge in (a), N13's world fix holds, and the
cast is as good as 85b044be54's. But the gate would refuse this book, 203 to 9, and the ruling's exit test is the gate.
That is leg one of two; this record does not close it.

## Reverse

Delete this record and the three findings; nothing outside `docs/staging/` was touched. Scratch is under `/var/tmp`.
