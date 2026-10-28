# Pre-registration: an occupier's bills read the triad's payment truth (2026-10-28)

Written before any run carries the fix. Grade on the first fresh full run whose commit includes it.

## The defect, and what each record counts

`INV_OVERDUE_WITHIN_PAGE_BALANCE` compares two figures. Here is what each one counts:

- **Overdue** is the collections desk's `undisputed_overdue_gbp` on its journey stage. It comes from
  the company's own ledger (`LivePaymentTriad._ledger_book`), and that ledger is fed by the payments
  that crossed the seam: the triad's ONE draw per leg and month (`record_period`).
- **Owed** is the page ledger's `running_balance_gbp`, summed over the household's fuel pages. It is
  built from the billing ledger's payments, and those take each bill's outcome from
  `arrears_engine._resolve_bills`. That function reads the triad's outcome only when the leg's
  `per_customer_behavioral` record carries `world_payment_truth`. Without it, it draws the outcome
  again.

`_build_behavioral_trajectories` built records for `ELEC_CUSTOMERS + GAS_CUSTOMERS` only. The
incoming occupiers' accounts (`OCC-`, B7 home moves) are on neither list. On the b2fc50facf run, 253
of 253 `OCC-` legs carried no truth record, while every C, PROS and SYN leg did. So for every
occupier's bill, the page and the desk read two different payment records of one fact.

**The supplier holds the triad's record**, because it is what crossed the wire. The fix makes the
page read that record too: every leg the triad posted gets a behavioral record that carries the
truth (`simulation/run_phase2b.py`). Test, red on origin c4738b64c9 and green with the fix:
`tests/simulation/test_an_occupiers_bills_read_the_triads_payment_truth.py`.

The lead case: OCC-198d2b2c01a7g, gas bill 808. It was due on 15 Apr 2025, and the page shows it
paid that day. The desk opened `missed_payment` on 16 Apr at GBP 102.17 and dunned it until 18 May.

## The baseline (b2fc50facf book, /var/tmp/deskfix-grade/ledger.json)

Measured with `/var/tmp/onepay-scripts/lag_occ4.py`, which is `/var/tmp/desk-wo-probe/lag.py` with
each class split by account prefix. The total is 9,454 (the runner's rounding counts 9,455).

| class | OCC- | other | total |
|---|---|---|---|
| (a) after the page's write-off | 33 | 690 | 723 |
| (b) at most 2p | 3 | 2,982 | 2,985 |
| (c) a payment the page posted that the desk has not seen | 448 | 18 | 466 |
| (d) not attributed | 2,005 | 3,275 | 5,280 |
| **total** | **2,489** | **6,965** | **9,454** |

Class (c) was read as DD-in-flight, but 448 of its 466 steps are on `OCC-` accounts, so it is
mostly this defect. That explanation is refuted for those 448 steps.

## The other causes inside (d), traced but not fixed here

These are on non-`OCC-` accounts, 3,275 steps.

1. **A credit bill never reaches the desk.** The run posts `max(0.0, ask)` to the triad, so a
   negative bill posts GBP 0. The page nets the credit against the next bill, and the desk duns that
   bill. Example: PROS-2016-0098 has a −58.97 credit bill on 30 Apr 2017. Its 57.18 bill's DD failed
   on 18 Jun. The page shows the account in credit by 1.79, and the desk prints 57.18 overdue the
   next day. Up to 2,067 steps sit after a credit bill on the household's pages. That count is an
   upper bound, not an attribution.
2. **One fuel's credit is netted against the other fuel's debt by the row.** The row's "owed" sums
   both fuel pages, while the desk's overdue counts unpaid bills. Example: PROS-2016-0042, Apr 2018.
   The electricity bill of 60.44 is unpaid, the gas page holds 13.35 in credit, the desk prints 60.45
   and the row reads 47.09 owed. 487 steps fit within the sum of each leg's positive balance. This
   is a definition question for the row, not two records of one fact.
3. **Pennies add up across several open bills.** For example, 3,314.70 against 3,314.65 on
   PROS-2020-0189. These steps sit above class (b)'s 2p band but come from the same per-bill
   rounding.

## Predictions (on the first fresh run carrying the fix)

- **P1.** Breaches on `OCC-` accounts fall from 2,489 to under 400. What remains is causes 1 to 3
  above, which also occur on occupier accounts.
- **P2.** Breaches on non-`OCC-` accounts stay within ±3% of 6,965. The fix touches no other leg's
  record. Other lanes' commits between c4738b64c9 and the run may move this, and the grade names
  them.
- **P3.** `world_payment_truth`'s `fallback_bills` count (`wpt.LAST_COUNTS`) falls to 0 or near it,
  from a count that includes every occupier bill.
- **P4 (figures that move).** The P&L's bad debt (`emergent_bad_debt_lines`) and debt recovery read
  the same `_resolve_bills`. Occupier accounts' write-offs and recoveries will therefore move to
  the triad's outcomes. The direction is not predicted. The grade prints `total_bad_debt` before and
  after.

## Class (a), written down and not changed here

One leaver's debt carries three write-off dates:
- the page's, at the final bill's due date, which is the engine's `WRITE_OFF_DATE_CONVENTION`;
- the company's sweep, a year later;
- the desk's journey, at the six-year bar.

`docs/market_research/debt_and_collections.md` §2.7 lists "the close-to-write-off clock (supplier
policy, said by Ofgem to differ)" as NOT established. No published date exists to give the book.
Choosing one date and making the other two read it is a design choice. It changes the engine's
declared convention, the company's sweep, and the desk's journey, so it is a change across three
records, not a lookup.

The recommendation is that the company's own write-off act is the one date. The page and the P&L
should read it, because the write-off is the supplier's accounting decision (§1, Centrica Note 17).
This goes to the delivery seat as the next item, with a knowledge-page amendment first (K8).
