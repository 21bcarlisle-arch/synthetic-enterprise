# Pre-registration: one due date for the collections desk and the billing ledger, on a fresh full run (2026-10-27)

**Item:** `the-collections-desk-and-the-billing-ledger-keep-one-payment-record`, point 2 of
`docs/staging/SEAT_FINDING_THE_COMPANYS_OWN_EVENTS_SHOW_NO_RENEWAL_NOTICE_TWO_PAYMENT_RECORDS_AND_A_CREDITED_PART_MONTH_2026-10-27.md`.

Written before the run returned. What I had already seen: the 2eeb3f0b3 and SLC 22C books both
grade `INV_OVERDUE_WITHIN_BALANCE` at 1,987 of 7,151 and `INV_STATUTE_BARRED_WRITE_OFF_AGE` at 25 of
41. On the 2eeb3f0b3 book, all 7,151 journeys open on a 29th or a 1st. The traces below are what
these predictions rest on.

## The cause, traced

There was one payment outcome, from the triad. The date it was carried on differed between the two
records. A bill's due date had three homes:

| Home | Due date of the bill for month M |
|---|---|
| `tools/generate_billing_ledger.py` (the billing ledger) | period end + generation delay (0-~10 days) + 14 |
| `simulation/arrears_engine._resolve_bills` (the engine) | period end + 14 |
| `simulation/run_phase2b._bill_due_on`, posted through `LivePaymentTriad.record_period` to the company's own ledger, which the collections desk walks | **the 28th of M itself** |

The third is wrong: a bill for October cannot fall due on 28 October, before the month has ended
or been billed. The desk opened its journey on the 29th, one day after that date. A late payment
was dated 28th + days late on the desk, and ledger due + the same days late in the billing ledger.

- **SYN-2016-356.** The desk opens on 29 Oct 2016 for October (desk due 28 Oct). The ledger's
  October bills are due 18 Nov (electricity) and 17 Nov (gas), and both fail. The September bills
  were due 16 Oct and collected that day. Nothing was overdue on 29 Oct in the ledger.
- **OCC-3c914ee8cef5 (statute bar).** The last bills (period to 31 Mar 2017) were paid on 15 Apr
  2017 in the ledger and on 28 Mar 2017 on the desk. The write-off was on 28 Mar 2023, six years
  after the desk's date and 18 days before the ledger's.
- **SYN-2016-132 (statute bar, paid late).** The ledger has the bill due 12 May 2018 and paid 22
  May. The desk has it due 28 Apr and paid 8 May, the same 10 days late. The write-off was on 8 May
  2024.

**All 25 statute-bar breaches are this split.** For 24, the write-off falls exactly six years
after the desk's date for the last payment. That date is two to four weeks before the billing
ledger's. The 25th, "no bill old enough", is PROS-2016-0313. Its final bill (period to 23 Dec 2016)
is due 9 Jan 2017 in the ledger and 28 Dec 2016 on the desk, and the write-off was on 28 Dec 2022.

**The two never-chased failed DDs from O27 are NOT this split.** OCC-3c914ee8cef5g (£48.93, March
2016) and OCC-561d240ea21a (£42.58, October 2017) fall in months the run booked wholly as the
unnamed occupier's debt (`occupier_debt_gbp` equals revenue). So the triad posted £0 to the
desk's ledger, and the engine has no row for the bill. The billing ledger still bills the named
payer and draws its own outcome for a bill with no engine row
(`tools/generate_billing_ledger.py`, the "No row" branch, the 2026-10-15 finding). That draw failed,
so the ledger holds a failed debit nobody was asked to chase. This is a third record of who owes
an occupier-window bill. It is not a due date, and this change does not touch it.

## What changed

1. `simulation/arrears_engine.bill_due_date(customer_id, period_end)` is the one home: period end,
   plus the generation delay moved here from `tools/generate_billing_ledger.py`, plus 14. The
   billing ledger and the engine both read it. The engine's own due dates move later by the
   delay, 3 days on average.
2. The run posts each month's bill to the company's ledger due on `bill_due_date` of that leg's
   last supplied day in the month. The account-close calls give the latest of the account's legs'
   final-bill due dates.
3. The triad keys its draws, outcomes, part-shares and budget year by the bill's month, passed
   explicitly. Before, the due date's month stood in for it, and that month is now usually the
   next one. Every outcome draw is therefore unchanged. What moves is the date each one is read
   on.
4. The DD stop board is now asked at the real due date, and decides on the bills before the one
   asking (`StopNoticeBoard.notice_as_of(..., bills_before=<bill month>)`). Asked at a due date in
   the next month, it would otherwise have built the asking bill itself, with no outcome yet. The
   board control caught this (1 of 4,613 questions, on a 2017 window). A stop whose notice falls
   between the month's end and its due date now applies to that collection. Before, it did not.

## Predictions (full run at origin 170f808884 plus this change)

- **P1.** `INV_OVERDUE_WITHIN_BALANCE` drops from 1,987 to **0-30**. Any residual is a journey
  opened by a non-bill debit, or one whose bill was settled by a crossing on its due date, and each
  is to be named.
- **P2.** `INV_STATUTE_BARRED_WRITE_OFF_AGE` drops from 25 to **0**. A write-off now falls six years
  after a date both records share.
- **P3.** Journey openings are no longer bunched on the 29th and 1st. No single day of the month
  carries more than 15% of them.
- **P4.** These rows move because of this change: the journey count, the
  collections-ordered row, and the provision and default-belief figures read off the company's
  ledger. Ageing now starts two to three weeks later on every bill. I predict the direction only:
  journeys are FEWER, because a household that pays within the month's real terms is no longer
  dunned on the 29th. Other rows also moved on origin since 2eeb3f0b3. A row that moves is
  reported, not attributed.
- **P5.** The never-chased failed DDs (OCC-3c914ee8cef5g, OCC-561d240ea21a) are unchanged. Their
  cause is the occupier-window draw, not the date.

## Grade

*(written after the run returned)*

**The run.** The onedue run named here died in end-of-run reporting, so it was not graded. The
grade is of a fresh full run at origin `1691ec0ecd`. That base carries this change and also
`7cec44a4b` (the occupier-window bill is the deemed account's), `25a8be909` (one EBSS home) and the
SLC 22C statement. Its other rows can therefore move for reasons other than this change. It ran
under `launch_long_job` as unit `longjob-fresh-run-1691ec0ecd`, exit 0, in 3,268 s, peaking under
5 GB. Output is in `/var/tmp/fresh-run-out-1691ec0ecd`, and the grade
(`tools/domain_invariant_runner --ledger`, 1,293 accounts) is in `/var/tmp/onedue-grade-1691/`.
The comparison book is the SLC 22C run (`/var/tmp/fresh-run-out-slc22c`), which graded the two rows
at 1,987 and 25, the same as 2eeb3f0b3.

- **P1: HELD on the count; the residual's cause was mispredicted.** `INV_OVERDUE_WITHIN_BALANCE`
  breached 4 of 7,380, down from 1,987 of 7,151. The cause is neither a non-bill debit nor a
  due-date crossing. The four are PROS-2017-0336 (opened 2018-01-20), PROS-2024-0010 (2024-03-17),
  PROS-2025-0106 (2025-05-16) and SYN-2016-582 (2017-02-19). They are exactly the four accounts in
  the billing ledger's `exception_queue`, and they hold all nine of its rows. Each is a household
  label whose metered load looks like an SME's, so the ledger holds those months' bills for VAT
  review and issues none. The run still posts those bills to the company's ledger, and the desk
  dunns them. A customer cannot owe a bill the supplier has not issued, so this is a defect: one
  bill, issued in one record and held in the other. It is not a due-date split.
- **P2: REFUTED.** `INV_STATUTE_BARRED_WRITE_OFF_AGE` breached 3 of 64, not 0 (from 25 of 41). All
  three have the same shape. A household carries two limitation write-offs, and the first is
  dated six years after a payment that is not the household's last:
  - OCC-6e59dd8b63e8: written off 2025-05-06. That is six years after the gas leg's final bill was
    paid (2019-05-06). The electricity leg's final bill was paid a day later, 2019-05-07, which
    gives the second write-off.
  - SYN-2016-016: written off 2024-03-24, from the electricity bill paid 2018-03-24. The gas leg's
    final bill was part-paid £2.40 on 2018-03-27, which gives the second write-off.
  - SYN-2016-611: written off 2024-09-14, from the bill paid 2018-09-14. The final bill (supply
    ended 16 Sep) was part-paid £2.86 on 2018-09-30, which gives the second write-off.

  In each case a final-bill payment that arrived after a leg closed did not restart the bar for the
  first write-off, although the desk's own rule (`collections_journey.statute_barred_gbp`: zero if
  any payment lands after the bar) would have blocked it if that payment were on the same ledger. Two things
  are NOT established. The first is whether the desk's ledger lacks the post-close payment, or
  bars per fuel leg. The second is whether limitation runs per fuel contract (two contracts, so
  OCC-6e59dd8b63e8 and SYN-2016-016 would be the grader's household reading being wrong) or per
  household account. SYN-2016-611 is single-fuel, so it is a defect on either reading.
- **P3: MOVED, bound MISSED.** Before, openings fell 93.5% on the 29th and 6.5% on the 1st. Now the
  busiest days are the 16th (22.6%), the 17th (17.3%) and the 15th (13.9%), which is the ledger's
  due date plus one. The 15% bound was wrong. Due dates are period end + 0-~10 days + 14, so they
  bunch in mid-month by construction, and a 15% bound assumed a spread that the dates do not have.
- **P4: direction REFUTED.** There are 7,380 journeys, against 7,151: MORE, not fewer. Write-off
  exits rose from 36 to 53, and statute-barred write-offs graded from 41 to 64. Several things
  changed between the two bases, so I cannot attribute the rise. The one-variable run (this change
  alone, on 170f808884) was not made.
- **P5: SUPERSEDED, not graded as predicted.** Neither OCC-3c914ee8cef5g nor OCC-561d240ea21a has a
  failed payment on this book (`failed_payment_count` 0, no payment in the month). That is
  `7cec44a4b`'s doing, not this change's.

Exceptions after this grade (`docs/design/DOMAIN_INVARIANT_EXCEPTIONS.yaml`):
`INV_OVERDUE_WITHIN_BALANCE` is lowered from 1,987 to 4, and `INV_STATUTE_BARRED_WRITE_OFF_AGE` from
25 to 3. Each is rewritten to name its residual. Neither is retired, because both residuals are
open defects with named causes.
