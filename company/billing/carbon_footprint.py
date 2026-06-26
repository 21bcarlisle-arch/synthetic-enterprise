"""Carbon footprint estimation for customers.

Uses Ofgem-published UK electricity fuel mix disclosure data (gCO2e/kWh)
to estimate customer carbon footprint from electricity consumption.

Gas carbon intensity from DESNZ (Defra conversion factors): 0.18316 kgCO2e/kWh.
"""

from __future__ import annotations


# UK electricity carbon intensity estimates (gCO2e/kWh) by year
# Source: UK DESNZ grid intensity (annual averages)
_ELECTRICITY_INTENSITY_G_CO2E_PER_KWH = {
    2016: 266,
    2017: 246,
    2018: 233,
    2019: 214,
    2020: 181,
    2021: 190,
    2022: 165,
    2023: 141,
    2024: 126,
    2025: 115,
}

# Gas: DESNZ Scope 1 conversion factor kgCO2e/kWh (stable 2016-2025)
_GAS_KG_CO2E_PER_KWH = 0.18316


def electricity_intensity(year: int) -> float:
    """Return UK grid electricity carbon intensity in gCO2e/kWh for given year."""
    if year in _ELECTRICITY_INTENSITY_G_CO2E_PER_KWH:
        return _ELECTRICITY_INTENSITY_G_CO2E_PER_KWH[year]
    if year < 2016:
        return _ELECTRICITY_INTENSITY_G_CO2E_PER_KWH[2016]
    return _ELECTRICITY_INTENSITY_G_CO2E_PER_KWH[2025]


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
