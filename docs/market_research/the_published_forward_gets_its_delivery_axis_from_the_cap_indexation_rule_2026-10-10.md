# The published forward gets its delivery axis from the cap's indexation rule

**Knowledge:** hedging-forward-market

*Worker tick, 2026-10-10, for `G15_forward_curve_series_to_backtest_hedging_by_physics` (L0). Follows
`the_published_forward_has_an_as_of_axis_and_no_delivery_axis_2026-10-07.md`, whose named next step
this is. Asset: `docs/data-sources/ofgem-forward-weekly.md`.*

## The rule

Ofgem describes the weekly series as "the reference contracts used in the price cap methodology".
The methodology says which contracts those are at each date. Ofgem, *Price cap – Final guidance on
treatment of price indexation in future default tariff cap periods* (August 2022,
https://www.ofgem.gov.uk/sites/default/files/2022-08/Price%20cap%20-%20Final%20guidance%20on%20treatment%20of%20price%20indexation%20in%20future%20default%20tariff%20cap%20periods1659530941267.pdf),
footnote 6:

> "We express the price cap formula in an index with the format X-Y-Z [A], where X is the price
> observation period, Y is the notice period between the end of the observation period and the
> start of the price cap period starting, Z is the forward view period and A is the period for
> which the cap is in place, all in months. So, a 3-1.5-12 [3] index for delivery starting
> 1 October 2022 means a three-month observation period running from mid-May to mid-August where
> 12-month forward prices are observed."

So at any trade week the basket is **the 12 months of delivery starting on the first day of the cap
period whose observation window contains that week.** The windows, by source:

| Trade weeks | Index | Delivery observed | Source |
|---|---|---|---|
| 1 Feb – 31 Jul (2021) | 6-2-12 [6] | 12 months from 1 Oct | the formula; the guidance's table starts the Oct-2022 window 01/02/2022 |
| 1 Aug 2021 – 31 Jan 2022 | 6-2-12 [6] | 12 months from 1 Apr 2022 | the formula |
| 01/02/2022 – 01/06/2022 | 6-2-12 → 7-1-12 | "Winter 2022" | the guidance's table, verbatim |
| 06/06/2022 – 18/08/2022 | 3-1.5-12 [3] | "Q4 2022" | table |
| 19/08/2022 – 16/11/2022 | 3-1.5-12 [3] | "Q1 2023" | table |
| 17/11/2022 – 17/02/2023 | 3-1.5-12 [3] | "Q2 2023" | table |
| 20/02/2023 – 18/05/2023 | 3-1.5-12 [3] | "Q3 2023" | table |
| from 19/05/2023 | 3-1.5-12 [3] | 12 months from each quarter start | the formula; window end taken as 44 days before the cap starts, which reproduces the table's mid-month ends to within four days |

**Two things this does not settle, stated rather than resolved.** The table names the transitional
product as "Winter 2022", a six-month season, where the formula says 12 months; the delivery START
(1 October 2022) is the same either way, and the start is all that is used below. And the enduring
window ends are an approximation (±4 days), so a published week that a boundary falls inside is
assigned to no basket rather than guessed: 9 of 283 weeks per fuel (2022-01-31, 2022-08-15,
2022-11-14, 2023-05-15, 2024-11-18, 2025-08-18, 2025-11-17, 2026-02-16, 2026-05-18).

## What it gives

274 of 283 weeks per fuel now carry a delivery start. The lead from trade week to delivery start is
**47 to 242 days, median 101.5** — the published figure is never a forward from today, which is
what the world's synthetic forward is.

## The 2026-10-07 prediction is refuted by construction, not by the world

That note filed: re-run the synthetic at the basket's own delivery start and "the 2021
over-pricing shrinks most". It cannot shrink. `sim/forward_curve.generate_forward_price` is spot
EWMA × the MEAN of twelve monthly seasonal multipliers × a tenor premium; a 12-month mean over a
12-month cycle is the same whatever month it starts in. Printed over all 274 assigned weeks, the
seasonal term at the as-of month and at the delivery-start month differ by **0.0** on both fuels.
And the function cannot take a delivery start later than its as-of date at all: its one date is
both, so passing the cap start would read spot the trader could not yet see.

So the 0.51–2.11 band in the earlier note is **wholly the model's**. The tenor gap is real — 47 to
242 days — but the world's forward has no axis on which it could show up. What the model lacks is
a term structure in delivery distance: in 2021 the market priced reversion that a spot EWMA cannot,
and in 2022-H2 it priced persistence ahead of spot.

## The first backtest the delivery axis allows: the published forward against what was delivered

With the delivery year known, each published week can be held against the mean of the world's own
spot over that delivery year (Elexon SSP daily means; NBP SAP, at 10/29.3071 £/MWh per p/therm).
Weeks whose delivery year the cache covers on ≥330 days only, which ends at trade week 2024-05-13.

| Fuel | Trade year | Weeks | Published forward | Realised over its delivery year | Median ratio | Range |
|---|---|---|---|---|---|---|
| Electricity | 2021 | 48 | 89.5 | 194.8 | 0.40 | 0.26–1.31 |
| | 2022 | 49 | 272.5 | 112.3 | 2.20 | 0.87–5.41 |
| | 2023 | 51 | 127.5 | 73.2 | 1.76 | 1.04–2.50 |
| | 2024 | 20 | 72.7 | 82.4 | 0.89 | 0.74–1.01 |
| Gas (£/MWh) | 2021 | 48 | 29.0 | 96.8 | 0.26 | 0.15–1.02 |
| | 2022 | 49 | 102.2 | 43.9 | 2.40 | 0.60–5.90 |
| | 2023 | 51 | 44.8 | 29.1 | 1.55 | 0.93–2.27 |
| | 2024 | 20 | 27.1 | 33.6 | 0.81 | 0.70–0.89 |

**What each number counts, before the ratio is read.** The published figure is a volume-weighted
broker price for baseload quarterly contracts. The realised figure is the imbalance price (SSP),
not a day-ahead baseload index, and is unweighted by any demand shape. So the ratio is the
forward's ex-post error plus the SSP-vs-traded-spot basis; it is not a supplier's hedge P&L, which
would need the demand shape and the hedge ladder. Over the 168 weeks, the published forward's
median ratio to realised is 1.49 (electricity) and 1.41 (gas); the world's synthetic forward's,
over the same weeks, is 1.17 and 1.04. That the synthetic sits closer to realised is no evidence
it is the better forward: it is built from spot, and the thing a hedge buys is the market's price,
not the outcome.

## What this changes

- The weekly series is now bitemporal for 2021-02 to 2026-06 at the resolution of a delivery
  START (not a full curve): a dated forward level for an identified 12-month delivery period.
  That is enough to ask "what did hedging at the market forward cost against floating, by
  delivery year" — the G15 question — once a demand shape is applied.
- **The series itself (2026-11-14):** `ofgem_forward_weekly_with_delivery_start_2021_2026.json`, one row
  per fuel per trade week, with `delivery_start`, `lead_days` and the window's source, and the nine
  boundary weeks carried as unassigned with their reason. Re-built from the CSVs by this page's rule,
  it reproduces the figures above exactly (274 of 283, lead 47-242 days, median 101.5).
- The world's forward cannot be graded against it on shape until it has a delivery-distance axis;
  a re-run that moves only the delivery start is a no-op today. Any change there is a world
  (fidelity) change, owned by `sim/`, and is not made here.
- 2016–2020 stays uncovered by any free dated forward source found.
