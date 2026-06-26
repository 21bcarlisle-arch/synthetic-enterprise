"""Imbalance price risk model.

In the UK Balancing Mechanism, suppliers must match their metered consumption
with licensed supply. Deviations between the contracted (notified) position
and actual metered demand result in imbalance charges:
- Long (over-contracted): sell surplus at System Buy Price (SBP) — can be below spot
- Short (under-contracted): buy deficit at System Sell Price (SSP) — can be far above spot

The NIV (Net Imbalance Volume) charge is typically 15-25% above spot for short positions.
In the 2021-22 crisis, SSP reached £9,999/MWh during stress events.

This module models imbalance exposure from observable data: metered consumption
vs contracted position (from the forward book).

Note: The company observes SSP/SBP from the Elexon API (public); it derives
its imbalance exposure from the difference between metered demand and its
forward position.
"""

from __future__ import annotations

from dataclasses import dataclass


# Typical SSP premium above spot (fraction) under normal conditions
_NIV_PREMIUM_NORMAL = 0.18  # 18% above spot
# During stress conditions (2021-22 crisis style), SSP can be >100% above spot
_NIV_PREMIUM_STRESS = 1.2


@dataclass
class ImbalanceExposure:
    period_id: str             # settlement period identifier
    metered_mwh: float         # actual consumption (from meter reads)
    contracted_mwh: float      # notified position (from forward book)
    spot_price_gbp_mwh: float
    imbalance_mwh: float       # metered - contracted (positive = short)
    charge_gbp: float          # positive = cost to supplier, negative = receipt
    status: str                # "short" / "long" / "balanced"


def compute_imbalance(
    period_id: str,
    metered_mwh: float,
    contracted_mwh: float,
    spot_price_gbp_mwh: float,
    stress: bool = False,
) -> ImbalanceExposure:
    """Compute imbalance exposure for one settlement period.

    Short (metered > contracted): buy at SSP premium above spot.
    Long (metered < contracted): receive at SBP (approximated as spot * 0.95).
    """
    imbalance_mwh = metered_mwh - contracted_mwh
    premium = _NIV_PREMIUM_STRESS if stress else _NIV_PREMIUM_NORMAL

    if abs(imbalance_mwh) < 0.001:
        charge_gbp = 0.0
        status = "balanced"
    elif imbalance_mwh > 0:
        # Short: buy at SSP = spot * (1 + premium)
        ssp = spot_price_gbp_mwh * (1 + premium)
        charge_gbp = imbalance_mwh * ssp
        status = "short"
    else:
        # Long: receive at SBP = spot * 0.95
        sbp = spot_price_gbp_mwh * 0.95
        charge_gbp = imbalance_mwh * sbp  # negative = receipt
        status = "long"

    return ImbalanceExposure(
        period_id=period_id,
        metered_mwh=metered_mwh,
        contracted_mwh=contracted_mwh,
        spot_price_gbp_mwh=spot_price_gbp_mwh,
        imbalance_mwh=round(imbalance_mwh, 4),
        charge_gbp=round(charge_gbp, 2),
        status=status,
    )


def imbalance_summary(exposures: list[ImbalanceExposure]) -> dict:
    """Aggregate imbalance exposure across multiple settlement periods."""
    total_charge = sum(e.charge_gbp for e in exposures)
    short_periods = [e for e in exposures if e.status == "short"]
    long_periods = [e for e in exposures if e.status == "long"]
    return {
        "total_periods": len(exposures),
        "short_periods": len(short_periods),
        "long_periods": len(long_periods),
        "balanced_periods": sum(1 for e in exposures if e.status == "balanced"),
        "total_charge_gbp": round(total_charge, 2),
        "total_short_mwh": round(sum(e.imbalance_mwh for e in short_periods), 4),
        "total_long_mwh": round(abs(sum(e.imbalance_mwh for e in long_periods)), 4),
        "net_cost_or_receipt": "cost" if total_charge > 0 else "receipt",
    }
