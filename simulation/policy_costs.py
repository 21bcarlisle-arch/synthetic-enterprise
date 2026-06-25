"""Phase 21a/27b/29a/30a/31a/30b: Electricity and gas policy cost pass-through.

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

Gas customers: RO, CfD, CM, and FiT levies are electricity-only. Domestic gas
is also exempt from electricity CCL. Phase 30b adds gas-side costs: gas CCL
(for non-domestic gas), gas network charges (GDN + NTS), and Green Gas Levy.
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


# Phase 31a: Feed-in Tariff (FiT) levelisation levy for all electricity demand customers.
# FiT is collected from all licensed suppliers proportional to their share of total GB
# electricity supply — no domestic exemption, no I&C exemption. All segments pay the same
# £/MWh rate. Obligation year runs Apr-Mar (same as RO).
#
# Two source streams cross-checked:
#   - 2021–2024: npower Business Solutions supplier pass-through schedule (authoritative)
#     "reconciled" rates are final settled figures; 2024 is initial billing (TBC Nov 2026)
#   - 2016–2020: total scheme cost (Ofgem FiT Annual Reports) ÷ ~245 TWh supply basis
#     245 TWh backed out from known 2023/24 reconciliation: £1,858m ÷ 0.763 p/kWh = 243 TWh
#
# Key pattern: rising 2016→2020 as fleet matured; dip 2021/22 (lower tariff rates on newer
# installs entering scheme); rising again 2022-2025 as RPI indexation exceeds generation decline.
# Contrast with CM: FiT less volatile (range £4-9/MWh vs CM £0.5-7.3/MWh).
#
# See docs/market_research/fit_levy_2016_2024.md for full derivation.
_FIT_LEVY_BY_YEAR: dict[int, float] = {
    2016: 4.10,   # 2016/17: ~£1.05bn ÷ ~245 TWh. Triangulated from cumulative total (£18.23bn through SY15).
    2017: 5.00,   # 2017/18: ~£1.25bn. Scheme growing; pre-2016 tariff cuts limiting new capacity additions.
    2018: 5.80,   # 2018/19: ~£1.45bn. FiT closed to new large sites Oct 2019; all applicants Jan 2020.
    2019: 6.40,   # 2019/20: £1.60bn — SY11 report states SY11 was £159m above SY10 → SY10 = £1.60bn.
    2020: 7.10,   # 2020/21: £1.76bn direct from Ofgem SY11 Annual Report.
    2021: 6.01,   # 2021/22: npower reconciled 0.601 p/kWh. Dip: lower generation tariffs on post-2016 installs.
    2022: 7.25,   # 2022/23: npower reconciled 0.725 p/kWh.
    2023: 7.63,   # 2023/24: npower reconciled 0.763 p/kWh. Ofgem SY14 confirms £1.858bn total.
    2024: 8.47,   # 2024/25: npower initial billing 0.847 p/kWh (reconciliation due Nov 2026).
}


def get_fit_levy_per_mwh(date_str: str) -> float:
    """Feed-in Tariff (FiT) levelisation levy (£/MWh) for electricity demand.

    Applies to all segments (resi, SME, I&C) — no domestic exemption.
    Obligation year runs Apr-Mar, same as RO. Falls back to nearest known year.
    Source: npower reconciled rates 2021-2024 (high confidence);
            Ofgem FiT Annual Reports 2019-2020 (medium confidence);
            triangulated from cumulative totals for 2016-2018 (low-medium confidence).
    """
    oy_year = _ro_oy_start_year(date_str)
    if oy_year in _FIT_LEVY_BY_YEAR:
        return _FIT_LEVY_BY_YEAR[oy_year]
    if oy_year < min(_FIT_LEVY_BY_YEAR):
        return _FIT_LEVY_BY_YEAR[min(_FIT_LEVY_BY_YEAR)]
    return _FIT_LEVY_BY_YEAR[max(_FIT_LEVY_BY_YEAR)]



# --- Phase 54: Supplier mutualization levy (2021-2022 failure wave) ---

# When a UK electricity supplier fails, Ofgem appoints a Supplier of Last Resort (SoLR).
# Shortfalls in the failed supplier's Renewable Obligation (RO) certificates, CfD levies,
# and BSC charges are recovered from remaining suppliers pro-rata to their electricity volumes.
#
# Industry mutualization costs (calendar year basis, Ofgem/Elexon published figures):
#   2021: ~£1.2bn recovered across 17 major SoLR events (Peoples Energy, PfP Energy, etc.)
#         GB electricity demand ~290TWh → ~£4.14/MWh average across all suppliers
#   2022: ~£2.9bn (major events: Bulb SoLR scheme, Elexon BSC shortfall recovery)
#         GB electricity demand ~290TWh → ~£10.00/MWh
#   2023: ~£0.4bn (residual Bulb/SoLR cleanup; Special Administration Regime wind-down)
#         GB electricity demand ~290TWh → ~£1.38/MWh
# All other years 2016-2020: negligible mutualization (no material supplier failures).
# 2024 onward: normalising as crisis period passes; no major events.
#
# Source: Ofgem Compliance and Enforcement Bulletins; Elexon BSC Audit Committee reports;
#         NAO "Energy supplier failures" report Nov 2022; Ofgem SoLR cost publications.
_MUTUALIZATION_LEVY_BY_YEAR: dict[int, float] = {
    2016: 0.00,
    2017: 0.00,
    2018: 0.00,
    2019: 0.00,
    2020: 0.00,
    2021: 4.14,   # £/MWh — 17 SoLR events; RO shortfall dominated
    2022: 10.00,  # £/MWh — Bulb Special Administration + BSC clearing shortfalls
    2023: 1.38,   # £/MWh — residual SAR wind-down; Bulb sale to Octopus April 2023
    2024: 0.20,   # £/MWh — minimal residual (normalising post-crisis)
}


def get_mutualization_levy_per_mwh(date_str: str) -> float:
    """Supplier mutualization levy (£/MWh) for electricity demand.

    Pro-rata recovery of failed supplier obligations levied on remaining
    licensed electricity suppliers based on their metered volumes.
    Applies to all electricity demand segments (resi, SME, I&C).
    Only electricity — gas SoLR costs are recovered separately via Xoserve/Ofgem.
    Falls back to nearest known year for out-of-range dates.
    """
    year = int(date_str[:4])
    if year in _MUTUALIZATION_LEVY_BY_YEAR:
        return _MUTUALIZATION_LEVY_BY_YEAR[year]
    if year < min(_MUTUALIZATION_LEVY_BY_YEAR):
        return _MUTUALIZATION_LEVY_BY_YEAR[min(_MUTUALIZATION_LEVY_BY_YEAR)]
    return _MUTUALIZATION_LEVY_BY_YEAR[max(_MUTUALIZATION_LEVY_BY_YEAR)]


# --- Phase 30b: Gas-side policy costs ---

# Gas CCL (Climate Change Levy) rates by obligation year start (April-March).
# Source: HMRC Environmental Taxes Bulletin historical rates (H confidence).
# Key: domestic (resi) gas is EXEMPT — only I&C and SME pay gas CCL.
# Pattern: frozen at £2.03/MWh 2016-2018, then rose sharply from 2019 as
# government rebalanced gas/electricity CCL toward parity (reached April 2024).
_GAS_CCL_RATE_BY_YEAR: dict[int, float] = {
    2016: 1.95,   # 0.195 p/kWh — HMRC Table 1
    2017: 1.98,   # 0.198 p/kWh
    2018: 2.03,   # 0.203 p/kWh
    2019: 3.39,   # 0.339 p/kWh — Budget 2016 rebalancing policy started
    2020: 4.06,   # 0.406 p/kWh
    2021: 4.65,   # 0.465 p/kWh
    2022: 5.68,   # 0.568 p/kWh
    2023: 6.72,   # 0.672 p/kWh
    2024: 7.75,   # 0.775 p/kWh — parity with electricity CCL from April 2024
}


def get_gas_ccl_per_mwh(date_str: str, segment: str = "resi") -> float:
    """Gas CCL (£/MWh) for non-domestic gas consumption.

    Domestic gas is exempt (zero CCL). I&C and SME pay the main gas CCL rate.
    CCL year runs April-March, same as electricity CCL and RO.
    Falls back to nearest known year for out-of-range dates.
    """
    if segment == "resi":
        return 0.0
    year = _ro_oy_start_year(date_str)
    if year in _GAS_CCL_RATE_BY_YEAR:
        return _GAS_CCL_RATE_BY_YEAR[year]
    if year < min(_GAS_CCL_RATE_BY_YEAR):
        return _GAS_CCL_RATE_BY_YEAR[min(_GAS_CCL_RATE_BY_YEAR)]
    return _GAS_CCL_RATE_BY_YEAR[max(_GAS_CCL_RATE_BY_YEAR)]


# Gas network charges (GDN distribution + NTS transmission), £/MWh, all on unit rate.
# Confidence: M — derived from Ofgem price cap network cost % share × cap unit rates.
# Gas network costs sit entirely in the unit rate (no standing charge component for
# network, unlike electricity where standing charge carries network costs).
# Post-2021: RIIO-GD2 price control began Apr 2021; SOLR costs socialised from 2021/22.
# 2023/24 step-up reflects RIIO-GD2 allowed revenue increases + SOLR cost recovery.
_GAS_NETWORK_COST_BY_YEAR: dict[int, float] = {
    2016: 9.9,    # ~26% × 3.8 p/kWh pre-cap market rate
    2017: 9.9,    # similar pre-cap regime
    2018: 9.6,    # ~26% × 3.7 p/kWh
    2019: 10.0,   # ~27% × 3.7 p/kWh; stable RIIO-GD1
    2020: 9.0,    # ~28% × 3.2 p/kWh; RIIO-GD1 final year
    2021: 10.3,   # ~25% × 4.1 p/kWh; RIIO-GD2 started Apr 2021
    2022: 11.0,   # network fixed while wholesale spiked; crisis year
    2023: 17.6,   # RIIO-GD2 + SOLR cost socialisation; ~22% × £8.0/kWh avg cap rate
    2024: 14.3,   # ~22% × £6.5/kWh avg; post-crisis normalisation
}


def get_gas_network_cost_per_mwh(date_str: str) -> float:
    """Gas network charges (GDN + NTS, £/MWh) — applies to all gas customers.

    Gas network costs are entirely on the unit rate (no standing charge component).
    No segment exemptions — resi, SME, and I&C all pay the same unit-rate charge.
    Falls back to nearest known year.
    """
    year = _ro_oy_start_year(date_str)
    if year in _GAS_NETWORK_COST_BY_YEAR:
        return _GAS_NETWORK_COST_BY_YEAR[year]
    if year < min(_GAS_NETWORK_COST_BY_YEAR):
        return _GAS_NETWORK_COST_BY_YEAR[min(_GAS_NETWORK_COST_BY_YEAR)]
    return _GAS_NETWORK_COST_BY_YEAR[max(_GAS_NETWORK_COST_BY_YEAR)]


# Green Gas Levy (GGL) — annual rate per meter point (MPRN), £/meter/year.
# Introduced 30 Nov 2021 to fund the Green Gas Support Scheme (biomethane).
# Charged per active meter (not per kWh) — normalised to £/MWh via customer AQ.
# Source: DESNZ GOV.UK GGL rates publications (H confidence).
# Rate structure: Year 1/2 (Nov 2021–Mar 2023) same rate; then fell sharply as
# scheme attracted fewer biomethane projects than modelled.
_GGL_RATE_GBP_PER_METER_YEAR: dict[int, float] = {
    # OY key = Apr-start year; GGL started mid-OY-2021 (Nov 2021)
    2021: 0.576 * 365 / 100,   # Nov 2021 – Mar 2022: 0.576 p/meter/day = £2.10/yr
    2022: 0.576 * 365 / 100,   # Apr 2022 – Mar 2023: same rate (Year 2)
    2023: 0.122 * 365 / 100,   # Apr 2023 – Mar 2024: 0.122 p/meter/day = £0.45/yr
    2024: 0.105 * 365 / 100,   # Apr 2024 – Mar 2025: 0.105 p/meter/day = £0.38/yr
}


def get_ggl_per_mwh(date_str: str, aq_kwh: float) -> float:
    """Green Gas Levy (£/MWh), normalised to the customer's annual quantity.

    GGL is a per-MPRN daily charge (not per kWh). Converting to £/MWh using the
    customer's AQ preserves the settlement convention: ggl_per_mwh × daily_mwh =
    annual_rate / 365 (the correct per-day charge regardless of consumption shape).
    Returns 0 for dates before 30 Nov 2021 (GGL did not exist).
    Applies to all gas customer segments (no exemptions).
    """
    if date_str < "2021-11-30":
        return 0.0
    year = _ro_oy_start_year(date_str)
    if year not in _GGL_RATE_GBP_PER_METER_YEAR:
        return 0.0
    if aq_kwh <= 0:
        return 0.0
    return _GGL_RATE_GBP_PER_METER_YEAR[year] / (aq_kwh / 1000.0)


# ─── Standing Charges (Phase 62) ─────────────────────────────────────────────
# Daily standing charge (£/day) for domestic and SME electricity customers.
# Covers metering costs, network fixed capacity charges, and supplier admin margin.
# Source: Ofgem quarterly tariff tracker; EPG/price-cap publications Oct 2022+.
# Pre-2022: typical market averages across standard fixed-rate tariff offers.
# I&C customers have separate capacity and utilisation charges via BSC settlement;
# standing charge = 0 for I&C (their fixed meter costs are in the capacity tariff).
_ELEC_SC_PENCE_PER_DAY_BY_YEAR: dict[int, float] = {
    2016: 24.0,   # ~£88/yr; typical pre-crisis fixed-rate market average
    2017: 25.0,
    2018: 26.0,
    2019: 27.0,
    2020: 27.0,   # COVID: network investment paused; SC held flat
    2021: 29.0,
    2022: 46.0,   # Ofgem EPG default tariff Q4 2022 cap (46p/day)
    2023: 53.0,   # Q1 2023 Ofgem cap; SC rose as network cost recovery increased
    2024: 61.0,   # 2024 cap; many suppliers at ceiling
}

# Daily gas standing charge (£/day) for resi/SME gas customers.
# Source: Ofgem quarterly tariff tracker; EPG publications.
_GAS_SC_PENCE_PER_DAY_BY_YEAR: dict[int, float] = {
    2016: 22.0,   # ~£80/yr; typical pre-crisis fixed-rate market average
    2017: 23.0,
    2018: 24.0,
    2019: 25.0,
    2020: 25.0,
    2021: 26.0,
    2022: 28.0,   # Ofgem EPG Q4 2022 default tariff cap
    2023: 29.0,
    2024: 31.0,
}

# SME meter capacity standing charge multiplier vs resi (larger meters, higher capacity).
_SME_SC_MULTIPLIER: float = 1.5


def get_electricity_standing_charge_per_day(date_str: str, segment: str = "resi") -> float:
    """Daily electricity standing charge (£/day) by year and segment.

    Resi/SME: covers metering costs, network fixed capacity, and supplier admin.
    SME pays 1.5x the resi rate (larger meter, higher capacity charge).
    I&C: returns 0.0 -- capacity charges handled via BSC settlement mechanism.
    Falls back to nearest known year.
    """
    if segment == "I&C":
        return 0.0
    year = int(date_str[:4])
    if year in _ELEC_SC_PENCE_PER_DAY_BY_YEAR:
        pence = _ELEC_SC_PENCE_PER_DAY_BY_YEAR[year]
    elif year < min(_ELEC_SC_PENCE_PER_DAY_BY_YEAR):
        pence = _ELEC_SC_PENCE_PER_DAY_BY_YEAR[min(_ELEC_SC_PENCE_PER_DAY_BY_YEAR)]
    else:
        pence = _ELEC_SC_PENCE_PER_DAY_BY_YEAR[max(_ELEC_SC_PENCE_PER_DAY_BY_YEAR)]
    sc = pence / 100.0
    return sc * _SME_SC_MULTIPLIER if segment == "SME" else sc


def get_gas_standing_charge_per_day(date_str: str, segment: str = "resi") -> float:
    """Daily gas standing charge (£/day) by year and segment.

    Resi/SME: covers gas meter fixed charges (metering + network fixed component).
    SME pays 1.5x the resi rate.
    I&C: returns 0.0 -- transportation tariffs handled separately.
    Falls back to nearest known year.
    """
    if segment == "I&C":
        return 0.0
    year = int(date_str[:4])
    if year in _GAS_SC_PENCE_PER_DAY_BY_YEAR:
        pence = _GAS_SC_PENCE_PER_DAY_BY_YEAR[year]
    elif year < min(_GAS_SC_PENCE_PER_DAY_BY_YEAR):
        pence = _GAS_SC_PENCE_PER_DAY_BY_YEAR[min(_GAS_SC_PENCE_PER_DAY_BY_YEAR)]
    else:
        pence = _GAS_SC_PENCE_PER_DAY_BY_YEAR[max(_GAS_SC_PENCE_PER_DAY_BY_YEAR)]
    sc = pence / 100.0
    return sc * _SME_SC_MULTIPLIER if segment == "SME" else sc

