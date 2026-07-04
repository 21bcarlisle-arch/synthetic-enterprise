## Phase PV COMPLETE -- Market Feed Swappable Adapter
Last updated: 2026-07-04T01:42:00Z

**Status:** COMPLETE. 15,335 tests passing.

**Phase PV -- Market Feed Swappable Adapter:**
- tools/market_data_port.py: MarketDataPort Protocol (get_spot_elec/get_spot_gas/get_forward_price/get_market_summary; optional as_of date)
- tools/market_adapters/frozen_2025.py: Frozen2025Adapter wraps live_market.py unchanged
- tools/market_adapters/__init__.py: get_market_adapter(source) factory; reads MARKET_ADAPTER_SOURCE env var (default: frozen_2025)
- tools/run_live_decisions.py: market_adapter injection param; defaults to factory
- Architecture: correlated synthetic generator drops in as CorrelatedGeneratorAdapter with zero company-layer rework
- Epistemic: PASS

**Next: Phase PW -- I&C Corporate Arrears Calibration** (proposed 2026-07-04 01:22; 4h opt-out window closes ~05:22 BST)

**Latest simulation results (2016–2025)** — auto-processed (667s / 11 min):
- Net margin: £1,445,257.67 | Gross: £6,467,308.57 | Capital: £51,433
- Treasury: £2,466,636 → £3,911,894 | 38 committee interventions | 1605 bills issued
- Enterprise value: £8,826,938.57 | Net after CTS: £6,360,822
- Retention: 12 offers, 12/12 retained | 6 no-offer churns | 6 total churned accounts