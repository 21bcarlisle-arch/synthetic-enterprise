# The published forward has an as-of axis and no delivery axis

**Knowledge:** hedging-forward-market

*Worker tick, 2026-10-07, for `G15_forward_curve_series_to_backtest_hedging_by_physics` (L0).
Asset and provenance: `docs/data-sources/ofgem-forward-weekly.md`.*

## What was found

The map row's own note says what makes this hard: a forward price is a price for a delivery
period as of a trade date, so a usable series must carry both dates. The one free, published,
dated GB forward series is Ofgem's weekly forward-delivery average (electricity £/MWh, gas
p/therm, 2021-02 onward, volume-weighted broker trades in the price cap's reference quarterly
contracts). It carries the **as-of** date exactly — a row is the Monday-to-Friday trades of its
week. It does **not** carry the delivery period: each row averages several quarterly contracts and
the basket at each week is not published beside it. ICE settlement curves would carry both and
are paywalled.

So the series is a dated forward LEVEL, good for checking the world's forward level week by week
from 2021, and not yet good for G15's purpose — backtesting a hedge SHAPE — until the basket at
each week is established from the price cap methodology
(https://www.ofgem.gov.uk/decision/default-tariff-cap-decision-overview).

## The world's synthetic forward against it

`sim/forward_curve.generate_forward_price` (spot EWMA × seasonal shape × term premium, 12-month
delivery from the as-of date) was evaluated as of the Monday after each published week, against
the cached Elexon SSP (`sim/cache/elexon_ssp_full.json`) and NBP (`sim/gas_data/nbp_sap.csv`);
gas converted at 10/29.3071 £/MWh per p/therm. 225 weeks to 2025-06. Ratio = synthetic / published.

| Fuel | Year | Weeks | Published mean | Synthetic mean | Median ratio | Range |
|---|---|---|---|---|---|---|
| Electricity | 2021 | 48 | 89.5 | 111.9 | 1.18 | 0.93–1.65 |
| | 2022 | 52 | 273.7 | 211.4 | 0.81 | 0.51–1.36 |
| | 2023 | 52 | 127.5 | 110.5 | 0.84 | 0.64–1.13 |
| | 2024 | 53 | 79.7 | 74.3 | 0.95 | 0.70–1.20 |
| | 2025 | 20 | 86.9 | 100.4 | 1.17 | 0.95–1.29 |
| Gas (£/MWh) | 2021 | 48 | 29.0 | 41.0 | 1.14 | 0.95–2.11 |
| | 2022 | 52 | 102.7 | 105.5 | 1.10 | 0.72–1.61 |
| | 2023 | 52 | 44.7 | 40.2 | 0.86 | 0.61–1.29 |
| | 2024 | 53 | 31.3 | 30.3 | 0.97 | 0.79–1.22 |
| | 2025 | 20 | 34.6 | 38.3 | 1.12 | 0.94–1.32 |

Over all weeks the median ratio is 1.00 (electricity) and 1.04 (gas), but only 44% and 56% of
weeks fall within ±15%. The extremes sit where the market was most backwardated or contangoed:
electricity 0.51 on 2022-11-14 (published 298.5, synthetic 153.4), 1.65 on 2021-09-06; gas 2.11 on
2021-11-08, 0.61 on 2023-08-21.

**What the two numbers count, before the ratio is read.** The synthetic figure is a 12-month
strip starting at the as-of date. The published figure is the average over the cap's reference
quarters, whose distance from the as-of date is not stated. In a flat curve the two agree whatever
the basket; in 2021–2022 the curve was steeply backwardated (the October 2021 rows are £113–119/MWh
electricity and 105–115 p/therm gas, against an October mean SSP of £158.5/MWh and NBP SAP of 233 p/therm in
the world's own cached record), so the ratio there mixes the
model's error with the tenor gap. **I cannot yet say how much of the 0.51–2.11 band is the
model.** The one-variable version is to re-run the synthetic at the basket's own delivery quarters
once the basket is established; prediction filed now: the 2021 over-pricing (synthetic built from
crisis spot, published reaching further out) shrinks most, and the 2022-H2 under-pricing
(synthetic EWMA lagging a forward that ran ahead of spot) survives.

## What this changes

- The world's forward has never been checked against a traded forward; now it can be, from 2021.
- G15 is not at a backtestable series yet. The missing step is the delivery axis: establish the
  cap's reference-contract basket by week (published methodology), then this series becomes a
  dated, delivery-identified forward level for 2021–2025. 2016–2020 stays uncovered by any free
  source found.
