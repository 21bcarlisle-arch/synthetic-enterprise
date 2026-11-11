**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# Preregistration: the eleventh cold read, on the first D1 book, graded through the publisher's gate first (2026-11-11)

Written at 01:40 UTC while the book is still being simulated (PID 37703, `run_output_e1587ec5b_20261111T012324Z.json`,
started 01:23), so before any page is built, before the gate is graded and before a brief exists. Lane-0 item
`the-eleventh-cold-read-on-a-book-the-publishers-gate-passes`.

**The premise, re-measured.** The four commits the item cites are all on origin. The tenth read (5fdf9c106) found the
068b5e3cc8 book refused at the publisher's gate, so a read on a book the gate passes is still owed. No book built on or
after D1 (b47832f7e) exists yet; the e1587ec5b run is the first. Origin is 45e531f233. Since e1587ec5b it adds only the
tenth read's staging files and four blind rows (N25 to N28, `checkable: false`) in `DOMAIN_INVARIANTS.yaml`, so the
page code and the gate's checkable rows are the book's own.

## Order, fixed now

1. **The gate first.** `/var/tmp/eleventh-read/scripts/build.sh <book>` builds the pages in a scratch tree at origin
   with the publisher's customer-page chain, then `generate_explore_hh_day` and `generate_explore_carbon`. Then
   `scripts/gate.py <git>` calls `background.process_run_complete._domain_invariant_gate_permits_publish` from that
   tree. **Not** the `launch_d1_book.sh` → `after_run.sh` → `grade.py` chain: it does not build `final_bills`, so it
   reads the closed-account row as NOT_IN_EXPORT (the tenth read's finding).
2. **If the gate refuses, the read does not run.** I record the refusal and its rows, trace any new breach as far as
   one turn allows, and the item waits for the next book. A read on a refused book cannot meet exit leg three.
3. **If the gate passes,** the read runs as the tenth did: `tools/blind_worktree.py` tree checked with `--check`,
   priors in the brief's first 30 lines, every moment of the eight slots and six stages of ten Section B households
   rendered by Playwright. Section B is `random.Random(20261112).sample(pool, 10)`, the pool being the picker's
   households less every id in an earlier draw or cast and less this cast.
4. **The trade, new to these reads:** an Energy Ombudsman case investigator, who reads a household's bills,
   statements, payments and letters from the complainant's side and decides what a supplier got wrong (Ombudsman
   Services' terms of reference, Ofgem's complaint-handling standards, back-billing, SLC 27 payments and refunds,
   SLC 31A bill content, final bills and refunds on closing). Earlier trades: the generalist (1 to 5), metering and
   settlement (6), consumer protection and collections (7), the price-cap analyst (8), the revenue-assurance
   auditor (9), the registration and meter data-quality analyst (10).
5. **The seat's checks over every page file,** run after the gate and before the brief: the tenth read's four
   (`checks.py`, `closed.py`) plus N25 (`fixmove.py`).

## Predictions

| # | prediction |
|---|---|
| P1 | The gate **refuses** the D1 book. p(pass) ≈ 0.35. SYN-2016-493's residue is a close refund sized from the pre-final credit while the direct debit then collects the full final bill. D1 changes how a credit bill meets a leg's debt, not how the close sizes its refund, and the population is drawn from the same seeds |
| P2 | If it refuses, `INV_CLOSED_ACCOUNT_BALANCE_REACHES_ZERO` is the row, with 3 breaches (the same three legs). No other row goes from clean or excepted to unexcepted |
| P3 | D1 moves at least one row's breach or flag count by more than 10% against the tenth read's gate (`/var/tmp/tenth-read/gate.txt`) |
| P4 | Seat check N25: fixed runs with a standing charge moving by more than 1% are still between 600 and 800 (no fix has landed) |
| P5 | Seat check (d): closed accounts a year on holding at least GBP 5, credit side under GBP 1k, debt side between GBP 1k and 10k (the tenth read measured GBP 11.56 and GBP 3,636) |
| P6 | Only if the read runs. **Control on the reader:** unaided, it objects that some page's ledger sentence does not add up to the balance printed (N26). p ≈ 0.5 |
| P7 | Only if the read runs: at least one new class; p(no new class) ≈ 0.2 |
| P8 | Exit legs: leg one NOT MET (P1). Leg two NOT MET: the N28 cast templates are unfixed. Leg three NOT MET or not graded |

## Reverse

Delete this file. Nothing outside `docs/staging/` is touched.
