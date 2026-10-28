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
