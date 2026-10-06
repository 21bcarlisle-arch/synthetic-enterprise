# An electricity founder dated 2016-01-01 prices its first term off 55 days of history, not 90

**Severity:** LATENT · **Lane:** W1_market_weather · **Epoch:** 4 · **Atom:** `unminted` · **Claim:** `electricity-first-term-lookback-is-short` (Lane 0 delivery)

**2026-10-06.** Found while fixing the day-one gas founder (b8808f4ad). That fix extended the gas
record back to 2015-10-01 from its own published source, so a gas founder dated 2016-01-01 now has
its full 90-day lookback. The ELECTRICITY record starts 2015-11-07. An electricity founder dated
2016-01-01 therefore prices its first forward term off 55 days, without error and without a flag:
the same defect class as the gas one, silent instead of raising.

**Owed:** extend the electricity price record back to 2015-10-03 from its own published source,
if that source holds those days, as the gas fix did. Otherwise flag the short lookback on the price
record with its reason. Either way, assert that a first term's lookback is complete or flagged, never
silently short.
