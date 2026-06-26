"""Renewal pricing engine.

When a fixed-term contract approaches expiry (typically flagged at 42 days),
the company generates renewal offers for the customer. Pricing uses:
  1. The company's published price feed (observable market data, Phase 76)
  2. Customer segment and consumption history (company-side data)
  3. Margin targets set by the risk committee

This module produces renewal quote packs with multiple options:
  - Fixed 1-year (typically lowest unit rate for new money)
  - Fixed 2-year (priced slightly above 1yr for term premium)
  - Variable (SVT) — customer falls onto this if no renewal chosen

The company cannot see simulation forward curves — it uses only the
observable price feed (docs/market_data/price_feed.json).

Renewal quote acceptance rate feeds into churn analytics (Phase 124).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


# Margin targets by segment (company pricing policy)
_MARGIN_TARGET_P_KWH = {
    "RESI": 2.5,
    "SME": 3.0,
    "IC": 1.8,  # I&C: lower unit margin, higher volume
}

# Term premium over base (additional p/kWh for longer contracts)
_TERM_PREMIUM_P_KWH = {
    "fixed_1yr": 0.0,
    "fixed_2yr": 0.5,   # 0.5p/kWh above 1yr for longer hedge cost
    "variable_svt": 2.5,  # SVT: higher risk premium
}

# Standing charge (p/day) — used in annual cost estimate
_STANDING_CHARGE_P_DAY = {
    "RESI": 61.0,
    "SME": 92.0,
    "IC": 0.0,
}


@dataclass
class RenewalQuote:
    quote_id: str
    customer_id: str
    segment: str
    tariff_type: str
    unit_rate_p_kwh: float
    standing_charge_p_day: float
    annual_est_cost_gbp: float
    valid_until: str   # ISO date
    recommended: bool = False

    @property
    def term_label(self) -> str:
        return {"fixed_1yr": "Fixed 1 Year", "fixed_2yr": "Fixed 2 Year",
                "variable_svt": "Variable (SVT)"}.get(self.tariff_type, self.tariff_type)


@dataclass
class RenewalPack:
    customer_id: str
    expiry_date: str
    days_to_expiry: int
    spot_price_p_kwh: float
    quotes: list[RenewalQuote]

    @property
    def cheapest(self) -> RenewalQuote | None:
        return min(self.quotes, key=lambda q: q.annual_est_cost_gbp) if self.quotes else None

    @property
    def recommended(self) -> RenewalQuote | None:
        return next((q for q in self.quotes if q.recommended), None)


def generate_renewal_pack(
    customer_id: str,
    segment: str,
    spot_price_p_kwh: float,
    annual_consumption_kwh: float,
    expiry_date: str,
    days_to_expiry: int,
    quote_valid_until: str,
) -> RenewalPack:
    """Generate a pack of renewal quotes for a customer contract expiry."""
    margin = _MARGIN_TARGET_P_KWH.get(segment.upper(), 2.5)
    sc = _STANDING_CHARGE_P_DAY.get(segment.upper(), 61.0)
    quotes = []

    tariff_types = ["fixed_1yr", "fixed_2yr", "variable_svt"]
    for i, tt in enumerate(tariff_types):
        unit_rate = round(spot_price_p_kwh + margin + _TERM_PREMIUM_P_KWH[tt], 2)
        annual_cost = round(
            (annual_consumption_kwh * unit_rate / 100.0) + (sc / 100.0 * 365.0), 2
        )
        quotes.append(RenewalQuote(
            quote_id=f"RQ-{customer_id}-{tt[:3].upper()}",
            customer_id=customer_id,
            segment=segment,
            tariff_type=tt,
            unit_rate_p_kwh=unit_rate,
            standing_charge_p_day=sc,
            annual_est_cost_gbp=annual_cost,
            valid_until=quote_valid_until,
            recommended=(tt == "fixed_1yr"),  # default recommend cheapest fixed
        ))

    return RenewalPack(
        customer_id=customer_id,
        expiry_date=expiry_date,
        days_to_expiry=days_to_expiry,
        spot_price_p_kwh=spot_price_p_kwh,
        quotes=quotes,
    )
