"""Phase 2b — Gas Dual Fuel.

Adds gas supply to C1-C4 resi customers (dual fuel). Runs 2016-2025 with:
  - Electricity-only: C5, C6 (SME, PC3)
  - Dual fuel: C1-C4 (electricity PC1) + C1g-C4g (gas, daily, flat AQ/365)

Key differences from Phase 2a repriced:
  - Gas price feed: NBP SAP from sim/gas_data/nbp_sap.csv (FRED/IMF monthly)
  - Gas settlement: daily granularity, AQ/365 flat consumption
  - Gas forward curve: same generate_forward_price() logic on NBP records
  - Gas risk engine: assess_term_risk() with NBP records (same dual-window VaR)
  - Shared treasury: electricity + gas capital costs deducted from same pot
  - Starting treasury: scaled by total energy volume (elec + gas)

Delegation note: hand-written (orchestration-adjacent, per protocol).
"""

import random
import statistics
from collections import defaultdict
from datetime import date, datetime, time, timedelta

import sim.risk_committee_agent as risk_committee_agent
from background.gap_metric import format_ageing_summary as _format_ageing_summary
from background.gap_metric import format_belief_summary as _format_belief_summary
from background.gap_metric import format_detection_summary as _format_detection_summary
from background.live_fidelity_evidence import emit_live_fidelity_evidence
from background.live_payment_triad import LivePaymentTriad
from company.interfaces.churn_estimation import (
    RenewalObservation,
    active_pressure_ledger,
    crisis_hangover_periods,
    estimate_churn_without_rate_history,
    estimate_renewal_churn,
    estimate_secondary_fuel_churn,
    pressure_ledger_scope,
    score_churn_estimates,
)
from company.interfaces.counterparty_collateral import build_counterparty_collateral
from company.interfaces.customer_experience import (
    CustomerContact,
    CustomerExperienceDesk,
    PaymentOutcome,
    RenewalReached,
    SurveyInstrument,
    SurveyResponse,
)
from company.interfaces.fixed_overhead import book_monthly_overhead
from company.interfaces.flexibility_revenue import build_flexibility_revenue
from company.interfaces.growth_desk import (
    book_acquisition_gate,
    book_acquisition_spend,
    book_retention_cost,
    decide_acquisition,
    growth_mandate_label,
    mandate_permits_replacement,
    replacement_cost_avoided_gbp,
)
from company.interfaces.hedge_desk import build_hedge_desk, hedge_mandate
from company.interfaces.point_in_time_view import PointInTimeView, build_price_bitemporal_log
from company.interfaces.renewal_offer import (
    request_company_forward_estimate,
    request_fixed_unit_rate,
)
from company.interfaces.renewal_rate_chain import decide_renewal_rate
from company.interfaces.statutory_obligations import build_statutory_obligations
from company.interfaces.supply_book import (
    acquired_supply_points,
    successor_supply_points,
)
from company.interfaces.supply_book import (
    register_acquired_point as make_acquired_customer,
)
from company.interfaces.supply_book import (
    registered_point as get_customer,
)
from company.interfaces.tou_offer import request_tou_offer
from company.interfaces.tpi_commission import build_tpi_commission
from company.policy.decision_policy import (
    CURRENT_POLICY,
    DecisionPolicy,
    active_policy,
    framing_type_for,
)
from sim.cache_store import get_cached_prices, log_cache_access
from sim.forward_curve import (
    BASE_TERM_PREMIUM,
    DEFAULT_RISK_FACTOR,
    EWMA_HALF_LIFE_DAYS,
    GAS_BASE_TERM_PREMIUM,
    SUMMER_MULTIPLIER,
    WINTER_MONTHS,
    WINTER_MULTIPLIER,
    _ewma,
    _seasonal_shape,
    generate_forward_price,
)
from sim.gas_prices_history import load_nbp_history
from sim.profile_class_1 import load_pc1_shape
from sim.profile_class_3 import load_pc3_shape
from sim.risk_committee import RiskCommitteeMonitor
from sim.risk_engine import assess_term_risk, is_administration_triggered
from sim.system_prices_history import get_system_prices_range
from sim.weather_hdd import REFERENCE_MONTHLY_HDD, get_hdd
from sim.weather_price_sensitivity import weather_sensitivity_multiplier
from simulation.acquisition_funnel import run_acquisition_funnel
from simulation.bad_debt_incidence import world_bad_debt_incidence
from simulation.bill_shock_tracker import count_rate_shocks as _count_rate_shocks
from simulation.churn_journey import ChurnJourneyRegister
from simulation.competitor_reference import CompanyPositionLedger
from simulation.customer_events import (
    HOME_MOVE_ACTIVATE_SUCCESSOR,
    home_move_disposition,
    roll_lifecycle_event,
)
from simulation.demand_model import build_demand_shape, solar_generation_shape
from simulation.demand_response import compute_shift_fraction, make_shifted_shape_fn
from simulation.dwelling_records import (
    DEFAULT_ASSETS,
    DEFAULT_HEATING_SYSTEM,
    DEFAULT_OCCUPANCY_PATTERN,
    build_properties,
)
from simulation.fabric_demand_path import (
    FABRIC_PROVIDER,
    LEGACY_PROVIDER,
    METERED_PROVIDER,
    coverage_refusals,
    fabric_providers_for_book,
    fabric_shape_fn,
    settled_shape_is_physically_textured,
    settlement_providers_match_eligibility,
    the_switch_moves_the_settled_volume,
)
from simulation.fabric_physics import DEFAULT_LATITUDE_DEG
from simulation.feedback_survey import (
    dispatch_complaint_and_resolution,
    dispatch_csat_survey,
    dispatch_nps_survey,
)
from simulation.gas_settlement import run_gas_term
from simulation.hedged_settlement import run_deemed_term, run_flex_term, run_hedged_term
from simulation.hh_consumption import (
    estimate_annual_kwh,
    hh_shape_fn,
    is_hh_customer,
    load_hh_consumption,
)
from simulation.household import household_of
from simulation.household_demand import HouseholdDemandRegister
from simulation.live_population import (
    campaign_quotes_paid_for,
    founding_capital_gbp,
    live_drawn_households,
    live_dwellings,
    live_population,
)
from simulation.nudge_physics import framing_effectiveness_multiplier, susceptibility_for
from simulation.payment_timing import generate_payment_record, stress_bad_debt_multiplier
from simulation.policy_costs import (
    get_gas_ccl_per_mwh,
    get_gas_network_cost_per_mwh,
    get_ggl_per_mwh,
)
from simulation.premise_trace import WEATHER_DATA_DIR as WEATHER_DATA_DIR_PATH
from simulation.renewal_engagement import passive_churn_cap_for, rolls_active_renewal
from simulation.renewals import NOTICE_DAYS, build_renewal_schedule
from simulation.reputation_index import ReputationEventType
from simulation.resentment_ledger import FrictionEventType
from simulation.settlement import CONTRACT_LENGTH_DAYS
from simulation.settlement_daily import PeriodRegisters, TreasuryDrawdown, fold_to_days
from simulation.settlement_fold import SettlementFold
from simulation.sim_satisfaction import sim_satisfaction_score as _sim_satisfaction_score
from simulation.svt_product import SVT_TARIFF_TYPE
from simulation.tou_periods import is_peak_period as _is_peak_period
from simulation.triad import (
    _triad_year,
    build_triad_alert_set,
    compute_triad_exposure,
    identify_triad_candidates,
    make_triad_aware_shape_fn,
)
from simulation.volume_tolerance import compute_term_volume_tolerance
from simulation.weather_inputs import (
    _weather_source_customer_id,
    cloud_cover_for_customer,
    lookback_mean_temps,
    weather_means_for_customer,
)
from tools.acquisition_funnel_port import AcquisitionFunnelMessage
from tools.credit_adapters import get_credit_bureau_adapter

# The supply book, bound once at import: the seam hands back the LIVE roster
# objects (see company/interfaces/supply_book.py, IDENTITY), so a runtime append
# to the acquired book is visible here exactly as it was before KNIFE pass 2.
ACQUIRED_CUSTOMERS = acquired_supply_points()
# generator_draw_wiring ACTIVATION (2026-08-13): the run's book comes through the
# population seam, not straight off the static roster. Flag OFF, `live_population()`
# returns the same 18 records in the same order, so this is byte-identical; flag ON,
# it is those 18 plus the curriculum's drawn 2021-2025 trickle, and the drawn points
# are registered on the book so `registered_point()` can resolve them.
CUSTOMERS = live_population()
SUCCESSOR_CUSTOMERS = successor_supply_points()

REPORT_START = "2016-01-01"
REPORT_END = "2025-06-07"
CRISIS_YEARS = {"2021", "2022"}

# 2026-07-10: point-in-time-blindfold fix (docs/review_gates/
# HEDGE_VOLATILITY_LOOKBACK_FORESIGHT_BUG.md) -- originally fixed with a
# per-call-site wrapper (_price_history_as_of(), a bisect-slice bounding the
# blast radius to this one caller without touching estimate_price_volatility
# itself). 2026-07-11 (M1 depth work): retired in favour of the structural
# fix the bug always needed -- PointInTimeView.get_price_history_as_of(),
# backed by a BitemporalEventLog (company/interfaces/point_in_time_view.py
# ::build_price_bitemporal_log()) built once per run below. The bound now
# lives on the view object, not in a caller's remembered wrapper call.

# Treasury scaled by total EAC across all commodities
# Base: £3,250 per 15,000 kWh of electricity EAC
ELEC_CUSTOMERS = [c for c in CUSTOMERS if c["commodity"] == "electricity"]
GAS_CUSTOMERS = [c for c in CUSTOMERS if c["commodity"] == "gas"]
# Phase 47a: segment lookup for Ofgem cap — resi customers subject to price cap
_RESI_CUSTOMER_IDS: frozenset[str] = frozenset(
    c["customer_id"] for c in CUSTOMERS if c.get("segment") == "resi"
)
# Phase 7e: successor electricity customers (activated on home-move win).
# Separate from ELEC_CUSTOMERS so they don't inflate the starting treasury.
SUCCESSOR_ELEC_CUSTOMERS = [c for c in SUCCESSOR_CUSTOMERS if c["commodity"] == "electricity"]
SUCCESSOR_MAP: dict[str, str] = {
    c["successor_of"]: c["customer_id"] for c in SUCCESSOR_ELEC_CUSTOMERS
}
_SUCCESSOR_ELEC_IDS: frozenset[str] = frozenset(c["customer_id"] for c in SUCCESSOR_ELEC_CUSTOMERS)
_ALL_KNOWN_CUSTOMERS = CUSTOMERS + SUCCESSOR_CUSTOMERS
#: cid -> segment, for the Triad carve-out in `settlement_daily.PeriodRegisters`. Triad
#: exposure is an I&C matter, so that register keeps the periods for those accounts in the
#: Triad season and nothing else. Built once here rather than looked up per record.
_SEGMENT_OF = {c["customer_id"]: c.get("segment", "resi") for c in _ALL_KNOWN_CUSTOMERS}
ORIGINAL_4_CUSTOMER_EAC_KWH = 15_000

# Phase 6a: HH (smart meter) customers have eac_kwh=None — their effective
# EAC for hedging-volume sizing and treasury scaling is derived from real
# half-hourly consumption data (simulation/hh_consumption.py) instead.
EFFECTIVE_EAC_KWH: dict[str, float] = {
    c["customer_id"]: c["eac_kwh"] if c["eac_kwh"] is not None
    else estimate_annual_kwh(load_hh_consumption(c["customer_id"]))
    for c in ELEC_CUSTOMERS
}
# Successor customers share the same property EAC as their predecessor.
EFFECTIVE_EAC_KWH.update({
    c["customer_id"]: c["eac_kwh"]
    for c in SUCCESSOR_ELEC_CUSTOMERS
})

# Treasury sized on original customers only — successors don't exist yet at t=0.
TOTAL_ELEC_EAC = sum(
    EFFECTIVE_EAC_KWH[c["customer_id"]] for c in ELEC_CUSTOMERS
)
TOTAL_GAS_AQ = sum(c["aq_kwh"] for c in GAS_CUSTOMERS)
# Gas is priced ~10x cheaper per MWh than electricity; weight accordingly
# Treat 1 kWh gas ≈ 0.25 kWh electricity for treasury sizing (conservative)
GAS_ELEC_WEIGHT = 0.25
EFFECTIVE_EAC = TOTAL_ELEC_EAC + TOTAL_GAS_AQ * GAS_ELEC_WEIGHT
# FOUNDING CAPITAL, not a multiple of the book's meter reads (2026-08-24).
#
# THE FORMULA BELOW IS THE FALLBACK AND IT IS KEPT DELIBERATELY. `3250 * (EFFECTIVE_EAC /
# 15000)` is a scaling hack inherited from the four-customer era -- `run_phase1e.py` still
# carries the un-scaled ancestor, `STARTING_TREASURY_GBP = 3250.0`. It makes the company's
# CAPITAL a function of its customers' CONSUMPTION, and three impossible things follow: it can
# never be undercapitalised, because taking on a customer capitalises it; it can never be
# capital-constrained in a way that binds, because the constraint grows with the thing it
# constrains; and suspending a segment destroys capital that was never earned from it.
#
# That last one is how it surfaced. Suspending I&C on the director's word dropped opening
# treasury from £2,201,241 to £12,134 while the licensing obligation was unchanged. A real
# supplier that stops selling to industry does not lose its share capital.
#
# The curriculum figure is a FOUNDING INVESTMENT: fixed, independent of the book, and derived
# from the Ofgem MCR and the shipped funnel's measured cost per win
# (docs/design/curriculum/founding_capital.json carries the arithmetic). `null` there restores
# the formula, which is why the formula stays in this file rather than in a git history.
STARTING_TREASURY_GBP = founding_capital_gbp(
    fallback=3250.0 * (EFFECTIVE_EAC / ORIGINAL_4_CUSTOMER_EAC_KWH)
)

# Phase 5c minimum hedge mandate: every term starts at the mandate floor, not a
# neutral 50/50 guess. KNIFE3 step 23 (§3r): the floor is the DESK's mandate and
# is now read off it, rather than the world importing the company's constant.
RESET_HEDGE_FRACTION = hedge_mandate().opening_hedge_fraction

RETENTION_THRESHOLD = 0.30
RETENTION_EFFECTIVENESS = 0.20

# Phase QM (QL_WIRE_AND_DEFERRAL.md): expected_term_margin_gbp below already prices ONE
# renewal term, not lifetime CLV -- this constant makes that implicit assumption an explicit,
# named H1 hypothesis so company/analytics/retention_deferral_economics.py can compare it
# against the H2 realized deferral (time to the customer's next offer or churn).
ASSUMED_DEFERRAL_MONTHS = 12

# Phase 14a: tiered discount — risk-proportional rather than flat 5%
# Higher churn risk warrants a larger offer; borderline cases get a lighter touch.
RETENTION_TIERS: list[tuple[float, float]] = [
    (0.75, 0.08),  # high risk (≥75%): 8% discount
    (0.50, 0.05),  # medium risk (50-75%): 5% discount
    (0.30, 0.03),  # low-risk-above-threshold (30-50%): 3% discount
]


def _retention_discount_for_risk(company_est: float) -> float:
    """Return the retention discount fraction appropriate for the churn estimate."""
    for threshold, discount in RETENTION_TIERS:
        if company_est >= threshold:
            return discount
    return 0.0

EARLIEST_SSP_DATE = "2015-11-07"
COMMITTEE_COOLDOWN_PERIODS = 1440
COMMITTEE_COOLDOWN_DAYS = 30  # calendar-day cooldown; replaces record-count approach

SHAPE_LOADERS = {1: load_pc1_shape, 3: load_pc3_shape}

# Phase 4c-1 property records only cover resi electricity customers (C1-C4).
# SME customers (C5, C6) get this default property for 4c-2's demand-shape
# adjustment — no occupancy/asset seed data exists for them.
DEFAULT_PROPERTY = {
    "heating_system": DEFAULT_HEATING_SYSTEM,
    "occupancy_pattern": DEFAULT_OCCUPANCY_PATTERN,
    "assets": dict(DEFAULT_ASSETS),
}


# Phase Q: battery home energy storage dispatch constants + helper.
_BATTERY_EVENING_PEAK: frozenset = frozenset(range(33, 41))  # periods 33-40 = 16:00-20:00
_BATTERY_ROUNDTRIP_EFFICIENCY: float = 0.90  # typical Li-ion roundtrip

# Phase P: EV overnight smart-charging shape (UK Smart Charge Point Regulations 2021).
# 90% of home EV charging occurs overnight (23:00-07:00); periods are 1-indexed.
_EV_OVERNIGHT_PERIODS: frozenset = frozenset(range(1, 15)) | frozenset({47, 48})  # 16 periods
_EV_OVERNIGHT_FRACTION: float = 0.90
_EV_DAYTIME_FRACTION: float = 0.10


def _battery_daily_dispatch(
    gross_load: list[float],
    solar_gen: list[float],
    battery_kwh: float,
) -> list[float]:
    """One-day home battery dispatch: charge from excess solar, discharge in evening peak.

    Returns 48-period net import [kWh], clamped >= 0.
    Efficiency applied on the way in (charge); discharge is 1:1 from stored kWh.
    Battery only charges from excess solar outside the evening peak window.
    """
    soc = 0.0
    for i, (load, gen) in enumerate(zip(gross_load, solar_gen)):
        period = i + 1
        if period not in _BATTERY_EVENING_PEAK:
            excess = max(0.0, gen - load)
            can_charge = (battery_kwh - soc) / _BATTERY_ROUNDTRIP_EFFICIENCY
            soc += min(excess, can_charge) * _BATTERY_ROUNDTRIP_EFFICIENCY

    net = [max(0.0, l - g) for l, g in zip(gross_load, solar_gen)]
    for i in range(32, 40):  # 0-indexed: periods 33-40
        if soc > 0.0 and net[i] > 0.0:
            discharge = min(soc, net[i])
            soc -= discharge
            net[i] -= discharge
    return net


def _weather_adjusted_shape_fn(
    base_shape_fn,
    weather_means: dict[str, float],
    property_record: dict,
    cloud_cover_means: dict[str, float] | None = None,
    latitude_deg: float | None = None,
    household_register: "HouseholdDemandRegister | None" = None,
    customer_id: str | None = None,
):
    """Wrap a SHAPE_LOADERS[...] base-shape function with 4c-2's
    weather/occupancy/asset demand adjustment (`build_demand_shape`).

    Falls back to the unadjusted base shape on dates with no weather data
    (e.g. outside sim/weather_data's 2016-01-01..2025-06-07 coverage).

    Phase 25a: cloud_cover_means + latitude_deg enable solar irradiance
    reduction for customers with assets.solar=True (currently C4).
    Phase C: household_register + customer_id enable EPC consumption
    multiplier and time-varying EV ownership.
    """
    from datetime import date as _date

    from sim.weather_engine import half_hourly_solar_irradiance

    def shape_fn(date_str):
        base_shape = base_shape_fn(date_str)
        mean_temp = weather_means.get(date_str)

        # Phase C: time-varying EV flag from household life events
        eff_property = property_record
        _has_battery = False
        _battery_kwh = 0.0
        if household_register is not None and customer_id is not None:
            dyn = household_register.dynamic_assets(customer_id, date_str)
            if dyn:
                assets = dict(property_record.get("assets") or {})
                assets["ev"] = dyn.get("ev", assets.get("ev", False))
                assets["solar"] = dyn.get("solar", assets.get("solar", False))
                eff_property = dict(property_record)
                eff_property["assets"] = assets
                _has_battery = dyn.get("battery", False)
                _battery_kwh = dyn.get("battery_kwh", 0.0)

        if mean_temp is None:
            shape = list(base_shape)
        else:
            irradiance = None
            if cloud_cover_means is not None and latitude_deg is not None:
                cloud_pct = cloud_cover_means.get(date_str)
                if cloud_pct is not None:
                    day_of_year = _date.fromisoformat(date_str).timetuple().tm_yday
                    irradiance = [
                        half_hourly_solar_irradiance(day_of_year, p, latitude_deg, cloud_pct)
                        for p in range(1, 49)
                    ]
            # Phase Q: battery dispatch replaces solar reduction in build_demand_shape.
            # Battery charges from excess solar, discharges 16:00-20:00 (periods 33-40).
            if _has_battery and _battery_kwh > 0.0 and irradiance is not None:
                _no_solar_prop = dict(eff_property)
                _no_solar_prop["assets"] = dict(_no_solar_prop.get("assets") or {})
                _no_solar_prop["assets"]["solar"] = False
                _gross = build_demand_shape(base_shape, mean_temp, "electricity", _no_solar_prop, None)
                shape = _battery_daily_dispatch(_gross, solar_generation_shape(irradiance), _battery_kwh)
            else:
                shape = build_demand_shape(base_shape, mean_temp, "electricity", eff_property, irradiance)

        # Phase C: EPC-band consumption multiplier
        if household_register is not None and customer_id is not None:
            epc_mult = household_register.epc_multiplier(customer_id, date_str)
            shape = [v * epc_mult for v in shape]

        # Phase I: ASHP electricity uplift -- HDD-weighted seasonal shape.
        # 70% space-heating (scales with HDD, same basis as gas boiler gas), 30% DHW (flat).
        # Replaces Phase G flat approximation. Annual total unchanged at ~5,500 kWh/yr.
        # Phase N: EV electricity demand -- flat load across all HH periods.
        # ~2,143 kWh/yr (7,500 mi / 3.5 mi/kWh). Applies from ev_acquired date.
        if household_register is not None and customer_id is not None:
            _hh = household_register.household_at_date(customer_id, date_str)
            if _hh is not None:
                _ashp_annual = _hh.ashp_annual_kwh()
                if _ashp_annual > 0:
                    _hdd_day = get_hdd(date_str, customer_id)
                    _hdd_ref = sum(REFERENCE_MONTHLY_HDD.values())
                    _daily_heating = _ashp_annual * 0.70 * (_hdd_day / _hdd_ref)
                    _daily_dhw = _ashp_annual * 0.30 / 365.25
                    _ashp_hh_kwh = (_daily_heating + _daily_dhw) / 48
                    shape = [v + _ashp_hh_kwh for v in shape]
                # Phase P: overnight-weighted EV shape (90% periods 47-48, 1-14).
                # Replaces Phase N flat distribution. Annual total conserved.
                _ev_annual = _hh.ev_annual_kwh()
                if _ev_annual > 0:
                    _ev_daily = _ev_annual / 365.25
                    _ev_on = _ev_daily * _EV_OVERNIGHT_FRACTION / len(_EV_OVERNIGHT_PERIODS)
                    _ev_day = _ev_daily * _EV_DAYTIME_FRACTION / (48 - len(_EV_OVERNIGHT_PERIODS))
                    shape = [v + (_ev_on if (p + 1) in _EV_OVERNIGHT_PERIODS else _ev_day)
                             for p, v in enumerate(shape)]

        return shape

    return shape_fn


def _clamp_term_end(term_start: str, end_date: str = REPORT_END) -> str:
    natural = (date.fromisoformat(term_start) + timedelta(days=CONTRACT_LENGTH_DAYS)).isoformat()
    if natural > end_date:
        return (date.fromisoformat(end_date) + timedelta(days=1)).isoformat()
    return natural


def _bootstrap_first_term_forward_price(
    term_start: str, gas_records: list[dict],
    contract_length_months: int = 12, lookback_days: int = 90, risk_factor: float = 1.2,
    lookback_daily_mean_temps_c: list[float] | None = None,
    fuel: str = "electricity",
) -> float:
    """Forward price for a customer's first gas term when NBP history begins
    on (not before) term_start — the standard 90-day-prior lookback in
    generate_forward_price() finds nothing and raises ValueError.

    Mirrors generate_forward_price() exactly but draws its window from the
    first lookback_days of *available* records (forward-looking bootstrap).
    One-time use for the very first term only.
    """
    start_date = date.fromisoformat(term_start)
    window_end = start_date + timedelta(days=lookback_days - 1)

    filtered_records = [
        record for record in gas_records
        if start_date <= date.fromisoformat(record["settlementDate"]) <= window_end
    ]

    # Use EWMA + term-structure formula (mirrors generate_forward_price reform)
    daily_buckets: dict[str, list[float]] = {}
    for r in filtered_records:
        daily_buckets.setdefault(r["settlementDate"], []).append(r["systemSellPrice"])
    daily_means = [
        statistics.mean(prices)
        for _d, prices in sorted(daily_buckets.items())
    ]
    effective_hl = min(EWMA_HALF_LIFE_DAYS, len(daily_means)) if daily_means else 1
    spot_ewma = _ewma(daily_means, effective_hl) if daily_means else 0.0
    seasonal = _seasonal_shape(start_date.month, contract_length_months, fuel)
    tenor_years = contract_length_months / 12.0
    base_premium = GAS_BASE_TERM_PREMIUM if fuel == "gas" else BASE_TERM_PREMIUM
    term_premium = base_premium * (tenor_years ** 0.5) * (risk_factor / DEFAULT_RISK_FACTOR)
    forward_price = spot_ewma * seasonal * (1.0 + term_premium)

    if lookback_daily_mean_temps_c is not None and fuel == "electricity":
        forward_price *= weather_sensitivity_multiplier(lookback_daily_mean_temps_c)

    return forward_price


def _build_gas_renewal_schedule(
    customer: dict, gas_records: list[dict], lookback_temps_fn=None,
    report_end: str = REPORT_END, tariff_type: str = "fixed",
) -> list[dict]:
    """Build renewal schedule for a gas customer using NBP forward prices.

    lookback_temps_fn (Phase 4c-3, optional): see
    `simulation.renewals.build_renewal_schedule` — same callable, threaded
    through to `generate_forward_price`'s `lookback_daily_mean_temps_c`.
    Phase 30b: gas CCL + GGL (policy) and gas network cost passed through in unit rate.
    """
    aq_kwh = customer["aq_kwh"]
    acq_date = customer["acquisition_date"]
    cust_segment = customer.get("segment", "resi")
    schedule = []
    term_start = acq_date

    while term_start <= report_end:
        term_end = _clamp_term_end(term_start, end_date=report_end)
        lookback_temps = lookback_temps_fn(term_start) if lookback_temps_fn else None
        try:
            sim_fwd = generate_forward_price(term_start, gas_records, lookback_daily_mean_temps_c=lookback_temps, fuel="gas")
        except ValueError:
            if not schedule:
                sim_fwd = _bootstrap_first_term_forward_price(
                    term_start, gas_records, lookback_daily_mean_temps_c=lookback_temps, fuel="gas"
                )
            else:
                break
        # Phase 34a: gas tariffs also priced NOTICE_DAYS before term start.
        gas_notice_date = (date.fromisoformat(term_start) - timedelta(days=NOTICE_DAYS)).isoformat()
        # KNIFE step 24 (§3s): WHICH forward the company prices gas off is its
        # own estimate, made behind the door -- the same door electricity has
        # used since B7. The world still owns the cold-start fallback it hands
        # over, which is the leak §3a records as owed.
        company_fwd = request_company_forward_estimate(
            commodity="gas",
            notice_date=gas_notice_date,
            observable_price_records=gas_records,
            fallback_gbp_per_mwh=sim_fwd,
        )
        # Phase 30b: gas policy cost (CCL + GGL) and network charges pass-through.
        # CCL: domestic gas exempt; GGL applies from Nov 2021.
        gas_policy = (
            get_gas_ccl_per_mwh(term_start, cust_segment)
            + get_ggl_per_mwh(term_start, aq_kwh)
        )
        gas_network = get_gas_network_cost_per_mwh(term_start)
        # KNIFE step 25 (§3t): WHICH of the published components this product
        # locks at signing (Phase 40b), the naked fraction the capital cost is
        # priced on, and the strike itself are ONE act and it is the supplier's.
        # The world publishes the levy and network schedules; it was also
        # reading them on the company's behalf. Electricity has struck its rate
        # behind `quote_renewal` since B7 -- gas now uses the same
        # implementation, not a second copy that agreed by inspection.
        _gas_strike = request_fixed_unit_rate(
            tariff_type=tariff_type,
            company_forward_price_gbp_per_mwh=company_fwd,
            eac_kwh=aq_kwh,
            term_start=term_start,
            published_policy_cost_per_mwh=gas_policy,
            published_network_cost_per_mwh=gas_network,
        )
        unit_rate = _gas_strike.unit_rate_gbp_per_mwh
        schedule.append({
            "acquisition_date": term_start,
            "notice_date": gas_notice_date,
            "term_end": term_end,
            "forward_price_gbp_per_mwh": sim_fwd,
            "company_forward_price_gbp_per_mwh": company_fwd,
            "unit_rate_gbp_per_mwh": unit_rate,
            "tariff_type": tariff_type,
        })
        term_start = term_end  # next term starts where this ends

    return schedule


def _build_churn_basis_risk(customer_events_log: list) -> list[dict]:
    """Phase 11b + 39a: Build churn basis risk records with SVT comparison."""
    from simulation.svt_rates import get_svt_elec_rate_gbp_per_mwh

    records = []
    for e in customer_events_log:
        if e.get("company_churn_estimate") is None:
            continue
        unit_rate = e.get("unit_rate_gbp_per_mwh")
        term_start = e["event_date"]
        svt_rate = get_svt_elec_rate_gbp_per_mwh(term_start)
        rate_vs_svt_pct = None
        if unit_rate is not None and svt_rate is not None and svt_rate > 0:
            rate_vs_svt_pct = round((unit_rate - svt_rate) / svt_rate * 100.0, 2)
        records.append({
            "customer_id": e["customer_id"],
            "term_start": term_start,
            "sim_churn_probability": e.get("realized_churn_probability", e["churn_probability"]),
            "company_churn_estimate": e["company_churn_estimate"],
            "churn_estimate_error_pct": e["churn_estimate_error_pct"],
            "is_active_renewal": e.get("is_active_renewal", True),
            "unit_rate_gbp_per_mwh": unit_rate,
            "svt_rate_gbp_per_mwh": svt_rate,
            "rate_vs_svt_pct": rate_vs_svt_pct,
        })
    return records


def _build_company_event_log(
    customer_events_log: list,
    won_successor_activations: dict,
    fresh_acquisitions: list,
    successor_map: dict,
) -> list:
    """Build the company CRM event log from simulation outputs — Phase 12a.

    Returns a list of dicts (one per event) that the company CRM knows about.
    Churn events come from customer_events_log; acquisition events come from
    won_successor_activations (home-move wins) and fresh_acquisitions (market wins).
    """
    result = []
    for evt in customer_events_log:
        if evt["event_type"] == "churned":
            result.append({
                "event_type": "churn",
                "customer_id": evt["customer_id"],
                "event_date": evt["event_date"],
                "reason": "non-renewal",
                "sim_churn_probability": evt.get("realized_churn_probability", evt.get("churn_probability")),
                "company_churn_estimate": evt.get("company_churn_estimate"),
            })
    for successor_id, activation_date in won_successor_activations.items():
        predecessor = next(
            (p for p, s in successor_map.items() if s == successor_id), None
        )
        result.append({
            "event_type": "acquisition",
            "customer_id": successor_id,
            "event_date": activation_date,
            "channel": "home-move-win",
            "predecessor_id": predecessor,
        })
    for acq in fresh_acquisitions:
        result.append({
            "event_type": "acquisition",
            "customer_id": acq["customer_id"],
            "event_date": acq["event_date"],
            "channel": "market-acquisition",
            "predecessor_id": acq.get("predecessor_id"),
        })
    return sorted(result, key=lambda e: e["event_date"])


def _compute_company_divergence(
    basis_risk_terms: list[dict],
    churn_basis_risk: list[dict],
    demand_estimation_log: list[dict] | None = None,
) -> dict:
    """Aggregate company-model divergence from SIM ground truth, by year -- Phase 12e/23a.

    basis_risk_terms: per-term tariff pricing error (tariff_error_pct = signed)
    churn_basis_risk: per-renewal churn estimate error (churn_estimate_error_pct = signed, may be None)
    demand_estimation_log: per-renewal EAC estimation error (Phase 23a)
    Returns: {tariff_error_by_year, churn_error_by_year, demand_error_by_year}
    """
    by_year_tariff: dict[str, list[float]] = defaultdict(list)
    for b in basis_risk_terms:
        by_year_tariff[b["term_start"][:4]].append(abs(b["tariff_error_pct"]))

    by_year_churn: dict[str, list[float]] = defaultdict(list)
    for c in churn_basis_risk:
        if c.get("churn_estimate_error_pct") is not None:
            by_year_churn[c["term_start"][:4]].append(abs(c["churn_estimate_error_pct"]))

    by_year_demand: dict[str, list[float]] = defaultdict(list)
    for d in (demand_estimation_log or []):
        by_year_demand[d["term_start"][:4]].append(abs(d["error_pct"]))

    def _summarize(by_year: dict) -> dict:
        return {
            yr: {
                "n": len(errs),
                "mean_abs_error_pct": round(sum(errs) / len(errs), 4),
                "max_abs_error_pct": round(max(errs), 4),
            }
            for yr, errs in sorted(by_year.items())
        }

    return {
        "tariff_error_by_year": _summarize(by_year_tariff),
        "churn_error_by_year": _summarize(by_year_churn),
        "demand_error_by_year": _summarize(by_year_demand),
    }


def _as_fold(settled) -> SettlementFold:
    """Accept either the fold or a plain list of records.

    The list branch is for the tests that pin these two functions directly (they hand over a
    handful of hand-built records, which is the clearest way to state what the function means).
    The RUN never takes it: `main` builds one fold and feeds it once, because a second fold
    built from a different slice of the book is exactly the point-in-time drift these functions
    must not have.
    """
    if isinstance(settled, SettlementFold):
        return settled
    fold = SettlementFold()
    fold.add(settled or [])
    return fold


def _derive_eac_from_settlement(cid: str, settled) -> float:
    """Mean actual annual consumption from all available settlement records.

    Phase 25a: used as SIM oracle for the demand_estimation_log, replacing
    the declared EAC (EFFECTIVE_EAC_KWH) which mismatches actual consumption
    for EV customers (C2/C4: declared 3500/5500 kWh, actual ~6820 kWh with EV).
    Falls back to EFFECTIVE_EAC_KWH when fewer than 180 days of records exist.

    2026-08-24: reads a running fold instead of filtering the whole settled book by
    customer_id. Same answer, from O(1) lookups rather than a scan whose cost grows with
    everything every other customer has ever settled -- see `simulation/settlement_fold.py`
    for the measurement that made this the run's only quadratic term.
    """
    fold = _as_fold(settled)
    if not fold.has_records(cid):
        return EFFECTIVE_EAC_KWH.get(cid, 0.0)
    total_days = fold.span_days(cid)
    if total_days < 180:
        return EFFECTIVE_EAC_KWH.get(cid, 0.0)
    return fold.total_consumption_kwh(cid) / total_days * 365.25


def _company_eac_estimate(
    cid: str, term_start_str: str, settled,
    base_eac_override: float | None = None,
) -> float:
    """Estimate customer annual consumption from observable prior-year billing records.

    Phase 23a: replaces SIM-internal EFFECTIVE_EAC_KWH lookup in company-layer decisions.
    The company observes kWh billed in the 12 months before the renewal date.
    Falls back to EFFECTIVE_EAC_KWH on the first term (no prior billing yet).

    Phase H: base_eac_override replaces the EFFECTIVE_EAC_KWH fallback when provided.
    Allows the caller to supply a household-model-adjusted base (EV/solar/ASHP multiplied).

    2026-08-24: the 12-month window is now answered from per-day totals rather than by
    filtering the whole book. The WINDOW IS UNCHANGED and still half-open -- `[year_ago,
    term_start)` -- because it is the point-in-time blindfold, not an implementation detail.
    """
    from datetime import date as _date

    from simulation.customer_events import twelve_month_window_open

    term_start = _date.fromisoformat(term_start_str)
    # NOT `term_start.replace(year=...)`: that raises on a term starting 29 February and took
    # the whole run down the first time the book held one. See the helper for the convention
    # and for why it opens on 1 March rather than 28 February.
    year_ago = twelve_month_window_open(term_start)
    estimated = _as_fold(settled).consumption_kwh_between(
        cid, year_ago.isoformat(), term_start.isoformat())
    base = base_eac_override if (base_eac_override is not None) else EFFECTIVE_EAC_KWH.get(cid, 0.0)
    return estimated if estimated > 0 else base


def _domestic_flex_assets_by_date(
    household_register,
    report_years: list[str],
    customer_ids: list[str],
) -> dict[str, dict[str, dict]]:
    """Resolve the world's asset register into the snapshot the flex door takes.

    KNIFE pass 3 step 18 (register §3m). The company's flexibility book used to
    be handed this register and pull `dynamic_assets` out of it; now the pull
    happens here, on the world's side, and only the answers cross.

    `year_end` serves as BOTH the query date and the snapshot key, deliberately:
    that is what makes it impossible to file one year's assets under another
    year's date, which would silently reprice the whole portfolio. Customer
    order is preserved because the book prices in the order it is given.
    """
    snapshot: dict[str, dict[str, dict]] = {}
    for year_str in report_years:
        year_end = f"{int(year_str)}-12-31"
        snapshot[year_end] = {
            cid: household_register.dynamic_assets(cid, year_end)
            for cid in customer_ids
        }
    return snapshot


def _ic_flex_roster(elec_customers: list[dict], eac_by_cid: dict) -> list[tuple]:
    """The I&C electricity book, as the flex door takes it.

    KNIFE pass 3 step 18 (register §3m). The `segment == "I&C"` filter is the
    one thing this cut genuinely put at risk: drop it and every domestic
    customer is offered to an I&C aggregator, which changes the flexibility
    total while every test exercising the book directly stays green, because the
    book would be given exactly what this function chose to give it.
    """
    return [
        (c["customer_id"], eac_by_cid.get(c["customer_id"], 0.0))
        for c in elec_customers
        if c.get("segment") == "I&C"
    ]


def campaign_acquisition_spend_events(report_end: str = REPORT_END) -> list[dict]:
    """The growth campaign's quotes, booked as acquisition spend. PB3 exit (c), 2026-08-25.

    THE DEFECT THIS CLOSES, measured on unmodified HEAD at the shipped configuration. The
    two `acquisition_spend_events.append` sites in `main` both sit inside the CHURN branch of
    the replacement path, so the only acquisition spend that ever reached
    `company.finance.accounting_close.close_the_books` — and therefore the only spend that
    ever reached the P&L — was the cost of replacing customers who had left. The ten-year
    growth campaign beside it, which won 244 of the book's 264 accounts, issued **1,295
    quotes and spent £157,155**, and booked none of it. The total was summed into
    `docs/observability/book_growth_campaign.json` and held in
    `simulation.live_population.LAST_CAMPAIGN`; neither is a ledger. The published run
    reported **£5,587.50** of acquisition spend (`site/data/dashboard.json`,
    `financial.ledger.acquisition_spend_gbp`) over **43** `acquisition_spend_event` rows
    (`docs/reports/ANNUAL_REPORT.md`). 96.4% of what this supplier spent winning customers
    was missing from its own accounts.

    IT IS THE ATOM'S OWN MECHANISM, not a reporting tidy-up. The ruling names three —
    *"churn, acquisition cost, and the competitor field are the mechanisms"* — and a growth
    curve whose cost is booked to a JSON file cannot be lost on price, because losing costs
    nothing and quoting is free. This is exit criterion (c)'s "costs a penny" clause applied
    to the earned half of the book. The activation record for this very campaign told the
    director *"Growth costs money. 245 quotes were paid for and 231 lost"*; in the accounts
    they were not.

    THROUGH THE `growth_desk` DOOR, the same one the replacement path uses two screens below.
    What an attempt COST is company accounting — the wall `run_acquisition_funnel` states in
    its own docstring, which is why `total_amount_gbp` is a required INPUT to the funnel
    rather than something the world looks up. So the world resolves who was quoted and what
    the attempt cost it, and the supplier books it. `won` rides along unchanged, so cost per
    acquisition stays derivable and a lost quote stays what it is: spend with no account
    against it, which is exactly what makes acquisition cost something this company can get
    wrong.

    WITHIN THE REPORTED PERIOD, filtered rather than assumed, and against `report_end` — the
    run's EFFECTIVE end — rather than the constant, so a truncated window does not post a
    decade of cost into a close that stops in March. At the shipped full window it excludes
    nothing: all 1,295 rows fall inside it, asserted rather than claimed in
    `test_c_the_window_filter_excludes_nothing_at_the_shipped_configuration`.

    RETURNS `[]` WITH THE GROWTH MANDATE OFF, because `_campaign` short-circuits to an empty
    outcome there — so the default path books exactly what it booked before, and the null
    control that proves the measured spend is the CAMPAIGN's rather than a re-labelling of
    the replacement path's is a real one.
    """
    return [
        book_acquisition_spend(
            billing_account=quote["prospect_id"],
            event_date=quote["event_date"],
            amount_gbp=quote["amount_gbp"],
            won=quote["won"],
            segment=quote["segment"],
        )
        for quote in campaign_quotes_paid_for()
        if REPORT_START <= quote["event_date"] <= report_end
    ]


def main(report_end: str | None = None, policy: DecisionPolicy | None = None,
         gap_ledger_path=None):
    """Run one simulation under its own fresh competitive-pressure ledger.

    NO `sim_interface` PARAMETER, DELIBERATELY (2026-08-29). This function used to accept
    one and route five `notify_*` calls through `if sim_interface is not None`. No
    production entry point ever passed an interface — `run_phase4c_on_phase2b`,
    `run_phase4b_on_phase2b`, `run_phase3a` and `run_scenario` all left it None — so the
    company's `CompanyEventLog` was constructed and never written on any path behind a
    published figure, and the only callers that filled it were four tests with a stub.
    That is the same shape that made the competitive-pressure ledger's first live
    measurement worthless (see the comment at the churn booking below), and an
    accepted-but-ignored parameter is worse than none: a caller can pass one and silently
    get nothing back. The `SimInterface.notify_*` methods stay — they are the COMPANY's
    API for recording what the company itself observed, which is what a real supplier's
    CRM is. What was wrong was the WORLD calling them: an event stream the sim hands over
    is not the company's record of what it saw, and reconciling the two was a mirror
    (`saas/reporting/annual_report.py::_section_company_crm`). When the company gets its
    own writer, it books from the company side.

    The ledger is COMPANY STATE and stays on the company side of the wall: this function opens
    the scope, and nothing in `simulation/` reads it. What accumulates into it is booked by
    `company/crm/churn_desk` (what the company believed) and by the unconditional
    `observe_competitive_loss` call at every departure below, and only
    `company/crm/competitive_pressure` reads it back.

    ONE LEDGER PER RUN, OPENED HERE rather than by each caller, because the callers that most
    need it are the two arms of an A/B: a ledger shared between them would let the control arm's
    realised losses inform the treatment arm's beliefs, and on a comparison whose entire subject
    is the difference between the arms that is not a leak, it is a fabricated result. Opening it
    at the single entry point every run passes through means no caller can forget.
    """
    with pressure_ledger_scope():
        return _main(report_end=report_end, policy=policy,
                     gap_ledger_path=gap_ledger_path)


def _main(report_end: str | None = None, policy: DecisionPolicy | None = None,
          gap_ledger_path=None):
    """Run the full Phase 2b + 4c settlement simulation.

    report_end: ISO date string (e.g. "2022-12-31") to truncate the
        simulation window for faster iteration. Defaults to REPORT_END
        (the full 2016-2025 window). Use --end-year on the annual_report
        CLI or pass directly for experiment runs.
    policy: swappable retention/hedging decision policy (FROZEN_POLICY_BASELINE_DESIGN.md
        option B). Defaults to CURRENT_POLICY -- every existing caller sees zero
        behaviour change. tools/run_frozen_baseline.py passes NAIVE_POLICY for the
        superseded pre-14a/15b/43b comparison run.
    gap_ledger_path: where the live payment triad publishes its coupled-gap entry.
        Defaults to None, i.e. the LIVE observability ledger -- correct for a real run
        and refused outright inside a test process by `live_ledger_guard`.

        THE INJECTION POINT EXISTED AND STOPPED ONE LEVEL SHORT (2026-08-27).
        `LivePaymentTriad.measure_and_write` already took `ledger_path=`, and the guard's
        own refusal message tells the caller to "pass an explicit ledger_path=tmp_path"
        -- but `main()` had no way to express it, so EVERY test running the full pipeline
        hit the guard and there was no legal way past. That is a control correctly
        refusing an action nobody could avoid: the fix is a route, never a weakening of
        the guard, which exists because a test's 276-invoice fixture book once overwrote
        the real ledger and republished the public Proof door 2.68x too low.
    """
    effective_end = report_end or REPORT_END
    policy = policy or CURRENT_POLICY
    # A run's policy identity must be ONE thing (2026-08-12, closing
    # WORKER_FINDING_THE_NAIVE_ARM_KEEPS_THE_LIVE_TONE_2026-08-10). Fields this
    # function is handed come from `policy`; the collections letter tone is
    # resolved without an argument, from the active scope, deep in the arrears
    # path. If those two disagree the run is a chimera -- naive retention with
    # current dunning letters -- and the frozen baseline's delta silently
    # attributes an uncontrolled variable to the policy change. Refusing here is
    # fail-CLOSED: the default scope IS CURRENT_POLICY, so every caller that
    # passes nothing, or passes CURRENT_POLICY, is unaffected; only a caller
    # that swaps the policy without swapping the scope is stopped, and it is
    # stopped loudly rather than producing a plausible wrong number.
    if policy is not active_policy():
        raise ValueError(
            "run_phase2b was given policy=%r but the active policy scope is %r. "
            "Wrap the run in company.policy.decision_policy.policy_scope(policy) "
            "so argument-less consumers (the collections-communication seam) "
            "resolve the same policy this run claims to be executing."
            % (policy.name, active_policy().name)
        )
    print("=== Phase 2b — Gas Dual Fuel ===")
    print(f"Electricity customers: {[c['customer_id'] for c in ELEC_CUSTOMERS]}")
    print(f"Gas customers:         {[c['customer_id'] for c in GAS_CUSTOMERS]}")
    print(f"Elec EAC: {TOTAL_ELEC_EAC:,.0f} kWh  Gas AQ: {TOTAL_GAS_AQ:,} kWh")
    print(f"Starting treasury: £{STARTING_TREASURY_GBP:.2f}")
    if effective_end != REPORT_END:
        print(f"[Truncated window: {REPORT_START} to {effective_end}]\n")
    else:
        print()

    # ---- Load price feeds ----
    earliest_acq = min(
        date.fromisoformat(c["acquisition_date"])
        for c in ELEC_CUSTOMERS + GAS_CUSTOMERS
    )
    fetch_start_natural = (earliest_acq - timedelta(days=365)).isoformat()
    fetch_start = max(fetch_start_natural, EARLIEST_SSP_DATE)

    cached = get_cached_prices(fetch_start, effective_end)
    if cached is not None:
        elec_records = cached
        print(f"Cache hit: {len(elec_records):,} SSP records.")
        log_cache_access("elexon_ssp_full.json", hit=True, phase="2b")
    else:
        elec_records = get_system_prices_range(fetch_start, effective_end)
        log_cache_access("elexon_ssp_full.json", hit=False, phase="2b")
    print(f"Electricity: {len(elec_records):,} SSP records ({fetch_start} to {effective_end}).")

    gas_records = load_nbp_history()
    print(f"Gas: {len(gas_records):,} NBP daily records.\n")

    # M1 depth work (docs/design/M1_PRICE_HISTORY_PIPELINE_FINDING.md): built
    # ONCE per run from the sim's own records, structurally replacing
    # _price_history_as_of()'s per-call-site bisect-slice. Every hedge
    # decision constructs a fresh, cheap PointInTimeView wrapping this SAME
    # shared log with its own decision_time -- the bound lives on the view,
    # not in caller memory.
    _price_bitemporal_log = build_price_bitemporal_log(elec_records, gas_records)

    elec_price_lookup = {
        (r["settlementDate"], r["settlementPeriod"]): r["systemSellPrice"]
        for r in elec_records
    }

    # Phase MT: pre-compute Triad alert set for I&C demand curtailment.
    # Identifies (date, period) pairs where SSP signals a Triad risk window.
    _ic_triad_alert_set = build_triad_alert_set(elec_records)

    # ---- Phase 4c-1/4c-2/4c-3 inputs: per-customer weather + property records ----
    # B12: the DWELLING is the world's. Both of these take the world's own drawn
    # dwelling for every SYN-* home; omit them and each drawn home reverts to the
    # supplier's modal-band approximation ("D"), which the company then scores itself
    # right against by construction.
    _drawn_dwellings = live_dwellings()
    properties = build_properties(CUSTOMERS, dwellings=_drawn_dwellings)
    # Phase C: household physical model (EPC multipliers, time-varying EV/solar)
    household_demand_register = HouseholdDemandRegister(
        CUSTOMERS, drawn_households=live_drawn_households()
    )
    weather_by_customer = {
        c["customer_id"]: weather_means_for_customer(c)
        for c in ELEC_CUSTOMERS + GAS_CUSTOMERS + SUCCESSOR_ELEC_CUSTOMERS
    }
    # Phase O: cloud cover for all elec customers — any can acquire solar via life events.
    cloud_cover_by_customer = {
        c["customer_id"]: cloud_cover_for_customer(c)
        for c in ELEC_CUSTOMERS + SUCCESSOR_ELEC_CUSTOMERS
    }

    # Phase 6a: per-customer HH consumption for HH (smart meter) customers.
    hh_consumption_by_customer = {
        c["customer_id"]: load_hh_consumption(c["customer_id"])
        for c in ELEC_CUSTOMERS if is_hh_customer(c)
    }

    # ---- W1_11 L2->L3: THE SETTLEMENT SWITCH ----
    # Fabric physics REPLACES the rescaled national PC1 shape as the demand
    # PROVIDER for eligible domestic premises. Until this line, the company had
    # never faced the fabric world on the path it actually settles, bills and
    # hedges on -- the coupling was a side panel (tools/couple_fabric.py) standing
    # beside the book. The provider changes; no consumer does.
    #
    # R12/R13 PRE-COMMITMENT (recorded before any downstream number was read): a
    # real premise is spikier than a rescaled national average and its annual
    # level is set by its FABRIC, not by its declared EAC. Imbalance cost and net
    # margin will very likely get WORSE and per-customer volumes will move
    # materially. That is the correct consequence of removing a smoothing
    # artefact, not a regression, and nothing here may be tuned to bring the old
    # numbers back. The declared EAC stays untouched: it is the company's BELIEF,
    # and the disagreement with the world is the coupled-triad gap.
    #
    # GAS IS DELIBERATELY NOT SWITCHED. `run_gas_term` takes an AQ, not a
    # shape_fn, and -- unlike electricity, whose EAC is re-estimated from billing
    # records each term (`_company_eac_estimate`) -- the gas AQ never reconciles
    # to settled volumes. Driving gas demand from fabric while the AQ belief stays
    # frozen at its declared value would lock in a permanent 4x hedge mismatch no
    # real supplier could carry, which is an absurdity, not a gap. The gas seam +
    # AQ reconciliation is registered as the next atom, not built here.
    _fabric_start = date.fromisoformat(REPORT_START)
    _fabric_end = date.fromisoformat(effective_end)
    fabric_series_by_customer, fabric_eligibility_verdicts = fabric_providers_for_book(
        customers=ELEC_CUSTOMERS + SUCCESSOR_ELEC_CUSTOMERS,
        household_at_date=household_demand_register.household_at_date,
        is_half_hourly_metered=is_hh_customer,
        weather_site_for=_weather_source_customer_id,
        weather_available=lambda site: (WEATHER_DATA_DIR_PATH / f"{site}.csv").exists(),
        latitude_for=lambda c: c.get("location", {}).get("lat") or DEFAULT_LATITUDE_DEG,
        start=_fabric_start,
        end=_fabric_end,
    )
    demand_provider_by_customer: dict[str, str] = {}
    print(f"Fabric-driven premises (W1_11 settlement switch): "
          f"{sorted(fabric_series_by_customer)}")
    for _v in fabric_eligibility_verdicts:
        if not _v.is_eligible:
            print(f"  {_v.customer_id}: legacy provider -- {_v.reason}")

    def _fabric_battery_dispatch_for(cid: str):
        """The one composition `fabric_shape_fn` leaves to the caller. The trace
        models PV but not the battery, so the battery is dispatched here against
        the trace's own gross load and generation -- the same function, and the
        same 16:00-20:00 discharge window, the legacy path uses."""
        def dispatch(gross: list[float], generation: list[float], date_str: str) -> list[float]:
            dyn = household_demand_register.dynamic_assets(cid, date_str) or {}
            battery_kwh = dyn.get("battery_kwh", 0.0) if dyn.get("battery") else 0.0
            if not battery_kwh:
                return [g - p for g, p in zip(gross, generation)]
            return _battery_daily_dispatch(gross, generation, battery_kwh)
        return dispatch

    # W1_11: the THIRD control, and the only one that reads the numbers. The two
    # controls at the end of this function judge the provider LABEL and the
    # DECLARATION -- both pass unchanged on a book where every fabric premise is
    # handed the rescaled national shape, because the label is assigned by the same
    # branch that builds the callable and so can never disagree with itself. This
    # one consumes the SAME shape_fn term pricing is about to receive, downstream of
    # PV netting, battery dispatch and the zero floor, and fires if what arrives at
    # settlement is texturally the artefact the switch exists to replace. Sampled
    # rather than exhaustive: a fortnight from each end of the window costs nothing
    # and a rescaled shape recurs on 100% of days by construction, so it cannot hide
    # in the unsampled middle.
    for _fab_cid, _fab_series in sorted(fabric_series_by_customer.items()):
        _sample_dates = sorted(_fab_series.gross_electricity_kwh)
        _sample_dates = _sample_dates[:14] + _sample_dates[-14:]
        if not settled_shape_is_physically_textured(
            fabric_shape_fn(
                _fab_series,
                "electricity",
                battery_dispatch=_fabric_battery_dispatch_for(_fab_cid),
            ),
            _sample_dates,
        ):
            raise AssertionError(
                f"{_fab_cid} settles on the fabric provider but the shape reaching "
                "settlement is a rescaled base shape, not physics: the switch is "
                "labelled but not thrown"
            )
        # W1_11 L2->L3: the FOURTH control, and the only one that asks whether the
        # switch is INERT. Its three siblings judge the label, the declaration and
        # the texture -- all three stay green on a book whose fabric premises settle
        # exactly the volume the legacy provider would have given them. A textured
        # shape integrating to the same annual kWh is economically invisible, and a
        # demand-generator switch that moves no volume has not reached the book.
        # Built against the same legacy provider the else-branch below constructs,
        # so this is the real counterfactual, not a reconstruction of one.
        _legacy_customer = get_customer(_fab_cid)
        if not the_switch_moves_the_settled_volume(
            fabric_shape_fn(
                _fab_series,
                "electricity",
                battery_dispatch=_fabric_battery_dispatch_for(_fab_cid),
            ),
            _weather_adjusted_shape_fn(
                SHAPE_LOADERS[_legacy_customer.get("profile_class", 1)],
                weather_by_customer[_fab_cid],
                properties.get(_fab_cid, DEFAULT_PROPERTY),
                cloud_cover_means=cloud_cover_by_customer.get(_fab_cid),
                latitude_deg=_legacy_customer.get("location", {}).get("lat"),
                household_register=household_demand_register,
                customer_id=_fab_cid,
            ),
            _sample_dates,
        ):
            raise AssertionError(
                f"{_fab_cid} settles on the fabric provider but its settled volume "
                "is indistinguishable from the legacy provider's: the switch is "
                "labelled and textured but INERT"
            )

    def _lookback_temps_fn(cid):
        weather_means = weather_by_customer[cid]
        return lambda term_start: lookback_mean_temps(weather_means, term_start)

    # ---- Build electricity schedules ----
    elec_schedules = {}
    for c in ELEC_CUSTOMERS:
        elec_schedules[c["customer_id"]] = build_renewal_schedule(
            c["customer_id"], c["acquisition_date"], effective_end,
            elec_records, EFFECTIVE_EAC_KWH[c["customer_id"]],
            lookback_temps_fn=_lookback_temps_fn(c["customer_id"]),
            segment=c.get("segment", "resi"),
            tariff_type=c.get("tariff_type", "fixed"),
            deemed_gap_days=c.get("deemed_gap_days", 0),
        )

    # Phase 7e: pre-generate successor schedules (gated until activation).
    # Successors use the same acquisition_date as their predecessor so the
    # term schedule aligns — actual settlement only starts at the churn date.
    for c in SUCCESSOR_ELEC_CUSTOMERS:
        elec_schedules[c["customer_id"]] = build_renewal_schedule(
            c["customer_id"], c["acquisition_date"], effective_end,
            elec_records, EFFECTIVE_EAC_KWH[c["customer_id"]],
            lookback_temps_fn=_lookback_temps_fn(c["customer_id"]),
            segment=c.get("segment", "resi"),
        )

    # ---- Build gas schedules ----
    gas_schedules = {}
    for c in GAS_CUSTOMERS:
        gas_schedules[c["customer_id"]] = _build_gas_renewal_schedule(
            c, gas_records, lookback_temps_fn=_lookback_temps_fn(c["customer_id"]),
            report_end=effective_end, tariff_type=c.get("tariff_type", "fixed"),
        )

    # ---- Interleave all terms chronologically ----
    all_terms = []
    for cid, schedule in elec_schedules.items():
        for term in schedule:
            all_terms.append((term["acquisition_date"], cid, "electricity", term))
    for cid, schedule in gas_schedules.items():
        for term in schedule:
            all_terms.append((term["acquisition_date"], cid, "gas", term))
    all_terms.sort(key=lambda x: (x[0], x[1]))

    # ---- Simulation state ----
    treasury = STARTING_TREASURY_GBP
    monitor = RiskCommitteeMonitor(treasury)

    all_customers_ids = (
        [c["customer_id"] for c in ELEC_CUSTOMERS]
        + [c["customer_id"] for c in GAS_CUSTOMERS]
        + [c["customer_id"] for c in SUCCESSOR_ELEC_CUSTOMERS]
    )
    # Phase 7e: successor_id → activation_date (set when home-move is won).
    # Gate: successor terms are skipped until their activation date.
    won_successor_activations: dict[str, str] = {}
    next_hf = {cid: RESET_HEDGE_FRACTION for cid in all_customers_ids}
    pending_committee_overrides: dict[str, float] = {}
    current_risk: dict[str, dict] = {}
    current_hf: dict[str, float] = {cid: RESET_HEDGE_FRACTION for cid in all_customers_ids}

    # Phase 16c + 19a: track prior-term realized margin + revenue per customer (all commodities)
    # Gas customers use separate CIDs (C1g, C2g, etc.) so this dict works for both.
    prev_term_margin: dict[str, float] = {}
    prev_term_revenue: dict[str, float] = {}
    margin_feedback_log: list[dict] = []
    profitability_uplift_log: list[dict] = []
    # WRITER 3b's log (2026-08-26, the value cycle). Empty on every run of the control arm, which
    # is the point: an empty list here and a list of flat-margin choices are different facts, and
    # only one of them means "this run priced per customer".
    value_arm_log: list[dict] = []
    # THE DENOMINATOR OF `value_arm_log` (2026-08-28). One row per renewal the rate chain saw,
    # on EVERY arm including the control, carrying the guard that stopped it. Non-empty on the
    # control arm by design -- that is what makes "the world offered N renewals" readable from a
    # run in which the arm priced none, and it is why this is a separate list rather than more
    # rows in `value_arm_log` (whose emptiness under `flat_rules` the A/B asserts).
    value_arm_funnel_log: list[dict] = []
    # EP2 sub-atom 3 (2026-08-13, WORKER_FINDING_TWO_PRICING_LOOPS_...): four writers move one
    # `unit_rate` at renewal — the portfolio premium, the margin surcharge, the profitability
    # uplift and the domestic price cap. Each of their own logs used to record a before/after
    # pair as though it were the only writer, so no published pair spanned the move the customer
    # actually got. This is the ONE decomposed span per renewal: original -> contracted, with
    # each cause named and its own chained sub-span. The per-writer logs stay (each is now a
    # true link in the chain) but the contracted rate is only ever read from here.
    rate_decomposition_log: list[dict] = []
    demand_response_log: list[dict] = []   # Phase 52: per-term DR shift records
    hedge_var_log: list[dict] = []   # Trading & Market tab: realized VaR per hedge decision
    # Phase 22a: post-crisis hangover — how many more renewals get the +12% churn uplift
    hangover_remaining: dict[str, int] = {}
    # KNIFE step 21 (§3p): the company's four customer-experience books —
    # satisfaction, NPS, complaints, payment behaviour — now live behind one
    # door. The world reports what happened; the desk decides what it means.
    _cx_desk = CustomerExperienceDesk()
    _churn_journey_register = ChurnJourneyRegister()
    churn_journey_log: list[dict] = []
    # Phase RU: solicited feedback survey engine (FEEDBACK_AND_REPUTATION.md Layer 1)
    feedback_survey_log: list[dict] = []
    reputation_events_log: list[dict] = []
    # Nudge Physics Layer 1 (NUDGE_PHYSICS.md): SIM-side hidden companion to
    # retention_log's framing_type -- carries the true susceptibility and
    # effectiveness multiplier for Sim-tab verification only. Company code
    # must never read this log.
    nudge_physics_log: list[dict] = []
    # Phase NH: payment behaviour analytics -- three-signal churn model wiring
    # (now one arm of the customer-experience desk above, §3p)
    _payment_rng = random.Random(42 + 7919)
    _payment_month_seen: set[tuple[str, str]] = set()  # (cid, YYYY-MM)
    # L3 payment coupled triad (W2_11 source / W4_4 seam / D5 consumer / gap),
    # LIVE per-run. W2_11's generate_payment_event is now the CANONICAL payment
    # truth: the analytics dict below is DERIVED from that single event (one
    # coherent reality per customer/period), while emit_wall_responses ->
    # consumer.observe forms the company's observable-only belief and the gap is
    # measured + written at run end (background.live_payment_triad).
    _payment_triad = LivePaymentTriad()
    _NG_BILL_SHOCK_THRESHOLD = 0.20  # matches simulation.bill_shock_tracker.BILL_SHOCK_THRESHOLD
    CRISIS_HANGOVER_LOSS_THRESHOLD = 0.20  # trigger: net loss > 20% of term revenue

    # Phase 17a + 19a: rolling portfolio-wide margin rates for learning premium
    portfolio_elec_margin_rates: list[float] = []
    portfolio_gas_margin_rates: list[float] = []  # Phase 19a: separate gas tracking
    dynamic_pricing_log: list[dict] = []

    all_records: list[dict] = []
    # THE FOLD, fed at exactly one place -- the line that extends `all_records` below.
    # Fed anywhere else it would see records the list has not, and the point-in-time window
    # `_company_eac_estimate` depends on would quietly widen. `simulation/settlement_fold.py`
    # carries the measurement that put it here.
    settled_fold = SettlementFold()
    # THE TREASURY DRAWDOWN REGISTER, fed from the same single point for the same reason.
    # `treasury_cash_balance_gbp` is a PORTFOLIO running total stamped on each record as the
    # term loop produces it, so it means something in accumulation order and in no other; the
    # register walks the peaks and troughs HERE, while that order is still the one it is being
    # read in. `saas/reporting/annual_report.py` used to rebuild the path by re-sorting the
    # finished book into date order, which interleaves balances from different points in the
    # term loop and manufactured 6,747 phantom drawdown events in a 2017 that had none.
    treasury_drawdown = TreasuryDrawdown()
    # The three published figures a DAILY row cannot answer, folded from the same per-period
    # records as they are produced -- see simulation/settlement_daily.py for which figure
    # each serves and why a rescan afterwards is not an option once the periods are gone.
    period_registers = PeriodRegisters(is_peak_period=_is_peak_period)
    evolution_logs: dict[str, list] = {cid: [] for cid in all_customers_ids}
    term_indices: dict[str, int] = {cid: 0 for cid in all_customers_ids}
    # Phase NI: term-level rate shock counter. Replaces count_rate_shocks(all_records)
    # which incorrectly counted TOU peak/offpeak transitions as bill shocks for HH customers.
    _elec_rate_shock_counts: dict[str, int] = {}
    # Phase QV: per-year shock dates (SIM_TAB_OVERHAUL.md event frequency panel) --
    # _elec_rate_shock_counts above is an all-time rolling scalar; this retains
    # the actual term_start_str of each shock so the site can bucket per year.
    _bill_shock_dates: dict[str, list] = {}
    committee_wake_ups: list[dict] = []
    customer_events_log: list[dict] = []
    # THE RIVAL'S VIEW OF THIS COMPANY (2026-08-28, atom B10, director's C2). Run-scoped and
    # explicit: a module global would leak between runs and make the reference depend on
    # execution order, which is the non-determinism the seeded-run discipline forbids. It is
    # fed from the term loop AFTER each offer is struck and read a quarter later, so the world's
    # opponent moves on its own cycle rather than inside the term the company is pricing.
    _competitor_position_ledger = CompanyPositionLedger()
    churned_billing_accounts: set[str] = set()
    administration_event = None
    periods_since_committee = COMMITTEE_COOLDOWN_PERIODS
    last_committee_date: date = date.fromisoformat(REPORT_START) - timedelta(days=COMMITTEE_COOLDOWN_DAYS)
    total_periods_processed = 0
    PROGRESS_EVERY_PERIODS = 100

    # Phase 23a: demand estimation divergence tracking
    demand_estimation_log: list[dict] = []

    # Phase 43a: company trading book — forward position lifecycle.
    # KNIFE3 step 23 (§3r): the book is held by the DESK that opens positions in
    # it, decides the fractions those positions are sized at, settles them and
    # rolls the fraction forward. The world holds the desk, not the book.
    hedge_desk = build_hedge_desk()

    # Phase 8a: growth mandate tracking.
    # PB3 exit (c), 2026-08-25: SEEDED with the growth campaign's own quotes, which until now
    # were paid for and never booked. See `campaign_acquisition_spend_events`.
    acquisition_spend_events: list[dict] = campaign_acquisition_spend_events(effective_end)
    fixed_cost_events: list[dict] = []
    _acquisition_counter: dict[str, int] = {}  # base_id -> next fresh-acquisition suffix

    # PROCESS_NOT_EVENTS.md: acquisition as a funnel, not a coin flip.
    acquisition_funnel_log: list[dict] = []
    _credit_bureau = get_credit_bureau_adapter()
    _fixed_cost_emitted: set[str] = set()  # months already charged (dedup across customers)

    # Phase 11a: basis risk tracking — company_fwd vs sim_fwd per term
    basis_risk_terms: list[dict] = []
    # Phase 11b: track previous electricity unit rate per customer for churn estimate
    prev_elec_unit_rates: dict[str, float] = {}
    # Phase 14b: track previous gas unit rate for gas company churn estimate
    prev_gas_unit_rates: dict[str, float] = {}
    # Phase 12a: fresh acquisition wins for company_event_log
    fresh_acquisitions: list[dict] = []
    # Phase 12b: retention cost events and log
    retention_cost_events: list[dict] = []
    retention_log: list[dict] = []
    # Phase 12c: churns where no offer was made (missed opportunities)
    no_offer_churn_log: list[dict] = []
    # Phase 14b: gas renewal rate pressure log for dual-fuel monitoring
    company_gas_churn_log: list[dict] = []
    # Phase 27c: volume tolerance tracking for I&C customers
    volume_tolerance_log: list[dict] = []

    current_year_str = REPORT_START[:4]
    ytd_gross = ytd_net = ytd_capital = 0.0

    print("=== Processing terms chronologically ===\n")

    for term_start_str, cid, commodity, term in all_terms:
        if administration_event:
            break

        # Phase 6b: skip churned accounts (household level — covers both elec + gas legs).
        # KNIFE step 28 (§3w): the HOUSEHOLD, asked of the world, not the billing
        # account, asked of the supplier. The local name below is the supplier's
        # vocabulary and stays only because ~60 downstream uses and two run-record
        # output keys carry it; the VALUE no longer comes from a company module.
        billing_account = household_of(cid)
        if billing_account in churned_billing_accounts:
            term_indices[cid] += 1
            continue

        # Phase 7e: gate successor terms until activated by a home-move win.
        # Do NOT increment term_indices here — we want term_index=0 on first real term
        # so the churn roll doesn't fire prematurely.
        if cid in _SUCCESSOR_ELEC_IDS:
            activation_date = won_successor_activations.get(cid)
            if not activation_date or term_start_str < activation_date:
                continue

        term_end_str = term.get("term_end") or _clamp_term_end(term_start_str, end_date=effective_end)
        forward_price = term["forward_price_gbp_per_mwh"]        # sim's sophisticated estimate
        company_fwd = term.get("company_forward_price_gbp_per_mwh", forward_price)
        unit_rate = term["unit_rate_gbp_per_mwh"]
        term_tariff_type = term.get("tariff_type", "fixed")
        term_index = term_indices[cid]
        term_indices[cid] += 1

        # KNIFE step 24 (§3s): EVERY writer that moves this renewal's rate --
        # the portfolio learning premium, the realised-margin recovery
        # surcharge, the unprofitability uplift and the price-cap clamp -- is
        # the supplier's own pricing policy, including WHICH renewals each one
        # applies to and the ORDER they fire in. They form one chain producing
        # one number, so they are one door: company/interfaces/renewal_rate_chain.py.
        # The world reports the renewal as it happened and records what came back.
        _chain = decide_renewal_rate(
            customer_id=cid,
            billing_account=billing_account,
            commodity=commodity,
            term_start=term_start_str,
            tariff_type=term_tariff_type,
            term_index=term_index,
            struck_unit_rate_gbp_per_mwh=unit_rate,
            portfolio_margin_rates=(
                portfolio_elec_margin_rates if commodity == "electricity"
                else portfolio_gas_margin_rates
            ),
            prior_term_margin_gbp=prev_term_margin.get(cid),
            prior_term_revenue_gbp=prev_term_revenue.get(cid, 0.0),
            is_domestic=cid in _RESI_CUSTOMER_IDS,
            # `_SEGMENT_OF` already exists here for the Triad carve-out, so the fact the
            # renewal desk was missing was three lines away the whole time.
            segment=_SEGMENT_OF.get(cid, "resi"),
            settled_records=all_records,
        )
        unit_rate = _chain.unit_rate_gbp_per_mwh
        dynamic_pricing_log.extend(_chain.dynamic_pricing_entries)
        margin_feedback_log.extend(_chain.margin_feedback_entries)
        profitability_uplift_log.extend(_chain.profitability_uplift_entries)
        value_arm_log.extend(_chain.value_arm_entries)
        value_arm_funnel_log.extend(_chain.arm_funnel_entries)
        if _chain.decomposition is not None:
            rate_decomposition_log.append(_chain.decomposition)

        # Phase 11a: record basis risk (company estimate vs sim ground truth)
        basis_risk_terms.append({
            "customer_id": cid,
            "commodity": commodity,
            "term_start": term_start_str,
            "company_fwd_gbp_per_mwh": company_fwd,
            "sim_fwd_gbp_per_mwh": forward_price,
            "tariff_error_pct": (company_fwd - forward_price) / forward_price if forward_price else 0.0,
        })

        # Phase 11b + 14b: capture previous rates before updating.
        # Phase 40c: skip for deemed terms (no fixed unit_rate to record or compare).
        old_elec_rate = prev_elec_unit_rates.get(cid) if commodity == "electricity" else None
        old_gas_rate = prev_gas_unit_rates.get(cid) if commodity == "gas" else None
        # `svt` joins the indexed tariffs (2026-08-30, brief WORK item 4). It belongs here for
        # the same reason `deemed` and `flex` do and for one more: those two have no RENEWAL
        # because their price is indexed, and an SVT segment has no renewal because there is no
        # TERM -- a segment boundary is a cap change, not an expiry. Gating it out here is what
        # makes "no renewal decision" a property of the product rather than a claim about it.
        # An SVT account therefore cannot depart yet, which is exactly why no roster assigns
        # one; see simulation/svt_product.py on what is owed before assignment.
        _indexed_tariff = term_tariff_type in ("deemed", "flex", SVT_TARIFF_TYPE)
        if commodity == "electricity" and not _indexed_tariff:
            prev_elec_unit_rates[cid] = unit_rate
            if old_elec_rate is not None and old_elec_rate > 0:
                if (unit_rate - old_elec_rate) / old_elec_rate > _NG_BILL_SHOCK_THRESHOLD:
                    _elec_rate_shock_counts[cid] = _elec_rate_shock_counts.get(cid, 0) + 1
                    _bill_shock_dates.setdefault(cid, []).append(term_start_str)
        elif commodity == "gas" and not _indexed_tariff:
            prev_gas_unit_rates[cid] = unit_rate

        if term_index >= 1 and commodity == "electricity" and not _indexed_tariff:
            company_est_pre = None
            retention_modifier_val = None
            _no_offer_reason = "below_threshold"
            _would_be_discount_pct = None
            _bill_shock_this_term = False
            # Phase 33: active/passive renewal split. Default True until we know the rate.
            active_renewal = True
            passive_cap = None
            _engagement_level_str = None
            if old_elec_rate is not None:
                # Phase 2 Layer 1 (CORE_FIDELITY_PHASES.md): each household's
                # engagement archetype is a persistent trait (keyed on the
                # stable billing_account, not per-term_index), not a fresh
                # coin-flip every renewal -- the population-weighted
                # aggregate still reproduces the existing anchored ~35% rate.
                from simulation.household_segments import (
                    active_renewal_probability,
                    engagement_level_for_customer,
                )
                _engagement_level = engagement_level_for_customer(billing_account)
                _engagement_level_str = _engagement_level.value
                active_renewal = rolls_active_renewal(
                    term_start_str, f"{billing_account}_{term_index}",
                    active_renewal_probability(_engagement_level),
                )
                passive_cap = passive_churn_cap_for(active_renewal)
                acq_date_for_est = next(
                    (c["acquisition_date"] for c in _ALL_KNOWN_CUSTOMERS if c["customer_id"] == billing_account),
                    term_start_str,
                )
                tenure_for_est = (date.fromisoformat(term_start_str) - date.fromisoformat(acq_date_for_est)).days / 365.25
                # Phase 15d: pass previous-term hedge fraction — well-hedged customers
                # experienced stable prices, making them less rate-sensitive at renewal.
                prev_hf = current_hf.get(cid, 0.0)
                hangover_periods = hangover_remaining.get(cid, 0)
                # Phase 23a: company estimates EAC from observable prior-year billing
                company_eac = _company_eac_estimate(cid, term_start_str, settled_fold)
                # Phase 25a: true_eac is mean annual settled consumption (actual, not declared).
                # Fixes misleading ~100% error for EV customers (C2/C4 declared 3500/5500
                # kWh but actually consume ~6820 kWh/year with EV charging).
                true_eac = _derive_eac_from_settlement(cid, settled_fold) or EFFECTIVE_EAC_KWH.get(cid, 0.0)
                if true_eac > 0:
                    eac_err_pct = (company_eac - true_eac) / true_eac * 100.0
                    demand_estimation_log.append({
                        "customer_id": cid,
                        "term_start": term_start_str,
                        "company_eac_kwh": round(company_eac),
                        "true_eac_kwh": round(true_eac),
                        "error_pct": round(eac_err_pct, 2),
                        "source": "prior_billing" if company_eac != true_eac else "fallback",
                    })
                # Phase 27e: I&C segment uses broker-driven churn model
                cust_for_churn = next(
                    (c for c in _ALL_KNOWN_CUSTOMERS if c["customer_id"] == billing_account), None
                )
                segment_for_churn = cust_for_churn.get("segment", "resi") if cust_for_churn else "resi"
                # Phase 33: passive renewers use SVT-inertia constants; active use full model.
                # I&C customers are always active (brokers shop every renewal — no passive roll).
                _renewal_year = int(term_start_str[:4])
                # Phase QK: signal collection (shock count, behaviour score, satisfaction
                # decay/record) runs for EVERY renewal, not just active ones -- these are
                # observable state updates independent of which estimate formula applies.
                # Previously gated behind the active/I&C branch, so a passive-rolling
                # customer's satisfaction/shock tracking was frozen and never fed into
                # their estimate -- the root cause of the churn classifier's structural
                # recall=0%/precision=0% (docs/staging/EVIDENCE_IN_BUSINESS_SURFACES.md).
                _nd_shock_count = _elec_rate_shock_counts.get(cid, 0)
                # Phase NH: payment behaviour score from observable payment history
                _nh_behaviour_score = _cx_desk.payment_behaviour_score(cid)
                if _churn_journey_register.get_journey(billing_account) is None:
                    _churn_journey_register.register_customer(
                        billing_account, tenure_years=tenure_for_est, churn_threshold=50.0,
                    )
                if old_elec_rate > 0 and unit_rate / old_elec_rate - 1 > _NG_BILL_SHOCK_THRESHOLD:
                    _bill_shock_this_term = True
                    _churn_journey_register.record_friction(
                        billing_account, FrictionEventType.BILL_SHOCK, date.fromisoformat(term_start_str),
                    )
                # KNIFE step 21 (§3p): the world reports the term boundary and
                # whether this account's own rate rose past the shock threshold.
                # The twelve-month decay, the trust cost of a shock and the
                # per-year snapshot (Phase NG/QT) are the desk's, behind the door.
                _cx_desk.observe_renewal(RenewalReached(
                    customer_id=cid,
                    account_id=billing_account,
                    renewal_year=_renewal_year,
                    bill_shock=_bill_shock_this_term,
                ))
                _ng_satisfaction = _cx_desk.satisfaction_score(cid)
                # KNIFE step 20 (§3o): the world hands over what it can see and
                # takes back the company's belief. Which estimator applies to a
                # passive roller versus an active/I&C renewal is the company's
                # own segmentation judgement, behind this door.
                company_est_pre = estimate_renewal_churn(RenewalObservation(
                    old_rate_gbp_per_mwh=old_elec_rate,
                    new_rate_gbp_per_mwh=unit_rate,
                    tenure_years=tenure_for_est,
                    annual_consumption_kwh=company_eac,
                    bill_shock_count=_nd_shock_count,
                    behaviour_score=_nh_behaviour_score,
                    satisfaction_score=_ng_satisfaction,
                    hedge_fraction=prev_hf,
                    hangover_periods_remaining=hangover_periods,
                    segment=segment_for_churn,
                    renewal_year=_renewal_year,
                    active_renewal=active_renewal,
                ))
                if hangover_periods > 0:
                    hangover_remaining[cid] = hangover_periods - 1
                if company_est_pre > RETENTION_THRESHOLD:
                    eac_for_ret = company_eac  # Phase 23a: use company estimate
                    discount_pct = policy.retention_discount_for_risk(company_est_pre)
                    _would_be_discount_pct = discount_pct
                    ret_cost = unit_rate * discount_pct * eac_for_ret / 1000.0
                    expected_margin = (unit_rate - company_fwd) * eac_for_ret / 1000.0
                    # Phase 15b: include acquisition cost savings in the offer guard.
                    # If the customer churns, the company spends acq_cost on a replacement
                    # attempt (whether it wins or not). So the true value protected by
                    # retaining = expected_margin + acq_cost_saved.
                    # FROZEN_POLICY_BASELINE_DESIGN.md: NAIVE_POLICY excludes acq_cost_saved
                    # (pre-Phase-15b, margin-only guard) -- policy.include_acq_cost_saved_in_guard.
                    cust_data_ret = get_customer(billing_account)
                    seg_ret = cust_data_ret["segment"] if cust_data_ret else "resi"
                    acq_cost_saved = replacement_cost_avoided_gbp(
                        segment=seg_ret,
                        counted_in_guard=policy.include_acq_cost_saved_in_guard,
                    )
                    if expected_margin + acq_cost_saved > ret_cost:
                        # Nudge Physics Layer 1: framing_type is the company's own
                        # comms-cohort choice (observable by construction); the
                        # multiplier below is SIM ground truth (hidden loss-aversion
                        # susceptibility) applied to the actual offer effectiveness --
                        # the company never sees this multiplier, only the outcome.
                        _framing_type = framing_type_for(policy, billing_account, term_start_str)
                        _framing_multiplier = framing_effectiveness_multiplier(billing_account, _framing_type)
                        retention_modifier_val = min(0.95, RETENTION_EFFECTIVENESS * _framing_multiplier)
                        retention_cost_events.append(
                            book_retention_cost(
                                billing_account=billing_account,
                                event_date=term_start_str,
                                cost_gbp=ret_cost,
                                company_churn_estimate=company_est_pre,
                            )
                        )
                        retention_log.append({
                            "customer_id": billing_account,
                            "event_date": term_start_str,
                            "company_churn_estimate": company_est_pre,
                            "discount_pct": discount_pct,
                            "retention_cost_gbp": ret_cost,
                            "expected_term_margin_gbp": expected_margin,
                            "acq_cost_saved_gbp": round(acq_cost_saved, 2),
                            "assumed_deferral_months": ASSUMED_DEFERRAL_MONTHS,
                            "framing_type": _framing_type,
                            "outcome": "pending",
                        })
                    else:
                        _no_offer_reason = "uneconomical"
            # Phase NQ: industry base rate floor when no prior rate exists
            if company_est_pre is None:
                company_est_pre = estimate_churn_without_rate_history()
            # Phase MZ: SIM-side income stress -> actual switching propensity
            _churn_income_stress = None
            if household_demand_register is not None:
                _churn_income_stress = household_demand_register.income_stress_at_date(
                    billing_account, term_start_str
                )
            # Phase NF: SIM-side satisfaction -> actual churn probability
            _nf_shock_count = _elec_rate_shock_counts.get(cid, 0)
            _nf_tenure = (
                (date.fromisoformat(term_start_str) - date.fromisoformat(acq_date_for_est)).days / 365.25
                if old_elec_rate is not None else term_index * 0.5
            )
            # Real payment-method satisfaction gap + per-customer heterogeneity
            # (2026-07-10, ASSUMPTIONS.md "Customer Satisfaction Population
            # Distribution") -- resi-only, matching the existing
            # payment_channel_for_customer() convention (I&C/SME use bacs/chaps).
            _nf_payment_channel = None
            if segment_for_churn == "resi":
                from simulation.household_segments import payment_channel_for_customer
                _nf_payment_channel = payment_channel_for_customer(billing_account, "electricity")
            _nf_satisfaction = _sim_satisfaction_score(
                _nf_shock_count, _nf_tenure, _churn_income_stress,
                payment_channel=_nf_payment_channel, customer_id=cid,
            )
            # Phase RU: solicited feedback survey + complaint dispatch
            # (FEEDBACK_AND_REPUTATION.md Layer 1) -- CSAT/NPS off the SIM
            # ground-truth satisfaction just computed above; the company only
            # ever observes the response, never _nf_satisfaction itself.
            _csat_result = dispatch_csat_survey(
                billing_account, term_start_str, _nf_satisfaction, _churn_income_stress,
            )
            _survey_cust_data = get_customer(billing_account)
            _survey_segment = _survey_cust_data.get("segment", "resi") if _survey_cust_data else "resi"
            if _csat_result.responded:
                _cx_desk.observe_survey_response(SurveyResponse(
                    customer_id=cid,
                    account_id=billing_account,
                    instrument=SurveyInstrument.CSAT,
                    score_0_10=_csat_result.score_0_10,
                    responded_on=date.fromisoformat(term_start_str),
                    segment=_survey_segment,
                    channel="renewal",
                ))
            _nps_result = dispatch_nps_survey(
                billing_account, term_start_str, _nf_satisfaction, _churn_income_stress,
            )
            if _nps_result.responded:
                _cx_desk.observe_survey_response(SurveyResponse(
                    customer_id=cid,
                    account_id=billing_account,
                    instrument=SurveyInstrument.NPS,
                    score_0_10=_nps_result.score_0_10,
                    responded_on=date.fromisoformat(term_start_str),
                    segment=_survey_segment,
                    channel="renewal",
                ))
            feedback_survey_log.append({
                "customer_id": billing_account,
                "term_start": term_start_str,
                "true_satisfaction": round(_nf_satisfaction, 4),
                "csat_responded": _csat_result.responded,
                "csat_score_0_10": _csat_result.score_0_10,
                "nps_responded": _nps_result.responded,
                "nps_score_0_10": _nps_result.score_0_10,
            })
            from simulation.household_segments import occupancy_for_customer
            _complaint_outcome = dispatch_complaint_and_resolution(
                billing_account, term_start_str, _bill_shock_this_term,
                occupancy_for_customer(billing_account).value,
            )
            if _complaint_outcome.occurred:
                # KNIFE step 21 (§3p): the world reports that the customer got in
                # touch and whether the company closed it on time. Filing it under
                # BILLING, wording it, and both trust deltas are the desk's.
                _cx_desk.observe_contact(CustomerContact(
                    customer_id=cid,
                    account_id=billing_account,
                    contacted_on=date.fromisoformat(term_start_str),
                    about_bill_shock=_bill_shock_this_term,
                    resolved_on_time=(
                        _complaint_outcome.reputation_event_type
                        == ReputationEventType.COMPLAINT_RESOLVED_ON_TIME
                    ),
                ))
                if _complaint_outcome.reputation_event_type == ReputationEventType.COMPLAINT_RESOLVED_ON_TIME:
                    _churn_journey_register.record_friction(
                        billing_account, FrictionEventType.COMPLAINT_RESOLVED_WELL,
                        date.fromisoformat(term_start_str),
                    )
                else:
                    _churn_journey_register.record_friction(
                        billing_account, FrictionEventType.COMPLAINT_UNRESOLVED,
                        date.fromisoformat(term_start_str),
                        amplifier=(
                            1.5 if _complaint_outcome.reputation_event_type
                            == ReputationEventType.COMPLAINT_UPHELD_AT_OMBUDSMAN else 1.0
                        ),
                    )
                _churn_journey_register.gri.record(
                    _complaint_outcome.reputation_event_type, date.fromisoformat(term_start_str),
                    description=f"{billing_account} complaint raised {term_start_str}",
                )
                reputation_events_log.append({
                    "customer_id": billing_account,
                    "date": term_start_str,
                    "event_type": _complaint_outcome.reputation_event_type.value,
                    "days_to_resolve": _complaint_outcome.days_to_resolve,
                })
            _perceived_bill_saving_gbp = (
                max(0.0, unit_rate - old_elec_rate) * (company_eac / 1000.0)
                if old_elec_rate else 0.0
            )
            _journey_state = _churn_journey_register.advance(
                billing_account, date.fromisoformat(term_start_str),
                renewal_window_open=True,
                perceived_bill_saving_gbp=_perceived_bill_saving_gbp,
            )
            _journey = _churn_journey_register.get_journey(billing_account)
            churn_journey_log.append({
                "customer_id": billing_account,
                "term_start": term_start_str,
                "journey_state": _journey_state.value,
                "resentment_score": round(_journey.resentment.current_score(date.fromisoformat(term_start_str)), 2),
                "is_burned": _journey.resentment.is_burned,
                "perceived_bill_saving_gbp": round(_perceived_bill_saving_gbp, 2),
            })
            event = roll_lifecycle_event(
                cid, term_start_str, commodity, list(all_records), _ALL_KNOWN_CUSTOMERS,
                old_rate_gbp_per_mwh=old_elec_rate,
                new_rate_gbp_per_mwh=unit_rate,
                retention_modifier=retention_modifier_val,
                precomputed_company_estimate=company_est_pre,
                passive_churn_cap=passive_cap,
                income_stress=_churn_income_stress,
                satisfaction_score=_nf_satisfaction,
                market_year=int(term_start_str[:4]),
                position_ledger=_competitor_position_ledger,
                # THE SIM'S OWN forward price, never the company's estimate. A rival buys in the
                # same market this world clears, so its cost floor is built from what wholesale
                # ACTUALLY cost -- `company_fwd` is the company's belief about that number and
                # would make the rival's costs a function of the company's forecasting skill.
                wholesale_gbp_per_mwh=forward_price,
            )
            # THE RIVAL SEES THIS OFFER ONLY AFTER THE TERM IT WAS STRUCK IN (2026-08-28, C2).
            # Recorded AFTER the roll, and read back by `position_for()` a quarter later, so no
            # offer can ever reach the reference it is itself being measured against. Recording
            # it before the roll would make the differential partly a function of itself, which
            # is the tautology R15 names first.
            _competitor_position_ledger.observe(term_start_str, unit_rate)
            if event is not None:
                _journey.record_decision(
                    date.fromisoformat(term_start_str), switched=(event["event_type"] == "churned"),
                )
                event["is_active_renewal"] = active_renewal
                # Phase 2 Layer 1: SIM-internal ground truth, retained here for
                # evidence-surface use only (same pattern as credit_bureau_true_
                # creditworthy) -- demonstrates the persistent archetype trait
                # across a household's renewal history. MUST NEVER be read by
                # company/** decision code.
                event["engagement_level"] = _engagement_level_str
                event["unit_rate_gbp_per_mwh"] = unit_rate
                customer_events_log.append(event)
                if retention_modifier_val is not None and retention_log:
                    outcome_str = "churned_despite_offer" if event["event_type"] == "churned" else "retained"
                    retention_log[-1]["outcome"] = outcome_str
                    nudge_physics_log.append({
                        "customer_id": billing_account,
                        "event_date": term_start_str,
                        "framing_type": retention_log[-1].get("framing_type"),
                        "susceptibility": susceptibility_for(billing_account).value,
                        "effectiveness_multiplier": round(
                            retention_modifier_val / RETENTION_EFFECTIVENESS, 4
                        ) if RETENTION_EFFECTIVENESS else None,
                        "outcome": outcome_str,
                    })
                if event["event_type"] == "churned":
                    if retention_modifier_val is None:
                        # No offer was made — record as missed retention opportunity
                        eac_missed = company_eac  # Phase 23a: use company estimate
                        no_offer_churn_log.append({
                            "customer_id": billing_account,
                            "event_date": term_start_str,
                            "company_churn_estimate": company_est_pre,
                            "expected_term_margin_gbp": (unit_rate - company_fwd) * eac_missed / 1000.0,
                            # THE DENOMINATOR OF A DISCOUNT (2026-08-28, roadmap R3). A retention
                            # offer is a price cut, so its cost is a share of REVENUE -- not of
                            # margin, which is a few per cent of it, and not a flat sum. Without
                            # this field `counterfactual_retention` cannot price the offer it is
                            # counterfactualising, and it refuses rather than assuming.
                            "expected_term_revenue_gbp": unit_rate * eac_missed / 1000.0,
                            "no_offer_reason": _no_offer_reason,
                            "would_be_discount_pct": _would_be_discount_pct,
                        })
                    churned_billing_accounts.add(billing_account)
                    # THE COMPANY'S COMPETITIVE OBSERVABLE, BOOKED WHERE EVERY DEPARTURE PASSES
                    # -- unconditionally. A `notify_churn` call sat eight lines below behind
                    # `if sim_interface is not None`, and that guard is why the first live
                    # measurement of this channel was worthless: `run_phase4c_on_phase2b` calls
                    # this function with no interface, so the numerator never filled while the
                    # denominator did, and the belief collapsed on evidence that did not exist.
                    # A supplier knows who left it whether or not a notification seam happens to
                    # be plumbed in. The guard and its four siblings are now deleted outright
                    # (see `main`'s docstring); this booking is what replaced them.
                    #
                    # ARMED ADJACENT TO THE BOOKING and never anywhere else: if this call is
                    # deleted the arming goes with it, and an unarmed ledger declines to update
                    # rather than reading the resulting silence as a quiet market.
                    _pressure_ledger = active_pressure_ledger()
                    if _pressure_ledger is not None:
                        _pressure_ledger.arm_loss_reporting()
                        _pressure_ledger.observe_competitive_loss(int(term_start_str[:4]))
                    print(
                        f"  [CHURN] {billing_account} at {term_start_str} — "
                        f"p_retain={event['effective_retention_probability']:.4f}  "
                        f"roll={event['random_roll']:.4f}"
                    )
                    # The win roll and the DELIVERY of that win are two facts. Ask
                    # the disposition helper, never `if won: ... elif replace:` —
                    # that chain swallowed an undeliverable win and suppressed the
                    # market replacement with it (2026-08-14 BLOCKING finding).
                    successor_id = (
                        SUCCESSOR_MAP.get(billing_account)
                        if event.get("home_move_won") else None
                    )
                    _home_move = home_move_disposition(
                        bool(event.get("home_move_won")), successor_id
                    )
                    # Stamp the undeliverable win on the event so the realised win
                    # rate's shortfall against its parameter is visible in the
                    # event log rather than silent. Stamped BEFORE the branch: a
                    # wind-down mandate blocks the replacement, not the record.
                    if event.get("home_move_won") and successor_id is None:
                        event["home_move_win_undelivered"] = True
                        print(
                            f"  [WIN-UNDELIVERED] {billing_account} won its home-mover but has "
                            f"no successor supply point — going to market instead"
                        )
                    if _home_move == HOME_MOVE_ACTIVATE_SUCCESSOR:
                        won_successor_activations[successor_id] = term_start_str
                        print(f"  [WIN] Home-mover won: {successor_id} activates at {term_start_str}")
                    elif mandate_permits_replacement():
                        customer_data = get_customer(billing_account)
                        segment = customer_data["segment"] if customer_data else "resi"
                        acq_seed = f"acquire_{billing_account}_{term_start_str}"

                        # Phase 47b: cap-aware acquisition gate — the supplier declines
                        # to go to market when the cap would force resi electricity below
                        # wholesale cost. KNIFE3 step 27 (register §3v): the budget and
                        # the gate are ONE question asked through
                        # `company.interfaces.growth_desk`, not two the world answered off
                        # its own copy of the supplier's cost table.
                        _acq = decide_acquisition(
                            segment=segment,
                            commodity=commodity,
                            company_fwd_gbp_per_mwh=company_fwd,
                            term_start=term_start_str,
                        )
                        acq_cost = _acq.budget_gbp
                        if not _acq.attempt:
                            acquisition_spend_events.append(
                                book_acquisition_gate(
                                    billing_account=billing_account,
                                    event_date=term_start_str,
                                    segment=segment,
                                    gate_reason=_acq.gate_reason,
                                )
                            )
                            print(
                                f"  [GATE] Acquisition suppressed: {billing_account} at {term_start_str}"
                                f" — {_acq.gate_reason}"
                            )
                            continue

                        _funnel_result = run_acquisition_funnel(
                            segment, acq_seed, date.fromisoformat(term_start_str),
                            _credit_bureau, total_amount_gbp=acq_cost,
                        )
                        acq_won = _funnel_result.won

                        # WALLED_INTERFACES reference-flow conversion
                        # (W4_1_typed_adapters): the acquisition-funnel crossing
                        # now travels as a versioned typed message
                        # (tools.acquisition_funnel_port.AcquisitionFunnelMessage)
                        # rather than a raw dict. This is a transport-shape change
                        # only -- `to_log_entry()` is a lossless identity on the
                        # pre-conversion dict, so every downstream consumer of
                        # `acquisition_funnel_log` is unaffected. The seam is
                        # deliberately narrower than the internal
                        # AcquisitionFunnelResult: per-stage cost_increment_gbp is
                        # dropped (no consumer reads it; aggregate crosses as
                        # total_cost_gbp) and billing_account is added from loop
                        # context. Phase 3 item 5's real stage-to-stage calendar
                        # dates are preserved via FunnelStageMessage.
                        _funnel_message = AcquisitionFunnelMessage.from_log_entry({
                            "billing_account": billing_account,
                            "segment": segment,
                            "term_start": term_start_str,
                            "won": acq_won,
                            "stage_reached": _funnel_result.stage_reached,
                            "total_cost_gbp": _funnel_result.total_cost_gbp,
                            "credit_bureau_score_band": _funnel_result.credit_bureau_score_band,
                            "credit_bureau_passed": _funnel_result.credit_bureau_passed,
                            "credit_bureau_true_creditworthy": _funnel_result.credit_bureau_true_creditworthy,
                            "stages": [
                                {"stage": s.stage, "passed": s.passed, "stage_date": s.stage_date}
                                for s in _funnel_result.stages
                            ],
                        })
                        acquisition_funnel_log.append(
                            _funnel_message.to_log_entry(include_schema_version=True)
                        )

                        acquisition_spend_events.append(
                            book_acquisition_spend(
                                billing_account=billing_account,
                                event_date=term_start_str,
                                amount_gbp=_funnel_result.total_cost_gbp,
                                won=acq_won,
                                segment=segment,
                            )
                        )

                        if acq_won:
                            suffix = _acquisition_counter.get(billing_account, 3)
                            _acquisition_counter[billing_account] = suffix + 1
                            new_cid = f"{billing_account}_{suffix}"
                            new_customer = make_acquired_customer(new_cid, customer_data, term_start_str)
                            ACQUIRED_CUSTOMERS.append(new_customer)
                            fresh_acquisitions.append({
                                "customer_id": new_cid,
                                "event_date": term_start_str,
                                "predecessor_id": billing_account,
                            })
                            print(
                                f"  [ACQUIRE] Fresh acquisition won: {new_cid} at {term_start_str} "
                                f"(£{acq_cost:.0f}, {segment})"
                            )
                        else:
                            print(
                                f"  [ACQUIRE] Fresh acquisition failed: {billing_account} at {term_start_str} "
                                f"(£{acq_cost:.0f}, {segment})"
                            )
                    continue
            elif retention_modifier_val is not None and retention_log:
                # No lifecycle event — offer made, customer just renewed normally
                retention_log[-1]["outcome"] = "retained"
                nudge_physics_log.append({
                    "customer_id": billing_account,
                    "event_date": term_start_str,
                    "framing_type": retention_log[-1].get("framing_type"),
                    "susceptibility": susceptibility_for(billing_account).value,
                    "effectiveness_multiplier": round(
                        retention_modifier_val / RETENTION_EFFECTIVENESS, 4
                    ) if RETENTION_EFFECTIVENESS else None,
                    "outcome": "retained",
                })

        # Phase 14b: compute gas company churn estimate for dual-fuel monitoring.
        # Gas legs don't drive churn decisions (those live at electricity billing-account
        # level), but the company tracks gas renewal rate changes separately to spot
        # early-warning pressure on dual-fuel portfolios.
        if term_index >= 1 and commodity == "gas" and old_gas_rate is not None:
            gas_customer_data = next(
                (c for c in _ALL_KNOWN_CUSTOMERS if c["customer_id"] == billing_account),
                None,
            )
            if gas_customer_data is not None:
                acq_date_gas = gas_customer_data.get("acquisition_date", term_start_str)
                tenure_gas = (date.fromisoformat(term_start_str) - date.fromisoformat(acq_date_gas)).days / 365.25
                gas_company_est = estimate_secondary_fuel_churn(old_gas_rate, unit_rate, tenure_gas)
                company_gas_churn_log.append({
                    "customer_id": cid,
                    "billing_account": billing_account,
                    "term_start": term_start_str,
                    "old_gas_rate": round(old_gas_rate, 4),
                    "new_gas_rate": round(unit_rate, 4),
                    "company_gas_churn_estimate": gas_company_est,
                })

        if cid in pending_committee_overrides:
            hf = pending_committee_overrides.pop(cid)
        else:
            hf = next_hf[cid]
        current_hf[cid] = hf

        if commodity == "electricity":
            customer = get_customer(cid)
            # Phase H: adjust base EAC for EV/solar/ASHP at first term.
            # Billing history on renewal terms already reflects actual consumption;
            # the declared-EAC fallback needs the household multiplier.
            if household_demand_register is not None:
                _elec_mult = household_demand_register.eac_multiplier_for_date(cid, term_start_str)
                _base_elec_eac = EFFECTIVE_EAC_KWH.get(cid, 0.0)
                _adj_base_elec = max(1, round(_base_elec_eac * _elec_mult))
            else:
                _adj_base_elec = None
            # Phase 25a/H: use billing records; falls back to household-adjusted declared EAC.
            eac_kwh = _company_eac_estimate(cid, term_start_str, settled_fold, base_eac_override=_adj_base_elec)
            if is_hh_customer(customer):
                shape_fn = hh_shape_fn(hh_consumption_by_customer[cid])
                # Phase MT: I&C customers reduce demand 25% during Triad risk windows.
                if customer.get("segment") == "I&C":
                    shape_fn = make_triad_aware_shape_fn(shape_fn, _ic_triad_alert_set)
                demand_provider_by_customer[cid] = METERED_PROVIDER
            elif cid in fabric_series_by_customer:
                # W1_11: the fabric trace IS the demand. Every legacy overlay
                # (HDD heating uplift, EPC consumption multiplier, ASHP uplift,
                # overnight-EV overlay, solar offset, occupancy shape/volume) is
                # REPLACED rather than stacked -- the trace already contains each
                # of them, so applying any of them here would double-count.
                shape_fn = fabric_shape_fn(
                    fabric_series_by_customer[cid],
                    "electricity",
                    battery_dispatch=_fabric_battery_dispatch_for(cid),
                )
                demand_provider_by_customer[cid] = FABRIC_PROVIDER
            else:
                demand_provider_by_customer[cid] = LEGACY_PROVIDER
                profile_class = customer.get("profile_class", 1)
                property_record = properties.get(cid, DEFAULT_PROPERTY)
                # Phase O: always pass cloud cover + latitude — any resi customer
                # can acquire solar via a life event (Phase B), so irradiance must be
                # available from the acquisition date onward.
                cloud_cover = cloud_cover_by_customer.get(cid)
                latitude = customer.get("location", {}).get("lat")
                shape_fn = _weather_adjusted_shape_fn(
                    SHAPE_LOADERS[profile_class], weather_by_customer[cid], property_record,
                    cloud_cover_means=cloud_cover, latitude_deg=latitude,
                    household_register=household_demand_register, customer_id=cid,
                )

            cust_segment = customer.get("segment", "resi") if customer else "resi"
            if term_tariff_type == "deemed":
                # Phase 40c: out-of-contract period — spot + deemed_premium, no forward hedge.
                # Phase 47a/MARGIN_REALISM Step 5: cap-bound 2019+ for resi (W3_1_price_cap_binding).
                deemed_premium = term.get("deemed_premium", 0.20)
                term_records = run_deemed_term(
                    cid, term_start_str, term_end_str, deemed_premium,
                    shape_fn, elec_records, segment=cust_segment, commodity=commodity,
                )
            elif term_tariff_type == "flex":
                # Phase 41a: flex/trading tariff — reference price (7-day rolling spot) + markup.
                # No capital cost (hedged weekly at reference). Fully hedged at reference price.
                flex_markup = term.get("flex_markup_per_mwh", 2.0)
                term_records = run_flex_term(
                    cid, term_start_str, term_end_str, flex_markup,
                    shape_fn, elec_records, segment=cust_segment,
                )
            else:
                # Phase 43b: VaR-constrained hedge decision replaces static hf for fixed/pass-through
                # electricity terms. The trading desk decides hedge fraction based on current market
                # conditions (observable price volatility, term duration, forward price).
                # Committee overrides still take precedence (already applied via pending_committee_overrides).
                term_days_count = (
                    date.fromisoformat(term_end_str) - date.fromisoformat(term_start_str)
                ).days
                if policy.use_var_hedge_decision and unit_rate and company_fwd and eac_kwh > 0 and term_days_count > 0:
                    _decision_time = datetime.combine(date.fromisoformat(term_start_str), time.min)
                    _piv = PointInTimeView(decision_time=_decision_time, bitemporal_log=_price_bitemporal_log)
                    _elec_price_hist = _piv.get_price_history_as_of("electricity")
                    # KNIFE3 step 23 (§3r): the desk takes the decision, adjudicates
                    # the committee override against it, and reports the VaR at the
                    # fraction that SURVIVES. The world supplies only what it can
                    # observe — its demand estimate, its locked forward, its proposed
                    # tariff, and a price history already through the blindfold.
                    _elec_hedge = hedge_desk.decide_term_hedge(
                        customer_id=cid,
                        term_start=term_start_str,
                        term_end=term_end_str,
                        commodity="electricity",
                        volume_kwh=eac_kwh,
                        forward_price_gbp_per_mwh=company_fwd,
                        unit_rate_gbp_per_mwh=unit_rate,
                        price_records=_elec_price_hist,
                        term_days=term_days_count,
                        current_fraction=hf,
                        accept_decision=(cid not in pending_committee_overrides),
                    )
                    if _elec_hedge.decision_accepted:
                        hf = _elec_hedge.hedge_fraction
                        current_hf[cid] = hf
                    hedge_var_log.append(_elec_hedge.var_log_entry)

                naked_kwh = eac_kwh * (1.0 - hf)
                risk = assess_term_risk(term_start_str, naked_kwh, forward_price, elec_records)
                counterfactual_risk = assess_term_risk(term_start_str, float(eac_kwh), forward_price, elec_records)
                current_risk[cid] = risk

                # Phase 50/51: the customer record carries the METERING FACTS the
                # rollout stamped -- `metering` and `smart_meter`. The world owns
                # those; whether they buy a ToU offer is answered at the door.
                # KNIFE step 25 (§3t): WHETHER a ToU product is offered to a
                # customer whose meter permits it, and the peak/off-peak shape of
                # the pair, are the supplier's commercial decision -- one door,
                # `company/interfaces/tou_offer.py`. The METER is the world's and
                # stays here, on the customer record the door is handed.
                _tou = request_tou_offer(
                    customer=customer, flat_unit_rate_gbp_per_mwh=unit_rate,
                )
                tou_rates = None
                if _tou is not None:
                    tou_rates = (_tou.peak_rate_gbp_per_mwh, _tou.offpeak_rate_gbp_per_mwh)
                    # Phase 52: demand response — ToU-eligible customers shift a fraction
                    # of peak consumption to off-peak (base 15%, +12% EV, +8% heat pump).
                    _assets = properties.get(cid, DEFAULT_PROPERTY).get("assets")
                    _dr_shift = compute_shift_fraction(_assets)
                    effective_shape_fn = make_shifted_shape_fn(shape_fn, _dr_shift)
                    demand_response_log.append({
                        "customer_id": cid,
                        "term_start": term_start_str,
                        "term_end": term_end_str,
                        "shift_fraction": round(_dr_shift, 4),
                        "has_ev": bool((_assets or {}).get("ev")),
                        "has_heat_pump": bool((_assets or {}).get("heat_pump")),
                    })
                else:
                    effective_shape_fn = shape_fn

                term_records = run_hedged_term(
                    cid, term_start_str, term_end_str, unit_rate, forward_price, hf,
                    risk["monthly_cost_of_capital_gbp"], effective_shape_fn, elec_records,
                    tou_rates=tou_rates, segment=cust_segment,
                    pass_through=(term_tariff_type == "pass_through"),
                )
                # Phase 43a: open a forward contract in the company trading book.
                # agreed_price = company_fwd (the price the company locked at tariff signing).
                # notional_mwh = hedged portion of EAC estimate.
                if company_fwd and hf > 0:
                    # KNIFE3 step 23 (§3r): sizing the notional, pricing the spread,
                    # attributing the counterparty (VALUE_CHAIN step 2) and booking
                    # the contract are one execution act, and it is the desk's.
                    hedge_desk.open_term_hedge(
                        customer_id=cid,
                        term_start=term_start_str,
                        term_end=term_end_str,
                        volume_kwh=eac_kwh,
                        forward_price_gbp_per_mwh=company_fwd,
                        hedge_fraction=hf,
                        term_days=term_days_count,
                    )
                    # Add hedge_pnl_gbp per settlement record (decomposed from supply margin).
                    for rec in term_records:
                        spot = rec.get("wholesale_cost_gbp", 0.0) / (rec["consumption_kwh"] / 1000.0) if rec["consumption_kwh"] > 0 else 0.0
                        rec["hedge_pnl_gbp"] = round(hedge_desk.settle_period_pnl_gbp(
                            cid, term_start_str, rec["consumption_kwh"], spot
                        ), 6)
            for rec in term_records:
                rec["data_regime"] = "historical"
                rec["commodity"] = "electricity"

            # Phase 27c: volume tolerance for I&C customers.
            # Skip for deemed/flex — no locked hedge price to unwind against.
            if cust_segment == "I&C" and term_records and forward_price is not None:
                term_days = (
                    date.fromisoformat(term_end_str) - date.fromisoformat(term_start_str)
                ).days
                contracted_term_kwh = eac_kwh * term_days / 365.25
                actual_term_kwh = sum(r["consumption_kwh"] for r in term_records)
                avg_spot = (
                    sum(r.get("wholesale_cost_gbp", 0) for r in term_records)
                    / (sum(r["consumption_kwh"] for r in term_records) / 1000.0)
                    if actual_term_kwh > 0 else 0.0
                )
                vt = compute_term_volume_tolerance(
                    actual_term_kwh, contracted_term_kwh, avg_spot, forward_price, hf
                )
                volume_tolerance_log.append({
                    "customer_id": cid,
                    "term_start": term_start_str,
                    "term_end": term_end_str,
                    **vt,
                })

        else:  # gas
            gas_customer = get_customer(cid)
            aq_kwh = gas_customer["aq_kwh"]
            # Phase D: scale gas AQ by EPC-band multiplier from household model.
            if household_demand_register is not None:
                _gas_mult = household_demand_register.gas_eac_multiplier_for_date(cid, term_start_str)
                aq_kwh = max(1, round(aq_kwh * _gas_mult))

            # Phase 44b: VaR-constrained hedge decision for gas fixed terms (mirrors electricity 43b).
            # Phase 56: Pass-through gas customers must not hedge — they bill at spot, so a forward
            # hedge creates wrong-way risk (windfall gain 2021, catastrophic loss 2023 on reversion).
            if term_tariff_type == "pass_through":
                hf = 0.0
                current_hf[cid] = 0.0
            elif policy.use_var_hedge_decision and unit_rate and company_fwd and aq_kwh > 0:
                _gas_term_days = (
                    date.fromisoformat(term_end_str) - date.fromisoformat(term_start_str)
                ).days
                if _gas_term_days > 0:
                    _gas_decision_time = datetime.combine(date.fromisoformat(term_start_str), time.min)
                    _gas_piv = PointInTimeView(decision_time=_gas_decision_time, bitemporal_log=_price_bitemporal_log)
                    _gas_price_hist = _gas_piv.get_price_history_as_of("gas")
                    # KNIFE3 step 23 (§3r): the same desk, the same door, the other
                    # commodity — `commodity` is a named argument rather than the
                    # two near-identical inlined blocks this replaced.
                    _gas_hedge = hedge_desk.decide_term_hedge(
                        customer_id=cid,
                        term_start=term_start_str,
                        term_end=term_end_str,
                        commodity="gas",
                        volume_kwh=aq_kwh,
                        forward_price_gbp_per_mwh=company_fwd,
                        unit_rate_gbp_per_mwh=unit_rate,
                        price_records=_gas_price_hist,
                        term_days=_gas_term_days,
                        current_fraction=hf,
                        accept_decision=(cid not in pending_committee_overrides),
                    )
                    if _gas_hedge.decision_accepted:
                        hf = _gas_hedge.hedge_fraction
                        current_hf[cid] = hf
                    hedge_var_log.append(_gas_hedge.var_log_entry)

            # Phase NE: pass-through gas has no commodity price risk -- customer pays spot
            # directly, so company holds no naked position. Using aq_kwh here was generating
            # spurious VaR capital costs on a genuinely zero-risk position.
            naked_kwh = 0.0 if term_tariff_type == "pass_through" else aq_kwh * (1.0 - hf)
            risk = assess_term_risk(term_start_str, naked_kwh, forward_price, gas_records)
            counterfactual_risk = assess_term_risk(
                term_start_str,
                0.0 if term_tariff_type == "pass_through" else float(aq_kwh),
                forward_price, gas_records,
            )
            current_risk[cid] = risk

            # Phase W: gas HDD shape is now computed daily inside run_gas_term.
            # weather_factor term-level scalar removed; resi/SME uses per-day HDD internally.
            term_records = run_gas_term(
                cid, term_start_str, term_end_str, aq_kwh,
                unit_rate, hf, forward_price,
                risk["monthly_cost_of_capital_gbp"], gas_records,
                segment=cust_segment,
                pass_through=(term_tariff_type == "pass_through"),
            )
            for rec in term_records:
                rec["data_regime"] = "historical"

        # Phase MW: income stress bad-debt uplift (residential only).
        _income_stress = (
            household_demand_register.income_stress_at_date(cid, term_end_str)
            if household_demand_register is not None else None
        )
        _stress_bd_mult = stress_bad_debt_multiplier(_income_stress)

        settled_this_term: list[dict] = []
        for rec in term_records:
            rec_year = rec["settlement_date"][:4]
            if rec_year != current_year_str:
                ytd_gross = ytd_net = ytd_capital = 0.0
                current_year_str = rec_year

            # Phase 8a: emit one fixed_cost_event per calendar month.
            # Use a seen-set to deduplicate across customers (multiple customers'
            # terms interleave, so naive current_month_str comparison double-counts).
            # Fixed costs flow through the ledger only — not deducted from the
            # energy trading treasury (trading vs. ops architectural separation).
            rec_month = rec["settlement_date"][:7]
            if rec_month not in _fixed_cost_emitted:
                fixed_cost_events.append(book_monthly_overhead(rec_month))
                _fixed_cost_emitted.add(rec_month)

            # Phase NH: generate one payment record per customer-month for analytics.
            # L3 coupled triad: the CANONICAL payment truth is now W2_11's
            # generate_payment_event (via LivePaymentTriad.record_period), which
            # ALSO crosses the W4_4 seam into the D5 consumer belief LIVE. The
            # analytics dict fed here is DERIVED from that single event -- one
            # coherent reality per customer/period, no second independent draw.
            _pm_key = (cid, rec['settlement_date'][:7])
            if _pm_key not in _payment_month_seen:
                _payment_month_seen.add(_pm_key)
                _pm_due = date.fromisoformat(rec['settlement_date'][:7] + '-28')
                _pm_rec = _payment_triad.record_period(
                    customer_id=cid,
                    due_date=_pm_due,
                    amount_gbp=rec.get('revenue_gbp', 0.0),
                    income_stress_value=(_income_stress.value if _income_stress is not None else None),
                    segment=cust_segment,
                )
                _cx_desk.observe_payment(PaymentOutcome(
                    customer_id=cid,
                    due_date=_pm_rec["due_date"],
                    result=_pm_rec["result"],
                    days_late=_pm_rec["days_late"],
                    amount_gbp=_pm_rec["amount_gbp"],
                ))
            # Real-time placeholder only -- simulation.run_phase4c_on_phase2b.main()
            # overwrites this with real, emergent bad debt from the payment/
            # arrears model (simulation.arrears_engine) once bills exist (Phase QD).
            #
            # KNIFE pass 3 (`B11_default_incidence_is_the_worlds` step 29,
            # 2026-08-14, register §3x): the incidence is the WORLD's
            # (simulation.bad_debt_incidence), not the supplier's provisioning
            # table. Until this line the fraction of revenue the supplier
            # PROVIDED FOR was the fraction that actually went bad -- including
            # inside `is_administration_triggered(treasury)` below, so the
            # supplier's own assumption decided whether the supplier survived.
            # The stress multiplier beside it was already world-side.
            _bd_rate = world_bad_debt_incidence(int(rec_year), cust_segment) * _stress_bd_mult
            _bad_debt = round(rec.get("revenue_gbp", 0.0) * _bd_rate, 6)
            rec["bad_debt_gbp"] = _bad_debt
            rec["net_margin_gbp"] = round(rec["net_margin_gbp"] - _bad_debt, 6)
            treasury += rec["net_margin_gbp"]
            rec["treasury_cash_balance_gbp"] = treasury
            ytd_gross += rec["margin_gbp"]
            ytd_net += rec["net_margin_gbp"]
            ytd_capital += rec["capital_cost_gbp"]
            settled_this_term.append(rec)

            total_periods_processed += 1
            if total_periods_processed % PROGRESS_EVERY_PERIODS == 0:
                print(
                    f"  ... progress: {total_periods_processed:,} settlement periods "
                    f"processed (latest: {rec['settlement_date']} period "
                    f"{rec.get('settlement_period', '-')}, treasury £{treasury:.2f})"
                )

            if is_administration_triggered(treasury) and administration_event is None:
                administration_event = {
                    "date": rec["settlement_date"],
                    "customer_id": rec["customer_id"],
                    "treasury_balance_gbp": treasury,
                    "commodity": commodity,
                }
                break

            periods_since_committee += 1
            _rec_date = date.fromisoformat(rec["settlement_date"])
            if (_rec_date - last_committee_date).days < COMMITTEE_COOLDOWN_DAYS:
                continue

            # Risk committee check (electricity customers only for VaR aggregation)
            active_elec = [c for c in ELEC_CUSTOMERS if c["customer_id"] in current_risk]
            if not active_elec:
                continue

            portfolio_var_current = sum(
                current_risk[c["customer_id"]]["var_current_gbp"] for c in active_elec
            )
            portfolio_var_stressed = sum(
                current_risk[c["customer_id"]]["var_stressed_gbp"] for c in active_elec
            )
            _eac = {c["customer_id"]: _company_eac_estimate(c["customer_id"], rec["settlement_date"], settled_fold) for c in active_elec}
            total_eac_active = sum(_eac.values())
            sigma_weighted = sum(
                current_risk[c["customer_id"]]["sigma_recent"] * _eac[c["customer_id"]] / total_eac_active
                for c in active_elec
            )

            portfolio_state = {
                "customers": [
                    {
                        "customer_id": c["customer_id"],
                        "hedge_fraction": current_hf[c["customer_id"]],
                        "eac_kwh": _eac[c["customer_id"]],
                        "active_collateral_gbp": current_risk[c["customer_id"]]["active_collateral_gbp"],
                        "monthly_cost_of_capital_gbp": current_risk[c["customer_id"]]["monthly_cost_of_capital_gbp"],
                        "var_current_gbp": current_risk[c["customer_id"]]["var_current_gbp"],
                        "var_stressed_gbp": current_risk[c["customer_id"]]["var_stressed_gbp"],
                    }
                    for c in active_elec
                ],
                "gross_margin_ytd_gbp": ytd_gross,
                "net_margin_ytd_gbp": ytd_net,
                "capital_costs_ytd_gbp": ytd_capital,
                "sigma_recent": sigma_weighted,
                "forward_price_gbp_per_mwh": forward_price if commodity == "electricity" else 0.0,
            }

            settlement_period = rec.get("settlement_period", 1)
            triggered = monitor.update(
                treasury, rec["settlement_date"], settlement_period,
                portfolio_var_current, portfolio_var_stressed,
                portfolio_state, elec_records,
            )
            # Always update last_committee_date — prevents re-checking on every record
            # when conditions aren't met (old record-count cooldown had this bug too).
            last_committee_date = _rec_date
            if triggered:
                periods_since_committee = 0
                print(
                    f"\n  [RISK COMMITTEE] Woken at {rec['settlement_date']} — "
                    f"treasury £{treasury:.2f}"
                )
                try:
                    adjustments = risk_committee_agent.invoke(
                        rec["settlement_date"], settlement_period, dict(current_hf),
                    )
                    for adj_cid, new_hf_val in adjustments.items():
                        pending_committee_overrides[adj_cid] = new_hf_val
                        print(f"    {adj_cid}: hf override → {new_hf_val:.2f}")
                    committee_wake_ups.append({
                        "settlement_date": rec["settlement_date"],
                        "treasury_gbp": treasury,
                        "adjustments": adjustments,
                        "portfolio_var_current_gbp": portfolio_var_current,
                        "portfolio_var_stressed_gbp": portfolio_var_stressed,
                    })
                except Exception as exc:
                    print(f"    [ERROR] Committee invocation failed: {exc}")

        # THE REGISTERS SEE EVERY HALF-HOUR; the retained book keeps only the day. All three
        # are fed from `settled_this_term` here, the last point in the run at which the
        # per-period records exist. The SPINE is untouched: settlement above still walks 48
        # periods and prices each on its own rate (director ruling, GATE 13).
        period_registers.add(settled_this_term, segment_of=_SEGMENT_OF)
        treasury_drawdown.add(settled_this_term)
        all_records.extend(fold_to_days(settled_this_term))
        settled_fold.add(settled_this_term)
        if administration_event:
            break

        # Evolution (use actual vs naked net margin)
        actual_net = sum(r["net_margin_gbp"] for r in settled_this_term)
        if commodity == "electricity":
            months = len({r["settlement_date"][:7] for r in settled_this_term})
            naked_capital = counterfactual_risk["monthly_cost_of_capital_gbp"] * months
            naked_gross = sum(
                r["revenue_gbp"]
                - (r["consumption_kwh"] / 1000)
                * elec_price_lookup.get((r["settlement_date"], r["settlement_period"]), 0.0)
                for r in settled_this_term
            )
            naked_net = naked_gross - naked_capital
        else:
            months = len({r["settlement_date"][:7] for r in settled_this_term})
            naked_capital = counterfactual_risk["monthly_cost_of_capital_gbp"] * months
            gas_spot_lookup = {r["settlementDate"]: r["systemSellPrice"] for r in gas_records}
            aq_kwh = get_customer(cid)["aq_kwh"]
            daily_kwh = aq_kwh / 365.0
            naked_gross = sum(
                r["revenue_gbp"]
                - (daily_kwh / 1000.0) * gas_spot_lookup.get(r["settlement_date"], 0.0)
                for r in settled_this_term
            )
            naked_net = naked_gross - naked_capital

        # Phase 16c + 17a + 19a: record term margin + revenue for all commodities
        prev_term_margin[cid] = actual_net
        term_revenue = sum(r["revenue_gbp"] for r in settled_this_term)
        prev_term_revenue[cid] = term_revenue
        # Phase 22a: trigger post-crisis hangover when electricity term suffers >20% net loss.
        # Company observes this from its own P&L — customers scarred by crisis prices stay anxious
        # even when rates improve, so churn stays elevated for 2 renewal periods.
        if commodity == "electricity" and term_revenue > 0 and actual_net / term_revenue < -CRISIS_HANGOVER_LOSS_THRESHOLD:
            hangover_remaining[cid] = crisis_hangover_periods()
        if term_revenue > 0:
            if commodity == "electricity":
                portfolio_elec_margin_rates.append(actual_net / term_revenue)
            else:
                portfolio_gas_margin_rates.append(actual_net / term_revenue)  # Phase 19a

        # KNIFE3 step 23 (§3r): the backward-looking arm of the SAME desk — was the
        # hedge worth paying for, and where does that put next term's opening.
        new_hf, reason = hedge_desk.roll_hedge_fraction(hf, naked_net, actual_net)
        next_hf[cid] = new_hf
        evolution_logs[cid].append({
            "term_index": term_index, "term_start": term_start_str,
            "commodity": commodity, "hf_used": hf, "actual_net": actual_net,
            "naked_net": naked_net, "next_hf": new_hf,
        })

        _rate_str = f"£{unit_rate:.2f}/MWh" if unit_rate is not None else "flex/deemed"
        print(
            f"  {cid} ({commodity[:4]}) term {term_index:2d} ({term_start_str}→{term_end_str[:10]}): "
            f"hf={hf:.2f}→{new_hf:.2f}  "
            f"unit_rate={_rate_str}  "
            f"actual_net=£{actual_net:8.2f}  naked_net=£{naked_net:8.2f}"
        )

    # =================== REPORTING ===================

    if administration_event:
        print(f"\n!!! ADMINISTRATION EVENT on {administration_event['date']} !!!")
        print(f"    Customer: {administration_event['customer_id']} ({administration_event['commodity']})")
        print(f"    Treasury: £{administration_event['treasury_balance_gbp']:.4f}")
    else:
        final_t = all_records[-1]["treasury_cash_balance_gbp"] if all_records else STARTING_TREASURY_GBP
        print(f"\n=== SURVIVED full window. Final treasury: £{final_t:.2f} ===")

    yearly_records: dict[str, list] = defaultdict(list)
    for rec in all_records:
        yearly_records[rec["settlement_date"][:4]].append(rec)

    print("\n=== Portfolio P&L by calendar year (all commodities) ===")
    print(f"{'Year':<6} {'Gross £':>9} {'Cap £':>9} {'Net £':>9} {'Treasury £':>12} {'Flag':>8}")
    for year in sorted(yearly_records.keys()):
        yr = yearly_records[year]
        gross = sum(r["margin_gbp"] for r in yr)
        capital = sum(r["capital_cost_gbp"] for r in yr)
        net = sum(r["net_margin_gbp"] for r in yr)
        treas = yr[-1]["treasury_cash_balance_gbp"]
        flag = "CRISIS" if year in CRISIS_YEARS else ""
        print(f"{year:<6} {gross:>9.2f} {capital:>9.2f} {net:>9.2f} {treas:>12.2f} {flag:>8}")

    print("\n=== Commodity exposure split ===")
    for commodity in ["electricity", "gas"]:
        recs = [r for r in all_records if r.get("commodity") == commodity]
        gross = sum(r["margin_gbp"] for r in recs)
        cap = sum(r["capital_cost_gbp"] for r in recs)
        net = sum(r["net_margin_gbp"] for r in recs)
        print(f"  {commodity:12s}: gross=£{gross:.2f}  capital=£{cap:.2f}  net=£{net:.2f}")

    print("\n=== Per-customer lifetime P&L ===")
    for c in ELEC_CUSTOMERS + GAS_CUSTOMERS:
        cid = c["customer_id"]
        recs = [r for r in all_records if r["customer_id"] == cid]
        gross = sum(r["margin_gbp"] for r in recs)
        cap = sum(r["capital_cost_gbp"] for r in recs)
        net = sum(r["net_margin_gbp"] for r in recs)
        kwh = EFFECTIVE_EAC_KWH.get(cid) or c.get("aq_kwh")
        comm = c["commodity"]
        print(
            f"  {cid} ({comm[:4]}, {kwh:,.0f} kWh): "
            f"gross=£{gross:.2f}  capital=£{cap:.2f}  net=£{net:.2f}"
        )

    print(f"\n=== Customer lifecycle events: {len(customer_events_log)} ===")
    renewals_by_type: dict[str, int] = {}
    for evt in customer_events_log:
        renewals_by_type[evt["event_type"]] = renewals_by_type.get(evt["event_type"], 0) + 1
    print(f"  Renewed: {renewals_by_type.get('renewed', 0)}  Churned: {renewals_by_type.get('churned', 0)}")
    for evt in customer_events_log:
        flag = " *** CHURNED ***" if evt["event_type"] == "churned" else ""
        print(
            f"  {evt['customer_id']} {evt['event_date']}: "
            f"p_churn={evt['churn_probability']:.4f}  "
            f"p_win={evt['win_probability']:.4f}  "
            f"p_retain={evt['effective_retention_probability']:.4f}  "
            f"roll={evt['random_roll']:.4f}{flag}"
        )

    print(f"\n=== Context Handshake wake-ups: {len(committee_wake_ups)} ===")
    if committee_wake_ups:
        for wu in committee_wake_ups:
            adjs = ", ".join(f"{k}→{v:.2f}" for k, v in wu["adjustments"].items()) or "(none)"
            print(f"  {wu['settlement_date']}: treasury=£{wu['treasury_gbp']:.2f}  {adjs}")
    else:
        print("  (no wake-ups — thresholds not breached)")

    total_gross = sum(r["margin_gbp"] for r in all_records)
    total_capital = sum(r["capital_cost_gbp"] for r in all_records)
    total_bad_debt = sum(r.get("bad_debt_gbp", 0.0) for r in all_records)
    total_net = sum(r["net_margin_gbp"] for r in all_records)
    final_treasury = all_records[-1]["treasury_cash_balance_gbp"] if all_records else STARTING_TREASURY_GBP

    # Phase AF (domestic DSR/Capacity Market) + Phase NX (I&C demand response).
    # KNIFE pass 3 step 18 moved both behind one door (register §3m): enrolling
    # your own book in the CM and DFS, and booking what the aggregator leaves
    # you, is the supplier commercialising its own portfolio, not world physics.
    # They are one door and not two because they feed ONE total. The world hands
    # over the asset snapshot it resolved and its own I&C roster; the clearing
    # prices, DFS rates, eligibility floor and flex-kW estimates stay
    # company-side.
    _all_years = sorted({r["settlement_date"][:4] for r in all_records})
    _elec_cids = [c["customer_id"] for c in ELEC_CUSTOMERS]
    _flex = build_flexibility_revenue(
        report_years=_all_years,
        domestic_assets_by_date=(
            _domestic_flex_assets_by_date(
                household_demand_register, _all_years, _elec_cids
            )
            if household_demand_register is not None
            else None
        ),
        ic_elec_roster=_ic_flex_roster(ELEC_CUSTOMERS, EFFECTIVE_EAC_KWH),
    )
    flexibility_revenue_summary = _flex.domestic_summary
    ic_flexibility_summary = _flex.ic_summary
    _flex_by_year = _flex.domestic_revenue_by_year
    total_flexibility_revenue = _flex.total_revenue_gbp

    # Phase OA: I&C Broker/TPI Commission Model.
    # KNIFE step 22 (§3q): I&C customers procure electricity via brokers, and
    # which brokers the supplier is accredited with, on what tier, on what
    # basis and at what rate are the commercial terms of its own channel. They
    # now live behind company/interfaces/tpi_commission.py. The world hands over
    # the settled records and its own I&C roster; nothing else crosses.
    _ic_billing_ids = {c["customer_id"] for c in ELEC_CUSTOMERS if c.get("segment") == "I&C"}
    tpi_summary = build_tpi_commission(
        settled_records=all_records,
        ic_elec_customer_ids=_ic_billing_ids,
        report_years=_all_years,
    ).summary

    # Phases OG/OH/OI: the supplier's annual statutory return -- Renewables
    # Obligation, FiT levelisation levy, Climate Change Levy. KNIFE pass 3 step
    # 17 moved all three behind one door (register §3l): working out what you
    # owe off your own supply volumes is the supplier's statutory accounting,
    # not world physics. The world hands over the settled records and its own
    # I&C book; the obligation levels, buy-out prices and levy rates stay
    # company-side.
    _statutory = build_statutory_obligations(
        settled_records=all_records,
        report_years=_all_years,
        ic_elec_customer_ids={
            c["customer_id"] for c in ELEC_CUSTOMERS if c.get("segment") == "I&C"
        },
        ic_gas_customer_ids={
            c["customer_id"] for c in GAS_CUSTOMERS if c.get("segment") == "I&C"
        },
    )
    roc_summary = _statutory.roc_summary
    fit_summary = _statutory.fit_summary
    ccl_summary = _statutory.ccl_summary

    # Phase 27d: Triad risk for I&C customers.
    # Identify Triad periods for each winter in the run window, then compute
    # each I&C customer's TNUoS exposure. Uses SSP as a demand proxy.
    ic_customer_ids = [
        c["customer_id"]
        for c in _ALL_KNOWN_CUSTOMERS
        if c.get("segment") == "I&C"
    ]
    triad_log: list[dict] = []
    if ic_customer_ids:
        triad_winters = set()
        for rec in elec_records:
            d = date.fromisoformat(rec["settlementDate"])
            if d.month in {11, 12, 1, 2}:
                triad_winters.add(_triad_year(rec["settlementDate"]))
        for winter_year in sorted(triad_winters):
            triad_periods = identify_triad_candidates(elec_records, winter_year)
            if not triad_periods:
                continue
            for cid in ic_customer_ids:
                # From the REGISTER, not the book: `compute_triad_exposure` looks records up
                # by (settlement_date, settlement_period) and the book now holds days. The
                # register kept exactly these -- I&C accounts in the Triad season -- for it.
                cid_records = [r for r in period_registers.triad_records
                               if r.get("customer_id") == cid]
                if not cid_records:
                    continue
                exposure = compute_triad_exposure(cid, triad_periods, cid_records, winter_year)
                triad_log.append(exposure)

    print("\n=== Full-window portfolio summary ===")
    print(f"Gross margin:      £{total_gross:>12.2f}")
    print(f"Capital costs:     £{total_capital:>12.2f}")
    print(f"Bad debt:          £{total_bad_debt:>12.2f}")
    print(f"Net margin:        £{total_net:>12.2f}")
    print(f"Starting treasury: £{STARTING_TREASURY_GBP:>12.2f}")
    print(f"Final treasury:    £{final_treasury:>12.2f}")
    print(f"Treasury change:   £{final_treasury - STARTING_TREASURY_GBP:>+12.2f}")
    print(f"Capital cost ratio: {total_capital/total_gross*100:.1f}% of gross")
    if administration_event:
        print(f"OUTCOME: ADMINISTRATION on {administration_event['date']}")
    else:
        print("OUTCOME: SURVIVED — full window completed")

    # L3 payment coupled triad: measure the LIVE belief-vs-truth gap over this
    # run's population and write the DETECTION headline into the coupled gap
    # ledger. Wrapped fail-safe: a measurement error must NEVER kill the run
    # (the run's own outputs are the primary artefact) -- it surfaces as a loud
    # warning + a stale ledger entry, not a crashed run.
    try:
        _triad_head = None
        try:
            import subprocess as _subprocess
            _triad_head = _subprocess.check_output(
                ["git", "rev-parse", "HEAD"], text=True
            ).strip()
        except Exception:
            _triad_head = None
        _triad_result = _payment_triad.measure_and_write(
            run_git_commit=_triad_head, ledger_path=gap_ledger_path)
        if _triad_result is not None:
            _det = _triad_result["detection"]
            print(
                f"[coupled-triad W2_11<->D5] LIVE payment belief-vs-truth gap: "
                # D11: never print the detection headline as a bare scalar. It is
                # a BALANCED error over two directions, and the bare form is how
                # the retired recall-only figure got read as "nearly perfect
                # detection" while half the company's flags were on paid invoices.
                f"{_format_detection_summary(_det)} "
                f"(true failures {_triad_result['stats']['n_true_failures']}, "
                f"ever-flagged {_triad_result['stats']['n_flagged_failures']}, "
                f"non-DD blind {_triad_result['stats']['n_true_non_dd_failures']}, "
                # D10: the headline is reconciliation-determined -- the DD
                # channel's contribution is only visible in DAYS, never here.
                f"DD-channel unique detections "
                f"{_triad_result['stats']['n_flagged_via_dd_channel_only']}, "
                f"DD channel buys {_triad_result['stats']['dd_channel_days_earlier']} "
                f"days earlier detection); "
                # D19: never print the belief headline as a bare scalar either.
                # It was a population-TV distance until 2026-08-10, and the bare
                # form is precisely how a number blind to WHICH account holds
                # which belief got read as a per-case error rate.
                f"{_format_belief_summary(_triad_result['belief'])} "
                f"(population mix "
                f"{_triad_result['belief_population_mix'].gap:.4f}) "
                # D7: never print the ageing figure as a bare scalar -- it is a
                # bucket displacement with no baseline, and the bare form is how
                # the retired one got mis-read as a normalised score.
                f"{_format_ageing_summary(_triad_result['ageing'])}"
            )
            # WIRE the SAME live belief-vs-truth signal into the G1/G2/G3
            # fidelity machinery (background.live_fidelity_evidence). This is the
            # live company consumer the G atoms' blocked_on names; it reuses the
            # triad's already-measured primitives (no second draw, no clock). A
            # bridge failure is loud-but-non-fatal: the run must not die on a
            # HARNESS emission (defensive, matching the enclosing block).
            try:
                _fid_as_of_date = max(r.due_date for r in _payment_triad.records)
                _fid_as_of = _fid_as_of_date.isoformat()
                # SOURCE 2 (PLANNER_MINTED_payment_grid_coverage_2026-07-25):
                # partition the DETECTION dimension by the run's OWN observed
                # price regime (world-side UK gas-crisis calendar, never leaked
                # company-side) and light each honestly-measured A1_Gx cell,
                # instead of collapsing the whole regime-mixed run onto A1_G2.
                # A run spanning calm + crisis lights >1 cell; a single-regime
                # run lights one. Belief/ageing stay regime-mixed (named
                # simplification on each per-cell record).
                # KNIFE pass 3 step 33 (disposition register §3ab): the cells
                # are asked of the TRIAD, not computed here from its innards.
                # This block used to import `detection_cell_measurements` and
                # hand it `_payment_triad.consumer` -- a live company object,
                # held by the world's composition, obtained through a SECOND
                # bridge (`tools.couple_w2_11_d5`) that reaches the same two
                # company modules as `background.live_payment_triad` does. The
                # measurement is unchanged; who holds the consumer is not.
                from background.live_fidelity_evidence import emit_live_fidelity_cells
                _cell_gaps = _payment_triad.detection_cells(_fid_as_of_date)
                if len(_cell_gaps) >= 2:
                    _mc = emit_live_fidelity_cells(cell_gaps=_cell_gaps, as_of=_fid_as_of)
                    _lit = ", ".join(
                        f"{c}={_cell_gaps[c].detection_gap:.4f}" for c in _mc.cell_ids
                    )
                    print(
                        f"[fidelity-evidence G1/G2/G3] LIVE per-cell emission: "
                        f"{len(_mc.cell_ids)} cells lit ({_lit}) -> grid worst "
                        f"{_mc.grid_score.worst_cell} ({_mc.grid_score.fidelity_score:.4f}), "
                        f"gate PASS, {len(_mc.grid_score.untested_cells)} cells untested"
                    )
                elif _cell_gaps:
                    # Single regime present -> conservative single-cell collapse,
                    # fed from THAT CELL rather than from the triad headline.
                    #
                    # D12 (2026-08-09): the cells are now the SAME two-directional
                    # shape as the headline -- both directions on their own
                    # per-cell denominators -- so the grid is one measure end to
                    # end again. The headline still never enters the grid: it is
                    # scored over an EVER-FLAGGED population while the cells score
                    # the at-`as_of` belief, and feeding one into one branch and
                    # the other into the other would move the band for a reason no
                    # reader could see. The fidelity grid stays fed by
                    # `detection_cell_measurements` end to end.
                    _only_cell = next(iter(_cell_gaps.values()))
                    _fid_em = emit_live_fidelity_evidence(
                        detection_gap=_only_cell.detection_gap,
                        true_failures=_only_cell.true_failures,
                        believed_failures=_only_cell.believed_failures,
                        as_of=_fid_as_of,
                    )
                    print(
                        f"[fidelity-evidence G1/G2/G3] LIVE emission: cell {_fid_em.cell_id} "
                        f"gap={_fid_em.detection_gap} -> grid worst {_fid_em.grid_score.worst_cell} "
                        f"({_fid_em.grid_score.fidelity_score:.4f}), gate PASS, "
                        f"{len(_fid_em.grid_score.untested_cells)} cells untested"
                    )
                else:
                    # No cell carried any true failure -- nothing honestly
                    # measured, so nothing is emitted. Substituting the headline
                    # here would light a grid cell off a different measure than
                    # the one the cells are scored with (D11), which is how a
                    # grid gets a value it never earned.
                    print(
                        "[fidelity-evidence G1/G2/G3] no cell carried a true "
                        "payment failure -- nothing emitted (cells stay dark)"
                    )
            except Exception as _fid_exc:  # pragma: no cover - defensive
                print(f"WARNING [fidelity-evidence G1/G2/G3] live emission failed: {_fid_exc}")
        else:
            print("[coupled-triad W2_11<->D5] no true payment failures this run — gap not written")
    except Exception as _triad_exc:  # pragma: no cover - defensive, run must not die
        import traceback as _traceback
        print(f"WARNING [coupled-triad W2_11<->D5] live gap measurement failed: {_triad_exc}")
        _traceback.print_exc()

    # --- VALUE_CHAIN observation feed + MC-2 collateral death-test, 2026-08-12: one door.
    # KNIFE pass 3 step 19 (disposition register §3n). Marking the company's own book,
    # sizing its counterparty lines, deriving the variation margin it owes and asking at
    # what price move its facility breaks is the supplier's own treasury and credit-risk
    # function -- it is not world physics. The world hands over the book it holds, its
    # customer register's commodity column and the two PUBLIC spot histories; it takes back
    # a position. The credit block's peak_sample_date no longer passes through this file on
    # its way to the death test: that thread is now internal to the desk that owns both.
    # Both failure domains stay independent -- reported on the result, not raised (§3n).
    # R6 (2026-08-28): the supplier's OWN balance sheet crosses to its credit desk, so the
    # independent amount a counterparty demands above the mark can move. Three plain scalars, the
    # same shape `plan_growth_campaign_year` already uses -- what it holds, how many accounts it
    # holds it against, and the stressed close-out move MEASURED from the public spot history it
    # already marks with. No rate table, no counterparty internal, and nothing about the future.
    #
    # THIS IS WHAT JOINS ACQUISITION SPEND TO COLLATERAL. Campaign spend leaves `final_treasury`;
    # free equity falls; below the point where it covers the position, counterparties start asking
    # for collateral over the mark on a book that has not moved. That is the CMA's mechanism, and
    # until now this repository had both ends of it and no wire.
    #
    # THE CLOSE-OUT MOVE IS MEASURED INSIDE THE DESK, NOT HERE, and the first draft got that wrong:
    # it imported `company.risk.independent_amount` directly and the wall-crossing register refused
    # the commit -- a live SIM->company crossing with no disposition. It was right to. The desk
    # already holds these same spot records to mark the book with, so measuring the close-out there
    # means one reading of one series rather than two, and the world hands over only what it holds:
    # what the supplier is worth and how many accounts it holds it against.
    #
    # WHAT `accounts_held` COUNTS, AND WHY IT IS NOT `len(_ALL_KNOWN_CUSTOMERS)` (2026-08-29). It
    # was, and that was 24 -- a number that is none of the five populations this run publishes and
    # is wrong in three separate ways at once. `_ALL_KNOWN_CUSTOMERS` is bound at IMPORT, so it is
    # the static founder roster and cannot see one of the accounts the funnel won; it is keyed by
    # per-COMMODITY customer_id, so every dual-fuel household counted twice against a £130 that is
    # levied once per account; and it makes no domestic/non-domestic distinction, though SLC 27's
    # capital regime is a domestic obligation. Net of the three the MCR claim came out at £3,120
    # against a book that in fact obliges £15,600, and free equity was overstated by £12,480.
    #
    # THE POPULATION IS NOW THE SAME SUPPLIER `final_treasury` DESCRIBES, and that is the whole
    # point of the change rather than a detail of it. `free_equity = net_assets - accounts x £130`
    # is a SUBTRACTION, so both sides must count one supplier. `final_treasury` is read off
    # `all_records` -- the SETTLED book -- so the account count is read off `all_records` too.
    # Note what this deliberately does NOT use: the commercial book the campaign won (587 accounts
    # by 2025). That is a real and larger supplier, and the growth desk is right to plan against
    # it, because it nets 587 against the FOUNDING CAPITAL, which is that same supplier's balance
    # sheet. Netting 587 accounts of MCR against a treasury earned on the ~17.9% of them our
    # settlement engine can process would mix two suppliers, and the only way to repair it in that
    # direction is to scale the treasury up by the sample rate -- inventing a number, which is the
    # defect R1 exists to remove. The settled-book answer has no invented number in it.
    #
    # THE WALL QUESTION, asked out loud because this is a company-side figure: could a real
    # supplier's finance function put this number in front of a counterparty? Yes, and it is close
    # to the only number it could -- how many domestic accounts it bills, on supply today, dual
    # fuel counted once. Every leg of the selection is a read of the supplier's own settlement
    # record and its own customer register. Nothing here consults `churned_billing_accounts`, which
    # is the WORLD's truth about who left; the supplier reads cessation off its own 35-day
    # continuity rule and is allowed to be wrong about it.
    #
    # SO THE COUNTING HAPPENS IN THE DESK, not here, exactly as the close-out move already does.
    # The world hands over the two things it holds -- the settled record and the customer register
    # -- and the desk applies the selection. Counting here would have meant `simulation` importing
    # `saas.capital.solvency`, a new SIM->company crossing the wall ratchet refuses and should:
    # the rule for who owes £130 is the company's, and belongs on the company's side of the seam.
    #
    # THE REGISTER IS THE LIVE ROSTER, not the import-time snapshot: `ACQUIRED_CUSTOMERS` is the
    # object the supply book appends funnel wins to (supply_book.py, IDENTITY), so the accounts
    # this campaign won carry their own segment here instead of falling through a default.
    _collateral = build_counterparty_collateral(
        hedge_desk.book,
        commodity_by_customer_id={c["customer_id"]: c["commodity"] for c in _ALL_KNOWN_CUSTOMERS},
        elec_spot_records=elec_records,
        gas_spot_records=gas_records,
        mark_date=effective_end,
        balance_sheet={"net_assets_gbp": final_treasury},
        settled_records=all_records,
        segment_by_customer_id={
            c["customer_id"]: c.get("segment", "resi")
            for c in CUSTOMERS + SUCCESSOR_CUSTOMERS + ACQUIRED_CUSTOMERS
        },
    )
    _wholesale_credit_summary = _collateral.credit_summary
    _margin_call_summary = _collateral.margin_call_summary
    _mc2_death_test_summary = _collateral.death_test_summary
    if _collateral.credit_feed_error is not None:  # pragma: no cover - defensive
        import traceback as _feed_tb
        print(f"WARNING [value-chain credit/margin feed] failed: {_collateral.credit_feed_error}")
        _feed_tb.print_exception(_collateral.credit_feed_error)
    if _collateral.death_test_error is not None:  # pragma: no cover - defensive
        import traceback as _mc2_tb
        print(f"WARNING [MC-2 collateral death-test] failed: {_collateral.death_test_error}")
        _mc2_tb.print_exception(_collateral.death_test_error)

    # W1_11 settlement switch: the control runs on the SETTLED book, not on the
    # intention. It raises rather than returns False on a book it cannot judge.
    if not settlement_providers_match_eligibility(
        demand_provider_by_customer, fabric_eligibility_verdicts
    ):
        raise AssertionError(
            "the fabric settlement switch did not reach the book it was declared for: "
            f"providers={demand_provider_by_customer}, "
            f"eligible={sorted(v.customer_id for v in fabric_eligibility_verdicts if v.is_eligible)}"
        )

    # ...and the control above cannot catch the switch being emptied rather than
    # missed. A premise refused because the weather archive stops short of the
    # settlement window is structurally eligible: it reverts to the rescaled
    # national shape while the match-control still reads clean, because an
    # undeclared customer cannot be an unswitched one. Extend REPORT_END past the
    # archive and the whole fabric population disappears in silence, so the empty
    # set is asserted separately here rather than trusted.
    _coverage_refused = coverage_refusals(fabric_eligibility_verdicts)
    if _coverage_refused:
        raise AssertionError(
            "the fabric settlement switch was silently emptied by archive coverage: "
            f"{_coverage_refused} are structurally eligible premises settled on the "
            f"legacy provider because the weather archive does not span "
            f"{REPORT_START}..{effective_end}"
        )

    return {
        "all_records": all_records,
        "administration_event": administration_event,
        # W1_11: which generator settled each electricity customer's demand, and
        # why a premise is not fabric-driven -- recorded so an unexplained
        # population change is visible in the run, not inferred from its numbers.
        "demand_provider_by_customer": dict(demand_provider_by_customer),
        "fabric_eligibility": [
            {"customer_id": v.customer_id, "is_eligible": v.is_eligible, "reason": v.reason}
            for v in fabric_eligibility_verdicts
        ],
        # The treasury path's turning points for the WHOLE book, folded in accumulation order as
        # the balances were produced, each tagged with the year of its record.
        # `annual_report._drawdown_events_by_year` walks this instead of re-deriving a path from
        # the finished book. One path, not one per year: a year's records are a subsequence of a
        # portfolio running total, so bucketing them showed one swing as an event in each of two
        # years (2026-08-24; see `TreasuryDrawdown`).
        "treasury_drawdown_path": treasury_drawdown.points(),
        # The other two registers. `all_records` holds DAILY rows from here on; the half-hour
        # survives only where a published figure needs it, which is these.
        "worst_period_by_year": period_registers.worst_period_by_year,
        "tou_by_customer": period_registers.tou_by_customer,
        "committee_wake_ups": committee_wake_ups,
        "customer_events": customer_events_log,
        "churned_billing_accounts": sorted(churned_billing_accounts),
        "won_successor_activations": won_successor_activations,
        "hedge_evolution": evolution_logs,
        "total_gross": total_gross,
        "total_capital": total_capital,
        "total_bad_debt": total_bad_debt,
        "total_net": total_net,
        "final_treasury": final_treasury,
        "starting_treasury": STARTING_TREASURY_GBP,
        # Phase 8a: growth mandate outputs
        "acquisition_spend_events": acquisition_spend_events,
        "acquisition_funnel_log": acquisition_funnel_log,
        "fixed_cost_events": fixed_cost_events,
        "acquired_customers": [c["customer_id"] for c in ACQUIRED_CUSTOMERS],
        "growth_mandate": growth_mandate_label(),
        # Phase 11a: basis risk — company estimate vs sim ground truth per term
        "basis_risk_terms": basis_risk_terms,
        # Phase 11b: churn basis risk — company churn estimate vs sim ground truth per renewal
        # Phase 39a: extended with SVT comparison fields
        "churn_basis_risk": _build_churn_basis_risk(customer_events_log),
        # Phase 12a: company CRM event log — dated artefacts of churn and acquisition
        "company_event_log": _build_company_event_log(
            customer_events_log, won_successor_activations, fresh_acquisitions, SUCCESSOR_MAP
        ),
        "retention_log": retention_log,
        "nudge_physics_log": nudge_physics_log,
        "retention_cost_events": retention_cost_events,
        "no_offer_churn_log": no_offer_churn_log,
        "company_gas_churn_log": company_gas_churn_log,
        "volume_tolerance_log": volume_tolerance_log,
        "triad_log": triad_log,
        "margin_feedback_log": margin_feedback_log,
        "profitability_uplift_log": profitability_uplift_log,
        "value_arm_log": value_arm_log,   # the value cycle's per-renewal decisions
        # ...and the population those decisions were drawn FROM. See the list's own note.
        "value_arm_funnel_log": value_arm_funnel_log,
        "demand_response_log": demand_response_log,   # Phase 52
        "hedge_var_log": hedge_var_log,
        "dynamic_pricing_log": dynamic_pricing_log,
        "rate_decomposition_log": rate_decomposition_log,   # EP2 sub-atom 3
        # Phase 12e: aggregated company-model divergence by year
        "company_divergence": _compute_company_divergence(
            basis_risk_terms,
            [
                {
                    "term_start": e["event_date"],
                    "churn_estimate_error_pct": e["churn_estimate_error_pct"],
                }
                for e in customer_events_log
                if e.get("company_churn_estimate") is not None
            ],
            demand_estimation_log=demand_estimation_log,  # Phase 23a
        ),
        "demand_estimation_log": demand_estimation_log,  # Phase 23a: full log for report
        # Phase 43a: company trading book — forward position lifecycle
        "trading_book": hedge_desk.summary(),
        # VALUE_CHAIN observation feed (2026-07-24): the two board-level credit/liquidity
        # registers, marked at an end-of-run observable forward-price snapshot (None if the
        # mark could not be formed from observable history).
        "wholesale_credit_exposure": _wholesale_credit_summary,
        "margin_call_book": _margin_call_summary,
        # MC-2 collateral death-test (2026-07-27): breaking-strain sweep against the real 2021-22
        # replay (DIRECTOR_RULING_MC2 §2). None if the run does not reach the 2021-22 window.
        "mc2_collateral_death_test": _mc2_death_test_summary,
        # Phase AF: DSR/Capacity Market flexibility revenue
        "flexibility_revenue_summary": flexibility_revenue_summary,
        "flexibility_revenue_by_year": _flex_by_year,
        "total_flexibility_revenue": total_flexibility_revenue,
        # Phase NX: I&C demand response enrollment
        "ic_flexibility_summary": ic_flexibility_summary,
        # Phase OA: I&C broker/TPI commission
        "tpi_summary": tpi_summary,
        # Phase OG: Renewable Obligation cost
        "roc_summary": roc_summary,
        # Phase OH: FiT Levelisation Levy
        "fit_summary": fit_summary,
        # Phase OI: Climate Change Levy pass-through
        "ccl_summary": ccl_summary,
        "per_customer_behavioral": _build_behavioral_trajectories(
            ELEC_CUSTOMERS + GAS_CUSTOMERS,
            household_demand_register,
            _cx_desk,
            _bill_shock_dates,
        ),
        # Phase NJ: company churn model calibration report
        "churn_model_performance": score_churn_estimates(
            customer_events_log, retention_log, no_offer_churn_log
        ),
        # Phase QL Part 2: hidden churn-journey state trajectory (SIM-side shadow
        # tracker -- does not gate the roll_lifecycle_event dice roll itself)
        "churn_journey_log": churn_journey_log,
        # Phase RU: solicited feedback survey engine (FEEDBACK_AND_REPUTATION.md Layer 1)
        "feedback_survey_log": feedback_survey_log,
        "reputation_events_log": reputation_events_log,
        "nps_annual_summaries": {yr: _cx_desk.nps_annual_summary(yr) for yr in range(2016, 2026)},
        "complaint_annual_summaries": {yr: _cx_desk.complaint_annual_summary(yr) for yr in range(2016, 2026)},
        "gri_trajectory": [
            {
                "year": yr,
                "gri_score": _churn_journey_register.gri.score(date(yr, 12, 31)),
                "band": _churn_journey_register.gri.band(date(yr, 12, 31)).value,
            }
            for yr in range(2016, 2026)
        ],
    }



def _build_behavioral_trajectories(customers, hdr, cx_desk, bill_shock_dates=None):
    """Splice the world's own per-customer trajectories around the company's
    experience record.

    KNIFE step 21 (§3p): the payment score/metrics/miss-trajectory and the
    satisfaction score/trajectory used to be assembled here, field by field,
    out of two of the company's CRM books. They are now one call through the
    door — `cx_desk.behavioural_record(cid)`, whose key order is part of that
    contract. Phase QT's per-year satisfaction history and Phase QV's payment
    miss buckets (SIM_TAB_OVERHAUL.md) are unchanged; only who assembles them
    moved.
    """
    if hdr is None:
        return {}
    sim_years = list(range(2016, 2026))
    out = {}
    all_cids = {c["customer_id"] for c in customers}
    empty_record = {
        "payment_behaviour_score": None,
        "payment_behaviour_metrics": None,
        "company_satisfaction_score": None,
        "satisfaction_score_trajectory": [],
        "payment_miss_trajectory": [],
    }
    for cid in sorted(all_cids):
        out[cid] = {
            "income_stress_trajectory": hdr.income_stress_trajectory(cid, sim_years),
            "life_event_history": hdr.life_event_history(cid),
            **(cx_desk.behavioural_record(cid) if cx_desk else dict(empty_record)),
            "bill_shock_history": (bill_shock_dates or {}).get(cid, []),
        }
    return out


if __name__ == "__main__":
    main()
