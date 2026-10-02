**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `PB3_book_growth_as_earned_outcome` · **Claim:** `make-acquisition-see-the-price-so-the-first-term-cap-rule-can-go` (Lane 0 delivery)

# The campaign now asks for the quote before the win. The quote needs the market's price, not the cap, as its reference

Follow-on 1 of `SEAT_FINDING_A_CHOSEN_FIXED_RENEWAL_IS_OUTSIDE_THE_CAP_AND_A_FIRST_TERM_IS_HELD_BY_THE_ACQUISITION_RULE_2026-10-02.md`.
This item is bigger than one turn. This note records what landed, what "done" means, and the
measurement that decides the next step.

## What done means

`ACQUISITION_HELD_AT_CAP_TARIFF_TYPES` is deleted, and nothing in the world or the company holds a
first term at the cap. In its place there are three things:

1. **The quote comes before the win.** The company's first-term rate is struck when the prospect is
   quoted, not after the funnel has already decided they won.
2. **The world responds to price.** The funnel's quote-to-application stage reads this prospect's
   own position, not the run-level `PRICE_DIFFERENTIAL_PCT = 0.0`.
3. **The company can decline to quote.** It goes through **one** no-offer rule for both acquisition
   routes. That rule is `saas.growth_mandate.should_attempt_acquisition` behind
   `company/interfaces/growth_desk.decide_acquisition`, which the replacement path already uses. It
   is not a second implementation.

Graded by one variable in one world (the hold removed, with legs 1–3 in place), against a
pre-registration written before the run.

## Landed this turn: leg 1's mechanism

`net_new_acquisition.plan_growth_campaign(first_term_offer_fn=...)` (default `None`, which leaves
production unchanged):

- **Declined.** The company issues no quote and spends nothing. The home stays in the remainder and
  is recorded in `quotes_withheld` with the company's reason.
- **Quoted.** The funnel decides the prospect at its own `price_differential_pct`.
- **The quote book.** `quotes_issued` excludes withheld quotes, so the company's planner never reads
  a quote it withheld as one the market turned down.

One partition control covers withheld, quoted-and-won and quoted-and-lost. A second control checks
that each prospect's own position reaches the funnel, and that with no offer function the funnel is
called exactly as before.

**No production caller yet, and that is the gap.** Producing the quote at campaign time needs the
company's forward, and that is struck from the 129 MB SSP cache (`sim/cache_store`). The campaign
resolves when the population is drawn, so loading the cache there would put it into every test
process that draws a population. Wiring it is the next increment, not something to do quietly.

## The measurement that decides the reference

From the flat run at `db2184ec9` (`/var/tmp/se-fixed-cap/flat_base.json`), domestic fixed first
terms, struck rate ex-VAT against the published cap inc-VAT (`svt_rates.get_svt_elec_rate_gbp_per_mwh`
/ gas):

| year | n | median d vs cap | above cap | mean `offer_position_multiplier` if cap were the reference |
|---|---|---|---|---|
| 2016 | 76 | −0.24 | 0 | 3.84 |
| 2019 | 19 | −0.31 | 0 | 3.89 |
| 2020 | 17 | −0.36 | 0 | 4.23 |
| 2021 | 21 | +0.06 | 12 | 1.14 |
| 2022 | 3 | +2.00 | 3 | 0.23 |
| 2023 | 14 | −0.39 | 0 | 4.40 |
| 2024 | 23 | −0.13 | 0 | 2.56 |

(The VAT bases differ in this table: that is how the table was read, and it is corrected below.)

**The cap cannot be the win-side reference.** Against the cap, a typical 2016–20 offer saturates
the curve: quote-to-application goes from 0.24 to about 0.92. That would grow the book on a
comparison no prospect makes. A household shopping for a fix compares against the fixes on offer,
which in 2016 were about £300 a year below the default (`MARKET_SAVINGS_BY_YEAR`).

The loss side is right to use the cap: `market_switching_multiplier` carries the level there
(`competitor_reference.py`, "WHY THE CAP IS THE NO-OP POINT"). The win side has no level carrier,
because `QUOTE_TO_APPLICATION` is flat over the years. So the win side's parity point should be the
market's going rate. Measured as a saving in pounds, that is our saving against the default minus
the market's saving, at the household's own bill.

The knowledge layer already supports this direction. Per
`docs/market_research/svt_rates_active_passive_2016_2025.md:120,134`, the cap sat £200–350 above
the cheapest fix, and in 2016–18 an SVT of about 14p/kWh faced fixes of about 10–11p. On a common
VAT basis our 2016 first terms sit about 20% below the cap, which is level with the market's fixes
rather than far below them.

**What is still open is a question for research, not a value to pick.** How the dual-fuel `MARKET_SAVINGS_BY_YEAR`
maps onto a single-fuel or non-typical household is not established. Note also that
`competitor_reference.historical_discount_pct` divides a dual-fuel £ saving by an
**electricity** unit rate, which may understate the fraction. That module keeps the result off its
reference path, so nothing has been resting on it yet. Settle both before increment 2 reads either.

## Next, in order

1. Widen `should_attempt_acquisition` from "cap < wholesale forward, electricity only" to the struck
   rate against the published default, on both fuels and with the VAT basis stated. PROS-2022-0063g
   was gas, and the current gate always lets gas proceed. One rule, both routes.
2. Settle the win-side reference (above), then wire `first_term_offer_fn` in
   `live_population._resolve_campaign` with the SSP load priced in memory.
3. Pre-register, delete the hold, and run one variable in one world.

## What the landing had to clear first (its own commit, before this one)

Any change to `net_new_acquisition.py` selects its test file, and that file held three reds at
HEAD. Neither cause was this item's, but both had to be fixed before anything here could land:

- **The registry EAC broke every truncated run.** Since `3bf64c4e7`,
  `registry_eac_from_own_reads` refuses a trace shorter than a year. That refusal is right and has
  its own test, but a `report_end="2016-06-30"` run died at import. The fix is at the caller:
  `run_phase2b` keeps the drawn band and logs it when the window holds under a year of reads. A full
  run never reaches that branch.
- **The settlement ceiling outran memory.** The journal leg re-priced the ceiling on a 6,451.2 MB
  `sim-runner.service` peak and got 1,094.9 customer-years, against a shipped 1,250. Moved downward
  to 1,050, and the book-growth page's sentence was corrected in the same commit. **This rescales
  every book from that commit on** (the settlement sample shrinks by about 16%), so a comparison
  made across it is not one variable. The curve was not re-measured.
