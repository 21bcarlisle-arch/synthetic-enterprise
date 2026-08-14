"""Carbon footprint estimation for customers.

Grid intensity is NOT declared here. This module used to carry its own
`_ELECTRICITY_INTENSITY_G_CO2E_PER_KWH` table (266 gCO2e/kWh in 2016 falling to 115 in 2025) —
the lowest of three mutually inconsistent series in the tree, up to 55.6% below the one the
annual report publishes, and with no renderer of its own. Deleted 2026-08-14 discharging
`WORKER_FINDING_THREE_LIVE_GRID_INTENSITY_SERIES_DISAGREE_BY_HALF_2026-08-14.md`; the single
owner is `company.regulatory.carbon_emissions`. Do not reintroduce a local table — the control
`tools/grid_intensity_guard.py` fails if one reappears, wherever and however it is declared.

Gas Scope 1 factor also comes from the same owner. It was 0.18316 kgCO2e/kWh here against
0.183 in the published report; the published value survives, because this reconciliation removes
duplicates rather than revaluing anything (the ~0.09% difference is recorded, not resolved — no
external source was fetched).
"""

from __future__ import annotations

from company.regulatory.carbon_emissions import (
    GAS_EMISSION_FACTOR_G_CO2E_PER_KWH,
    grid_intensity_g_co2e_per_kwh,
)

# Gas: Scope 1 conversion factor kgCO2e/kWh, derived from the single owned gram figure.
_GAS_KG_CO2E_PER_KWH = GAS_EMISSION_FACTOR_G_CO2E_PER_KWH / 1000.0


def electricity_intensity(year: int) -> float:
    """Return UK grid electricity carbon intensity in gCO2e/kWh for given year.

    Delegates to the single owner. Years outside the covered window clamp there, preserving this
    function's long-standing pre-2016/post-2025 behaviour.
    """
    return grid_intensity_g_co2e_per_kwh(year)


def estimate_carbon(
    eac_kwh: float,
    commodity: str,
    year: int,
) -> dict:
    """Estimate annual carbon footprint in kg and tonnes CO2e.

    eac_kwh: annual estimated consumption in kWh
    commodity: "electricity" or "gas"
    year: tariff year for intensity lookup

    Returns dict: kg_co2e, tonnes_co2e, intensity, unit.
    """
    if commodity.lower() == "gas":
        kg = round(eac_kwh * _GAS_KG_CO2E_PER_KWH, 1)
        intensity = _GAS_KG_CO2E_PER_KWH * 1000  # in gCO2e/kWh
        unit = "gCO2e/kWh (gas, DESNZ)"
    else:
        g_per_kwh = electricity_intensity(year)
        kg = round(eac_kwh * g_per_kwh / 1000.0, 1)
        intensity = float(g_per_kwh)
        unit = "gCO2e/kWh (grid, DESNZ)"

    return {
        "kg_co2e": kg,
        "tonnes_co2e": round(kg / 1000.0, 2),
        "intensity": intensity,
        "unit": unit,
        "year": year,
    }


def carbon_trend(eac_kwh: float, commodity: str, years: list[int]) -> list[dict]:
    """Return carbon estimates for a sequence of years to show grid decarbonisation."""
    return [
        {"year": yr, **estimate_carbon(eac_kwh, commodity, yr)}
        for yr in years
    ]
