"""Credit bureau adapter factory.

Usage:
    from tools.credit_adapters import get_credit_bureau_adapter
    bureau = get_credit_bureau_adapter()          # default: synthetic_bureau
    bureau = get_credit_bureau_adapter("synthetic_bureau")

Swap the source by setting CREDIT_ADAPTER_SOURCE env var -- no code changes needed.
Same shape as tools/market_adapters/__init__.py::get_market_adapter (Phase PV).
"""
import os
from tools.credit_bureau_port import CreditBureauPort


def get_credit_bureau_adapter(source: str | None = None) -> CreditBureauPort:
    """Return a CreditBureauPort for the given source (default: CREDIT_ADAPTER_SOURCE or synthetic_bureau)."""
    resolved = source or os.environ.get("CREDIT_ADAPTER_SOURCE", "synthetic_bureau")
    if resolved == "synthetic_bureau":
        from tools.credit_adapters.synthetic_bureau import SyntheticBureauAdapter
        return SyntheticBureauAdapter()
    raise ValueError(f"Unknown credit adapter source: {resolved!r}")
