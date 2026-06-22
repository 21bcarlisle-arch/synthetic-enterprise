"""Phase 39a: UK domestic SVT (Standard Variable Tariff) electricity unit rates.

Rates sourced from Ofgem Default Tariff Cap quarterly updates.
Unit: pence per kWh (convert × 10 for £/MWh).

Quarterly periods: Jan (Q1), Apr (Q2), Jul (Q3), Oct (Q4).
Each period's rate applies until the next period begins.
"""

from __future__ import annotations
from datetime import date

# (year, quarter_start_month) → pence/kWh electricity SVT unit rate
# Pre-2019: midpoint of reported range (±15% confidence)
# Post-2019: Ofgem cap figures, high confidence
_SVT_ELEC_PENCE_PER_KWH: dict[tuple[int, int], float] = {
    (2016, 1): 14.0,
    (2017, 1): 14.0,
    (2018, 1): 15.25,
    # Post-cap (Ofgem Default Tariff Cap)
    (2019, 1): 16.52,
    (2019, 4): 18.56,
    (2019, 7): 18.56,  # no Jul 2019 change in data; hold Apr
    (2019, 10): 17.85,
    (2020, 1): 17.81,
    (2020, 4): 17.81,
    (2020, 7): 17.81,
    (2020, 10): 17.19,
    (2021, 1): 17.19,
    (2021, 4): 18.95,
    (2021, 7): 18.95,
    (2021, 10): 20.80,
    (2022, 1): 20.80,
    (2022, 4): 28.34,
    (2022, 7): 28.34,
    (2022, 10): 51.89,
    (2023, 1): 67.0,   # EPG applied; cap ceiling was ~£4,279/year
    (2023, 4): 30.1,
    (2023, 7): 30.1,
    (2023, 10): 27.4,
    (2024, 1): 27.4,
    (2024, 4): 24.50,
    (2024, 7): 22.36,
    (2024, 10): 24.50,
    (2025, 1): 24.86,
    (2025, 4): 27.03,
    (2025, 7): 25.73,
    (2025, 10): 26.35,
    # Extrapolated 2026+ — moderate decline as renewables penetration rises
    (2026, 1): 26.0,
    (2026, 4): 25.5,
    (2026, 7): 25.0,
    (2026, 10): 25.5,
    (2027, 1): 25.0,
    (2027, 4): 24.5,
    (2027, 7): 24.0,
    (2027, 10): 24.5,
    (2028, 1): 24.0,
    (2028, 4): 23.5,
    (2028, 7): 23.0,
    (2028, 10): 23.5,
    (2029, 1): 23.0,
    (2029, 4): 22.5,
    (2029, 7): 22.0,
    (2029, 10): 22.5,
}

_QUARTER_START_MONTHS = (1, 4, 7, 10)


def _quarter_start_month(month: int) -> int:
    """Return the cap-period start month for a given calendar month."""
    for q in reversed(_QUARTER_START_MONTHS):
        if month >= q:
            return q
    return 1


def get_svt_elec_rate_gbp_per_mwh(date_str: str) -> float | None:
    """Return electricity SVT unit rate in £/MWh for the given date.

    Returns None if the date is before 2016 (no data).
    Falls back to the earliest available period if no exact match.
    """
    d = date.fromisoformat(date_str)
    if d.year < 2016:
        return None
    q = _quarter_start_month(d.month)
    # Walk back to find nearest available key
    for year in range(d.year, 2015, -1):
        for start_month in reversed(_QUARTER_START_MONTHS):
            if year == d.year and start_month > q:
                continue
            key = (year, start_month)
            if key in _SVT_ELEC_RATE_GBP_PER_MWH:
                return _SVT_ELEC_RATE_GBP_PER_MWH[key]
    return None


# Pre-compute £/MWh version (pence/kWh × 10)
_SVT_ELEC_RATE_GBP_PER_MWH: dict[tuple[int, int], float] = {
    k: round(v * 10, 2) for k, v in _SVT_ELEC_PENCE_PER_KWH.items()
}
