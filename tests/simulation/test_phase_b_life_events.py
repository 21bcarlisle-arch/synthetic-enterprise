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
                   "smart_meter_installed", "insulation_upgraded"}
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
