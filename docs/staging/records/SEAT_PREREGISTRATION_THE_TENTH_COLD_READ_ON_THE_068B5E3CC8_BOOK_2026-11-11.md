**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# Preregistration: the tenth cold read, on the 068b5e3cc8 book, the first book that passes the gate (2026-11-11)

Written before the packet is rendered, before the gate is re-graded on the scratch pages, before the seat's checks run
and before the reader is briefed. Lane-0 item `the-tenth-cold-read-on-the-first-book-that-passes-the-gate`. The
reading that grades it will be `records/SEAT_READING_THE_TENTH_COLD_READ_ON_THE_068B5E3CC8_BOOK_2026-11-11.md`.

**The premise, re-measured.** The embargo (`SEAT_RECORD_THE_TENTH_COLD_READ_WAITS_BECAUSE_NO_BOOK_PASSES_THE_GATE_2026-11-09.md`)
waited for a book the gate passes. 6fff2c257 records one: `run_output_068b5e3cc8_20261110T190254Z.json` through origin
3f74b93289's page reads 0 unexcepted, 9 excepted, refuse False (`/var/tmp/grade-d1/control-068-at-3f74/grade.txt`).
Origin is now 6fff2c2575, which adds one staging file to 3f74b93289, so no page code moved. No D1 book exists
(D1's build is not on origin). The read is owed and this is the book.

**What is read.**
- The pages are rebuilt from that book by the publisher's customer-page chain (`/var/tmp/fourth-read-scripts/pages.py`)
  in a scratch tree at origin 6fff2c2575 (`/var/tmp/tenth-read/tree/`), **then** `generate_explore_hh_day` and
  `generate_explore_carbon`, as the ninth read's correction requires. **These are not the live pages.**
- **Section B** is `random.Random(20261111).sample(pool, 10)`. The pool is the picker's households less the 99 ids in
  any earlier read's draw or cast (`/var/tmp/tenth-read/seen_before.json`) and less this book's cast. No household is
  added by name. The drawn ids are recorded in the reading.

## Method

- The reader's tree from `tools/blind_worktree.py`, checked with `--check`; the reader reads `BRIEF.md` only, and the
  priors-first line sits in the brief's first 30 lines.
- The packet is rendered with Playwright by the fourth read's route: every moment of the eight slots, all six stages of
  each of the ten households.
- **The trade, new to these reads:** a supply-point registration and meter data-quality analyst (MPAS / Xoserve UK
  Link, the MAP/MOP/DC flows, BSCP504 and the UNC read rules). Earlier trades: the generalist (1–5), metering and
  settlement (6), consumer protection and collections (7), the price-cap analyst (8), the revenue-assurance auditor (9).
- **The brief carries the seat's named questions, to be checked by eye:** (a) price between wholesale cost and cap;
  (b) one meter serial per supply point, and whether an actual read's use differs from the same month a year earlier,
  on both fuels; (c) the payment method on each bill's date; (d) what happens to an account's balance after it closes.
  It names no expected finding and says nothing about the 34-supply-point serial row, N17, or the excepted classes.
- **The gate** is re-graded by calling `background.process_run_complete._domain_invariant_gate_permits_publish` from the
  scratch tree, on the scratch pages.
- **The seat's checks over every page file:** serials carrying more than one supply number (and supply numbers
  carrying more than one serial); same-month change of actual-read use on each fuel; payment method on each bill's
  date; closed accounts holding a balance of GBP 5 or more a year or more after their last bill.

## Predictions

| # | prediction |
|---|---|
| P1 | The gate on the scratch pages reproduces 6fff2c257: 0 unexcepted, the same 9 excepted rows, refuse False. (If it does not, the read stops: the book does not pass at origin's head) |
| P2 | Explore cast: 8 of 8 filled |
| P3 | Seat check, serials: 0 serials on two or more supply numbers. Supply numbers on two or more serials: under 5% of supply points (an exchange is lawful) |
| P4 | Seat check, repeats: electricity median same-month change under 3% (N17, excepted, not fixed); gas 8–18% |
| P5 | Seat check, payment method: 0 prepayment statements paid another way outside INV_PPM_NOT_CREDIT_BILLED's 12 excepted |
| P6 | Seat check, closed balances: still present (the ninth read's GBP 15.7k credit and 21.6k debt class has no landed fix I know of); each side between GBP 5k and 40k |
| P7 | **Control on the reader:** unaided, it objects that some household's metered electricity repeats or barely moves year on year (N17). p ≈ 0.6, because the trade reads consumption data quality for a living |
| P8 | 20–40 objections |
| P9 | At least one new class (every earlier read found one); at most three. p(no new class) ≈ 0.2 |
| P10 | The reader raises nothing on one-serial-per-supply-point that survives the seat's check (P3) |
| P11 | Exit legs: leg one MET (P1); leg two MET if the reader grades at least 6 of 8 slots valid and no slot prints a gate-breaching figure; leg three NOT MET (P9) |

## Reverse

Delete this file. Nothing outside `docs/staging/` is touched.
