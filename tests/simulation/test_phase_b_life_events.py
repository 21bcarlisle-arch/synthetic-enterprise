"""Phase B — Life events engine tests.

Tests for simulation/life_events.py: event generation, ordering,
application, and point-in-time reconstruction.
"""

import pytest
from simulation.household import (
    BoilerAge,
    BuildEra,
    HeatingSystem,
    Household,
    InsulationLevel,
    PropertyType,
    make_household,
    build_household_register,
)
from simulation.life_events import (
    LifeEvent,
    apply_events,
    generate_life_events,
    household_at_date,
    _SOLAR_INSTALL_PROB_BY_YEAR,
    _EV_ACQUIRED_PROB_BY_YEAR,
    _HEAT_PUMP_INSTALL_PROB_BY_YEAR,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _semi(epc="D", home_type="suburban_semi", segment="resi") -> Household:
    return make_household({
        "customer_id": "T1",
        "home_type": home_type,
        "epc_rating": epc,
        "bedrooms": 3,
        "segment": segment,
    })


def _flat(epc="D") -> Household:
    return make_household({
        "customer_id": "T2",
        "home_type": "urban_flat",
        "epc_rating": epc,
        "bedrooms": 2,
        "segment": "resi",
    })


def _detached(epc="E") -> Household:
    return make_household({
        "customer_id": "T3",
        "home_type": "rural_detached",
        "epc_rating": epc,
        "bedrooms": 4,
        "segment": "resi",
    })


# ---------------------------------------------------------------------------
# LifeEvent dataclass
# ---------------------------------------------------------------------------

def test_life_event_is_immutable():
    e = LifeEvent("C1", "2020-06-01", "solar_install", {"solar_kwp": 3.8})
    with pytest.raises(Exception):
        e.event_type = "ev_acquired"  # type: ignore[misc]


def test_life_event_date_ordering():
    events = [
        LifeEvent("C1", "2022-03-15", "boiler_replaced", {"boiler_age": "new"}),
        LifeEvent("C1", "2020-01-10", "solar_install", {"solar_kwp": 3.5}),
        LifeEvent("C1", "2021-07-20", "ev_acquired", {"ev_charger_kw": 7.0}),
    ]
    events.sort(key=lambda e: e.event_date)
    assert events[0].event_date == "2020-01-10"
    assert events[-1].event_date == "2022-03-15"


# ---------------------------------------------------------------------------
# Probability tables
# ---------------------------------------------------------------------------

def test_solar_prob_table_covers_all_sim_years():
    for year in range(2016, 2026):
        assert year in _SOLAR_INSTALL_PROB_BY_YEAR, f"{year} missing from solar prob table"


def test_ev_prob_table_covers_all_sim_years():
    for year in range(2016, 2026):
        assert year in _EV_ACQUIRED_PROB_BY_YEAR, f"{year} missing from EV prob table"


def test_heat_pump_prob_table_covers_all_sim_years():
    for year in range(2016, 2026):
        assert year in _HEAT_PUMP_INSTALL_PROB_BY_YEAR, f"{year} missing from ASHP prob table"


def test_solar_prob_rises_during_energy_crisis():
    assert _SOLAR_INSTALL_PROB_BY_YEAR[2022] > _SOLAR_INSTALL_PROB_BY_YEAR[2018]


def test_ev_prob_rises_monotonically_to_2024():
    for y in range(2016, 2024):
        assert _EV_ACQUIRED_PROB_BY_YEAR[y] <= _EV_ACQUIRED_PROB_BY_YEAR[y + 1], \
            f"EV prob not monotone: {y} → {y+1}"


def test_heat_pump_prob_rises_monotonically():
    for y in range(2016, 2025):
        assert _HEAT_PUMP_INSTALL_PROB_BY_YEAR[y] <= _HEAT_PUMP_INSTALL_PROB_BY_YEAR[y + 1], \
            f"ASHP prob not monotone: {y} → {y+1}"


# ---------------------------------------------------------------------------
# generate_life_events — determinism and ordering
# ---------------------------------------------------------------------------

def test_generate_events_is_deterministic():
    h = _semi()
    e1 = generate_life_events(h, 2016, 2025, seed=42)
    e2 = generate_life_events(h, 2016, 2025, seed=42)
    assert e1 == e2


def test_generate_events_returns_sorted_by_date():
    h = _semi()
    events = generate_life_events(h, 2016, 2025, seed=42)
    dates = [e.event_date for e in events]
    assert dates == sorted(dates)


def test_generate_events_customer_id_on_all_events():
    h = _semi()
    events = generate_life_events(h, 2016, 2025, seed=123)
    for e in events:
        assert e.customer_id == h.customer_id


def test_generate_events_different_seeds_may_differ():
    h = _semi()
    e1 = generate_life_events(h, 2016, 2025, seed=1)
    e2 = generate_life_events(h, 2016, 2025, seed=9999)
    # Not guaranteed to differ, but extremely unlikely to be identical over 10 years
    # This is a probabilistic assertion; if it fails with a different seed pair, revisit.
    # Using a flag: at minimum one event type list should differ
    types1 = [e.event_type for e in e1]
    types2 = [e.event_type for e in e2]
    # At worst: both have zero events; accept that but flag in comment
    # More usefully, check both are valid (all event types in known set)
    valid_types = {"solar_install", "ev_acquired", "boiler_replaced",
                   "heat_pump_installed", "battery_installed",
                   "smart_meter_installed", "insulation_upgraded",
                   "job_loss", "income_recovery", "new_baby", "retirement_starts"}
    for e in e1 + e2:
        assert e.event_type in valid_types


# ---------------------------------------------------------------------------
# generate_life_events — physical constraints
# ---------------------------------------------------------------------------

def test_flat_does_not_get_solar():
    # Flats can't install rooftop solar
    h = _flat()
    # Use a fixed seed and check across many seeds — none should produce solar for a flat
    for seed in range(20):
        events = generate_life_events(h, 2016, 2025, seed=seed)
        solar_events = [e for e in events if e.event_type == "solar_install"]
        assert solar_events == [], f"Seed {seed}: flat got solar panel"


def test_solar_already_installed_not_duplicated():
    # rural_detached already has solar in make_household
    h = _detached()
    assert h.has_solar is True
    events = generate_life_events(h, 2016, 2025, seed=7)
    solar_events = [e for e in events if e.event_type == "solar_install"]
    assert solar_events == []


def test_battery_only_after_solar():
    h = _semi()
    events = generate_life_events(h, 2016, 2025, seed=42)
    solar_dates = {e.event_date for e in events if e.event_type == "solar_install"}
    battery_events = [e for e in events if e.event_type == "battery_installed"]
    for b in battery_events:
        # Battery date must not precede all solar dates
        assert any(s <= b.event_date for s in solar_dates) or h.has_solar, \
            f"Battery at {b.event_date} with no prior solar"


def test_heat_pump_only_for_gas_heated_resi():
    # I&C warehouse: district heat, not residential
    h = make_household({
        "customer_id": "IC1",
        "home_type": "warehouse_unit",
        "epc_rating": "C",
        "segment": "I&C",
        "metering": "HH",
    })
    events = generate_life_events(h, 2016, 2025, seed=5)
    hp_events = [e for e in events if e.event_type == "heat_pump_installed"]
    assert hp_events == []


def test_ev_only_for_residential():
    h = make_household({
        "customer_id": "IC2",
        "home_type": "warehouse_unit",
        "epc_rating": "C",
        "segment": "I&C",
        "metering": "HH",
    })
    events = generate_life_events(h, 2016, 2025, seed=5)
    ev_events = [e for e in events if e.event_type == "ev_acquired"]
    assert ev_events == []


def test_ev_not_duplicated():
    h = _semi()
    for seed in range(5):
        events = generate_life_events(h, 2016, 2025, seed=seed)
        ev_events = [e for e in events if e.event_type == "ev_acquired"]
        assert len(ev_events) <= 1, f"Seed {seed}: EV acquired twice"


# ---------------------------------------------------------------------------
# apply_events
# ---------------------------------------------------------------------------

def test_apply_solar_event():
    h = _semi()
    events = [LifeEvent("T1", "2019-05-01", "solar_install", {"solar_kwp": 4.0})]
    result = apply_events(h, events)
    assert result.has_solar is True
    assert result.solar_kwp == pytest.approx(4.0)
    assert result.solar_install_year == 2019


def test_apply_ev_event():
    h = _semi()
    events = [LifeEvent("T1", "2022-03-15", "ev_acquired", {"ev_charger_kw": 7.0})]
    result = apply_events(h, events)
    assert result.has_ev is True
    assert result.ev_charger_kw == pytest.approx(7.0)


def test_apply_heat_pump_event():
    h = _semi()
    events = [LifeEvent("T1", "2023-08-01", "heat_pump_installed",
                        {"heating_system": "heat_pump_air"})]
    result = apply_events(h, events)
    assert result.is_heat_pump
    assert not result.is_gas_heated
    assert result.boiler_age == BoilerAge.NA


def test_apply_boiler_replaced_event():
    h = make_household({
        "customer_id": "C3",
        "home_type": "tenement_flat",
        "epc_rating": "E",
        "bedrooms": 2,
        "segment": "resi",
    })
    # Tenement flat → PRE_1919 → OLD boiler
    assert h.boiler_age == BoilerAge.OLD
    events = [LifeEvent("C3", "2020-11-01", "boiler_replaced", {"boiler_age": "new"})]
    result = apply_events(h, events)
    assert result.boiler_age == BoilerAge.NEW


def test_apply_insulation_upgraded_poor_to_partial():
    h = _semi(epc="E")  # EPC E → POOR insulation
    assert h.insulation == InsulationLevel.POOR
    events = [LifeEvent("T1", "2021-02-01", "insulation_upgraded",
                        {"insulation": "partial"})]
    result = apply_events(h, events)
    assert result.insulation == InsulationLevel.PARTIAL


def test_apply_battery_event():
    h = _semi()
    # First add solar, then battery
    events = [
        LifeEvent("T1", "2018-06-01", "solar_install", {"solar_kwp": 3.5}),
        LifeEvent("T1", "2020-04-15", "battery_installed", {"battery_kwh": 9.5}),
    ]
    result = apply_events(h, events)
    assert result.has_battery is True
    assert result.battery_kwh == pytest.approx(9.5)


def test_apply_empty_events_returns_unchanged_household():
    h = _semi()
    result = apply_events(h, [])
    assert result == h


def test_apply_events_preserves_unchanged_fields():
    h = _semi()
    events = [LifeEvent("T1", "2019-05-01", "solar_install", {"solar_kwp": 3.0})]
    result = apply_events(h, events)
    # Unchanged fields should be identical
    assert result.property_type == h.property_type
    assert result.build_era == h.build_era
    assert result.epc_rating == h.epc_rating
    assert result.bedrooms == h.bedrooms
    assert result.heating_system == h.heating_system


# ---------------------------------------------------------------------------
# household_at_date
# ---------------------------------------------------------------------------

def test_household_at_date_before_any_event():
    h = _semi()
    events = [LifeEvent("T1", "2021-06-01", "solar_install", {"solar_kwp": 3.5})]
    result = household_at_date(h, events, "2020-12-31")
    assert result.has_solar is False


def test_household_at_date_on_event_date_includes_event():
    h = _semi()
    events = [LifeEvent("T1", "2021-06-01", "solar_install", {"solar_kwp": 3.5})]
    result = household_at_date(h, events, "2021-06-01")
    assert result.has_solar is True


def test_household_at_date_after_event():
    h = _semi()
    events = [LifeEvent("T1", "2021-06-01", "ev_acquired", {"ev_charger_kw": 7.0})]
    result = household_at_date(h, events, "2025-01-01")
    assert result.has_ev is True


def test_household_at_date_partial_event_window():
    h = _semi()
    events = [
        LifeEvent("T1", "2018-03-01", "solar_install", {"solar_kwp": 3.0}),
        LifeEvent("T1", "2022-07-01", "ev_acquired", {"ev_charger_kw": 7.0}),
    ]
    result = household_at_date(h, events, "2020-01-01")
    assert result.has_solar is True   # solar installed 2018
    assert result.has_ev is False     # EV not yet acquired


# ---------------------------------------------------------------------------
# Integration: generate + apply round-trip
# ---------------------------------------------------------------------------

def test_round_trip_is_idempotent():
    h = _semi(epc="E")
    events = generate_life_events(h, 2016, 2025, seed=77)
    final = apply_events(h, events)
    # Re-applying the same events should yield the same result
    final2 = apply_events(h, events)
    assert final == final2


def test_all_real_customers_generate_events_without_error():
    from simulation.run_phase2b import CUSTOMERS
    register = build_household_register(CUSTOMERS)
    for cid, h in register.items():
        events = generate_life_events(h, 2016, 2025)
        # Must all be valid LifeEvent instances
        for e in events:
            assert isinstance(e, LifeEvent)
            assert e.customer_id == cid


# ---------------------------------------------------------------------------
# RESIDENTIAL-ONLY demographic-event contract (W2_5 HARDEN, 2026-07-16)
#
# Demographic / economic life events (job_loss, income_recovery, new_baby,
# retirement_starts, illness, divorce) model PEOPLE in a dwelling and must NEVER
# fire for a business (SME/I&C) account -- an SME has no "new baby" (R10
# absurdity class; W2_6_sme_distress_twin models business distress instead).
# These are the CLASS-LEVEL controls that make that absurdity fail automatically
# rather than an instance fix (R10), and they are mutation-provable (R15): the
# gate is shown to be load-bearing, not vacuously passing.
# ---------------------------------------------------------------------------

from simulation.life_events import _RESIDENTIAL_ONLY_DEMOGRAPHIC_EVENTS

# Every non-residential (business) home_type in _HOME_TYPE_TO_PROPERTY.
_BUSINESS_HOME_TYPES = [
    "small_office",       # commercial_office
    "warehouse_unit",     # commercial_warehouse
    "office_building",    # commercial_office
    "chemical_plant",     # industrial
    "supermarket",        # commercial_warehouse
]


def _business_household(home_type: str, cid: str = "BIZ") -> Household:
    return make_household({
        "customer_id": cid,
        "home_type": home_type,
        "epc_rating": "C",
        "segment": "I&C",
        "metering": "HH",
    })


def test_demographic_event_set_is_exactly_the_gated_events():
    # Guards the contract itself: the named constant must list precisely the
    # economic/demographic events, so a future addition can't silently escape
    # the residential gate by being omitted from this set.
    assert _RESIDENTIAL_ONLY_DEMOGRAPHIC_EVENTS == frozenset({
        "job_loss", "income_recovery", "new_baby",
        "retirement_starts", "illness", "divorce",
    })


def test_no_demographic_events_for_business_property():
    # THE CONTROL: no business-property household may ever receive a
    # residential demographic event, across every business property type and a
    # wide seed sweep (not a single lucky seed).
    for home_type in _BUSINESS_HOME_TYPES:
        h = _business_household(home_type)
        assert not h.is_residential, f"{home_type} unexpectedly residential"
        for seed in range(300):
            events = generate_life_events(h, 2016, 2025, seed=seed)
            leaked = [e.event_type for e in events
                      if e.event_type in _RESIDENTIAL_ONLY_DEMOGRAPHIC_EVENTS]
            assert leaked == [], (
                f"{home_type} seed {seed}: business account received "
                f"residential demographic events {leaked}"
            )


def test_demographic_gate_is_load_bearing():
    # MUTATION / can-fail proof (R15): the SAME seeds that produce ZERO
    # demographic events for a business household DO produce them for a
    # residential household -- so the exclusion above is the is_residential
    # gate doing real work, not the events simply never firing. If the gate
    # were removed, test_no_demographic_events_for_business_property would fail.
    h = _semi()
    assert h.is_residential
    fired = set()
    for seed in range(300):
        events = generate_life_events(h, 2016, 2025, seed=seed)
        fired |= {e.event_type for e in events
                  if e.event_type in _RESIDENTIAL_ONLY_DEMOGRAPHIC_EVENTS}
    # Over 300 seeds a residential household reaches multiple demographic
    # events; require at least the common ones so the control is demonstrably
    # exercising a live code path, not a dead branch.
    assert "job_loss" in fired
    assert len(fired) >= 3, f"residential demographic events seen: {sorted(fired)}"


def test_business_household_only_emits_physical_adoption_events():
    # Belt-and-braces: whatever a business household DOES emit must be drawn
    # only from the physical-adoption event types, never a demographic one.
    # Catches a newly-added demographic event that forgets the residential gate.
    h = _business_household("warehouse_unit")
    seen = set()
    for seed in range(300):
        seen |= {e.event_type for e in generate_life_events(h, 2016, 2025, seed=seed)}
    assert seen & _RESIDENTIAL_ONLY_DEMOGRAPHIC_EVENTS == set(), (
        f"business household emitted demographic events: "
        f"{sorted(seen & _RESIDENTIAL_ONLY_DEMOGRAPHIC_EVENTS)}"
    )


def test_real_roster_business_segment_never_residential():
    # R10 class-level closure over the REAL customer book: every business-segment
    # (SME/I&C) customer must map to a NON-residential property_type AND receive
    # zero demographic events. If a future roster edit puts an SME/I&C account in
    # a residential dwelling (making is_residential a wrong proxy for segment),
    # this fails loudly -- the property_type gate can no longer silently diverge
    # from the segment it stands in for.
    from simulation.run_phase2b import CUSTOMERS
    for c in CUSTOMERS:
        seg = c.get("segment", "resi")
        if seg not in ("SME", "I&C"):
            continue
        h = make_household(c)
        assert not h.is_residential, (
            f"{c['customer_id']} is segment {seg} but maps to residential "
            f"property_type {h.property_type.value} -- demographic life events "
            f"would wrongly fire (R10 absurdity)"
        )
        for seed in range(50):
            events = generate_life_events(h, 2016, 2025, seed=seed)
            leaked = [e.event_type for e in events
                      if e.event_type in _RESIDENTIAL_ONLY_DEMOGRAPHIC_EVENTS]
            assert leaked == [], f"{c['customer_id']} ({seg}) leaked {leaked}"


# ---------------------------------------------------------------------------
# W2_5 HARDEN 2026-07-24 (Rule-0 self-refill, dial yielded): emission-gate vs
# canonical-timeline consistency.
#
# generate_life_events() gates the ==LOW-only demographic events (new_baby,
# divorce) on income_stress mutated in a FIXED per-year PROCESSING order
# (income_recovery is processed before new_baby/divorce). But each event's
# DATE is an independent per-substream draw, and apply_events() -- the ONLY
# income_stress any consumer sees (household_demand.income_stress_at_date ->
# churn + bad-debt) -- replays in DATE order. So when a same-year
# income_recovery is dated AFTER a new_baby/divorce it enabled, the canonical
# (date-ordered) timeline places the LOW-gated event while the household is
# still HIGH-stress: the event's own emission precondition is violated in the
# authoritative timeline (a "divorce only when stable income" event happening
# to a HIGH-stress household).
#
# QUEUED DEFECT, not fixed here (SELF_INTERRUPT_DISCIPLINE + R4 + R10): the fix
# is a core-generation-loop change (evaluate the within-year demographic gates
# in date order) that shifts every household's event stream -> full sim re-run
# + downstream triage -> a BUILD, not a bounded HARDEN patch. See the W2_5
# maturity-map simplifications entry. These two controls MECHANISE the defect
# (MAKE_IT_STICK): the seed-42 control proves it is NOT live in production; the
# xfail(strict) control encodes the invariant, is proven to FIRE on the live
# defect (R15 can-fail), and auto-alarms (XPASS -> strict failure) the day the
# generator is fixed, forcing this note + the map entry to be closed.
# ---------------------------------------------------------------------------

from simulation.household import IncomeStress

_LOW_GATED_DEMOGRAPHIC_EVENTS = {"new_baby", "divorce"}


def _stress_before(household: Household, events, event) -> IncomeStress:
    """income_stress in the canonical (date-ordered) timeline just before `event`."""
    prior = [e for e in events if e.event_date < event.event_date]
    return apply_events(household, prior).income_stress


def _lowgate_violations(household: Household, seeds) -> list:
    """LOW-gated demographic events that land while NOT low-stress in the
    reconstructed (consumer-visible) timeline."""
    out = []
    for seed in seeds:
        events = generate_life_events(household, 2016, 2025, seed=seed)
        for e in events:
            if e.event_type in _LOW_GATED_DEMOGRAPHIC_EVENTS:
                if _stress_before(household, events, e) != IncomeStress.LOW:
                    out.append((seed, e.event_date, e.event_type))
    return out


def test_lowgated_demographic_events_hold_on_real_roster_seed42():
    # Production roster + production seed: proves the emission/reconstruction
    # divergence is NOT LIVE today (a latent hole, same class as the
    # residential-gate finding). If a future roster/seed change makes it live,
    # this fails loudly rather than the defect silently entering production.
    from simulation.run_phase2b import CUSTOMERS
    register = build_household_register(CUSTOMERS)
    for cid, hh in register.items():
        if not hh.is_residential:
            continue
        cid_seed = 42 ^ (int(__import__("hashlib").md5(cid.encode()).hexdigest()[:8], 16) & 0xFFFF)
        v = _lowgate_violations(hh, [cid_seed])
        assert v == [], (
            f"{cid}: LOW-gated demographic event lands while not low-stress in "
            f"the canonical timeline {v} -- the W2_5 emission/reconstruction "
            f"defect is now LIVE in production"
        )


@pytest.mark.xfail(strict=True, reason=(
    "W2_5 QUEUED DEFECT (2026-07-24): new_baby/divorce are gated on "
    "income_stress==LOW in the generator's fixed PROCESSING order, but "
    "apply_events (the value consumers see) replays in DATE order, so a "
    "same-year later income_recovery can leave the LOW-gated event landing "
    "while the household is still HIGH-stress (~1.4% of such events on the "
    "real roster across seeds). Fix = date-order the within-year gate "
    "evaluation (a BUILD: shifts every event stream, needs a full sim run). "
    "When fixed, this XPASSes -> strict failure -> close this note + the map."
))
def test_lowgated_demographic_gate_holds_in_canonical_timeline():
    # THE INVARIANT (currently violated -> xfail): every LOW-gated demographic
    # event must land at a date when the reconstructed income_stress is LOW.
    # Proven to FIRE on the real defect (R15 can-fail): a HIGH-start
    # residential household over seeds 0-999 contains real violations today.
    hh = Household(
        customer_id="HS", property_type=PropertyType.SEMI_DETACHED,
        build_era=BuildEra.POST_2000, epc_rating="C", bedrooms=3,
        heating_system=HeatingSystem.GAS_BOILER_COMBI, boiler_age=BoilerAge.MID,
        has_solar=False, solar_kwp=0.0, solar_install_year=None,
        has_battery=False, battery_kwh=0.0, has_ev=False, ev_charger_kw=0.0,
        has_smart_meter=False, smart_meter_install_year=None,
        insulation=InsulationLevel.PARTIAL, has_driveway=True, roof_aspect="S",
        income_stress=IncomeStress.HIGH,
    )
    violations = _lowgate_violations(hh, range(1000))
    assert violations == [], (
        f"{len(violations)} LOW-gated demographic events land while not "
        f"low-stress in the canonical timeline, e.g. {violations[:3]}"
    )


# ---------------------------------------------------------------------------
# SEGMENTATION_GENERATOR_BUILD_PLAN.md step 2: tenure->low-carbon-adoption
# gating MECHANISM (`adoption_eligibility_multiplier`). Default OFF (1.0) so
# every existing call site is byte-identical; the multiplier measurably
# reduces solar_install/ev_acquired/heat_pump_installed frequency and leaves
# every other event type untouched.
# ---------------------------------------------------------------------------

_ADOPTION_EVENT_TYPES = {"solar_install", "ev_acquired", "heat_pump_installed"}


def test_default_multiplier_is_byte_identical_to_no_multiplier():
    h = _semi()
    for seed in range(30):
        a = generate_life_events(h, 2016, 2025, seed=seed)
        b = generate_life_events(h, 2016, 2025, seed=seed, adoption_eligibility_multiplier=1.0)
        assert a == b


def test_lower_multiplier_never_increases_adoption_events_and_reduces_them_on_average():
    h = _semi()
    default_count = 0
    gated_count = 0
    for seed in range(400):
        default_events = generate_life_events(h, 2016, 2025, seed=seed)
        gated_events = generate_life_events(h, 2016, 2025, seed=seed, adoption_eligibility_multiplier=0.17)
        default_count += sum(1 for e in default_events if e.event_type in _ADOPTION_EVENT_TYPES)
        gated_count += sum(1 for e in gated_events if e.event_type in _ADOPTION_EVENT_TYPES)
    assert gated_count < default_count, (
        f"gated multiplier (0.17) did not reduce adoption events: "
        f"default={default_count} gated={gated_count}"
    )


def test_multiplier_leaves_non_adoption_events_untouched():
    # boiler_replaced / insulation_upgraded / economic-demographic events must
    # be byte-identical regardless of adoption_eligibility_multiplier -- the
    # gate is scoped to the three named low-carbon adoption event types only.
    h = _semi()
    for seed in range(60):
        default_events = generate_life_events(h, 2016, 2025, seed=seed)
        gated_events = generate_life_events(h, 2016, 2025, seed=seed, adoption_eligibility_multiplier=0.17)
        non_adoption_default = [e for e in default_events if e.event_type not in _ADOPTION_EVENT_TYPES]
        non_adoption_gated = [e for e in gated_events if e.event_type not in _ADOPTION_EVENT_TYPES]
        assert non_adoption_default == non_adoption_gated


def test_multiplier_zero_eliminates_adoption_events():
    h = _semi()
    seen = set()
    for seed in range(200):
        events = generate_life_events(h, 2016, 2025, seed=seed, adoption_eligibility_multiplier=0.0)
        seen |= {e.event_type for e in events if e.event_type in _ADOPTION_EVENT_TYPES}
    assert seen == set()


def test_multiplier_is_clamped_to_zero_one_range():
    # A malformed >1 or negative caller value must never manufacture
    # probability mass above 1.0 or below 0.0 (R15 fail-closed) -- clamped
    # silently to the valid range rather than raising, since a curriculum
    # value is a director dial, not a hard programmer contract.
    h = _semi()
    for seed in range(30):
        over_one = generate_life_events(h, 2016, 2025, seed=seed, adoption_eligibility_multiplier=5.0)
        at_one = generate_life_events(h, 2016, 2025, seed=seed, adoption_eligibility_multiplier=1.0)
        assert over_one == at_one
        negative = generate_life_events(h, 2016, 2025, seed=seed, adoption_eligibility_multiplier=-3.0)
        at_zero = generate_life_events(h, 2016, 2025, seed=seed, adoption_eligibility_multiplier=0.0)
        assert negative == at_zero


# ---------------------------------------------------------------------------
# FROM_AGENT_SEGMENTATION_INTEGRATION_FOLLOWON item 2: PER-ASSET dict form
# (director CONFIRMED 2026-07-22). Each of the three gates uses its own asset's
# factor; a uniform dict is byte-identical to the scalar; the independent C-S2
# substreams mean zeroing one asset's gate leaves the other two byte-identical.
# ---------------------------------------------------------------------------
_ASSET_OF_EVENT = {"solar_install": "solar_pv", "ev_acquired": "ev", "heat_pump_installed": "heat_pump"}


def test_uniform_per_asset_dict_is_byte_identical_to_the_scalar():
    h = _semi()
    for seed in range(60):
        scalar = generate_life_events(h, 2016, 2025, seed=seed, adoption_eligibility_multiplier=0.17)
        uniform = generate_life_events(
            h, 2016, 2025, seed=seed,
            adoption_eligibility_multiplier={"solar_pv": 0.17, "ev": 0.17, "heat_pump": 0.17},
        )
        assert scalar == uniform


def test_per_asset_dict_gates_only_its_own_asset():
    # Zero solar, leave ev + heat_pump ungated. Independent substreams (C-S2)
    # mean the ev/heat_pump events are byte-identical to the fully-ungated run,
    # while solar_install is eliminated -- proof the gate is per-asset, not shared.
    h = _semi()
    per_asset = {"solar_pv": 0.0, "ev": 1.0, "heat_pump": 1.0}
    saw_solar = False
    for seed in range(200):
        default = generate_life_events(h, 2016, 2025, seed=seed)
        gated = generate_life_events(h, 2016, 2025, seed=seed, adoption_eligibility_multiplier=per_asset)
        assert not [e for e in gated if e.event_type == "solar_install"]
        # ev + heat_pump (and every non-adoption event) unchanged from default
        default_kept = [e for e in default if e.event_type != "solar_install"]
        gated_kept = [e for e in gated if e.event_type != "solar_install"]
        assert default_kept == gated_kept
        saw_solar |= any(e.event_type == "solar_install" for e in default)
    assert saw_solar, "test household never adopted solar in the ungated arm -- widen seeds"


def test_missing_asset_key_defaults_to_ungated():
    # A partial dict (only solar named) leaves ev + heat_pump at 1.0 (ungated) --
    # byte-identical to the fully-default run for those two gates.
    h = _semi()
    for seed in range(60):
        default = generate_life_events(h, 2016, 2025, seed=seed)
        partial = generate_life_events(
            h, 2016, 2025, seed=seed, adoption_eligibility_multiplier={"solar_pv": 0.0},
        )
        default_non_solar = [e for e in default if e.event_type != "solar_install"]
        partial_non_solar = [e for e in partial if e.event_type != "solar_install"]
        assert default_non_solar == partial_non_solar
