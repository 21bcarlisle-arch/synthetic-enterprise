**Severity:** LATENT · **Lane:** C_customer_ops · **Epoch:** 2 · **Atom:** `EP4_collections_journey`

# A dual-fuel household is one account everywhere the run bills, moves and switches it, and two accounts in collections

Found while taking B13 to L1 (seat, 25 Oct). Measured on one phase 4c run to 2017-12-31 with moves
and move-with-us on: 354 dual households. The control is
`tests/simulation/test_a_dual_fuel_household_is_one_account_across_both_fuels.py`, and each of its
controls was checked against a data mutation of that run's output.

**What holds.** Every leg carries its household's billing account. Both fuels are billed for one
period each month. The two exceptions are SYN-2016-296 and SYN-2016-345, whose gas legs end at a move
to a home with no gas (home_moves.md s.8.7). A household moves out on one date (28 dual move-outs) and
switches away on one date, taking every leg it holds (65 households). The 95 mid-life credits on dual
legs (89 gas, 6 electricity) each come off their own fuel's next paid bill (dac6b90d7). All 7 leg
credits at close are refunded on their own fuel, so the account's balance is the sum of its two
legs (SLC 27.16).

**Direct debit, not a defect of this kind.** 11 households pay their electricity on prepayment or
standard credit beside a gas direct debit, in 144 household-months. All 11 fall in the band
`0.72 <= U < 0.75` between the fuels' published DD shares (`simulation/household_segments.
payment_channel_for_customer`). That band is the design's stated coupling: the true joint is not
published. The control asserts the band is the only route. Whether a real dual-fuel account ever
pays one fuel by DD and the other on receipt is a practitioner question (K4).

**Split 1: collections runs one journey per fuel leg.** The payment triad posts to `ACC-<supply
point>`, so `collections_journeys` holds `ACC-C1` and `ACC-C1g` apart. 189 of 354 dual households
have journeys on both legs, and 80 of them have two open at once: two reminder ladders, two
statements of account, two exits for one household. The same per-leg key reaches the site: the
reaction chain reads `ACC-<cid>` per customer file, and 413 of 964 files in `site/data/customers/`
are gas legs published as customers of their own. No published total was found reading these
journeys as households, so this is LATENT, not BLOCKING. **Proposal:** key the triad's account by
`household_of(point)` and keep the per-fuel contract inside it (the balance walk already nets per
fuel). Then measure how many journeys merge before ruling. The control is a non-strict `xfail`:
`test_collections_runs_one_journey_per_household`.

**Split 2: a switch names a gas leg the household stopped taking a year earlier.** SYN-2016-296
moved with us on 2016-09-09 to a home with no gas, so its gas term ended that day. When it switched
away on 2017-10-01, `leg_departures` listed `SYN-2016-296g` as churned on that date too. That is 1
leg in this window. The departure takes its points from the household's registered points, not
from the points supplied on the day. A switch count that reads `leg_departures` per fuel counts
one gas loss that never happened. Control: `test_no_leg_switches_away_after_its_supply_ended`
(non-strict `xfail`).

**Not measured.** From 22 Jan 2021 the DD book offsets one fuel's credit against the other's debt
at the final bill (SLC 27.8D, `dd_balance_book.dual_fuel_offsets`). The balance walk and the refund
log net per fuel only. No dual leaver in this window closed with a credit on one fuel and a debt
on the other, and the window predates the right. Whether the refund log pays out a credit that the
DD book has already set off is open. It needs a post-2021 window.

## Split 1 fix: pre-registration (written 2026-10-25, before either run below finished)

**Change.** The triad's ledger account is `ACC-<household_of(point)>`. Bills, invoice refs,
correlation ids and DD remittances stay per leg (`<point>::<period>`), so each fuel's bill is
still its own item inside the account. A household's journey is walked only as far as every leg
that can still post a bill has posted (terms post whole, electricity before gas, so walking on the
electricity leg alone would step past gas bills not yet on the ledger).

**Prediction at 2017-12-31, same run as the control (moves and move-with-us on).**
1. No journey is keyed to a gas leg of a dual household (189 -> 0). This is the definition, not a
   test of it.
2. Journeys on dual households fall by at least 80 (the households with two open at once each lose
   at least one) and by no more than the number of gas-leg journeys before the change.
3. Journeys on single-fuel households move by under 5%: they change only second-hand, through the
   book-wide default belief that renewal prices read.
4. Push payments now clear oldest-first across both fuels, so a few journeys open later or cure
   sooner than either leg's did. I cannot size this in advance.

## Split 1 fix: the result (same day, after the runs)

Baseline (origin/main b0e5b0d80) and change, the same run twice each; the baseline reproduced
exactly (1,465 journeys both times).

| | before | after |
|---|---|---|
| journeys, all | 1,465 | 1,462 |
| accounts with a journey | 559 | 370 |
| gas-leg accounts with a journey | 241 | 0 |
| dual households with journeys on both legs | 189 | 0 |
| journeys on dual households | 1,226 | 1,223 |
| journeys on single-fuel households | 239 | 239 |
| stages entered | 6,699 | 6,353 |
| journeys still open at 2017-12-31 | 125 | 109 |

1. **Held.** 189 -> 0.
2. **Refuted.** Journeys on dual households fell by 3, not by 80 or more. On the 189 households
   with both legs in collections, 1,013 journeys became 970. Merging the overlaps alone would have
   left 862. The difference is the cause I could not size in point 4. Under the balance-based,
   oldest-first allocation that `account_hierarchy_payment_allocation.md` s.1 anchors, one fuel's
   payment clears the other fuel's older overdue bill. A household paying a month late then clears
   everything overdue on each due date and is overdue again the next day. What was one long gas
   journey climbing the ladder (SYN-2016-517: 15 stages, May to October 2017) becomes a monthly cure
   and reopen. The 12 dual households whose journeys were all on the gas leg gain 25 journeys, and
   5 others gain 15.
3. **Held.** Single-fuel households are unchanged: 239 journeys before and after.

**Open, for a practitioner (K4).** Take a household that is always one bill behind but clears its
overdue balance on each due date. It is reminded every month and never escalated. Under FIFO
ageing its debt is never more than a month old, so the model is consistent with its anchor. Would
a real desk instead escalate on a balance that never clears? The same pattern was already on
single-fuel ledgers before this change (SYN-2016-449). It is the desk's cure rule, not the merge.

**Still per leg.** The site's reaction chain reads `ACC-<file id>` per customer file. A gas leg's
file now finds no journey, and the household's journey is on its electricity file. The 413 gas-leg
files are still published as customers of their own. That is the chain's own split and is not
changed here.
