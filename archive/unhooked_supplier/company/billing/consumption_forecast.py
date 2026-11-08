"""Annual cost forecast from calibrated EAC and tariff rate.

Uses customer invoice history to derive EAC, then projects forward
using current tariff unit rate and standing charge.
"""

from __future__ import annotations
from pathlib import Path

from company.billing.eac_calibration import calibrate_eac
from company.billing.invoice import DEFAULT_DB_PATH


def forecast_annual_cost(
    account_id: str,
    unit_rate_p_per_kwh: float,
    standing_charge_p_per_day: float,
    db_path: Path = DEFAULT_DB_PATH,
    lookback_years: int = 2,
) -> dict | None:
    """Forecast annual energy cost using calibrated EAC.

    Returns None if insufficient invoice history to calibrate EAC.
    Returns dict with: eac_kwh, annual_commodity_gbp, annual_sc_gbp, annual_total_gbp,
    quarterly_total_gbp (list of 4), monthly_total_gbp (list of 12).
    """
    eac = calibrate_eac(account_id, db_path, lookback_years)
    if eac is None:
        return None
    annual_commodity = round(eac * unit_rate_p_per_kwh / 100.0, 2)
    annual_sc = round(standing_charge_p_per_day * 365 / 100.0, 2)
    annual_total = round(annual_commodity + annual_sc, 2)
    # Seasonal split: Q1=30%, Q2=22%, Q3=18%, Q4=30% (UK heating profile)
    q_weights = [0.30, 0.22, 0.18, 0.30]
    quarterly = [round(annual_commodity * w + annual_sc / 4, 2) for w in q_weights]
    # Monthly: proportional to quarterly, split evenly within each quarter
    monthly = []
    for q, w in enumerate(q_weights):
        q_commodity = round(annual_commodity * w, 2)
        q_sc = round(annual_sc / 4, 2)
        for _ in range(3):
            monthly.append(round((q_commodity + q_sc) / 3, 2))
    return {
        "eac_kwh": round(eac, 1),
        "unit_rate_p_per_kwh": unit_rate_p_per_kwh,
        "standing_charge_p_per_day": standing_charge_p_per_day,
        "annual_commodity_gbp": annual_commodity,
        "annual_sc_gbp": annual_sc,
        "annual_total_gbp": annual_total,
        "quarterly_total_gbp": quarterly,
        "monthly_total_gbp": monthly,
    }
