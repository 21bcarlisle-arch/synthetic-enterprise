"""Price Elasticity Estimator — models customer churn response to tariff changes.

Company-observable: calibrated from billing history and bill-shock events.
Does NOT read simulation internals (churn parameters, forward curves).
Reference: CMA Energy Market Investigation 2016; Ofgem consumer research 2019-2023.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional

# Price elasticity of demand for domestic electricity/gas in UK
# Defined as: extra_churn_rate_pct per 1% price increase
# Source: CMA 2016 Appendix 9.11; Ofgem switching research 2019-2023
# Negative sign: higher price → higher churn
_PRICE_ELASTICITY_BY_SEGMENT: dict[str, float] = {
    "resi": -0.18,        # 10% price increase → ~1.8% additional annual churn
    "SME": -0.12,         # SME less elastic (switching costs, annual reviews)
    "I&C": -0.05,         # I&C very low (long contracts, dedicated account manager)
}

# Bill shock threshold: tariff changes above this level are classified as high-shock events
_HIGH_SHOCK_THRESHOLD_PCT = 20.0

# Crisis elasticity multiplier: during energy price crises, customers are more sensitised
_CRISIS_ELASTICITY_MULTIPLIER = 1.5


class ElasticityBand(str, Enum):
    LOW = "low"          # Stable bills, below-SVT pricing — lowest churn risk
    MODERATE = "moderate"  # Standard pricing, moderate shock
    HIGH = "high"        # Large price increase or above-SVT pricing


@dataclass(frozen=True)
class PriceChangeImpact:
    segment: str
    tariff_change_pct: float
    base_churn_rate_pct: float
    extra_churn_rate_pct: float
    total_churn_rate_pct: float
    expected_lost_customers: int
    expected_lost_revenue_gbp: float
    expected_retained_revenue_gbp: float
    pre_change_revenue_gbp: float
    is_viable: bool  # retained revenue > pre_change revenue

    @property
    def elasticity_band(self) -> ElasticityBand:
        if self.extra_churn_rate_pct < 2.0:
            return ElasticityBand.LOW
        elif self.extra_churn_rate_pct < 8.0:
            return ElasticityBand.MODERATE
        return ElasticityBand.HIGH

    @property
    def revenue_delta_gbp(self) -> float:
        return round(self.expected_retained_revenue_gbp - self.pre_change_revenue_gbp, 2)


@dataclass(frozen=True)
class PortfolioImpact:
    tariff_change_pct: float
    total_customers: int
    total_lost_customers: int
    total_lost_revenue_gbp: float
    total_retained_revenue_gbp: float
    pre_change_revenue_gbp: float
    is_viable: bool

    @property
    def net_revenue_delta_gbp(self) -> float:
        return round(self.total_retained_revenue_gbp - self.pre_change_revenue_gbp, 2)

    @property
    def retention_rate_pct(self) -> float:
        if self.total_customers == 0:
            return 100.0
        retained = self.total_customers - self.total_lost_customers
        return round(retained / self.total_customers * 100, 1)


class PriceElasticityBook:
    """Estimates portfolio churn response to tariff changes using price elasticity model.

    Calibrated from CMA 2016 / Ofgem switching research — company-observable.
    """

    def __init__(self, is_crisis_year: bool = False) -> None:
        self._is_crisis_year = is_crisis_year

    def _elasticity_for_segment(self, segment: str) -> float:
        base = _PRICE_ELASTICITY_BY_SEGMENT.get(segment, -0.15)
        if self._is_crisis_year:
            base *= _CRISIS_ELASTICITY_MULTIPLIER
        return base

    def estimate_churn_impact(
        self,
        segment: str,
        tariff_change_pct: float,
        base_churn_rate_pct: float,
        customer_count: int,
        annual_revenue_gbp: float,
    ) -> PriceChangeImpact:
        """Estimate churn response to a single-segment tariff change.

        Args:
            segment: Customer segment ("resi", "SME", "I&C")
            tariff_change_pct: Percentage tariff change (positive = increase)
            base_churn_rate_pct: Existing annual churn rate without price change
            customer_count: Number of customers in segment
            annual_revenue_gbp: Total annual revenue from segment
        """
        elasticity = self._elasticity_for_segment(segment)
        # Extra churn = elasticity × tariff_change_pct (elasticity is negative for price rises)
        extra_churn_pct = abs(elasticity * tariff_change_pct)
        # Extra churn only applies for price increases
        if tariff_change_pct < 0:
            extra_churn_pct = -abs(elasticity * tariff_change_pct) * 0.3  # partial offset for decreases
        total_churn_pct = min(100.0, base_churn_rate_pct + extra_churn_pct)
        lost = round(customer_count * total_churn_pct / 100)
        retained = customer_count - lost
        rev_per_customer = annual_revenue_gbp / customer_count if customer_count else 0.0
        new_rate_factor = 1 + tariff_change_pct / 100
        retained_revenue = round(retained * rev_per_customer * new_rate_factor, 2)
        lost_revenue = round(lost * rev_per_customer, 2)
        is_viable = retained_revenue >= annual_revenue_gbp
        return PriceChangeImpact(
            segment=segment,
            tariff_change_pct=tariff_change_pct,
            base_churn_rate_pct=round(base_churn_rate_pct, 2),
            extra_churn_rate_pct=round(extra_churn_pct, 2),
            total_churn_rate_pct=round(total_churn_pct, 2),
            expected_lost_customers=lost,
            expected_lost_revenue_gbp=lost_revenue,
            expected_retained_revenue_gbp=retained_revenue,
            pre_change_revenue_gbp=round(annual_revenue_gbp, 2),
            is_viable=is_viable,
        )

    def model_portfolio_impact(
        self,
        tariff_change_pct: float,
        segments: dict[str, dict],
    ) -> PortfolioImpact:
        """Model cross-portfolio impact of a uniform tariff change.

        Args:
            tariff_change_pct: Same percentage applied to all segments
            segments: dict of segment_name -> {"churn_pct": float, "count": int, "revenue_gbp": float}
        """
        total_customers = 0
        total_lost = 0
        total_retained_rev = 0.0
        total_pre_rev = 0.0
        total_lost_rev = 0.0
        for seg, params in segments.items():
            impact = self.estimate_churn_impact(
                segment=seg,
                tariff_change_pct=tariff_change_pct,
                base_churn_rate_pct=params.get("churn_pct", 25.0),
                customer_count=params.get("count", 0),
                annual_revenue_gbp=params.get("revenue_gbp", 0.0),
            )
            total_customers += params.get("count", 0)
            total_lost += impact.expected_lost_customers
            total_retained_rev += impact.expected_retained_revenue_gbp
            total_pre_rev += impact.pre_change_revenue_gbp
            total_lost_rev += impact.expected_lost_revenue_gbp
        return PortfolioImpact(
            tariff_change_pct=tariff_change_pct,
            total_customers=total_customers,
            total_lost_customers=total_lost,
            total_lost_revenue_gbp=round(total_lost_rev, 2),
            total_retained_revenue_gbp=round(total_retained_rev, 2),
            pre_change_revenue_gbp=round(total_pre_rev, 2),
            is_viable=total_retained_rev >= total_pre_rev,
        )

    def optimal_tariff_change(
        self,
        segment: str,
        base_churn_rate_pct: float,
        customer_count: int,
        annual_revenue_gbp: float,
        step_pct: float = 1.0,
        search_range: tuple[float, float] = (-10.0, 30.0),
    ) -> float:
        """Find tariff change % that maximises retained revenue for a segment."""
        best_change = 0.0
        best_retained = annual_revenue_gbp
        c = search_range[0]
        while c <= search_range[1]:
            impact = self.estimate_churn_impact(
                segment=segment,
                tariff_change_pct=c,
                base_churn_rate_pct=base_churn_rate_pct,
                customer_count=customer_count,
                annual_revenue_gbp=annual_revenue_gbp,
            )
            if impact.expected_retained_revenue_gbp > best_retained:
                best_retained = impact.expected_retained_revenue_gbp
                best_change = c
            c = round(c + step_pct, 6)
        return best_change

    def elasticity_summary(self) -> str:
        crisis_note = " [CRISIS YEAR — elasticity ×1.5]" if self._is_crisis_year else ""
        lines = [
            f"Price Elasticity Estimator{crisis_note}",
            "Calibration (CMA 2016 / Ofgem 2019-2023):",
        ]
        for seg, e in _PRICE_ELASTICITY_BY_SEGMENT.items():
            eff = e * (_CRISIS_ELASTICITY_MULTIPLIER if self._is_crisis_year else 1.0)
            lines.append(f"  {seg}: {eff:.3f} ({abs(eff * 10):.1f}% extra churn per 10% price rise)")
        return "\n".join(lines)
