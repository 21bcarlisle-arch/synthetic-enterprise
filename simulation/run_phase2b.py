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

import bisect
import calendar
import dataclasses
import heapq
import itertools
import random
import sys
from collections import defaultdict
from datetime import date, datetime, time, timedelta

import sim.risk_committee_agent as risk_committee_agent
import simulation.dd_shock_response as _dd_shock_response
import simulation.payment_method_dynamics as _method_dynamics
import simulation.world_payment_truth as _world_payment_truth
from background.gap_metric import format_ageing_summary as _format_ageing_summary
from background.gap_metric import format_belief_summary as _format_belief_summary
from background.gap_metric import format_detection_summary as _format_detection_summary
from background.live_fidelity_evidence import emit_live_fidelity_evidence
from background.live_payment_triad import LivePaymentTriad
from company.interfaces.bill_assembly import owed_after_scheme_credit, scheme_credit
from company.interfaces.churn_estimation import (
    RenewalObservation,
    SvtSegmentObservation,
    active_pressure_ledger,
    crisis_hangover_periods,
    ending_term_type,
    estimate_churn_without_rate_history,
    estimate_renewal_churn,
    estimate_secondary_fuel_churn,
    estimate_svt_drift,
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
    book_retention_holdout,
    book_retention_offer,
    decide_acquisition,
    growth_mandate_label,
    mandate_permits_replacement,
    new_retention_holdout,
    refuse_retention_offer_below_own_cost_floor,
    replacement_cost_avoided_gbp,
    retention_bad_debt_charge,
    retention_cut_share_at_price_match,
    retention_cut_share_at_risk_tiers,
    retention_engagement,
    retention_offer_can_buy_anything,
    retention_save_holdout_draws,
    retention_value_at_save_rate_lower_bound,
    retention_value_protected,
    retention_value_weighed_by_save_odds,
)
from company.interfaces.hedge_desk import build_hedge_desk, hedge_mandate
from company.interfaces.move_with_us import request_move_with_us_offer
from company.interfaces.point_in_time_view import PointInTimeView, build_price_bitemporal_log
from company.interfaces.renewal_offer import (
    request_company_forward_estimate,
    request_fixed_unit_rate,
)
from company.interfaces.renewal_rate_chain import (
    RenewalDecisionInputs,
    bill_the_shared_rise,
    decide_renewal,
    open_portfolio_margin_book,
    portfolio_position,
)
from company.interfaces.save_offer import (
    SaveLeg,
    published_best_deal_gap_share,
    published_default_rate_ex_vat,
    request_household_save,
    request_save_offer,
)
from company.interfaces.statutory_obligations import build_statutory_obligations
from company.interfaces.supply_book import (
    acquired_supply_points,
    incoming_occupant_supply_points,
    open_change_of_supplier_register,
    open_move_out_register,
    open_priority_services_register,
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
from company.interfaces.transfer_objection import (
    open_transfer_objection_register,
    request_debt_objection,
)
from company.policy.decision_policy import (
    CURRENT_POLICY,
    DEFAULT_BELIEF_OWN_BOOK,
    DEFAULT_BELIEF_SOURCES,
    DecisionPolicy,
    active_policy,
    framing_type_for,
)
from sim.cache_store import get_cached_prices, log_cache_access
from sim.customer_state_layer import (
    VOID_CONSUMPTION_GAP_REASON,
    account_move_out,
    as_void_row,
    incoming_occupant_record,
    moves_active,
    term_window_under_move,
    unnamed_kwh_after_move,
    unnamed_until,
    void_end,
)
from sim.forward_curve import (
    SUMMER_MULTIPLIER,
    WINTER_MONTHS,
    WINTER_MULTIPLIER,
    generate_forward_price,
    short_first_term_lookbacks,
)
from sim.gas_prices_history import RECORD_START as NBP_RECORD_START
from sim.gas_prices_history import SHORT_RECORD_REASON as NBP_SHORT_RECORD_REASON
from sim.gas_prices_history import load_nbp_history
from sim.profile_class_1 import load_pc1_shape
from sim.profile_class_2 import load_pc2_shape
from sim.profile_class_3 import load_pc3_shape
from sim.risk_committee import RiskCommitteeMonitor
from sim.risk_engine import assess_term_risk, is_administration_triggered
from sim.system_prices_history import RECORD_START as SSP_RECORD_START
from sim.system_prices_history import SHORT_RECORD_REASON as SSP_SHORT_RECORD_REASON
from sim.system_prices_history import get_system_prices_range
from sim.weather_hdd import REFERENCE_MONTHLY_HDD, get_hdd, relocate_premise_sky
from simulation.acquisition_funnel import run_acquisition_funnel
from simulation.bad_debt_incidence import world_bad_debt_incidence
from simulation.bill_shock_tracker import count_rate_shocks as _count_rate_shocks
from simulation.churn_journey import ChurnJourneyRegister
from simulation.competitor_reference import CompanyPositionLedger
from simulation.customer_events import (
    DEPARTURE_OCCASION_SVT_SEGMENT,
    RENEWAL_DECLINED_FIX,
    churn_roll_for_renewal,
    declined_fix_event,
    departure_decision_leg,
    departure_event,
    departure_rolled_at_renewal,
    households_own_records,
    position_vs_default,
    renewal_outcome,
    roll_lifecycle_event,
    svt_conversion_event,
)
from simulation.dd_review_in_loop import InLoopDDReview
from simulation.dd_shock_response import RECORD_KEY as _DD_SHOCK_RECORD_KEY
from simulation.dd_shock_response import DDShockResponseBook, respond_to_told_amount
from simulation.debt_objection import apply_objection, debt_objection_active, objection_request_day
from simulation.demand_model import (
    build_demand_shape,
    eac_scaled_shape_fn,
    solar_generation_shape,
)
from simulation.demand_response import compute_shift_fraction, make_shifted_shape_fn
from simulation.departure_level_anchor import year_level_anchor
from simulation.departure_risks import (
    DECLARED_SENSITIVITY_SCALE,
    build_departure_risks,
    total_departure_probability,
)
from simulation.dwelling_records import (
    DEFAULT_ASSETS,
    DEFAULT_HEATING_SYSTEM,
    DEFAULT_OCCUPANCY_PATTERN,
    build_properties,
)
from simulation.fabric_demand_path import (
    DEFAULT_TRACE_SEED,
    FABRIC_PROVIDER,
    LEGACY_PROVIDER,
    METERED_PROVIDER,
    FabricEligibility,
    WeatherWorldSource,
    build_fabric_series_for_site,
    coverage_refusals,
    fabric_eligibility,
    fabric_providers_for_book,
    fabric_shape_fn,
    rebind_fabric_verdict_to_new_home,
    registry_eac_from_own_reads,
    settled_shape_is_physically_textured,
    settlement_providers_match_eligibility,
    the_switch_moves_the_settled_volume,
    the_switch_reaches_the_book,
    untextured_premises_within_a_textured_book,
)
from simulation.fabric_physics import DEFAULT_LATITUDE_DEG
from simulation.feedback_survey import (
    dispatch_complaint_and_resolution,
    dispatch_csat_survey,
    dispatch_dd_shock_complaint,
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
from simulation.household import (
    GAS_LEG_ID_SUFFIX,
    HeatingSystem,
    household_of,
    households_whose_account_closed,
)
from simulation.household_demand import HouseholdDemandRegister
from simulation.household_demand_shape import (
    SeasonalGasRefusal,
    seasonal_gas_split,
    seasonal_gas_splits_for_book,
)
from simulation.household_segments import active_renewal_probability_for_customer
from simulation.household_segments import tenure_for_customer as _tenure_of_household
from simulation.live_population import (
    campaign_quotes_paid_for,
    founding_capital_gbp,
    live_drawn_households,
    live_dwellings,
    live_population,
    population_seed_argument,
    run_base_seed,
)
from simulation.move_destination import (
    draw_destination,
    household_at_destination,
    next_move_from_destination,
)
from simulation.move_destination import shape_across_a_move as _shape_across_a_move
from simulation.move_out_notice_feed import MoveOutNoticeFeed
from simulation.move_with_us_answer import (
    NOT_ANSWERABLE,
    default_tariff_roll,
    household_moves_with_us,
    move_with_us_active,
    p_stay_on_default_tariff,
    take_up_scale,
)
from simulation.nudge_physics import framing_effectiveness_multiplier, susceptibility_for
from simulation.payment_timing import generate_payment_record, stress_bad_debt_multiplier
from simulation.policy_costs import (
    get_gas_ccl_per_mwh,
    get_gas_network_cost_per_mwh,
    get_ggl_per_mwh,
)
from simulation.record_table import RecordTable
from simulation.registration_loss_feed import RegistrationLossFeed, supply_points_on_supply
from simulation.renewal_engagement import passive_churn_cap_for, rolls_active_renewal
from simulation.renewals import NOTICE_DAYS, build_renewal_schedule, price_fixed_term
from simulation.reputation_index import ReputationEventType
from simulation.resentment_ledger import FrictionEventType
from simulation.retention_offer import ask_world_at_offer, offered_rate
from simulation.save_on_loss_notice import (
    billed_rate_when_saved,
    household_takes_save,
    save_offers_active,
    world_save_response_scale,
)
from simulation.segment_vocabulary import is_business
from simulation.settlement import CONTRACT_LENGTH_DAYS
from simulation.settlement_daily import PeriodRegisters, TreasuryDrawdown, fold_to_days
from simulation.settlement_fold import SettlementFold
from simulation.sim_satisfaction import sim_satisfaction_score as _sim_satisfaction_score
from simulation.svt_product import (
    SVT_TARIFF_TYPE,
    build_svt_schedule,
    inertia_hazard_for_term,
    price_segment_for_payment_method,
    stamp_hmt_epg_receipt,
)
from simulation.tou_periods import is_peak_period as _is_peak_period
from simulation.triad import (
    _triad_year,
    build_triad_alert_set,
    compute_triad_exposure,
    identify_triad_candidates,
    make_triad_aware_shape_fn,
)
from simulation.volume_tolerance import compute_term_volume_tolerance
from simulation.vulnerability_state import (
    hidden_state_active,
    registration_notices,
    wire_registrations,
)
from simulation.weather_inputs import (
    adopt_book,
    adopt_shared_world,
    cloud_cover_for_customer,
    lookback_mean_temps,
    weather_means_for_customer,
    weather_refusals_for_book,
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
# EP17's switch: `SE_POPULATION_SEED` names the book seed; unset is today's book, byte for byte.
CUSTOMERS = live_population(base_seed=population_seed_argument())
SUCCESSOR_CUSTOMERS = successor_supply_points()

REPORT_START = "2016-01-01"
REPORT_END = "2025-06-07"
CRISIS_YEARS = {"2021", "2022"}


def effective_report_end(report_end: str | None) -> str:
    """THE DAY THIS RUN'S WORLD ACTUALLY STOPS, from the value the caller handed the run.

    A FUNCTION RATHER THAN THE INLINE `report_end or REPORT_END` IT REPLACES, because it now has
    a second reader. `tools/run_annual_report._simulation_window` stamps the window into the
    published artefact, and a stamp that resolves the default with its own copy of `or REPORT_END`
    is a claim about a branch it does not watch -- the same shape as reading `--fast` instead of
    `sim.risk_committee_agent.fast_mode_enabled()`, which stamped the wrong committee for exactly
    the launch shape the arms use. One predicate, two readers, so they cannot disagree.

    `None` MEANS UNTRUNCATED AND IS NOT AN ABSENT ANSWER. Every caller that passes nothing runs
    the full 2016-2025 window, so `effective_report_end(None)` IS the full-window boundary and is
    how the stamp asks for it -- never by importing `REPORT_END`, which would bind a second copy
    at import time and keep agreeing after this constant moved.
    """
    return report_end or REPORT_END

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
#: THE DECLINE-AND-STAY RULE'S SWITCH (2026-10-02): a domestic household that stays never
#: contracts a fixed renewal above the default tariff it would otherwise pay; it goes onto that
#: default for the term instead (`customer_events.renewal_outcome`). ON since the pre-registered
#: pair graded it at 822218441 (P1-P6 in `docs/staging/
#: WORKER_FINDING_AN_SVT_HOUSEHOLD_CAN_DECLINE_THE_FIX_DESIGN_AND_BASELINE_2026-10-02.md`): P5 held,
#: and the P3/P4 refutations trace to a decline being a calendar event as well as a price one.
#: Read as a module global at run time, so a paired run can switch it off in-process; off, the
#: loop's output is byte-identical to the code before the splice existed (P6).
DECLINE_A_FIX_ABOVE_THE_DEFAULT: bool = True

#: Stamped on a default-tariff segment spliced in for a declined term. Such a segment is not a
#: boundary the schedule builders counted, so it must not advance `term_indices` -- the loop's
#: engagement seed `f"{account}_{term_index}"` has to keep agreeing with the builders'
#: `f"{household}_{len(terms)}"` at every later boundary (PB6, 2026-09-29).
_DECLINED_FIX_SPLICE = "declined_fix_splice"

#: Stamped on a riding leg's term (a dual household's gas) that has been put back in the heap until
#: its household's decision leg has passed a term start inside it. A leg's whole term is posted at
#: once, and since the book went dual (c136809f53) a gas term starts days before the electricity
#: term whose roll can end the household, so posted at its own start it billed up to a year past a
#: departure (WORKER_FINDING_A_DUAL_HOUSEHOLD_THAT_LEAVES_..._2026-10-22).
_HELD_FOR_THE_DECISION_LEG = "held_for_the_decision_leg"

#: Stamped on a fixed term the loop struck for a woken SVT household that chose to stay (C30). The
#: household took it at the contact, so its start is not a renewal: no departure roll and no
#: decline against the default.
_WOKEN_REFIX = "woken_svt_stayer_refix"

# Phase 47a: segment lookup for Ofgem cap — resi customers subject to price cap
_RESI_CUSTOMER_IDS: frozenset[str] = frozenset(
    c["customer_id"] for c in CUSTOMERS if c.get("segment") == "resi"
)
# Phase 7e: successor electricity customers. NEVER SUPPLIED SINCE 2026-10-10: they were activated
# by a "home-move win" rolled on every renewal churner, and a household that switches at renewal
# vacates nothing (`simulation/customer_events.py`). A real move's incoming occupant is B7's
# (`_admit_incoming_occupant`). The roster entries stay only because their weather and fabric
# draws sit in shared streams; retiring them from the roster is its own measured change.
SUCCESSOR_ELEC_CUSTOMERS = [c for c in SUCCESSOR_CUSTOMERS if c["commodity"] == "electricity"]
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

#: THE REGISTRY AS IMPORT DREW IT, kept so every run starts from it (H50, 2026-10-07). `main()`
#: rewrites a fabric premise's `eac_kwh` to its own reads IN the shared roster dicts, and admits
#: incoming-occupant legs into `EFFECTIVE_EAC_KWH`. Phase 4c reads those records AFTER the run,
#: so the reset is at a run's START, never its end: a second run in one process -- the A/B's
#: second arm -- must not start on the first run's rewrite.
_DRAWN_REGISTRY_EAC_KWH: dict[str, float | None] = {
    c["customer_id"]: c["eac_kwh"] for c in ELEC_CUSTOMERS + SUCCESSOR_ELEC_CUSTOMERS
}
_DRAWN_EFFECTIVE_EAC_KWH: dict[str, float] = dict(EFFECTIVE_EAC_KWH)


def register_hh_accounts_eac(
    customers: list[dict], hh_consumption_by_customer: dict[str, dict[str, list[float]]],
) -> list[tuple[str, float, str]]:
    """Write the registry EAC a gaining supplier is handed into each half-hourly record that
    registered none, from its own metered import (`registry_eac_from_own_reads`). Returns
    `(customer_id, kwh, basis)` for each record it wrote; a record already registered is left."""
    written = []
    for c in customers:
        if not is_hh_customer(c) or c["eac_kwh"] is not None:
            continue
        reads = hh_consumption_by_customer[c["customer_id"]]
        eac, basis = registry_eac_from_own_reads(
            hh_shape_fn(reads), list(reads), c["acquisition_date"])
        c["eac_kwh"] = round(eac, 1)
        written.append((c["customer_id"], c["eac_kwh"], basis))
    return written


def start_from_the_drawn_book() -> None:
    """Put back what a previous run in this process wrote into module-level book state: the
    registry EACs, `EFFECTIVE_EAC_KWH`, and the run's own acquisitions."""
    for c in ELEC_CUSTOMERS + SUCCESSOR_ELEC_CUSTOMERS:
        c["eac_kwh"] = _DRAWN_REGISTRY_EAC_KWH[c["customer_id"]]
    EFFECTIVE_EAC_KWH.clear()
    EFFECTIVE_EAC_KWH.update(_DRAWN_EFFECTIVE_EAC_KWH)
    ACQUIRED_CUSTOMERS.clear()

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

EARLIEST_SSP_DATE = SSP_RECORD_START
COMMITTEE_COOLDOWN_PERIODS = 1440
COMMITTEE_COOLDOWN_DAYS = 30  # calendar-day cooldown; replaces record-count approach

SHAPE_LOADERS = {1: load_pc1_shape, 2: load_pc2_shape, 3: load_pc3_shape}


def registered_profile_class(customer: dict, household_register, as_of: str) -> int:
    """The profile class this home's meter point was registered on, as the world holds it.

    In 2016-2025 the class followed the METER: a domestic meter with an off-peak register was PC2,
    "Domestic Economy 7" (docs/data-sources/profile-class-2.md). The world puts a two-rate meter in
    a home only where its heating needs one -- a storage heater charges overnight on it
    (`fabric_physics.storage_charge_kwh`) -- so a home drawn with `ELECTRIC_STORAGE` is PC2 and
    every other domestic home keeps the roster's class. E7 meters in gas-heated or direct-electric
    homes are a GAP (G2, G3 there), not a zero anyone measured.

    Read from the drawn household at `as_of` (the start of supply), never from
    `dwelling_records.build_properties`, whose `heating_system` is `electric_storage` by DEFAULT
    for any home without a gas account and so would register oil-, heat-pump- and communal-heated
    homes on E7. A home the world drew no household for keeps the roster's class.
    """
    roster = customer.get("profile_class", 1)
    if roster != 1:
        return roster
    household = household_register.household_at_date(customer["customer_id"], as_of)
    if household is not None and household.heating_system == HeatingSystem.ELECTRIC_STORAGE:
        return 2
    return roster

#: Profile classes whose published base shape is a DOMESTIC average, and for which
#: an account's own annual consumption is therefore the right level. PC1 is
#: "domestic unrestricted", PC2 "domestic Economy 7"; PC3 is non-domestic and its two SME accounts keep the
#: published Group Average Demand level until the same question is answered for a
#: non-domestic profile from its own evidence, which is a separate piece of work.
_EAC_LEVELLED_PROFILE_CLASSES = frozenset({1, 2})


def _base_profile_eac(customer: dict) -> float | None:
    """The annual consumption that sets the LEVEL of this account's base profile,
    or None to leave the published Group Average Demand level alone.

    ONE function, called by BOTH `_weather_adjusted_shape_fn` call sites, because
    the second of them builds the LEGACY COUNTERFACTUAL that W1_11's
    `the_switch_moves_the_settled_volume` control grades the fabric provider
    against. Two independent decisions about the level here would move that
    control's subject for a reason that has nothing to do with fabric.

    WHOSE NUMBER THIS IS, said plainly because it matters and is not yet settled.
    On a drawn account, `eac_kwh` is the world's own draw
    (`population_draw._draw_one` samples the published Ofgem TDCV band) rendered
    into the supplier's roster VERBATIM by `SyntheticCustomer.to_customer_dict`.
    So the world's statement and the supplier's declaration are the same object
    today, and driving the world's volume from it makes the company's own EAC
    re-estimation partly self-referential in a way it was not before -- W1_11's
    docstring reads the declared EAC as the company's BELIEF for exactly this
    reason. What keeps it from being a tautology is that the overlays sit on top,
    so settled volume is not the declaration: occupancy, EPC band, heating system
    and assets all move a household away from it, and that gap is what
    `_company_eac_estimate` still has to discover. The structural repair -- a
    world-side true EAC and a supplier-side declaration that may differ, with a
    read error between them -- is OWED and named in
    docs/staging/WORKER_PREREGISTRATION_WHAT_SCALING_EACH_HOUSEHOLDS_PROFILE_TO_ITS_OWN_EAC_MUST_SHOW_2026-08-31.md.
    Not doing this at all was the worse option: it left the world's own statement
    about a household reaching nothing at all.
    """
    if customer.get("profile_class", 1) not in _EAC_LEVELLED_PROFILE_CLASSES:
        return None
    declared = customer.get("eac_kwh")
    if declared is None:
        return None
    return float(declared)

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
    eac_kwh: float | None = None,
):
    """Wrap a SHAPE_LOADERS[...] base-shape function with 4c-2's
    weather/occupancy/asset demand adjustment (`build_demand_shape`).

    Falls back to the unadjusted base shape on dates with no weather data
    (e.g. outside sim/weather_data's 2016-01-01..2025-06-07 coverage).

    Phase 25a: cloud_cover_means + latitude_deg enable solar irradiance
    reduction for customers with assets.solar=True (currently C4).
    Phase C: household_register + customer_id enable EPC consumption
    multiplier and time-varying EV ownership.

    `eac_kwh` sets the LEVEL of the base profile to this household's own annual
    consumption (`demand_model.eac_scaled_shape_fn`). Omitted or None, the base
    profile keeps its published Group Average Demand level -- the average
    customer's -- which is correct for a non-domestic profile class and for an
    account the world makes no annual statement about, and wrong for a domestic
    account that carries one. It is applied HERE, ahead of every overlay, so
    that the multiplicative responses (occupancy volume, EPC band) compose with
    it and the additive ones (heating, EV, ASHP) do not.
    """
    from datetime import date as _date

    from sim.weather_engine import half_hourly_solar_irradiance

    if eac_kwh is not None:
        base_shape_fn = eac_scaled_shape_fn(base_shape_fn, float(eac_kwh))

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
                # The car's charging is added ONCE, below, from `ev_annual_kwh()`, after the EPC
                # multiplier. Passing the flag through as well made `build_demand_shape` add its own
                # 8 kWh/night on top (2,143 + 2,922 = 5,065 kWh/yr against Electric Nation's
                # published 1,800-3,500), and put the car under the insulation multiplier.
                # docs/market_research/ev_solar_and_batteries_as_products.md §6.
                assets["ev"] = False
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


def refuse_a_window_past_the_record_without_a_world(effective_end: str) -> None:
    """THE PRICE RECORD ENDS AT REPORT_END, before the weather record does, so this is the first
    thing a run past the record meets. Without a named world it would settle on whatever prices the
    cache happened to hold and print nothing (2026-10-03)."""
    if effective_end <= REPORT_END:
        return
    from simulation.run_scenario import active_forward_world
    if active_forward_world() is None:
        raise ValueError(
            f"this run ends {effective_end}, past the record's last price ({REPORT_END}). A run "
            "past the record must name the world it lives through: run it inside "
            "simulation.run_scenario.forward_world(...).")


def _clamp_term_end(term_start: str, end_date: str = REPORT_END) -> str:
    natural = (date.fromisoformat(term_start) + timedelta(days=CONTRACT_LENGTH_DAYS)).isoformat()
    if natural > end_date:
        return (date.fromisoformat(end_date) + timedelta(days=1)).isoformat()
    return natural


def resolved_tariff_type(record: dict, *, successor: bool = False) -> str | None:
    """The `tariff_type` this record's schedule builder ACTUALLY stamps on every term it emits.

    ONE function, and since 2026-09-16 ONE answer -- the commodity split is gone. It existed
    because the answer DIFFERED by commodity and the difference was a live defect:
    `population_draw.to_customer_dict` renders `"tariff_type": self.tariff_type` unconditionally,
    so a drawn or won record carries the key PRESENT and `None`, and
    `record.get("tariff_type", "fixed")` never reaches its default
    (`docs/design/DRAWN_BOOK_TARIFF_TYPE_FIDELITY_DETERMINATION.md`, settled 2026-08-28). The
    electricity call site was repaired to `or "fixed"` on 2026-08-30 and the gas one was not, so
    for eighteen days the two schedule builders resolved the same record differently.

    That mattered twice over, because `run_value_cycle_ab.product_label_by_account_class` had
    restated the pre-repair spelling as a THIRD copy in order to census the guard's own input. It
    therefore published `resolved_tariff_type: null, the_guard_admits_it: false` for 137
    electricity legs the builder labels `fixed` and the guard admits, in the same artefact whose
    funnel measured only 158 unlabelled refusals -- all of them gas. Two blocks of one file
    disagreeing about one read is what a restated spelling buys.

    So the census IMPORTS this rather than restating it, which is why repairing the gas side was
    one edit in one place that moved the world and the diagnostic together.

    WHY `or "fixed"` IS NOT THE BLANKET-FIXED THE DETERMINATION REFUSED, and this is the whole of
    why repair 2 could not be this line alone. The determination refused labelling the drawn book
    `fixed` FOR ITS WHOLE TENURE, against a published domestic fixed share of roughly a third.
    What this resolves is the OPENING TERM: an account the company won or drew arrived by taking a
    deal, so its first product is a fixed term, on either fuel. Every boundary after that is
    decided by the household's own engagement roll -- `rolls_active_renewal`, in
    `renewals.build_renewal_schedule` for electricity and in `_build_gas_renewal_schedule` below
    for gas, landed in the same commit as this line and for this reason. Read this line on its own
    and it IS the refused blanket; read it with the roll it is paired with and it is the opening
    term of a tenure the world then decides. Deleting that roll and keeping this line would
    re-create the refused shape with nothing here to say so, which is what the pairing note
    at the gas builder's C1b block exists to stop.

    THE REMAINING ASYMMETRY IS THE SUCCESSOR LEG AND IT IS ABOUT THE CALL SITE, NOT THE RECORD.
    """
    if successor:
        # The successor call site passes no `tariff_type` at all, so `build_renewal_schedule`'s
        # own signature default decides -- not the record, whatever the record happens to carry.
        return "fixed"
    # NO COMMODITY BRANCH. Both builders now spell the read the same way, and a branch returning
    # the identical value on both legs would read as a live distinction to the next editor.
    return record.get("tariff_type") or "fixed"


def strike_gas_fixed_term(
    customer: dict, term_start: str, notice_date: str, term_end: str, sim_fwd: float,
    gas_records: list[dict], *, tariff_type: str = "fixed",
) -> dict:
    """One gas term, struck through the company's doors as of `notice_date`: the term dict
    `_build_gas_renewal_schedule` appends at every boundary, lifted out so the run loop can strike
    a gas fix at a moment the schedule never reached (B13 L2, a dual household re-fixing both
    fuels on one contact). The gas twin of `renewals.price_fixed_term`. `term_end` is exclusive.
    """
    aq_kwh = customer["aq_kwh"]
    cust_segment = customer.get("segment", "resi")
    # KNIFE step 24 (§3s): WHICH forward the company prices gas off is its
    # own estimate, made behind the door -- the same door electricity has
    # used since B7. The world still owns the cold-start fallback it hands
    # over, which is the leak §3a records as owed.
    company_fwd = request_company_forward_estimate(
        commodity="gas",
        notice_date=notice_date,
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
    return {
        "acquisition_date": term_start,
        "notice_date": notice_date,
        "term_end": term_end,
        "forward_price_gbp_per_mwh": sim_fwd,
        "company_forward_price_gbp_per_mwh": company_fwd,
        "unit_rate_gbp_per_mwh": _gas_strike.unit_rate_gbp_per_mwh,
        "locked_policy_cost_gbp_per_mwh": _gas_strike.locked_policy_cost_gbp_per_mwh,
        "locked_network_cost_gbp_per_mwh": _gas_strike.locked_network_cost_gbp_per_mwh,
        "tariff_type": tariff_type,
    }


def _build_gas_renewal_schedule(
    customer: dict, gas_records: list[dict], lookback_temps_fn=None,
    report_end: str = REPORT_END, tariff_type: str = "fixed",
) -> list[dict]:
    """Build renewal schedule for a gas customer using NBP forward prices.

    lookback_temps_fn (Phase 4c-3, optional): see
    `simulation.renewals.build_renewal_schedule` — same callable, threaded
    through to `generate_forward_price`'s `lookback_daily_mean_temps_c`.
    Phase 30b: gas CCL + GGL (policy) and gas network cost passed through in unit rate.

    C1b REACHES GAS (2026-09-16) — see the block inside the loop. Until today every term this
    builder emitted was a fixed term, whatever the household did, and `resolved_tariff_type`
    resolving to `"fixed"` without this would BE the blanket-fixed the 2026-08-28 determination
    refused. The two land together and neither is correct alone.
    """
    acq_date = customer["acquisition_date"]
    cust_segment = customer.get("segment", "resi")
    if "customer_id" not in customer:
        # A NAMED REFUSAL, NOT A `.get()`. Until 2026-09-16 this builder never read the id at all,
        # so a caller could hand it a record without one. The C1b roll below needs the HOUSEHOLD
        # (`household_of(customer_id)`) to ask which engagement archetype this family has, and a
        # record with no id has no household -- so the roll cannot be taken. Skipping it instead
        # would put that leg on a fixed term for its whole tenure without saying so, which is
        # exactly the blanket-fixed shape the determination refused, arrived at by a missing key.
        raise ValueError(
            "a gas customer record reaching _build_gas_renewal_schedule carries no "
            "`customer_id`, so `household_of` cannot name the household whose engagement roll "
            "decides each boundary: the record is incomplete, and defaulting it to a fixed "
            "tenure would be the 2026-08-28 determination's refused blanket arrived at quietly"
        )

    # A STANDARD VARIABLE TARIFF IS NOT A TERM, so it is not built by a loop over terms. The same
    # delegation `renewals.build_renewal_schedule` makes at its own head, and for the same reason:
    # every line below assumes a contract that ends -- a 42-day notice date, a rate struck through
    # `request_fixed_unit_rate`, a renewal decision at each boundary -- and an SVT has none of
    # them. Reached by a record that arrives already ON the product; the mid-tenure route is the
    # C1b roll below.
    #
    # AND IT IS NOT ABSORBING, FOR A RESI HOUSEHOLD (2026-09-18) -- the same repair as
    # `renewals.build_renewal_schedule`'s, landed with it and for the reason stated there: a
    # household that ARRIVED on the default tariff could not reach a fixed term for its whole
    # tenure, while one that ROLLED there got its anniversary back. The exit is the C1b roll below,
    # unchanged; all this branch adds is the first stint, because arriving on the cap is not a
    # decision the household revisits on day one. Published refusal:
    # `tools.published_route_split.svt_internal_conversion_floor`.
    svt_origin_terms: list[dict] = []
    if tariff_type == SVT_TARIFF_TYPE:
        _svt_origin_window_end = (
            date.fromisoformat(acq_date) + timedelta(days=CONTRACT_LENGTH_DAYS)
        )
        if cust_segment != "resi" or _svt_origin_window_end > date.fromisoformat(report_end):
            return build_svt_schedule(
                customer["customer_id"], acq_date, report_end, gas_records,
                lookback_temps_fn=lookback_temps_fn, fuel="gas",
            )
        svt_origin_terms = build_svt_schedule(
            customer["customer_id"], acq_date,
            (_svt_origin_window_end - timedelta(days=1)).isoformat(), gas_records,
            lookback_temps_fn=lookback_temps_fn, fuel="gas",
        )
        # Falls through into the loop rather than recursing. The roll below is gated on `schedule`
        # being non-empty, so the prefix is exactly what makes the first anniversary a real
        # boundary this household's own engagement decides -- rather than a fixed term it is handed.
        acq_date = _svt_origin_window_end.isoformat()
        tariff_type = "fixed"

    schedule = list(svt_origin_terms)
    term_start = acq_date

    while term_start <= report_end:
        # ═══════════════════════════════════════════════════════════════════════════════════
        # C1b — THE GAS LEG NOW ROLLS TOO (2026-09-16), repair 2 of the tariff-type determination
        # ═══════════════════════════════════════════════════════════════════════════════════
        #
        # NO NEW RULE, NO NEW CONSTANT AND NO SECOND IMPLEMENTATION. This is the block
        # `renewals.build_renewal_schedule` has carried since 2026-08-30, reached through the same
        # `rolls_active_renewal`, seeded with the same grammar (`{household}_{rows emitted so
        # far}`, and `len(schedule)` is this builder's row count exactly as `len(terms)` is that
        # one's), at the same anchored 35% population active-renewal rate with the same
        # per-household engagement archetype, and forced passive across the same
        # `renewal_engagement.FTC_WITHDRAWAL_WINDOW`. What differs is the fuel handed to
        # `build_svt_schedule`, which is the whole of what repair 2 had to build.
        #
        # WHY IT IS HERE AND NOT SHARED WITH ELECTRICITY'S COPY. The two builders differ in how a
        # TERM is priced -- NBP against Elexon, a cold-start bootstrap this one needs and that one
        # does not -- not in how the DECISION is taken, and the decision is one imported function
        # in both. Hoisting the six lines around it into a third module would put the boundary
        # arithmetic somewhere neither builder's loop can be read against, for no property gained.
        # What IS controlled is that neither builder restates the roll:
        # `tests/simulation/test_the_gas_leg_rolls_onto_the_cap_like_the_electricity_one.py`.
        #
        # DOMESTIC ONLY, because the product is: `simulation/svt_rates.py` is the Ofgem DOMESTIC
        # default-tariff cap and an SME or I&C gas site has no default tariff to roll onto. That
        # is the published scope of the anchor, not a carve-out chosen here.
        #
        # THE HOUSEHOLD KEY IS `household_of`, NOT THE SUPPLY POINT. A gas leg is registered as
        # `<point>g`; the engagement archetype is a fact about the HOUSEHOLD, so a dual-fuel
        # household's two legs must ask about the same one. Seeding on the raw gas id would draw a
        # second, independent archetype for the same family under a different name.
        if schedule and tariff_type == "fixed" and cust_segment == "resi":
            _household = household_of(customer["customer_id"])
            _anniversary = (
                date.fromisoformat(term_start) + timedelta(days=CONTRACT_LENGTH_DAYS)
            )
            if not rolls_active_renewal(
                term_start,
                f"{_household}_{len(schedule)}",
                active_renewal_probability_for_customer(_household),
            ):
                _stint_end = min(
                    _anniversary - timedelta(days=1), date.fromisoformat(report_end)
                )
                try:
                    _stint = build_svt_schedule(
                        customer["customer_id"],
                        term_start,
                        _stint_end.isoformat(),
                        gas_records,
                        lookback_temps_fn=lookback_temps_fn,
                        fuel="gas",
                    )
                except ValueError:
                    # THE SAME RULE THE FIXED PATH BELOW ALREADY FOLLOWS, and it has to be stated
                    # here too or the two products end differently when the NBP series runs out:
                    # a fixed term `break`s and the schedule simply stops, while a cap segment
                    # would raise out of `generate_forward_price` and take the whole run with it.
                    # "The price history ends here" is one fact about the world and it cannot have
                    # two answers depending on which product the household happens to be on.
                    break
                schedule.extend(_stint)
                term_start = _anniversary.isoformat()
                continue

        term_end = _clamp_term_end(term_start, end_date=report_end)
        lookback_temps = lookback_temps_fn(term_start) if lookback_temps_fn else None
        try:
            sim_fwd = generate_forward_price(term_start, gas_records, lookback_daily_mean_temps_c=lookback_temps, fuel="gas")
        except ValueError:
            # A FIRST TERM WITH NO PRICE HISTORY BEHIND IT IS AN ERROR, NOT A BOOTSTRAP (2026-10-06).
            # This used to fall back to `_bootstrap_first_term_forward_price`, which priced the term
            # off the 90 days AFTER its start -- hindsight, and handed on to the company below as its
            # cold-start fallback. It priced C1g's 2016-01-01 term at 12.41 GBP/MWh off Q1 2016,
            # where the Oct-Dec 2015 record a supplier actually held gives 16.38. The gas record now
            # starts 2015-10-01 (`sim.gas_prices_history.RECORD_START`), so no simulated first term
            # reaches here; one that does has outrun the record and must say so.
            if not schedule:
                raise
            break
        # Phase 34a: gas tariffs also priced NOTICE_DAYS before term start.
        gas_notice_date = (date.fromisoformat(term_start) - timedelta(days=NOTICE_DAYS)).isoformat()
        schedule.append(strike_gas_fixed_term(
            customer, term_start, gas_notice_date, term_end, sim_fwd, gas_records,
            tariff_type=tariff_type))
        term_start = term_end  # next term starts where this ends

    return schedule


def _build_churn_basis_risk(customer_events_log: list) -> list[dict]:
    """Phase 11b + 39a: Build churn basis risk records with SVT comparison.

    `rate_vs_svt_pct` is against WHAT THE HOUSEHOLD WAS CHARGED (2026-09-08), because the record
    is about a household's churn and it must be the same quantity as the customer event's
    `price_differential_vs_svt` that `_svt_position` writes. Reading the Ofgem cap here while the
    event read the guarantee would have put the two 50% apart across 2022-10-01..2023-06-30 under
    names that both say `svt` -- the exact shape `run_price_ladder`'s reconciliation caught in
    August, and it is caught here before it lands rather than after.
    """
    from simulation.customer_events import _household_svt_gbp_per_mwh
    from simulation.price_cap_enforcement import household_price_inc_vat

    records = []
    for e in customer_events_log:
        if e.get("company_churn_estimate") is None:
            continue
        unit_rate = e.get("unit_rate_gbp_per_mwh")
        term_start = e["event_date"]
        # The event's own fuel (2026-10-01): a gas event against the electricity SVT read ~80%
        # cheaper than the market, and disagreed with the event's `price_differential_vs_svt`.
        svt_rate = _household_svt_gbp_per_mwh(e["commodity"], term_start)
        rate_vs_svt_pct = None
        if unit_rate is not None and svt_rate is not None and svt_rate > 0:
            # The struck rate is ex-VAT and the SVT is the inc-VAT published price (2026-10-01).
            rate_vs_svt_pct = round(
                (household_price_inc_vat(unit_rate) - svt_rate) / svt_rate * 100.0, 2
            )
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


def _build_company_event_log(customer_events_log: list, fresh_acquisitions: list) -> list:
    """Build the company CRM event log from simulation outputs — Phase 12a.

    Returns a list of dicts (one per event) that the company CRM knows about.
    Churn events come from customer_events_log; acquisition events from fresh_acquisitions
    (market wins). Phase 7e's "home-move-win" acquisitions are retired (2026-10-10).
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
        if d.get("error_pct") is not None:
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


def _grade_demand_estimates_against_the_year_ahead(log: list[dict], settled) -> None:
    """Fill each row's `true_eac_kwh` with the settled kWh of the twelve months FROM its term start,
    and `error_pct` with the forecast's error against it. A row whose year the run did not settle
    in full keeps `None` and says why: a part year is not a year, and annualising it would grade
    the forecast against the season the run happened to stop in."""
    fold = _as_fold(settled)
    for row in log:
        start = date.fromisoformat(row["term_start"])
        try:
            end = start.replace(year=start.year + 1)
        except ValueError:  # a term starting 29 February: its year ahead ends on 1 March
            end = date(start.year + 1, 3, 1)
        days = fold.monthly_totals(row["customer_id"])
        if not days or days[0][0] > start.isoformat() or days[-1][1] < (end - timedelta(days=1)).isoformat():
            row["ungraded_reason"] = "the run did not settle the full year ahead of this term"
            continue
        actual = fold.consumption_kwh_between(row["customer_id"], start.isoformat(), end.isoformat())
        if actual <= 0:
            row["ungraded_reason"] = "no consumption settled in the year ahead"
            continue
        row["true_eac_kwh"] = round(actual)
        row["error_pct"] = round((row["company_eac_kwh"] - actual) / actual * 100.0, 2)


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


def _company_held_register_reads(cid: str, term_start_str: str, settled,
                                 read_feed=None) -> list[tuple]:
    """The register reads the company HOLDS for `cid` on `term_start_str`: what the meter told it.

    WORLD-SIDE, AND THE ONLY THING IT HANDS OVER IS READS. The change-of-supply opening read
    (register 0 the day before the first settled day), then one per complete calendar month whose
    read ARRIVED -- `simulate_read`'s own verdict, keyed exactly as the bill run keys it (the
    month's last settled day), and only where `period end + delay` falls before the term starts.
    A month billed as an estimate contributes no read; its kWh reach the company only inside the
    next actual read's advance, which is what a register does.
    """
    from simulation.meter_reads import SimulatedReadFeed

    feed = read_feed if read_feed is not None else SimulatedReadFeed()
    fold = _as_fold(settled)
    months = fold.monthly_totals(cid)
    if not months:
        return []
    term_start = date.fromisoformat(term_start_str)
    meter_type = feed.meter_type_for(get_customer(cid))
    reads = [(date.fromisoformat(months[0][0]) - timedelta(days=1), 0.0)]
    register = 0.0
    for first_day, last_day, kwh in months:
        register += kwh
        closing = date.fromisoformat(last_day)
        month_end = date(closing.year, closing.month, calendar.monthrange(closing.year, closing.month)[1])
        if month_end >= term_start:
            break
        event = feed.read_for(cid, last_day, meter_type, kwh, 0)
        if event.status == "actual" and closing + timedelta(days=event.delay_days) < term_start:
            reads.append((closing, register))
    return reads


def _company_eac_estimate(
    cid: str, term_start_str: str, settled, commodity: str = "electricity",
    read_feed=None,
) -> float:
    """The annual volume the company believes `cid` uses at `term_start_str`, from what it holds.

    Through `company.interfaces.sim_interface.supplier_annual_volume_kwh`: the register reads
    that arrived (`_company_held_register_reads`) and the registry figure -- the declared EAC, or
    the registered AQ for gas. Never the settled fold's true kWh and never a household multiplier
    (`tests/simulation/test_the_hedge_volume_reads_only_what_the_company_holds.py`).

    UNTIL 2026-10-11 this summed the settled fold's TRUE kWh over the twelve months before the
    term, months billed as estimates included (79% of traditional-meter months in run
    7379375f6), and its first-term fallback took the declared EAC times the household's own
    EV/solar/heat-pump multiplier; gas took the AQ times an EPC-band multiplier. Each overshot by
    8-12% and none crosses the seam (finding:
    docs/staging/SEAT_FINDING_SEVERAL_CONSUMPTION_FORECASTS_A_WALL_LEAK_IN_HEDGE_VOLUME_AND_THE_CAPITAL_TARGET_IS_115_2026-10-11.md).
    """
    return _company_volume_reading(cid, term_start_str, settled, commodity, read_feed)["kwh"]


def _company_volume_reading(cid: str, term_start_str: str, settled,
                            commodity: str = "electricity", read_feed=None) -> dict:
    """`_company_eac_estimate` with its basis: {"kwh", "basis", "from", "to"} from the seam."""
    from company.interfaces.sim_interface import supplier_annual_volume_kwh

    if commodity == "electricity":
        registry = EFFECTIVE_EAC_KWH.get(cid, 0.0)
    else:
        registry = (get_customer(cid) or {}).get("aq_kwh")
    return supplier_annual_volume_kwh(
        commodity, _company_held_register_reads(cid, term_start_str, settled, read_feed),
        registry)


def _price_match_inputs(term: dict, commodity: str, term_start_str: str,
                        company_fwd: float | None) -> dict:
    """THE PRICE MATCH'S INPUTS (2026-10-10): the published default for this fuel, the published
    best-deal gap for the quarter, and the cost floor of the rate the company struck for this term --
    what its own desk floors at. One reading for the save and the renewal cut (B8 Q5). The gap and
    the default are the company's read of the published record, through the save door -- the
    default EX VAT, as the re-fix and the floor are; NOT `_account_state_svt_rate`, which is the
    inc-VAT account-state record's field."""
    # ONE FLOOR (2026-10-14): writer 1 stops a discount at `pre_margin_unit_rate` (forward + capital
    # + the two locked costs) since 2026-10-13; this handed the save forward + the two locked costs,
    # so one supplier held two floors GBP 2.2-4.5/MWh apart on every electricity renewal.
    from company.interfaces.renewal_offer import term_cost_floor

    return {
        "published_default_rate": published_default_rate_ex_vat(commodity, term_start_str),
        "published_best_deal_gap_share": published_best_deal_gap_share(term_start_str),
        "cost_floor": term_cost_floor(
            company_fwd, term_start_str, term.get("locked_policy_cost_gbp_per_mwh"),
            term.get("locked_network_cost_gbp_per_mwh")),
    }


def _household_save_legs(cid: str, commodity: str, term: dict, term_start_str: str,
                         unit_rate: float, company_fwd: float | None, company_eac: float | None,
                         points: list, elec_schedules: dict, gas_schedules: dict,
                         settled) -> list:
    """THE LEGS ONE HOUSEHOLD SAVE IS DECIDED OVER (fuel page §8a, step 1b): the departure leg first,
    then each other point of the household starting a fixed term on the same date. Every input is
    the company's: the offer as struck for the start, the published default ex VAT, the cost floor,
    and the company's own annual volume (never the settled fold's true kWh)."""
    def leg(point, fuel, leg_term, rate, fwd, kwh):
        inputs = _price_match_inputs(leg_term, fuel, term_start_str, fwd)
        return SaveLeg(supply_point_id=point, renewal_unit_rate=rate,
                       published_default_rate=inputs["published_default_rate"],
                       cost_floor=inputs["cost_floor"],
                       annual_mwh=None if kwh is None else kwh / 1000.0)
    legs = [leg(cid, commodity, term, unit_rate, company_fwd, company_eac)]
    for point, fuel in points:
        if point == cid:
            continue
        schedule = (elec_schedules if fuel == "electricity" else gas_schedules).get(point, ())
        other = next((t for t in schedule if t["acquisition_date"] == term_start_str), None)
        if other is None or other.get("tariff_type", "fixed") != "fixed":
            continue
        legs.append(leg(point, fuel, other, other["unit_rate_gbp_per_mwh"],
                        other.get("company_forward_price_gbp_per_mwh",
                                  other["forward_price_gbp_per_mwh"]),
                        _company_volume_reading(point, term_start_str, settled, fuel)["kwh"]))
    return legs


def _write_household_save_carry(carry: dict, rates: dict, decision_point: str,
                                term_start_str: str) -> None:
    """Carry a saved household's rate to each of its OTHER legs, to be billed when that leg's term
    is priced (fuel page §8a). The term heap pops on `(term_start, supply point id)`, so a carry is
    only ever read if its point sorts AFTER the deciding point: one sorting before it was priced
    already on this date and the carry would sit unread, the save silently unbilled on that leg.

    Today that cannot arise: a household is `C1` plus `C1g`, and gas decides only where there is no
    electricity point (`departure_decision_leg`), so the only riding leg is `C1g`, after `C1`. The
    refusal is what keeps it true if a household ever gains a point that sorts first."""
    for point, rate in rates.items():
        if point == decision_point:
            continue
        if point <= decision_point:
            raise ValueError(
                f"household save carry to {point!r} on {term_start_str} cannot be billed: the term "
                f"heap prices {point!r} before the deciding leg {decision_point!r} on a shared start")
        carry[(point, term_start_str)] = rate


def _take_household_save_carry(carry: dict, cid: str, term_start_str: str, unit_rate: float,
                               *, spliced: bool) -> float | None:
    """The rate this leg is billed on its household's save, or None where it is billed the chain's
    rate. The carry is consumed either way. The save was priced on this leg's offer as first struck;
    where the chain has since gone lower, the lower rate stands, because a save never raises a
    price. A spliced default-tariff segment is not the fixed term the save was struck against."""
    carried = carry.pop((cid, term_start_str), None)
    if carried is None or spliced or carried >= unit_rate:
        return None
    return billed_rate_when_saved(unit_rate, carried)


def _renewal_terms(commodity: str, term_start_str: str, unit_rate: float,
                   company_eac_kwh: float | None):
    """C35'S ROOM AT THE NOTICE (2026-10-20, §6.1 "C35 at the renewal notice"): the fix as offered,
    the published default for this fuel on the start (ex VAT, the price match's reading) and the
    company's own annual volume. A rise above the headroom between them sends a stayer to the
    default. None where no default was published (before 2019) or no volume is held: unknown, not
    zero."""
    from company.interfaces.renewal_advice import RenewalTerms

    return RenewalTerms(unit_rate, published_default_rate_ex_vat(commodity, term_start_str),
                        None if not company_eac_kwh else company_eac_kwh / 1000.0)


def _refuse_a_rise_with_no_caller(policy) -> None:
    """The rise is priced only by C34's desk at the notice. Asked for without it, no engine path
    would price one and the run would read as if the rise had been tried."""
    if policy.next_best_action_shares_by_retention_rise and not policy.next_best_action_decides_at_renewal:
        raise ValueError(
            "next_best_action_shares_by_retention_rise is priced at the renewal notice by C34's desk, "
            "and this policy leaves next_best_action_decides_at_renewal off, so no rise would be "
            "priced: switch both on, or neither")


def _refuse_a_billed_rise_with_no_price(policy) -> None:
    """A billed rise is the rise C35 priced at the notice. Asked for without it, nothing is priced to
    bill, and the run would read as if the share had been tried."""
    if policy.renewal_rate_bills_the_shared_rise and not policy.next_best_action_shares_by_retention_rise:
        raise ValueError(
            "renewal_rate_bills_the_shared_rise bills the rise next_best_action_shares_by_retention_rise "
            "prices, and this policy leaves that off, so no rise would be billed: switch both on, or neither")


def _refuse_save_odds_with_no_ending_term(policy) -> None:
    """The save rate is learned per type of term ending, and only the ending-term belief supplies
    the type. Asked for without it, every offer would read "no type" and the guard would run as
    if the save odds had been weighed."""
    if policy.retention_weighs_save_odds and not policy.renewal_belief_by_ending_term:
        raise ValueError(
            "retention_weighs_save_odds learns its save rate per ending-term type, and this policy "
            "leaves renewal_belief_by_ending_term off, so no type would reach it: switch both on")
    if policy.retention_save_rate_learned_against_holdout and not policy.retention_weighs_save_odds:
        raise ValueError(
            "retention_save_rate_learned_against_holdout feeds the save rate the save-odds guard "
            "weighs, and this policy leaves retention_weighs_save_odds off, so nothing would read "
            "it and the held-out households would lose their offer for nothing: switch both on")
    if (policy.retention_offers_on_the_save_rate_lower_bound
            and not policy.retention_save_rate_learned_against_holdout):
        raise ValueError(
            "retention_offers_on_the_save_rate_lower_bound reads the interval of the holdout's "
            "save rate, and this policy leaves retention_save_rate_learned_against_holdout off, so "
            "there is no interval and the guard would never offer: switch both on")


def _riding_leg_term_end(term_end: str, departed_on: str) -> str:
    """A riding leg's exclusive term end once its household has left: the earlier of the two.

    The departure CUTS a term that runs past it; it never lengthens one that ends first. Until
    2026-10-25 the run assigned the departure date outright, and a riding gas leg is posted only
    after its decision leg has rolled every start inside its term -- so a declined fix's default
    segments, spliced after the household left at a later cap boundary, each popped with
    `term_end` stretched to that departure. Every one settled and billed to the leaving day, and
    each month was billed at the mean of the overlapping rates: 6 bills above the cap and 22
    mispriced at 1c30d6c728 (`SEAT_FINDING_A_GAS_SVT_TERM_STARTED_OFF_A_CAP_QUARTER_..._2026-10-25`).
    """
    return departed_on if departed_on < term_end[:10] else term_end


def _account_state_svt_rate(commodity: str, term_start_str: str) -> float | None:
    """The default-tariff rate the account-state record carries for THIS leg's fuel.

    PER FUEL, AND THAT IS THE HONEST SHAPE. The account-state writer read "ELECTRICITY ONLY ...
    there is no gas equivalent in it" until 2026-09-06, which was true of `simulation/svt_rates`
    and false of the world: the Ofgem cap covers both fuels (Domestic Gas and Electricity (Tariff
    Cap) Act 2018), and the regulation commons has carried the gas leg per published window since
    W3_1b. The cost of believing the gap: 449 of `account_state_log`'s 2,098 rows are gas and every
    one carried `None`, so 105 households -- all of them gas-only -- had no value for the field in
    any term, and `tools/r1_inference_ceiling.py` read that as the field's own truth rather than as
    a missing read, on a rung A49 gates R3 and R4 on.

    The original warning stands and is what the dispatch honours: writing the ELECTRICITY cap
    against a gas leg would be a spread between two commodities. Writing the GAS cap against a gas
    leg is the quantity the field was always meant to be.

    A NAMED FUNCTION RATHER THAN THE INLINE CONDITIONAL IT REPLACES, because inside `_main`'s term
    loop the only way to reach this dispatch is a decade-long run. `svt_rates` declines to publish
    a `get_svt_rate(fuel, date)` of its own -- deliberately, so a caller always knows which of two
    different instruments answered it -- so the dispatch belongs to the record that needs it, and
    is named for that record.

    An unknown commodity returns `None` rather than guessing a fuel: there is no default tariff for
    a fuel we cannot name, and a rate written under the wrong one would be unfalsifiable.
    """
    from simulation.svt_rates import (
        get_svt_elec_rate_gbp_per_mwh,
        get_svt_gas_rate_gbp_per_mwh,
    )

    if commodity == "electricity":
        return get_svt_elec_rate_gbp_per_mwh(term_start_str)
    if commodity == "gas":
        return get_svt_gas_rate_gbp_per_mwh(term_start_str)
    return None


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


def _record_renewal_decision(journey, log: list, *, customer_id: str, event_date: str,
                             commodity: str, rolled: bool, event: dict | None) -> None:
    """Every renewal is a decision on the household's journey, rolled or not.

    A household converting off the SVT is not rolled (`departure_rolled_at_renewal`) but it
    stayed, so it records a stay. Recording only rolled renewals left a converter's journey
    wherever `advance()` had put it, read as still comparing years after it had decided.
    `record_decision` draws no random number and nothing in the run loop reads a journey.
    """
    switched = event is not None and event["event_type"] == "churned"
    journey.record_decision(date.fromisoformat(event_date), switched=switched)
    log.append({"customer_id": customer_id, "event_date": event_date,
                "commodity": commodity, "rolled": rolled, "switched": switched})


def _company_provision_by_year_end(triad, effective_end: str, payment_method_of,
                                   crisis_overlay: bool = False,
                                   arrears_overlay: bool = False) -> dict:
    """The company's provision stock at each year end in the run and at its end, read once the run
    is over. Each read is by value date, so a later read of an earlier date sees only cash that had
    arrived by then; reading during the run would force-cross held settlements and change the run.
    A failed read is recorded with its reason and does not kill a finished run.

    The company's month-end write-off sweeps run first (`LivePaymentTriad.write_off_closed_balances`),
    each on the ledger as it stood that day, so every stock carries its write-offs and recoveries
    to date and the IFRS 9 charge can be read off two of them."""
    end = date.fromisoformat(effective_end)
    dates = [date(y, 12, 31) for y in range(int(REPORT_START[:4]), end.year) if date(y, 12, 31) < end]
    try:
        write_offs = triad.write_off_closed_balances(end)
        stocks = {d.isoformat(): triad.provision_stock(d, payment_method_of=payment_method_of,
                                                       crisis_overlay=crisis_overlay,
                                                       arrears_overlay=arrears_overlay)
                  for d in dates + [end]}
    except Exception as exc:  # noqa: BLE001 -- a reporting read must not kill a completed run
        print(f"WARNING [company provision] could not be read: {exc!r}")
        return {"unavailable_because": repr(exc)}
    return {"by_date": stocks, "closing": stocks[end.isoformat()], "write_offs_posted": write_offs}


def _box_admission():
    """`resource_headroom.queued` for one run, declared at the shipped budget's measured peak
    (`budgeted_run_peak_mb`; the `sim_run` class weight when no curve prices it). Over-declares for
    a small run, which is the safe side: it may wait, it never crowds the box."""
    import contextlib

    from background.live_ledger_guard import in_test_process
    if in_test_process():
        return contextlib.nullcontext()
    from background import resource_headroom
    peak, _basis = budgeted_run_peak_mb()
    # A budget below the curve's anchor extrapolates the line to a negative peak, which the queue
    # reads as undeclared and refuses for ever (a budget-0 run, 24 Oct): off the curve, the class
    # weight prices it, as the docstring says.
    return resource_headroom.queued("sim_run", weight_mb=peak if peak and peak > 0 else None,
                                    log=print)


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
    import time as _time

    from simulation import run_cost

    started = _time.monotonic()
    # THE BOX'S ONE BUDGET (director, 2026-10-08). A run started directly -- a lane's script, a tool
    # calling this in-process -- queues for room like a gate or a long job, instead of co-running.
    # Already-admitted work (sim-runner's cycle, a launched long job, an admitted gate) passes
    # straight through, and a test process never queues.
    with _box_admission(), pressure_ledger_scope():
        result = _main(report_end=report_end, policy=policy,
                       gap_ledger_path=gap_ledger_path)
    # Which cast this run faced. Read back from the seam, not from the argument, so it is the seed
    # the book was actually drawn at.
    result["population_seed"] = run_base_seed()
    # One line per run: its cost against the book it settled (simulation/run_cost.py).
    run_cost.record(result, wall_s=_time.monotonic() - started, report_end=report_end)
    return result


def _deliver_psr_registrations(all_records: list[dict], base_seed: int) -> list[dict]:
    """The company's Priority Services Register, built ONLY from disclosures that crossed the seam.

    The world names each domestic supply point's first supplied day; a household whose latent
    PSR-type state discloses sends one notice per point, framed on the wire
    (`interface/contracts/psr_registration_seam.py`), and the company's register decodes it.
    Delivered after the loop because nothing inside it reads the register yet: each notice still
    carries its own date, and when a collections step reads protections it must move in-loop.
    """
    first_day: dict[str, str] = {}
    for rec in all_records:
        cid = rec["customer_id"]
        if is_business(_SEGMENT_OF.get(cid)):
            continue
        day = str(rec["settlement_date"])[:10]
        if cid not in first_day or day < first_day[cid]:
            first_day[cid] = day
    disclosures = registration_notices(
        ((sp, date.fromisoformat(d)) for sp, d in first_day.items()), base_seed)
    register = open_priority_services_register()
    for wire in wire_registrations(disclosures):
        register.receive_registration_wire(wire)
    return [{"account_id": r.account_id, "registration_date": r.registration_date.isoformat(),
             "categories": [c.value for c in r.categories]}
            for r in register.active_records]


def occupier_scheme_credit(credit_left: dict, cid: str, settlement_date: str, owed_gbp: float,
                           segment: str, commodity: str, opened: dict | None = None) -> float:
    """The EBSS credit one unnamed-occupier row nets from its debt, drawn down in `credit_left`.

    The month's credit opens only on a row dated the 1st, because eligibility is the account held
    at 00:00 on the qualifying date (EBSS supplier guidance 5.4); a home void on the 1st is Annex
    C's vacant exception and opens nothing. No row takes more than it owes: a credit larger than
    the occupier's month leaves the account in credit, which the government's payment funds.
    `opened`, when given, records the month's WHOLE credit as the account received it on the 1st:
    the drawdown is only what the debt used, and a window that ends mid-month leaves the rest
    unrecorded though the account held it (the named payer is guarded from a second).
    """
    key = (cid, settlement_date[:7])
    if settlement_date[8:10] == "01" and key not in credit_left:
        credit_left[key] = scheme_credit(segment, commodity, settlement_date[:7])
        if opened is not None:
            opened[key] = credit_left[key]
    credit = min(credit_left.get(key, 0.0), max(0.0, owed_gbp))
    if credit > 0.0:
        credit_left[key] -= credit
    return credit


def _main(report_end: str | None = None, policy: DecisionPolicy | None = None,
          gap_ledger_path=None):
    """Run the full Phase 2b + 4c settlement simulation.

    NAMED STRUCTURAL DEBT: THIS FUNCTION (director, 2026-10-08). About 3,400 lines and roughly a
    hundred local variables, grown one phase at a time; every term of every customer passes
    through one date-ordered heap that carries the treasury, the pricing beliefs and the churn
    rolls. What it blocks:
      * CHECKPOINT AND RESUME. The run's state is these locals, so there is nothing to save.
      * PARALLEL SETTLEMENT. Customers cannot be settled apart; only per-premise inputs
        (fabric traces) can be built in parallel ahead of the loop.
      * SAFE CHANGE. A change here is tested end to end or not at all.
    Not refactored on purpose: the run tiers (seconds / minutes / hours, director 2026-10-08) make
    long runs rare. RAISE IT WITH THE DIRECTOR WHEN IT NEXT COSTS REAL WORK: a change that needs a
    checkpoint, needs customers settled in parallel, or cannot be made safely here.

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
    start_from_the_drawn_book()
    effective_end = effective_report_end(report_end)
    refuse_a_window_past_the_record_without_a_world(effective_end)
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
    if policy.renewal_default_belief not in DEFAULT_BELIEF_SOURCES:
        raise ValueError(
            f"renewal_default_belief={policy.renewal_default_belief!r} is not one of "
            f"{DEFAULT_BELIEF_SOURCES}: a misspelt source would silently price on the segment table")
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
    # A first term whose 90-day lookback starts before its fuel's record is priced off fewer days.
    # Raises unless the record declares why it cannot reach further back; recorded either way.
    _short_first_term_lookbacks = (
        short_first_term_lookbacks(ELEC_CUSTOMERS, SSP_RECORD_START, SSP_SHORT_RECORD_REASON, "electricity")
        + short_first_term_lookbacks(GAS_CUSTOMERS, NBP_RECORD_START, NBP_SHORT_RECORD_REASON, "gas")
    )
    if _short_first_term_lookbacks:
        print(f"{len(_short_first_term_lookbacks)} first term(s) priced off a short lookback "
              f"(see short_first_term_lookbacks).")

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
    # W1_14 step 1, 2026-09-21: THE SHAPE AND FORWARD-PRICE LEGS READ THE PER-CELL STORE TOO.
    # The fabric leg moved to it on 2026-09-17 (`_weather_source` below) and these two did not, so
    # the same premise's physics ran on its cell's sky while its demand SHAPE and its forward
    # temperature came from one of four per-property ERA5 archives resolved by exact `location`
    # match. The store is loaded HERE, once, and handed to every leg -- the load is 8 MB of gzip
    # and two copies of the world could drift from each other, which is the whole thing the
    # per-cell architecture exists to make impossible.
    _weather_source = WeatherWorldSource.load()
    _weather_world = _weather_source.world
    # PAST THE RECORD THERE IS NO WEATHER, and a run that reaches there must say which world it is
    # living through (2026-10-03). Inside `run_scenario.forward_world` the store is extended by
    # analogue years, keyed on the world and the run's base seed -- never on a noise-floor seed, so
    # every seed of one A/B lives through the same weather, as it lives through the same prices.
    # Outside one it REFUSES: an empty sky past the record would settle nothing and say nothing.
    from simulation.run_scenario import active_forward_world
    _forward = active_forward_world()
    if effective_end > _weather_world.record_end():
        if _forward is None:
            raise ValueError(
                f"this run ends {effective_end} and the weather record ends "
                f"{_weather_world.record_end()}. A run past the record must name the world it lives "
                "through: run it inside simulation.run_scenario.forward_world(...).")
        _weather_world = _weather_world.extended_by_analogue_years(
            effective_end, seed=f"{_forward['world_id']}:{run_base_seed()}")
        _weather_source = WeatherWorldSource(_weather_world)
    # W1_14 step 3, 2026-09-21: the GAS/HDD leg reads the store too, and it is the one leg that
    # cannot be handed the world -- `get_hdd(date_str, customer_id)` sits five frames under
    # `run_gas_term` with no world in any signature on the way down. Adopting the store the line
    # above just loaded is what stops it loading a second copy (18 MB gzip, ~60 MB columnar) that
    # could then drift from this one.
    adopt_shared_world(_weather_world)
    # ...and the RECORDS, because that id carries no coordinate: without this every drawn SYN-*
    # or PROS-* gas premise read the monthly normal (91 of 95, 2026-09-30).
    adopt_book(ELEC_CUSTOMERS + GAS_CUSTOMERS + SUCCESSOR_ELEC_CUSTOMERS)
    weather_by_customer = {
        c["customer_id"]: weather_means_for_customer(c, _weather_world)
        for c in ELEC_CUSTOMERS + GAS_CUSTOMERS + SUCCESSOR_ELEC_CUSTOMERS
    }
    # Phase O: cloud cover for all elec customers — any can acquire solar via life events.
    cloud_cover_by_customer = {
        c["customer_id"]: cloud_cover_for_customer(c, _weather_world)
        for c in ELEC_CUSTOMERS + SUCCESSOR_ELEC_CUSTOMERS
    }
    # WHY THE EMPTY SERIES ARE COUNTED HERE RATHER THAN LEFT TO SPEAK FOR THEMSELVES: a premise the
    # store cannot answer settles on the UNADJUSTED base shape, which is a number and looks like
    # every other number. Nothing downstream can distinguish "this cell's weather said the shape
    # needed no adjustment" from "there was no weather". So the reasons are carried out of the
    # resolver and into the run's own record, one entry per premise, naming the cell and the remedy.
    weather_refusal_by_customer = weather_refusals_for_book(
        ELEC_CUSTOMERS + GAS_CUSTOMERS + SUCCESSOR_ELEC_CUSTOMERS, world=_weather_world
    )

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
    # THE WEATHER COMES FROM THE PER-CELL STORE (2026-09-17), not from four per-customer archive
    # CSVs. `_weather_source_customer_id` resolved a premise to one of the four `sim/weather_data`
    # files, so 4 of the book's 146 electricity premises settled on fabric physics and 137 were
    # refused with "no weather archive for this customer's location". `sim.weather_world` holds
    # the world's daily weather keyed by 1 km OSGB cell, and the premise READS it -- which is the
    # director's architecture rather than a wider pull: two households in one cell now get the
    # identical sky, so the difference between their demand is attributable to fabric and people.
    # The store is loaded ONCE for the whole run -- at the 4c inputs above, since 2026-09-21, where
    # the shape and forward-price legs need the same world -- and its accessors handed to the seam;
    # a load per premise, or one load per leg, would be the per-property design in a different coat.
    fabric_series_by_customer, fabric_eligibility_verdicts = fabric_providers_for_book(
        customers=ELEC_CUSTOMERS + SUCCESSOR_ELEC_CUSTOMERS,
        household_at_date=household_demand_register.household_at_date,
        is_half_hourly_metered=is_hh_customer,
        weather_site_for=_weather_source.site_for,
        weather_available=_weather_source.available,
        latitude_for=lambda c: c.get("location", {}).get("lat") or DEFAULT_LATITUDE_DEG,
        start=_fabric_start,
        end=_fabric_end,
        weather_days_for=_weather_source.days,
    )
    # W2_30, the GAS half. The comment above is still right that gas must not be driven
    # off fabric VOLUME while the AQ belief stays frozen -- and the canon does not ask for
    # that. It asks for a seasonal SHAPE, because gas prices do not move within a month.
    # So each domestic gas household's own daily gas trace is projected onto the two-term
    # form `run_gas_term` already settles (`household_demand_shape.seasonal_gas_split`),
    # and only the heating FRACTION changes: at reference HDD the annual total is the AQ
    # whatever the fraction is, so the level -- and therefore the hedge -- is untouched.
    # One reference year is generated per household rather than the whole window: the
    # split is a property of fabric and occupancy, not of which year we settle.
    _gas_fit_end = min(_fabric_end, _fabric_start + timedelta(days=364))

    def _daily_gas_series_for(customer):
        """This household's own daily gas and the HDD it saw, or None if no trace can be
        built for it. Takes the customer RECORD because resolving a premise to a weather
        site reads its `location`. The eligibility predicate is the electricity side's,
        unchanged -- the two paths must not be able to disagree about which premises have
        physics."""
        cid = str(customer["customer_id"])
        _hh = household_demand_register.household_at_date(cid, _fabric_start.isoformat())
        # THE SAME SOURCE OBJECT as the electricity leg above, not a second one built the same
        # way. The docstring's promise is that the two paths cannot disagree about which premises
        # have physics, and two independently-constructed resolvers is exactly how that promise
        # rots -- the electricity leg moving to the cell store while this one kept reading
        # `sim/weather_data/*.csv` would have split the book silently.
        _site = _weather_source.site_for(customer)
        _verdict = fabric_eligibility(
            customer,
            _hh,
            is_half_hourly_metered=False,
            weather_available=_weather_source.available(_site),
            weather_site=_site,
        )
        if not _verdict.is_eligible:
            return None
        _series = build_fabric_series_for_site(
            customer_id=cid,
            household_at_date=lambda d, _c=cid: household_demand_register.household_at_date(_c, d),
            weather_site=_site,
            latitude_deg=DEFAULT_LATITUDE_DEG,
            start=_fabric_start,
            end=_gas_fit_end,
            seed=DEFAULT_TRACE_SEED,
            weather_days_for=_weather_source.days,
        )
        _dates = sorted(_series.gas_kwh)
        return (
            [sum(_series.gas_kwh[d]) for d in _dates],
            [get_hdd(d, cid) for d in _dates],
            [_series.gas_space_heating_kwh[d] for d in _dates],
        )

    gas_heating_fraction_by_customer, gas_shape_refusals = seasonal_gas_splits_for_book(
        customers=[c for c in GAS_CUSTOMERS if c.get("segment") == "resi"],
        daily_gas_series_for=_daily_gas_series_for,
    )
    print(f"Per-household seasonal gas shape (W2_30, MODELLED AND NOT VALIDATED): "
          f"{sorted(gas_heating_fraction_by_customer)}")
    for _r in gas_shape_refusals:
        print(f"  {_r.customer_id}: population 70/30 split -- {_r.reason}")

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
    # ASKED OF THE BOOK, NOT OF EACH PREMISE, and the reason is a measurement rather than a red
    # (2026-09-17, the commit that moved the weather source to the per-cell store). This was a
    # per-premise `raise`, and it was the right shape for a fabric population of FOUR: if any one
    # of four premises settled the legacy volume, the switch was largely inert. Over 91 premises
    # it asserts something the control was never written to assert -- a per-premise fidelity
    # claim rather than an inertness one. Measured over all 91:
    #
    #     every premise moves (>0); median move 44.0%; largest 1396%
    #     4 of 91 move less than the 2% floor: 0.43%, 0.57%, 1.09%, 1.09%
    #
    # C1 is one of the four and its reason is legible: its 1 km cell reads +1.19 C warmer than
    # its old point archive -- the London urban heat island, which is the thing the 1 km pull was
    # for -- so its heating falls, and C1 is GAS-heated, so the fall lands in gas (-8.3% annual)
    # while its electricity moves +0.45%. A gas-heated premise whose electricity is mostly not
    # heating is entitled to settle nearly the legacy electricity volume. That is fidelity, not
    # an inert switch.
    #
    # WHAT WOULD MAKE THIS RED: the switch failing to move a MAJORITY of fabric premises. An
    # inert switch -- the defect the control exists for -- moves none of them and fails on the
    # first count. The floor is 50%, not the 96% measured today, so it is keyed to "the switch
    # reached the book" and not to this book's answer.
    # THE TEXTURE CONTROL IS ASKED OF THE BOOK TOO (2026-10-06), on the same reasoning and floor:
    # it raised on the first untextured premise, and a 4,000-founder book aborted on 1 premise in
    # 1,200. Each failure is NAMED below and in the run output; a majority failing still aborts.
    # See `untextured_premises_within_a_textured_book`.
    _switch_verdicts: list[tuple[str, bool]] = []
    _texture_verdicts: list[tuple[str, bool]] = []
    for _fab_cid, _fab_series in sorted(fabric_series_by_customer.items()):
        _sample_dates = sorted(_fab_series.gross_electricity_kwh)
        _sample_dates = _sample_dates[:14] + _sample_dates[-14:]
        _texture_verdicts.append((_fab_cid, settled_shape_is_physically_textured(
            fabric_shape_fn(
                _fab_series,
                "electricity",
                battery_dispatch=_fabric_battery_dispatch_for(_fab_cid),
            ),
            _sample_dates,
        )))
        # W1_11 L2->L3: the FOURTH control, and the only one that asks whether the
        # switch is INERT. Its three siblings judge the label, the declaration and
        # the texture -- all three stay green on a book whose fabric premises settle
        # exactly the volume the legacy provider would have given them. A textured
        # shape integrating to the same annual kWh is economically invisible, and a
        # demand-generator switch that moves no volume has not reached the book.
        # Built against the same legacy provider the else-branch below constructs,
        # so this is the real counterfactual, not a reconstruction of one.
        _legacy_customer = get_customer(_fab_cid)
        _switch_verdicts.append((_fab_cid, the_switch_moves_the_settled_volume(
            fabric_shape_fn(
                _fab_series,
                "electricity",
                battery_dispatch=_fabric_battery_dispatch_for(_fab_cid),
            ),
            _weather_adjusted_shape_fn(
                SHAPE_LOADERS[registered_profile_class(
                    _legacy_customer, household_demand_register,
                    max(_legacy_customer.get("acquisition_date") or REPORT_START, REPORT_START))],
                weather_by_customer[_fab_cid],
                properties.get(_fab_cid, DEFAULT_PROPERTY),
                cloud_cover_means=cloud_cover_by_customer.get(_fab_cid),
                latitude_deg=_legacy_customer.get("location", {}).get("lat"),
                household_register=household_demand_register,
                customer_id=_fab_cid,
                eac_kwh=_base_profile_eac(_legacy_customer),
            ),
            _sample_dates,
        )))

    _untextured_fabric_premises = untextured_premises_within_a_textured_book(_texture_verdicts)
    for _cid in _untextured_fabric_premises:
        print(f"  FINDING {_cid}: settles on the fabric provider but its sampled settled shape "
              f"recurs like a rescaled base shape (settled_shape_is_physically_textured); "
              f"{len(_untextured_fabric_premises)} of {len(_texture_verdicts)} fabric premises")
    _switch_moved = [cid for cid, moved in _switch_verdicts if moved]
    if not the_switch_reaches_the_book([moved for _, moved in _switch_verdicts]):
        _still = sorted(cid for cid, moved in _switch_verdicts if not moved)
        raise AssertionError(
            f"the fabric switch moves the settled volume for only {len(_switch_moved)} of "
            f"{len(_switch_verdicts)} fabric premise(s): it is labelled and textured but INERT "
            f"across the book. Unmoved: {_still[:12]}"
        )

    # A SETTLED HOME'S REGISTRY EAC IS ITS OWN READS (2026-10-01). The drawn TDCV band was the
    # registry EAC on every account, set before and blind to the dwelling, while a fabric
    # premise's demand is its physics -- so an electrically heated home using 10-20 MWh was
    # quoted, hedged and DD-sized at 1,600-2,500 kWh, and every one of them sat in the year-one
    # >100% renewal-rise tail. A gaining supplier is handed the old supplier's read-derived EAC
    # (BSCP504 s3.2.6.51); see `registry_eac_from_own_reads`. Written into the customer record
    # itself, because the sign-up quote, the roster and EFFECTIVE_EAC_KWH must stay one object.
    # AFTER the switch verdicts above, deliberately: their legacy counterfactual is the
    # band-levelled provider and is not this change's subject. Gas is untouched: its AQ IS the
    # level its settlement uses, so its registry and its demand already agree. Founding
    # treasury (TOTAL_ELEC_EAC) is sized at import and stays on the drawn bands.
    _elec_record_of = {c["customer_id"]: c for c in ELEC_CUSTOMERS + SUCCESSOR_ELEC_CUSTOMERS}
    for _fab_cid, _fab_series in sorted(fabric_series_by_customer.items()):
        _fab_customer = _elec_record_of[_fab_cid]
        if len(_fab_series.dates()) < 365:
            # A WINDOW SHORTER THAN A YEAR HOLDS NO REGISTRY EAC TO DERIVE, and the rule's refusal
            # is right. Only a truncated run reaches this (a full window holds ten years), so the
            # drawn band stands and the log says so, rather than every short run dying at import.
            print(f"  registry EAC {_fab_cid}: the window holds {len(_fab_series.dates())} days "
                  f"of reads, under a year -- drawn {_fab_customer.get('eac_kwh')} kWh kept")
            continue
        _own_eac, _own_basis = registry_eac_from_own_reads(
            fabric_shape_fn(
                _fab_series, "electricity",
                battery_dispatch=_fabric_battery_dispatch_for(_fab_cid),
            ),
            _fab_series.dates(),
            _fab_customer["acquisition_date"],
        )
        print(f"  registry EAC {_fab_cid} [{_fab_series.heating_commodity}-heated]: drawn "
              f"{_fab_customer.get('eac_kwh')} -> own reads {_own_eac:.0f} kWh ({_own_basis[:22]})")
        _fab_customer["eac_kwh"] = round(_own_eac, 1)
        EFFECTIVE_EAC_KWH[_fab_cid] = _fab_customer["eac_kwh"]

    # A HALF-HOURLY ACCOUNT IS HANDED AN EAC TOO (2026-10-19). The HH roster records carry
    # `eac_kwh: None`, so before its first actual read the bill fell back to the TDCV MEDIUM
    # band: C7 billed 3,100 kWh a year against 13,230 used, and was 67% of the open closing
    # undercharge on the 19 Oct book
    # (docs/staging/SEAT_FINDING_A_LEAVER_NEVER_READ_BILLS_A_QUARTER_OF_ITS_TRUE_USE_AND_REFUSED_THE_PUBLISH_2026-10-19.md).
    # The registration is the same rule as a fabric premise's, read through the same shape
    # settlement uses. Demand is untouched: an HH account settles on its file, never on its EAC.
    # EFFECTIVE_EAC_KWH is left on its whole-file mean deliberately, so the hedge is not a
    # second variable in this change (C7 12,802 vs 13,179 kWh; the I&C sites within 0.2%).
    for _hh_cid, _hh_eac, _hh_basis in register_hh_accounts_eac(
            ELEC_CUSTOMERS, hh_consumption_by_customer):
        print(f"  registry EAC {_hh_cid} [HH]: none registered -> own reads {_hh_eac:.0f} kWh "
              f"({_hh_basis[:22]})")

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
            # `resolved_tariff_type` resolves this to `or`, NOT `.get(..., "fixed")`, AND THE
            # DIFFERENCE WAS 137 OF 146 ACCOUNTS. The reasoning is kept here, beside the world it
            # decides; the function exists so the census that reports this read cannot restate it.
            # `population_draw.to_customer_dict` renders `"tariff_type": self.tariff_type`
            # unconditionally, so a drawn or won electricity leg carries the key PRESENT with
            # value None and the default here was never reached
            # (`DRAWN_BOOK_TARIFF_TYPE_FIDELITY_DETERMINATION.md` §(a), measured again at 137/146
            # on 2026-08-30). Those terms then settled with `tariff_type: None`, which the
            # company's `UPLIFTABLE_TARIFF_TYPES` refuses -- the value arm reached 10 of 168
            # accounts for this reason and no other.
            #
            # THE DETERMINATION REFUSED A BLANKET `fixed` AND THIS IS NOT ONE. It refused
            # labelling the whole drawn book fixed for its whole tenure, against a published
            # domestic fixed share of roughly a third. What this resolves is the FIRST term only:
            # an account the company won or drew arrived by taking a deal, so its opening product
            # is a fixed term. Every boundary after that is decided by the household's own
            # engagement roll in `build_renewal_schedule`, which is what puts roughly two thirds
            # of the domestic book on the standard variable product -- the distribution the
            # determination said was owed, generated rather than asserted.
            tariff_type=resolved_tariff_type(c),
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
            report_end=effective_end, tariff_type=resolved_tariff_type(c),
        )

    # ---- Interleave all terms chronologically ----
    # A HEAP KEYED (term_start, cid, seq), not a sorted list, because a declined fix splices
    # default-tariff segments in mid-run (`DECLINE_A_FIX_ABOVE_THE_DEFAULT`). `seq` is the
    # insertion order, so with nothing spliced the pop order is exactly the stable sort on
    # (term_start, cid) this replaced, and the term dicts are never compared.
    _term_seq = itertools.count()
    all_terms: list[tuple] = []
    for cid, schedule in elec_schedules.items():
        for term in schedule:
            all_terms.append((term["acquisition_date"], cid, next(_term_seq), "electricity", term))
    for cid, schedule in gas_schedules.items():
        for term in schedule:
            all_terms.append((term["acquisition_date"], cid, next(_term_seq), "gas", term))
    heapq.heapify(all_terms)
    #: Each supply point's term starts still in the heap, sorted, so a riding leg can ask whether
    #: its household's decision leg has a start inside the term it is about to post. Kept by
    #: `_push_term` and the pop at the head of the loop, the only two ways into and out of the heap.
    _pending_starts: dict[str, list[str]] = {}
    for _entry in all_terms:
        _pending_starts.setdefault(_entry[1], []).append(_entry[0])
    for _starts in _pending_starts.values():
        _starts.sort()

    def _push_term(term_start: str, leg: str, commodity: str, term: dict) -> None:
        heapq.heappush(all_terms, (term_start, leg, next(_term_seq), commodity, term))
        bisect.insort(_pending_starts.setdefault(leg, []), term_start)

    _gas_customer_by_leg = {c["customer_id"]: c for c in GAS_CUSTOMERS}

    def _plan_the_gas_refix(leg: str, contact_date: str, fix_start: date) -> dict:
        """The gas half of a dual household's re-fix (B13 L2, contact page s.7.5b): `{}` for a
        household with no gas leg on supply, `{"refused": why}` to refuse the whole act, else a
        plan whose `_apply` splices the gas fix and returns its row. Nothing moves until `_apply`.

        The gas fix starts on the electricity fix's day, is quoted on the same contact, and runs to
        the gas contract's own next anniversary (each fuel is its own contract, SLC 27.16), which
        may sit days from the electricity one's because the two legs registered days apart."""
        _household = household_of(leg)
        _day = fix_start.isoformat()
        _premise = _move_in_entry.get(leg, {}).get("premise")
        if _premise is not None and any(household_of(g) == household_of(_premise)
                                        for g in gas_schedules):
            # An incoming occupant's gas leg is admitted when the vacated gas leg pops, which can
            # be after this contact, and has no drawn record to quote on (OCC-8bd9f5bbfa68).
            return {"refused": "an incoming occupant at a home with gas: its gas leg has no drawn "
                               "record to quote a fix on"}
        # The drawn gas legs and an incoming occupant's, which is pushed straight into the heap.
        _gas = sorted(g for g in (
            {g for g in gas_schedules if household_of(g) == _household}
            | {k for k, v in _move_in_entry.items()
               if v["commodity"] == "gas" and v["household"] == _household})
            if _moved_out_on_by_leg.get(g, _day) >= _day
            and (g in _last_tariff_type or any(e[1] == g for e in all_terms)))
        if not _gas:
            return {}
        if len(_gas) > 1 or _gas[0] not in _gas_customer_by_leg:
            return {"refused": f"the household's gas legs {_gas} are not one drawn leg with a "
                               "registered AQ (an incoming occupant's leg has no drawn record)"}
        g = _gas[0]
        # Only default segments are withdrawn. A gas leg already on a fix, or with an offer on the
        # fix's day, is refused below: its window holds a term that is not a default segment.
        _before = [e for e in all_terms if e[1] == g and e[0] < _day]
        _offer = [e[0] for e in _before if e[4].get("tariff_type") != SVT_TARIFF_TYPE]
        if _offer:
            # A fix still in the heap before the day is an offer the gas leg has not answered: a
            # riding leg pops after its decision leg, and declines at its pop (SYN-2016-023g took
            # its 2017-01-17 offer as a fix here, then declined it onto the default).
            return {"refused": f"the gas leg {g} has not yet answered its renewal offer of "
                               f"{_offer[0]}, so the household cannot fix both fuels in one act"}
        _first = _gas_customer_by_leg[g]["acquisition_date"]
        _years = (fix_start - date.fromisoformat(_first)).days // CONTRACT_LENGTH_DAYS + 1
        _gas_end = min(date.fromisoformat(_first) + timedelta(days=_years * CONTRACT_LENGTH_DAYS),
                       date.fromisoformat(effective_end) + timedelta(days=1))
        _out = [e for e in all_terms
                if e[1] == g and fix_start.isoformat() <= e[0] < _gas_end.isoformat()]
        _not_default = [(e[0], e[4].get("tariff_type")) for e in sorted(_out)
                        if e[4].get("tariff_type") != SVT_TARIFF_TYPE
                        or e[4].get(_HELD_FOR_THE_DECISION_LEG)
                        or (e[4].get("term_end") or "")[:10] > _gas_end.isoformat()]
        _starts = sorted(e[0] for e in _out)
        _after = [s for s in _pending_starts[g] if s >= _gas_end.isoformat()]
        if (not _starts or _starts[0] != fix_start.isoformat() or _not_default
                or (_after and _after[0] != _gas_end.isoformat())):
            return {"refused": (
                f"the gas leg {g} is not on default segments from {fix_start} to its anniversary "
                f"{_gas_end} (starts {_starts[:3]}, not default {_not_default[:3]}, next "
                f"{_after[:1]}), so the household cannot fix both fuels in one act")}
        try:
            _temps = _lookback_temps_fn(g)
            _sim_fwd = generate_forward_price(
                fix_start.isoformat(), gas_records,
                lookback_daily_mean_temps_c=_temps(fix_start.isoformat()) if _temps else None,
                fuel="gas")
            _gfix = strike_gas_fixed_term(
                _gas_customer_by_leg[g], fix_start.isoformat(), contact_date,
                _gas_end.isoformat(), _sim_fwd, gas_records)
        except ValueError as _no_history:
            return {"refused": f"no gas fix could be struck: {_no_history}"}
        _gas_vs_default = (position_vs_default(_gfix["unit_rate_gbp_per_mwh"], contact_date,
                                               commodity="gas")
                           if DECLINE_A_FIX_ABOVE_THE_DEFAULT else None)
        if _gas_vs_default is not None and _gas_vs_default > 0:
            # Per fuel and both-or-neither: a household weighing the pair as one bill would take
            # some of these, so refusing them understates its side (F11).
            return {"refused": f"the gas fix sits {_gas_vs_default:+.1%} against its default, so "
                               "the household fixes neither fuel"}

        def _apply() -> dict:
            _gone = {id(e) for e in _out}
            all_terms[:] = [e for e in all_terms if id(e) not in _gone]
            heapq.heapify(all_terms)
            for _start in _starts:
                _pending_starts[g].remove(_start)
            _gfix[_WOKEN_REFIX] = True
            _push_term(fix_start.isoformat(), g, "gas", _gfix)
            term_indices[g] += len(_out) - 1
            return {"customer_id": g, "fix_end": _gas_end.isoformat(),
                    "unit_rate_gbp_per_mwh": _gfix["unit_rate_gbp_per_mwh"],
                    "default_segments_withdrawn": len(_out),
                    "withdrawn_default_rates": [
                        [e[0], e[4].get("term_end"), e[4].get(
                            "household_charged_unit_rate_gbp_per_mwh",
                            e[4].get("unit_rate_gbp_per_mwh"))] for e in sorted(_out)],
                    "aq_kwh": _gas_customer_by_leg[g]["aq_kwh"]}
        return {"_apply": _apply}

    def _splice_a_refix(leg: str, contact_date: str, segment_end: str, stint_start: str,
                        commodity: str) -> dict:
        """C30, research doc §7.5a: a woken SVT stayer re-fixes from its next default segment.

        The fix is quoted through `price_fixed_term` (the builders' renewal door) as of the contact,
        and runs to the household's next anniversary, which is already in the heap and stays as
        built. Starting at the next cap segment rather than the contact, and stopping at the
        anniversary rather than running twelve months, both understate the household's side (F11).
        The default segments in between are withdrawn. Returns what happened, or why not.
        """
        if commodity != "electricity":
            # GAP: a gas fix is priced inside `_build_gas_renewal_schedule` (NBP, its own
            # bootstrap refusal) and is not yet callable from here; a gas-only household stays.
            return {"refused": "a gas fix is struck only inside the gas builder"}
        _stint = date.fromisoformat(stint_start)
        _seg_end = date.fromisoformat(segment_end[:10])
        # Every SVT stint the run builds -- arrival, a passive roll, a declined fix -- is one
        # CONTRACT_LENGTH_DAYS window from an anniversary, and consecutive stints chain, so the
        # household's next boundary is the first whole window from the stint's start.
        _windows = max(1, -(-(_seg_end - _stint).days // CONTRACT_LENGTH_DAYS))
        _boundary = _stint + timedelta(days=_windows * CONTRACT_LENGTH_DAYS)
        _fix_start, _fix_end_excl = _seg_end, min(
            _boundary, date.fromisoformat(effective_end) + timedelta(days=1))
        _withdrawn = [e for e in all_terms
                      if e[1] == leg and _fix_start.isoformat() <= e[0] < _fix_end_excl.isoformat()]
        if not _withdrawn:
            return {"refused": (
                "the run ends with this segment" if _fix_start >= _fix_end_excl else
                "the contact fell in the stint's last segment, so its anniversary is the "
                "household's next look")}
        _starts = sorted(e[0] for e in _withdrawn)
        _foreign = [(e[0], e[4].get("tariff_type")) for e in sorted(_withdrawn)
                    if e[4].get("tariff_type") != SVT_TARIFF_TYPE
                    or e[4].get(_HELD_FOR_THE_DECISION_LEG)]
        if _starts[0] != _fix_start.isoformat():
            # The segment was cut short of the cap boundary: a move-out inside it.
            return {"refused": f"this segment ends at {_fix_start}, before the next default "
                               f"segment at {_starts[0]}: the household moves out"}
        if _foreign:
            return {"refused": (
                f"the window {_fix_start} to {_fix_end_excl} holds terms that are not this "
                f"stint's default segments: {_foreign}")}
        _past = [(e[0], e[4].get("term_end")) for e in _withdrawn
                 if (e[4].get("term_end") or "")[:10] > _fix_end_excl.isoformat()]
        if _past:
            # An incoming occupant's default supply is one schedule with no anniversary, so its
            # segments do not stop at one: withdrawing them whole left the leg unsupplied from the
            # fix's end to the segment's (OCC-6387bf64272a, 2017-04-21 to 07-01, B13 L2 probe).
            return {"refused": (
                f"the default segment {_past[0]} runs past the stint's anniversary "
                f"{_fix_end_excl}: the stint is not anniversary-bound, so the fix would leave the "
                "leg unsupplied")}
        if not _is_domestic_leg(leg):
            return {"refused": "the default tariff and its re-fix are domestic"}
        if leg not in EFFECTIVE_EAC_KWH:
            return {"refused": "no registered EAC to quote the fix on"}
        try:
            _fix = price_fixed_term(
                leg, _fix_start, date.fromisoformat(contact_date), _fix_end_excl,
                elec_records, EFFECTIVE_EAC_KWH[leg],
                policy_cost_days=(_fix_end_excl - _fix_start).days,
                lookback_temps_fn=_lookback_temps_fn(leg), segment="resi",
            )
        except ValueError as _no_history:
            return {"refused": f"no fix could be struck: {_no_history}"}
        # The decline-and-stay rule, here rather than at the pop: the pop skips a `_WOKEN_REFIX`
        # term, so without this a woken stayer took a fix dearer than its default (6 in 2021 on
        # the first full arm). Against the default paid on the contact day: the next cap is
        # usually unpublished when a first-segment letter lands.
        _vs_default = (position_vs_default(_fix["unit_rate_gbp_per_mwh"], contact_date,
                                           commodity=commodity)
                       if DECLINE_A_FIX_ABOVE_THE_DEFAULT else None)
        if _vs_default is not None and _vs_default > 0:
            return {"refused": f"the fix sits {_vs_default:+.1%} against the default it would "
                               "replace, so the household stays on the default"}
        # B13 L2: A DUAL HOUSEHOLD'S FIX COVERS ITS GAS TOO, in the same act or not at all
        # (how_households_respond_to_supplier_contact.md s.7.5b). Planned before anything moves.
        _gas_plan = _plan_the_gas_refix(leg, contact_date, _fix_start)
        if "refused" in _gas_plan:
            return _gas_plan
        _gone = {id(e) for e in _withdrawn}
        all_terms[:] = [e for e in all_terms if id(e) not in _gone]
        heapq.heapify(all_terms)
        for _start in _starts:
            _pending_starts[leg].remove(_start)
        _fix[_WOKEN_REFIX] = True
        _push_term(_fix_start.isoformat(), leg, commodity, _fix)
        # The builders counted each withdrawn segment; the fix advances one when it pops, so the
        # rest are advanced here and the engagement seed agrees with theirs at the anniversary.
        term_indices[leg] += len(_withdrawn) - 1
        _gas_leg = _gas_plan.pop("_apply", lambda: None)()
        return {
            **({"gas_leg": _gas_leg} if _gas_leg else {}),
            "fix_start": _fix_start.isoformat(),
            "fix_end": _fix_end_excl.isoformat(),
            "unit_rate_gbp_per_mwh": _fix["unit_rate_gbp_per_mwh"],
            "default_segments_withdrawn": len(_withdrawn),
            # What the household would have paid instead, ex VAT as the fix is, so its side of
            # the re-fix can be graded off this row: the household's share, net of any EPG.
            "withdrawn_default_rates": [
                [e[0], e[4].get("term_end"), e[4].get(
                    "household_charged_unit_rate_gbp_per_mwh", e[4].get("unit_rate_gbp_per_mwh"))]
                for e in sorted(_withdrawn)],
            "eac_kwh": EFFECTIVE_EAC_KWH[leg],
        }

    # The fuels each household is supplied, so the budget (`household_budget.BudgetPaymentBook`)
    # can split one household's money across its legs. A move-in adds its leg below.
    _fuels_of_household: dict = {}
    for _leg_cid in elec_schedules:
        _fuels_of_household.setdefault(household_of(_leg_cid), set()).add("electricity")
    for _leg_cid in gas_schedules:
        _fuels_of_household.setdefault(household_of(_leg_cid), set()).add("gas")

    # WHICH BILLING ACCOUNTS HOLD AN ELECTRICITY SUPPLY POINT IN THIS RUN, which is the only
    # input `departure_decision_leg` needs to say which leg carries an account's departure roll.
    #
    # BUILT FROM THE SCHEDULES AND NOT FROM `ELEC_CUSTOMERS`, and the difference is the one that
    # matters: this set must mean "has an electricity leg that actually runs terms here". A leg
    # on the roster with an empty schedule would claim the decision and then never roll, which
    # would leave its household with no route out — reintroducing exactly the defect below on a
    # smaller population, and silently, because nothing downstream distinguishes "rolled and
    # stayed" from "never rolled".
    _accounts_with_an_electricity_leg = {
        household_of(cid) for cid, schedule in elec_schedules.items() if schedule
    }
    # EVERY SUPPLY POINT ON EACH ACCOUNT, so a decision about the whole account reads the whole
    # account's payment record. The departure roll is on one leg; reading only that leg's score
    # left a dual-fuel account's other leg invisible to the company's belief (2026-10-07: a
    # CRITICAL gas leg behind a FAIR electricity one). Sorted so the pooled record is
    # order-independent of dict iteration.
    _supply_points_of_account: dict[str, tuple[str, ...]] = {}
    for _sp in sorted(set(elec_schedules) | set(gas_schedules)):
        _supply_points_of_account[household_of(_sp)] = (
            *_supply_points_of_account.get(household_of(_sp), ()), _sp)

    # ---- Simulation state ----
    treasury = STARTING_TREASURY_GBP
    monitor = RiskCommitteeMonitor(treasury)

    all_customers_ids = (
        [c["customer_id"] for c in ELEC_CUSTOMERS]
        + [c["customer_id"] for c in GAS_CUSTOMERS]
        + [c["customer_id"] for c in SUCCESSOR_ELEC_CUSTOMERS]
    )
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
    # One row per decision the journey records at a renewal (SIM-side ground truth).
    renewal_decisions_log: list[dict] = []
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
    # ONE BILL PER LEG PER MONTH, POSTED WHEN THE MONTH CLOSES (2026-10-03). The bill is the month's
    # settled revenue summed, not the first settlement record's (a half-hour, median GBP 0.023 over
    # a decade). Terms run in date order across customers and a renewal splits a month between two
    # terms of one leg, so a month is held open per leg and posted when that leg's next month starts
    # or the run ends -- never twice, since the ledger keys a bill on (customer, month).
    _payment_month_open: dict[str, dict] = {}  # cid -> the month being accumulated
    # (cid, month) -> the EBSS credit an unnamed occupier's deemed account still has to net.
    _occupier_credit_left: dict[tuple[str, str], float] = {}

    def _book_complaint_for(cid, billing_account, term_start_str, _outcome, _about_bill_shock):
        # KNIFE step 21 (§3p): the world reports that the customer got in
        # touch and whether the company closed it on time. Filing it under
        # BILLING, wording it, and both trust deltas are the desk's.
        # One booking for every complaint the world raises: the rate-shock roll at a renewal and
        # DD4b's complaint about the DD review told in the loop (`_post_month_bill`) both come here.
        _cx_desk.observe_contact(CustomerContact(
            customer_id=cid,
            account_id=billing_account,
            contacted_on=date.fromisoformat(term_start_str),
            about_bill_shock=_about_bill_shock,
            resolved_on_time=(
                _outcome.reputation_event_type
                == ReputationEventType.COMPLAINT_RESOLVED_ON_TIME
            ),
        ))
        if _outcome.reputation_event_type == ReputationEventType.COMPLAINT_RESOLVED_ON_TIME:
            _churn_journey_register.record_friction(
                billing_account, FrictionEventType.COMPLAINT_RESOLVED_WELL,
                date.fromisoformat(term_start_str),
            )
        else:
            _churn_journey_register.record_friction(
                billing_account, FrictionEventType.COMPLAINT_UNRESOLVED,
                date.fromisoformat(term_start_str),
                amplifier=(
                    1.5 if _outcome.reputation_event_type
                    == ReputationEventType.COMPLAINT_UPHELD_AT_OMBUDSMAN else 1.0
                ),
            )
        _churn_journey_register.gri.record(
            _outcome.reputation_event_type, date.fromisoformat(term_start_str),
            description=f"{billing_account} complaint raised {term_start_str}",
        )
        reputation_events_log.append({
            "customer_id": billing_account,
            "date": term_start_str,
            "event_type": _outcome.reputation_event_type.value,
            "days_to_resolve": _outcome.days_to_resolve,
        })

    def _bill_due_on(month: str) -> date:
        # A month's bill falls due on its 28th; the gone-household close reads the same day.
        return date.fromisoformat(month + '-28')

    def _post_month_bill(cid: str, held: dict) -> None:
        # PB8 (`simulation/payment_method_dynamics.py`): a household paying by DD may cancel its
        # mandate this month for its own reasons, before the month's collection is presented.
        # Nothing is drawn while the share is zero.
        if not _method_strengths.off:
            _own_household = household_of(cid)
            _own = _method_dynamics.own_reasons_cancellation(
                household=_own_household, month=held["month"],
                stress=held["income_stress_value"],
                pays_by_direct_debit=_method_dynamics.pays_by_direct_debit(cid, held["fuel"]),
                already_cancelled=_dd_shock_book.has_cancelled(_own_household),
                strengths=_method_strengths,
            )
            if _own is not None:
                _dd_shock_book.record(_own)
        # DD4b, AT THE REVIEW THE HOUSEHOLD ACTUALLY MEETS (`simulation/dd_review_in_loop.py`): the
        # supplier's annual review is asked as this month's bill posts, and a DD household told a
        # material rise answers it before this month's collection is presented. One answer per
        # household per review month: its two legs are reviewed together and draw the same uniforms.
        if not _dd_shock_strengths.off:
            _told = _dd_in_loop_review.post(cid, held["month"])
            _dd_household = household_of(cid)
            if (_told is not None
                    and _method_dynamics.pays_by_direct_debit(cid, held["fuel"])
                    and not any(r.get("review_month") == held["month"]
                                for r in _dd_shock_book.responses_of(_dd_household))):
                _dd_response = respond_to_told_amount(
                    household=_dd_household, month=held["month"],
                    amount_in_force_gbp=_told["current_dd_gbp"],
                    new_amount_gbp=_told["recommended_monthly_gbp"],
                    stress=held["income_stress_value"], stays=True,
                    already_cancelled=_dd_shock_book.has_cancelled(_dd_household),
                    strengths=_dd_shock_strengths,
                )
                if _dd_response is not None:
                    _dd_shock_book.record(_dd_response)
                    if _dd_response["complained"]:
                        _book_complaint_for(cid, _dd_household, _told["review_date"],
                                            dispatch_dd_shock_complaint(_dd_household,
                                                                        _told["review_date"]),
                                            True)
        _pm_rec = _payment_triad.record_period(
            customer_id=cid,
            due_date=_bill_due_on(held["month"]),
            # Net of the scheme credit, from the same door the arrears engine asks, so the pounds
            # the household's budget weighs are the pounds that can fail. A month left in credit
            # owes nothing.
            # A month whose credit the unnamed occupier's account took gives no second one.
            amount_gbp=max(0.0, held["amount_gbp"] if (cid, held["month"]) in _occupier_credit_left
                           else owed_after_scheme_credit(
                               held["amount_gbp"], held["segment"], held["fuel"], held["month"])),
            income_stress_value=held["income_stress_value"],
            segment=held["segment"],
            fuel=held["fuel"],
            dd_stopped_by=lambda _cid, _due: _dd_stop_board.notice_as_of(
                _cid, _due.isoformat()) is not None,
            dd_shock_effect=(None if not _mandate_book_live
                             else _dd_shock_book.effect(household_of(cid), held["month"])),
            moved_out_on=_moved_out_on_by_leg.get(cid),
            household_legs=len(_fuels_of_household.get(household_of(cid), ())) or 1,
        )
        _cx_desk.observe_payment(PaymentOutcome(
            customer_id=cid,
            due_date=_pm_rec["due_date"],
            result=_pm_rec["result"],
            days_late=_pm_rec["days_late"],
            amount_gbp=_pm_rec["amount_gbp"],
        ))
    # L3 payment coupled triad (W2_11 source / W4_4 seam / D5 consumer / gap),
    # LIVE per-run. W2_11's generate_payment_event is now the CANONICAL payment
    # truth: the analytics dict below is DERIVED from that single event (one
    # coherent reality per customer/period), while emit_wall_responses ->
    # consumer.observe forms the company's observable-only belief and the gap is
    # measured + written at run end (background.live_payment_triad).
    _payment_triad = LivePaymentTriad()
    # A dual household's journey waits for its slower leg: whole terms post in turn.
    _payment_triad.legs_still_posting = lambda household: {
        leg for leg in (household, household + GAS_LEG_ID_SUFFIX)
        if _pending_starts.get(leg) or leg in _payment_month_open}
    # SLC 14: the company's own objection register. It decides a debt objection from its OWN
    # ledger at the switch request; the world only completes or cancels the switch (EP12).
    _transfer_objection_register = open_transfer_objection_register()
    # The company's own method register, as the renewal price reads it, for every resi account the
    # book's default rate learns over (`DecisionPolicy.renewal_default_belief`), ON A DATE: a DD the
    # supplier stopped is pay-on-receipt from its notice on, and the learner reads each provision
    # on the row for the method held that day. Asked once per account and date; read only when the
    # policy prices on the book.
    # ASKED ON THE ACCOUNT'S OWN FUEL (2026-10-04): this used to ask "electricity" of every account,
    # so a gas leg, or a gas-only household, was answered off the electricity branch, and its own
    # gas stop never reached the row its provisions were read on. The fuel is read off the live
    # roster, acquisitions included, and an account the roster does not hold is refused, not
    # guessed: the method register has no fuel to ask on for it.
    _book_methods: dict = {}

    def _book_method_of(account_id: str, on: date):
        cid = account_id[len("ACC-"):] if account_id.startswith("ACC-") else account_id
        if _SEGMENT_OF.get(cid, "resi") != "resi":
            return None
        if (cid, on) not in _book_methods:
            from company.interfaces.sim_interface import LiveSimInterface
            # The incoming occupants a home move supplies (B7 slice 3) are on the book too: with
            # moves on, the 2026-10-08 first run refused here on ACC-OCC-* before this line read them.
            fuel = next((c["commodity"] for c in _known_customers() + ACQUIRED_CUSTOMERS
                         if c["customer_id"] == cid), None)
            if fuel is None:
                raise ValueError(
                    f"_book_method_of({account_id!r}): no account on the roster, so there is no "
                    "fuel to ask its payment method on")
            _book_methods[(cid, on)] = LiveSimInterface().get_payment_method(
                cid, fuel, as_of=on.isoformat())
        return _book_methods[(cid, on)]
    _NG_BILL_SHOCK_THRESHOLD = 0.20  # matches simulation.bill_shock_tracker.BILL_SHOCK_THRESHOLD
    CRISIS_HANGOVER_LOSS_THRESHOLD = 0.20  # trigger: net loss > 20% of term revenue

    # Phase 17a + 19a: the supplier's realised margin per ended term, per fuel, which its portfolio
    # premium reads. The company's own bookkeeping (2026-10-12): the run reports each ended term and
    # each save, and the book decides what it admits and when (`PortfolioMarginBook`).
    _portfolio_margins = open_portfolio_margin_book()
    dynamic_pricing_log: list[dict] = []
    # THE COMPANY'S RECORD OF ITS OWN BOOK, ACCOUNT-SHAPED (2026-09-06). Every other customer log
    # in this run is EVENT-shaped: it exists because a renewal fired, an offer was made, a journey
    # advanced. So the observables a supplier holds CONTINUOUSLY -- what it charges, what the
    # default tariff costs, the gap between them, and its own estimate of the account's annual
    # consumption -- were only ever written down for the minority of households that renewed on a
    # fixed electricity term. On run_output_f53c90b85 that was 69 households of 177, and it is why
    # `tools/r1_inference_ceiling.py` could not put a point estimate on the pair rung: it needed
    # ~72 households carrying both fields of a pair and had ~62. That is a bookkeeping accident,
    # not a fact about what a supplier can see -- withholding from the company an EAC IT COMPUTED
    # and a rate IT SET makes us look weaker at inference than we are.
    #
    # ONE ROW PER (household leg, term) FOR EVERY TERM THE BOOK ACTUALLY SERVES, including gas
    # legs, first terms, and indexed products that have no renewal decision at all. Written before
    # the term is settled, so `company_eac_kwh` carries the same point-in-time blindfold the
    # renewal estimate does.
    #
    # WHAT IS DELIBERATELY NOT HERE, because it is a decision artefact and not account state:
    # `discount_pct` and `expected_term_margin_gbp` exist only where an offer was priced;
    # `company_churn_estimate`, `resentment_score` and `perceived_bill_saving_gbp` exist only
    # where a renewal window opened. Manufacturing any of them for a term that had no decision
    # would be inventing the coverage rather than recording it. `OBSERVABLE_FIELD_SCOPE` in
    # `tools/r1_inference_ceiling.py` states that per field so the reader sees the gap named.
    account_state_log: list[dict] = []

    # THE SETTLED BOOK IS COLUMNAR (`simulation/record_table.py`): a term builds plain dicts, and
    # they become typed columns at the one `extend` below. Its rows are Mappings, not dicts -- a
    # reader gating on `isinstance(r, dict)` would skip every one, so such gates read Mapping.
    all_records: RecordTable = RecordTable()
    # PB8 L2: WHETHER THE SUPPLIER HAD STOPPED A HOUSEHOLD'S DD BY A DATE, for the payment-method seam
    # the renewal price and the engagement antecedent read. Fed beside `all_records`, so it bills
    # only what the run has settled. Stress is the household's drawn trajectory, the same one
    # `_build_behavioral_trajectories` hands the money side, fixed before the first term.
    from simulation.dd_collection_book import StopNoticeBoard, install_stop_notice_board
    # DD4b: the household's own answer to a DD shock, recorded at each review the run reaches.
    # Read once per run from the module, so a harness that measures a setting sets it before main().
    _dd_shock_strengths = _dd_shock_response.STRENGTHS
    _dd_shock_book = DDShockResponseBook()
    _dd_in_loop_review = InLoopDDReview(get_customer, run_end=effective_end)
    # PB8, the household's own acts (`simulation/payment_method_dynamics.py`): a mandate cancelled
    # for its own reasons is a row on the same book, so the triad, the rails and the arrears engine
    # read it as they read a shock's. Read once per run, as above.
    _method_strengths = _method_dynamics.STRENGTHS
    _mandate_book_live = not (_dd_shock_strengths.off and _method_strengths.off)
    _dd_stop_board = StopNoticeBoard(
        lambda _cid: household_demand_register.income_stress_trajectory(_cid, list(range(2016, 2026)))
        if household_demand_register is not None else [],
        dd_shock_responses_of=lambda _sp: _dd_shock_book.responses_of(household_of(_sp)),
        payment_truth_of=(_payment_triad.payment_truth_so_far
                          if _world_payment_truth.UNIFIED else None))
    install_stop_notice_board(_dd_stop_board)
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
    _rate_shock_counts: dict[str, int] = {}
    # Phase QV: per-year shock dates (SIM_TAB_OVERHAUL.md event frequency panel) --
    # _rate_shock_counts above is an all-time rolling scalar; this retains
    # the actual term_start_str of each shock so the site can bucket per year.
    _bill_shock_dates: dict[str, list] = {}
    committee_wake_ups: list[dict] = []
    customer_events_log: list[dict] = []
    # C29: each fuel leg's payment method as the supplier last read it at a renewal, which is the
    # book `engagement_at` fits on. Filled only when the policy weighs engagement.
    _engagement_channels: dict[str, str] = {}
    # THE RIVAL'S VIEW OF THIS COMPANY (2026-08-28, atom B10, director's C2). Run-scoped and
    # explicit: a module global would leak between runs and make the reference depend on
    # execution order, which is the non-determinism the seeded-run discipline forbids. It is
    # fed from the term loop AFTER each offer is struck and read a quarter later, so the world's
    # opponent moves on its own cycle rather than inside the term the company is pricing.
    _competitor_position_ledger = CompanyPositionLedger()
    # W2_39: what reached each household from the company, written only through the seam below and
    # read only by the SVT roll. Run-scoped for the same reason as the ledger above.
    from simulation.contact_response import ContactsReceived
    _contacts_received = ContactsReceived()
    # A contact about a missed payment reaches the same store (`contact_response`, early contact).
    _payment_triad.contacts_received = _contacts_received
    _svt_contact_instrument = policy.svt_contact_instrument
    # C34: the company's own coin keeps a share of that stock out of the contact, so what the
    # contact did can be read against who was left alone. `None` holds nobody out.
    _svt_contact_holdout_share = policy.svt_contact_holdout_share
    if _svt_contact_instrument is not None:
        from company.interfaces.contact_programme import contact_arm, sends_at_segment
        from company.interfaces.sim_interface import LiveSimInterface
        _contact_seam = LiveSimInterface(contacts_received=_contacts_received)
    churned_billing_accounts: set[str] = set()
    #: The date each household's departure took effect: no leg supplies on or after it.
    _departed_on: dict[str, str] = {}
    _leg_departures: list[dict] = []

    def _supplies_nothing(household: str, term_start: str) -> bool:
        return household in churned_billing_accounts and term_start >= _departed_on[household]
    # B7 slice 2 (`sim/customer_state_layer.py`). Read once per run; with it off nothing below asks.
    _home_moves_on = moves_active()
    # Vulnerability as a hidden household state (`simulation/vulnerability_state.py`). Read once
    # per run; with it off nothing below asks and the result carries no `psr_registrations`.
    _vulnerability_hidden_state_on = hidden_state_active()
    # The save on the Invitation to Intervene (`simulation/save_on_loss_notice.py`). Read once per
    # run; with it off the save branch below is never entered and nothing reads the scale.
    _save_offers_on = save_offers_active()
    _save_scale = world_save_response_scale() if _save_offers_on else 1.0
    save_on_loss_notice_log: list[dict] = []
    # ONE SAVE ANSWERS EVERY NOTICE A HOUSEHOLD SENT (fuel page §8a, step 1b). The household rule is
    # a price match, so a cut-share experiment cannot run under it; refused rather than ignored.
    _save_decides_per_household = policy.save_offer_decides_per_household
    if _save_decides_per_household and (policy.save_offer_cut_share is not None
                                        or policy.save_offer_sizing != "price_match"):
        raise ValueError(
            "save_offer_decides_per_household prices a household by price match; this policy sizes "
            f"saves by cut share {policy.save_offer_cut_share!r} / sizing "
            f"{policy.save_offer_sizing!r}, which the household rule does not implement")
    # A saved household's other legs, billed their save when priced: (point, start) -> rate.
    _household_save_carry: dict[tuple[str, str], float] = {}
    _move_out_by_household: dict[str, date | None] = {}
    # THE MOVE-OUT NOTICE (`interface/contracts/move_out_notice_seam.py`): our household tells us,
    # two Working Days before its move, and the company files it in its own register. Only a
    # household still ours at the notice sends one; with moves off nothing is sent.
    _move_out_feed = MoveOutNoticeFeed()
    _move_out_register = open_move_out_register()
    # ...and what the company decided on each, one row per household, on its deciding leg.
    move_with_us_log: list[dict] = []
    # Whether households answer that offer (`simulation/move_with_us_answer.py`): read once per run.
    _move_with_us_answers = move_with_us_active()
    _move_with_us_k = take_up_scale() if _move_with_us_answers else None
    # STEP 4: a mover who takes the offer is supplied at its new home (home_moves.md s.8.6). Its
    # electricity leg keeps its account; from the move it lives at a drawn destination, and its next
    # move is drawn there (`_move_out_by_leg`). Its new home's data is bound to the account at its
    # next term (`_relocation_pending`): the term in force settles the old home to the move date and
    # the new one after it (`_carried_from`). Every one stays empty unless a mover follows.
    _move_out_by_leg: dict[str, date | None] = {}
    _home_move_by_leg: dict = {}
    _relocation_pending: dict[str, dict] = {}
    _journey_before_move: dict[tuple, object] = {}
    _followed_moves: set[tuple] = set()
    _home_move_by_household: dict = {}
    # s.8.7: what a carried electricity leg's destination tells its household's gas leg, keyed by
    # (household, move date); and, per gas leg that followed, the new home its next term binds.
    _destination_for_gas: dict[tuple, dict] = {}
    _gas_relocation_pending: dict[str, dict] = {}
    home_move_outs: list[dict] = []
    # leg -> move date, for the triad's final-bill exit under one payment truth.
    _moved_out_on_by_leg: dict[str, str] = {}
    # B7 slice 3: who supplies a vacated premise from the move date. The book is live and module
    # level, so a second run in one process starts it empty.
    _incoming_occupant_book = incoming_occupant_supply_points()
    _incoming_occupant_book.clear()
    home_move_ins: list[dict] = []
    # B7 slice 4: per incoming leg, the day its energy stops being the unnamed occupier's.
    _unnamed_until: dict[str, date] = {}
    # B7 slice 6 (voids, director 2026-10-08): per incoming leg, the first day that is not the
    # owner's void; per incoming household, the day its own occupancy (and move hazard) starts;
    # per incoming leg, its `home_move_ins` entry, so the void's charge is totalled on it.
    _void_until: dict[str, date] = {}
    _occupant_from: dict[str, date] = {}
    _move_in_entry: dict[str, dict] = {}

    # AN INCOMING OCCUPANT IS DOMESTIC WHEN ITS PREMISE WAS. `_RESI_CUSTOMER_IDS` is frozen at
    # import, so an account admitted mid-run was never in it, and the renewal chain was told
    # `is_domestic=False`: the cap clamp skipped every OCC- default-tariff term, 1,388 of 1,866 sat
    # above their own window's cap (x1.15 median, up to x1.38) on the 19 Oct run
    # (SEAT_FINDING_SVT_BILLS_ABOVE_THE_CAP_ARE_TWO_DEFECTS_NOT_A_GRADING_ARTEFACT_2026-10-23).
    _admitted_resi_ids: set[str] = set()

    def _is_domestic_leg(cid: str) -> bool:
        return cid in _RESI_CUSTOMER_IDS or cid in _admitted_resi_ids

    def _known_customers() -> list[dict]:
        """The run's accounts, the incoming occupants admitted so far included. With moves off it
        is `_ALL_KNOWN_CUSTOMERS` exactly."""
        return _ALL_KNOWN_CUSTOMERS + _incoming_occupant_book

    def _admit_incoming_occupant(vacated_leg: dict, commodity: str, move) -> None:
        """Supply the vacated leg under the incoming occupant's account from the move date, on
        the default tariff. Everything keyed by meter point (weather, fabric trace, property,
        annual quantity) is the premise's. The account's own state starts empty."""
        record = incoming_occupant_record(vacated_leg, move)
        leg, premise = record["customer_id"], vacated_leg["customer_id"]
        if get_customer(leg) is not None:
            return
        if record.get("segment", "resi") == "resi":
            _admitted_resi_ids.add(leg)
        _incoming_occupant_book.append(record)
        # B7 slice 6: the vacated home stands empty for its tenure's void, read from the
        # register for the MOVER's tenure (the home vacated is theirs). The meter point's account
        # still opens on the move date, because the supplier stays registered and settles the
        # void; those rows are the owner's (`as_void_row`). The occupant's own supply, and so the
        # unnamed window, start when the void ends.
        _vacated_tenure = _tenure_of_household(household_of(premise))
        _occupant_start, _void_reason = void_end(move.move_date, _vacated_tenure)
        if _occupant_start > move.move_date:
            _void_until[leg] = _occupant_start
        _occupant_from[household_of(leg)] = _occupant_start
        _unnamed_until[leg] = unnamed_until(_occupant_start)
        for _by_point in (weather_by_customer, cloud_cover_by_customer, hh_consumption_by_customer,
                          fabric_series_by_customer, properties):
            if premise in _by_point:
                _by_point[leg] = _by_point[premise]
        if premise in EFFECTIVE_EAC_KWH:
            EFFECTIVE_EAC_KWH[leg] = EFFECTIVE_EAC_KWH[premise]
        # Fabric eligibility is a verdict on the premise, so the incoming leg carries its premise's.
        fabric_eligibility_verdicts.extend(
            FabricEligibility(leg, _v.is_eligible, _v.reason)
            for _v in list(fabric_eligibility_verdicts) if _v.customer_id == premise
        )
        next_hf[leg] = current_hf[leg] = RESET_HEDGE_FRACTION
        term_indices[leg] = 0
        evolution_logs[leg] = []
        if commodity == "electricity":
            _accounts_with_an_electricity_leg.add(household_of(leg))
        _fuels_of_household.setdefault(household_of(leg), set()).add(commodity)
        try:
            segments = build_svt_schedule(
                leg, record["acquisition_date"], effective_end,
                elec_records if commodity == "electricity" else gas_records,
                lookback_temps_fn=_lookback_temps_fn(leg), fuel=commodity,
            )
        except ValueError:
            # The price history ends before the window does, as for a declined fix.
            segments = []
        for _segment in segments:
            _push_term(_segment["acquisition_date"], leg, commodity, _segment)
        _move_in_entry[leg] = {
            "premise": premise, "customer_id": leg, "household": household_of(leg),
            "commodity": commodity, "supply_start": _occupant_start.isoformat(),
            "account_opened": record["acquisition_date"],
            "terms": record["terms"], "tariff_type": record["tariff_type"],
            "segments": len(segments),
            "unnamed_until": _unnamed_until[leg].isoformat(),
            "occupancy_start_unknown_reason": move.incoming.start_date_unknown_reason,
            "vacated_tenure": _vacated_tenure.value,
            "void_days": (_occupant_start - move.move_date).days,
            "void_reason": _void_reason,
            "void_consumption_unknown_reason": (
                VOID_CONSUMPTION_GAP_REASON if leg in _void_until else None),
            "void_owner_charge_gbp": 0.0,
        }
        home_move_ins.append(_move_in_entry[leg])
    def _supply_at_new_home(cid: str, commodity: str, household: str, move_end: date,
                            carried_to: str) -> tuple[dict, str | None]:
        """Bind a mover who took the offer to its new home (home_moves.md s.8.6, choices 3-5).
        Returns (what the log records, the reason it could not be supplied, or None)."""
        if commodity != "electricity":
            # A dual-fuel household's gas follows its electricity (`_carry_gas_leg`); a household
            # we supply gas alone has no electricity leg to draw the destination on.
            return {}, ("a gas-only household's destination is not drawn: its gas follows only "
                        "beside an electricity leg (home_moves.md s.8.7)")
        record = get_customer(cid)
        if record is None or is_hh_customer(record):
            return {}, ("a half-hourly account settles on its own metered file, which cannot be "
                        "redrawn for a new home")
        move = _home_move_by_leg.get(cid, _home_move_by_household[household])
        dest = draw_destination(move.mover_arrives.premise_id, record, move_end, run_base_seed())
        if dest is None:
            return {}, "the origin names no ONS region, or the destination region has no siting cells"
        _now = household_demand_register.household_at_date(cid, move_end.isoformat())
        # AN INCOMING OCCUPANT the world drew no household for carries nothing of its own (no EV,
        # its stress unknown): it lives at the new dwelling as drawn. Named, not filled in.
        new_home = (household_at_destination(_now, dest) if _now is not None
                    else dataclasses.replace(dest.premise.household, customer_id=cid,
                                             output_area=dest.output_area))
        dest_record = {**record, "location": {"lat": dest.lat, "lon": dest.lon,
                                               "region": dest.region,
                                               "output_area": dest.output_area}}
        site = _weather_source.site_for(dest_record)
        if not _weather_source.available(site):
            return {}, f"no weather for the destination's cell ({site})"
        household_demand_register.relocate(cid, move_end.isoformat(), new_home)
        series = build_fabric_series_for_site(
            customer_id=cid,
            household_at_date=lambda d, _c=cid: household_demand_register.household_at_date(_c, d),
            weather_site=site, latitude_deg=dest.lat, start=move_end,
            end=date.fromisoformat(effective_end), seed=DEFAULT_TRACE_SEED,
            weather_days_for=_weather_source.days,
        )
        _shape = fabric_shape_fn(series, "electricity",
                                 battery_dispatch=_fabric_battery_dispatch_for(cid))
        _dates = series.dates()
        if len(_dates) >= 365:
            eac, _basis = registry_eac_from_own_reads(_shape, _dates, move_end.isoformat())
        else:
            # Under a year of the new home left in the window: its own reads, annualised.
            eac = sum(sum(_shape(d)) for d in _dates) * 365.0 / max(1, len(_dates))
        from simulation.premise_population import dwelling_record
        _relocation_pending[cid] = {
            "location": dest_record["location"], "series": series,
            "property": {**properties.get(cid, DEFAULT_PROPERTY),
                         **dwelling_record(dest.premise), "output_area": dest.output_area},
            "eac_kwh": round(eac, 1),
        }
        nxt = next_move_from_destination(
            move, date.fromisoformat(carried_to[:10]),
            date.fromisoformat(effective_end) + timedelta(days=1), run_base_seed())
        _move_out_by_leg[cid] = nxt.move_date if nxt else None
        _home_move_by_leg[cid] = nxt
        _destination_for_gas[(household, move_end)] = {
            "destination": dest, "location": dest_record["location"], "series": series,
            "next_move": nxt}
        return {"destination_premise": dest.premise_id, "destination_region": dest.region,
                "destination_in_origin_region": dest.in_origin_region,
                "destination_epc": new_home.epc_rating,
                "destination_property_type": new_home.property_type.value,
                "destination_eac_kwh": round(eac, 1),
                "next_move_date": nxt.move_date.isoformat() if nxt else None,
                "destination_takes_gas": dest.premise.commodity == "gas",
                "supplied_at_new_home": True}, None

    def _carry_gas_leg(cid: str, household: str, move_end: date) -> str | None:
        """A dual-fuel household that moved with us takes its gas leg to the new home on the same
        date (home_moves.md s.8.7). Returns None when the leg follows, else the named reason it
        ends at the move. The registered AQ stays the household's band draw (choice 4); the
        weather changes on the move date and the dwelling's multiplier and heating share from the
        end of the carried term (choice 3)."""
        dest = _destination_for_gas.get((household, move_end))
        if dest is None:
            return "the household's electricity leg was not supplied at a new home"
        if dest["destination"].premise.commodity != "gas":
            return ("the new home has no mains gas meter (its drawn dwelling burns no mains gas): "
                    "the household arrives electricity-only")
        _why = relocate_premise_sky(cid, move_end.isoformat(), {"location": dest["location"]})
        if _why is not None:
            return f"no weather for the destination's cell: {_why}"
        _now = household_demand_register.household_at_date(cid, move_end.isoformat())
        if _now is not None:
            household_demand_register.relocate(
                cid, move_end.isoformat(), household_at_destination(_now, dest["destination"]))
        _gas_relocation_pending[cid] = dest
        nxt = dest["next_move"]
        _move_out_by_leg[cid] = nxt.move_date if nxt else None
        _home_move_by_leg[cid] = nxt
        return None

    # EP12: HOW THE SUPPLIER HEARS IT LOST A HOUSEHOLD -- a registration-loss notice per supply
    # point, from the registration service, filed in its change-of-supplier register. Called at
    # every site that adds to `churned_billing_accounts` and handed only the household and the
    # date, so nothing from the departure event can ride on the notice. It crosses framed and on
    # the wire (`interface/contracts/registration_loss_seam.py`), like the bureau's ADDACS advices.
    _registration_loss_feed = RegistrationLossFeed()
    _change_of_supplier_register = open_change_of_supplier_register()

    def _notify_registration_loss(household: str, effective_from: str,
                                  pending_already_sent: bool = False) -> None:
        _points = supply_points_on_supply(household, effective_from, elec_schedules, gas_schedules,
                                          _moved_out_on_by_leg)
        _departed_on[household] = effective_from
        # EACH LEG'S OWN DEPARTURE, for readers that count per supply point. Not
        # `customer_events_log`: its churned rows are counted as households leaving, and a second
        # row for the gas leg would count every dual departure twice.
        for _point, _fuel in _points:
            _leg_departures.append({
                "customer_id": _point, "household": household, "commodity": _fuel,
                "event_type": "churned", "event_date": effective_from,
            })
        # The account closes today, so its final bill is the month of the last day supplied: told
        # now, before the next reader forces a crossing (`close_account`).
        _payment_triad.close_account(household, _bill_due_on(
            (date.fromisoformat(effective_from[:10]) - timedelta(days=1)).isoformat()[:7]))
        _pending = [] if pending_already_sent else (
            _registration_loss_feed.wire_pending_notices_for_departure(_points, effective_from))
        for _wire in (
            _pending + _registration_loss_feed.wire_notices_for_departure(_points, effective_from)
        ):
            _change_of_supplier_register.receive_loss_wire(_wire)

    # C1b. THE DAY THIS ACCOUNT'S CURRENT STINT ON THE STANDARD VARIABLE PRODUCT BEGAN, which is
    # what the published inertia bands are cut on (under 3 years / 3+ years on the default
    # tariff). Reset when a household takes a fixed deal again, because "years on SVT" is
    # CONTINUOUS tenure on the default tariff and not a lifetime total -- a household that fixed
    # in between has demonstrably shopped, which is the whole thing the band is measuring.
    _svt_stint_start: dict[str, str] = {}
    _last_tariff_type: dict[str, str] = {}
    #: Whether each leg's last term was a default segment spliced in by a declined fix, so the
    #: company can tell the default stint a refusal began from one it was rolled onto.
    _last_term_spliced: dict[str, bool] = {}
    _svt_departures: list[dict] = []
    #: EVERY SVT segment decision, not only the ones that ended in a departure. `_svt_departures`
    #: is the numerator; nothing can be graded on a numerator. A hazard or a belief is scored over
    #: the decisions where the household COULD have left, which on this book is 1,266 against 50
    #: departures — and without the 1,216 that stayed there is no denominator, no null and no AUC.
    _svt_decisions: list[dict] = []
    #: A fix refused on the leg that does NOT carry its household's departure. Not
    #: `customer_events_log`: that leg takes no stay-or-leave decision (its household took it on the
    #: decision leg, which already has its row), so a `renewed` row there is a decision nobody
    #: took. Every renewal-decision counter would gain it, and since it names the gas leg's own id
    #: the whole-book account denominator would gain an account that exists only in decline years.
    _declined_on_the_riding_leg: list[dict] = []
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
    # World-side: what each offer changed (harness only), and the save rate's own holdout.
    retention_offer_channel_log: list[dict] = []
    retention_save_holdout_log: list[dict] = []
    retention_save_rate_lower_bound_log: list[dict] = []
    # B8 L3: the company's own retention holdout, on a policy that runs one.
    _retention_holdout = new_retention_holdout() if policy.retention_runs_holdout else None
    retention_holdout_log: list[dict] = []
    # C34 at the renewal notice, on a policy that asks for it: records only, moves nothing.
    # The term's contribution is the one margin every renewal decision weighs (C34, the retention
    # guard, the missed-retention log), so it is imported whether or not C34 is on.
    from company.interfaces.renewal_advice import (
        RenewalAdviceDesk,
        term_contribution_per_month,
        term_contribution_per_year,
    )
    _renewal_advice = None
    _refuse_a_rise_with_no_caller(policy)
    _refuse_a_billed_rise_with_no_price(policy)
    shared_rise_log: list[dict] = []
    _refuse_save_odds_with_no_ending_term(policy)
    if policy.next_best_action_decides_at_renewal:
        _renewal_advice = RenewalAdviceDesk(policy)
    # What the value test would have said where the 10-10 gate refused first. Read by nothing in
    # the loop, so it changes no outcome; it says whether the gate binds or the guard would have
    # refused the same households anyway.
    retention_gate_value_test_log: list[dict] = []
    # Phase 12c: churns where no offer was made (missed opportunities)
    no_offer_churn_log: list[dict] = []
    # Phase 14b: gas renewal rate pressure log for dual-fuel monitoring
    company_gas_churn_log: list[dict] = []
    # Phase 27c: volume tolerance tracking for I&C customers
    volume_tolerance_log: list[dict] = []

    current_year_str = REPORT_START[:4]
    ytd_gross = ytd_net = ytd_capital = 0.0

    print("=== Processing terms chronologically ===\n")

    while all_terms:
        term_start_str, cid, _, commodity, term = heapq.heappop(all_terms)
        _pending_starts[cid].remove(term_start_str)
        if term.pop(_HELD_FOR_THE_DECISION_LEG, False):
            term_start_str = term["acquisition_date"]
        _spliced = bool(term.get(_DECLINED_FIX_SPLICE))
        if administration_event:
            break

        # Phase 6b: skip churned accounts (household level — covers both elec + gas legs).
        # KNIFE step 28 (§3w): the HOUSEHOLD, asked of the world, not the billing
        # account, asked of the supplier. The local name below is the supplier's
        # vocabulary and stays only because ~60 downstream uses and two run-record
        # output keys carry it; the VALUE no longer comes from a company module.
        billing_account = household_of(cid)
        # THE LEG THIS ACCOUNT'S DEPARTURE IS ROLLED ON, resolved once per term and used at both
        # booking sites below so the two cannot drift apart. `"electricity"` for every account
        # that holds an electricity leg, which is what both sites spelled as a literal until
        # 2026-09-16; `"gas"` only where the alternative was no roll at all.
        _decision_leg = departure_decision_leg(
            billing_account,
            accounts_with_an_electricity_leg=_accounts_with_an_electricity_leg,
        )
        if _supplies_nothing(billing_account, term_start_str):
            if not _spliced:
                term_indices[cid] += 1
            continue

        # Phase 7e's successor points are never supplied (see `SUCCESSOR_ELEC_CUSTOMERS`).
        if cid in _SUCCESSOR_ELEC_IDS:
            continue

        term_end_str = term.get("term_end") or _clamp_term_end(term_start_str, end_date=effective_end)

        # A RIDING LEG WAITS FOR THE ROLL IT RIDES ON. The household leaves once, on its decision
        # leg, so a gas term that a decision-leg start falls inside goes back in the heap keyed to
        # that start; the decision leg pops first there (`C1` sorts before `C1g`). Asked again
        # until no such start is left, then posted -- whole, or cut below at the departure.
        if commodity != _decision_leg and billing_account not in churned_billing_accounts:
            _decision_starts = _pending_starts.get(billing_account, ())
            _i = bisect.bisect_right(_decision_starts, term_start_str)
            if _i < len(_decision_starts) and _decision_starts[_i] < term_end_str[:10]:
                term[_HELD_FOR_THE_DECISION_LEG] = True
                _push_term(_decision_starts[_i], cid, commodity, term)
                continue
        # A CHANGE OF SUPPLIER ENDS EVERY FUEL ON ONE DATE: the riding leg's last day supplied is
        # the day before its household's departure (`unbilled_energy_and_revenue_assurance.md`).
        # `term_end` is exclusive, so it is the departure date itself.
        if billing_account in churned_billing_accounts:
            term_end_str = _riding_leg_term_end(term_end_str, _departed_on[billing_account])

        # A LEG THAT MOVED WITH US is bound to its new home from this term on: weather, dwelling,
        # demand trace and the meter point's annual quantity are the destination's. The vacated
        # home's data went to its incoming occupant as new references, so nothing there moves.
        if cid in _relocation_pending:
            _new_home = _relocation_pending.pop(cid)
            _rec = get_customer(cid)
            _rec["location"] = _new_home["location"]
            weather_by_customer[cid] = weather_means_for_customer(_rec, _weather_world)
            cloud_cover_by_customer[cid] = cloud_cover_for_customer(_rec, _weather_world)
            # THE VERDICT FOLLOWS THE HOME, as the series does (the incoming-occupier path copies its
            # premise's for the same reason). Inline, it was left behind once and only a fresh-seed run
            # saw it; tests/simulation/test_run_phase2b_mover_verdict.py holds this block to the call.
            rebind_fabric_verdict_to_new_home(
                cid, _new_home["series"],
                series_by_customer=fabric_series_by_customer,
                verdicts=fabric_eligibility_verdicts,
            )
            properties[cid] = _new_home["property"]
            _rec["eac_kwh"] = EFFECTIVE_EAC_KWH[cid] = _new_home["eac_kwh"]
        # ...and a GAS LEG that moved with it (s.8.7, choice 3): the new home's coordinate, and the
        # heating share refitted on the new dwelling's own gas trace under the household's
        # occupancy. Its sky already turned on the move date (`_carry_gas_leg`); its AQ is kept.
        if cid in _gas_relocation_pending:
            _new_home = _gas_relocation_pending.pop(cid)
            get_customer(cid)["location"] = _new_home["location"]
            gas_heating_fraction_by_customer.pop(cid, None)
            gas_shape_refusals[:] = [r for r in gas_shape_refusals if r.customer_id != cid]
            _fit_dates = sorted(_new_home["series"].gas_kwh)[:365]
            _split = seasonal_gas_split(
                cid, [sum(_new_home["series"].gas_kwh[d]) for d in _fit_dates],
                [get_hdd(d, cid) for d in _fit_dates],
                daily_space_heating_kwh=[_new_home["series"].gas_space_heating_kwh[d]
                                         for d in _fit_dates])
            if isinstance(_split, SeasonalGasRefusal):
                gas_shape_refusals.append(_split)
            else:
                gas_heating_fraction_by_customer[cid] = _split

        # B7 slice 2: a home move ends this household's supply at the move date. Asked once, at
        # the household's first term (the heap is chronological), over its own supply window, so
        # a household won in 2020 cannot lose a term to a move drawn in 2018. Off unless the curriculum
        # file says on.
        _moved_in_term = False
        _carried_from = None
        if _home_moves_on:
            if billing_account not in _move_out_by_household:
                # An incoming occupant moves on the same hazard, so a premise can turn over twice.
                _mover = next(
                    (c for c in _known_customers()
                     if c["customer_id"] == billing_account), None
                )
                # An incoming household lives there only from the end of the void.
                _hazard_from = max(date.fromisoformat(term_start_str),
                                   _occupant_from.get(billing_account, date.min))
                _hazard_to = date.fromisoformat(effective_end) + timedelta(days=1)
                # A void that ends at or after the window's end leaves this household no time in
                # the window to move: no move, not an empty window (which first_move_out refuses).
                _move = (account_move_out(_mover, _hazard_from, _hazard_to, run_base_seed())
                         if _hazard_from < _hazard_to else None)
                _move_out_by_household[billing_account] = _move.move_date if _move else None
                _home_move_by_household[billing_account] = _move
            _move_end, _moved_in_term = term_window_under_move(
                date.fromisoformat(term_start_str), date.fromisoformat(term_end_str[:10]),
                _move_out_by_leg.get(cid, _move_out_by_household[billing_account]),
            )
            if _move_end is None:
                if not _spliced:
                    term_indices[cid] += 1
                continue
            if _moved_in_term:
                _next_renewal_str = term_end_str
                term_end_str = _move_end.isoformat()
                if _churn_journey_register.get_journey(billing_account) is None:
                    _churn_journey_register.register_customer(billing_account)
                _mover_journey = _churn_journey_register.get_journey(billing_account)
                # A household that moved with us is still ours: its other leg's move does not end
                # its journey, and the leg that carried it restores what the move recorded.
                if (billing_account, _move_end) not in _followed_moves:
                    _journey_before_move.setdefault((billing_account, _move_end),
                                                    _mover_journey.state)
                    _mover_journey.record_home_move(_move_end)
                # W2_36 slice 3: the change-of-tenancy gap. The vacated meter goes on recording
                # with nobody named liable; sim/customer_state_layer.py says why the window is an
                # expectation and why the rate is the meter point's annual quantity.
                _leg = get_customer(cid)
                _moved_out_on_by_leg[cid] = _move_end.isoformat()
                home_move_outs.append({
                    "household": billing_account, "customer_id": cid,
                    "commodity": commodity, "move_date": _move_end.isoformat(),
                    "journey_state": _mover_journey.state.value,
                    "catchable": _mover_journey.is_catchable(),
                    "unnamed_kwh_expected": unnamed_kwh_after_move(
                        _leg.get("aq_kwh") if commodity == "gas" else _leg.get("eac_kwh")),
                })
                _admit_incoming_occupant(
                    _leg, commodity,
                    _home_move_by_leg.get(cid, _home_move_by_household[billing_account]))
                # A GAS LEG FOLLOWS ITS HOUSEHOLD (home_moves.md s.8.7): two meters, one date. Its
                # decision leg popped first (a riding leg waits for it, above), so whether the
                # household moved with us is already known. The vacated meter is admitted above.
                if commodity == "gas" and (billing_account, _move_end) in _followed_moves:
                    _gas_why_not = _carry_gas_leg(cid, billing_account, _move_end)
                    home_move_outs[-1]["followed_household"] = _gas_why_not is None
                    for _row in reversed(move_with_us_log):
                        if (_row["billing_account"] == billing_account
                                and _row["move_out_date"] == _move_end.isoformat()):
                            _row["gas_leg_follows"] = _gas_why_not is None
                            _row["gas_not_followed_reason"] = _gas_why_not
                            break
                    if _gas_why_not is None:
                        term_end_str = _next_renewal_str
                        # Choice 7: a follower is not an exit, so its bills are not final bills.
                        _moved_out_on_by_leg.pop(cid, None)

        # A DEFAULT TARIFF IS PRICED AT ITS PAYMENT METHOD'S CAP COLUMN (SLC 28AD), read from the
        # method the company's own register holds on the segment's first day. The schedule was
        # built at the DD level before any register could be asked; 496 electricity and 462 gas
        # prepayment term-windows sat over the prepayment cap on the 67a893e749 book until this.
        _svt_priced_method = None
        if term.get("tariff_type") == SVT_TARIFF_TYPE and _is_domestic_leg(cid):
            from company.interfaces.sim_interface import LiveSimInterface
            _svt_priced_method = LiveSimInterface().get_payment_method(
                billing_account, commodity, as_of=term["acquisition_date"])
            price_segment_for_payment_method(
                term, fuel=commodity, method_held=_svt_priced_method)

        forward_price = term["forward_price_gbp_per_mwh"]        # sim's sophisticated estimate
        company_fwd = term.get("company_forward_price_gbp_per_mwh", forward_price)
        unit_rate = term["unit_rate_gbp_per_mwh"]
        term_tariff_type = term.get("tariff_type", "fixed")
        # A spliced segment carries the index of the term it replaced and advances nothing.
        term_index = term_indices[cid] - 1 if _spliced else term_indices[cid]
        if not _spliced:
            term_indices[cid] += 1

        # KNIFE step 24 (§3s): EVERY writer that moves this renewal's rate --
        # the portfolio learning premium, the realised-margin recovery
        # surcharge, the unprofitability uplift and the price-cap clamp -- is
        # the supplier's own pricing policy, including WHICH renewals each one
        # applies to and the ORDER they fire in. They form one chain producing
        # one number, so they are one door: company/interfaces/renewal_rate_chain.py.
        # The world reports the renewal as it happened and records what came back.
        # THE PORTFOLIO POSITION AS THE CHAIN BELOW WILL READ IT, taken here and carried down to
        # the account-state record rather than re-read there. The two call sites are ~260 lines
        # apart with the margin history mutable between them; taking one reading is what makes
        # the recorded figure the one the rate was actually struck against, and not a second
        # reading that agrees today.
        _portfolio_margins.as_of(term_start_str)
        _position = portfolio_position(_portfolio_margins.rates(commodity),
                                       _portfolio_margins.priced_for(commodity))
        # WHAT THIS ACCOUNT HAS PAID, ASKED BEFORE THE PRICE IS STRUCK (2026-10-03). The value arm
        # priced every renewal blind to payment history -- the arrears state reached the churn
        # estimate below, AFTER the rate was set, and never reached the rate. Asked through the
        # same doors and on the same no-look-ahead bound as that estimate: the company's own ledger
        # (the triad) and the payment-method seam. Pure reads, so a control-arm run, which never
        # looks at them, is unchanged. An acquisition term has nothing on the ledger to ask about.
        # `_company_payment_method` is resolved HERE for the price and again, identically, in the
        # churn block below, which resets it every term -- one name for the one fact, so the run
        # can only ever hand the company the method it resolved.
        _chain_arrears_state = _chain_receivable = _company_payment_method = None
        _chain_default_belief = None
        if term_index >= 1 and not _spliced:
            _chain_segment = _SEGMENT_OF.get(cid, "resi")
            _chain_asof = date.fromisoformat(term_start_str)
            _chain_arrears_state = _payment_triad.arrears_state(
                cid, _chain_asof, segment=_chain_segment)
            _chain_receivable = _payment_triad.receivable(cid, _chain_asof, segment=_chain_segment)
            if _chain_segment == "resi":
                from company.interfaces.sim_interface import LiveSimInterface
                _company_payment_method = LiveSimInterface().get_payment_method(
                    billing_account, commodity, as_of=term_start_str)
                # THE BOOK'S OWN DEFAULT RATE, asked only when the policy prices on it, so a
                # run on the default policy makes no extra read. The method register it learns
                # over is the same seam read, per resi account, kept for the run.
                if active_policy().renewal_default_belief == DEFAULT_BELIEF_OWN_BOOK:
                    _chain_default_belief = _payment_triad.default_belief_rate(
                        _chain_asof, _chain_arrears_state, payment_method_of=_book_method_of)
        # A FIRST TERM'S FIXED STRIKE CARRIES THE BOOK'S BELIEF TOO (B12, 2026-10-15). The block
        # above is a renewal's read of the account's own record; a new account has none, but its
        # strike still bears bad debt, so it is priced on the book's belief at the account's state
        # (the whole-book prior until outcomes resolve). Without this, 200 of the 249 2016-19 fixed
        # terms the premium reads carried no allowance (PREREG_B12, grade of S-prime).
        if (_chain_default_belief is None and term_index == 0
                and _SEGMENT_OF.get(cid, "resi") == "resi"
                and active_policy().renewal_default_belief == DEFAULT_BELIEF_OWN_BOOK):
            _first_asof = date.fromisoformat(term_start_str)
            _chain_default_belief = _payment_triad.default_belief_rate(
                _first_asof, _payment_triad.arrears_state(cid, _first_asof, segment="resi"),
                payment_method_of=_book_method_of)
        # A spliced or first default segment resolves no renewal method above, but the chain's cap
        # clamp still needs one (SLC 28AD): the method this segment was priced on, the same seam read.
        # Nothing reads the name again before the churn block resets it.
        if _company_payment_method is None:
            _company_payment_method = _svt_priced_method
        # THE TYPED SEAM RECORD (2026-10-12): every input is declared company-observable on the
        # record itself, and its field list is an allow-list a world-only value cannot join.
        _chain = decide_renewal(RenewalDecisionInputs(
            customer_id=cid,
            billing_account=billing_account,
            commodity=commodity,
            term_start=term_start_str,
            tariff_type=term_tariff_type,
            term_index=term_index,
            struck_unit_rate_per_mwh=unit_rate,
            portfolio_margin_rates=_portfolio_margins.rates(commodity),
            portfolio_priced_for_rates=_portfolio_margins.priced_for(commodity),
            prior_term_margin=prev_term_margin.get(cid),
            prior_term_revenue=prev_term_revenue.get(cid, 0.0),
            is_domestic=_is_domestic_leg(cid),
            # `_SEGMENT_OF` already exists here for the Triad carve-out, so the fact the
            # renewal desk was missing was three lines away the whole time.
            segment=_SEGMENT_OF.get(cid, "resi"),
            settled_records=all_records,
            # The same record the ToU offer below is handed, for the same metering facts: the
            # company grades a term it sells as ToU against the multi-register cap.
            customer=get_customer(cid),
            arrears_state=_chain_arrears_state,
            receivable=_chain_receivable,
            payment_method=_company_payment_method,
            default_belief_rate=_chain_default_belief,
            # THE COMPANY'S OWN DEFAULT TARIFF on the day: what it bills a household on its SVT,
            # which is the published series this world bills that product at. A supplier knows
            # its own default price; before the 2019 cap there is no ceiling to read it from.
            own_default_tariff_inc_vat_per_mwh=(
                _account_state_svt_rate(commodity, term_start_str)
                if _is_domestic_leg(cid) else None),
            # THE COMPANY'S OWN OFFER for this term, read off the term dict its offer wrote, so the
            # desk can floor a discount at the cost it struck over. Deliberately NOT `company_fwd`
            # above, which falls back to the world's forward where the offer recorded none.
            company_forward_per_mwh=term.get("company_forward_price_gbp_per_mwh"),
            locked_policy_cost_per_mwh=term.get("locked_policy_cost_gbp_per_mwh"),
            locked_network_cost_per_mwh=term.get("locked_network_cost_gbp_per_mwh"),
        ))
        unit_rate = _chain.unit_rate_gbp_per_mwh
        dynamic_pricing_log.extend(_chain.dynamic_pricing_entries)
        margin_feedback_log.extend(_chain.margin_feedback_entries)
        profitability_uplift_log.extend(_chain.profitability_uplift_entries)
        value_arm_log.extend(_chain.value_arm_entries)
        value_arm_funnel_log.extend(_chain.arm_funnel_entries)
        if _chain.decomposition is not None:
            rate_decomposition_log.append(_chain.decomposition)
        # THE OFFER'S POSITION AGAINST THE DEFAULT THIS HOUSEHOLD WOULD OTHERWISE PAY, read once,
        # here, against the rate the chain struck. None wherever the decline-and-stay rule does
        # not apply, and None never declines -- so with the switch off nothing below moves.
        _offer_vs_default = (
            position_vs_default(unit_rate, term_start_str, commodity=commodity)
            if (DECLINE_A_FIX_ABOVE_THE_DEFAULT and term_index >= 1 and not _spliced
                and term_tariff_type == "fixed" and _is_domestic_leg(cid)
                and not term.get(_WOKEN_REFIX))
            else None
        )
        _renewal_outcome = None
        _held_on_a_save = False
        # THE OTHER LEG OF A HOUSEHOLD SAVED AT ITS ROLL is supplied at its save (fuel page §8a). The
        # save was priced on this leg's offer as first struck; where the chain has since gone lower,
        # the lower rate stands, because a save never raises a price.
        _carried_billed = _take_household_save_carry(
            _household_save_carry, cid, term_start_str, unit_rate, spliced=_spliced)
        if _carried_billed is not None:
            unit_rate = _carried_billed
            _held_on_a_save = True
            _offer_vs_default = None

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
        # THE PRIOR RATE THE DEPARTURE DECISION IS TAKEN AGAINST, on whichever leg carries it.
        # Named for the ROLE and not for the fuel (it was `old_elec_rate` until 2026-09-16), which
        # is the whole reason the gas-only defect was invisible from inside this branch: a name
        # saying "elec" reads as correct beside a guard saying "electricity" however wrong the
        # guard is. On an account with an electricity leg this is the same lookup it always was.
        old_decision_leg_rate = (
            prev_elec_unit_rates.get(cid) if commodity == "electricity"
            else prev_gas_unit_rates.get(cid)
        ) if commodity == _decision_leg else None
        # THE SECONDARY FUEL'S OWN PRIOR RATE, and it stays fuel-spelled on purpose: its one
        # consumer below is the dual-fuel gas pressure log, which is about the leg that does NOT
        # decide. See the guard there.
        old_gas_rate = prev_gas_unit_rates.get(cid) if commodity == "gas" else None
        # `svt` joins the indexed tariffs (2026-08-30, brief WORK item 4). It belongs here for
        # the same reason `deemed` and `flex` do and for one more: those two have no RENEWAL
        # because their price is indexed, and an SVT segment has no renewal because there is no
        # TERM -- a segment boundary is a cap change, not an expiry. Gating it out here is what
        # makes "no renewal decision" a property of the product rather than a claim about it.
        # An SVT account therefore cannot depart yet, which is exactly why no roster assigns
        # one; see simulation/svt_product.py on what is owed before assignment.
        _indexed_tariff = term_tariff_type in ("deemed", "flex", SVT_TARIFF_TYPE)
        # What a refused offer must not leave behind is restored from these (see the decline).
        _prior_rates = prev_elec_unit_rates if commodity == "electricity" else prev_gas_unit_rates
        _prior_rate_before_offer = _prior_rates.get(cid)
        _shock_counted_this_term = False
        if commodity == "electricity" and not _indexed_tariff:
            prev_elec_unit_rates[cid] = unit_rate
        elif commodity == "gas" and not _indexed_tariff:
            prev_gas_unit_rates[cid] = unit_rate
        # THE SHOCK HISTORY FOLLOWS THE DECISION LEG, because its only two readers are inside the
        # renewal branch that leg gates. Counting it on the electricity leg alone left a gas-only
        # account's history permanently empty, and an empty history reads downstream as "this
        # household has never had a bill rise" rather than as "nobody looked" — which understates
        # its departure risk, the direction that flatters the company. On every account holding an
        # electricity leg this fires on exactly the terms it always did.
        if commodity == _decision_leg and not _indexed_tariff:
            if old_decision_leg_rate is not None and old_decision_leg_rate > 0:
                if (unit_rate - old_decision_leg_rate) / old_decision_leg_rate > _NG_BILL_SHOCK_THRESHOLD:
                    _rate_shock_counts[cid] = _rate_shock_counts.get(cid, 0) + 1
                    _bill_shock_dates.setdefault(cid, []).append(term_start_str)
                    _shock_counted_this_term = True

        # ═══════════════════════════════════════════════════════════════════════════════════════
        # C1b — AN ACCOUNT ON THE STANDARD VARIABLE PRODUCT CAN NOW LEAVE (2026-08-30)
        # ═══════════════════════════════════════════════════════════════════════════════════════
        #
        # `simulation/svt_product.py` refused assignment until this existed, and named the reason:
        # the renewal decision was the only place this function rolled a departure, an SVT segment
        # correctly has no renewal decision, so a household moved here would have been IMMORTAL and
        # a book of immortal households earns more than a real one. This is that interlock
        # discharged, and it lands in the same commit as the assignment for exactly that reason.
        #
        # THIS IS NOT A RENEWAL AND IT IS NOT SHAPED LIKE ONE. No offer is requested, no rate is
        # struck, no retention discount is considered and no company estimate is compared -- there
        # is nothing for the company to price and nothing it is being graded on. What happens is
        # that the household, at some point in this cap period, gets round to it. The record says
        # so: `departure_occasion` is the segment, never `"renewal"`, which is the distinction
        # `customer_events.departure_event` refuses to let a caller blur.
        #
        # WHAT IS DELIBERATELY NOT ON THIS ROLL, AND WHICH WAY IT ERRS. Only the inertia risk
        # fires here. A household on SVT can in reality also leave over a bill shock, our price
        # position or our service, and all three of those hazards need per-renewal state this
        # branch does not compute (`_price_response` needs the felt differential against an offer
        # that was never made). Omitting them REMOVES departure routes, which is the direction
        # that favours the company, so it is stated here and on the artefact rather than left to
        # be discovered: the honest reading is that an SVT account's departures are understated by
        # whatever those three would have added. What is NOT true is that SVT accounts leave less
        # than fixed ones -- the inertia band alone (10-20%/yr) sits above this book's anchored
        # whole-population level in most years of the window, and the run measures the net.
        if commodity == _decision_leg and term_tariff_type == SVT_TARIFF_TYPE:
            if _last_tariff_type.get(cid) != SVT_TARIFF_TYPE:
                _svt_stint_start[cid] = term_start_str
            _stint_start = _svt_stint_start[cid]
            _segment_days = (
                date.fromisoformat(term_end_str) - date.fromisoformat(term_start_str)
            ).days
            _years_on_svt = (
                date.fromisoformat(term_start_str) - date.fromisoformat(_stint_start)
            ).days / 365.25
            # THE GUARD IS IN `inertia_hazard_for_term`, NOT IN THIS BRANCH CONDITION. It returns
            # 0.0 for any term that is not an SVT segment, so a future edit that widens the branch
            # above cannot hand a fixed-term household the inertia hazard -- and the guard is one
            # call a test can drive, rather than the condition of a 2,000-line loop that needs a
            # decade run to reach. `term` carries its own start and end, so the two are read from
            # the same record the settlement will use.
            from simulation.household_segments import engagement_level_for_customer
            _svt_hazard = inertia_hazard_for_term(
                term, stint_start=_stint_start,
                engagement_level=engagement_level_for_customer(billing_account).value,
            )
            # The SAME action-propensity modulator every other risk carries. Income stress and
            # tenure gate whether a household acts at all, and drifting off a default tariff is
            # an action -- `departure_risks` records why a carve-out here was rejected.
            from simulation.household_segments import tenure_for_customer
            from simulation.switching_propensity import (
                stress_switching_multiplier,
                tenure_switching_multiplier,
            )
            _svt_stress = (
                household_demand_register.income_stress_at_date(billing_account, term_start_str)
                if household_demand_register is not None else None
            )
            _svt_propensity = (
                stress_switching_multiplier(_svt_stress)
                * tenure_switching_multiplier(tenure_for_customer(billing_account).value)
                if _svt_stress is not None else 1.0
            )
            _svt_risks = build_departure_risks(
                bill_shock_base=0.0,
                price_response=0.0,
                dissatisfaction_response=0.0,
                action_propensity=_svt_propensity,
                sensitivity_scale=DECLARED_SENSITIVITY_SCALE,
                level_anchor=year_level_anchor(int(term_start_str[:4])),
                svt_inertia=_svt_hazard,
            )
            _svt_p_depart = total_departure_probability(_svt_risks)
            # W2_39: A CONTACT WAKES A SHARE OF THIS STOCK, AND A WOKEN HOUSEHOLD CHOOSES ON PRICE.
            # The company's side is only the send, at the segment's start, through the seam. The
            # world then asks its own record of what arrived, so a contact that did not go through
            # the seam cannot reach this roll. With nothing received, `_svt_p_depart` is untouched
            # and the draw below is the one it always was.
            _svt_p_uncontacted = _svt_p_depart
            _svt_contact_arm = None
            if _svt_contact_instrument is not None and sends_at_segment(
                    term_start_str, _stint_start, policy.svt_contact_once_per_stint):
                _svt_contact_arm = contact_arm(
                    billing_account, _svt_contact_holdout_share, f"svt_contact_{run_base_seed()}")
                if _svt_contact_arm != "holdout":
                    _contact_seam.send_contact(
                        billing_account, date.fromisoformat(term_start_str),
                        _svt_contact_instrument)
            _svt_contact = _contacts_received.instrument_reaching(
                billing_account, date.fromisoformat(term_start_str),
                date.fromisoformat(term_end_str))
            _svt_churn_if_choosing = None
            _svt_contact_unanswered = None
            if _svt_contact is not None:
                from simulation.contact_response import (
                    churn_if_choosing_off_svt,
                    svt_departure_after_contact,
                )
                from simulation.customer_events import (
                    _annual_bill_gbp,
                    _bill_scale_for,
                    _price_differential_vs_market,
                )
                from simulation.population_draw import price_elasticity_for_customer
                # The best thing in front of a woken household is the default it is on, against
                # the one market reference every renewal is measured against. That reference is
                # the published default or a rival chasing it, never the cheapest fix on offer, so
                # where fixes sat far below the default (2016-2019) the premium is understated and
                # so is the loss: it errs in the company's favour.
                _svt_premium = _price_differential_vs_market(
                    unit_rate, term_start_str, commodity=commodity,
                    position_ledger=_competitor_position_ledger,
                    wholesale_gbp_per_mwh=forward_price,
                )
                if _svt_premium is None:
                    # Parity is a claim; an unknown position is not it. The contact went and the
                    # world cannot say what it did, so the row says so and the roll is unchanged.
                    _svt_contact_unanswered = "no market reference for this fuel and date"
                else:
                    _svt_segment = next(
                        (c.get("segment") for c in _known_customers()
                         if c.get("customer_id") == billing_account), None)
                    _svt_churn_if_choosing = churn_if_choosing_off_svt(
                        our_premium_pct=_svt_premium,
                        elasticity=price_elasticity_for_customer(billing_account, run_base_seed()),
                        annual_bill_gbp=_bill_scale_for(_svt_segment, _annual_bill_gbp(
                            billing_account, households_own_records(billing_account, all_records),
                            term_start_str)),
                        level_anchor=year_level_anchor(int(term_start_str[:4])),
                        action_propensity=_svt_propensity,
                    )
                    _svt_p_depart = svt_departure_after_contact(
                        instrument=_svt_contact, p_drift=_svt_p_uncontacted,
                        churn_if_choosing=_svt_churn_if_choosing,
                    )
            import simulation.contact_response as _contact_response
            # C30: the re-fix band sits directly above the departure band on the same draw.
            _svt_refix_top = (
                _contact_response.svt_refix_band_top(
                    instrument=_svt_contact, p_drift=_svt_p_uncontacted,
                    p_contacted=_svt_p_depart, churn_if_choosing=_svt_churn_if_choosing)
                if _contact_response.A_WOKEN_SVT_STAYER_REFIXES
                and _svt_churn_if_choosing is not None else None
            )
            # READ BEFORE THE ROLL AND USED ONLY AFTER IT. This is the company's side of the
            # decision -- its own collections record on this account -- and it is deliberately
            # NOT among the `_svt_risks` above: the belief reaches no hazard, which is the only
            # thing that makes it gradable against the outcome (see the estimate below).
            #
            # READ OVER THE ACCOUNT'S SUPPLY POINTS, NEVER UNDER `billing_account` ITSELF. The desk
            # is fed by `observe_payment(customer_id=cid)` below, so the household key alone
            # returns `None` wherever a household holds more than one meter point -- a fail-open
            # that reads as "no payment history". And `cid` alone is the decision leg only, which
            # hid a dual-fuel account's gas record from this belief until 2026-10-07.
            _svt_behaviour = _cx_desk.account_payment_behaviour_score(
                _supply_points_of_account.get(billing_account, (cid,)))
            _svt_roll = random.Random(
                f"svt_inertia_{billing_account}_{term_start_str}").random()
            from simulation.contact_response import svt_cause_on_the_coupled_roll
            _svt_cause = svt_cause_on_the_coupled_roll(
                _svt_roll, p_uncontacted=_svt_p_uncontacted, p_contacted=_svt_p_depart)
            # THE DECISION IS RECORDED BEFORE THE BRANCH, so that staying is a row too. Recording
            # inside the `if` below would log only departures and every rate computed from the file
            # would have a numerator and no denominator.
            _svt_decisions.append({
                "route": "svt_segment",
                "customer_id": billing_account,
                "event_date": term_start_str,
                "market_year": int(term_start_str[:4]),
                "event_type": "churned" if _svt_roll < _svt_p_depart else "stayed",
                "departure_cause": _svt_cause,
                "realized_churn_probability": round(_svt_p_depart, 6),
                # W2_39. `contact_instrument` is the company's own send and it knows it.
                # `sim_p_depart_uncontacted` is the same household's probability had nothing
                # arrived: the true counterfactual an uplift estimate is graded against, ground
                # truth, and never read by company code.
                "contact_instrument": _svt_contact,
                # C34. The company's own coin: "treated", "holdout", or None with no holdout run.
                "contact_arm": _svt_contact_arm,
                "sim_p_depart_uncontacted": round(_svt_p_uncontacted, 6),
                "sim_churn_if_choosing": (
                    round(_svt_churn_if_choosing, 6)
                    if _svt_churn_if_choosing is not None else None),
                "sim_contact_unanswered": _svt_contact_unanswered,
                "random_roll": round(_svt_roll, 6),
                "sim_svt_inertia": round(_svt_hazard, 6),
                "sim_action_propensity": round(_svt_propensity, 6),
                "sim_level_anchor": round(year_level_anchor(int(term_start_str[:4])), 6),
                "sim_years_on_svt": round(_years_on_svt, 3),
                "sim_segment_days": _segment_days,
                # THE COMPANY'S OWN COLLECTIONS RECORD ON THIS ACCOUNT, AS AT THIS DECISION.
                # Prefixed `company_`, not `sim_`, because it is not the world's: `_cx_desk` is
                # company-side and this is what it has already been told through
                # `observe_payment`. Recorded on the row so the grader can REPLAY the belief off
                # the capture instead of joining a second artefact -- the same reason
                # `sim_years_on_svt` is here.
                #
                # POINT-IN-TIME IS A PROPERTY OF WHERE THIS LINE SITS, and it is worth saying
                # because nothing local would show it. `observe_payment` is called further down
                # this same `all_terms` loop, which is ordered by term start, so at this moment
                # the desk holds payments from terms that started BEFORE this one and none from
                # this one or later. Reading it after the loop would have scored every account on
                # its own future.
                "company_payment_behaviour": (
                    _svt_behaviour.value if _svt_behaviour is not None else None
                ),
                # THE COMPANY'S OWN VIEW OF THIS SEGMENT, AND IT REACHES NO HAZARD ABOVE.
                # Computed AFTER `_svt_p_depart` and after the roll, deliberately: the number
                # cannot influence what happened, which is the only thing that makes it gradable.
                # `build_churn_risk` seeds `effective_p_retain` and is then scored against the roll
                # it seeded, so its 0.6815 against a 0.7400 ceiling measures the world reading back
                # its own input and its capture ratio is refused. This one is recorded beside the
                # outcome and nothing else — `tests/architecture/
                # test_the_svt_drift_belief_is_not_wired_to_any_decision.py` holds that open.
                "company_svt_drift_estimate": estimate_svt_drift(
                    SvtSegmentObservation(
                        years_on_svt=_years_on_svt,
                        segment_days=_segment_days,
                        payment_behaviour=(
                            _svt_behaviour.value if _svt_behaviour is not None else None
                        ),
                    )
                ),
                "data_regime": "historical",
            })
            if _svt_roll < _svt_p_depart:
                churned_billing_accounts.add(billing_account)
                _notify_registration_loss(billing_account, term_start_str)
                _svt_event = departure_event(
                    customer_id=billing_account,
                    event_date=term_start_str,
                    commodity=commodity,
                    occasion=DEPARTURE_OCCASION_SVT_SEGMENT,
                    cause=_svt_cause,
                    realized_churn_probability=round(_svt_p_depart, 4),
                    random_roll=round(_svt_roll, 4),
                    unit_rate_gbp_per_mwh=unit_rate,
                    sim_years_on_svt=round(_years_on_svt, 3),
                    sim_segment_days=_segment_days,
                    sim_action_propensity=round(_svt_propensity, 6),
                    sim_level_anchor=round(year_level_anchor(int(term_start_str[:4])), 6),
                )
                # ITS OWN LIST, NOT `customer_events_log`, AND THE FIRST RUN IS WHY. Appending it
                # there crashed `_main`'s own summary at `evt['churn_probability']` -- a key an
                # SVT departure has no business carrying, because there was no renewal decision to
                # estimate a churn probability FOR. Twelve more consumers index the same key
                # unguarded (`saas/clv_model`, `saas/enterprise_value`, `saas/home_move_win_rate`,
                # `saas/growth_mandate`, `saas/reporting/annual_report`,
                # `company/analytics/customer_value_view`, `tools/capture_departure_factors`), and
                # every one of them has RENEWAL DECISIONS as its subject.
                #
                # THE REPAIR IS NOT `evt.get("churn_probability") or 0`. That is the fail-open
                # this project has already paid for once: it would put a departure with no renewal
                # into a CLV survival sum as a renewal with zero churn probability, which is a
                # customer who was there and certain to stay. Two populations, two lists, and a
                # reader that wants both unions them deliberately.
                #
                # OWED, NAMED RATHER THAN LEFT TO BE FOUND: the readers whose subject is ALL
                # departures -- `tools/population_anchor._churn_by_year` and
                # `tools/measure_departure_level` -- must union these in, or they will report a
                # departure LEVEL that is missing the route this commit added. Neither is live
                # against this log today (both read captured artefacts), so nothing regresses on
                # landing; both go stale the moment the next capture runs.
                _svt_departures.append(_svt_event)
                print(
                    f"  [CHURN-SVT] {billing_account} at {term_start_str} — "
                    f"p_depart={_svt_p_depart:.4f}  roll={_svt_roll:.4f}  "
                    f"years_on_svt={_years_on_svt:.2f}"
                )
            elif _svt_refix_top is not None:
                # Written only with the switch on and a contact answered, so off is byte-identical.
                _svt_decisions[-1]["sim_refix"] = (
                    _splice_a_refix(cid, term_start_str, term_end_str, _stint_start, commodity)
                    if _svt_roll < _svt_refix_top else None
                )
        # Read BEFORE the overwrite: the renewal roll below asks what this term converted FROM.
        _previous_tariff_type = _last_tariff_type.get(cid)
        _last_tariff_type[cid] = term_tariff_type
        _previous_term_spliced = _last_term_spliced.get(cid, False)
        _last_term_spliced[cid] = _spliced

        # ACCOUNT STATE, WRITTEN FOR EVERY TERM AND NOT ONLY FOR THE ONES THAT RENEWED.
        # Placed HERE, above the renewal gate, for two reasons that are both properties and not
        # conveniences: it is outside every branch below, so no future narrowing of the renewal
        # gate can quietly narrow the book's own record; and it is above
        # `settled_fold.add(settled_this_term)` at the foot of this loop, so the EAC estimate sees
        # the twelve months BEFORE this term and never the term itself.
        _state_unit_rate = unit_rate if isinstance(unit_rate, (int, float)) else None
        # PER FUEL. The dispatch and the reason it exists are in `_account_state_svt_rate`, module
        # level, because the only route to this line is a decade-long run and a branch no control
        # can reach is a branch that goes wrong quietly.
        _state_svt_rate = _account_state_svt_rate(commodity, term_start_str)
        _state_rate_vs_svt_pct = (
            round((_state_unit_rate - _state_svt_rate) / _state_svt_rate * 100.0, 2)
            if _state_unit_rate is not None and _state_svt_rate else None
        )
        _account_state_row = {
            "customer_id": cid,
            "billing_account": billing_account,
            "commodity": commodity,
            "term_start": term_start_str,
            "term_end": term_end_str,
            "term_index": term_index,
            "tariff_type": term_tariff_type,
            "unit_rate_gbp_per_mwh": _state_unit_rate,
            "svt_rate_gbp_per_mwh": _state_svt_rate,
            "rate_vs_svt_pct": _state_rate_vs_svt_pct,
            "company_eac_kwh": round(_company_eac_estimate(cid, term_start_str, settled_fold, commodity)),
            # THE PORTFOLIO POSITION, WRITTEN FOR EVERY TERM AND NOT ONLY THE ONES IT MOVED.
            # `dynamic_pricing_log` records these two only where the premium cleared 1e-6 and
            # changed a rate, which made a continuously-held reading look like an event: 149 of
            # 164 households carried them, and the fifteen missing were accounts whose premium
            # rounded to nothing, not accounts the company had no position on. `None` where the
            # supplier has no completed term of this commodity yet — an honest absence, and the
            # one case where there genuinely is no reading to record.
            "mean_recent_margin_rate": (
                _position["mean_recent_margin_rate"] if _position else None
            ),
            "portfolio_premium_pct": (
                _position["portfolio_premium_pct"] if _position else None
            ),
            "data_regime": "historical",
        }
        account_state_log.append(_account_state_row)
        # C34's riding leg: a dual household's other fuel, priced on the start its roll was decided
        # on (`X` pops before `Xg`), joins the household's decision. A household that left at the
        # roll never prices it, and is decided on one leg.
        if (_renewal_advice is not None and commodity != _decision_leg
                and _state_unit_rate is not None):
            _renewal_advice.observe_riding_leg(
                account_id=billing_account, term_start=term_start_str, fuel=commodity,
                monthly_margin_gbp=term_contribution_per_month(
                    unit_rate_gbp_per_mwh=_state_unit_rate, term_start=term_start_str,
                    company_forward_per_mwh=term.get("company_forward_price_gbp_per_mwh"),
                    locked_policy_cost_per_mwh=term.get("locked_policy_cost_gbp_per_mwh"),
                    locked_network_cost_per_mwh=term.get("locked_network_cost_gbp_per_mwh"),
                    company_eac_kwh=_account_state_row["company_eac_kwh"], fuel=commodity),
                renewal=_renewal_terms(commodity, term_start_str, _state_unit_rate,
                                       _account_state_row["company_eac_kwh"]))
        # C29: EVERY domestic leg the supplier bills is on the book `engagement_at` fits, not only
        # the ones that reached a renewal offer. Enrolled at the offer instead, a household that
        # rolled to the default was never asked for and the book held only choosers: every
        # channel rate read 1.0 (2016-2020 smoke run, 2026-10-05).
        if policy.retention_weighs_engagement:
            _enrolled = next(
                (c for c in _known_customers() if c["customer_id"] == billing_account), None)
            if (_enrolled or {}).get("segment", "resi") == "resi":
                from company.interfaces.sim_interface import LiveSimInterface
                _engagement_channels[cid] = LiveSimInterface().get_payment_method(
                    billing_account, commodity, as_of=term_start_str)

        _renewal_event_this_term = None
        if (term_index >= 1 and commodity == _decision_leg and not _indexed_tariff
                and not term.get(_WOKEN_REFIX)):
            company_est_pre = None
            _retention_offer = None
            _holdout_arm = None
            _holdout_would_offer = False
            _no_offer_reason = "below_threshold"
            _would_be_discount_pct = None
            _bill_shock_this_term = False
            # Phase 33: active/passive renewal split. Default True until we know the rate.
            active_renewal = True
            passive_cap = None
            _engagement_level_str = None
            # PB7: the company's own record of how this account pays, resolved once per term and
            # reset here every term. Initialised at this level rather than inside the branch below
            # because the DEPARTURE booking further down is outside that branch -- a name left over
            # from the previous iteration would book one customer's channel against another's loss.
            _company_payment_method = None
            # HOISTED OUT OF THE BRANCH BELOW (2026-09-19) because the churn-journey REGISTRATION
            # that used it is now needed at a second site -- the `advance` call at the end of this
            # block, which is NOT inside the branch. Same expression, same inputs, no side effects:
            # a lookup over a list and a date subtraction. See the registration guard beside that
            # advance for what it is for.
            acq_date_for_est = next(
                (c["acquisition_date"] for c in _known_customers()
                 if c["customer_id"] == billing_account),
                term_start_str,
            )
            tenure_for_est = (
                date.fromisoformat(term_start_str) - date.fromisoformat(acq_date_for_est)
            ).days / 365.25
            if old_decision_leg_rate is not None:
                # Phase 2 Layer 1 (CORE_FIDELITY_PHASES.md): each household's
                # engagement archetype is a persistent trait (keyed on the
                # stable billing_account, not per-term_index), not a fresh
                # coin-flip every renewal -- the population-weighted
                # aggregate still reproduces the existing anchored ~35% rate.
                from simulation.household_segments import (
                    active_renewal_probability_at_a_decision,
                    engagement_level_for_customer,
                )
                _engagement_level = engagement_level_for_customer(billing_account)
                _engagement_level_str = _engagement_level.value
                # Phase 27e: I&C segment uses broker-driven churn model
                cust_for_churn = next(
                    (c for c in _known_customers() if c["customer_id"] == billing_account), None
                )
                segment_for_churn = cust_for_churn.get("segment", "resi") if cust_for_churn else "resi"
                # THE SCHEDULE ALREADY ASKED THIS, on this seed, for a resi household: it is why
                # this term is fixed and not an SVT stint. Asked with the same probability, so the
                # answer is the same one (PB6, 2026-09-29) -- see
                # `active_renewal_probability_at_a_decision` for the band it used to disagree in.
                active_renewal = rolls_active_renewal(
                    term_start_str, f"{billing_account}_{term_index}",
                    active_renewal_probability_at_a_decision(billing_account, segment_for_churn),
                )
                passive_cap = passive_churn_cap_for(active_renewal)
                # Phase 15d: pass previous-term hedge fraction — well-hedged customers
                # experienced stable prices, making them less rate-sensitive at renewal.
                prev_hf = current_hf.get(cid, 0.0)
                hangover_periods = hangover_remaining.get(cid, 0)
                # Phase 23a: company estimates EAC from observable prior-year billing
                _volume = _company_volume_reading(cid, term_start_str, settled_fold, commodity)
                company_eac = _volume["kwh"]
                # GRADED AGAINST THE YEAR THAT FOLLOWS, filled in after the run
                # (`_grade_demand_estimates_against_the_year_ahead`). Until 2026-10-11 `true_eac`
                # was the run-average settled year to date and `company_eac` the trailing settled
                # year: two backward reads of one fold, published as forecast accuracy.
                demand_estimation_log.append({
                    "customer_id": cid,
                    "commodity": commodity,
                    "term_start": term_start_str,
                    "company_eac_kwh": round(company_eac),
                    "true_eac_kwh": None,
                    "error_pct": None,
                    "source": "prior_billing" if _volume["basis"] == "annualised_advance" else "fallback",
                })
                # PB7: THE OBSERVABLE THE COMPANY ALREADY HAS A SEAM FOR, ACTUALLY HANDED OVER.
                # `SimInterface.get_payment_method` has exposed this since PB6 and no run passed
                # it, so `payment_method_engagement_factor` returned 1.0 on every account in every
                # run and the coefficient PB6 landed reached nothing. Resi-only: an I&C account
                # pays by BACS or CHAPS and the CIM survey's household banners say nothing about it.
                # READ THROUGH THE SEAM, not from `payment_channel_for_customer` (2026-09-29). The
                # value is the same today; the route is not -- anything the seam later models (a
                # CRM miss, a method changed mid-tenure) would otherwise never reach a run.
                if segment_for_churn == "resi":
                    from company.interfaces.sim_interface import LiveSimInterface
                    _company_payment_method = LiveSimInterface().get_payment_method(
                        billing_account, commodity, as_of=term_start_str)
                # THE COMPANY'S OWN RECEIVABLE, ASKED FOR AT THE RENEWAL (2026-09-25). The
                # distress term in `churn_model` used to be a knee on the household's BILL, and
                # the bill is the wrong variable: Ofgem/BMG puts the bill-to-switching
                # correlation at -0.07 to +0.05, and DESNZ QEP 2.7.1 has switching COLLAPSING in
                # the year every bill rose. What Ofgem CIM w6 Table 56 does establish is a
                # position on the supplier's own ARREARS -- 1.28x the population switching rate
                # for a household whose arrears are getting harder, 0.79x for one with no debt.
                #
                # `_payment_triad` has been posting this company's bills and its observed cash
                # into the company's own ledger all run, so the position is a read and not an
                # estimate. ASKED THROUGH THE DOOR, never by reaching for the consumer: the
                # triad hands back a STATE string, exactly as `detection_cells` hands back
                # numbers, and no company object crosses. Nothing here consults
                # `simulation/arrears_engine` -- that is the world's arrears, and reading it
                # would turn an inference the supplier genuinely has into access it does not.
                #
                # NO LOOK-AHEAD: this renewal is decided before this term's own bills are
                # settled below, so the ledger it reads holds only what was billed and observed
                # BEFORE `term_start_str`. An account this run has not billed yet reads
                # `unknown`, which leaves the estimate bit-for-bit as it was.
                _company_arrears_state = _payment_triad.arrears_state(
                    cid, date.fromisoformat(term_start_str), segment=segment_for_churn,
                )
                # Phase 33: passive renewers use SVT-inertia constants; active use full model.
                # I&C customers are always active (brokers shop every renewal — no passive roll).
                _renewal_year = int(term_start_str[:4])
                _ending_term_type = (
                    ending_term_type(_previous_tariff_type,
                                     previous_term_spliced=_previous_term_spliced,
                                     default_tariff_type=SVT_TARIFF_TYPE)
                    if policy.renewal_belief_by_ending_term else None)
                # Phase QK: signal collection (shock count, behaviour score, satisfaction
                # decay/record) runs for EVERY renewal, not just active ones -- these are
                # observable state updates independent of which estimate formula applies.
                # Previously gated behind the active/I&C branch, so a passive-rolling
                # customer's satisfaction/shock tracking was frozen and never fed into
                # their estimate -- the root cause of the churn classifier's structural
                # recall=0%/precision=0% (docs/staging/EVIDENCE_IN_BUSINESS_SURFACES.md).
                _nd_shock_count = _rate_shock_counts.get(cid, 0)
                # Phase NH: payment behaviour score from observable payment history
                _nh_behaviour_score = _cx_desk.account_payment_behaviour_score(
                    _supply_points_of_account.get(billing_account, (cid,)))
                if _churn_journey_register.get_journey(billing_account) is None:
                    _churn_journey_register.register_customer(
                        billing_account, tenure_years=tenure_for_est, churn_threshold=50.0,
                    )
                if old_decision_leg_rate > 0 and unit_rate / old_decision_leg_rate - 1 > _NG_BILL_SHOCK_THRESHOLD:
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
                    old_rate_gbp_per_mwh=old_decision_leg_rate,
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
                    payment_method=_company_payment_method,
                    arrears_state=_company_arrears_state,
                    # B8: the company's own facts about this renewal, so it can learn its price
                    # response: which account, which day, which fuel.
                    account_id=billing_account,
                    term_start=term_start_str,
                    fuel=commodity,
                    # The company's own book, before the roll; None on every standing policy.
                    ending_term_type=_ending_term_type,
                ))
                if hangover_periods > 0:
                    hangover_remaining[cid] = hangover_periods - 1
                # C34 at the renewal notice: our contribution on the offered rate (net of the
                # term's pass-through costs and cost to serve, §6.1), the company's own belief.
                if _renewal_advice is not None and segment_for_churn == "resi":
                    _renewal_advice.observe_roll(
                        account_id=billing_account, term_start=term_start_str, fuel=commodity,
                        monthly_margin_gbp=term_contribution_per_month(
                            unit_rate_gbp_per_mwh=unit_rate, term_start=term_start_str,
                            company_forward_per_mwh=term.get("company_forward_price_gbp_per_mwh"),
                            locked_policy_cost_per_mwh=term.get("locked_policy_cost_gbp_per_mwh"),
                            locked_network_cost_per_mwh=term.get("locked_network_cost_gbp_per_mwh"),
                            company_eac_kwh=company_eac, fuel=commodity),
                        renewal_churn_belief=company_est_pre,
                        renewal=_renewal_terms(commodity, term_start_str, unit_rate, company_eac))
                    # C34'S PRICE HALF (2026-10-24): the rise the desk priced is billed on the fix,
                    # before the world's roll is asked, so the household answers the raised price.
                    if policy.renewal_rate_bills_the_shared_rise:
                        _rise, _rise_why = _renewal_advice.rise_at_notice(
                            account_id=billing_account, term_start=term_start_str)
                        _rise_terms = _renewal_terms(commodity, term_start_str, unit_rate, company_eac)
                        _struck_rate = unit_rate
                        unit_rate, _billed_why = bill_the_shared_rise(
                            unit_rate_gbp_per_mwh=unit_rate,
                            rise_gbp_per_month=None if _rise is None else _rise.rise_gbp_per_month,
                            annual_mwh=_rise_terms.annual_mwh,
                            headroom_gbp_per_month=_rise_terms.headroom_gbp_per_month())
                        shared_rise_log.append({
                            "account_id": billing_account, "term_start": term_start_str,
                            "fuel": commodity, "struck_unit_rate_gbp_per_mwh": round(_struck_rate, 4),
                            "billed_unit_rate_gbp_per_mwh": round(unit_rate, 4),
                            "rise_gbp_per_month": None if _rise is None else _rise.rise_gbp_per_month,
                            "reason": _billed_why if _rise is not None else f"{_billed_why}: {_rise_why}",
                        })
                        if unit_rate != _struck_rate:
                            _prior_rates[cid] = unit_rate
                            _account_state_row["unit_rate_gbp_per_mwh"] = unit_rate
                            _account_state_row["rate_vs_svt_pct"] = (
                                round((unit_rate - _state_svt_rate) / _state_svt_rate * 100.0, 2)
                                if _state_svt_rate else None)
                if company_est_pre > RETENTION_THRESHOLD:
                    eac_for_ret = company_eac  # Phase 23a: use company estimate
                    # B8 Q5: sized against the best published deal on the day, as the save is, or
                    # by the churn-belief tiers; either way no deeper than the re-fix's own cost
                    # floor. None = no cut left to give (the match: our re-fix already meets it).
                    _cut_inputs = _price_match_inputs(term, commodity, term_start_str, company_fwd)
                    if policy.retention_cut_sizing == "price_match":
                        _cut = retention_cut_share_at_price_match(unit_rate, **_cut_inputs)
                    elif policy.retention_cut_sizing == "risk_tiers":
                        _cut = retention_cut_share_at_risk_tiers(
                            unit_rate, policy.retention_discount_for_risk(company_est_pre),
                            cost_floor=_cut_inputs["cost_floor"])
                    else:
                        raise ValueError(f"retention_cut_sizing {policy.retention_cut_sizing!r} "
                                         "is neither 'risk_tiers' nor 'price_match'")
                    discount_pct = 0.0 if _cut is None else _cut
                    _market_beats_the_fix = _cut is not None
                    _would_be_discount_pct = discount_pct
                    ret_cost = unit_rate * discount_pct * eac_for_ret / 1000.0
                    # What retaining protects is the term's contribution, not the spread over
                    # wholesale, which still carries the pass-through costs (§6.1, 2026-10-20).
                    # None only where the term has no floor, and then both sizings gave no cut.
                    expected_margin = term_contribution_per_year(
                        unit_rate_gbp_per_mwh=unit_rate, term_start=term_start_str,
                        company_forward_per_mwh=term.get("company_forward_price_gbp_per_mwh"),
                        locked_policy_cost_per_mwh=term.get("locked_policy_cost_gbp_per_mwh"),
                        locked_network_cost_per_mwh=term.get("locked_network_cost_gbp_per_mwh"),
                        company_eac_kwh=eac_for_ret, fuel=commodity, segment=segment_for_churn)
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
                    # C29: worth protecting only in proportion to the chance this household looks
                    # at all. Its own term record, as the book stood the day before, through
                    # the growth desk; `None` (no record yet, or I&C) leaves today's guard.
                    _engagement = retention_engagement(
                        cid, term_start_str, terms=account_state_log,
                        departures=customer_events_log,
                        channel_by_account=_engagement_channels, fuel=commodity,
                        contract_length_days=CONTRACT_LENGTH_DAYS,
                    ) if policy.retention_weighs_engagement else None
                    # THE COMPANY'S OWN BAD-DEBT BELIEF ON THE TERM IT PROTECTS (2026-10-07). The
                    # payment score lifts a debtor's churn belief over the threshold above; valued
                    # as if it pays, the discount then goes to the worst payers. The rate is the one
                    # the renewal chain already read for this leg and date; on a run that priced on
                    # the segment table, or a spliced term, the guard asks the book itself.
                    _ret_default_belief = None
                    if policy.retention_nets_bad_debt and segment_for_churn == "resi":
                        _ret_default_belief = (
                            _chain_default_belief if _chain_default_belief is not None
                            else _payment_triad.default_belief_rate(
                                date.fromisoformat(term_start_str), _company_arrears_state,
                                payment_method_of=_book_method_of))
                    _ret_billed = unit_rate * eac_for_ret / 1000.0
                    # AT A TERM THE WORLD DOES NOT ROLL, ONLY A CONVERSION CAN BE BOUGHT (2026-10-10).
                    # The household is on our default tariff, so its exits were carried there; the
                    # offer can only turn a fix it would decline into one it takes. The company asks
                    # that of its own fix, its own discount and the published default.
                    _offer_can_buy = _market_beats_the_fix and (
                        not policy.retention_offers_at_default_anniversary_only_where_the_discount_wins
                        or retention_offer_can_buy_anything(
                            previous_term_on_our_default=(
                                _previous_tariff_type == SVT_TARIFF_TYPE),
                            full_position_vs_default=_offer_vs_default,
                            offered_position_vs_default=(
                                position_vs_default(offered_rate(unit_rate, discount_pct),
                                                    term_start_str, commodity=commodity)
                                if _offer_vs_default is not None else None)))
                    # B8 L3: on a policy that runs the holdout, the company's own coin holds half
                    # the renewals an offer could buy anything at out, and its own interval, once
                    # decided, replaces the guard below on the rest. `_cut_decision` None on the
                    # treated arm = still learning.
                    _cut_decision = None
                    if _offer_can_buy and _retention_holdout is not None:
                        _holdout_arm, _cut_decision = _retention_holdout.decide(
                            account_id=billing_account, event_date=term_start_str,
                            payment_method=_company_payment_method,
                            term_margin_gbp=expected_margin, term_billed_gbp=_ret_billed,
                            billed_kwh=eac_for_ret, cut_gbp_per_mwh=unit_rate * discount_pct,
                            # Q8: valued at its own stay belief, on the published prior (C8).
                            stay_belief=1.0 - company_est_pre,
                            # Q10: a row's outcome is read at its window from the company's own
                            # loss notices, so a departure months after the renewal is the row's.
                            losses_notified=_change_of_supplier_register.losses_notified())
                        retention_holdout_log.append({
                            "customer_id": billing_account, "event_date": term_start_str,
                            "arm": _holdout_arm, "payment_method": _company_payment_method,
                            "discount_pct": discount_pct,
                            "decided": _cut_decision is not None,
                            "offer_cut": None if _cut_decision is None else _cut_decision.offer_cut,
                            "reason": None if _cut_decision is None else _cut_decision.reason,
                            "outcome_window_days": _retention_holdout.outcome_window_days,
                        })
                    # One reading of the guard, so the gate's record below is the guard's own verdict.
                    _value_protected = retention_value_protected(
                        expected_margin, acq_cost_saved, _engagement,
                        default_belief_rate=_ret_default_belief, billed=_ret_billed)
                    # (2026-10-22) Weighed by the chance the offer saves anything: the belief x the
                    # company's own save rate on past offers ending this type of term.
                    _save_rate = None
                    _save_rate_refusal = None
                    if policy.retention_offers_on_the_save_rate_lower_bound:
                        # (2026-10-22) Only on what the holdout can show: the interval's lower
                        # bound must pay, and an unlearned rate offers nothing (prereg §16).
                        _value_protected, _interval, _save_rate_refusal, _save_rate_reason = (
                            retention_value_at_save_rate_lower_bound(
                                _value_protected, belief=company_est_pre,
                                ending_term_type=_ending_term_type, renewal_year=_renewal_year,
                                offer_cost=ret_cost))
                        _save_rate = None if _interval is None else _interval[1]
                        retention_save_rate_lower_bound_log.append({
                            "customer_id": billing_account, "event_date": term_start_str,
                            "ending_term_type": _ending_term_type,
                            "company_churn_estimate": company_est_pre,
                            "save_rate_interval": (None if _interval is None
                                                   else [round(v, 4) for v in _interval]),
                            "offer_cost_gbp": round(ret_cost, 2),
                            "refusal": _save_rate_refusal, "reason": _save_rate_reason,
                        })
                    elif policy.retention_weighs_save_odds:
                        _value_protected, _save_rate, _save_rate_reason = (
                            retention_value_weighed_by_save_odds(
                                _value_protected, belief=company_est_pre,
                                ending_term_type=_ending_term_type, renewal_year=_renewal_year))
                    # Whether it WOULD offer is read before the coin matters, on both arms: only
                    # those renewals are the experiment, so a row is due on either arm exactly then.
                    _would_offer = _value_protected is not None and (
                        _retention_holdout.would_offer(_cut_decision, _value_protected > ret_cost)
                        if _retention_holdout is not None else _value_protected > ret_cost)
                    _holdout_would_offer = _holdout_arm is not None and _would_offer
                    if _holdout_arm is not None:
                        retention_holdout_log[-1]["would_offer"] = _would_offer
                    if not _market_beats_the_fix:
                        _no_offer_reason = (
                            "the_fix_already_meets_the_best_published_deal"
                            if policy.retention_cut_sizing == "price_match"
                            else "the_fix_has_no_room_above_its_cost_floor")
                    elif not _offer_can_buy:
                        _no_offer_reason = "the_discount_cannot_win_the_fix"
                        retention_gate_value_test_log.append({
                            "customer_id": billing_account, "event_date": term_start_str,
                            # None where the lower-bound guard refused (prereg §16).
                            "value_protected_gbp": (None if _value_protected is None
                                                    else round(_value_protected, 2)),
                            "offer_cost_gbp": round(ret_cost, 2),
                            "value_test_would_offer": (_value_protected is not None
                                                       and _value_protected > ret_cost),
                            # On a holdout policy the coin, not this test, would have decided
                            # half of them first; the verdict here is the guard's alone.
                            "holdout_would_have_drawn": _retention_holdout is not None,
                        })
                    elif (_would_offer and _holdout_arm != "holdout"
                          and policy.retention_save_rate_learned_against_holdout
                          and retention_save_holdout_draws(billing_account, term_start_str)):
                        # (2026-10-22) THE SAVE RATE'S OWN HOLDOUT: a renewal the guard would offer
                        # on, held out by the company's coin, so the save rate can be read as the
                        # holdout's losses against the offered ones (prereg §15).
                        _no_offer_reason = "held_out_to_learn_the_save_rate"
                        book_retention_holdout(
                            renewal_year=_renewal_year, ending_term_type=_ending_term_type,
                            account_id=billing_account, belief=company_est_pre)
                        retention_save_holdout_log.append({
                            "customer_id": billing_account, "event_date": term_start_str,
                            "commodity": commodity, "ending_term_type": _ending_term_type,
                            "company_churn_estimate": company_est_pre,
                            "retention_cost_gbp_not_spent": ret_cost,
                        })
                    elif _holdout_arm != "holdout" and _would_offer:
                        # THE OFFER REACHES THE WORLD AS ITS RATE (director, 2026-10-09), answered
                        # at the roll below by `simulation.retention_offer`. It reached it as a flat,
                        # unsourced 0.20 cut to one hazard whatever the discount, so a 3% and an 8%
                        # offer retained alike. Nudge Physics Layer 1: framing_type is the company's
                        # own comms-cohort choice; the multiplier is SIM ground truth (the sourced
                        # relative uplift on a matched framing) scaling the offered rate's effect.
                        _framing_type = framing_type_for(policy, billing_account, term_start_str)
                        _framing_multiplier = framing_effectiveness_multiplier(billing_account, _framing_type)
                        _retention_offer = (discount_pct, _framing_multiplier,
                                            _cut_inputs["cost_floor"])
                        retention_cost_events.append(
                            book_retention_cost(
                                billing_account=billing_account,
                                event_date=term_start_str,
                                cost_gbp=ret_cost,
                                company_churn_estimate=company_est_pre,
                            )
                        )
                        if policy.retention_weighs_save_odds:
                            book_retention_offer(
                                renewal_year=_renewal_year, ending_term_type=_ending_term_type,
                                account_id=billing_account, belief=company_est_pre)
                        retention_log.append({
                            "customer_id": billing_account,
                            "event_date": term_start_str,
                            "company_churn_estimate": company_est_pre,
                            "discount_pct": discount_pct,
                            "offered_unit_rate_gbp_per_mwh": offered_rate(unit_rate, discount_pct),
                            "retention_cost_gbp": ret_cost,
                            "expected_term_margin_gbp": expected_margin,
                            "acq_cost_saved_gbp": round(acq_cost_saved, 2),
                            "assumed_deferral_months": ASSUMED_DEFERRAL_MONTHS,
                            "framing_type": _framing_type,
                            "outcome": "pending",
                            **({"engagement_estimate": round(_engagement, 4)}
                               if _engagement is not None else {}),
                            **({"save_rate": round(_save_rate, 4)}
                               if _save_rate is not None else {}),
                            **({"bad_debt_charge_gbp": round(retention_bad_debt_charge(
                                _ret_default_belief, _ret_billed), 2)}
                               if _ret_default_belief is not None else {}),
                        })
                    else:
                        _no_offer_reason = (
                            "held_out" if _holdout_arm == "holdout" and _would_offer
                            else _save_rate_refusal or "uneconomical")
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
            _nf_shock_count = _rate_shock_counts.get(cid, 0)
            _nf_tenure = (
                (date.fromisoformat(term_start_str) - date.fromisoformat(acq_date_for_est)).days / 365.25
                if old_decision_leg_rate is not None else term_index * 0.5
            )
            # Real payment-method satisfaction gap + per-customer heterogeneity
            # (2026-07-10, ASSUMPTIONS.md "Customer Satisfaction Population
            # Distribution") -- resi-only, matching the existing
            # payment_channel_for_customer() convention (I&C/SME use bacs/chaps).
            _nf_payment_channel = None
            if segment_for_churn == "resi":
                from simulation.household_segments import payment_channel_for_customer
                # THE FUEL THIS DECISION IS BEING TAKEN ON, not the literal `"electricity"` it
                # said until 2026-09-16. `payment_channel_for_customer` is keyed on (customer,
                # fuel) BY DESIGN — the DD anchor is 72% electricity against 75% gas — so asking
                # it about electricity for a household that holds no electricity leg returned a
                # channel drawn off a supply point that does not exist. Inside this branch
                # `commodity` IS the decision leg, so on every account that has one this is the
                # same lookup it always was.
                _nf_payment_channel = payment_channel_for_customer(billing_account, commodity)
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

            def _book_complaint(_outcome, _about_bill_shock):
                _book_complaint_for(cid, billing_account, term_start_str, _outcome,
                                    _about_bill_shock)

            if _complaint_outcome.occurred:
                _book_complaint(_complaint_outcome, _bill_shock_this_term)
            _perceived_bill_saving_gbp = (
                max(0.0, unit_rate - old_decision_leg_rate) * (company_eac / 1000.0)
                if old_decision_leg_rate else 0.0
            )
            # A TERM CAN REACH THIS ADVANCE HAVING NEVER STRUCK A RATE, AND UNTIL 2026-09-19 THAT
            # RAISED KeyError AND KILLED THE RUN. The registration above sits inside
            # `if old_decision_leg_rate is not None:`; this call is outside it, so the pairing held
            # only while every account's decision leg opened on a product with a struck rate. An
            # account that opens on the DEFAULT TARIFF has no rate to carry forward, reaches its
            # first in-window term unregistered, and dies here -- which is exactly what the C6
            # arrival producer began minting on 2026-09-19 (`simulation/arrival_route.py`), 989s
            # into a value-arm pass, on SYN-2016-008.
            #
            # INERT FOR EVERY WORLD THAT COMPLETES TODAY, which is the argument for fixing it here
            # rather than in the producer: an account reaching this line unregistered RAISED, so
            # this branch is reachable only in worlds that currently cannot finish at all. It
            # cannot move a published figure.
            if _churn_journey_register.get_journey(billing_account) is None:
                _churn_journey_register.register_customer(
                    billing_account, tenure_years=tenure_for_est, churn_threshold=50.0,
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
            # A household converting OFF the SVT has no renewal-point exit: C1b's inertia hazard
            # above already carried its exits for every SVT segment (`departure_rolled_at_renewal`).
            _rolled = departure_rolled_at_renewal(_previous_tariff_type)
            # THE ROLL'S ARGUMENTS ARE KEPT so a save offer can re-ask the same household on the
            # same roll at one other price (`simulation/save_on_loss_notice.py`). Built only when
            # it rolls, exactly as the call alone was.
            _roll_kwargs = dict(
                # This household's records only: the roll reads nothing else, and copying the
                # whole book into it per renewal was the quadratic term (see the function).
                records_so_far=households_own_records(billing_account, all_records),
                customers=_known_customers(),
                old_rate_gbp_per_mwh=old_decision_leg_rate,
                new_rate_gbp_per_mwh=unit_rate,
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
            ) if _rolled else None
            event = (roll_lifecycle_event(cid, term_start_str, commodity, **_roll_kwargs)
                     if _rolled else None)
            # A RETENTION OFFER IS A PRICE, so the world answers it at that price on the same roll
            # (`simulation/retention_offer.py`), and the household that stays is SUPPLIED at it: the
            # discount is the company's cost through the term's revenue. Until 2026-10-09 the kept
            # term was billed at the full rate, and `retention_cost_events` never reaches the P&L
            # (`test_retention_cost_events_are_minted_but_never_reach_the_pnl`), so the run's book
            # was never charged a penny for an offer. The decision leg only, as the save's cut.
            if _retention_offer is not None:
                _event_at_full_rate = event
                _full_position_vs_default = _offer_vs_default
                event = ask_world_at_offer(
                    roll_lifecycle_event, cid, term_start_str, commodity, _roll_kwargs or {},
                    event, discount_pct=_retention_offer[0],
                    framing_multiplier=_retention_offer[1])
                _refix_rate = unit_rate
                unit_rate = offered_rate(unit_rate, _retention_offer[0])
                # THE CLASS, asked of the rate the household is actually offered: the tier cut sold
                # under cost after the chain's own check had returned (95b3a38d2).
                refuse_retention_offer_below_own_cost_floor(
                    unit_rate, entered=_refix_rate, cost_floor=_retention_offer[2],
                    where=f"{billing_account} {commodity} {term_start_str}")
                _prior_rates[cid] = unit_rate
                _account_state_row["unit_rate_gbp_per_mwh"] = unit_rate
                _account_state_row["rate_vs_svt_pct"] = (
                    round((unit_rate - _state_svt_rate) / _state_svt_rate * 100.0, 2)
                    if _state_svt_rate else None)
                if _offer_vs_default is not None:
                    _offer_vs_default = position_vs_default(
                        unit_rate, term_start_str, commodity=commodity)
                # WHAT THE OFFER CHANGED, read world-side for the harness and by no company code
                # (prereg §13/§15): a departure (the household left at the full rate and stays at
                # the offer), a stayer's tariff (it stays either way, and only the discount takes
                # its fix to or below the default), or neither (the discount went to a choice it
                # would have made anyway).
                _left_at_full = (_event_at_full_rate is not None
                                 and _event_at_full_rate["event_type"] == "churned")
                _left_at_offer = event is not None and event["event_type"] == "churned"
                retention_offer_channel_log.append({
                    "customer_id": billing_account, "cid": cid, "event_date": term_start_str,
                    "commodity": commodity,
                    "retention_cost_gbp": retention_log[-1]["retention_cost_gbp"]
                    if retention_log else None,
                    "channel": (
                        "changed_a_departure" if _left_at_full and not _left_at_offer
                        else "changed_a_stayers_tariff" if (
                            not _left_at_full and _full_position_vs_default is not None
                            and _full_position_vs_default > 0
                            and _offer_vs_default is not None and _offer_vs_default <= 0)
                        else "changed_neither"),
                })
                # Its thinner margin does not teach the book's premium, for the reason a save's
                # does not (director, 2026-10-08): stayers must not pay for the discount.
                _held_on_a_save = event is None or event["event_type"] == "renewed"
            # THE DEBT OBJECTION IS THE COMPANY'S (SLC 14, EP12). A domestic household's switch
            # request reaches the company, which answers it from its own ledger and method register;
            # an objection cancels the switch. The world drew this block itself until 2026-10-25.
            if (event is not None and event["event_type"] == "churned"
                    and segment_for_churn == "resi" and debt_objection_active()):
                _request_day = objection_request_day(date.fromisoformat(term_start_str))
                _owed = _payment_triad.receivable(billing_account, _request_day)
                _objection = request_debt_objection(
                    _transfer_objection_register, billing_account, _request_day.isoformat(),
                    None if _owed is None else _owed["unpaid_bills_by_age"],
                    prepayment=_book_method_of(billing_account, _request_day) == "prepayment",
                    fuels=len(_fuels_of_household.get(household_of(cid), ())) or 1)
                event = apply_objection(event, _objection["objected"])
            _pending_notice_sent = False
            # THE RIVAL NEVER SEES A SAVE (2026-10-14). A save is a reactive price offered only to a
            # household that has already chosen to leave; it is on no tariff list a rival or a
            # comparison site reads. Fed to the rival's ledger, it moved every later household's
            # P(stay) by what the save cost, which is the save reaching the stayers through the world.
            _rate_the_rival_sees = unit_rate
            # A domestic household leaving a FIXED term: a Fixed Retention Tariff is a domestic
            # tariff, and one offered to a household leaving the default tariff is not established
            # as inside the SLC 22B derogation (`simulation/save_on_loss_notice.py`). Measured
            # 2026-10-08: repricing a default-tariff segment moved every gas default price after it.
            if (_save_offers_on and event is not None and event["event_type"] == "churned"
                    and segment_for_churn == "resi" and term_tariff_type == "fixed"):
                # THE SAVE ON THE INVITATION TO INTERVENE (director, 2026-10-08). The world sends
                # the loser its CSS Invitation; the company answers it from what it holds; the
                # household answers the offer on its own roll. Off unless the curriculum says on.
                _points = supply_points_on_supply(
                    billing_account, term_start_str, elec_schedules, gas_schedules,
                    _moved_out_on_by_leg)
                for _wire in _registration_loss_feed.wire_pending_notices_for_departure(
                        _points, term_start_str):
                    _change_of_supplier_register.receive_loss_wire(_wire)
                    _pending_notice_sent = True
                # WHAT THE COMPANY KNOWS OF THIS HOUSEHOLD'S VULNERABILITY is what it disclosed:
                # a PSR-type household that discloses does so on its point's first supplied day
                # (`simulation/vulnerability_state.py`), framed through the seam into the
                # company's own register. Never the latent state.
                _psr_register = None
                if _vulnerability_hidden_state_on:
                    _psr_register = open_priority_services_register()
                    _first_day = min((str(r["settlement_date"])[:10]
                                      for r in _roll_kwargs["records_so_far"]
                                      if r["customer_id"] == cid), default=term_start_str)
                    for _wire in wire_registrations(registration_notices(
                            [(cid, date.fromisoformat(_first_day))], run_base_seed())):
                        _psr_register.receive_registration_wire(_wire)
                _save_inputs = _price_match_inputs(term, commodity, term_start_str, company_fwd)
                if _save_decides_per_household:
                    _household_legs = _household_save_legs(
                        cid, commodity, term, term_start_str, unit_rate, company_fwd, company_eac,
                        _points, elec_schedules, gas_schedules, settled_fold)
                    _household_rates, _known_vulnerable = request_household_save(
                        _change_of_supplier_register, _household_legs, term_start_str,
                        _save_inputs["published_best_deal_gap_share"], policy,
                        psr_register=_psr_register)
                    _save_rate = _household_rates.get(cid)
                else:
                    _save_rate, _known_vulnerable = request_save_offer(
                        _change_of_supplier_register, cid, term_start_str, unit_rate,
                        policy.save_offer_cut_share, psr_register=_psr_register,
                        sizing=policy.save_offer_sizing, **_save_inputs)
                _asked = roll_lifecycle_event(
                    cid, term_start_str, commodity,
                    **{**_roll_kwargs, "new_rate_gbp_per_mwh": _save_rate},
                ) if _save_rate is not None else None
                # At the world's own response the answer IS the re-asked roll; a scaled response
                # (a sensitivity) is decided on the same exact roll by the scaled curve.
                _saved = _asked is not None and (
                    _asked["event_type"] == "renewed" if _save_scale == 1.0
                    else household_takes_save(
                        churn_roll_for_renewal(billing_account, term_start_str),
                        event["effective_retention_probability"],
                        _asked["effective_retention_probability"], _save_scale))
                save_on_loss_notice_log.append({
                    "customer_id": cid, "billing_account": billing_account,
                    "commodity": commodity, "term_start": term_start_str,
                    "invitation_held": _pending_notice_sent,
                    "renewal_unit_rate_gbp_per_mwh": unit_rate,
                    "save_unit_rate_gbp_per_mwh": _save_rate,
                    "price_match_inputs": _save_inputs,
                    "p_stay_at_offer": event["effective_retention_probability"],
                    "p_stay_at_save": (
                        _asked["effective_retention_probability"] if _asked is not None else None),
                    "saved": _saved,
                    "known_vulnerable": _known_vulnerable,
                    "eac_kwh": company_eac,
                } | ({"household_legs": len(_household_legs),
                      "household_save_rates": _household_rates}
                     if _save_decides_per_household else {}))
                if _saved:
                    if _save_decides_per_household:
                        _write_household_save_carry(
                            _household_save_carry, _household_rates, cid, term_start_str)
                    unit_rate = billed_rate_when_saved(unit_rate, _save_rate)
                    _held_on_a_save = True
                    _portfolio_margins.account_held_on_a_save(billing_account)
                    event = {**_asked, "event_type": "renewed", "departure_cause": None,
                             "saved_on_loss_notice": True}
                    if not _indexed_tariff:
                        _prior_rates[cid] = unit_rate
                    _account_state_row["unit_rate_gbp_per_mwh"] = unit_rate
                    _account_state_row["rate_vs_svt_pct"] = (
                        round((unit_rate - _state_svt_rate) / _state_svt_rate * 100.0, 2)
                        if _state_svt_rate else None)
                    # It ANSWERED an offer, so it chose the Fixed Retention Tariff: the decline-and-
                    # stay rule is for a renewal offer the household never answered, and reading it
                    # here would splice a saved household onto the default tariff.
                    _offer_vs_default = None
            _renewal_event_this_term = event
            # DD4b is no longer answered here: a renewal is not the review a default-tariff household
            # meets, and answering both would answer one rise twice. It is answered where the
            # supplier's review is told, in `_post_month_bill`. The departure leg (PB4's shock
            # hazard at this renewal) is unchanged.
            # STAY, LEAVE, OR STAY AND REFUSE. Leaving is the roll's and stands; the rule only
            # reprices a household that stayed.
            _renewal_outcome = renewal_outcome(
                event_type=event["event_type"] if event is not None else "renewed",
                position_vs_default=_offer_vs_default,
            )
            # THE RIVAL SEES THIS OFFER ONLY AFTER THE TERM IT WAS STRUCK IN (2026-08-28, C2).
            # Recorded AFTER the roll, and read back by `position_for()` a quarter later, so no
            # offer can ever reach the reference it is itself being measured against. Recording
            # it before the roll would make the differential partly a function of itself, which
            # is the tautology R15 names first.
            # A REFUSED offer is not a price this supplier holds anyone at, so the rival never
            # sees it: the household is on the default, which is what the ledger must read.
            if _renewal_outcome != RENEWAL_DECLINED_FIX:
                _competitor_position_ledger.observe(term_start_str, _rate_the_rival_sees,
                                                    commodity=commodity)
            # ...but it STAYED, and the record keeps the decision. Appended here and nowhere else:
            # the block below feeds the journey, the retention log and the departure handling, and
            # nothing inside this loop reads `customer_events_log`, so this row changes no outcome.
            if not _rolled and _renewal_outcome == RENEWAL_DECLINED_FIX:
                customer_events_log.append(declined_fix_event(
                    customer_id=billing_account, event_date=term_start_str, commodity=commodity,
                    declined_unit_rate_gbp_per_mwh=unit_rate,
                    position_vs_default=_offer_vs_default,
                    company_churn_estimate=company_est_pre,
                    retention_offered=_retention_offer is not None,
                    retention_withheld_because=(
                        _no_offer_reason if _retention_offer is None else None),
                    is_active_renewal=active_renewal,
                    engagement_level=_engagement_level_str,
                ))
            elif not _rolled:
                customer_events_log.append(svt_conversion_event(
                    customer_id=billing_account, event_date=term_start_str, commodity=commodity,
                    company_churn_estimate=company_est_pre,
                    retention_offered=_retention_offer is not None,
                    retention_withheld_because=(
                        _no_offer_reason if _retention_offer is None else None),
                    is_active_renewal=active_renewal,
                    engagement_level=_engagement_level_str,
                    unit_rate_gbp_per_mwh=unit_rate,
                ))
            _record_renewal_decision(
                _journey, renewal_decisions_log, customer_id=billing_account,
                event_date=term_start_str, commodity=commodity, rolled=_rolled, event=event,
            )
            # B8 L3: a row on either arm exactly where the company would have offered.
            if _holdout_would_offer:
                _retention_holdout.record(
                    account_id=billing_account, event_date=term_start_str, arm=_holdout_arm,
                    stayed=not (event is not None and event["event_type"] == "churned"),
                    payment_method=_company_payment_method,
                    saved_on_loss_notice=bool(event is not None and event.get("saved_on_loss_notice")),
                    renewal=(
                        "left_at_decision" if event is not None and event["event_type"] == "churned"
                        else "declined_fix_on_default" if _renewal_outcome == RENEWAL_DECLINED_FIX
                        else "re_fixed"),
                    supply_points=_supply_points_of_account.get(billing_account, (cid,)),
                    cut_gbp=ret_cost)
                retention_holdout_log[-1]["stayed_at_decision"] = (
                    _retention_holdout.rows[-1]["stayed_at_decision"])
                retention_holdout_log[-1]["renewal"] = _retention_holdout.rows[-1]["renewal"]
            if event is not None:
                event["is_active_renewal"] = active_renewal
                # Phase 2 Layer 1: SIM-internal ground truth, retained here for
                # evidence-surface use only (same pattern as credit_bureau_true_
                # creditworthy) -- demonstrates the persistent archetype trait
                # across a household's renewal history. MUST NEVER be read by
                # company/** decision code.
                event["engagement_level"] = _engagement_level_str
                event["unit_rate_gbp_per_mwh"] = unit_rate
                if _renewal_outcome == RENEWAL_DECLINED_FIX:
                    event = declined_fix_event(
                        customer_id=cid, event_date=term_start_str, commodity=commodity,
                        declined_unit_rate_gbp_per_mwh=unit_rate,
                        position_vs_default=_offer_vs_default, rolled_event=event,
                    )
                customer_events_log.append(event)
                if _retention_offer is not None and retention_log:
                    outcome_str = "churned_despite_offer" if event["event_type"] == "churned" else "retained"
                    retention_log[-1]["outcome"] = outcome_str
                    nudge_physics_log.append({
                        "customer_id": billing_account,
                        "event_date": term_start_str,
                        "framing_type": retention_log[-1].get("framing_type"),
                        "susceptibility": susceptibility_for(billing_account).value,
                        "effectiveness_multiplier": round(_retention_offer[1], 4),
                        "outcome": outcome_str,
                    })
                if event["event_type"] == "churned":
                    if _retention_offer is None:
                        # No offer was made — record as missed retention opportunity
                        eac_missed = company_eac  # Phase 23a: use company estimate
                        no_offer_churn_log.append({
                            "customer_id": billing_account,
                            "event_date": term_start_str,
                            "company_churn_estimate": company_est_pre,
                            # The guard's own value. None only where a fixed term records no
                            # locked costs, which no renewal route writes today.
                            "expected_term_margin_gbp": term_contribution_per_year(
                                unit_rate_gbp_per_mwh=unit_rate, term_start=term_start_str,
                                company_forward_per_mwh=term.get(
                                    "company_forward_price_gbp_per_mwh"),
                                locked_policy_cost_per_mwh=term.get(
                                    "locked_policy_cost_gbp_per_mwh"),
                                locked_network_cost_per_mwh=term.get(
                                    "locked_network_cost_gbp_per_mwh"),
                                company_eac_kwh=eac_missed, fuel=commodity,
                                segment=(get_customer(billing_account) or {}).get(
                                    "segment", "resi")),
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
                    _notify_registration_loss(billing_account, term_start_str,
                                              pending_already_sent=_pending_notice_sent)
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
                        # THE CHANNEL TRAVELS WITH THE DEPARTURE (PB7). Booking the loss without
                        # it would fill the book-wide numerator while leaving the per-channel one
                        # empty, and the engagement belief would read "no prepayment customer has
                        # ever left us" off a wire that never carried the field. The per-channel
                        # arming is set BY this argument rather than by a call beside it, so it
                        # cannot survive the argument being dropped.
                        _pressure_ledger.observe_competitive_loss(
                            int(term_start_str[:4]), payment_method=_company_payment_method,
                            account_id=billing_account,
                        )
                    print(
                        f"  [CHURN] {billing_account} at {term_start_str} — "
                        f"p_retain={event['effective_retention_probability']:.4f}  "
                        f"roll={event['random_roll']:.4f}"
                    )
                    # A leaver at renewal is a switcher: it vacates nothing, so there is no
                    # property to win (Phase 7e's roll, retired 2026-10-10). Every one goes to market.
                    if mandate_permits_replacement():
                        customer_data = get_customer(billing_account)
                        segment = customer_data["segment"] if customer_data else "resi"
                        acq_seed = f"acquire_{billing_account}_{term_start_str}"

                        # Phase 47b: cap-aware acquisition gate — the supplier declines
                        # to go to market when its price is above the published default
                        # (2026-10-02: both fuels, ex-VAT, on the day). KNIFE3 step 27 (register §3v): the budget and
                        # the gate are ONE question asked through
                        # `company.interfaces.growth_desk`, not two the world answered off
                        # its own copy of the supplier's cost table.
                        _acq = decide_acquisition(
                            segment=segment,
                            commodity=commodity,
                            company_fwd_gbp_per_mwh=company_fwd,
                            term_start=term_start_str,
                            # The supplier's own strike for this commodity on this day, which is
                            # the fix a replacement would be quoted. Only a FIXED term's strike is
                            # one: an SVT term's rate is the cap itself and would always pass.
                            quoted_unit_rate_per_mwh=(
                                term["unit_rate_gbp_per_mwh"]
                                if term_tariff_type == "fixed" else None
                            ),
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
            elif _retention_offer is not None and retention_log:
                # No lifecycle event — offer made, customer just renewed normally
                retention_log[-1]["outcome"] = "retained"
                nudge_physics_log.append({
                    "customer_id": billing_account,
                    "event_date": term_start_str,
                    "framing_type": retention_log[-1].get("framing_type"),
                    "susceptibility": susceptibility_for(billing_account).value,
                    "effectiveness_multiplier": round(_retention_offer[1], 4),
                    "outcome": "retained",
                })

        # A LEG THAT DOES NOT CARRY ITS HOUSEHOLD'S DEPARTURE still decides whether to take its own
        # fuel's fix. The household's leave decision is on the electricity leg, which sorts first
        # (`X` < `Xg` at one term start), so reaching here means it stayed.
        if _renewal_outcome is None and commodity != _decision_leg:
            _renewal_outcome = renewal_outcome(
                event_type="renewed", position_vs_default=_offer_vs_default,
            )
            if _renewal_outcome == RENEWAL_DECLINED_FIX:
                _declined_on_the_riding_leg.append(declined_fix_event(
                    customer_id=cid, event_date=term_start_str, commodity=commodity,
                    declined_unit_rate_gbp_per_mwh=unit_rate,
                    position_vs_default=_offer_vs_default,
                ))

        # THE DECLINED TERM IS REPLACED BY THE DEFAULT TARIFF FOR THE SAME WINDOW, and nothing the
        # refused offer wrote may survive it: the household reads downstream as one on the default.
        # So the prior rate and the bill-shock count are put back (an SVT segment never writes
        # either), the account-state row for a term that was never contracted is withdrawn, and
        # `_last_tariff_type` is put back so the first spliced segment opens -- or, after a
        # conversion, continues -- the household's SVT stint. The segments are the same
        # `build_svt_schedule` window the builders splice for a passive renewer (term start to the
        # day before the anniversary, own fuel), and they settle, hedge and roll C1b's inertia
        # hazard exactly as any other default-tariff segment does. They never advance
        # `term_indices` (`_DECLINED_FIX_SPLICE`).
        if _renewal_outcome == RENEWAL_DECLINED_FIX:
            if _prior_rate_before_offer is None:
                _prior_rates.pop(cid, None)
            else:
                _prior_rates[cid] = _prior_rate_before_offer
            if _shock_counted_this_term:
                _rate_shock_counts[cid] -= 1
                _bill_shock_dates[cid].pop()
            if account_state_log and account_state_log[-1] is _account_state_row:
                account_state_log.pop()
            if _previous_tariff_type is None:
                _last_tariff_type.pop(cid, None)
            else:
                _last_tariff_type[cid] = _previous_tariff_type
            _last_term_spliced[cid] = _previous_term_spliced
            _default_end = min(
                date.fromisoformat(term_start_str) + timedelta(days=CONTRACT_LENGTH_DAYS - 1),
                date.fromisoformat(effective_end),
            )
            try:
                _default_segments = build_svt_schedule(
                    cid, term_start_str, _default_end.isoformat(),
                    elec_records if commodity == "electricity" else gas_records,
                    lookback_temps_fn=_lookback_temps_fn(cid), fuel=commodity,
                )
            except ValueError:
                # The price history ends inside the window: the builders stop the schedule there,
                # and so does this.
                _default_segments = []
            for _segment in _default_segments:
                _segment[_DECLINED_FIX_SPLICE] = True
                _push_term(_segment["acquisition_date"], cid, commodity, _segment)
            print(
                f"  [DECLINED-FIX] {billing_account} {commodity} at {term_start_str} — offer "
                f"{_offer_vs_default:+.1%} vs default; {len(_default_segments)} default segment(s)"
            )
            continue

        # Phase 14b: compute gas company churn estimate for dual-fuel monitoring.
        # The SECONDARY fuel's renewal pressure — a gas leg that does NOT carry its account's
        # departure decision, so the company watches it as an early warning on dual-fuel
        # portfolios rather than as a decision it takes.
        #
        # `!= _decision_leg` IS WHAT MAKES "SECONDARY" TRUE (2026-09-16). The guard was
        # `commodity == "gas"` when gas could never be the deciding leg, and the two read the
        # same. Now that a gas-only account decides on its gas leg, `estimate_secondary_fuel_churn`
        # would be applied to a household's PRIMARY fuel — a second, differently-shaped belief
        # about the very renewal the branch above already rolled, logged under a name asserting it
        # is about something else. On every dual-fuel account this guard is the identity on the
        # old one.
        if (term_index >= 1 and commodity == "gas" and commodity != _decision_leg
                and old_gas_rate is not None):
            gas_customer_data = next(
                (c for c in _known_customers() if c["customer_id"] == billing_account),
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

        # A DEPARTURE BOOKED ABOVE IS DATED THIS TERM'S START, SO THIS TERM SUPPLIES NOTHING. The
        # household's other leg, popped after this one, is skipped at the top of the loop; this leg
        # used to go on and settle its whole term, so a household that left on 1 January was
        # billed electricity to 31 March (SEAT_FINDING_ELECTRICITY_KEEPS_BILLING_..._2026-10-05).
        if _supplies_nothing(billing_account, term_start_str):
            if not _spliced:
                term_indices[cid] += 1
            continue

        # THE MOVE-OUT NOTICE, from a household still ours at this term's start whose move falls in
        # it: one notice for this leg's point, dated two Working Days before the move. Handed only
        # the point and the date, so nothing else of the move can ride on it.
        if _moved_in_term:
            for _wire in _move_out_feed.wire_notices_for_move([cid], _move_end):
                _move_out_register.receive_move_out_wire(_wire)
            # THE MOVE-WITH-US OFFER (`company/crm/move_with_us_offer.py`), asked once per household
            # on the leg that carries its decisions, from what the company holds: the notice, the
            # tariff in force, the cost it struck that rate against, its own consumption estimate,
            # and what the household disclosed to its Priority Services Register.
            if commodity == _decision_leg:
                _psr_for_move = None
                if _vulnerability_hidden_state_on:
                    _psr_for_move = open_priority_services_register()
                    _mover_record = get_customer(cid) or {}
                    for _wire in wire_registrations(registration_notices(
                            [(cid, date.fromisoformat(str(_mover_record.get(
                                "acquisition_date", term_start_str))[:10]))], run_base_seed())):
                        _psr_for_move.receive_registration_wire(_wire)
                _mwu_offer, _mwu_vulnerable, _mwu_reason = request_move_with_us_offer(
                    _move_out_register, cid, _move_end.isoformat(),
                    offers_on=policy.move_with_us_offers, tariff_type=term_tariff_type,
                    unit_rate_per_mwh=unit_rate, cost_per_mwh=company_fwd,
                    annual_kwh=_account_state_row.get("company_eac_kwh"),
                    psr_register=_psr_for_move)
                _mwu_notice = _move_out_register.notice_for(cid, _move_end.isoformat())
                move_with_us_log.append({
                    "billing_account": billing_account, "supply_point_id": cid,
                    "commodity": commodity, "move_out_date": _move_end.isoformat(),
                    "notified_on": (_mwu_notice.notified_on.isoformat()
                                    if _mwu_notice is not None else None),
                    "tariff_type": term_tariff_type, "unit_rate_gbp_per_mwh": unit_rate,
                    "cost_gbp_per_mwh": company_fwd,
                    "company_eac_kwh": _account_state_row.get("company_eac_kwh"),
                    "offered": _mwu_offer is not None, "no_offer_reason": _mwu_reason,
                    "known_vulnerable": _mwu_vulnerable,
                })
                # THE WORLD'S ANSWER (`simulation/move_with_us_answer.py`): the roll of the
                # household's NEXT decision against k times the world's P(stay) at the tariff it
                # carries -- its renewal onto a fixed term, or its current default-tariff segment's
                # stay annualised. A follower is then supplied at its new home (step 4).
                if _move_with_us_answers and _mwu_offer is not None:
                    if term_tariff_type == SVT_TARIFF_TYPE:
                        _segment_row = next(
                            (r for r in reversed(_svt_decisions)
                             if r["customer_id"] == billing_account
                             and r["event_date"] == term_start_str
                             and r["event_type"] == "stayed" and r.get("sim_segment_days")),
                            None)
                        _p_carried = (None if _segment_row is None else p_stay_on_default_tariff(
                            _segment_row["realized_churn_probability"],
                            _segment_row["sim_segment_days"]))
                        _next_roll = default_tariff_roll(billing_account, _next_renewal_str[:10])
                    else:
                        _p_carried = (_renewal_event_this_term or {}).get(
                            "effective_retention_probability")
                        _next_roll = churn_roll_for_renewal(
                            billing_account, _next_renewal_str[:10])
                    move_with_us_log[-1].update({
                        "take_up_scale": _move_with_us_k,
                        "p_stay_at_carried": _p_carried,
                        "unanswerable_reason": NOT_ANSWERABLE if _p_carried is None else None,
                        "next_renewal": _next_renewal_str[:10],
                        "next_renewal_roll": _next_roll,
                        "moves_with_us": (_p_carried is not None and household_moves_with_us(
                            _next_roll, _p_carried, _move_with_us_k)),
                    })
                    if move_with_us_log[-1]["moves_with_us"]:
                        _supplied, _why_not = _supply_at_new_home(
                            cid, commodity, billing_account, _move_end, _next_renewal_str)
                        move_with_us_log[-1].update(_supplied)
                        move_with_us_log[-1]["not_supplied_reason"] = _why_not
                        if _why_not is None:
                            # It stays ours: the term in force runs to its end, the old home to
                            # the move date and the new one after it.
                            term_end_str = _next_renewal_str
                            _carried_from = _move_end.isoformat()
                            # s.8.7 choice 7: a follower is not an exit, so its bills after the
                            # move are not drawn as a gone-away final bill.
                            _moved_out_on_by_leg.pop(cid, None)
                            home_move_outs[-1]["followed_household"] = True
                            _portfolio_margins.account_held_on_a_save(billing_account)
                            _followed_moves.add((billing_account, _move_end))
                            _prior_state = _journey_before_move.get((billing_account, _move_end))
                            if _prior_state is not None:
                                _churn_journey_register.get_journey(
                                    billing_account).state = _prior_state

        # A MOVE THAT DID NOT FOLLOW US CLOSES THE ACCOUNT on the move date (`move_end` is the
        # first day not supplied), and the queue is told now, as for a departure. A follower stays
        # ours and is not told.
        if (_home_moves_on and _moved_in_term
                and (billing_account, _move_end) not in _followed_moves):
            _payment_triad.close_account(billing_account, _bill_due_on(
                (_move_end - timedelta(days=1)).isoformat()[:7]))

        if cid in pending_committee_overrides:
            hf = pending_committee_overrides.pop(cid)
        else:
            hf = next_hf[cid]
        current_hf[cid] = hf

        if commodity == "electricity":
            customer = get_customer(cid)
            # The company's volume: its own arrived reads, else the declared EAC. No household
            # multiplier -- the household's assets are the world's; see `_company_eac_estimate`.
            eac_kwh = _company_eac_estimate(cid, term_start_str, settled_fold)
            settled_shape_fn = None
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
                # A non-HH meter of 2016-2025 was SETTLED on its volume x its registered profile,
                # not on its own half hours (SEAT_PREREGISTRATION_A_PROFILED_HOME_SETTLES_ITS_OWN_
                # VOLUME_ON_ITS_REGISTERED_PROFILE_2026-10-22.md). The legacy branch below needs no
                # such shape: its demand already IS its class's profile, weather-adjusted.
                settled_shape_fn = SHAPE_LOADERS[registered_profile_class(
                    customer, household_demand_register,
                    max(customer.get("acquisition_date") or REPORT_START, REPORT_START))]
            else:
                demand_provider_by_customer[cid] = LEGACY_PROVIDER
                profile_class = registered_profile_class(
                    customer, household_demand_register,
                    max(customer.get("acquisition_date") or REPORT_START, REPORT_START))
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
                    eac_kwh=_base_profile_eac(customer),
                )

            # THE TERM A MOVER CARRIED: the old home's demand to the move date, the new home's
            # trace after it (`_supply_at_new_home`). Only on this one term; later terms read the
            # new home's data directly.
            if _carried_from is not None:
                settled_shape_fn = None  # two homes' shapes spliced; left on its own trace
                shape_fn = _shape_across_a_move(
                    shape_fn,
                    fabric_shape_fn(_relocation_pending[cid]["series"], "electricity",
                                    battery_dispatch=_fabric_battery_dispatch_for(cid)),
                    _carried_from)

            cust_segment = customer.get("segment", "resi") if customer else "resi"
            if term_tariff_type == "deemed":
                # Phase 40c: out-of-contract period — spot + deemed_premium, no forward hedge.
                # Phase 47a/MARGIN_REALISM Step 5: cap-bound 2019+ for resi (W3_1_price_cap_binding).
                deemed_premium = term.get("deemed_premium", 0.20)
                term_records = run_deemed_term(
                    cid, term_start_str, term_end_str, deemed_premium,
                    shape_fn, elec_records, segment=cust_segment, commodity=commodity,
                    settled_shape=settled_shape_fn,
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
                # The term's tariff type goes with it: a default-tariff roll is single-rate,
                # because a ToU pair is a contract the household chose, not its meter's gift.
                _tou = request_tou_offer(
                    customer=customer, tariff_type=term_tariff_type,
                    flat_unit_rate_gbp_per_mwh=unit_rate,
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
                    # A time-of-use term needed HH data to settle (P300, Measurement Class F), so
                    # it keeps its own shifted shape.
                    settled_shape=(settled_shape_fn if tou_rates is None else None),
                )
                # Phase 43a: open a forward contract in the company trading book.
                # agreed_price = forward_price, the market's own PIT forward quote
                # (docs/market_research/a_hedge_executes_at_the_markets_quote_not_the_companys_own_forward_estimate_2026-10-12.md):
                # a counterparty prices the trade, not the company's own belief --
                # company_fwd stays the sizing input (decide_term_hedge, above) and
                # the tariff-pricing strike (request_fixed_unit_rate), neither of
                # which this changes.
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
                        forward_price_gbp_per_mwh=forward_price,
                        hedge_fraction=hf,
                        term_days=term_days_count,
                    )
                    # Add hedge_pnl_gbp per settlement record (decomposed from supply margin).
                    for rec in term_records:
                        _bought = rec.get("settled_kwh", rec["consumption_kwh"])
                        spot = rec.get("wholesale_cost_gbp", 0.0) / (_bought / 1000.0) if _bought > 0 else 0.0
                        rec["hedge_pnl_gbp"] = round(hedge_desk.settle_period_pnl_gbp(
                            cid, term_start_str, _bought, spot
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
            # TWO QUANTITIES, NOT ONE (2026-10-11). `aq_kwh` is the HOUSEHOLD's gas use -- the
            # registered AQ times its EPC-band multiplier (Phase D) -- and drives the world's
            # demand. `hedge_aq_kwh` is what the COMPANY believes it uses, from its own reads and
            # the registered AQ (`_company_eac_estimate`), and is all the desk and the risk see.
            aq_kwh = gas_customer["aq_kwh"]
            if household_demand_register is not None:
                _gas_mult = household_demand_register.gas_eac_multiplier_for_date(cid, term_start_str)
                aq_kwh = max(1, round(aq_kwh * _gas_mult))
            hedge_aq_kwh = _company_eac_estimate(cid, term_start_str, settled_fold, commodity="gas")

            # Phase 44b: VaR-constrained hedge decision for gas fixed terms (mirrors electricity 43b).
            # Phase 56: Pass-through gas customers must not hedge — they bill at spot, so a forward
            # hedge creates wrong-way risk (windfall gain 2021, catastrophic loss 2023 on reversion).
            if term_tariff_type == "pass_through":
                hf = 0.0
                current_hf[cid] = 0.0
            elif policy.use_var_hedge_decision and unit_rate and company_fwd and hedge_aq_kwh > 0:
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
                        volume_kwh=hedge_aq_kwh,
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
            naked_kwh = 0.0 if term_tariff_type == "pass_through" else hedge_aq_kwh * (1.0 - hf)
            risk = assess_term_risk(term_start_str, naked_kwh, forward_price, gas_records)
            counterfactual_risk = assess_term_risk(
                term_start_str,
                0.0 if term_tariff_type == "pass_through" else float(hedge_aq_kwh),
                forward_price, gas_records,
            )
            current_risk[cid] = risk

            # Phase W: gas HDD shape is now computed daily inside run_gas_term.
            # weather_factor term-level scalar removed; resi/SME uses per-day HDD internally.
            # W2_30: this household's OWN heating fraction where its physics could supply
            # one, the population 70/30 split where it could not -- and which it was is in
            # the run's own record above, never inferred from an absence.
            _gas_split = gas_heating_fraction_by_customer.get(cid)
            term_records = run_gas_term(
                cid, term_start_str, term_end_str, aq_kwh,
                unit_rate, hf, forward_price,
                risk["monthly_cost_of_capital_gbp"], gas_records,
                segment=cust_segment,
                pass_through=(term_tariff_type == "pass_through"),
                heating_fraction=_gas_split.heating_fraction_for(aq_kwh) if _gas_split else None,
                # Known only where the default tariff was priced by method; elsewhere the
                # credit row, which in 2022-23 undercharges a prepayment leg's UIG.
                prepayment=(_svt_priced_method == "prepayment"),
            )
            for rec in term_records:
                rec["data_regime"] = "historical"

        # B7 slice 6: a vacated premise's rows before the incoming occupier arrives are the
        # owner's void: standing charge, no energy (`sim/customer_state_layer.as_void_row`).
        if cid in _void_until:
            _void_end_iso = _void_until[cid].isoformat()
            _void_segment = (get_customer(cid) or {}).get("segment", "resi")
            for rec in term_records:
                if rec["settlement_date"][:10] < _void_end_iso:
                    as_void_row(rec, commodity, _void_segment)

        # The household on a default tariff paid the EPG rate; the Treasury paid the rest of
        # `revenue_gbp`. Its share rides on the record for the bill to carve out.
        if term_tariff_type == SVT_TARIFF_TYPE and _is_domestic_leg(cid):
            stamp_hmt_epg_receipt(term_records, fuel=commodity, method_held=_svt_priced_method)

        # Phase MW: income stress bad-debt uplift (residential only).
        _income_stress = (
            household_demand_register.income_stress_at_date(cid, term_end_str)
            if household_demand_register is not None else None
        )
        _stress_bd_mult = stress_bad_debt_multiplier(_income_stress)

        settled_this_term: list[dict] = []
        # Months this term closes are posted once the stop board has seen the term (below): a bill
        # asks whether its DD was stopped by its due date, and the board can only answer from every
        # month before it. Nothing in this loop reads the triad, so the posting order is unchanged.
        _months_closed_this_term: list = []
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
            # B7 slice 4: energy at a vacated premise before anyone is named is billed to "the
            # occupier" and goes unpaid (`unnamed_until`). It is its own field, not
            # `bad_debt_gbp`, because phase 4c releases that placeholder and re-books it from the
            # arrears engine, which would collect this window as if a named household paid it.
            #
            # B7 slice 6: a void row is the OWNER's deemed charge. It is its own receivable
            # (`void_owner_charge_gbp`), not occupier debt and not `bad_debt_gbp`, and no cash
            # arrives for it: the company has no landlord record to bill (back_billing_and_
            # liability.md s.9.5, "the void's cost stays with the supplier"). Whether owners pay
            # in practice is the register's open practitioner question; no recovery is booked.
            if "void_owner_charge_gbp" in rec:
                rec["net_margin_gbp"] = round(
                    rec["net_margin_gbp"] - rec["void_owner_charge_gbp"], 6)
                _move_in_entry[cid]["void_owner_charge_gbp"] += rec["void_owner_charge_gbp"]
                _bad_debt = 0.0
            elif (cid in _unnamed_until
                  and rec["settlement_date"][:10] < _unnamed_until[cid].isoformat()):
                # EBSS goes to whoever holds the account at 00:00 on the month's 1st (guidance
                # 5.4), and an unnamed occupier's deemed account on an occupied home is one (Annex
                # C, "Occupier Accounts"). The government pays the credit, so only the rest is
                # the occupier's debt. A home still void on the 1st is Annex C's vacant exception.
                _owed = rec.get("revenue_gbp", 0.0)
                _opened: dict[tuple[str, str], float] = {}
                _credit = occupier_scheme_credit(_occupier_credit_left, cid, rec["settlement_date"],
                                                 _owed, cust_segment, commodity, _opened)
                if _opened:
                    rec["occupier_scheme_month_credit_gbp"] = sum(_opened.values())
                if _credit > 0.0:
                    rec["occupier_scheme_credit_gbp"] = _credit
                rec["occupier_debt_gbp"] = _owed - _credit
                rec["net_margin_gbp"] = round(rec["net_margin_gbp"] - rec["occupier_debt_gbp"], 6)
                _bad_debt = 0.0
            rec["bad_debt_gbp"] = _bad_debt
            # Accumulated AFTER the two branches above, because they decide whose a row is: the
            # owner's void charge (slice 6) and the unnamed occupier's debt (slice 4) are not this
            # household's to pay, as the arrears engine already holds (`occupier_share`).
            _held = _payment_month_open.get(cid)
            if _held is not None and _held["month"] != rec_month:
                _months_closed_this_term.append((cid, _payment_month_open.pop(cid)))
                _held = None
            if _held is None:
                _held = _payment_month_open[cid] = {
                    "month": rec_month, "amount_gbp": 0.0,
                    "income_stress_value": (
                        _income_stress.value if _income_stress is not None else None),
                    "segment": cust_segment, "fuel": commodity}
            _held["amount_gbp"] += (float(rec.get('revenue_gbp', 0.0) or 0.0)
                                    - rec.get("void_owner_charge_gbp", 0.0)
                                    - rec.get("occupier_debt_gbp", 0.0)
                                    - rec.get("occupier_scheme_credit_gbp", 0.0))
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
        _committed_from = len(all_records)
        all_records.extend(fold_to_days(settled_this_term))
        # The board keeps what it observes for the rest of the run, so it is handed the committed
        # ROWS, not the term's dicts -- handed the dicts it would hold the whole book twice over.
        _folded_this_term = all_records[_committed_from:]
        _dd_stop_board.observe(_folded_this_term)
        if not _dd_shock_strengths.off:
            _dd_in_loop_review.observe(_folded_this_term)
        for _closed_cid, _closed in _months_closed_this_term:
            _post_month_bill(_closed_cid, _closed)
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
        # The term's outcome off the company's own P&L. Whether it teaches the premium (not if a
        # save held it: director, 2026-10-08) is the book's rule, behind its door.
        _portfolio_margins.term_ended(
            billing_account=billing_account, commodity=commodity,
            last_settled_day=max(r["settlement_date"] for r in settled_this_term),
            net_margin=actual_net, revenue=term_revenue,
            standing_charge_revenue=sum(
                r.get("standing_charge_gbp", r.get("gas_standing_charge_gbp", 0.0))
                for r in settled_this_term),
            volume_mwh=sum(r["consumption_kwh"] for r in settled_this_term) / 1000.0,
            held_on_a_save=_held_on_a_save, tariff_type=term_tariff_type,
        )

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

    # The months still open when the run ended are billed: the last month of every leg.
    for _open_cid in list(_payment_month_open):
        _post_month_bill(_open_cid, _payment_month_open.pop(_open_cid))
    # Every bill has posted, so each closed account's final bill is known: a lump dated after it is
    # a gone household's, and is lost (`world_payment_truth.GONE_HOUSEHOLD_PAYS_NO_LUMP`). Told
    # before the first reader below forces a crossing. The same set the P&L writes off at close.
    _payment_triad.close_accounts(households_whose_account_closed(
        {"churned_billing_accounts": churned_billing_accounts, "home_move_outs": home_move_outs}))

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
    # One pass, in book order, so each customer's sums add the same floats in the same order as
    # the per-customer filter did. That filter read the whole book once per customer: ~600m row
    # reads on a run to 2018-09, and quadratic in the book.
    _records_by_cid: dict[str, list] = defaultdict(list)
    for r in all_records:
        _records_by_cid[r["customer_id"]].append(r)
    for c in ELEC_CUSTOMERS + GAS_CUSTOMERS:
        cid = c["customer_id"]
        recs = _records_by_cid.get(cid, [])
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
        if evt.get("departure_rolled") is False:
            print(f"  {evt['customer_id']} {evt['event_date']}: converted off SVT, not rolled")
            continue
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
    total_occupier_debt = sum(r.get("occupier_debt_gbp", 0.0) for r in all_records)
    total_void_owner_charge = sum(r.get("void_owner_charge_gbp", 0.0) for r in all_records)
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

    # Phases OG/OH/OI + a53: the supplier's annual statutory return -- Renewables
    # Obligation, FiT levelisation levy, Climate Change Levy, Capacity Market
    # supplier levy. KNIFE pass 3 step 17 moved the first three behind one door
    # (register §3l): working out what you owe off your own supply volumes is the
    # supplier's statutory accounting, not world physics. The world hands over
    # the settled records and its own I&C book; the obligation levels, buy-out
    # prices and levy rates stay company-side.
    #
    # CM joined as the fourth leg on 2026-09-07. It is NOT a duplicate of the
    # `cm_levy_gbp` this file already accumulates through `hedged_settlement`:
    # that one is the pass-through as it lands in the settlement, bucketed by
    # Apr-Mar obligation year off each record; this one is the supplier's own
    # annual return on its calendar-year volumes, and it refuses years Ofgem has
    # not published rather than carrying a rate forward. The report prints both
    # and reconciles them -- the same shape RO, FiT and CCL already have.
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
    cm_statutory_summary = _statutory.cm_summary

    # Phase 27d: Triad risk for I&C customers.
    # Identify Triad periods for each winter in the run window, then compute
    # each I&C customer's TNUoS exposure. Uses SSP as a demand proxy.
    ic_customer_ids = [
        c["customer_id"]
        for c in _known_customers()
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
        commodity_by_customer_id={c["customer_id"]: c["commodity"] for c in _known_customers()},
        elec_spot_records=elec_records,
        gas_spot_records=gas_records,
        mark_date=effective_end,
        balance_sheet={"net_assets_gbp": final_treasury},
        settled_records=all_records,
        segment_by_customer_id={
            c["customer_id"]: c.get("segment", "resi")
            for c in _known_customers() + ACQUIRED_CUSTOMERS
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

    _grade_demand_estimates_against_the_year_ahead(demand_estimation_log, settled_fold)
    _psr_registrations = (
        {"psr_registrations": _deliver_psr_registrations(all_records, run_base_seed())}
        if _vulnerability_hidden_state_on else {})
    _result = {
        **_psr_registrations,
        "all_records": all_records,
        "administration_event": administration_event,
        # THE WORLD PAST THE RECORD, as the run actually lived it, or None for a run inside it.
        # Every input that is not the record is named: the spine world and price scenario, the
        # record year each forward year's weather replays, and the conventions held at the last
        # published value -- so a forward result can never read as a historical one.
        "beyond_the_record": (None if effective_end <= REPORT_END else {
            **(_forward or {}),
            "weather_analogue_years": getattr(_weather_world, "analogue_years", {}),
            "held_at_last_published": (
                "the domestic price cap carries its last published window forward "
                "(company.pricing.ofgem_price_cap); year-keyed world tables past their last "
                "published year return that year (simulation.policy_costs and peers)"),
        }),
        # W1_11: which generator settled each electricity customer's demand, and
        # why a premise is not fabric-driven -- recorded so an unexplained
        # population change is visible in the run, not inferred from its numbers.
        "demand_provider_by_customer": dict(demand_provider_by_customer),
        # W1_14 step 1: which premises the per-cell store could not give a daily mean temperature,
        # and why -- in the record rather than printed, for the same reason the gas half below is.
        # Empty is the good answer and it is still an ANSWER; a missing key would not be.
        "weather_refusal_by_customer": dict(weather_refusal_by_customer),
        # W2_30, THE GAS HALF OF THE SAME QUESTION (2026-09-18). These were computed, used at the
        # gas term below, and PRINTED -- reaching no artefact, so no reader could tell whether the
        # per-household seasonal shape had reached the gas book at all, or how many households were
        # quietly settling on the population 70/30 split instead. That is the state the electricity
        # side was in until `demand_provider_by_customer` was published beside it, and
        # `SeasonalGasRefusal`'s own docstring already claimed the opposite: the reason is carried
        # "so a customer silently keeping the population constant is visible in the run instead of
        # inferred from its numbers". It was visible only on a terminal nobody keeps.
        "gas_shape_provider_by_customer": {
            **{cid: "fabric_seasonal_split" for cid in gas_heating_fraction_by_customer},
            **{r.customer_id: "population_70_30_split" for r in gas_shape_refusals},
        },
        "gas_shape_refusals": [
            {"customer_id": r.customer_id, "reason": r.reason} for r in gas_shape_refusals
        ],
        "fabric_eligibility": [
            {"customer_id": v.customer_id, "is_eligible": v.is_eligible, "reason": v.reason}
            for v in fabric_eligibility_verdicts
        ],
        # The fabric premises whose settled shape failed the texture control in a book that passed it
        # as a whole -- recorded, not printed only, so a minority failure is a finding a reader can
        # find. Empty is the good answer and still an answer.
        "fabric_untextured_premises": list(_untextured_fabric_premises),
        # The founders whose first term priced off less than a full lookback, each with the reason
        # its record cannot reach further back. Empty is the good answer and still an answer.
        "short_first_term_lookbacks": _short_first_term_lookbacks,
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
        # C1b. A SECOND POPULATION UNDER A SECOND NAME. These are departures from the standard
        # variable product: no renewal decision happened, so none of the renewal-decision fields
        # `customer_events` carries exist on them. A reader whose subject is departures unions
        # the two; a reader whose subject is renewal decisions keeps reading the one above and is
        # unaffected by this commit, which is the property the separation buys.
        "svt_departures": _svt_departures,
        #: One churned row per supply point a departure ended, the riding gas leg included.
        "leg_departures": _leg_departures,
        # And the DECISIONS behind them — `tools/capture_departure_factors` writes these to the
        # `_svt_segment_decisions.json` companion, which is the population every SVT-route reading
        # in `tools/measure_churn_heterogeneity` is computed over.
        "svt_decisions": _svt_decisions,
        "declined_on_the_riding_leg": _declined_on_the_riding_leg,
        "churned_billing_accounts": sorted(churned_billing_accounts),
        # What the SUPPLIER holds about those departures, read from its own register.
        "registration_losses_notified": _change_of_supplier_register.losses_notified(),
        "registration_loss_exceptions": _change_of_supplier_register.loss_exceptions(),
        "hedge_evolution": evolution_logs,
        "total_gross": total_gross,
        "total_capital": total_capital,
        "total_bad_debt": total_bad_debt,
        "total_occupier_debt": total_occupier_debt,
        **({"total_void_owner_charge": total_void_owner_charge} if _home_moves_on else {}),
        # EP4: each account's collections journey on the COMPANY's own ledger -- dated stages from
        # a missed payment to an exit, or `exit: None` while still open at the run's end.
        "collections_journeys": _payment_triad.collections_journeys(
            date.fromisoformat(effective_end)),
        # ...and what became of the world's later lump settlements: crossed, replaced by an agreed
        # plan, or crossed for a bill a plan covers (the arrears paid twice). AFTER the journeys,
        # whose end-of-run forced crossing is the last that can move these counts.
        "later_settlements": _payment_triad.later_settlements(),
        # The COMPANY's bad-debt provision: a stock over its own receivables on the payment-seam
        # ledger, by footing and age, at each 31 December and at the end. Unlike
        # `total_bad_debt`'s provisioned reading, which is the world's incidence on revenue.
        "company_provision": _company_provision_by_year_end(
            _payment_triad, effective_end, _book_method_of,
            crisis_overlay=policy.provision_crisis_overlay,
            arrears_overlay=policy.provision_arrears_overlay),
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
            customer_events_log, fresh_acquisitions),
        "retention_log": retention_log,
        "retention_offer_channel_log": retention_offer_channel_log,
        "retention_save_holdout_log": retention_save_holdout_log,
        "retention_save_rate_lower_bound_log": retention_save_rate_lower_bound_log,
        **({"retention_holdout_log": retention_holdout_log,
            # Q10: each row's days to its first later loss, so any window can be read off the run.
            "retention_holdout_outcomes": _retention_holdout.outcomes(
                _change_of_supplier_register.losses_notified())}
           if policy.retention_runs_holdout else {}),
        **({"next_best_action_renewal_log": _renewal_advice.decisions(),
            "next_best_action_legs_without_contribution":
                _renewal_advice.legs_without_contribution}
           if _renewal_advice is not None else {}),
        **({"shared_rise_log": shared_rise_log}
           if policy.renewal_rate_bills_the_shared_rise else {}),
        "nudge_physics_log": nudge_physics_log,
        "retention_cost_events": retention_cost_events,
        "no_offer_churn_log": no_offer_churn_log,
        "retention_gate_value_test_log": retention_gate_value_test_log,
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
        "account_state_log": account_state_log,
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
        # a53: Capacity Market supplier levy -- the supplier's OWN statutory
        # position, distinct from the settlement pass-through in
        # `years[*].cm_levy_gbp`. Named `cm_statutory_summary` and not
        # `cm_summary` on purpose: the shorter name would sit next to the
        # settlement figure looking like the same quantity.
        "cm_statutory_summary": cm_statutory_summary,
        "per_customer_behavioral": _build_behavioral_trajectories(
            ELEC_CUSTOMERS + GAS_CUSTOMERS,
            household_demand_register,
            _cx_desk,
            _bill_shock_dates,
            {m["customer_id"]: m["move_date"] for m in home_move_outs},
            dd_shock_responses_of=_dd_shock_book.responses_of,
            # One payment truth (`simulation/world_payment_truth.py`), only when switched on. Built
            # here, after `collections_journeys` above has walked every account to the run's end.
            payment_truth=(_world_payment_truth.build(
                _payment_triad, date.fromisoformat(effective_end))
                if _world_payment_truth.UNIFIED else None),
        ),
        # DD4b: only present when its toggles are switched on, so the shipped output is unchanged.
        **({"dd_shock_response_summary": _dd_shock_book.summary(),
            "dd_review_told_in_loop": _dd_in_loop_review.told}
           if not _dd_shock_strengths.off else {}),
        **({"household_method_acts_summary": _method_dynamics.summarise(_dd_shock_book)}
           if not _method_strengths.off else {}),
        # Phase NJ: company churn model calibration report
        "churn_model_performance": score_churn_estimates(
            customer_events_log, retention_log, no_offer_churn_log
        ),
        # Phase QL Part 2: hidden churn-journey state trajectory (SIM-side shadow
        # tracker -- does not gate the roll_lifecycle_event dice roll itself)
        "churn_journey_log": churn_journey_log,
        **({"move_out_notices_filed": _move_out_register.notices(),
            "move_out_notice_exceptions": _move_out_register.exceptions()}
           if _home_moves_on else {}),
        **({"move_with_us_log": move_with_us_log} if policy.move_with_us_offers else {}),
        **({"home_move_outs": home_move_outs, "home_move_ins": home_move_ins}
           if _home_moves_on else {}),
        "renewal_decisions_log": renewal_decisions_log,
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
    } | ({"save_on_loss_notice_log": save_on_loss_notice_log} if _save_offers_on else {})
    # THE BOARD OUTLIVES THE LAST READ THAT ASKS IT. `company_provision` above asks the company's
    # method register for past dates, and `get_payment_method(as_of=)` refuses with no board. Cleared
    # here, after the result is built, rather than before it: from 42b2eb254 (2026-10-11) to
    # 2026-10-12 it was cleared first, and every run's company provision read "could not be read".
    install_stop_notice_board(None)
    return _result



def _build_behavioral_trajectories(customers, hdr, cx_desk, bill_shock_dates=None,
                                   move_out_dates=None, dd_shock_responses_of=None,
                                   payment_truth=None):
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
        # B7: a mover's last bill is the exit (`arrears_engine.mover_final_bill_outcome`). Only a
        # mover carries the key, so every other record is unchanged.
        if cid in (move_out_dates or {}):
            out[cid]["moved_out_on"] = move_out_dates[cid]
        # DD4b: a household's answer to a DD shock rides on each of its legs' records, for the
        # arrears engine and the rails. Only a responding household carries the key.
        _dd_responses = dd_shock_responses_of(household_of(cid)) if dd_shock_responses_of else None
        if _dd_responses:
            out[cid][_DD_SHOCK_RECORD_KEY] = list(_dd_responses)
        # One payment truth: the triad's outcomes and repayments for this leg, when switched on.
        if payment_truth and cid in payment_truth:
            out[cid][_world_payment_truth.RECORD_KEY] = payment_truth[cid]
    return out



def budgeted_run_peak_mb() -> tuple[float | None, str]:
    """`(peak_mb, basis)`: what one run at the shipped settlement budget is measured to hold.

    The measured whole-run curve evaluated AT `SETTLEMENT_CUSTOMER_YEAR_BUDGET` -- the same line
    `test_the_settlement_ceiling_does_not_outrun_the_measured_memory_curve` prices the budget on,
    read the other way: the budget fixes the customer-years, the curve gives the cgroup peak. The
    curve was measured on the production book (~175 founders); a 4,000-founder book is not on it.
    No curve is a `None` with its reason, never a number picked to fill the slot.
    """
    from simulation.net_new_acquisition import SETTLEMENT_CUSTOMER_YEAR_BUDGET
    from simulation.premise_population import ScaleProbeUnavailable, load_whole_run_rss_curve

    try:
        curve = load_whole_run_rss_curve()
    except (ScaleProbeUnavailable, OSError, ValueError) as exc:
        return None, f"no measured run curve to price the budget on ({exc})"
    budget = float(SETTLEMENT_CUSTOMER_YEAR_BUDGET)
    peak = curve["anchor_peak_rss_mb"] + (
        (budget - curve["anchor_customer_years"]) * curve["mb_per_customer_year"])
    return peak, (
        f"{curve['anchor_peak_rss_mb']:,.1f} MB at {curve['anchor_customer_years']:,.1f} "
        f"customer-years + {curve['mb_per_customer_year']:.3f} MB each up to the "
        f"{budget:,.0f} customer-year settlement budget, from {curve['path']}")


def entry_headroom_refusal(sample_fn=None, peak_fn=None) -> str | None:
    """Why this box cannot start a run now, or None when MemAvailable covers the budgeted peak.

    Sits in the entry point and not only in `launch_long_job`'s admission door, because the
    2026-10-07 11:52Z near-miss (1.6 GB of 24 GB free) was runs started with `setsid` around the
    door. Fails closed: an unreadable /proc or an unpriced run refuses, naming which.
    """
    peak, basis = (peak_fn or budgeted_run_peak_mb)()
    if peak is None:
        return f"the run's peak cannot be priced -- {basis} -- so it cannot be shown to fit"
    if sample_fn is None:
        from background.resource_headroom import sample as sample_fn
    obs = sample_fn()
    available = obs.get("available_mb")
    if available is None:
        return (f"/proc/meminfo gave no MemAvailable, so this box cannot be shown to hold the "
                f"run's budgeted {peak:,.0f} MB peak")
    if available >= peak:
        return None
    return (f"{available:,.0f} MB available of {obs.get('total_mb') or 0:,.0f} MB, and the run's "
            f"budgeted peak is {peak:,.0f} MB ({basis}). A run that dies mid-way lands nothing "
            "and can take other lanes with it; wait for the box to free up")


def cli(main_fn=None, **refusal_kwargs) -> int:
    """`python3 -m simulation.run_phase2b`: refuse a run the box cannot hold, else run it."""
    refusal = entry_headroom_refusal(**refusal_kwargs)
    if refusal:
        print(f"phase 2b run REFUSED: {refusal}", file=sys.stderr)
        return 2
    (main_fn or main)()
    return 0


if __name__ == "__main__":
    sys.exit(cli())
