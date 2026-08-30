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

# Annual switching rate: EXTERNAL changes of supplier on a domestic ELECTRICITY meter point, over
# ALL domestic electricity accounts, whether or not the account was at a decision point that year.
# The numerator and the denominator are both stated because neither is recoverable from the number
# (R14): a both-fuel numerator over this denominator double-counts every dual-fuel household and
# reads roughly 1.8x high, which is the standing trap in this area.
#
# EACH VALUE IS THE MIDPOINT OF THE PUBLISHED BAND, and that is a reading rather than a publication
# -- the record states switch COUNTS, and a count over an account total is a band once the account
# total's own drift is admitted. The band itself lives in the regulation commons at
# `docs/domain_artefact_library/regulatory/gb_domestic_switching_rate.json`, and
# `tests/architecture/test_switching_rate_commons.py` holds every lane's reading inside it. B3's
# rule applies here as it does to the cap: the commons holds the record, each lane holds its own
# reading, and no test pins two readings to each other.
#
# WHAT WAS HERE BEFORE, AND WHY IT WENT (2026-08-30). The previous table was per-line unsourced and
# sat OUTSIDE the published band in NINE of ten years -- 2021 at 6.1% against a published 17.9-18.4%,
# 2020 at 14.2% against 22.5-23.0%. `docs/market_research/f5_simulated_competitor_field.md` §9 caught
# the 2021 value against live Energy UK data in July and recorded that this table must be reconciled
# or retired before anything calibrated against it; nothing had. It reached no caller, so no shipped
# figure moves -- but it is exactly the clean importable accessor a future build would have reached
# for as a calibration target, which is what §9 predicted and why it is corrected rather than left.
_UK_SWITCHING_RATE_PCT: dict[int, float] = {
    2016: 17.3, 2017: 13.8, 2018: 19.8, 2019: 21.0, 2020: 22.8,
    2021: 18.2, 2022: 3.6,  2023: 10.7, 2024: 14.3, 2025: 16.1,
}


def get_market_elec_rate(year: int) -> float:
    """Return UK average domestic electricity unit rate in p/kWh."""
    return _UK_AVG_ELEC_UNIT_RATE_P_KWH.get(year, _UK_AVG_ELEC_UNIT_RATE_P_KWH[2025])


def get_market_gas_rate(year: int) -> float:
    """Return UK average domestic gas unit rate in p/kWh."""
    return _UK_AVG_GAS_UNIT_RATE_P_KWH.get(year, _UK_AVG_GAS_UNIT_RATE_P_KWH[2025])


def get_switching_rate(year: int) -> float:
    """Return the GB domestic switching rate for `year`, as a percentage.

    THE BASIS TRAVELS WITH THE FIGURE (R14), because neither half is recoverable from it:
    external changes of supplier on a domestic ELECTRICITY meter point, over ALL domestic
    electricity accounts including those mid-fixed-term. It is NOT a supplier's book churn rate
    and it is NOT comparable with a rate measured over renewals only, which narrows the
    denominator to accounts at a decision point and reads about a third high.

    A year outside the published window falls back to 2025 rather than refusing. That is a
    fail-open shape and it is left alone deliberately: this accessor has no caller, and changing
    its contract belongs with the caller that first needs it, not with the table correction.
    """
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
