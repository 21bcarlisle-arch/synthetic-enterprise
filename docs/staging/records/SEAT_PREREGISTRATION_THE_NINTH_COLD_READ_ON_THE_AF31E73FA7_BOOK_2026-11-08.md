**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# Preregistration: the ninth cold read, on the af31e73fa7 book (2026-11-08)

Written before the packet is rendered, before the gate grade or the named checks run, and before the reader is briefed.
Lane-0 item `the-ninth-cold-read-on-the-next-fresh-book`. The reading that grades it will be
`records/SEAT_READING_THE_NINTH_COLD_READ_ON_THE_AF31E73FA7_BOOK_2026-11-08.md`.

**The premise, re-measured.** The item names "the book now running from f248d5ffa". The run that was in flight at the
draw was the sim-runner's af31e73fa7 run (started 22:59Z on 7 Nov). f248d5ffa is an ancestor of af31e73fa7, so this
book carries 8b6316995 (the BSCP504 ceiling), 12a470de7 (the cash record) and the level DD schedule (8178e24218). It
does **not** carry a fix for the level-DD dunning finding: that item (`fix-level-dd-households-dunned-per-bill`) is
still claimed and unlanded. So the defect the reader is not told about should be on these pages. No reading of this
book exists. The read is owed.

**What is read.**
- The book is `docs/reports/run_output_af31e73fa7_20261107T225950Z.json` (finished 00:40Z, 8 Nov): 1,302 accounts,
  53,873 invoices, 757 households in the picker.
- The pages are built by the publisher's own customer-page chain (`/var/tmp/fourth-read-scripts/pages.py`) in a
  scratch tree at origin 8b8a737211, with that book as `run_output_latest.json`. The code that builds pages is the same
  at af31e73fa7 and 8b8a737211. Only `tools/domain_invariant_runner.py` differs (+34 lines), and the grade uses
  origin's. The tree is `/var/tmp/ninth-read/tree/site/`, served on 127.0.0.1:8799. **These are not the live pages.**
- The cast is 8 of 8 filled: switch_in PROS-2025-0022, renewal SYN-2016-592, estimate_trap PROS-2017-0264, mover
  SYN-2016-527, debt SYN-2016-217, ev PROS-2017-0183, storage_heating PROS-2020-0189, shock_2022 PROS-2019-0246.
- **Section B** comes from `random.Random(20261108).sample(pool, 10)`. The pool is the picker's 757 households less
  the 87 ids in any earlier read's draw and less this cast, leaving 669. The draw is **SYN-2016-035, SYN-2016-250,
  PROS-2020-0104, PROS-2024-0335, SYN-2016-136, SYN-2016-439, OCC-1a3fe25a0372, SYN-2016-428, SYN-2016-206,
  OCC-8e60215a8bd9.** No household is added by name.

## Method

- **The reader's tree** is built from `tools/blind_worktree.py` and checked with `--check`. The reader is told to read
  `BRIEF.md` only, and the line saying that its priors come first sits inside the brief's first 30 lines (the eighth
  read's order slip).
- **The packet** is rendered with Playwright by the fourth read's route. It holds every moment of the eight slots and
  all six stages of each of the ten households.
- **The trade, new to these reads:** a revenue-assurance and billing-operations auditor from a GB supplier's internal
  audit function. This person reconciles bills, payments and account balances, and knows direct-debit schemes, the
  bill and statement rules (SLC 31A), VAT on domestic energy, accounting for unbilled revenue and credit balances, and
  how a margin is built from revenue, wholesale, network, policy and operating cost. Earlier trades were the
  generalist (reads 1–5), metering and settlement (6), consumer protection and collections (7), and the price-cap
  analyst (8).
- **The brief carries the seat's named questions:** (a) price between wholesale cost and cap; (b) what a meter is, and
  whether an actual read differs from last year's; (c) the payment method on each bill's date. It names no expected
  finding, and it **says nothing about level direct debits, dunning, arrears or "overdue"**.
- **The gate** is graded by calling `background.process_run_complete._domain_invariant_gate_permits_publish` from the
  scratch tree. That is the publisher's function, reading `docs/state/billing_ledger.json` and `site/data/customers`,
  with the cast beside the customer pages. It is not the scratch `grade.py`.
- **The seat's checks over every page file:** one meter serial per supply point; same-month repeats on both fuels; the
  payment method on each bill's date; the unit rate between wholesale and cap, per fuel and year; and the contribution
  label after cost to serve.

## Predictions

| # | prediction |
|---|---|
| P1 | Through the publisher's path, both page rows grade on a real count: INV_HOUSEHOLD_PAGE_TARIFF_IS_THE_BILLED_TERM and INV_HOUSEHOLD_PAGE_MISSED_BILL_WAS_NOT_SETTLED each read CHECKED > 0, neither UNREACHED nor NOT_IN_EXPORT. **No code change is needed** to build `cast_tariffs` and `payment_tallies`: `load_book` and `load_printed` read `explore_cast.json` beside the page files |
| P2 | TARIFF_IS_THE_BILLED_TERM: 0 breaches. MISSED_BILL_WAS_NOT_SETTLED: at least 1 breach, on level-DD households, if any cast household is on a level DD |
| P3 | INV_OVERDUE_WITHIN_PAGE_BALANCE between 1,000 and 2,500, and INV_PAYMENT_RECORD_RECONCILES_TO_COLLECTIONS_DUE between 20 and 80, almost all on level-DD households (fa915ac0d7 read 1,724 and 45). The gate refuses |
| P4 | **The reader finds the level-DD dunning defect unaided:** it says that a household on a direct debit is shown as overdue, chased or offered an arrangement while its balance is in credit or nil. My confidence is about 0.6, because the auditor trade reconciles balances, and 176 of 454 level-DD households on the last book showed the defect |
| P5 | 25–45 objections |
| P6 | At least one new class (every earlier read found one). At most three |
| P7 | Named checks: 0 serials carrying two supply numbers; 0 default bills under the wholesale floor; default bills at the cap from 2019 (median within 1% of the median-region cap) |
| P8 | Same-month change in metered electricity: median still under 3% (N17 is the world's side and is not fixed). Gas: 8–18% |
| P9 | Contribution after cost to serve: the page names it a contribution. The book-wide resi figure is 7–12% in the years with full cover (N21 regraded to 9.30% on fd91027799) |
| P10 | Payment method: no prepayment statement paid another way, except the excepted INV_PPM_NOT_CREDIT_BILLED class |
| P11 | Exit legs: leg one NOT MET (P3); leg two MET (8 of 8 filled, and the reader grades at least 6 valid); leg three NOT MET (P6) |

## Reverse

Delete this file. Nothing outside `docs/staging/` is touched.
