**Severity:** LATENT · **Lane:** W1_market_weather · **Epoch:** 4 · **Atom:** `EP16_anchored_generators`

# The world's NBP is a monthly TTF proxy, so EP16 cannot fit daily gas volatility

*Delivery seat, 2026-10-25. Third of the three dated-rule fixes drawn from
`SEAT_FINDING_THE_WORLD_READS_STATIC_ASSET_FIGURES_WHERE_THE_25_OCT_PACKS_GIVE_DISTRIBUTIONS_AND_DATED_RULES_2026-10-25.md`.
Measured. The other two (dated VAT and dated TDCV) landed in code alongside this finding.*

## What the world has

`sim/gas_data/nbp_sap.csv`, read by `sim.gas_prices_history.load_nbp_history`, is FRED
`PNGASEUUSDM`. That series is the IMF Dutch TTF price in USD/MMBtu, monthly. The world spreads each
month's value over every day of that month, and converts at a fixed 1.28 $/£. Over 2015-10-01 to
2025-06-07 there are 3,538 days, and the value changes on 116 of them, the month boundaries.
Measured on 25 Oct.

*Correction, kept beside the claim: my first count said 3,537 changes. I had taken the first
non-`date` column, which here is `settlementDate`, so I was counting dates. With
`systemSellPrice` the count is 116.*

## Why it blocks the volatility steer

`DIRECTOR_STEER_FORWARD_YEARS_MUST_REPRODUCE_VOLATILITY_AT_EVERY_SCALE_2026-10-25.md`, item 2, asks
for the distribution of daily gas log-returns: fat tails, mean reversion, and how a shock decays.
The proposed fit is "on 2016-2025 NBP". On this record, a daily log-return is zero on 3,421 of
3,537 days and a month-sized jump on the other 116. Any gas path fitted to it has no daily or weekly
volatility. A grade against it would pass a generator that has none either, because the record
can't press back at those scales. The monthly and yearly scales can be fitted. The daily and
weekly ones can't, and item 4 (the spark spread's daily range) inherits the same limit on the gas
leg.

The fixed exchange rate removes a second source of monthly movement in £ terms, but that matters
less than the missing daily data.

## What closes it

A daily GB gas price series held lawfully, ingested by the harness as a fetched artefact (W6),
never as a runtime read by the company. **GAP, not established:** which published series is free
to hold. The candidates are National Gas Transmission's daily System Average Price, which the
file's own name (`nbp_sap`) already points at, and Ofgem's wholesale market indicators. Neither
licence nor coverage has been read. This needs a K8 page and a knowledge check of the licences.
Until it exists, EP16's grade must name daily and weekly gas volatility as **not gradeable**, not
as passed.
