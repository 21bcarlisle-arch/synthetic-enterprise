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
it the difference. This tree states the scheme in the company's own words —
`company/regulatory/epg_reconciliation_register.py`, "HM Treasury paid suppliers
the difference between EPG rates and their [actual rates]".

THE WORLD NOW HAS ITS OWN RECEIPT LEG (2026-09-08):
`price_cap_enforcement.hmt_epg_receipt_gbp_per_mwh`, wired into every SVT segment
by `svt_product`, so a billed rate is recorded as the two receipts it was made of.
It is the WORLD's leg and not the company's register, because `simulation/` may
not import `company/` — the register is the supplier's audit trail behind the
wall and still has no production caller, which is separate filed work.

So there are two honest numbers for those three quarters and this accessor is the
CAP one, deliberately:

  * `simulation/svt_product.py` bills a default-tariff household at it, because
    that is the supplier's REVENUE and the receipt leg beside it says who paid.
    Returning 34.0p here would take roughly half the unit revenue out of the
    crisis quarters and call it fidelity, when a real GB supplier was made whole
    in exactly those quarters.
  * `simulation/competitor_reference.py` already documents its reading of this
    module as "the published cap series … the anchor and the ceiling".

  * THE HOUSEHOLD-FACING CONSUMERS ASK THE OTHER QUESTION and now have their own
    accessor: `get_svt_elec_rate_charged_to_household_gbp_per_mwh` below, landed
    2026-09-08 together with the receipt leg
    (`price_cap_enforcement.hmt_epg_receipt_gbp_per_mwh`, wired into every SVT
    segment by `svt_product`). The two had to land together: the accessor alone
    re-breaks billing, and the receipt leg alone leaves the churn reference
    reading the cap. An accessor that quietly answered the other question under
    THIS name would still be the same defect with the sign flipped, which is why
    the name is eight words long.

GAS HAS NO `charged_to_household` TWIN AND THAT IS A GAP, NOT A SYMMETRY CLAIM.
The EPG capped gas at 10.3p against a 17.08p cap, so the same 6.8p/kWh split
exists there. It is not built because it would have no caller: every consumer
re-pointed on 2026-09-08 — the price differential, the SVT position, the churn
basis reference — is electricity-only, and an accessor with no caller is an
orphan that reads as coverage. When a gas consumer appears, the twin is two lines
over `binding_cap_unit_rate_gbp_per_mwh_inc_vat` and this paragraph is its brief.

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


def get_svt_elec_rate_charged_to_household_gbp_per_mwh(date_str: str) -> float | None:
    """Return what a domestic default-tariff household was actually CHARGED per
    MWh of electricity on `date_str`, £/MWh inc-VAT, excluding standing charge.

    THE OTHER OF THE TWO NUMBERS. `get_svt_elec_rate_gbp_per_mwh` above answers
    what the tariff was priced at and what its supplier was compensated to; this
    answers what came out of the household's pocket. From 2022-10-01 to
    2023-06-30 they differ, reaching 33p/kWh in January 2023, and the difference
    is the HM Treasury receipt (`price_cap_enforcement.hmt_epg_receipt_gbp_per_mwh`).
    Everywhere else the two are the same number, which is why one accessor was
    enough for as long as nobody asked.

    ASK THIS ONE WHEN THE ANSWER IS ABOUT A HOUSEHOLD'S EXPERIENCE — what it pays,
    what it compares an offer against, whether its bill jumped. Ask the other when
    the answer is about the supplier's book — revenue, the ceiling a bill may not
    exceed, what a rival's default tariff was priced at.

    Delegates to the binding instrument, `min(Ofgem cap, EPG)`, because a
    household could not lawfully be charged above either — the world's reading of
    which instrument binds lives in one place and this is not it. The pre-cap
    years read the same table as the accessor above: before 2019 there was no cap
    and no EPG, so what the household paid and what the tariff was priced at were
    one number with nothing between them.

    Returns None before 2016 (no data), on the same rule as the cap accessor.
    """
    d = date.fromisoformat(date_str)
    if d.year < 2016:
        return None
    if d.year in _SVT_ELEC_PRECAP_PENCE_PER_KWH:
        return round(_SVT_ELEC_PRECAP_PENCE_PER_KWH[d.year] * 10, 2)
    from simulation.price_cap_enforcement import (
        binding_cap_unit_rate_gbp_per_mwh_inc_vat,
    )

    return binding_cap_unit_rate_gbp_per_mwh_inc_vat("electricity", d)


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
