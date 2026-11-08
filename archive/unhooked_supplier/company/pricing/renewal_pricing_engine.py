"""Renewal Pricing Engine — compute optimal renewal tariff for each customer.

Combines:
- Cost-to-serve floor: price must cover wholesale + non-commodity + CTS
- SVT ceiling: price at or below SVT (customer incentive to renew)
- Price elasticity: higher price → lower renewal conversion
- Expected margin: maximize conversion × margin_per_customer

Company-observable: uses customer AQ, cost structure, and SVT from market feed.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Optional

# Renewal conversion decay per % above competitor: calibrated to Phase M / CMA 2016
_RENEWAL_CONVERSION_DECAY_PER_PCT_ABOVE: float = 0.02  # 2% conversion lost per 1% above benchmark

# Minimum acceptable gross margin (below this, renewal is loss-making)
_MIN_GROSS_MARGIN_PCT: float = 0.04  # 4% of revenue


class RenewalPricingRecommendation(str, Enum):
    FULL_MARGIN = "full_margin"       # Price at standard margin; customer likely to renew
    COMPETITIVE = "competitive"        # Match competitor (SVT - discount)
    COST_PLUS = "cost_plus"           # Minimum viable price (covers cost)
    NO_OFFER = "no_offer"             # Expected loss even at best price — don't renew


@dataclass(frozen=True)
class RenewalPricingResult:
    customer_id: str
    segment: str
    annual_kwh: float
    current_tariff_gbp_per_mwh: float
    svt_gbp_per_mwh: float
    wholesale_cost_gbp_per_mwh: float
    non_commodity_cost_gbp_per_mwh: float
    cost_to_serve_gbp_pa: float
    recommended_tariff_gbp_per_mwh: float
    recommendation: RenewalPricingRecommendation
    expected_conversion_pct: float
    expected_gross_margin_gbp_pa: float
    expected_net_margin_gbp_pa: float   # after cost_to_serve

    @property
    def total_cost_gbp_per_mwh(self) -> float:
        return round(self.wholesale_cost_gbp_per_mwh + self.non_commodity_cost_gbp_per_mwh, 2)

    @property
    def margin_per_mwh(self) -> float:
        return round(self.recommended_tariff_gbp_per_mwh - self.total_cost_gbp_per_mwh, 2)

    @property
    def is_viable(self) -> bool:
        return self.recommendation != RenewalPricingRecommendation.NO_OFFER

    @property
    def vs_svt_pct(self) -> float:
        if self.svt_gbp_per_mwh <= 0:
            return 0.0
        return round((self.recommended_tariff_gbp_per_mwh - self.svt_gbp_per_mwh)
                     / self.svt_gbp_per_mwh * 100, 2)


def _estimate_conversion(tariff_gbp_mwh: float, svt_gbp_mwh: float,
                         base_conversion_pct: float, segment: str) -> float:
    """Conversion drops as tariff rises above SVT."""
    if svt_gbp_mwh <= 0:
        return base_conversion_pct
    overprice_pct = max(0.0, (tariff_gbp_mwh - svt_gbp_mwh) / svt_gbp_mwh * 100)
    decay = overprice_pct * _RENEWAL_CONVERSION_DECAY_PER_PCT_ABOVE
    # I&C customers are more tolerant of above-SVT prices (relationship selling)
    if segment == "I&C":
        decay *= 0.3
    return max(0.0, min(100.0, base_conversion_pct - decay * 100))


class RenewalPricingEngine:
    """Computes optimal renewal tariff for each customer at renewal date.

    Strategy:
    1. Compute minimum viable tariff (cost floor)
    2. Compute customer's sensitivity to price vs SVT
    3. Find tariff that maximises expected margin (conversion × margin)
    """

    def __init__(
        self,
        base_renewal_conversion_pct: float = 85.0,
        risk_premium_pct: float = 5.0,
    ) -> None:
        self._base_conversion = base_renewal_conversion_pct
        self._risk_premium_pct = risk_premium_pct

    def _cost_floor(self, wholesale: float, non_commodity: float,
                    cost_to_serve_pa: float, annual_kwh: float) -> float:
        """Minimum tariff that covers all costs (no margin)."""
        cts_per_mwh = (cost_to_serve_pa / (annual_kwh / 1000)) if annual_kwh > 0 else 0.0
        return round(wholesale + non_commodity + cts_per_mwh, 2)

    def _target_tariff(self, cost_floor: float, svt: float,
                       risk_premium_pct: float) -> float:
        """Standard offer: cost_floor × (1 + risk_premium)."""
        return round(cost_floor * (1 + risk_premium_pct / 100), 2)

    def price_renewal(
        self,
        customer_id: str,
        segment: str,
        annual_kwh: float,
        current_tariff_gbp_per_mwh: float,
        svt_gbp_per_mwh: float,
        wholesale_cost_gbp_per_mwh: float,
        non_commodity_cost_gbp_per_mwh: float,
        cost_to_serve_gbp_pa: float,
    ) -> RenewalPricingResult:
        cost_floor = self._cost_floor(
            wholesale_cost_gbp_per_mwh, non_commodity_cost_gbp_per_mwh,
            cost_to_serve_gbp_pa, annual_kwh,
        )
        target = self._target_tariff(cost_floor, svt_gbp_per_mwh, self._risk_premium_pct)
        # Cap at SVT × 1.02 (2% above SVT is maximum that preserves meaningful conversion)
        max_tariff = round(svt_gbp_per_mwh * 1.02, 2) if svt_gbp_per_mwh > 0 else target
        final_tariff = min(target, max_tariff)
        # If floor > SVT, we can't make money without pricing above SVT
        if cost_floor > svt_gbp_per_mwh and svt_gbp_per_mwh > 0:
            recommendation = RenewalPricingRecommendation.NO_OFFER
            final_tariff = cost_floor
        elif final_tariff <= cost_floor * 1.001:
            recommendation = RenewalPricingRecommendation.COST_PLUS
        elif abs(final_tariff - svt_gbp_per_mwh) / max(svt_gbp_per_mwh, 1) < 0.03:
            recommendation = RenewalPricingRecommendation.COMPETITIVE
        else:
            recommendation = RenewalPricingRecommendation.FULL_MARGIN
        conversion = _estimate_conversion(
            final_tariff, svt_gbp_per_mwh, self._base_conversion, segment
        )
        margin_per_mwh = final_tariff - (wholesale_cost_gbp_per_mwh + non_commodity_cost_gbp_per_mwh)
        gross_margin = round(margin_per_mwh * annual_kwh / 1000 * (conversion / 100), 2)
        net_margin = round(gross_margin - cost_to_serve_gbp_pa * (conversion / 100), 2)
        return RenewalPricingResult(
            customer_id=customer_id,
            segment=segment,
            annual_kwh=annual_kwh,
            current_tariff_gbp_per_mwh=current_tariff_gbp_per_mwh,
            svt_gbp_per_mwh=svt_gbp_per_mwh,
            wholesale_cost_gbp_per_mwh=wholesale_cost_gbp_per_mwh,
            non_commodity_cost_gbp_per_mwh=non_commodity_cost_gbp_per_mwh,
            cost_to_serve_gbp_pa=cost_to_serve_gbp_pa,
            recommended_tariff_gbp_per_mwh=round(final_tariff, 2),
            recommendation=recommendation,
            expected_conversion_pct=round(conversion, 1),
            expected_gross_margin_gbp_pa=gross_margin,
            expected_net_margin_gbp_pa=net_margin,
        )

    def portfolio_renewal_plan(
        self,
        customers: list[dict],
    ) -> list[RenewalPricingResult]:
        """Price all customers at renewal. Input dicts have keys matching price_renewal args."""
        results = []
        for c in customers:
            r = self.price_renewal(
                customer_id=c["customer_id"],
                segment=c.get("segment", "resi"),
                annual_kwh=c.get("annual_kwh", 3500.0),
                current_tariff_gbp_per_mwh=c.get("current_tariff_gbp_per_mwh", 200.0),
                svt_gbp_per_mwh=c.get("svt_gbp_per_mwh", 280.0),
                wholesale_cost_gbp_per_mwh=c.get("wholesale_cost_gbp_per_mwh", 150.0),
                non_commodity_cost_gbp_per_mwh=c.get("non_commodity_cost_gbp_per_mwh", 55.0),
                cost_to_serve_gbp_pa=c.get("cost_to_serve_gbp_pa", 50.0),
            )
            results.append(r)
        return results

    def pricing_summary(self, results: list[RenewalPricingResult]) -> str:
        if not results:
            return "No renewal pricing results."
        by_rec = {}
        for r in results:
            by_rec.setdefault(r.recommendation.value, []).append(r)
        total_exp_net = sum(r.expected_net_margin_gbp_pa for r in results)
        viable = [r for r in results if r.is_viable]
        lines = [
            f"Renewal Pricing Engine: {len(results)} customers priced",
            f"Viable renewals: {len(viable)}/{len(results)} | Expected net margin: £{total_exp_net:,.0f}",
        ]
        for rec, recs in sorted(by_rec.items()):
            lines.append(f"  {rec}: {len(recs)} customer(s)")
        return "\n".join(lines)
