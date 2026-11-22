**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 2 · **Atom:** `PB3_book_growth_as_earned_outcome` · **Claim:** `make-acquisition-see-the-price-so-the-first-term-cap-rule-can-go` (Lane 0 delivery)

# The campaign now asks for the quote before the win. The quote needs the market's price, not the cap, as its reference

**Fate (2026-10-12, clear-the-decks):** ATOM -- ACQUISITION_HELD_AT_CAP_TARIFF_TYPES still present (doc's "done means" called for its deletion); campaign-time net-new acquisition quote still does not read the company's own forward price -- only the replacement-acquisition path got quoted_unit_rate_per_mwh wired (28eb35ec7) (P2)

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

## 2026-11-22: the win-side reference is settled from the record, and the defect it rested on is fixed

The "question for research" above has been answered since 2026-10-10. The answer was never wired
on the world side. `docs/market_research/cheapest_fix_against_the_default_tariff_gb_2016_2025.md`
holds Ofgem's own RMI series ("market cheapest tariff" against the default, typical dual-fuel, at
the TDCV in force on each date). It sits in the commons as
`docs/domain_artefact_library/regulatory/gb_best_deal_gap_to_default.json`, and the company's save
desk already reads it. **A share of the default bill needs no single-fuel mapping:** Ofgem computes
it on the whole typical bill. Applying that share to each fuel's unit rate is a stated belief, not
a published split (the same GAP that `save_offer.published_default_rate_ex_vat` records for
pre-2019 per-fuel defaults).

**The defect, now fixed.** `competitor_reference.historical_discount_pct` divided a dual-fuel £
saving by 14.2 MWh and then by the electricity rate. Printed at real inputs against the published
mean:

| year | old | published | year | old | published |
|---|---|---|---|---|---|
| 2016 | 0.151 | 0.304 | 2021 | 0.000 | 0.167 (Q4 0.0) |
| 2017 | 0.091 | 0.244 | 2022 | −0.068 | 0.000 |
| 2018 | 0.086 | 0.286 | 2023 | 0.010 | 0.022 |
| 2019 | 0.075 | 0.266 | 2024 | 0.037 | 0.076 |
| 2020 | 0.049 | 0.287 | 2025 | 0.050 | 0.116 |

It now reads the commons. `best_deal_gap_share(date)` is quarterly, and `anchor_rate_gbp_per_mwh`
uses the quarter: 2021 collapses inside the year, from 24.6% in Q3 to 0.0 in Q4. 2022 reads 0.0
rather than negative, because the household's alternative to a dear fix is the default it already
has. No production path read either function, so no book moves.

**This changes the measurement table above.** At the published gap, the 2016–20 first terms (a
median of about −24% to −36% against the cap, on mixed VAT bases) sit near the market's going rate,
not far below it. That agrees with what the table's own prose concluded.

**Still owed, in order:** (1) wire `first_term_offer_fn` in `live_population._resolve_campaign`.
Strike via `request_fixed_unit_rate`, decline via `decide_acquisition(quoted_unit_rate_per_mwh=)`,
and set the prospect's `price_differential_pct` against `anchor_rate_gbp_per_mwh` on a common VAT
basis. The SSP-cache load must be priced in memory first. (2) Pre-register, delete
`ACQUISITION_HELD_AT_CAP_TARIFF_TYPES`, and run one variable in one world.

## 2026-11-22 (later): the SSP-cache load at campaign time, priced

The precondition named above, measured in a fresh process (`sim.cache_store.get_cached_prices`
over the cache's whole span, 2015-11-07 to 2025-06-07, 168,026 half-hourly records):

| load | resident after | peak during the parse | wall time |
|---|---|---|---|
| electricity SSP | +238 MB | 376 MB | 0.6 s |
| gas NBP (`load_nbp_history`, 3,538 days) | +1 MB | — | — |

**Where the cost would land.** The campaign resolves when `run_phase2b` is imported
(`CUSTOMERS = live_population(...)`, line 367). That is before `main()` loads its own price feeds
(line 1946), so in the run the campaign cannot borrow the run's list. It would make a second,
earlier load. Run sequentially and released, the run's own peak does not rise. It also falls on
every process that draws a population with the campaign live: 55 test files reach
`live_population` or `_campaign`, and under xdist each worker pays 376 MB at peak.

**What the company's forward actually reads.** `CompanyTariffEngine.get_forward_price` reads only
per-day aggregates, through `_DailyIndex`: the half-hourly count per day (the
`MIN_RECORDS_FOR_ESTIMATE` floor), and the daily mean that the EWMA, the adaptive lookback and the
regime premium each read through `_daily_means_for_window`. So a daily feed of `(date, count,
mean)` built once from the cache (about 3,500 rows) and handed to a `_DailyIndex` built from
aggregates would strike exactly the same forward without the 238 MB. That is a company-side
constructor, and its control is equality with the half-hourly path at every campaign quote date.
It is not built yet.

**Recommendation for increment 2.** Build the daily-aggregate feed first and assert it is equal to
the half-hourly forward across the real campaign dates. Then wire `first_term_offer_fn` reading that
feed. Do not load the 129 MB file at import. Wiring the quote moves the book on its own (the win
becomes price-aware while the hold is still in place), so it lands as its own baseline. The
pre-registered single variable stays the deletion of `ACQUISITION_HELD_AT_CAP_TARIFF_TYPES`
against that baseline.

## 2026-11-22 (later still): the daily-aggregate feed is built and strikes the same forward

`company.pricing.tariff_engine.DailyPriceFeed` holds one `(date, count, mean)` row per day and is
accepted wherever `get_forward_price` takes `price_records`. Its index carries the count (the
refusal floor) and the `statistics.mean` daily mean (every estimator) exactly, so the result is the
same float, not a close one. It refuses out-of-order, non-canonical or empty rows rather than
pricing them approximately.

At real inputs, weekly from 2016-01-01 to 2025-06-01, 12- and 24-month terms: **984 of 984 quotes
are bit-identical on each fuel**. Electricity uses 3,501 rows in place of 168,026 records; gas uses
3,538 rows from NBP's 3,538. The control (`test_a_daily_feed_prices_exactly_as_the_half_hourly_history_it_was_built_from`)
covers both the priced leg and the refusal leg, plus a JSON round-trip. Two mutations each turn it
red: a count off by one, and a mean scaled by 1.000001.

**Still owed:** (1) persist the feed beside the cache, built once from it, so the campaign never
loads the half-hourly file. Then wire `first_term_offer_fn` in `live_population._resolve_campaign`
as described above, landed as its own baseline. (2) Pre-register, delete
`ACQUISITION_HELD_AT_CAP_TARIFF_TYPES`, and run one variable in one world.

## 2026-11-22 (fourth increment): the daily feed is persisted beside the cache

`sim.cache_store.get_cached_daily_ssp()` returns the whole SSP cache as `(date, count, mean)` rows,
read from `sim/cache/elexon_ssp_daily.json` (gitignored with the rest of the cache). That file is
built once from `elexon_ssp_full.json` and rebuilt whenever the source's size or mtime differs. The
reduction is `sim.cache_store.daily_ssp_rows`, computed on the world side so `sim/` never imports
the company. Its control checks equality with `DailyPriceFeed.from_records` and checks both the
served leg and the rebuild leg (`tests/sim/test_cache_store.py`).

Measured at real inputs on this machine:

- The first build takes 0.85 s and produces 3,501 rows (132 KB).
- A warm read takes 2 ms and adds **2.0 MB** at peak, including wrapping it in a `DailyPriceFeed`.
  The half-hourly load added 376 MB.
- After the JSON round-trip, **984 of 984** electricity forwards (weekly from 2016-01-01 to
  2025-06-01, 12- and 24-month terms) are identical to the half-hourly path's.

**Still owed:** (1) wire `first_term_offer_fn` in `live_population._resolve_campaign`. Build it
through the growth-desk seam from `DailyPriceFeed(get_cached_daily_ssp())` and the NBP history
(about 1 MB), and land it as its own baseline. (2) Pre-register, delete
`ACQUISITION_HELD_AT_CAP_TARIFF_TYPES`, and run one variable in one world.

## 2026-11-22 (fifth increment): the campaign quotes before the win, landed as its own baseline

`live_population._resolve_campaign` now passes `first_term_offer_fn`, built from
`get_cached_daily_ssp()` and the NBP history reduced to daily rows. The company's act sits behind one
door, `growth_desk.quote_first_term` → `renewal_desk.quote_first_term`: the forward over the daily
feed, the base strike (`strike_fixed_unit_rate`), and the one no-offer rule
(`should_attempt_acquisition`). The world reads the prospect's position as the strike against
`market_cheapest_ex_vat`: the default charged (net of the EPG) × (1 − the quarter's published gap)
÷ 1.05. The design choices are on the knowledge page,
`docs/market_research/cheapest_fix_against_the_default_tariff_gb_2016_2025.md` §7.

At the run's seed the campaign goes from 3,250 quotes and 210 wins to 3,066 quotes and 230 wins,
with 235 quotes withheld (150 in 2021, 70 in 2022). Of 3,301 offers asked, 951 are default-tariff
prospects and read no position: GAP, the funnel stays at the run level for them. With no SSP cache
there is no quote, and the campaign record says so (`first_term_quote`).

**Surprise, not attributed.** 2023–24 strikes sit 20–28% below Ofgem's cheapest deal, which is
implausible for a real market. Either the company's spot-EWMA forward underprices, or the per-fuel
gap is wrong for electricity in those years. I cannot yet say which. That has to be settled before
the hold comes off, because removing the hold would let those strikes through.

**Still owed:** (1) attribute the 2023–24 position (above). (2) Pre-register, delete
`ACQUISITION_HELD_AT_CAP_TARIFF_TYPES`, and run one variable in one world against this baseline.
