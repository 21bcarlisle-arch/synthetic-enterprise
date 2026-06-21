# Phase 13d: Seasonal Forward Price Awareness in Company Tariff Engine

## Context

Phase 11a gave the company its own tariff engine (120-day rolling mean + 15% premium).
The key limitation: no seasonal weighting. In the UK energy market, forward prices for
winter delivery are systematically higher than the 120-day rolling mean of spot prices
(which includes summer lows). This causes the company to underprice winter contracts,
contributing to the negative net margin visible in the crisis years.

Phase 13c fixed the churn model. Phase 13d should improve the tariff engine.

## What to build

`company/pricing/tariff_engine.py`: Add an optional seasonal weight to the rolling mean:

- If the delivery month is in Oct-Mar (winter delivery): apply +10% uplift to the base estimate
- If the delivery month is in Apr-Sep (summer delivery): apply -5% reduction
- Controlled by `SEASONAL_UPLIFT_ENABLED = True` and parameters
  `WINTER_UPLIFT = 0.10` / `SUMMER_DISCOUNT = 0.05`
- The company observes this pattern from historical pricing — it's in public data

## Why this matters

The 120-day lookback window for a September contract start includes June, July, August
prices (low season). This underestimates the cost of the Dec-Mar delivery. The company
systematically quotes too cheap for autumn/winter renewals, which is where margins collapse.

In the run data: 2021 net margin = -£3,069, 2022 = -£5,582. Part of this is genuine
market adversity (no model fixes that), but part is the company quoting at rolling-mean
prices in August 2021 for a September renewal, then buying at November 2021 prices.

## What we expect to see

- Company divergence tables: tariff error in 2021-2022 should decrease
- Retention ROI: more offers at sensible rates (not underpriced)
- Risk committee: possibly fewer interventions (hedging decisions improve when company prices more accurately)
- Net margin: modest improvement in normal years; crisis years still negative (genuine adversity)

## Ordering

This is opt-out: Claude should proceed after the current sim run completes.
If Rich has a different priority, stage it in docs/staging/.
