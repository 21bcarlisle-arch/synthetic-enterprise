"""Phase 21a/27b/29a/30a: Electricity policy cost pass-through.

Renewable Obligation (RO) and Contract for Difference (CfD) levies are
mandatory per-MWh costs on all UK electricity supply. They are not embedded
in Elexon SSP spot prices — a supplier pays them separately to Ofgem/LCCC.

Phase 27b adds Climate Change Levy (CCL) for business electricity customers.
Domestic tariffs are exempt from CCL; business (SME/I&C) customers pay the
main CCL rate on every kWh consumed. CCL is passed through in the business
unit rate and deducted at settlement — the supplier remits it to HMRC.

Phase 30a adds Capacity Market (CM) levy. Unlike CCL, CM applies to all demand
segments including domestic. Rate is highly variable (£0.5–7.3/MWh, 2016–2024)
reflecting auction clearing prices from 1–4 years prior.

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
    # Phase 29b: calibrated from Ofgem Annex 9 v1.10 (June 2026) "NC" row (£/customer/yr ÷ 3.1 MWh).
    # Includes DUoS + TNUoS + BSUoS + metering — the full network cost component as Ofgem models it.
    # Apr-Mar years mapped to calendar year of Q1 (the year the obligation year starts).
    2016: 43.0,   # 2016/17 est. (~£42-44/MWh based on Annex 9 trend)
    2017: 44.0,   # 2017/18: £43.67/MWh
    2018: 42.0,   # 2018/19: £42.41/MWh
    2019: 45.0,   # 2019/20: £44.96/MWh
    2020: 46.0,   # 2020/21: £45.89/MWh
    2021: 49.0,   # 2021/22: £49.42/MWh
    2022: 66.0,   # 2022/23: £66.24/MWh — BSUoS moved 100% to demand side Apr 2022
    2023: 75.0,   # 2023/24: £74.56/MWh — RIIO-ED2 commenced Apr 2023
    2024: 69.0,   # 2024/25: £68.95/MWh
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


# Phase 30a: Capacity Market (CM) levy for all electricity demand customers.
# CM applies universally — domestic (resi), SME, and I&C all pay. No exemption.
# Rate varies year-to-year based on auction clearing prices from 1-4 years prior.
# Source: Ofgem Annex 9 v1.8 (November 2025), CM row, £/customer/year ÷ 3.1 MWh benchmark.
# See docs/market_research/capacity_market_levy_2016_2024.md for full derivation.
_CM_LEVY_BY_YEAR: dict[int, float] = {
    2016: 0.5,   # 2016/17: TA auctions only, tiny volume. Pre-Annex 9 estimate.
    2017: 1.10,  # 2017/18: £3.41/cust/yr ÷ 3.1 MWh. First year in Annex 9.
    2018: 3.67,  # 2018/19: £11.36/cust/yr. First full T-4 delivery year.
    2019: 4.79,  # 2019/20: £14.85/cust/yr. T-4 at £18.00/kW.
    2020: 5.86,  # 2020/21: £18.18/cust/yr. T-4 at £22.50/kW.
    2021: 4.67,  # 2021/22: £14.49/cust/yr. Cheapest year — T-4 only £8.40/kW (2017 auction).
    2022: 3.37,  # 2022/23: £10.44/cust/yr. T-4 suspended; T-3 + small T-1 at £75/kW cap.
    2023: 5.68,  # 2023/24: £17.61/cust/yr. T-4 £15.97/kW + T-1 £60/kW.
    2024: 7.27,  # 2024/25: £22.54/cust/yr (H1 only). T-4 + T-1 at £35.79/kW.
}


def get_cm_levy_per_mwh(date_str: str) -> float:
    """Capacity Market levy (£/MWh) for any electricity demand customer.

    Applies to all segments (resi, SME, I&C) — no domestic exemption.
    Obligation year runs Apr-Mar, same as RO. Falls back to nearest known year.
    """
    oy_year = _ro_oy_start_year(date_str)
    if oy_year in _CM_LEVY_BY_YEAR:
        return _CM_LEVY_BY_YEAR[oy_year]
    if oy_year < min(_CM_LEVY_BY_YEAR):
        return _CM_LEVY_BY_YEAR[min(_CM_LEVY_BY_YEAR)]
    return _CM_LEVY_BY_YEAR[max(_CM_LEVY_BY_YEAR)]
