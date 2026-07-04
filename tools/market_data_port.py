"""MarketDataPort — structural interface for market data sources.

Adapter implementations satisfy this Protocol without requiring inheritance.
Current adapters: Frozen2025Adapter (wraps live_market.py frozen 2025-12-31 cache).
Future adapters slot in with zero company-layer changes.
"""
from __future__ import annotations
import datetime
from typing import Optional, Protocol, runtime_checkable


@runtime_checkable
class MarketDataPort(Protocol):
    def get_spot_elec_gbp_per_mwh(self, as_of: Optional[datetime.date] = None) -> float: ...
    def get_spot_gas_gbp_per_mwh(self, as_of: Optional[datetime.date] = None) -> float: ...
    def get_forward_price(
        self,
        as_of: Optional[datetime.date] = None,
        delivery_date: Optional[datetime.date] = None,
        commodity: str = "electricity",
    ) -> float: ...
    def get_market_summary(self, as_of: Optional[datetime.date] = None) -> dict: ...
