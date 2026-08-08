"""W1_12 premise trace generator — Layer 2 behaviour on W1_11 fabric physics.

R15 DISCIPLINE: every control in `simulation.premise_trace` is exercised BOTH
ways here — it passes on the real generator AND a named mutation proves it fires
on the specific defect it exists to catch. A control that cannot fail is worse
than none, so a bare "control returns True" assertion is never sufficient on its
own and never appears alone in this file.

The defects being controlled for are the MEASURED ones from the 2026-08-03
demotion of `W1_5_premise_demand_shape` (L3 -> L1): day-vs-next-day shape
correlation 0.97, no half-hour below 0.05 kWh in ten years, annual totals within
8% of each other, and one national HDD constant applied to every home.
"""

from __future__ import annotations

import dataclasses
import datetime as dt
import math

import pytest

from simulation import premise_trace as pt
from simulation.household import (
    BoilerAge,
    BuildEra,
    HeatingSystem,
    Household,
    InsulationLevel,
    PropertyType,
)

# Short windows keep this suite cheap: generation costs ~0.5 s per premise-year,
# so every fixture below is scoped and reused rather than regenerated per test.
WINDOW_START = dt.date(2022, 1, 1)
WINDOW_END = dt.date(2022, 6, 30)


def make_household(
    customer_id: str = "C1",
    *,
    property_type: PropertyType = PropertyType.SEMI_DETACHED,
    build_era: BuildEra = BuildEra.ERA_1965_1980,
    insulation: InsulationLevel = InsulationLevel.PARTIAL,
    heating_system: HeatingSystem = HeatingSystem.GAS_BOILER_COMBI,
    bedrooms: int | None = 3,
    has_solar: bool = False,
    solar_kwp: float = 0.0,
    has_ev: bool = False,
    ev_charger_kw: float = 0.0,
    roof_aspect: str = "south",
) -> Household:
    return Household(
        customer_id=customer_id,
        property_type=property_type,
        build_era=build_era,
        epc_rating="D",
        bedrooms=bedrooms,
        heating_system=heating_system,
        boiler_age=BoilerAge.MID,
        has_solar=has_solar,
        solar_kwp=solar_kwp,
        solar_install_year=2019 if has_solar else None,
        has_battery=False,
        battery_kwh=0.0,
        has_ev=has_ev,
        ev_charger_kw=ev_charger_kw,
        has_smart_meter=True,
        smart_meter_install_year=2020,
        insulation=insulation,
        has_driveway=True,
        roof_aspect=roof_aspect,
    )


@pytest.fixture(scope="module")
def weather() -> list[pt.TraceWeatherDay]:
    """The REAL Open-Meteo reanalysis archive — Historical Ground Truth, not a
    synthetic shape. If this file is missing the suite must FAIL, not skip."""
    return pt.load_trace_weather("C1", start=WINDOW_START, end=WINDOW_END)


@pytest.fixture(scope="module")
def trace(weather) -> pt.PremiseTrace:
    return pt.generate_premise_trace(
        premise_id="P-base", household=make_household(), weather=weather, seed=42, latitude_deg=pt.DEFAULT_LATITUDE_DEG)


# ---------------------------------------------------------------------------
# The generator runs, on real weather, and produces a physical trace
# ---------------------------------------------------------------------------


def test_generates_a_half_hourly_trace_over_the_real_archive(trace, weather):
    assert len(trace.days) == len(weather)
    for day in trace.days:
        assert len(day.electricity_kwh) == pt.PERIODS_PER_DAY
        assert len(day.gas_kwh) == pt.PERIODS_PER_DAY
        assert len(day.indoor_air_c) == pt.PERIODS_PER_DAY
        for value in day.electricity_kwh:
            assert math.isfinite(value) and value >= 0.0
        for value in day.gas_kwh:
            assert math.isfinite(value) and value >= 0.0


def test_a_gas_heated_premise_puts_its_heat_in_gas_not_electricity(trace):
    """The commodity split is a real supplier's most basic fact about a premise."""
    assert trace.heating_commodity == "gas"
    assert sum(sum(d.gas_kwh) for d in trace.days) > 0.0
    for day in trace.days:
        # A gas-heated premise burns gas for space heat AND hot water; nothing
        # else reaches the gas meter.
        assert sum(day.gas_kwh) == pytest.approx(
            sum(day.heating_fuel_kwh) + sum(day.dhw_fuel_kwh), rel=1e-9
        )


def test_annual_levels_sit_in_the_external_anchor_band(trace):
    """G.1 against Ofgem TDCV — a DIAGNOSTIC band (R12), never a target. The
    generator is not tuned toward it; a breach triggers R4."""
    assert pt.annual_level_in_band(trace.annual_kwh("gas"), (5_000.0, 20_000.0), label="gas")
    assert pt.annual_level_in_band(
        trace.annual_kwh("electricity"), (1_200.0, 6_000.0), label="electricity"
    )


# ---------------------------------------------------------------------------
# C-S2 — determinism and substream isolation
# ---------------------------------------------------------------------------


def test_the_same_premise_and_seed_reproduce_the_trace_exactly(weather):
    kwargs = dict(
        premise_id="P-det", household=make_household(), weather=weather[:60], seed=11
    )
    a = pt.generate_premise_trace(**kwargs, latitude_deg=pt.DEFAULT_LATITUDE_DEG)
    b = pt.generate_premise_trace(**kwargs, latitude_deg=pt.DEFAULT_LATITUDE_DEG)
    assert [list(d.electricity_kwh) for d in a.days] == [
        list(d.electricity_kwh) for d in b.days
    ]
    assert [list(d.gas_kwh) for d in a.days] == [list(d.gas_kwh) for d in b.days]


def test_two_premises_differ_structurally_not_by_injected_noise(weather):
    """Diversity must come from the STRUCTURAL per-premise draw. Same fabric,
    same weather, different premise id -> different trace."""
    a = pt.generate_premise_trace(
        premise_id="P-a", household=make_household("C1"), weather=weather[:60], seed=5, latitude_deg=pt.DEFAULT_LATITUDE_DEG)
    b = pt.generate_premise_trace(
        premise_id="P-b", household=make_household("C2"), weather=weather[:60], seed=5, latitude_deg=pt.DEFAULT_LATITUDE_DEG)
    assert [list(d.electricity_kwh) for d in a.days] != [
        list(d.electricity_kwh) for d in b.days
    ]


def test_this_module_draws_from_its_own_named_substream():
    """C-S2: a draw here can never shift another subsystem's sequence."""
    assert pt.STREAM_NAME == "W1_12_premise_trace"
    from simulation import fabric_physics

    assert pt.STREAM_NAME != fabric_physics.STREAM_NAME


# ---------------------------------------------------------------------------
# THE SEPARABILITY CONTRACT — the atom's hard requirement, both halves
# ---------------------------------------------------------------------------


def _pinned_layer_two(weather, *, premise_id="P-sep", seed=7):
    """Layer 2 held EXACTLY fixed so only the fabric can move."""
    household = make_household()
    behaviour = pt.behaviour_profile_for(premise_id, household, seed=seed)
    away = pt.away_day_calendar(premise_id, behaviour, [d.date for d in weather], seed=seed)
    return dict(
        premise_id=premise_id, weather=weather, seed=seed, behaviour=behaviour, away_days=away
    )


def test_fabric_only_moves_level_and_character(weather):
    """Half one: hold Layer 2 fixed, vary the fabric -> only level+character move."""
    common = _pinned_layer_two(weather)
    leaky = pt.generate_premise_trace(
        household=make_household(insulation=InsulationLevel.POOR, build_era=BuildEra.PRE_1919),
        **common, latitude_deg=pt.DEFAULT_LATITUDE_DEG)
    tight = pt.generate_premise_trace(
        household=make_household(insulation=InsulationLevel.FULL, build_era=BuildEra.POST_2000),
        **common, latitude_deg=pt.DEFAULT_LATITUDE_DEG)
    assert pt.fabric_only_moves_level_and_character(leaky, tight)


def test_fabric_only_control_FIRES_when_fabric_leaks_into_behaviour(weather):
    """R15 mutation: the thermal model reaching back into the appliance stream is
    the contract violation this control exists to catch."""
    common = _pinned_layer_two(weather)
    leaky = pt.generate_premise_trace(
        household=make_household(insulation=InsulationLevel.POOR, build_era=BuildEra.PRE_1919),
        **common, latitude_deg=pt.DEFAULT_LATITUDE_DEG)
    tight = pt.generate_premise_trace(
        household=make_household(insulation=InsulationLevel.FULL, build_era=BuildEra.POST_2000),
        **common, latitude_deg=pt.DEFAULT_LATITUDE_DEG)
    day = tight.days[0]
    mutated_day = dataclasses.replace(
        day,
        behavioural_electricity_kwh=tuple(v + 0.01 for v in day.behavioural_electricity_kwh),
    )
    mutated = dataclasses.replace(tight, days=(mutated_day,) + tight.days[1:])
    assert not pt.fabric_only_moves_level_and_character(leaky, mutated)


def test_fabric_only_control_FIRES_when_fabric_does_not_move_the_level(weather):
    """R15 mutation: cloning one home is the 'archetype-and-perturb' defect."""
    common = _pinned_layer_two(weather)
    household = make_household()
    a = pt.generate_premise_trace(household=household, **common, latitude_deg=pt.DEFAULT_LATITUDE_DEG)
    b = pt.generate_premise_trace(household=household, **common, latitude_deg=pt.DEFAULT_LATITUDE_DEG)
    # Identical fabric -> heat ratio 1.0 -> the fabric did no work.
    assert not pt.fabric_only_moves_level_and_character(a, b)


def test_behaviour_only_moves_timing_and_volume(weather):
    """Half two: hold the fabric fixed, vary Layer 2 -> only timing+volume move."""
    common = _pinned_layer_two(weather)
    household = make_household()
    base = pt.generate_premise_trace(household=household, **common, latitude_deg=pt.DEFAULT_LATITUDE_DEG)
    shifted_behaviour = dataclasses.replace(
        common["behaviour"],
        wake_period=common["behaviour"].wake_period + 4,
        daytime_occupancy=min(0.95, common["behaviour"].daytime_occupancy + 0.4),
    )
    shifted = pt.generate_premise_trace(
        household=household, **{**common, "behaviour": shifted_behaviour}, latitude_deg=pt.DEFAULT_LATITUDE_DEG)
    assert pt.behaviour_only_moves_timing_and_volume(base, shifted)


def test_behaviour_only_control_FIRES_when_behaviour_moves_the_fabric(weather):
    """R15 mutation: Layer 2 reaching inside the thermal model."""
    common = _pinned_layer_two(weather)
    base = pt.generate_premise_trace(household=make_household(), **common, latitude_deg=pt.DEFAULT_LATITUDE_DEG)
    other_fabric = pt.generate_premise_trace(
        household=make_household(insulation=InsulationLevel.POOR, build_era=BuildEra.PRE_1919),
        **common, latitude_deg=pt.DEFAULT_LATITUDE_DEG)
    assert not pt.behaviour_only_moves_timing_and_volume(base, other_fabric)


def test_behaviour_only_control_FIRES_when_the_seam_is_dead(weather):
    """R15 mutation: a Layer 2 seam that changes nothing is a dead seam — an
    orphan transition (R11), which is a defect and not a pass."""
    common = _pinned_layer_two(weather)
    household = make_household()
    a = pt.generate_premise_trace(household=household, **common, latitude_deg=pt.DEFAULT_LATITUDE_DEG)
    b = pt.generate_premise_trace(household=household, **common, latitude_deg=pt.DEFAULT_LATITUDE_DEG)
    assert not pt.behaviour_only_moves_timing_and_volume(a, b)


# ---------------------------------------------------------------------------
# L1.3 — an empty house must be REPRESENTABLE (the shipped generator's defect)
# ---------------------------------------------------------------------------


def test_away_days_are_representable(trace):
    assert trace.away_days > 0
    assert pt.away_days_are_representable(trace)


def test_away_day_control_FIRES_on_the_shipped_defect(trace):
    """R15 mutation: the MEASURED shipped defect — no half-hour below 0.05 kWh in
    ten years. Flooring the series reproduces it exactly."""
    floored = tuple(
        dataclasses.replace(
            day, electricity_kwh=tuple(max(v, 0.2) for v in day.electricity_kwh)
        )
        for day in trace.days
    )
    assert not pt.away_days_are_representable(dataclasses.replace(trace, days=floored))


def test_an_away_day_falls_to_base_load_but_the_fridge_keeps_running(trace):
    """The always-on load is standby PLUS cycling cold appliances: an empty house
    is not flat, it hums. Zero would make away days trivially detectable in a way
    real meter data is not."""
    away = [d for d in trace.days if d.is_away]
    assert away, "the fixture premise takes no holidays — cannot judge"
    for day in away[:3]:
        overnight = day.electricity_kwh[0:10]
        assert all(v > 0.0 for v in overnight), "an away day went to exactly zero"
        assert min(overnight) < 0.05, "an away day never reached base load"


def test_the_base_load_is_not_a_flat_constant(trace):
    """The cold-appliance cycling model is what removes the smooth series. A flat
    base load would re-introduce the very artefact this atom exists to remove."""
    away = [d for d in trace.days if d.is_away]
    assert away, "the fixture premise takes no holidays — cannot judge"
    overnight = [v for day in away[:5] for v in day.electricity_kwh[0:10]]
    assert len(set(round(v, 6) for v in overnight)) > 3, (
        "overnight base load is effectively constant — the cold-appliance duty "
        "cycle is not reaching the output series"
    )


# ---------------------------------------------------------------------------
# G.2-G.4 — texture, variability and the seasonal shape
# ---------------------------------------------------------------------------


def test_daily_variability_is_non_degenerate(trace):
    assert pt.daily_variability_is_non_degenerate(trace.daily("gas"))


def test_variability_control_FIRES_on_a_smooth_temperature_only_generator(trace):
    """R15 mutation: a daily total that is a smooth function of daily mean
    temperature alone — the shipped generator's shape."""
    flat = [100.0] * len(trace.days)
    assert not pt.daily_variability_is_non_degenerate(flat)


def test_seasonal_gas_ratio_sits_in_its_diagnostic_band(trace):
    doy = [d.day_of_year for d in trace.days]
    assert pt.seasonal_gas_ratio_in_band(trace.daily("gas"), doy)


def test_seasonal_ratio_control_FIRES_outside_the_band(trace):
    """R15 mutation: a premise with no seasonal signal at all."""
    doy = [d.day_of_year for d in trace.days]
    assert not pt.seasonal_gas_ratio_in_band([50.0] * len(doy), doy)


# ---------------------------------------------------------------------------
# G.3 / L2.4 — the population must be diverse (one national constant is the bug)
# ---------------------------------------------------------------------------

POPULATION = [
    ("solid_wall_detached", InsulationLevel.POOR, PropertyType.DETACHED, BuildEra.PRE_1919),
    ("interwar_semi", InsulationLevel.POOR, PropertyType.SEMI_DETACHED, BuildEra.ERA_1919_1944),
    ("postwar_terrace", InsulationLevel.PARTIAL, PropertyType.TERRACED, BuildEra.ERA_1945_1964),
    ("seventies_semi", InsulationLevel.PARTIAL, PropertyType.SEMI_DETACHED, BuildEra.ERA_1965_1980),
    ("eighties_detached", InsulationLevel.PARTIAL, PropertyType.DETACHED, BuildEra.ERA_1981_2000),
    ("modern_flat", InsulationLevel.FULL, PropertyType.FLAT, BuildEra.POST_2000),
]


@pytest.fixture(scope="module")
def population(weather) -> dict[str, pt.PremiseTrace]:
    return {
        name: pt.generate_premise_trace(
            premise_id=name,
            household=make_household(
                f"C-{name}", insulation=ins, property_type=ptype, build_era=era
            ),
            weather=weather,
            seed=200 + i, latitude_deg=pt.DEFAULT_LATITUDE_DEG)
        for i, (name, ins, ptype, era) in enumerate(POPULATION)
    }


def test_per_home_hdd_response_varies_with_fabric(population, weather):
    """G.3: the shipped defect is ONE national constant
    (GAS_HEATING_KWH_PER_DEGREE_DAY = 8.0) applied to every home."""
    temps = [d.weather.temperature_mean_c for d in weather]
    gradients = {
        name: pt.hdd_response_gradient(trace.daily("gas"), temps)
        for name, trace in population.items()
    }
    assert pt.hdd_response_varies_between_homes(gradients)


def test_hdd_spread_control_FIRES_on_one_national_constant(population, weather):
    """R15 mutation: give every home the same gradient — today's shipped model."""
    gradients = {name: 8.0 for name in population}
    assert not pt.hdd_response_varies_between_homes(gradients)


def test_annual_level_spread_is_material(population):
    """L2.4: the measured shipped defect was annual totals within 8%."""
    annual = {name: trace.annual_kwh("gas") for name, trace in population.items()}
    assert pt.annual_level_spread_is_material(annual)


def test_level_spread_control_FIRES_on_a_cloned_population(population):
    """R15 mutation: set every home to the population mean."""
    annual = {name: trace.annual_kwh("gas") for name, trace in population.items()}
    mean = sum(annual.values()) / len(annual)
    assert not pt.annual_level_spread_is_material({name: mean for name in annual})


def test_no_two_premises_share_a_trace(population):
    """The 'clone one home N times' mutation the harness spec names as the defect."""
    shapes = {
        name: tuple(round(v, 6) for day in trace.days for v in day.electricity_kwh)
        for name, trace in population.items()
    }
    assert len(set(shapes.values())) == len(shapes)


# ---------------------------------------------------------------------------
# LCT rewiring — the heat pump COP is the falsifiable claim
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def heat_pump_trace(weather) -> pt.PremiseTrace:
    return pt.generate_premise_trace(
        premise_id="P-hp",
        household=make_household(
            "C-hp", heating_system=HeatingSystem.HEAT_PUMP_AIR, insulation=InsulationLevel.FULL
        ),
        weather=weather,
        seed=77, latitude_deg=pt.DEFAULT_LATITUDE_DEG)


def test_a_heat_pump_premise_heats_with_electricity(heat_pump_trace):
    assert heat_pump_trace.heating_commodity == "electricity"
    assert sum(sum(d.gas_kwh) for d in heat_pump_trace.days) == 0.0


def test_heat_pump_cop_falls_with_cold(heat_pump_trace):
    """The temperature-dependent COP is what makes heat-pump electricity rise
    super-linearly in a cold snap — invisible under today's flat 1.2 kWh/degree-day."""
    assert pt.heat_pump_cop_falls_with_cold(heat_pump_trace)


def test_cop_control_FIRES_on_a_flat_cop(heat_pump_trace):
    """R15 mutation: flatten the COP — exactly today's shipped constant."""
    flattened = tuple(
        dataclasses.replace(
            day, heating_fuel_kwh=tuple(v / 3.0 for v in day.heat_delivered_kwh)
        )
        for day in heat_pump_trace.days
    )
    mutated = dataclasses.replace(heat_pump_trace, days=flattened)
    assert not pt.heat_pump_cop_falls_with_cold(mutated)


# ---------------------------------------------------------------------------
# The prebound effect must be a LIVE mechanism, not a buried constant
# ---------------------------------------------------------------------------


def test_prebound_response_is_live():
    """It is today a hard-coded constant in Household.epc_consumption_multiplier's
    docstring ('adjusted 50% toward 1.0'). As a Layer 2 response it must MOVE with
    stress."""
    from simulation.household import IncomeStress

    responses = [
        pt.comfort_constraint_for(income_stress=stress)
        for stress in (IncomeStress.LOW, IncomeStress.MODERATE, IncomeStress.HIGH)
    ]
    assert pt.prebound_response_is_live(responses)


def test_the_prebound_response_moves_with_PRICE_as_well_as_income():
    """It is a response to the WORLD, not a household attribute: the same
    household rations harder when the unit price rises."""
    from simulation.household import IncomeStress

    cheap = pt.comfort_constraint_for(
        income_stress=IncomeStress.MODERATE, unit_price_p_per_kwh=20.0,
        reference_price_p_per_kwh=20.0,
    )
    dear = pt.comfort_constraint_for(
        income_stress=IncomeStress.MODERATE, unit_price_p_per_kwh=60.0,
        reference_price_p_per_kwh=20.0,
    )
    assert dear.rationing_intensity > cheap.rationing_intensity
    assert dear.setpoint_reduction_c > cheap.setpoint_reduction_c


def test_prebound_control_FIRES_on_the_shipped_constant():
    """R15 mutation: one constant for every household at every price."""
    fixed = [pt.ComfortConstraint.unconstrained() for _ in range(3)]
    assert not pt.prebound_response_is_live(fixed)


def test_prebound_control_FIRES_on_a_non_monotone_response():
    """R15 mutation: rationing that EASES as stress rises is not a response."""
    from simulation.household import IncomeStress

    base = pt.comfort_constraint_for(income_stress=IncomeStress.HIGH)
    easing = [
        base,
        dataclasses.replace(base, rationing_intensity=base.rationing_intensity / 2.0),
        dataclasses.replace(base, rationing_intensity=0.0),
    ]
    assert not pt.prebound_response_is_live(easing)


def test_a_rationing_household_underheats_relative_to_its_own_comfort(weather):
    """The prebound effect as a MECHANISM: same fabric, same weather, same
    behaviour — only the income constraint differs."""
    from simulation.household import IncomeStress

    common = _pinned_layer_two(weather, premise_id="P-preb", seed=31)
    household = make_household()
    comfortable = pt.generate_premise_trace(
        household=household, constraint=pt.ComfortConstraint.unconstrained(), **common, latitude_deg=pt.DEFAULT_LATITUDE_DEG)
    squeezed = pt.generate_premise_trace(
        household=household,
        constraint=pt.comfort_constraint_for(income_stress=IncomeStress.HIGH),
        **common, latitude_deg=pt.DEFAULT_LATITUDE_DEG)
    assert squeezed.annual_kwh("gas") < comfortable.annual_kwh("gas")


# ---------------------------------------------------------------------------
# R15 FAIL-OPEN CLOSURE — a statistic over a vacuous trace must FAIL, not pass
# ---------------------------------------------------------------------------


def test_empty_weather_raises_rather_than_producing_an_empty_trace():
    with pytest.raises(ValueError):
        pt.generate_premise_trace(
            premise_id="P-empty", household=make_household(), weather=[], seed=1, latitude_deg=pt.DEFAULT_LATITUDE_DEG)


def test_a_missing_weather_archive_raises():
    with pytest.raises(FileNotFoundError):
        pt.load_trace_weather("NO_SUCH_LOCATION")


def test_a_non_residential_premise_is_refused():
    """This generator is DOMESTIC. Silently producing a trace for a warehouse
    would be a fail-open."""
    with pytest.raises(ValueError):
        pt.generate_premise_trace(
            premise_id="P-shed",
            household=make_household(property_type=PropertyType.COMMERCIAL_WAREHOUSE),
            weather=[],
            seed=1, latitude_deg=pt.DEFAULT_LATITUDE_DEG)


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_weather_is_rejected_first(bad, weather):
    """NaN comparisons are False by luck, not by design — non-finite input must be
    rejected BEFORE any band check can pass vacuously."""
    day = weather[0]
    poisoned = dataclasses.replace(
        day, weather=dataclasses.replace(day.weather, temperature_mean_c=bad)
    )
    with pytest.raises(ValueError):
        pt.generate_premise_trace(
            premise_id="P-nan", household=make_household(), weather=[poisoned], seed=1, latitude_deg=pt.DEFAULT_LATITUDE_DEG)


def test_controls_refuse_a_population_too_small_to_judge():
    with pytest.raises(ValueError):
        pt.hdd_response_varies_between_homes({"a": 1.0, "b": 2.0})
    with pytest.raises(ValueError):
        pt.annual_level_spread_is_material({"a": 1.0, "b": 2.0})
    with pytest.raises(ValueError):
        pt.prebound_response_is_live([pt.ComfortConstraint.unconstrained()])


def test_variability_control_refuses_a_window_too_short_to_judge():
    with pytest.raises(ValueError):
        pt.daily_variability_is_non_degenerate([1.0, 2.0, 3.0])


def test_hdd_gradient_refuses_a_window_with_no_temperature_variation():
    """A gradient over a constant temperature is undefined, not zero."""
    with pytest.raises(ValueError):
        pt.hdd_response_gradient([5.0] * 90, [10.0] * 90)


# ---------------------------------------------------------------------------
# The epistemic wall
# ---------------------------------------------------------------------------


def test_the_generator_is_world_side_only():
    """This is a WORLD module. It may never import the company or saas layers —
    the company discovers premises through meter reads, never by reading this."""
    import pathlib

    source = pathlib.Path(pt.__file__).read_text()
    assert "import company" not in source
    assert "from company" not in source
    assert "import saas" not in source
    assert "from saas" not in source


# ---------------------------------------------------------------------------
# The sizing answer the FRAME demanded before any BUILD shape was fixed
# ---------------------------------------------------------------------------


def test_the_measured_sizing_constant_is_recorded_with_its_hardware():
    """The FRAME required the cost question be ANSWERED, not assumed. The constant
    is a MEASUREMENT (it carries the machine it was measured on), not a budget."""
    assert pt.PREMISE_YEAR_SECONDS_MEASURED > 0.0
    assert "i5-13400F" in pt.PREMISE_YEAR_SECONDS_MEASURED_ON


def test_book_cost_estimate_scales_with_the_book():
    small = pt.estimate_book_cost(10, 365)
    large = pt.estimate_book_cost(1_000, 365)
    assert large["cpu_seconds"] == pytest.approx(100 * small["cpu_seconds"], rel=1e-9)
    assert pt.estimate_book_cost(1_000, 365, workers=16)["wall_hours_at_workers"] == (
        pytest.approx(large["cpu_hours"] / 16.0)
    )


def test_book_cost_refuses_a_degenerate_book():
    """A cost of zero for an empty book would be a fail-open on the sizing answer."""
    with pytest.raises(ValueError):
        pt.estimate_book_cost(0, 365)
    with pytest.raises(ValueError):
        pt.estimate_book_cost(10, 0)
    with pytest.raises(ValueError):
        pt.estimate_book_cost(10, 365, workers=0)


# ---------------------------------------------------------------------------
# The household's own clock, and the switched base load (both added 2026-08-08
# to close the two residual cells of the two-level test). Each is exercised BOTH
# ways per this file's standing R15 discipline.
# ---------------------------------------------------------------------------


def test_the_routine_offset_is_a_HABIT_not_a_daily_draw():
    """It must be a property of the HOUSEHOLD: identical every time the premise is
    profiled, and different between premises. A per-day draw would give the same
    within-home variation while leaving every home's long-run centre identical —
    which is the defect (L2.3) this mechanism exists to remove."""
    household = make_household()
    repeated = {
        pt.behaviour_profile_for("P-habit", household, seed=5).routine_offset_periods
        for _ in range(5)
    }
    assert len(repeated) == 1, "a household's clock must not be re-drawn"

    across_homes = {
        pt.behaviour_profile_for(f"P-{i}", make_household(f"C-{i}"), seed=5).routine_offset_periods
        for i in range(40)
    }
    assert len(across_homes) > 30, "households must not share one national clock"
    assert max(abs(o) for o in across_homes) <= pt._MAX_ROUTINE_OFFSET_PERIODS


def test_the_routine_offset_moves_the_household_s_EVENING_not_its_volume(weather):
    """MUTATION-STYLE PAIR: two premises identical but for their clock must differ
    in WHEN they use electricity and not materially in HOW MUCH."""
    household = make_household()
    early = pt.behaviour_profile_for("P-early", household, seed=5)
    early = dataclasses.replace(early, routine_offset_periods=-3.0)
    late = dataclasses.replace(early, routine_offset_periods=3.0)

    def evening_centre(profile):
        trace = pt.generate_premise_trace(
            premise_id="P-clock", household=household, weather=weather, seed=5,
            behaviour=profile, latitude_deg=pt.DEFAULT_LATITUDE_DEG,
        )
        grid = trace.half_hourly("electricity")
        picks = [max(range(29, 46), key=lambda p: day[p]) for day in grid]
        return sum(picks) / len(picks), trace.annual_kwh("electricity")

    early_centre, early_kwh = evening_centre(early)
    late_centre, late_kwh = evening_centre(late)
    assert late_centre > early_centre + 1.0, (
        f"a three-half-hour-later routine must move the evening peak later — "
        f"early {early_centre:.2f}, late {late_centre:.2f}"
    )
    assert late_kwh == pytest.approx(early_kwh, rel=0.10), (
        "the clock moves consumption in TIME; it must not create or destroy it"
    )


def test_switched_units_REFUSE_an_occupancy_that_is_not_a_probability():
    """FAIL-OPEN guard: an out-of-range probability must raise, never be clipped
    into a plausible-looking load."""
    import random as _random

    rng = _random.Random(0)
    assert 0 <= pt.switched_units_on(rng, 4, 0.5, 2) <= 4
    for bad in (-0.01, 1.01, float("nan")):
        with pytest.raises(ValueError):
            pt.switched_units_on(rng, 4, bad, 2)
    with pytest.raises(ValueError):
        pt.switched_units_on(rng, -1, 0.5, 0)


def test_the_switched_base_load_PRESERVES_energy(weather):
    """THE STANDING GUARD ON THE DRIFT THIS MECHANISM ALREADY CAUSED ONCE.

    Switching lighting and electronics must rearrange the same energy in time,
    never change how much there is: the anchored quantity (Ofgem TDCV ~2,700
    kWh/yr non-heating) belongs to the continuous form the switching replaced.

    The first implementation relaxed into each new occupancy level with a
    3.3-period time constant and so sat below its own stationary level at the
    start of every block — a systematic -2.2% that no cell of the two-level test
    would ever have caught, because every one of them is scale-free. This test is
    the control for that class, and it is the reason the chain re-seeds on a step.

    It is measured ACROSS HOMES on purpose. The bias is systematic and the
    per-home realisation noise is not, so aggregating separates the two. The
    first draft of this control asserted one home inside a 2% band and scored the
    real -1.93% defect as a PASS — a fail-open in the control written to catch a
    fail-open, which is why the mutation below is part of the deliverable.
    """
    bias = _switching_bias(weather, pt.switched_units_on)
    assert abs(bias) < 0.01, (
        f"switching must rearrange energy in time, not change it: {100 * bias:+.2f}%"
    )


def test_the_switched_energy_guard_FIRES_on_the_relaxation_BIAS(weather):
    """R15 for the control above: the defect it was written for must trip it.

    The mutation is the mechanism exactly as first implemented — never re-seed on
    an occupancy step, always relax into the new level.
    """
    # Bound BEFORE `_switching_bias` rebinds the module attribute, or the stub
    # would call itself rather than the real chain.
    chain = pt.switched_units_on

    def lagging(rng, units, occupancy, state, **kw):
        return chain(rng, units, occupancy, state, previous_occupancy=occupancy)

    bias = _switching_bias(weather, lagging)
    assert bias < -0.01, (
        f"the relaxation bias must trip the energy guard, measured {100 * bias:+.2f}%"
    )


def _switching_bias(weather, implementation) -> float:
    """Relative shift in book non-heating electricity under `implementation`,
    measured against the continuous form that IS the chain's expectation."""
    households = [
        make_household(f"C-sw{i}", insulation=ins, property_type=ptype)
        for i, (ins, ptype) in enumerate(
            (
                (InsulationLevel.POOR, PropertyType.TERRACED),
                (InsulationLevel.PARTIAL, PropertyType.SEMI_DETACHED),
                (InsulationLevel.FULL, PropertyType.DETACHED),
                (InsulationLevel.PARTIAL, PropertyType.FLAT),
            )
        )
    ]

    def book(fn):
        original = pt.switched_units_on
        pt.switched_units_on = fn
        try:
            return sum(
                pt.generate_premise_trace(
                    premise_id=f"P-sw{i}", household=hh, weather=weather,
                    seed=11 + i, latitude_deg=pt.DEFAULT_LATITUDE_DEG,
                ).annual_kwh("electricity")
                for i, hh in enumerate(households)
            )
        finally:
            pt.switched_units_on = original

    continuous = book(lambda rng, units, occupancy, state, **kw: units * occupancy)
    return (book(implementation) - continuous) / continuous
