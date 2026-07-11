# M1 finding: two separate price-data pipelines, not one (2026-07-11)

**Context:** THE_VALUE_CYCLE_FRAMING.md's M1 exit test requires "the hedge
decision literally cannot see past 'now'" as a structural property, not a
per-call-site patch. The obvious next step looked like: migrate
`company/trading/hedge_decision.py::estimate_price_volatility()`'s one known
call site (`simulation/run_phase2b.py`) onto the existing `PointInTimeView`
object, retiring the wrapper-based fix (`_price_history_as_of()`) from the
already-closed hedge-volatility-lookback bug.

**Why that would have been wrong, caught before writing the code:**

`PointInTimeView.market_data_port` is backed by
`tools/market_adapters/frozen_2025.py` -> `tools/live_market.py`, which reads
`sim/cache/elexon_ssp_full.json` — a frozen snapshot, explicitly built for the
**live decision path** (the module's own comment: "Merged into the LIVE
decision path only, here" — i.e. `tools/run_live_decisions.py`-style
present-day company view).

The **historical backtest simulation**'s own price records — `elec_records`/
`gas_records` in `simulation/run_phase2b.py`, the exact lists
`_price_history_as_of()` bounds — come from a **completely different**
pipeline: `sim/system_prices_history.py::get_system_prices_range()` hits the
**live Elexon API directly** for the run's own date range (real historical
settlement data, fetched fresh per run).

Migrating the hedge-decision call site onto `PointInTimeView`/
`MarketDataPort` as originally planned would have silently swapped the
historical backtest's real settlement-price basis for an unrelated frozen
2025-snapshot feed — corrupting the entire historical simulation's economics,
not fixing anything. Also confirmed: `MarketDataPort` has no bulk-history
method at all (only single-point spot/forward/summary reads) — would need
extending regardless of which pipeline it served.

**Real next step (not yet built):** either

- (a) extend `PointInTimeView.get_history_as_known()` to be backed by a
  `BitemporalEventLog` populated from the historical simulation's OWN
  `elec_records`/`gas_records` (not `MarketDataPort`), or
- (b) promote `_price_history_as_of()`'s already-correct per-call-site bound
  into a small dedicated as-of-view class wrapping the sim's own record lists
  directly, never touching `MarketDataPort` at all.

Sizing/choice between (a)/(b) is the next M1 depth-work session's first task.
Registered in `docs/design/maturity_map.yaml`'s `W1_reveal_over_time` atom.
