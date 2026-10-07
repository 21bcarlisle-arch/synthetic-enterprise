# Ofgem weekly forward delivery prices (GB electricity and gas)

The first published, dated forward-price series this project holds. Registered 2026-10-07 for
`G15_forward_curve_series_to_backtest_hedging_by_physics` (the use-case register ruling of
2026-09-06, section 3.2: "register both as data assets with provenance; no product build").

| | |
|---|---|
| Publisher | Ofgem, Wholesale Market Indicators — "Electricity prices: forward delivery contracts - weekly average (Great Britain)" and "Gas prices: forward delivery contracts - weekly average (Great Britain)" |
| Page | https://www.ofgem.gov.uk/news-and-insight/data/data-portal/wholesale-market-indicators |
| Data | the CSV embedded in each chart: `https://app.everviz.com/inject/0eDBSsofl/` (electricity), `https://app.everviz.com/inject/xQHwOz4nR/` (gas) — the `"csv"` field |
| Underlying | "Ofgem analysis of broker data"; the chart was marked "Information correct as of August 2026" |
| Pulled | 2026-10-07, 283 weekly rows each, 2021-02-01 to 2026-06-29 |
| Stored | `sim/data/ofgem_forward_weekly_electricity.csv` (£/MWh), `sim/data/ofgem_forward_weekly_gas.csv` (p/therm), dates rewritten to ISO, values untouched |

## What one row is (Ofgem's own methodology text)

- "the weekly price of specific quarterly forward contracts, averaged by volume"; "these are the
  reference contracts used in the price cap methodology".
- "All transactions for each contract type, for each week, are averaged on a volume-weighted basis.
  These are then averaged to arrive at a single data point for each week."
- "Where a particular contract is not traded within a given week, it is excluded from the data
  point average."
- "the 26 April 2021 data point covers all transactions for the week of Monday 26 April 2021 to
  Friday 30 April 2021 inclusive." So a row is KNOWABLE from the Friday of its week; read it no
  earlier than the following Monday.
- "updated monthly"; the cap's own wholesale assessment uses a different, third-party price
  reporting agency feed, so this is NOT the cap's index, only the same contracts.

## What it is not

**It has an as-of axis and no delivery axis.** Each row averages several quarterly contracts, and
which quarters are in the basket at each week is not published beside the row. It is a forward
LEVEL index, not a curve: it cannot price a specific delivery period and so cannot, on its own,
backtest a hedge shape. It starts 2021-02, so 2016–2020 is not covered. ICE settlement curves,
which would be the full bitemporal record, are paywalled (`gas-nbp.md`: "Do NOT use: ICE").

Finding and first comparison against the world's synthetic forward:
`docs/market_research/the_published_forward_has_an_as_of_axis_and_no_delivery_axis_2026-10-07.md`.
