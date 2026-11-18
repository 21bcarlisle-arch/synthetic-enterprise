**Severity:** RECORDED · **Lane:** W3_industry_systems · **Epoch:** unassigned · **Atom:** `unminted`
**Knowledge:** suppliers-accounts-and-capital -- `docs/market_research/why_gb_suppliers_failed_or_survived_2021_22.md`

# Result, second test: the 2021-22 cash-hole ranking with the world's own weather on gas volume (2026-11-18)

*Delivery seat, claim `world-ranks-2021-22-reregister-and-test-the-non-price-world`. Pre-registration, unchanged:
`SEAT_PREREG_THE_2021_22_CASH_HOLE_RANKING_UNDER_THE_WORLDS_OWN_WEATHER_2026-11-18.md`. Instrument:
`tools/strategy_cash_hole_2021_22.py` (default mode; `--first-test` reruns the first test). Full output:
`SEAT_RESULT_CASH_HOLE_UNDER_THE_WORLDS_WEATHER_2021_22_2026-11-18.json` beside this file. At normal weather the
instrument reproduces every series of the first test's record exactly, and a control holds that.*

## Headline

**The re-registered test PASSES.** Under the primary (anomaly) weather and the static reading, S5's hole is £0 at both
fixed shares: its cash never goes below zero. The smallest hole in S1–S4 is £236.12 (S4 at fixed share 0.75). F grid
points £25 to £225 rescue S5 and none of S1–S4. There are no inversions. The rolling reading and the level-weather
sensitivity also pass (bands £0 to £238 and £0 to £168).

**But weather cannot discriminate between the strategies in this instrument, and that is the finding that matters.**
The 2021-22 weather moves every strategy's hole by almost the same amount, about +£48 per customer: +£29 to +£30 on
the wholesale leg and +£19 on the credit drawdown. This is structural rather than a fact about 2021-22. Cover is sized
on planned volume, so in *every* strategy the marginal unit of weather volume is bought or sold at spot and earns the
same revenue rate. The hedge decides the price of the planned volume, not of the surprise. **A monthly instrument
therefore cannot show weather separating a well-hedged book from a badly hedged one.** The mechanism that could do so
is shape: cold days that coincide with price spikes. It needs daily gas price and daily volume, and the world's gas
price here is a monthly proxy.

## The weather the world had (gas, typical customer, 12,000 kWh benchmark)

| | Apr-21 | May-21 | Sep-21 | Oct-21 | Nov-21 | Dec-21 | Jan-22 | Feb-22 | Mar-22 |
|---|---|---|---|---|---|---|---|---|---|
| HDD, 1991-2020 normal | 200 | 118 | 38 | 140 | 249 | 341 | 350 | 315 | 275 |
| HDD, world anomaly basis (primary) | 281 | 206 | 18 | 119 | 251 | 327 | 342 | 282 | 255 |
| HDD, world level (sensitivity) | 261 | 156 | 20 | 103 | 236 | 280 | 324 | 240 | 232 |

Oct-21 to Mar-22 gas volume: 8.585 MWh at normal weather, 8.199 MWh on the anomaly basis (−4.5%) and 7.545 MWh at the
store's level (−12.1%). April and May 2021 were cold, before the window. The first only moves the opening balance,
which cancels out of H.

## The holes (static, £ per opening customer, credit level £65)

| Strategy | fixed 0.5: normal → anomaly | fixed 0.75: normal → anomaly |
|---|---|---|
| S1 unhedged | −1,004.80 → −956.05 | −986.42 → −938.25 |
| S2 20%/15% | −829.33 → −780.58 | −818.07 → −769.89 |
| S3 PFP · Together | −475.52 · −436.73 → −426.77 · −387.98 | −351.53 · −293.34 → −303.36 · −245.17 |
| S4 Pure Planet | −504.80 → −456.05 | −284.29 → −236.12 |
| S5 cap 6-2-12 | −26.58 → **0.00** | −45.18 → **0.00** |

S5's wholesale leg rises from +£19–37 to +£48–67. Its credit drawdown falls from −£63.78 to −£44.69: the direct debit
is set on a normal winter, the winter was mild, and balances drained less. Together these net to above zero in every
month.

## Prediction beside outcome (§4 of the pre-registration)

| Predicted (before the run) | Outcome |
|---|---|
| 1. Oct–Mar gas within ±10% of normal, most likely 3–8% below | **Right:** −4.5% on the anomaly basis. (The level sensitivity gives −12.1%, outside the band, but it carries the store's warm urban level, which is why it is not primary) |
| 2. A mild winter: every hole shrinks, none deepens | **Right** |
| 3. No H moves by more than 10% of its first-test value | **Wrong** for S3 and S4 at 0.75 (−16%, −17%) and for S5 (−100%). I pictured the shift as proportional to the hole. It is a near-constant £48 per customer, so it is large against small holes |
| 4. Verdict passes; S4 stays shallower than Together-S3 at 0.75 | **Right** (−236.12 against −245.17) |
| 5. Refutation (colder than normal) | Did not arise: the window was milder than normal on every basis |

## A defect I made and caught, recorded beside the claim

The first cut of the weather reader parsed `sim/weather_world/daily.csv.gz` raw. That file holds each regime's daily
*anomaly*, and the cell's level is added back only by `WeatherWorld.for_cell`. The raw read gave 262 HDD in July 2021
and a "passes: false" level sensitivity. No number from that cut is in this result. The reader now goes through
`for_cell`, and `test_the_worlds_weather_is_read_with_each_cells_level_added_back` holds the property: every July is
under 40 HDD and every January is over 200. Two controls added for the second test were mutation-checked. When the
direct debit was re-set on actual weather, the first version of the DD control **did not fire**: that was a missing
test, not an equivalence. It was rewritten to hold the monthly balance step equal to the bill difference, and both
mutations (DD on actual; weather leaking into electricity) now fire.

## What this does and does not establish (F11)

It establishes that the real 2021-22 weather does not overturn the price-driven ranking. That is weak support,
because by construction weather enters every strategy almost identically at monthly resolution. It does **not** test:

- **shape risk** (daily cold against daily spot), the mechanism behind Together's "demand uncertainties". **GAP:**
  the world's gas spot is a monthly proxy;
- **leavers within the year and SoLR inflow** (still GAPs);
- **a cold winter at a high spot**, which this window did not have.

The next run that could make the world press back is shape: daily gas volume from the store against a daily gas price.
It waits on a daily GB gas price in the world.
