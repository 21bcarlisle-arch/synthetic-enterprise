# NEXT PHASE PROPOSAL: Phase PV -- Market Feed Swappable Adapter

## Gap addressed
Phase PU built tools/live_market.py as a direct Elexon SSP cache reader (frozen 2025-12-31).
This is correct for NOW but hardwires one source behind the company's decision layer.
Rich's steer (2026-07-04): the company's daily decision loop must consume a market-data PORT;
what sits behind it (historical replay, fresh API, synthetic correlated generator) is a swap,
not a rewrite. Build the adapter now so the correlated generator (endgame) drops in with
zero company-layer rework.

## What real fidelity is gained
A real UK energy supplier's risk system is source-agnostic: it receives a market data feed
and acts on it regardless of origin. PV makes our simulation architecturally honest:
the company layer no longer "knows" it is reading a frozen 2025-12-31 cache -- it just
consumes a MarketDataPort, same as it will when we eventually wire in the synthetic
correlated generator.

## What this phase builds

### Part A: MarketDataPort interface (tools/market_data_port.py)
Abstract interface (Protocol / ABC):
  class MarketDataPort:
    def get_spot_elec_gbp_per_mwh(self, as_of: date) -> float
    def get_spot_gas_p_per_therm(self, as_of: date) -> float
    def get_forward_price(self, as_of: date, delivery_date: date, commodity: str) -> float
    def get_market_summary(self, as_of: date) -> dict

### Part B: Frozen2025Adapter (tools/market_adapters/frozen_2025.py)
Wraps existing tools/live_market.py functions unchanged behind MarketDataPort.
All current callers (tools/run_live_decisions.py) switch to Frozen2025Adapter().
Behaviour identical to today; ONLY the call site changes.

### Part C: Adapter factory (tools/market_adapters/__init__.py)
get_market_adapter(source: str = "frozen_2025") -> MarketDataPort
  "frozen_2025" -> Frozen2025Adapter
  (future) "synthetic" -> CorrelatedGeneratorAdapter  # not implemented here
  (future) "live_bmrs" -> BmrsLiveAdapter

### Part D: Update callers
tools/run_live_decisions.py: replace direct live_market.py calls with adapter.get_*()
tools/generate_dashboard_data.py: if it calls live_market, route via adapter

### Part E: Update process_run_complete.py
Pass adapter source as env var MARKET_ADAPTER_SOURCE (default: frozen_2025).
Swapping to a different adapter = change one env var, not code surgery.

## Architecture decision (reversible)
The Frozen2025Adapter is a thin wrapper; if it is removed, existing code reverts exactly
to today's state. No one-way door.

## Epistemic check
The adapter is pure plumbing -- no new data sources, no new company-layer capabilities.
Company layer still only consumes observable market prices. PASS.

## Test targets (~15 tests)
1. MarketDataPort Protocol is satisfied by Frozen2025Adapter
2. get_spot_elec_gbp_per_mwh returns a float > 0 for 2025-12-31
3. get_spot_gas_p_per_therm returns a float > 0 for 2025-12-31
4. get_forward_price returns float for elec and gas
5. get_market_summary returns dict with expected keys
6. get_market_adapter("frozen_2025") returns Frozen2025Adapter instance
7. get_market_adapter with unknown source raises ValueError
8. run_live_decisions uses adapter internally (no direct live_market import in caller)
9. Frozen2025Adapter result matches direct live_market.py result (regression)
10. process_run_complete runs end-to-end with adapter source = frozen_2025
11. MARKET_ADAPTER_SOURCE env var controls adapter selection in factory
12. Adapter satisfies MarketDataPort for date BEFORE as-of (returns frozen 2025 data)
13. Adapter satisfies MarketDataPort for date AFTER as-of (same frozen data)
14. Two adapter instances for same params return equal spot prices (determinism)
15. Adding a stub ThirdAdapter satisfying the Protocol requires no changes to callers

## Expected outcome
tools/live_market.py unchanged. tools/run_live_decisions.py now imports adapter, not live_market.
When correlated generator is eventually built, it drops in as CorrelatedGeneratorAdapter
implementing MarketDataPort -- zero company-layer changes needed.
