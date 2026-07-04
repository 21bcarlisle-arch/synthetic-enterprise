"""Market adapter factory.

Usage:
    from tools.market_adapters import get_market_adapter
    adapter = get_market_adapter()          # default: frozen_2025
    adapter = get_market_adapter("frozen_2025")

Swap the source by setting MARKET_ADAPTER_SOURCE env var — no code changes needed.
"""
import os
from tools.market_data_port import MarketDataPort


def get_market_adapter(source: str | None = None) -> MarketDataPort:
    """Return a MarketDataPort for the given source (default: MARKET_ADAPTER_SOURCE or frozen_2025)."""
    resolved = source or os.environ.get("MARKET_ADAPTER_SOURCE", "frozen_2025")
    if resolved == "frozen_2025":
        from tools.market_adapters.frozen_2025 import Frozen2025Adapter
        return Frozen2025Adapter()
    if resolved == "synthetic":
        from tools.market_adapters.synthetic_generator import CorrelatedGeneratorAdapter
        return CorrelatedGeneratorAdapter()
    raise ValueError(f"Unknown market adapter source: {resolved!r}")
