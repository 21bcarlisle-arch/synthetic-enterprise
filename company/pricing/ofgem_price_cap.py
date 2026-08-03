"""Ofgem Default Tariff Cap — domestic unit rate ceiling.

The Ofgem Default Tariff Cap (introduced Q4 2019) limits what licensed
suppliers can charge residential customers on variable and default tariffs.
Suppliers on fixed terms can also be subject to the cap when their locked
rate exceeds the prevailing cap level.

Source: Ofgem quarterly cap publications + Energy Price Guarantee (Oct 2022–Jun 2023).

CSS data (EDF/British Gas 2023-2024) confirms domestic supply was loss-making
under the cap 2021-2023. See docs/market_research/CSS_BENCHMARKS.md.

All values in £/MWh (excluding standing charge).
Electricity typical unit rate: Ofgem p/kWh × 10 = £/MWh.
Gas typical unit rate: Ofgem p/kWh × 10 = £/MWh.

TWO LOOKUPS, DELIBERATELY (W3_1b_intra_year_price_cap_granularity, 2026-08-03)
-----------------------------------------------------------------------------
``get_cap_unit_rate_gbp_per_mwh(fuel, year)`` — the ANNUAL blend. Kept for
callers whose own grain is a year (annual compliance anchors, growth mandates,
switching advice). Rich's direction for these: "ballpark + components right, not
year-on-year precision."

``get_cap_unit_rate_for_date(fuel, on_date)`` — the CAP-WINDOW lookup, keyed on
the window that actually contained that date. Required for anything that clamps a
settlement period or a term, because the real cap does not move on 1 January: it
moved every 6 months (Apr/Oct) to Sep-2022 and quarterly thereafter, and the
defining event of the crisis — the +54% step from £1,277 to £1,971 — landed on
**1 April 2022**. An annual blend puts a Jan-Mar 2022 deemed customer under the
305 £/MWh full-year average instead of the 208 £/MWh cap that really applied,
which loosens the ceiling by ~£97/MWh in exactly the quarter the squeeze bit.

Basis note (R14): the published unit rates below are Ofgem's typical-household
figures INCLUDING VAT at 5% and EXCLUDING standing charge — the same basis the
existing annual table and ``company/regulatory/price_cap.py`` are already on. The
standing-charge leg is a separate, declared simplification; the cap here is a
unit-rate ceiling only.
"""

from __future__ import annotations

from datetime import date

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


# --- Sub-annual cap-window schedule (W3_1b_intra_year_price_cap_granularity) ---
#
# The WINDOW BOUNDARIES are Ofgem's own published cap periods (six-monthly
# Apr/Oct from 1 Jan 2019 through 30 Sep 2022, quarterly from 1 Oct 2022):
#   https://www.ofgem.gov.uk/energy-regulation/domestic-and-non-domestic/
#     energy-pricing-rules/energy-price-cap/energy-price-cap-default-tariff-levels
# The UNIT RATES are the published typical-household p/kWh for each of those
# periods (electricityprices.org.uk's cap history, whose Oct-2021 20.8p/4.07p and
# Apr-2022 28.34p/7.37p are independently corroborated by the House of Commons
# Library CBP-9714 "20.8p → 28.3p electricity, 4.1p → 7.4p gas"), converted
# p/kWh × 10 → £/MWh.
#
# R13 WALL: every date and level here is real published regulatory history,
# sourced blind to company P&L. No value in this table may be moved because a
# simulation result looks wrong. Full sourcing: docs/market_research/
# ofgem_cap_windows.md.
#
# PORTABILITY: this is a schedule of (from, to, rates) tuples, not `if year ==
# 2022`. A second market or a changed regime supplies its own window list behind
# the same accessor.
#
# EPG: between Oct-2022 and Jun-2023 the Energy Price Guarantee held a typical
# dual-fuel bill at £2,500, well below the Ofgem cap (which peaked at £4,279 for
# Jan-Mar 2023). The binding domestic ceiling in those windows is therefore
# min(Ofgem cap, EPG), which is modelled as a separate overlay column rather than
# baked into one number, so the two instruments stay legible.
_CAP_WINDOWS: list[dict] = [
    # (effective_from, effective_to, elec £/MWh, gas £/MWh, elec EPG, gas EPG)
    {"from": date(2019, 1, 1), "to": date(2019, 3, 31), "elec": 165.2, "gas": 37.3},
    {"from": date(2019, 4, 1), "to": date(2019, 9, 30), "elec": 185.6, "gas": 41.4},
    {"from": date(2019, 10, 1), "to": date(2020, 3, 31), "elec": 178.5, "gas": 36.8},
    {"from": date(2020, 4, 1), "to": date(2020, 9, 30), "elec": 178.1, "gas": 35.0},
    {"from": date(2020, 10, 1), "to": date(2021, 3, 31), "elec": 171.9, "gas": 30.0},
    {"from": date(2021, 4, 1), "to": date(2021, 9, 30), "elec": 189.5, "gas": 33.4},
    # The Oct-2021 cap ran THROUGH 31 Mar 2022 — this is the window the annual
    # blend erases, and the one the crisis was fought in.
    {"from": date(2021, 10, 1), "to": date(2022, 3, 31), "elec": 208.0, "gas": 40.7},
    # +54% step, 1 Apr 2022 (£1,277 → £1,971 typical dual-fuel bill).
    {"from": date(2022, 4, 1), "to": date(2022, 9, 30), "elec": 283.4, "gas": 73.7},
    {"from": date(2022, 10, 1), "to": date(2022, 12, 31), "elec": 518.9, "gas": 147.6,
     "elec_epg": 340.0, "gas_epg": 103.2},
    {"from": date(2023, 1, 1), "to": date(2023, 3, 31), "elec": 674.7, "gas": 170.8,
     "elec_epg": 340.0, "gas_epg": 103.2},
    {"from": date(2023, 4, 1), "to": date(2023, 6, 30), "elec": 506.0, "gas": 126.1,
     "elec_epg": 340.0, "gas_epg": 103.2},
    {"from": date(2023, 7, 1), "to": date(2023, 9, 30), "elec": 301.1, "gas": 75.1},
    {"from": date(2023, 10, 1), "to": date(2023, 12, 31), "elec": 273.5, "gas": 68.9},
    {"from": date(2024, 1, 1), "to": date(2024, 3, 31), "elec": 286.2, "gas": 74.2},
    {"from": date(2024, 4, 1), "to": date(2024, 6, 30), "elec": 245.0, "gas": 60.4},
    {"from": date(2024, 7, 1), "to": date(2024, 9, 30), "elec": 223.6, "gas": 54.8},
    {"from": date(2024, 10, 1), "to": date(2024, 12, 31), "elec": 245.0, "gas": 62.4},
    {"from": date(2025, 1, 1), "to": date(2025, 3, 31), "elec": 248.6, "gas": 63.4},
    {"from": date(2025, 4, 1), "to": date(2025, 6, 30), "elec": 270.3, "gas": 69.9},
    {"from": date(2025, 7, 1), "to": date(2025, 9, 30), "elec": 257.3, "gas": 63.3},
    {"from": date(2025, 10, 1), "to": date(2025, 12, 31), "elec": 263.5, "gas": 62.9},
]

_CAP_FIRST_DAY = _CAP_WINDOWS[0]["from"]
_CAP_LAST_DAY = _CAP_WINDOWS[-1]["to"]


def get_cap_unit_rate_for_date(fuel: str, on_date: date) -> float | None:
    """Return the domestic cap unit-rate ceiling (£/MWh) in force ON a given date.

    fuel: 'electricity' or 'gas'.
    on_date: the settlement date (or term start) the ceiling is being applied to.

    Returns None when no cap applied (before 1 Jan 2019), else the binding
    ceiling — min(Ofgem cap, Energy Price Guarantee) where the EPG was in force.

    Dates beyond the last published window CARRY THE LAST WINDOW FORWARD rather
    than returning None: a None there would silently un-cap every resi customer,
    which is the FAIL-OPEN pattern R15 names. The cap is a standing statutory
    instrument, so "we have no published level yet" means "the last one still
    stands", never "there is no ceiling".

    Only applies to domestic (resi) customers — callers must filter by segment.
    """
    if fuel not in ("electricity", "gas"):
        return None
    if on_date < _CAP_FIRST_DAY:
        return None

    window = None
    for w in _CAP_WINDOWS:
        if w["from"] <= on_date <= w["to"]:
            window = w
            break
    if window is None:
        # Past the end of the published schedule — carry the last window forward.
        window = _CAP_WINDOWS[-1]

    key = "elec" if fuel == "electricity" else "gas"
    ofgem = window[key]
    epg = window.get(f"{key}_epg")
    return min(ofgem, epg) if epg is not None else ofgem
