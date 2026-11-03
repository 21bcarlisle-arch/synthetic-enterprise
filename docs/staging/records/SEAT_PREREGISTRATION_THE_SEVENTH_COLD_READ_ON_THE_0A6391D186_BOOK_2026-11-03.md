**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# Preregistration: the seventh cold read, on the 0a6391d186 book (2026-11-03)

Written before the packet is rendered and before the reader is briefed. DIRECTION row
`the-seventh-cold-read-on-the-published-0a6391d186-pages`. The reading that grades it will be
`records/SEAT_READING_THE_SEVENTH_COLD_READ_ON_THE_0A6391D186_BOOK_2026-11-03.md`.

**The premise, re-measured.** The two commits the item cites (0a6391d186, 19aa987bc) are on origin because they
are the book and its publish, not because a read landed. No reading of this book exists under `records/`. The
read is still owed.

**What is read.**
- The book is 0a6391d186: 1,293 accounts, 52,828 invoices, 752 households in the picker.
- The pages are origin's `site/` at 1eaf19d78d, extracted with `git archive` to `/var/tmp/seventh-read/tree/site/`
  and served on 127.0.0.1. This is what is live. The cast was regenerated at 03:24Z and last touched by
  98caf45105, so the pages carry the N12 page fix (4b0025c9b1) on a book whose code predates it.
- The book's code does **not** carry the N13 adoption fix (ea2f3394dc), the weather-store cover (7ec8b1030d), the
  held-opening-estimate release (54f76662d1) or the PROS-2020-0191 desk-cure trace (c144971dab).
- The cast is the sixth read's households: PROS-2025-0022, SYN-2016-031, PROS-2017-0264, SYN-2016-368,
  SYN-2016-210, PROS-2017-0233, PROS-2019-0246; EV empty.

## Method

- **The reader's tree** is made by `tools/blind_worktree.py` at `/var/tmp/blind/seventh-read-0a6391d186`, and
  checked clean before the reader starts. The reader is told to read `BRIEF.md` only.
- **The packet** is rendered with Playwright by the fourth read's route (`/var/tmp/fourth-read-scripts/render.mjs`):
  Section A is every moment of the eight slots; Section B is five households.
- **Section B** is drawn by `random.Random(20261104).sample(…, 5)` from the picker's 752, less the 74 ids that
  appear in any earlier read's packet or record and less the 7 cast households (678 left):
  **SYN-2016-566, PROS-2019-0261, SYN-2016-024, SYN-2016-109, SYN-2016-328.** No household is added by name.
- **The reader's trade**, one no reader has used: a supplier's consumer-protection and collections practitioner
  who knows SLC 27 (payment methods, ability to pay, debt and disconnection), SLC 21BA back-billing, the Standards
  of Conduct (SLC 0), final bills and credit refunds, and vulnerability. The brief names no expected finding and
  asks no named question.

## The classes already open, so the reading can say which findings are known

Grader-only; none of this goes in the brief.

- **N13**: metered gas repeats last year's month to the decimal. Decided world-side (ea2f3394dc); 227 of 477 gas
  premises had no weather cell. Not fixed in this book, so it should still print.
- **N12**: a two-rate bill printed one summed read. Fixed on the page (4b0025c9b1), so it should not print.
- **The E7 1.5p night line**: a two-rate bill prints the energy component as the unit rate
  (`SEAT_FINDING_A_PRINTED_ECONOMY_7_BILL_SHOWS_A_1_5P_NIGHT_RATE_2026-11-03.md`). Open.
- **Debt held flat after the last rung**: the "after the last rung" GAP (first read O17; fifth and sixth reads'
  O11), and 1eaf19d78d's measurement that 0 of 35 year-overdue accounts went 12 months without a desk act.
- **Two "notice before the miss" refusals** on the collections ladder (third read; collections-tone finding).
- **Contract layer**: a fix billed at the cap; one £/MWh for two fuels; renewal notice timing; a committed rate
  read from a stub (first read O5, O7, O9, O11; fourth read N9).
- **Mover / cross-fuel**: the O32 family (credit shown per fuel, refund dates).
- **Ledger gaps equal to deemed charges** (first read O26, fourth read O24).
- **Opening reads from zero at switch-in** (the open opening-read finding).
- **Overdue class, held estimates billed at the next actual read, the cleared-while-owed debt stories**, the
  London weather series (fifth read O17), carbon against usage, and copy/denominator classes from reads one to six.

**Known breach households at 0a6391d186** (from `docs/reports/DOMAIN_INVARIANTS.md`): 0 unexcepted; 6 rows carry
named, dated exceptions (EPG household rate 350, PPM credit-billed 12, EBSS 6+6, carbon panel 6, estimated run 3).

**What counts as a new class:** an objection the seat confirms in the record or the page code, and that no earlier
read's O/N list, open finding or domain-invariant row already names.

## The three named checks, made by the seat after the read, over every page

- (a) **Back-billing.** No domestic bill issued from 1 May 2018 charges for energy used more than 12 months before
  it, unless the account is flagged as the customer's fault. (The suite FLAGS 144 periods.)
- (b) **Debt after the last rung.** Of accounts whose collections journey reaches its last rung with a balance
  still owed, how many print no further act for 12 months.
- (c) **Final bill and refund.** Every account that leaves with a credit is refunded, and the refund date follows
  the final bill within a credible window (SoC / SLC 27.17-style "promptly", knowledge page first).

## Predictions

| # | prediction | range |
|---|---|---|
| P1 | slots filled (known, a check) | 7 of 8; EV empty |
| P2 | the reader grades the storage-heating slot | valid (the winter Day/Night moment is now shown) |
| P3 | objections | 20–45 |
| P4 | new classes confirmed | at least one; each of the six earlier reads found one |
| P5 | N12 recurs as an objection | no |
| P6 | N13 recurs as an objection | no: a collections reader will not compare gas years. If it does, it is N13, not new |
| P7 | the reader raises debt or collections conduct (the last-rung GAP, notice timing, ability to pay) | yes, at least two objections, and all map to known classes |
| P8 | named check (a): domestic periods back-billed beyond 12 months | non-zero, within the suite's 144 flagged |
| P9 | the exit-test legs | leg one MET (0 unexcepted, 6 excepted), leg two MET, leg three NOT MET (follows P4); the stretch does not exit |

P4 and P9 are written against our own thesis (F11). If P4 is refuted, the read meets leg three.

## Results

*(Filled in the reading, beside each prediction.)*
