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
