"""Non-commodity bill components — Phase 9a / Phase 78.

UK retail energy bills contain two broad categories:
  1. Commodity: wholesale cost + hedging capital + margin (already modelled)
  2. Non-commodity: network charges (DUoS/TNUoS/BSUoS), environmental and
     policy levies (RO, FiT, CfD, CM, SM), plus VAT

Non-commodity charges are pass-throughs — the supplier collects them from
the customer and remits them to network operators and government. Zero margin
on these components. They are excluded from gross/net margin calculations but
must appear on customer bills.

Standing charges (£/day) are pure supplier revenue — they cover metering,
data services, and admin. They DO contribute to margin.

Phase 78: year-indexed non-commodity rates matching the settlement layer
(Phase 29b). The 2022 energy crisis drove DUoS/TNUoS up sharply; flat
2019 constants under-billed customers by ~£18/MWh in the peak crisis year.

Sources: Ofgem Retail Market Monitoring, Cornwall Insight, BEIS energy stats.
"""

# Year-indexed electricity non-commodity rate for resi (£/MWh).
# Includes: DUoS, TNUoS, BSUoS, RO, FiT, CfD, CM, Smart Metering.
# Source: Ofgem Retail Market Monitoring / Cornwall Insight network cost data.
_NON_COMMODITY_ELEC_RESI_BY_YEAR: dict[int, float] = {
    2016: 52.0,
    2017: 54.0,
    2018: 53.0,
    2019: 55.0,
    2020: 57.0,
    2021: 62.0,
    2022: 73.0,  # DUoS/TNUoS spiked during crisis; levy stack elevated
    2023: 80.0,  # CM + RO obligations at peak
    2024: 74.0,
}

# SME elec multiplier vs resi: lower levy burden, some DUoS variation.
_SME_ELEC_MULTIPLIER = 0.77

# Year-indexed gas non-commodity rate for resi (£/MWh).
# Includes: GDN transportation, NTS charges, metering.
_NON_COMMODITY_GAS_RESI_BY_YEAR: dict[int, float] = {
    2016: 9.0,
    2017: 9.5,
    2018: 10.0,
    2019: 11.0,
    2020: 11.0,
    2021: 12.0,
    2022: 15.0,
    2023: 16.0,
    2024: 14.0,
}

# SME gas multiplier vs resi.
_SME_GAS_MULTIPLIER = 0.80

# Flat fallback rates (2019 baseline) — used when year is not provided.
NON_COMMODITY_RATE_GBP_PER_MWH: dict[str, float] = {
    "resi": 55.0,
    "SME": 42.0,
}
NON_COMMODITY_GAS_RATE_GBP_PER_MWH: dict[str, float] = {
    "resi": 10.0,
    "SME": 8.0,
}

# Standing charge by commodity and segment (£/day).
# Covers: metering data collection, supply point admin, network standing.
#
# FALLBACK-ONLY as of the standing-charge double-count fix (2026-07-11): the
# AUTHORITATIVE standing charge is the year-calibrated, Ofgem-sourced value the
# settlement engines fold into every record and expose as its own field
# (`standing_charge_gbp` / `gas_standing_charge_gbp`, from
# simulation/policy_costs.py). saas/bill_generator.generate_bill() now SOURCES
# the bill's standing charge from those record fields; this flat table is used
# only when a record genuinely lacks that field (synthetic/legacy test
# fixtures pre-dating Phase 62). It is deliberately NOT year-varying and MUST
# NOT be treated as a second authoritative source for a real bill.
#
# I&C is listed EXPLICITLY as 0.0 (matching both real settlement engines, which
# return 0.0 for I&C -- capacity/transportation charges are handled via BSC
# settlement, not a per-day standing charge). Before this fix standing_charge_
# rate()'s numeric default silently charged I&C the resi 0.27 rate -- the exact
# missing-segment-key class BILL_CORRECTNESS_ADDENDUM.md Defect 1 fixed for
# VAT_RATE. Every real segment must appear here explicitly; see
# test_standing_charge_rate_never_silently_defaults_a_segment.
STANDING_CHARGE_GBP_PER_DAY: dict[str, dict[str, float]] = {
    "electricity": {"resi": 0.27, "SME": 0.55, "I&C": 0.0},
    "gas": {"resi": 0.25, "SME": 0.40, "I&C": 0.0},
}

# VAT rate by segment.
# UK: 5% reduced rate for domestic energy, 20% standard rate for business.
# BILL_CORRECTNESS_ADDENDUM.md Defect 1 (2026-07-08): "I&C" was missing from
# this dict, so vat_rate()'s fallback silently charged I&C accounts the
# domestic 5% rate instead of the legally-required 20% business rate --
# same incoherence class as the C6 SME-rendered-as-Household label bug,
# found while sweeping for it. Every non-domestic segment must be listed
# explicitly here; see test_vat_rate_never_silently_defaults_a_business_segment.
VAT_RATE: dict[str, float] = {
    "resi": 0.05,
    "SME": 0.20,
    "I&C": 0.20,
}


def non_commodity_rate(commodity: str, segment: str, year: int | None = None) -> float:
    """Return the non-commodity pass-through unit rate (£/MWh).

    When year is provided, returns the year-indexed rate. Falls back to the
    flat 2019 baseline when year is None or outside the indexed range.
    """
    if commodity == "gas":
        if year is not None and year in _NON_COMMODITY_GAS_RESI_BY_YEAR:
            resi_rate = _NON_COMMODITY_GAS_RESI_BY_YEAR[year]
            if segment == "SME":
                return resi_rate * _SME_GAS_MULTIPLIER
            return resi_rate
        return NON_COMMODITY_GAS_RATE_GBP_PER_MWH.get(segment, NON_COMMODITY_GAS_RATE_GBP_PER_MWH["resi"])
    # electricity
    if year is not None and year in _NON_COMMODITY_ELEC_RESI_BY_YEAR:
        resi_rate = _NON_COMMODITY_ELEC_RESI_BY_YEAR[year]
        if segment == "SME":
            return resi_rate * _SME_ELEC_MULTIPLIER
        return resi_rate
    return NON_COMMODITY_RATE_GBP_PER_MWH.get(segment, NON_COMMODITY_RATE_GBP_PER_MWH["resi"])


def standing_charge_rate(commodity: str, segment: str) -> float:
    """Return the FALLBACK flat standing charge (£/day).

    FALLBACK ONLY. The authoritative standing charge for a real bill is the
    year-calibrated value on each settlement record (see
    STANDING_CHARGE_GBP_PER_DAY docstring); generate_bill() reads that field
    directly and only calls this when a record carries no such field.

    Every real segment (resi, SME, I&C) is listed explicitly in
    STANDING_CHARGE_GBP_PER_DAY, so no real segment hits the numeric fallback
    below. The resi rate remains the fallback for a genuinely unknown segment,
    but a NEW business segment MUST add itself explicitly (see
    test_standing_charge_rate_never_silently_defaults_a_segment) rather than
    silently inherit the domestic rate -- the exact class of bug fixed here for
    I&C (previously defaulted to the resi 0.27 rate).
    """
    commodity_rates = STANDING_CHARGE_GBP_PER_DAY.get(
        commodity, STANDING_CHARGE_GBP_PER_DAY["electricity"]
    )
    return commodity_rates.get(segment, commodity_rates["resi"])


def vat_rate(segment: str) -> float:
    """Return the VAT rate (0.05 or 0.20)."""
    return VAT_RATE.get(segment, VAT_RATE["resi"])
