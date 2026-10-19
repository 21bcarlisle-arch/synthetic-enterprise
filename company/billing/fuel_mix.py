"""UK electricity fuel mix disclosure: the UK comparison mix a supplier shows its customers.

Suppliers must disclose their own fuel mix beside the UK one (Electricity (Fuel Mix Disclosure)
Regulations 2005, supply licence condition 21). This module holds the UK one, as DESNZ publishes it
in the *Fuel mix disclosure data table*, section "UK fuel mix ... (for comparison, including
estimate for imports)".

THIS IS THE SUPPLY BASIS, NOT THE GENERATION MIX. It counts electricity supplied, imports allocated
at the European Attribute Mix, over a 1 April to 31 March period. The grid's generation mix (DUKES
5.6.C, calendar year, no imports) is a different fact and lives in
`company/regulatory/carbon_emissions.py::UK_GRID_FUEL_MIX`. DESNZ's own note 5 says the two differ.
Until 2026-10-19 this table held a generation mix under the FMD heading. The sources, vintages and
what moved are in `docs/market_research/two_uk_electricity_fuel_mixes_generation_and_disclosure.md`,
whose `fuel-mix-sources` block this table is tested against.
"""

from __future__ import annotations

from typing import Optional

#: Keyed by the disclosure period's START year: 2024 is 1 April 2024 to 31 March 2025. One DESNZ
#: edition per period, read from the Internet Archive's captures of the GOV.UK page (which is
#: overwritten each year) and the live 2025/26 edition updated 2026-08-03.
#: 2016-2018 ARE ABSENT, NOT FILLED: no edition before 2019/20 was found (GAP on the page).
_FUEL_MIX_BY_YEAR: dict[int, dict[str, float]] = {
    2019: {"renewable": 37.9, "nuclear": 16.6, "gas": 39.4, "coal": 3.9, "other": 2.2},
    2020: {"renewable": 40.3, "nuclear": 16.1, "gas": 38.2, "coal": 2.7, "other": 2.7},
    2021: {"renewable": 38.7, "nuclear": 16.1, "gas": 38.5, "coal": 3.8, "other": 2.9},
    2022: {"renewable": 40.8, "nuclear": 13.9, "gas": 39.3, "coal": 3.4, "other": 2.6},
    2023: {"renewable": 43.2, "nuclear": 12.7, "gas": 35.0, "coal": 6.3, "other": 2.8},
    2024: {"renewable": 42.1, "nuclear": 16.2, "gas": 33.3, "coal": 5.9, "other": 2.5},
    2025: {"renewable": 48.0, "nuclear": 13.7, "gas": 31.4, "coal": 4.7, "other": 2.2},
}


def disclosure_period(year: int) -> str:
    """The period a key names, as the data table writes it: 2024 -> "2024/25"."""
    return f"{year}/{(year + 1) % 100:02d}"


def get_fuel_mix(year: int) -> Optional[dict[str, float]]:
    """The UK FMD mix for the period starting 1 April `year`, or None when no edition was fetched.

    It used to clamp a year outside the table to the nearest edge. That published 2016's mix for
    2010, and would now publish 2019/20's for 2016, a figure for a period nobody disclosed.
    """
    mix = _FUEL_MIX_BY_YEAR.get(year)
    return dict(mix) if mix is not None else None


def fuel_mix_summary(year: int) -> Optional[dict]:
    """Return fuel mix with derived fields for portal display, or None for an absent period.

    Includes: year, period, mix breakdown, renewable_pct, low_carbon_pct (renewable + nuclear),
    fossil_pct, trend vs prior period (None when the prior period is absent).
    """
    mix = get_fuel_mix(year)
    if mix is None:
        return None
    prior = get_fuel_mix(year - 1)

    renewable_pct = mix["renewable"]
    low_carbon_pct = mix["renewable"] + mix["nuclear"]
    fossil_pct = mix["gas"] + mix["coal"]

    renewable_trend = round(renewable_pct - prior["renewable"], 1) if prior else None

    return {
        "year": year,
        "period": disclosure_period(year),
        "mix": mix,
        "renewable_pct": round(renewable_pct, 1),
        "low_carbon_pct": round(low_carbon_pct, 1),
        "fossil_pct": round(fossil_pct, 1),
        "renewable_trend": renewable_trend,
        "trend_direction": (
            None if renewable_trend is None
            else "up" if renewable_trend > 0 else "down" if renewable_trend < 0 else "flat"
        ),
    }
