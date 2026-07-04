"""Frozen2025Adapter — wraps tools/live_market.py behind MarketDataPort.

Behaviour is identical to calling live_market.py functions directly;
only the call site changes. Removing this adapter reverts exactly to the pre-PV state.
"""
from __future__ import annotations
import datetime
from typing import Optional


class Frozen2025Adapter:
    """MarketDataPort backed by the frozen Elexon SSP cache (as-of 2025-12-31)."""

    def get_spot_elec_gbp_per_mwh(self, as_of: Optional[datetime.date] = None) -> float:
        from tools.live_market import fetch_spot_elec
        return fetch_spot_elec(str(as_of) if as_of else None)

    def get_spot_gas_gbp_per_mwh(self, as_of: Optional[datetime.date] = None) -> float:
        from tools.live_market import fetch_spot_gas
        return fetch_spot_gas(str(as_of) if as_of else None)

    def get_forward_price(
        self,
        as_of: Optional[datetime.date] = None,
        delivery_date: Optional[datetime.date] = None,
        commodity: str = "electricity",
    ) -> float:
        from tools.live_market import build_live_forward_price
        return build_live_forward_price(str(as_of) if as_of else None, fuel=commodity)

    def get_market_summary(self, as_of: Optional[datetime.date] = None) -> dict:
        from tools.live_market import get_market_summary
        return get_market_summary(str(as_of) if as_of else None)
