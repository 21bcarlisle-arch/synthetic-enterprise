**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# Preregistration: the eighth cold read, on the b3ce2a4e73 book (2026-11-04)

Written before the packet is rendered and before the reader is briefed. Lane-0 item `the-eighth-cold-read`. The
reading that grades it will be `records/SEAT_READING_THE_EIGHTH_COLD_READ_ON_THE_B3CE2A4E73_BOOK_2026-11-04.md`.

**The premise, re-measured.** The one commit the item cites, b3ce2a4e73, is on origin because it is the book's
producing commit, not because a read landed. No reading of this book exists under `records/`. Focus item 1's cast
exists (`records/SEAT_RECORD_THE_B3CE2A4E73_BOOK_GRADED_AGAINST_ITS_FIXES_PREDICTIONS_2026-11-04.md`). The read is
still owed.

**What is read.**
- The book is b3ce2a4e73 (`docs/reports/run_output_b3ce2a4e73_20261103T175203Z.json`): 1,291 accounts, 52,715
  invoices, 751 households in the picker. It is the first book carrying N14 (c6e1a29e1), N15 (6a3da3e48), N16
  (d14ff599e), e28089f99 and the HDD store rebuild (7ec8b1030). It does not carry ba868134c or 5d3d11da0c.
- The pages are the ones focus item 1 built with the publisher's own chain, unpublished:
  `/var/tmp/fresh-grade-b3ce2a4e73/tree/site/`, served on 127.0.0.1:8798. **These are not the live pages.** The
  publisher offers this book itself when the 9 Nov window opens.
- The cast: switch_in PROS-2025-0022, renewal SYN-2016-592, estimate_trap PROS-2017-0264, mover SYN-2016-368,
  debt SYN-2016-217, ev (empty), storage_heating PROS-2020-0189, shock_2022 PROS-2019-0246.

## Method

- **The reader's tree** is made from `tools/blind_worktree.py`'s `COLD_READER_SITE` and `check`, at
  `/var/tmp/blind/eighth-read-b3ce2a4e73`, and checked clean before the reader starts. The reader is told to read
  `BRIEF.md` only. As on the seventh read, there is no finished-book directory with `DONE.json`, so the leak check
  runs against the run output and the grade scratch in place of the book.
- **The packet** is rendered with Playwright by the fourth read's route (`/var/tmp/fourth-read-scripts/render.mjs`).
  Section A is every moment of the eight slots; Section B is five households.
- **Section B** is drawn by `random.Random(20261105).sample(…, 5)` from the picker's 751, less the 82 ids that appear
  in any earlier read's packet or draw and in this cast (669 left): **OCC-eb72725807da, PROS-2016-0187,
  SYN-2016-531, OCC-a8253b022c52, SYN-2016-185.** No household is added by name.
- **The reader's trade**, one no reader has used: an Ofgem price-cap and tariff analyst who knows the default tariff
  cap methodology (SLC 28AD; the wholesale, network, policy, operating, EBIT and headroom allowances), payment-method
  and multi-register differentials, the EPG and EBSS, fixed-term pricing against the forward curve, and how
  tariffs and rates appear on a bill (SLC 31A). Earlier trades were billing arithmetic, GB metering and settlement,
  and consumer protection and collections.
- **The brief carries three seat-named questions** the reader answers whatever its trade, besides its own
  objections: (a) does each bill's unit rate and standing charge sit between the period's wholesale cost and its
  cap; (b) what is a meter here: does one serial, MPAN or MPRN stand for one meter, and does an actual read differ
  from last year's; (c) what was the payment method on each bill's date. The brief names no expected finding.

## The classes already open, so the reading can say which findings are known

Grader-only; none of this goes in the brief.

- **The gate on this book** (focus item 1's grade): 203 unexcepted breaches on 7 rows. INV_ESTIMATED_RUN 53,
  INV_OVERDUE_WITHIN_PAGE_BALANCE 128, carbon panel 14, billed ex-VAT vs revenue 5, contiguity and opening 1 + 1
  (SYN-2016-604g), estimate after latest actual 1. Excepted: EPG household rate 307, PPM credit-billed 12, EBSS 6 + 6.
- **N14's edge**: the catch-up cap tested against the period end, not the issue date (5 bills).
- **N15's residue**: 7 re-offers ba868134c fixed after this book was produced.
- **The debt slot's "cleared while still owed"** refusals (3).
- **The E7 1.5p night line** on a printed two-rate bill.
- **Profile class 2 rows breached by the E7 and PC2 builds**; **the DD balance book keeps a level DD after the
  mandate ended**; **the desk never ran on five accounts the ledger dunned**; **held estimates billed at the next
  actual read**.
- **Contract layer**: one £/MWh for two fuels, renewal notice timing, a committed rate read from a stub (first read
  O7, O9, O11; fourth read N9). "A fix billed at the cap" is now N16, fixed in this book.
- **Mover / cross-fuel** (the O32 family), **ledger gaps equal to deemed charges**, **opening reads from zero at
  switch-in**, the London weather series, carbon against usage, and the copy and denominator classes of reads one
  to seven.

**What counts as a new class:** an objection the seat confirms in the record or the page data, and that no earlier
read's O/N list, open finding or domain-invariant row already names.

## The three named checks, run by the seat over every page (1,292 page files)

Sources: `docs/domain_artefact_library/regulatory/ofgem_cap_unit_rate_composition.json` (per payment method and cap
period: the ex-VAT cap unit rate and standing charge at the regional median, and the DF+CM wholesale floor at the
regional minimum), and `ofgem_default_tariff_cap_windows.json`.

- (a) **Price between wholesale and cap.** For each domestic single-register bill: is the printed ex-VAT unit rate
  at or above the period's wholesale floor (DF+CM, lowest region), and, on a default tariff, at or below the cap
  for its payment method (median region, so a regional rate above it is a flag, not a breach)? Is the standing
  charge at or below the cap's? A fixed term is graded only for the floor, and a fixed rate under a later floor is
  a hedge outcome, not a defect.
- (b) **What a meter is.** Per account and fuel: how many serials, MPANs or MPRNs; does each serial carry one MPAN
  or MPRN; does a serial change without a closing and opening read; on actual-read bills, does the period's use
  equal the same months a year earlier to 0.1 kWh.
- (c) **Payment method on the bill's date.** For each bill: the method of the payments that settle it, from the
  page ledger. Count bills settled by direct debit after the account's last direct-debit mandate, and prepayment
  accounts billed as credit.

## Predictions

| # | prediction | range |
|---|---|---|
| P1 | slots filled (known, a check) | 7 of 8; EV empty |
| P2 | the reader grades every filled slot valid | yes for 6 or 7 of 7 |
| P3 | objections | 20–45 |
| P4 | new classes confirmed | at least one; each of the seven earlier reads found one |
| P5 | the price analyst raises a price-level objection | yes, at least two; all map to known classes (EPG household rate, E7 night line, contract layer) |
| P6 | check (a): default-tariff single-register bills under the wholesale floor | 0 |
| P7 | check (a): default-tariff bills above the median-region cap | non-zero, on no more than the 22 households the cast's `above_cap` census names |
| P8 | check (a): default-tariff standing charge above the cap | 0 (the suite's two standing-charge rows are clean) |
| P9 | check (b): a serial carrying more than one MPAN or MPRN | 0 |
| P10 | check (b): actual-read gas pairs repeating last year's month to 0.1 kWh | about 10, as focus item 1's census |
| P11 | check (c): bills settled by direct debit after the mandate ended | non-zero (the open DD-balance-book finding) |
| P12 | the exit-test legs | leg one NOT MET (203 unexcepted), leg two MET, leg three NOT MET (follows P4); the stretch does not exit |

P4 and P12 are written against our own thesis (F11). If P4 is refuted, the read meets leg three.

## Results

*(Filled in the reading, beside each prediction.)*
