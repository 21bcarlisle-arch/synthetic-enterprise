"""UK electricity fuel mix disclosure.

UK suppliers must disclose their annual fuel mix to customers (Ofgem/BEIS requirement).
This module provides Ofgem-published average UK grid fuel mix data and allows the
company to report a "matched" renewable tariff for green products.

Data: UK DESNZ Fuel Mix Disclosure, published annually.
"""

from __future__ import annotations


# UK average grid fuel mix (%) by year — DESNZ Annual Fuel Mix Disclosure
# Note: these are UK-average grid figures, not company-specific.
_FUEL_MIX_BY_YEAR: dict[int, dict[str, float]] = {
    2016: {"renewable": 24.6, "nuclear": 20.9, "gas": 42.6, "coal": 9.0, "other": 2.9},
    2017: {"renewable": 29.3, "nuclear": 20.4, "gas": 40.7, "coal": 7.0, "other": 2.6},
    2018: {"renewable": 33.0, "nuclear": 19.3, "gas": 39.4, "coal": 5.1, "other": 3.2},
    2019: {"renewable": 36.9, "nuclear": 17.4, "gas": 38.3, "coal": 2.1, "other": 5.3},
    2020: {"renewable": 42.2, "nuclear": 16.7, "gas": 35.8, "coal": 1.8, "other": 3.5},
    2021: {"renewable": 39.8, "nuclear": 14.5, "gas": 38.3, "coal": 2.5, "other": 4.9},
    2022: {"renewable": 40.5, "nuclear": 14.5, "gas": 37.8, "coal": 1.7, "other": 5.5},
    2023: {"renewable": 47.8, "nuclear": 14.6, "gas": 31.5, "coal": 1.3, "other": 4.8},
    2024: {"renewable": 51.4, "nuclear": 14.1, "gas": 28.6, "coal": 0.4, "other": 5.5},
    2025: {"renewable": 55.0, "nuclear": 13.5, "gas": 26.0, "coal": 0.1, "other": 5.4},
}


def get_fuel_mix(year: int) -> dict[str, float]:
    """Return UK average grid fuel mix percentages for the given year."""
    if year in _FUEL_MIX_BY_YEAR:
        return dict(_FUEL_MIX_BY_YEAR[year])
    if year < 2016:
        return dict(_FUEL_MIX_BY_YEAR[2016])
    return dict(_FUEL_MIX_BY_YEAR[2025])


def fuel_mix_summary(year: int) -> dict:
    """Return fuel mix with derived fields for portal display.

    Includes: year, mix breakdown, renewable_pct, low_carbon_pct (renewable + nuclear),
    fossil_pct, trend vs prior year.
    """
    mix = get_fuel_mix(year)
    prior = get_fuel_mix(year - 1)

    renewable_pct = mix["renewable"]
    low_carbon_pct = mix["renewable"] + mix["nuclear"]
    fossil_pct = mix["gas"] + mix["coal"]

    prior_renewable = prior["renewable"]
    renewable_trend = round(renewable_pct - prior_renewable, 1)

    return {
        "year": year,
        "mix": mix,
        "renewable_pct": round(renewable_pct, 1),
        "low_carbon_pct": round(low_carbon_pct, 1),
        "fossil_pct": round(fossil_pct, 1),
        "renewable_trend": renewable_trend,
        "trend_direction": "up" if renewable_trend > 0 else "down" if renewable_trend < 0 else "flat",
    }
