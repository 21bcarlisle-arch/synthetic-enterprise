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

## Resolution, 2026-10-06 — FLAGGED, not extended

**The source does not hold those days.** Re-probed Elexon's system-prices endpoint on 2026-10-06:
2015-10-03, 2015-11-04 and 2015-11-05 return 0 records, 2015-11-06 one, and 2015-11-07 a full 48.
This is P305's single-price start (`docs/simulation-period.md`), so nothing under the current
methodology exists to extend from.

- `sim.system_prices_history.RECORD_START` / `SHORT_RECORD_REASON` declare the start and why it
  cannot move. Gas declares `SHORT_RECORD_REASON = None` beside its own `RECORD_START`.
- `sim.forward_curve.short_first_term_lookbacks` refuses a short first-term lookback on a record
  with no declared reason, naming the customer. `run_phase2b` calls it for both fuels and publishes
  the rows as `short_first_term_lookbacks`. On the production book that is 8 of 109 electricity
  accounts (acquired 2016-01-01 to 2016-02-04, 55–89 days covered), and no gas accounts.
- **No after-start read for electricity.** The gas leak came from a gas-only fallback (removed in
  b8808f4ad); electricity always went through `generate_forward_price`, which filters strictly
  before the start. Measured on the real record: for 2016-01-01, 01-15, 02-04 and 02-05, the price
  from the whole record equals the price from only the records before the start.
- **The control:** `tests/sim/test_first_term_lookback.py`, over both fuels. It goes red when the
  electricity reason is dropped, when the gas record is moved to start on the founders' day, when
  the guard never raises, and when it never flags.

Not done here: the cold-spell weather lookback (`lookback_mean_temps`) has its own record start,
and this finding does not establish whether that window is complete for a day-one founder.
