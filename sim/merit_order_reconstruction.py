"""W1_6b — Merit-order / gas-first price-engine reconstruction (2026-07-28).

The structural replacement for the *reduced-form* residual-demand-scarcity curve
in `sim/price_engine.py`. Where `price_engine.py` multiplies a single gas floor by
a globally-fitted `(A0 + A1*x + A2*max(0, x-X_TIGHT)^p)` multiplier, THIS module
dispatches a typed short-run-marginal-cost (SRMC) stack against residual demand and
returns the SRMC of the *marginal* (last-dispatched) plant — the way a real GB power
price forms on an ordinary day.

  the ordinary-day fidelity delta: price stops being a fitted multiple of a gas
  floor and becomes the marginal cost of the plant that actually sets the margin.

--- What is grounded, and what is a named gap (R10 / R13) ---
EVERY numeric constant below is either cited to a resolvable published GB source or
marked NAMED GAP. Nothing here is fit to Elexon SSP (R13: the baseline changes for
fidelity-to-reality reasons only, blind to company P&L; R12: SSP is a diagnostic,
never a target). All ground-truth sources are documented in
`docs/market_research/ssp_multiplant_srmc_stack_heat_rates_2026-07-25.md` (the DISCOVER
half) and `docs/design/frame/W1_6_merit_order_reconstruction_FRAME.md` (the FRAME).

GROUNDED (cited):
  - CCGT / coal fleet-average thermal efficiency, per year: DUKES Table 5.10.C
    (gross CV basis, 2016-2024, H confidence).
  - Best-build CCGT efficiency (top of the operating-fleet efficiency spread):
    53.7% HHV, DECC/BEIS 2016 report Table 19 H-class reference plant.
  - Gas / coal per-electrical-MWh emission factors, per year: DUKES Table 5.14
    (tCO2 per MWh supplied, 2016-2024).
  - Gas fuel-input emission factor 0.1829 tCO2/MWh_th: DESNZ GHG conversion
    factors 2024 (confirms the live `price_engine.EF_GAS_TCO2_PER_MWH_TH = 0.184`).
  - Carbon Price Support ~GBP 18/tCO2, time-INVARIANT 1 Apr 2016 - 31 Mar 2028:
    HMRC Climate Change Levy rates (the single cleanest, most load-bearing input).
  - CCGT / OCGT variable O&M bookends GBP 3/MWh (2016) -> GBP 5/MWh (2024/25):
    DECC 2016 + DESNZ 2025 generation-cost workbooks (only two points ~9y apart;
    the between-years path is a stated simplification, not evidenced — see below).
  - GB cash-out / scarcity ceiling GBP 6,000/MWh: 2026-07-24 external benchmark pass.

  - EU-ETS (2016-2020) MARKET carbon price: EUA annual VOLUME-WEIGHTED primary
    auction clearing price from EEX's own auction-report archive, converted at the
    ECB annual average reference rate. UK-ETS 2021: the DESNZ statutory same-year
    determination. Sourced 2026-08-03, provenance + probe log in
    `docs/market_research/eu_uk_ets_carbon_price_series_2026-08-03.md`. This CLOSES
    the atom's headline named gap for 2016-2021 and is now the DEFAULT
    (`ets_price_gbp_per_tonne=None` => the grounded series).

NAMED GAPS (R10, carried forward, NOT fabricated):
  - UK-ETS 2022-2024 same-calendar-year market carbon price: the published statutory
    series turns FORWARD-REFERENCING from 2022 (the figure labelled year N is the
    Dec-N UKA futures contract as traded during year N-1), so applying it year-for-year
    would misalign the cost with its own year, and deriving a same-year spot from it
    would be fabrication. Those years fall back to CPS-only and are NAMED in
    `ETS_SERIES_NAMED_GAP_YEARS` rather than carrying a wrong number.
  - OCGT fleet-average efficiency (only new-build reference exists): peaker tier uses
    the DESNZ new-build reference 35% HHV as a stated proxy.
  - Coal variable O&M: not found; coal VOM approximated by the CCGT VOM bookends
    (coal is rarely marginal in GB 2016-2024 — DUKES 5.10.B load factors 8-21%).
  - Fleet capacity split (must-run / CCGT / total dispatchable): round structural
    scales (DUKES Ch.5 order of magnitude), stated simplifications, not fit to SSP.

--- The frozen ruler (exit criterion 2, R15 independence) ---
The reconstruction is graded against `gas_floor_alone` — the naive baseline family in
`background/fidelity_emitter.py::_NAIVE_FAMILY_IDS`, which this module NEVER edits. The
ruler stays frozen: `gas_floor_alone_price()` here reproduces that baseline (gas over
the pre-existing `price_engine.THERMAL_EFFICIENCY` with zero carbon) so the test can
grade against an unmoved benchmark. Do NOT change `THERMAL_EFFICIENCY` or the naive
family to make the lift look positive — the test checks the family by identity (R15).
"""

from __future__ import annotations

import math
from typing import NamedTuple

from sim.price_engine import THERMAL_EFFICIENCY  # the frozen-ruler efficiency (0.50)

# ---------------------------------------------------------------------------
# R10 CLASS GUARD — the vacuous-evidence control family (2026-08-03).
#
# A real FAIL-OPEN was found in `reconstructibility_verdict({})`: it returned
# met=True on EMPTY input, because "no losing cells" is vacuously true when
# there are no cells at all. That is R15 killer pattern #2 (a control that
# passes on missing/empty/malformed data), and per R10 it may NOT be closed
# with an instance fix.
#
# THE CLASS: every function in this atom that renders a JUDGEMENT (a verdict, a
# per-cell grading, an ordering check) must be NOT-MET / False on
#   (i)  empty or missing evidence, and
#   (ii) non-finite (NaN/inf) evidence — rejected FIRST, before any comparison,
#        because every `<` / `<=` against NaN silently returns False and would
#        otherwise decide the verdict by accident rather than by intent.
#
# The names below are the registry. `tests/sim/test_merit_order_reconstruction.py`
# §5 DISCOVERS this family by introspection (public callables in the two modules
# whose name carries one of CONTROL_NAME_MARKERS) and fails if the discovered set
# and this registry disagree — so a NEW judgement function added later without a
# vacuity guard breaks the suite automatically, rather than joining the class
# defect silently.
# ---------------------------------------------------------------------------
CONTROL_NAME_MARKERS = ("verdict", "monotone", "reconstructibility")
VACUITY_GUARDED_CONTROLS = (
    "sim.merit_order_reconstruction.is_merit_order_monotone",
    "simulation.run_merit_order_reconstructibility.per_cell_reconstructibility",
    "simulation.run_merit_order_reconstructibility.reconstructibility_verdict",
)


def is_finite_number(value: object) -> bool:
    """True only for a real, finite int/float. Bool is rejected (a flag is not
    evidence). The single primitive every control in the family uses to reject
    non-finite evidence BEFORE comparing, so a NaN can never decide a verdict."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    return math.isfinite(float(value))

# ---------------------------------------------------------------------------
# GROUNDED per-year constants (DUKES 5.10.C thermal efficiency, gross CV basis).
# docs/market_research/ssp_multiplant_srmc_stack_heat_rates_2026-07-25.md §1a.
# ---------------------------------------------------------------------------
CCGT_THERMAL_EFFICIENCY_BY_YEAR = {
    2016: 0.4893, 2017: 0.4869, 2018: 0.4894, 2019: 0.4878, 2020: 0.4844,
    2021: 0.4900, 2022: 0.4911, 2023: 0.4991, 2024: 0.4893,
}
COAL_THERMAL_EFFICIENCY_BY_YEAR = {
    2016: 0.3498, 2017: 0.3486, 2018: 0.3410, 2019: 0.3205, 2020: 0.3324,
    2021: 0.3482, 2022: 0.3646, 2023: 0.3582, 2024: 0.4151,  # 2024 thin-sample outlier
}
# DESNZ new-build reference (DECC/BEIS 2016 Table 19). §1b — different population
# (best-available-technology, not fleet average); used as the TOP of the operating
# efficiency spread and as the OCGT peaker proxy.
CCGT_BEST_BUILD_EFFICIENCY = 0.537   # H-class, HHV
OCGT_REFERENCE_EFFICIENCY = 0.35     # new-build 300MW peaker proxy (fleet-avg = NAMED GAP)

# Per-electrical-MWh emission factors (DUKES 5.14, tCO2 per MWh supplied). §3b.
EF_GAS_TCO2_PER_MWH_E_BY_YEAR = {
    2016: 0.378, 2017: 0.380, 2018: 0.378, 2019: 0.367, 2020: 0.371,
    2021: 0.376, 2022: 0.379, 2023: 0.372, 2024: 0.382,
}
EF_COAL_TCO2_PER_MWH_E_BY_YEAR = {
    2016: 0.935, 2017: 0.918, 2018: 0.921, 2019: 0.992, 2020: 1.008,
    2021: 0.970, 2022: 0.987, 2023: 1.021, 2024: 0.919,
}
# Fuel-input emission factor — confirms live price_engine.EF_GAS_TCO2_PER_MWH_TH=0.184.
EF_GAS_TCO2_PER_MWH_TH = 0.1829      # DESNZ GHG conversion factors 2024, gross CV. §3a.

# Carbon Price Support: time-INVARIANT ~GBP 18/tCO2 across the whole window. §4a.
CPS_CARBON_GBP_PER_TONNE = 18.0

# ---------------------------------------------------------------------------
# EU-ETS / UK-ETS MARKET carbon price — the NAMED GAP, CLOSED 2026-08-03.
# Provenance: docs/market_research/eu_uk_ets_carbon_price_series_2026-08-03.md
#
# 2016-2020 (GB was inside the EU ETS): EUA annual VOLUME-WEIGHTED auction
# clearing price, computed from EEX's own "Emission Spot Primary Market Auction
# Report" 2012-2025 archive (one daily-auction row per auction, weighted by
# auction volume) — EEX is the platform the allowances are actually auctioned on.
#   https://www.eex.com/en/market-data/market-data-hub/environmentals/
#     eex-eua-primary-auction-spot-download
# CAVEAT (stated, not smoothed): this is the PRIMARY AUCTION CLEARING price, not
# the continuous secondary-market spot — they track closely but are not identical.
#
# 2021 (GB in its own UK ETS): the statutory UK ETS carbon price, DESNZ/UK ETS
# Authority determination under Art.46 Greenhouse Gas Emission Trading Scheme
# Order 2020 — for 2021 ONLY this is a genuinely contemporaneous same-year
# volume-weighted UK auction clearing average (GBP 47.96).
#   https://www.gov.uk/government/publications/determinations-of-the-uk-ets-carbon-price
#
# 2022-2024 are a NAMED GAP, still open, DELIBERATELY NOT FILLED: the same
# statutory series becomes FORWARD-REFERENCING from 2022 (the figure labelled
# year N is the Dec-N UKA futures contract as traded during year N-1), so
# applying it year-for-year would misalign the carbon cost with its own calendar
# year. Inferring a same-year UKA spot from it would be fabrication (R13), so
# those years fall back to CPS-only and say so, rather than carrying a wrong number.
# ---------------------------------------------------------------------------
EUA_AUCTION_VWAP_EUR_PER_TONNE_BY_YEAR = {
    2016: 5.26, 2017: 5.79, 2018: 15.34, 2019: 24.65, 2020: 24.51,
}
# ECB official daily reference rate EXR.D.GBP.EUR.SP00.A (GBP per 1 EUR), simple
# mean of all daily observations in each calendar year, ECB Data Portal API:
#   https://data-api.ecb.europa.eu/service/data/EXR/D.GBP.EUR.SP00.A?format=csvdata
ECB_GBP_PER_EUR_ANNUAL_AVERAGE_BY_YEAR = {
    2016: 0.8195, 2017: 0.8767, 2018: 0.8847, 2019: 0.8778, 2020: 0.8897,
    2021: 0.8596, 2022: 0.8528, 2023: 0.8698, 2024: 0.8466,
}
# UK ETS statutory determination, contemporaneous same-year basis (2021 only).
UK_ETS_CONTEMPORANEOUS_GBP_PER_TONNE_BY_YEAR = {
    2021: 47.96,
}
# Years for which NO same-calendar-year market carbon price could be sourced
# without fabricating one. These fall back to CPS-only; `ets_carbon_price_...`
# returns 0.0 and `ETS_SERIES_NAMED_GAP_YEARS` names them for the evidence doc.
ETS_SERIES_NAMED_GAP_YEARS = (2022, 2023, 2024)


def ets_carbon_price_gbp_per_tonne(year: int) -> float:
    """The MARKET carbon price (GBP/tCO2) a GB generator faced on top of CPS, from
    the grounded series above. Returns 0.0 ONLY for the years where no same-year
    figure could be sourced (2022-2024) — a NAMED GAP, not a claim of zero carbon.

    2016-2020 converts the EUA auction VWAP at that year's ECB average rate; the
    conversion is done HERE from the two cited primary series rather than stored as
    a pre-multiplied constant, so the derivation stays visible and checkable."""
    y = _year_of(year)
    if y in UK_ETS_CONTEMPORANEOUS_GBP_PER_TONNE_BY_YEAR:
        return UK_ETS_CONTEMPORANEOUS_GBP_PER_TONNE_BY_YEAR[y]
    if y in EUA_AUCTION_VWAP_EUR_PER_TONNE_BY_YEAR:
        return (EUA_AUCTION_VWAP_EUR_PER_TONNE_BY_YEAR[y]
                * ECB_GBP_PER_EUR_ANNUAL_AVERAGE_BY_YEAR[y])
    return 0.0  # NAMED GAP year (2022-2024) — CPS-only, flagged not fabricated

# GB cash-out / scarcity ceiling (DDM design). 2026-07-24 external benchmark pass.
CASH_OUT_CEILING_GBP_PER_MWH = 6000.0

# --- Structural fleet scales (NAMED SIMPLIFICATIONS — round DUKES Ch.5 orders of
#     magnitude, NOT fit to SSP; would be grounded per-year by the ESO capacity
#     register, portability debt). Used only to place the merit-order transitions. ---
MUST_RUN_FLOOR_MW = 8000.0           # nuclear + biomass/hydro must-run baseload
CCGT_CAPACITY_MW = 30000.0           # GB CCGT fleet (mid-merit)
TOTAL_DISPATCHABLE_MW = 45000.0      # +peakers/reserve above CCGT before the ceiling
# Curtailment floor: real SSP reaches ~ -GBP 185/MWh in deep oversupply. A single
# stated floor for the renewables-flood collapse (NAMED SIMPLIFICATION, order set by
# the observed real minimum, NOT a per-cell fit).
CURTAILMENT_FLOOR_GBP_PER_MWH = -60.0


def _year_of(year: int) -> int:
    """Clamp to the grounded 2016-2024 window (constants outside it are extrapolated
    to the nearest bounding year — a stated simplification, flagged not fabricated)."""
    if year < 2016:
        return 2016
    if year > 2024:
        return 2024
    return year


def carbon_price_total_gbp_per_tonne(
    year: int, ets_price_gbp_per_tonne: float | None = None
) -> float:
    """Total effective GB carbon price = Carbon Price Support (grounded, flat ~£18)
    + the ETS market price.

    `ets_price_gbp_per_tonne=None` (the DEFAULT since 2026-08-03) uses the GROUNDED
    EU/UK-ETS series above — the NAMED GAP that used to default to 0.0 is closed for
    2016-2021 from primary EEX auction data + ECB reference rates. Passing an explicit
    float OVERRIDES the series (used to price counterfactuals and to reproduce the
    pre-2026-08-03 CPS-only behaviour with `0.0`); it is never a fitted knob."""
    ets = (ets_carbon_price_gbp_per_tonne(year) if ets_price_gbp_per_tonne is None
           else ets_price_gbp_per_tonne)
    return CPS_CARBON_GBP_PER_TONNE + ets


def variable_om_gbp_per_mwh(year: int) -> float:
    """CCGT/OCGT variable O&M, linearly interpolated between the two grounded bookends
    GBP 3/MWh (DECC 2016) and GBP 5/MWh (DESNZ 2025). Only two points ~9y apart exist
    (§2, L confidence between them) — the interpolation is a STATED simplification."""
    y = _year_of(year)
    return 3.0 + (y - 2016) * (5.0 - 3.0) / (2024 - 2016)


def ccgt_efficiency_fleet_average(year: int) -> float:
    return CCGT_THERMAL_EFFICIENCY_BY_YEAR[_year_of(year)]


def _ccgt_efficiency_band(year: int) -> tuple[float, float]:
    """The operating CCGT efficiency SPREAD (worst-vintage .. best-build), grounded by
    two anchors: the TOP is the DESNZ best-build H-class (0.537), and the BOTTOM is set
    so the band MIDPOINT equals the DUKES fleet-average — i.e. worst = 2*fleet_avg -
    best. This produces the merit-order softening (efficient units marginal at low
    load, inefficient units marginal at high load) from PUBLISHED efficiency figures,
    with NO constant fit to SSP."""
    fleet_avg = ccgt_efficiency_fleet_average(year)
    best = CCGT_BEST_BUILD_EFFICIENCY
    worst = 2.0 * fleet_avg - best
    return worst, best


def ccgt_srmc_gbp_per_mwh(
    gas_price_gbp_per_mwh: float,
    year: int,
    thermal_efficiency: float | None = None,
    ets_price_gbp_per_tonne: float | None = None,
) -> float:
    """SRMC (£/MWh electrical) of a gas CCGT: fuel-over-efficiency + carbon + VOM.

        SRMC = gas/efficiency  +  carbon_total * EF_gas_e  +  VOM

    `thermal_efficiency` defaults to the year's fleet average; pass a band value to
    price a specific marginal vintage. Carbon uses the per-electrical-MWh emission
    factor (DUKES 5.14) so the carbon term is already on an electrical basis."""
    y = _year_of(year)
    eff = thermal_efficiency if thermal_efficiency is not None else ccgt_efficiency_fleet_average(y)
    carbon = carbon_price_total_gbp_per_tonne(y, ets_price_gbp_per_tonne)
    carbon_cost_e = carbon * EF_GAS_TCO2_PER_MWH_E_BY_YEAR[y]
    return gas_price_gbp_per_mwh / eff + carbon_cost_e + variable_om_gbp_per_mwh(y)


def coal_srmc_gbp_per_mwh(
    coal_price_gbp_per_mwh: float,
    year: int,
    ets_price_gbp_per_tonne: float | None = None,
) -> float:
    """SRMC (£/MWh electrical) of a coal unit — for merit-order ORDERING against gas.
    Coal VOM is a NAMED GAP (§2); approximated by the CCGT VOM bookend."""
    y = _year_of(year)
    eff = COAL_THERMAL_EFFICIENCY_BY_YEAR[y]
    carbon = carbon_price_total_gbp_per_tonne(y, ets_price_gbp_per_tonne)
    carbon_cost_e = carbon * EF_COAL_TCO2_PER_MWH_E_BY_YEAR[y]
    return coal_price_gbp_per_mwh / eff + carbon_cost_e + variable_om_gbp_per_mwh(y)


class MeritPlant(NamedTuple):
    label: str
    srmc_gbp_per_mwh: float
    capacity_mw: float


def build_merit_stack(
    gas_price_gbp_per_mwh: float,
    year: int,
    coal_price_gbp_per_mwh: float | None = None,
    ets_price_gbp_per_tonne: float | None = None,
) -> list[MeritPlant]:
    """The typed SRMC dispatch stack, cheapest-first (must-run renewables/nuclear at
    the bottom, then the CCGT band, then peakers). The returned list is ALWAYS SRMC-
    ascending by construction — `is_merit_order_monotone` grades exactly that, and the
    R15 mutation (mis-ordering the stack) makes the reconstructibility check go RED."""
    y = _year_of(year)
    worst_eff, best_eff = _ccgt_efficiency_band(y)
    stack = [
        # Zero/near-zero SRMC must-run: renewables + nuclear (price-takers).
        MeritPlant("must_run_renewables_nuclear", 0.0, MUST_RUN_FLOOR_MW),
        # CCGT band, priced at its two efficiency extremes (best unit first).
        MeritPlant("ccgt_best_vintage",
                   ccgt_srmc_gbp_per_mwh(gas_price_gbp_per_mwh, y, best_eff, ets_price_gbp_per_tonne),
                   CCGT_CAPACITY_MW / 2.0),
        MeritPlant("ccgt_worst_vintage",
                   ccgt_srmc_gbp_per_mwh(gas_price_gbp_per_mwh, y, worst_eff, ets_price_gbp_per_tonne),
                   CCGT_CAPACITY_MW / 2.0),
        # Peakers / reserve toward the ceiling.
        MeritPlant("ocgt_peaker",
                   ccgt_srmc_gbp_per_mwh(gas_price_gbp_per_mwh, y, OCGT_REFERENCE_EFFICIENCY, ets_price_gbp_per_tonne),
                   TOTAL_DISPATCHABLE_MW - MUST_RUN_FLOOR_MW - CCGT_CAPACITY_MW),
    ]
    if coal_price_gbp_per_mwh is not None:
        coal = MeritPlant("coal",
                          coal_srmc_gbp_per_mwh(coal_price_gbp_per_mwh, y, ets_price_gbp_per_tonne),
                          0.0)  # capacity not modelled (rarely marginal); ordering only
        stack = sorted([*stack, coal], key=lambda p: p.srmc_gbp_per_mwh)
    return stack


def is_merit_order_monotone(stack: list[MeritPlant]) -> bool:
    """R15 independence hook: True iff the stack is SRMC-ascending (a real merit order).
    The reconstructibility check asserts this; a mis-ordered stack (peaker below CCGT,
    say) makes it False → the check FIRES on its own named defect (non-monotone stack).

    VACUITY GUARD (R10 class fix, 2026-08-03): an empty or single-plant stack carries
    NO ordering evidence — `zip(srmcs, srmcs[1:])` is empty and `all([])` is True, so the
    unguarded form PASSED on no data (the same fail-open as `reconstructibility_verdict({})`).
    Ordering is a claim about a PAIR, so fewer than two plants is False, not vacuously True.
    Non-finite SRMCs are rejected FIRST: `nan <= x` is False, which would otherwise report
    "mis-ordered" for what is really "unmeasurable" — the right verdict by accident."""
    if len(stack) < 2:
        return False  # no pair => no ordering evidence => NOT met (never vacuously True)
    srmcs = [p.srmc_gbp_per_mwh for p in stack]
    if not all(is_finite_number(s) for s in srmcs):
        return False  # non-finite evidence rejected BEFORE any comparison
    return all(a <= b + 1e-9 for a, b in zip(srmcs, srmcs[1:]))


def reconstruct_price_gbp_per_mwh(
    gas_price_gbp_per_mwh: float,
    demand_mw: float,
    renewable_generation_mw: float,
    year: int,
    ets_price_gbp_per_tonne: float | None = None,
    must_run_floor_mw: float = MUST_RUN_FLOOR_MW,
    ccgt_capacity_mw: float = CCGT_CAPACITY_MW,
    total_dispatchable_mw: float = TOTAL_DISPATCHABLE_MW,
) -> float:
    """The reconstructed half-hourly price: the SRMC of the marginal (last-dispatched)
    plant against residual demand `RD = demand - renewables`.

    Three regimes, all from the typed stack — NOT a fitted multiplier:
      1. OVERSUPPLY (RD < must_run_floor): renewables+nuclear flood the system; price
         collapses linearly from the cheapest CCGT SRMC toward the curtailment floor.
      2. ORDINARY (must_run_floor <= RD <= must_run_floor + ccgt_capacity): a CCGT is
         marginal. Its efficiency slides from best-build (low load) to worst-vintage
         (high load) across the band, so ordinary-day price rises with residual demand
         through DECLINING MARGINAL EFFICIENCY — a grounded merit-order shape, not A1*x.
      3. TIGHT (RD > must_run_floor + ccgt_capacity): peakers/reserve; price rises
         convexly from the worst-CCGT SRMC toward the £6,000/MWh cash-out ceiling.
    """
    y = _year_of(year)
    residual_demand_mw = demand_mw - renewable_generation_mw
    worst_eff, best_eff = _ccgt_efficiency_band(y)
    srmc_low = ccgt_srmc_gbp_per_mwh(gas_price_gbp_per_mwh, y, best_eff, ets_price_gbp_per_tonne)
    srmc_high = ccgt_srmc_gbp_per_mwh(gas_price_gbp_per_mwh, y, worst_eff, ets_price_gbp_per_tonne)

    ccgt_band_top_mw = must_run_floor_mw + ccgt_capacity_mw

    if residual_demand_mw <= must_run_floor_mw:
        # Oversupply: fraction of the must-run floor still unmet by nothing dearer.
        # RD from must_run_floor down to 0 (and below) maps srmc_low -> curtailment.
        span = must_run_floor_mw if must_run_floor_mw > 0 else 1.0
        frac_below = (must_run_floor_mw - residual_demand_mw) / span  # 0 at floor, grows as RD falls
        frac_below = min(max(frac_below, 0.0), 1.0)
        return srmc_low + (CURTAILMENT_FLOOR_GBP_PER_MWH - srmc_low) * frac_below

    if residual_demand_mw <= ccgt_band_top_mw:
        # Ordinary: marginal CCGT efficiency slides best -> worst across the band.
        f = (residual_demand_mw - must_run_floor_mw) / ccgt_capacity_mw  # 0..1
        marginal_eff = best_eff - (best_eff - worst_eff) * f
        return ccgt_srmc_gbp_per_mwh(gas_price_gbp_per_mwh, y, marginal_eff, ets_price_gbp_per_tonne)

    # Tight: convex climb from worst-CCGT SRMC toward the ceiling.
    peaker_span = total_dispatchable_mw - ccgt_band_top_mw
    if peaker_span <= 0:
        return CASH_OUT_CEILING_GBP_PER_MWH
    f2 = min((residual_demand_mw - ccgt_band_top_mw) / peaker_span, 1.0)
    return srmc_high + (CASH_OUT_CEILING_GBP_PER_MWH - srmc_high) * (f2 ** 2)


def gas_floor_alone_price_gbp_per_mwh(gas_price_gbp_per_mwh: float) -> float:
    """The FROZEN naive baseline (`gas_floor_alone` in the fidelity naive family):
    gas over the pre-existing THERMAL_EFFICIENCY (0.50), zero carbon. Reproduced here
    ONLY so the reconstructibility test can grade against an unmoved ruler (R15 exit
    criterion 2). Do NOT change THERMAL_EFFICIENCY to move this — it is the benchmark."""
    return gas_price_gbp_per_mwh / THERMAL_EFFICIENCY
