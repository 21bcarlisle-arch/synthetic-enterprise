"""Ofgem domestic market report data.

Ofgem publishes quarterly domestic market reports including:
- Average unit rates by fuel/segment
- Average standing charges
- Number of domestic accounts per supplier tier
- Switching rates

This module provides access to published market benchmarks from Ofgem's
domestic markets reports. This is public information the company would use
for market intelligence — not simulation internals.

Data: Ofgem Domestic Market Report, Energy Trends (BEIS/DESNZ),
      Citizens Advice Energy Scorecard.
"""

from __future__ import annotations


# UK average domestic electricity unit rate (p/kWh, incl. VAT) by year
# Source: Ofgem domestic market reports, BEIS Energy Trends
_UK_AVG_ELEC_UNIT_RATE_P_KWH: dict[int, float] = {
    2016: 13.6, 2017: 14.1, 2018: 15.2, 2019: 16.3, 2020: 17.2,
    2021: 19.7, 2022: 34.0, 2023: 29.0, 2024: 24.5, 2025: 22.3,
}

# UK average domestic gas unit rate (p/kWh, incl. VAT) by year
_UK_AVG_GAS_UNIT_RATE_P_KWH: dict[int, float] = {
    2016: 3.5, 2017: 3.6, 2018: 4.0, 2019: 4.2, 2020: 4.3,
    2021: 5.7, 2022: 10.3, 2023: 7.2, 2024: 5.8, 2025: 5.2,
}

# Average number of domestic accounts in the market (millions)
_UK_DOMESTIC_ACCOUNTS_M: dict[int, float] = {
    2016: 27.9, 2017: 28.0, 2018: 28.1, 2019: 28.3, 2020: 28.0,
    2021: 27.5, 2022: 26.8, 2023: 27.2, 2024: 27.5, 2025: 27.8,
}

# Annual switching rate (% of domestic customers that switch per year)
_UK_SWITCHING_RATE_PCT: dict[int, float] = {
    2016: 17.0, 2017: 18.5, 2018: 20.1, 2019: 18.9, 2020: 14.2,
    2021: 6.1,  2022: 2.8,  2023: 8.4,  2024: 11.2, 2025: 13.0,
}


def get_market_elec_rate(year: int) -> float:
    """Return UK average domestic electricity unit rate in p/kWh."""
    return _UK_AVG_ELEC_UNIT_RATE_P_KWH.get(year, _UK_AVG_ELEC_UNIT_RATE_P_KWH[2025])


def get_market_gas_rate(year: int) -> float:
    """Return UK average domestic gas unit rate in p/kWh."""
    return _UK_AVG_GAS_UNIT_RATE_P_KWH.get(year, _UK_AVG_GAS_UNIT_RATE_P_KWH[2025])


def get_switching_rate(year: int) -> float:
    """Return UK domestic switching rate (% of accounts per year)."""
    return _UK_SWITCHING_RATE_PCT.get(year, _UK_SWITCHING_RATE_PCT[2025])


def market_benchmark(year: int) -> dict:
    """Return full market benchmark snapshot for a given year."""
    elec = get_market_elec_rate(year)
    gas = get_market_gas_rate(year)
    switch = get_switching_rate(year)
    accounts_m = _UK_DOMESTIC_ACCOUNTS_M.get(year, _UK_DOMESTIC_ACCOUNTS_M[2025])
    return {
        "year": year,
        "elec_unit_rate_p_kwh": elec,
        "gas_unit_rate_p_kwh": gas,
        "switching_rate_pct": switch,
        "domestic_accounts_millions": accounts_m,
        "elec_annual_gbp_typical": round(elec * 3100 / 100, 0),  # 3100 kWh/yr typical
        "gas_annual_gbp_typical": round(gas * 11500 / 100, 0),   # 11500 kWh/yr typical
    }


def compare_to_market(own_elec_p_kwh: float, own_gas_p_kwh: float, year: int) -> dict:
    """Compare company's effective rates to market averages.

    Returns: premium_elec (% above/below market), premium_gas, overall positioning.
    """
    market_elec = get_market_elec_rate(year)
    market_gas = get_market_gas_rate(year)

    elec_delta_pct = ((own_elec_p_kwh - market_elec) / market_elec * 100) if market_elec else 0.0
    gas_delta_pct = ((own_gas_p_kwh - market_gas) / market_gas * 100) if market_gas else 0.0

    positioning = "BELOW_MARKET" if elec_delta_pct < -3 else (
                  "ABOVE_MARKET" if elec_delta_pct > 3 else "AT_MARKET")

    return {
        "year": year,
        "own_elec_p_kwh": own_elec_p_kwh,
        "market_elec_p_kwh": market_elec,
        "elec_delta_pct": round(elec_delta_pct, 1),
        "own_gas_p_kwh": own_gas_p_kwh,
        "market_gas_p_kwh": market_gas,
        "gas_delta_pct": round(gas_delta_pct, 1),
        "positioning": positioning,
    }
