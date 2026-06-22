"""Phase 21a/27b/29a: Electricity policy cost pass-through.

Renewable Obligation (RO) and Contract for Difference (CfD) levies are
mandatory per-MWh costs on all UK electricity supply. They are not embedded
in Elexon SSP spot prices — a supplier pays them separately to Ofgem/LCCC.

Phase 27b adds Climate Change Levy (CCL) for business electricity customers.
Domestic tariffs are exempt from CCL; business (SME/I&C) customers pay the
main CCL rate on every kWh consumed. CCL is passed through in the business
unit rate and deducted at settlement — the supplier remits it to HMRC.

These lookup tables are derived from official Ofgem, EMR Settlement, and
HMRC sources (see docs/market_research/).

The supplier passes these costs through in the tariff: the policy cost is
added to the unit rate at contract pricing time, and deducted from gross margin
at settlement time. Net effect on margin is approximately zero when the tariff
pass-through exactly matches the levy — but diverges when the actual levy
differs from the estimate at pricing (e.g. the 2022 CfD rebate was unexpected).

Gas customers: RO and CfD levies are electricity-only. Domestic gas is also
exempt from CCL. This module returns 0.0 for gas.
"""

# RO effective cost floor (£/MWh) by obligation year start.
# Key = calendar year of April start of obligation year (Apr-Mar).
# Formula: obligation_level_ROCs_per_MWh × buy_out_price_per_ROC.
# Source: REF.org.uk obligation levels; Ofgem buy-out price publications.
_RO_COST_BY_OY_START: dict[int, float] = {
    2016: 15.6,   # OY 2016-17: 0.348 ROCs/MWh × £44.77
    2017: 18.6,   # OY 2017-18: 0.409 × £45.58
    2018: 22.1,   # OY 2018-19: 0.468 × £47.22
    2019: 23.6,   # OY 2019-20: 0.484 × £48.78
    2020: 23.6,   # OY 2020-21: 0.471 × £50.05
    2021: 25.0,   # OY 2021-22: 0.492 × £50.80
    2022: 26.0,   # OY 2022-23: 0.491 × £52.88
    2023: 27.7,   # OY 2023-24: 0.469 × £59.01
    2024: 31.8,   # OY 2024-25: 0.491 × £64.73
}

# CfD Interim Levy Rate annual average (£/MWh) by calendar year.
# Negative in 2022: wholesale prices exceeded CfD strike prices, so LCCC
# rebated suppliers. Source: EMR Settlement Ltd quarterly announcements.
_CFD_LEVY_BY_YEAR: dict[int, float] = {
    2016: 0.1,
    2017: 1.3,
    2018: 3.2,
    2019: 4.0,
    2020: 3.5,
    2021: 1.5,
    2022: -5.0,   # negative: crisis rebate to suppliers
    2023: 6.5,
    2024: 11.0,
}

# The RO obligation year runs Apr-Mar. For a contract starting in Jan-Mar,
# the applicable OY start is the prior year (e.g. Jan 2021 → OY 2020-21 → key 2020).
def _ro_oy_start_year(date_str: str) -> int:
    """Return the April-start year of the obligation year containing date_str."""
    year = int(date_str[:4])
    month = int(date_str[5:7])
    return year if month >= 4 else year - 1


def get_ro_cost_per_mwh(date_str: str) -> float:
    """Renewables Obligation effective cost (£/MWh) for the given date.

    Uses the obligation year that covers date_str. Falls back to the nearest
    known year for dates outside 2016-2024.
    """
    oy_year = _ro_oy_start_year(date_str)
    if oy_year in _RO_COST_BY_OY_START:
        return _RO_COST_BY_OY_START[oy_year]
    # Clamp to known range
    if oy_year < min(_RO_COST_BY_OY_START):
        return _RO_COST_BY_OY_START[min(_RO_COST_BY_OY_START)]
    return _RO_COST_BY_OY_START[max(_RO_COST_BY_OY_START)]


def get_cfd_levy_per_mwh(date_str: str) -> float:
    """CfD Interim Levy Rate (£/MWh) for the given date.

    Negative in 2022 (crisis rebate). Falls back to nearest year outside range.
    """
    year = int(date_str[:4])
    if year in _CFD_LEVY_BY_YEAR:
        return _CFD_LEVY_BY_YEAR[year]
    if year < min(_CFD_LEVY_BY_YEAR):
        return _CFD_LEVY_BY_YEAR[min(_CFD_LEVY_BY_YEAR)]
    return _CFD_LEVY_BY_YEAR[max(_CFD_LEVY_BY_YEAR)]


def get_electricity_policy_cost_per_mwh(date_str: str) -> float:
    """Total electricity policy cost (£/MWh): RO + CfD levy.

    For electricity customers only. Returns 0.0 for any other fuel.
    Excludes CCL — use get_ccl_per_mwh() separately for business customers.
    """
    return get_ro_cost_per_mwh(date_str) + get_cfd_levy_per_mwh(date_str)


# Phase 27b: Climate Change Levy (CCL) for business electricity customers.
# Domestic electricity is exempt from CCL (reduced rate = £0.00 since Apr 2001).
# Business electricity pays the main CCL rate, remitted to HMRC by the supplier.
# CCL year runs April-March (same as RO obligation year).
# Sources: HMRC Climate Change Levy rates tables.
_CCL_ELECTRICITY_RATE_BY_YEAR: dict[int, float] = {
    2016: 5.44,    # £/MWh: 0.544p/kWh × 100 / 100 = £5.44/MWh
    2017: 5.54,
    2018: 5.83,
    2019: 6.11,
    2020: 7.17,    # April 2020: step-change — electricity CCL raised as gas CCL frozen
    2021: 7.17,
    2022: 7.17,
    2023: 7.26,
    2024: 7.35,
}


# Phase 29a: Network charges (DUoS + TNUoS) for electricity customers.
# DUoS (Distribution Use of System) + TNUoS (Transmission Use of System)
# represent the single largest non-commodity cost component (~£32-46/MWh
# for residential/SME, 2016-2024). These are passed through in the tariff
# unit rate and recovered from the supplier's settlement payment.
#
# For residential/SME (LV connected): combined DUoS + TNUoS unit rate.
# Post-TCR (April 2023) TNUoS residual moved to fixed standing charge; the
# table retains the unit-rate equivalent for consistency.
#
# For I&C HV connected (C_IC1, C_IC2): DUoS only — TNUoS is Triad-based
# (tracked separately in simulation/triad.py as an annual lump exposure;
# NOT included here to avoid double-counting).
#
# Source: docs/market_research/historical_policy_costs_2016_2024.md Section 3
# and Ofgem Price Cap Annex 3 (post-2019).
_NETWORK_COST_RESI_SME_BY_YEAR: dict[int, float] = {
    2016: 35.0,  # TNUoS ~£13/MWh + DUoS ~£22/MWh (mid-range estimate)
    2017: 36.0,
    2018: 37.0,
    2019: 38.0,
    2020: 38.0,
    2021: 38.0,
    2022: 43.0,  # step-up: RIIO-ED2 transition + TCR reforms
    2023: 44.0,
    2024: 46.0,
}

# I&C HV DUoS only (TNUoS tracked separately via Triad mechanism)
_DUOS_IC_BY_YEAR: dict[int, float] = {
    2016: 11.0,
    2017: 11.0,
    2018: 11.5,
    2019: 12.0,
    2020: 12.0,
    2021: 12.0,
    2022: 13.0,
    2023: 13.5,
    2024: 14.0,
}


def get_electricity_network_cost_per_mwh(date_str: str, segment: str = "resi") -> float:
    """Network charge (DUoS + TNUoS) for electricity by year and customer segment.

    Residential/SME: combined DUoS + TNUoS unit rate (£32-46/MWh, 2016-2024).
    I&C HV: DUoS only (£11-14/MWh) — TNUoS is Triad-based, tracked in triad.py.
    Gas customers: returns 0.0 (gas network charges modelled separately or not at all).
    """
    year = int(date_str[:4])
    if segment == "I&C":
        table = _DUOS_IC_BY_YEAR
    else:
        table = _NETWORK_COST_RESI_SME_BY_YEAR
    if year in table:
        return table[year]
    if year < min(table):
        return table[min(table)]
    return table[max(table)]


def get_ccl_per_mwh(date_str: str, segment: str = "resi") -> float:
    """CCL (£/MWh) for business electricity.

    Returns 0.0 for domestic (resi) customers — domestic electricity is
    exempt from CCL under the reduced rate scheme.
    Returns the main CCL rate for SME, I&C, and all other non-domestic segments.
    Gas is not covered here (separate gas CCL rates apply; modelled as 0 for now).
    """
    if segment == "resi":
        return 0.0
    year = _ro_oy_start_year(date_str)  # CCL year also runs Apr-Mar
    if year in _CCL_ELECTRICITY_RATE_BY_YEAR:
        return _CCL_ELECTRICITY_RATE_BY_YEAR[year]
    if year < min(_CCL_ELECTRICITY_RATE_BY_YEAR):
        return _CCL_ELECTRICITY_RATE_BY_YEAR[min(_CCL_ELECTRICITY_RATE_BY_YEAR)]
    return _CCL_ELECTRICITY_RATE_BY_YEAR[max(_CCL_ELECTRICITY_RATE_BY_YEAR)]
