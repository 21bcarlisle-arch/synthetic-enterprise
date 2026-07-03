"""Elexon BSC settlement reconciliation cash flow exposure model.

UK electricity suppliers receive reconciliation adjustments up to 28 months
after each settlement day via the R1/R2/R3/RF run sequence. These runs
correct metering errors, re-read data, and finalise consumption volumes.

For suppliers, this creates:
  - Outstanding reconciliation pool: billed revenue still subject to adjustment
  - Direction uncertainty: adjustments can be credits or charges
  - Crisis-year bias: during price spikes, demand destruction causes
    actual < estimated consumption -> net credit in late reconciliation

Non-HH (profile class, resi/SME): ±4% variance on billed units.
HH (I&C with sub-half-hourly metering): ±0.5% variance.
Source: Elexon Settlement Performance Reports; Ofgem supplier review data.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Literal, Optional


# Reconciliation variance bands (fraction of billed kWh potentially adjusted)
_HH_RECON_VARIANCE = 0.005     # ±0.5% for HH-metered I&C customers
_NON_HH_RECON_VARIANCE = 0.040  # ±4.0% for profile-class non-HH meters

# Settlement run timeline (months after delivery date)
_R1_MONTHS = 1
_R2_MONTHS = 3
_R3_MONTHS = 5   # ~17 weeks
_RF_MONTHS = 28  # Final Reconciliation

# Share of total reconciliation volume resolved at each run
# (80% of errors found in R1/R2; long tail into RF is small but persistent)
_R1_SHARE = 0.60
_R2_SHARE = 0.25
_R3_SHARE = 0.12
_RF_SHARE = 0.03

# RAG thresholds: max adverse adjustment as % of monthly revenue
_GREEN_THRESHOLD = 5.0   # < 5% of monthly revenue
_AMBER_THRESHOLD = 15.0  # < 15% of monthly revenue


@dataclass(frozen=True)
class ReconciliationExposure:
    year: int
    annual_revenue_gbp: float
    hh_fraction: float            # fraction of revenue from HH-metered customers
    outstanding_pool_gbp: float   # approx volume still subject to adjustment at year-end
    max_adverse_gbp: float        # worst-case one-sided adjustment
    expected_adjustment_gbp: float  # expected |net| adjustment (zero-mean, this is 1-sigma)
    months_outstanding: float     # weighted-avg months until final settlement
    rag: Literal["GREEN", "AMBER", "RED"]
    is_crisis_year: bool          # crisis-year bias: expect net credit in late reconciliation


def _blended_variance(hh_fraction: float) -> float:
    """Weighted average reconciliation variance across HH and non-HH meters."""
    return hh_fraction * _HH_RECON_VARIANCE + (1 - hh_fraction) * _NON_HH_RECON_VARIANCE


def _outstanding_months_at_year_end() -> float:
    """Weighted-average months of outstanding reconciliation tail at any year-end.

    At year-end, the most recent 28 months of deliveries are still partially open:
    - Current year (12 months): in R1/R2 tail — high volume, quickly resolved
    - Prior year (12 months): in R3 tail
    - Year before (4 months): in RF tail

    Returns a consumption-weighted average months outstanding.
    """
    # Weight by share outstanding × remaining months
    r1_remaining = _R2_MONTHS - _R1_MONTHS   # 2 months cleared at R1
    r2_remaining = _R3_MONTHS - _R2_MONTHS   # 2 months cleared at R2
    r3_remaining = _RF_MONTHS - _R3_MONTHS   # 23 months cleared at R3
    rf_remaining = 0                          # RF is final

    weighted = (
        _R1_SHARE * r1_remaining +
        _R2_SHARE * r2_remaining +
        _R3_SHARE * r3_remaining +
        _RF_SHARE * rf_remaining
    )
    return weighted


def _rag(max_adverse_gbp: float, monthly_revenue_gbp: float) -> Literal["GREEN", "AMBER", "RED"]:
    if monthly_revenue_gbp <= 0:
        return "GREEN"
    pct = max_adverse_gbp / monthly_revenue_gbp * 100
    if pct < _GREEN_THRESHOLD:
        return "GREEN"
    if pct < _AMBER_THRESHOLD:
        return "AMBER"
    return "RED"


_CRISIS_YEARS = {2021, 2022}


def build_reconciliation_series(
    management_accounts: dict,
    hh_revenue_fraction: float = 0.90,
) -> List[ReconciliationExposure]:
    """Compute per-year settlement reconciliation exposure.

    Args:
        management_accounts: dict keyed by year string with revenue_gbp per year.
        hh_revenue_fraction: fraction of revenue from HH-metered I&C customers.
            Default 0.90 reflects an I&C-dominated portfolio (confirmed Phase NV).
    """
    by_year = management_accounts.get("by_year", {})
    if not by_year:
        return []

    variance = _blended_variance(hh_revenue_fraction)
    outstanding_months = _outstanding_months_at_year_end()
    result = []

    for yr_str in sorted(by_year.keys()):
        yr = int(yr_str)
        rev = by_year[yr_str].get("revenue_gbp", 0.0)
        if rev <= 0:
            continue

        monthly_rev = rev / 12.0
        # Outstanding pool: fraction of annual revenue still in reconciliation tail
        # Approximation: 12 months of deliveries × weighted outstanding fraction
        pool_fraction = outstanding_months / 12.0  # e.g. 2 months / 12 = 0.17
        pool = rev * pool_fraction
        max_adverse = pool * variance
        # Expected adjustment (1-sigma for zero-mean process)
        expected_adj = max_adverse * 0.5  # 1-sigma is roughly half the maximum band

        rag = _rag(max_adverse, monthly_rev)
        result.append(ReconciliationExposure(
            year=yr,
            annual_revenue_gbp=round(rev, 2),
            hh_fraction=hh_revenue_fraction,
            outstanding_pool_gbp=round(pool, 2),
            max_adverse_gbp=round(max_adverse, 2),
            expected_adjustment_gbp=round(expected_adj, 2),
            months_outstanding=round(outstanding_months, 1),
            rag=rag,
            is_crisis_year=yr in _CRISIS_YEARS,
        ))

    return result


def largest_exposure_year(
    series: List[ReconciliationExposure],
) -> Optional[ReconciliationExposure]:
    if not series:
        return None
    return max(series, key=lambda r: r.max_adverse_gbp)
