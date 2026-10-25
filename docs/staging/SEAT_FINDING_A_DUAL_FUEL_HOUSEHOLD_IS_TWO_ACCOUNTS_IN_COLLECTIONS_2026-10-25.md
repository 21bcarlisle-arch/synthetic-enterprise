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
