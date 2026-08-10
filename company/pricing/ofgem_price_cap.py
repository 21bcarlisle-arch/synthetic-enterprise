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

THIS FILE HOLDS A READING, NOT THE LAW (KNIFE pass 3, B3, 2026-08-10)
---------------------------------------------------------------------
The window schedule below is no longer written here. It is LOADED from the
regulation commons — ``docs/domain_artefact_library/regulatory/
ofgem_default_tariff_cap_windows.json`` — which holds the published boundaries
and levels and nothing else.

What stays here is this company's READING of that law, and it is allowed to be
wrong: the carry-forward past the last published window, the ``min(Ofgem, EPG)``
selection, the segment filter, and the annual blend in
``get_cap_unit_rate_gbp_per_mwh``. The world enforces the cap from its OWN
reading of the same published artefact (``simulation/price_cap_enforcement.py``)
and the two are deliberately NOT pinned equal — a supplier that misreads the cap
is exactly what the regulation-commons doctrine keeps structurally possible.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

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
# THE SCHEDULE IS NOT WRITTEN HERE. It is the published law, and it lives in the
# regulation commons where every lane can read it. This company reads it here,
# with its own loader, and interprets it below with its own rules; the world
# reads the same file with its own loader in `simulation/price_cap_enforcement.py`.
#
# WHY THE COMMONS IS A DATA FILE AND NOT A SHARED MODULE. A shared Python module
# would have to live somewhere `tools/epistemic_wall.py` does not walk, and a
# route through an unwalked package moves the measurement rather than the
# dependency — the laundering this pass refused for the shape-A harnesses. A
# JSON artefact cannot express a dependency at all: it has no import statement to
# hide one in. That is why the unwalked home is safe HERE and was not safe there,
# and `tests/architecture/test_price_cap_commons.py` holds it to being data.
#
# R13 WALL: every date and level in that artefact is real published regulatory
# history, sourced blind to company P&L.
_CAP_WINDOWS_ARTEFACT = (
    Path(__file__).resolve().parents[2]
    / "docs" / "domain_artefact_library" / "regulatory"
    / "ofgem_default_tariff_cap_windows.json"
)


def _load_published_windows() -> list[dict]:
    """Read the published cap windows from the regulation commons.

    NO FAIL-OPEN PATH (R15). A missing, empty or malformed artefact raises. The
    tempting alternative — return `[]` and let the lookup fall through to
    "no cap" — would silently un-cap every domestic customer, which is the exact
    fail-open shape the carry-forward rule below was written to avoid.
    """
    if not _CAP_WINDOWS_ARTEFACT.exists():
        raise FileNotFoundError(
            f"Ofgem cap-window commons artefact missing: {_CAP_WINDOWS_ARTEFACT}. "
            "The published cap schedule is required; there is no uncapped default."
        )
    raw = json.loads(_CAP_WINDOWS_ARTEFACT.read_text())
    windows = raw.get("windows")
    if not windows:
        raise ValueError(
            f"Ofgem cap-window commons artefact has no windows: {_CAP_WINDOWS_ARTEFACT}"
        )
    parsed: list[dict] = []
    for w in windows:
        entry = {
            "from": date.fromisoformat(w["from"]),
            "to": date.fromisoformat(w["to"]),
            "elec": float(w["elec"]),
            "gas": float(w["gas"]),
        }
        for epg_key in ("elec_epg", "gas_epg"):
            if epg_key in w:
                entry[epg_key] = float(w[epg_key])
        parsed.append(entry)
    return sorted(parsed, key=lambda w: w["from"])


_CAP_WINDOWS: list[dict] = _load_published_windows()

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
