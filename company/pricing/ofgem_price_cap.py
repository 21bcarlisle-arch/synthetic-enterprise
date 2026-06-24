"""Ofgem Default Tariff Cap — domestic unit rate ceiling.

The Ofgem Default Tariff Cap (introduced Q4 2019) limits what licensed
suppliers can charge residential customers on variable and default tariffs.
Suppliers on fixed terms can also be subject to the cap when their locked
rate exceeds the prevailing cap level.

Source: Ofgem quarterly cap publications + Energy Price Guarantee (Oct 2022–Jun 2023).
Simplified to annual averages. Rich's direction: "ballpark + components right,
not year-on-year precision."

CSS data (EDF/British Gas 2023-2024) confirms domestic supply was loss-making
under the cap 2021-2023. See docs/market_research/CSS_BENCHMARKS.md.

All values in £/MWh (excluding standing charge, excluding VAT).
Electricity typical unit rate: Ofgem p/kWh × 10 = £/MWh.
Gas typical unit rate: Ofgem p/kWh × 10 = £/MWh.
"""

# Electricity domestic unit rate cap (£/MWh), annual averages.
# Pre-2019: no cap (competitive market).
# Q4 2019 introduction at ~17p/kWh; raised significantly from Oct 2021 (gas crisis).
# 2022: EPG set at £2,500/yr typical (≈ 28-34p/kWh unit rate component).
# 2023: EPG → regular cap, normalising.
_ELEC_CAP_GBP_PER_MWH: dict[int, float] = {
    2019: 165.0,   # ~17p/kWh, Q4 2019 only (partial year, conservative)
    2020: 157.0,   # ~15.7p/kWh average
    2021: 183.0,   # ~17p/kWh H1, rose to ~20p/kWh Oct 2021
    2022: 305.0,   # Apr 2022 ~28p/kWh; EPG Oct 2022 ~30p/kWh equivalent
    2023: 265.0,   # EPG ~30p/kWh Q1-Q2; dropped to ~24-25p/kWh Q3-Q4
    2024: 210.0,   # Continuing normalisation ~20-22p/kWh
    2025: 190.0,   # ~19p/kWh approx
}

# Gas domestic unit rate cap (£/MWh), annual averages.
# Gas crisis drove gas cap from ~2.6p/kWh (2019) to ~7-10p/kWh (2022 peak).
_GAS_CAP_GBP_PER_MWH: dict[int, float] = {
    2019: 26.0,    # ~2.6p/kWh
    2020: 25.0,
    2021: 35.0,    # Gas crisis began Oct 2021, annual average elevated
    2022: 95.0,    # ~7-10p/kWh crisis peak; EPG in effect Q4
    2023: 70.0,    # EPG → lower cap, normalising
    2024: 55.0,    # ~5.5p/kWh
    2025: 52.0,
}

# Fallback for years beyond the table (cap assumed to continue post-2025)
_ELEC_CAP_FALLBACK = 190.0
_GAS_CAP_FALLBACK = 52.0


def get_cap_unit_rate_gbp_per_mwh(fuel: str, year: int) -> float | None:
    """Return Ofgem cap unit rate ceiling (£/MWh) for domestic customers.

    fuel: 'electricity' or 'gas'.
    year: calendar year of term start.

    Returns None when no cap applies (pre-2019), or a float ceiling in £/MWh.
    Callers should apply: unit_rate = min(unit_rate, cap) when cap is not None.

    Only applies to domestic (resi) customers — callers must filter by segment.
    Not applicable to I&C or SME customers.
    """
    if year < 2019:
        return None
    if fuel == "electricity":
        return _ELEC_CAP_GBP_PER_MWH.get(year, _ELEC_CAP_FALLBACK)
    if fuel == "gas":
        return _GAS_CAP_GBP_PER_MWH.get(year, _GAS_CAP_FALLBACK)
    return None
