"""Ofgem FRA Regulatory Capital Ratio -- Phase NZ.

The Ofgem Financial Resilience Assessment (FRA) requires energy suppliers
to maintain equity >= 1x estimated monthly revenue as a minimum threshold.
Post-2022, Ofgem tightened this after multiple supplier failures.

Fidelity: tracks the company's FRA capital ratio per year (equity/monthly revenue),
which real suppliers must report. A declining ratio (e.g., during the 2022 crisis
when revenue rose but equity grew more slowly) is a board-level signal.

Real-world context:
- Bulb Energy (2021 collapse): equity ~ -£4m vs monthly revenue ~ £400m -> ratio ~-0.01x
- Igloo Energy (2021): equity ~ £1m vs monthly revenue ~ £15m -> ratio ~0.07x
- Our SIM supplier: well-capitalised (16-32x), but 2022 is the weakest year.

Epistemic: uses management accounts data (company-observable, double-entry journal).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, List

_FRA_GREEN_THRESHOLD = 6.0    # Ofgem FRA best practice / sector strong
_FRA_AMBER_THRESHOLD = 3.0    # Early warning: approaching compliance risk
_FRA_RED_THRESHOLD = 1.0      # Ofgem FRA minimum (non-compliant below)


@dataclass(frozen=True)
class FRACapitalRatio:
    """Ofgem FRA capital ratio for one year."""

    year: int
    equity_gbp: float
    annual_revenue_gbp: float
    monthly_revenue_gbp: float
    fra_ratio: float             # equity / monthly_revenue
    rag: Literal["GREEN", "AMBER", "RED"]
    is_compliant: bool           # equity >= 1x monthly revenue

    @property
    def year_label(self) -> str:
        return str(self.year)

    @property
    def ratio_label(self) -> str:
        return f"{self.fra_ratio:.1f}x"


def _rag(ratio: float) -> Literal["GREEN", "AMBER", "RED"]:
    if ratio >= _FRA_GREEN_THRESHOLD:
        return "GREEN"
    if ratio >= _FRA_AMBER_THRESHOLD:
        return "AMBER"
    return "RED"


def build_fra_ratio_series(management_accounts: dict) -> List[FRACapitalRatio]:
    """Build the FRA capital ratio series from annual management accounts.

    management_accounts: dict of year -> {income_statement, balance_sheet}
    Returns list sorted by year; empty if no management accounts data.
    """
    if not management_accounts:
        return []

    result = []
    for yr_str in sorted(management_accounts.keys()):
        ma_yr = management_accounts[yr_str]
        bs = ma_yr.get("balance_sheet", {})
        ist = ma_yr.get("income_statement", {})

        equity = bs.get("total_equity_gbp", 0.0)
        revenue = ist.get("revenue_gbp", 0.0)
        if revenue <= 0:
            continue

        monthly_rev = revenue / 12.0
        ratio = equity / monthly_rev if monthly_rev > 0 else 0.0
        rag = _rag(ratio)

        result.append(FRACapitalRatio(
            year=int(yr_str),
            equity_gbp=equity,
            annual_revenue_gbp=revenue,
            monthly_revenue_gbp=round(monthly_rev, 2),
            fra_ratio=round(ratio, 2),
            rag=rag,
            is_compliant=ratio >= _FRA_RED_THRESHOLD,
        ))

    return result


def weakest_year(series: List[FRACapitalRatio]) -> FRACapitalRatio | None:
    """Return the year with the lowest FRA ratio."""
    if not series:
        return None
    return min(series, key=lambda r: r.fra_ratio)


def strongest_year(series: List[FRACapitalRatio]) -> FRACapitalRatio | None:
    """Return the year with the highest FRA ratio."""
    if not series:
        return None
    return max(series, key=lambda r: r.fra_ratio)
