"""Phase 39a: UK domestic SVT (Standard Variable Tariff) unit rates, BOTH FUELS.

Rates sourced from Ofgem Default Tariff Cap quarterly updates.
Unit: pence per kWh (convert × 10 for £/MWh).

Electricity is a table here. GAS is not, and the block above
`get_svt_gas_rate_gbp_per_mwh` says why: the published gas cap already has a home
in the regulation commons, and this module reads it rather than restating it.

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


# ---------------------------------------------------------------------------
# GAS. Added 2026-09-06, and the reason it was missing is worth more than the
# series.
#
# Three surfaces stated, as an honest gap, that no published gas equivalent
# existed: this module's own electricity-only docstring, `run_phase2b`'s
# account-state writer ("ELECTRICITY ONLY, and that is the honest shape rather
# than a gap"), and `tools/r1_inference_ceiling.py`'s field-scope declaration
# ("because `simulation/svt_rates` publishes no gas equivalent"). All three were
# true of THIS FILE and none of them was true of the tree. The Ofgem Default
# Tariff Cap has always covered both fuels — the Act names both in its title —
# and the world's own regulation commons,
# `docs/domain_artefact_library/regulatory/ofgem_default_tariff_cap_windows.json`,
# has carried the gas leg per published window since W3_1b, at the SAME
# granularity as electricity, read by `simulation/price_cap_enforcement.py`.
#
# Measured cost of the gap, on `docs/reports/run_output_latest.json`: 449 of the
# 2,098 account-state rows are gas, and every one of them carried
# `svt_rate_gbp_per_mwh = None`. 105 households had the field for no term at all,
# and every one of the 105 is gas-only.
#
# SO THE POST-CAP LEG IS NOT WRITTEN HERE. It is delegated to the commons, which
# is where the law lives; restating it would make a second home for a number that
# already has one, and the two would drift. Only the PRE-CAP years are a table,
# because before January 2019 there was no cap to read and the rate was supplier
# discretion — exactly the basis on which this module's own 2016–2018 electricity
# figures are carried.
#
# BASIS: £/MWh INCLUDING VAT at the domestic 5% rate, excluding standing charge —
# the published basis, the same one the electricity series above is on, and the
# one `binding_cap_unit_rate_gbp_per_mwh_inc_vat` declares. Both fuels on one
# basis is the whole point: this field is differenced against a unit rate
# downstream, and a spread between two bases is a number rather than a quantity.
#
# R13: sourced blind to company P&L, from the published record only.
# ---------------------------------------------------------------------------

#: Pre-cap gas SVT (p/kWh), 2016–2018. MIDPOINTS of the published ranges in
#: `docs/market_research/svt_rates_active_passive_2016_2025.md` §1, which is the
#: same treatment `_SVT_ELEC_PENCE_PER_KWH` already applies to its own 2016–2018
#: rows (14.0 is the midpoint of that table's ~13.5–14.5). Back-derived from BEIS
#: QEP bills + Ofgem SVT league tables; the source states ±15% and M confidence,
#: and that band is asserted rather than described by
#: `tests/simulation/test_svt_rates.py`.
#:   2016  ~3.8–4.2  -> 4.00
#:   2017  ~2.1–3.5  -> 2.80   (the source notes a Q4 low of 2.07p)
#:   2018  ~3.5–4.0  -> 3.75
_SVT_GAS_PRECAP_PENCE_PER_KWH: dict[int, float] = {
    2016: 4.00,
    2017: 2.80,
    2018: 3.75,
}


def get_svt_gas_rate_gbp_per_mwh(date_str: str) -> float | None:
    """Return the domestic gas SVT/default-tariff unit rate in £/MWh, inc-VAT.

    Returns None before 2016 (no data), exactly as the electricity accessor does.
    Never None merely because the published cap schedule has run out — the
    commons carries the standing instrument forward, and that is its rule to
    make rather than this module's.

    THE FUEL IS THE ARGUMENT-LESS PART. There is deliberately no
    `get_svt_rate(fuel, date)` dispatcher here: the two fuels are answered by
    different instruments (a pre-cap estimate versus a published ceiling) for
    different spans, and a single accessor would hide which one a caller got.
    """
    d = date.fromisoformat(date_str)
    if d.year < 2016:
        return None
    if d.year in _SVT_GAS_PRECAP_PENCE_PER_KWH:
        return round(_SVT_GAS_PRECAP_PENCE_PER_KWH[d.year] * 10, 2)
    # Imported at call time, not at module import: `price_cap_enforcement` reads
    # the commons artefact from disk on first use, and this module is imported by
    # loops that never ask about gas.
    from simulation.price_cap_enforcement import (
        binding_cap_unit_rate_gbp_per_mwh_inc_vat,
    )

    return binding_cap_unit_rate_gbp_per_mwh_inc_vat("gas", d)
