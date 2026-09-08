"""Phase 39a: UK domestic SVT (Standard Variable Tariff) unit rates, BOTH FUELS.

WHAT THIS MODULE ANSWERS, SAID ONCE, BECAUSE IT ANSWERED TWO QUESTIONS WITH ONE
NUMBER UNTIL 2026-09-08: the PUBLISHED OFGEM DEFAULT TARIFF CAP unit rate on the
date given — the level a domestic default tariff was priced at, and the level a
supplier of one was compensated to. **It is not what the household was charged.**
Between 2022-10-01 and 2023-06-30 those are different numbers and the gap reaches
33p/kWh; THE EPG below is the whole of that story.

Unit: £/MWh, INCLUDING VAT at the published rate, excluding standing charge — the
basis the commons artefact declares, and the same basis for both fuels, because
this field is differenced against a unit rate downstream and a spread between two
bases is a number rather than a quantity.

NEITHER FUEL IS A TABLE FOR THE CAPPED YEARS. Both delegate to
`simulation/price_cap_enforcement`, which reads the regulation commons. Only the
PRE-2019 years are tables here, because before January 2019 there was no cap to
read and the rate was supplier discretion.

THE EPG, AND WHY THIS ACCESSOR DOES NOT RETURN IT (2026-09-08)
---------------------------------------------------------------
The Energy Price Guarantee held a household's unit rate at 34.0p/kWh from
2022-10-01 to 2023-06-30 while the Ofgem cap ran to 67.47p. It did that WITHOUT
reducing supplier revenue: the supplier billed the EPG rate and HM Treasury paid
it the difference. This tree already states the scheme —
`company/regulatory/epg_reconciliation_register.py`, "HM Treasury paid suppliers
the difference between EPG rates and their [actual rates]" — and that register has
no production caller, so the world has no HMT receipt leg.

So there are two honest numbers for those three quarters and this accessor is the
CAP one, deliberately:

  * `simulation/svt_product.py` bills a default-tariff household at it. With no
    subsidy leg wired, returning 34.0p here would take roughly half the unit
    revenue out of the crisis quarters and call it fidelity, when a real GB
    supplier was made whole in exactly those quarters.
  * `simulation/competitor_reference.py` already documents its reading of this
    module as "the published cap series … the anchor and the ceiling".

  * WHAT IS THEREFORE STILL WRONG, NAMED RATHER THAN IMPLIED: the household-facing
    consumers — `customer_events._price_differential_vs_market`, the churn
    reference — want what the household PAID, and get the cap. The repair is the
    HMT leg plus a second accessor over
    `price_cap_enforcement.binding_cap_unit_rate_gbp_per_mwh_inc_vat`, which is
    filed work and not a line to add here. An accessor that quietly answered the
    other question would be the same defect with the sign flipped.

R13: every value reaching this module is published regulatory history, sourced
blind to company P&L.
"""

from __future__ import annotations

from datetime import date

#: The published cap-period start months. THE HOME OF THIS TUPLE, imported by
#: `simulation/svt_product.py` for its billing segments rather than restated
#: there — until 2026-09-08 that module carried its own copy and a comment
#: claiming `test_the_segment_starts_match_the_published_series` guarded the two,
#: a control that has never existed in this tree. Deleting the duplication beats
#: guarding it; what IS now controlled, and could not be before, is that these
#: months cover every boundary the commons publishes
#: (`test_the_elec_svt_leg_reads_the_commons.py`).
CAP_PERIOD_START_MONTHS: tuple[int, ...] = (1, 4, 7, 10)

#: Pre-cap electricity SVT (p/kWh), 2016–2018. MIDPOINTS of the reported ranges,
#: the same treatment `_SVT_GAS_PRECAP_PENCE_PER_KWH` applies to its own years:
#: 14.0 is the midpoint of the ~13.5–14.5 in
#: `docs/market_research/svt_rates_active_passive_2016_2025.md` §1. The source
#: states ±15% and M confidence. Carried per YEAR and not per quarter because the
#: figures were only ever annual — the quarterly keys this table used to have were
#: three real values wearing twelve slots.
_SVT_ELEC_PRECAP_PENCE_PER_KWH: dict[int, float] = {
    2016: 14.00,
    2017: 14.00,
    2018: 15.25,
}


def get_svt_elec_rate_gbp_per_mwh(date_str: str) -> float | None:
    """Return the domestic electricity default-tariff CAP unit rate in £/MWh,
    inc-VAT — see the module docstring for which of the two 2022–23 numbers this
    is, and which it is not.

    Returns None before 2016 (no data). Never None merely because the published
    cap schedule has run out: the commons carries the standing instrument
    forward, and that is its rule to make rather than this module's — which is
    also why the invented "moderate decline as renewables penetration rises"
    series that used to stand at 2026–2029 is gone. It stood exactly where the
    commons publishes Ofgem's own cap level model.
    """
    d = date.fromisoformat(date_str)
    if d.year < 2016:
        return None
    if d.year in _SVT_ELEC_PRECAP_PENCE_PER_KWH:
        return round(_SVT_ELEC_PRECAP_PENCE_PER_KWH[d.year] * 10, 2)
    # Imported at call time for the same reason the gas leg does it: the commons
    # artefact is read from disk on first use.
    from simulation.price_cap_enforcement import (
        ofgem_cap_unit_rate_gbp_per_mwh_inc_vat,
    )

    return ofgem_cap_unit_rate_gbp_per_mwh_inc_vat("electricity", d)


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
#: same treatment `_SVT_ELEC_PRECAP_PENCE_PER_KWH` already applies to its own 2016–2018
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

    THE OFGEM CAP ROW, NOT THE BINDING INSTRUMENT, since 2026-09-08 and for the
    same reason the electricity leg gives. Until today this leg read
    `binding_cap_unit_rate_gbp_per_mwh_inc_vat`, so across 2022-10-01..2023-06-30
    it answered the EPG-bound 103.2 while the electricity leg answered the cap:
    one field, two questions, differing only in the three quarters that matter
    most, and nothing able to notice. Both fuels answer the cap now. That is a
    value move for gas in those three windows and it is recorded as one.

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
        ofgem_cap_unit_rate_gbp_per_mwh_inc_vat,
    )

    return ofgem_cap_unit_rate_gbp_per_mwh_inc_vat("gas", d)
