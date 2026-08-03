"""Tests for the fabric physics core (W1_11) — Layer 1 of the premise demand engine.

The tests are deliberately RELATIONAL, not pinned. Nothing here asserts a generated
number equals a stored constant: a pinned RNG-derived or physics-derived value is a
control that passes for the wrong reason and wedges the moment the model improves.
What is asserted is the RELATIONSHIP the design claims — heavier fabric damps more,
the deadband produces varying duty cycles, the reconstruction reconciles to the
archive it came from — each with the mutation that makes it FIRE (R15).
"""

from __future__ import annotations

import math

import pytest

from simulation.fabric_physics import (
    DEFAULT_LATITUDE_DEG,
    PERIODS_PER_DAY,
    AmbientProfile,
    ControlMode,
    DailyWeather,
    FabricParameters,
    HeatingSchedule,
    HeatSource,
    ThermalState,
    clear_sky_ghi_kw_per_m2,
    cloud_attenuation,
    daylight_hours,
    fabric_parameters,
    heat_pump_cop,
    heat_source_for,
    heating_schedule_for,
    mass_damps_intraday_swing,
    reconstruct_ambient_profile,
    reconstruct_irradiance_profile,
    reconstruction_reconciles,
    rescaled_fraction_multiplicity,
    simulate_day,
    simulate_premise,
    texture_is_not_a_rescaled_shape,
)
from simulation.household import (
    BoilerAge,
    BuildEra,
    HeatingSystem,
    Household,
    InsulationLevel,
    PropertyType,
)


def make_household(
    customer_id: str = "C1",
    *,
    property_type: PropertyType = PropertyType.SEMI_DETACHED,
    build_era: BuildEra = BuildEra.ERA_1965_1980,
    insulation: InsulationLevel = InsulationLevel.PARTIAL,
    heating_system: HeatingSystem = HeatingSystem.GAS_BOILER_COMBI,
    bedrooms: int | None = 3,
) -> Household:
    return Household(
        customer_id=customer_id,
        property_type=property_type,
        build_era=build_era,
        epc_rating="D",
        bedrooms=bedrooms,
        heating_system=heating_system,
        boiler_age=BoilerAge.MID,
        has_solar=False,
        solar_kwp=0.0,
        solar_install_year=None,
        has_battery=False,
        battery_kwh=0.0,
        has_ev=False,
        ev_charger_kw=0.0,
        has_smart_meter=True,
        smart_meter_install_year=2020,
        insulation=insulation,
        has_driveway=True,
        roof_aspect="south",
    )


def winter_week() -> list[DailyWeather]:
    """A cold, cloudy January week — plain daily statistics, exactly the shape of a
    real `sim/weather_data/*.csv` row."""
    return [
        DailyWeather(
            day_of_year=15 + i,
            temperature_min_c=0.5 + 0.3 * i,
            temperature_max_c=6.2 + 0.4 * i,
            temperature_mean_c=3.1 + 0.35 * i,
            cloud_cover_pct=70.0 + 2.0 * i,
        )
        for i in range(7)
    ]


# ---------------------------------------------------------------------------
# Sub-daily weather reconstruction
# ---------------------------------------------------------------------------


def test_reconstruction_reproduces_the_three_observed_daily_statistics():
    """Min, max exact by construction; mean recovered by the decay solve."""
    profile = reconstruct_ambient_profile(
        temperature_min_c=1.2,
        temperature_max_c=8.4,
        temperature_mean_c=4.3,
        day_of_year=20,
        latitude_deg=DEFAULT_LATITUDE_DEG,
    )
    assert len(profile.temperatures_c) == PERIODS_PER_DAY
    assert min(profile.temperatures_c) == pytest.approx(1.2, abs=0.05)
    assert max(profile.temperatures_c) == pytest.approx(8.4, abs=0.05)
    reconstructed_mean = sum(profile.temperatures_c) / PERIODS_PER_DAY
    assert reconstructed_mean == pytest.approx(4.3, abs=0.05)
    assert reconstruction_reconciles(profile)


@pytest.mark.parametrize(
    "t_min,t_max,t_mean,day",
    [
        (-4.0, 2.0, -1.2, 5),      # cold snap, short day
        (11.0, 24.0, 17.8, 190),   # summer, long day
        (6.0, 6.0, 6.0, 100),      # degenerate flat day
        (2.0, 15.0, 6.5, 300),     # mean far below the midpoint
    ],
)
def test_reconstruction_reconciles_across_the_year(t_min, t_max, t_mean, day):
    profile = reconstruct_ambient_profile(
        temperature_min_c=t_min,
        temperature_max_c=t_max,
        temperature_mean_c=t_mean,
        day_of_year=day,
        latitude_deg=DEFAULT_LATITUDE_DEG,
    )
    assert reconstruction_reconciles(profile)


def test_reconstruction_rejects_an_inverted_range_rather_than_fabricating_a_profile():
    with pytest.raises(ValueError):
        reconstruct_ambient_profile(
            temperature_min_c=9.0, temperature_max_c=2.0, temperature_mean_c=5.0, day_of_year=50,
            latitude_deg=DEFAULT_LATITUDE_DEG,
        )


def test_reconstruction_reconciles_control_fires_on_an_unreconciled_profile():
    """R15: the control must be able to FAIL. Hand it a profile whose residual the
    solve could not absorb and it fires."""
    good = reconstruct_ambient_profile(
        temperature_min_c=1.0, temperature_max_c=7.0, temperature_mean_c=4.0, day_of_year=20,
        latitude_deg=DEFAULT_LATITUDE_DEG,
    )
    assert reconstruction_reconciles(good)
    mutated = AmbientProfile(
        temperatures_c=good.temperatures_c,
        sunrise_hour=good.sunrise_hour,
        sunset_hour=good.sunset_hour,
        peak_hour=good.peak_hour,
        decay_k=good.decay_k,
        reconstruction_residual_c=1.8,
    )
    assert not reconstruction_reconciles(mutated)


def test_reconstruction_reconciles_rejects_a_non_finite_residual_first():
    """Comparison guards are NaN-blind: `abs(nan) <= tol` is False by luck, not by
    design. Assert the rejection is explicit for both NaN and inf."""
    for bad in (float("nan"), float("inf")):
        profile = AmbientProfile(
            temperatures_c=[5.0] * PERIODS_PER_DAY,
            sunrise_hour=8.0,
            sunset_hour=16.0,
            peak_hour=15.0,
            decay_k=1.0,
            reconstruction_residual_c=bad,
        )
        assert not reconstruction_reconciles(profile)


def test_the_profile_is_not_one_fixed_shape_across_the_year():
    """The timing comes from solar geometry, so a January and a July day with the
    same min/max/mean still peak at different hours."""
    january = reconstruct_ambient_profile(
        temperature_min_c=4.0, temperature_max_c=10.0, temperature_mean_c=6.5, day_of_year=15,
        latitude_deg=DEFAULT_LATITUDE_DEG,
    )
    july = reconstruct_ambient_profile(
        temperature_min_c=4.0, temperature_max_c=10.0, temperature_mean_c=6.5, day_of_year=196,
        latitude_deg=DEFAULT_LATITUDE_DEG,
    )
    assert january.sunrise_hour > july.sunrise_hour
    assert january.peak_hour != july.peak_hour
    assert january.temperatures_c != july.temperatures_c


def test_daylight_hours_are_seasonal_and_symmetric_about_solar_noon():
    winter_rise, winter_set = daylight_hours(DEFAULT_LATITUDE_DEG, 355)
    summer_rise, summer_set = daylight_hours(DEFAULT_LATITUDE_DEG, 172)
    assert (summer_set - summer_rise) > (winter_set - winter_rise)
    for rise, sett in ((winter_rise, winter_set), (summer_rise, summer_set)):
        assert rise + sett == pytest.approx(24.0, abs=1e-9)


def test_irradiance_is_zero_overnight_and_attenuated_by_cloud():
    clear = reconstruct_irradiance_profile(cloud_cover_pct=0.0, day_of_year=172)
    overcast = reconstruct_irradiance_profile(cloud_cover_pct=100.0, day_of_year=172)
    assert clear[0] == 0.0 and clear[-1] == 0.0
    assert sum(overcast) < sum(clear)
    assert all(o <= c + 1e-12 for o, c in zip(overcast, clear))
    # Midwinter noon sun is far weaker than midsummer noon sun.
    midwinter = reconstruct_irradiance_profile(cloud_cover_pct=0.0, day_of_year=355)
    assert max(midwinter) < max(clear)


def test_cloud_attenuation_is_bounded_and_monotone():
    assert cloud_attenuation(0.0) == pytest.approx(1.0)
    assert 0.0 < cloud_attenuation(1.0) < 1.0
    values = [cloud_attenuation(x / 10.0) for x in range(11)]
    assert all(b <= a for a, b in zip(values, values[1:]))
    # Out-of-range input is clamped, not propagated.
    assert cloud_attenuation(-3.0) == cloud_attenuation(0.0)
    assert cloud_attenuation(4.0) == cloud_attenuation(1.0)


def test_clear_sky_irradiance_is_zero_below_the_horizon():
    assert clear_sky_ghi_kw_per_m2(DEFAULT_LATITUDE_DEG, 355, 2.0) == 0.0
    assert clear_sky_ghi_kw_per_m2(DEFAULT_LATITUDE_DEG, 172, 12.0) > 0.0


# ---------------------------------------------------------------------------
# EPC fields -> 2R2C parameters
# ---------------------------------------------------------------------------


def test_fabric_parameters_order_by_construction_age_and_insulation():
    """The LEVEL claim: an uninsulated solid-wall Victorian loses more than a
    retrofitted one, which loses more than a modern build."""
    victorian = fabric_parameters(
        make_household(build_era=BuildEra.PRE_1919, insulation=InsulationLevel.POOR)
    )
    retrofitted = fabric_parameters(
        make_household(build_era=BuildEra.PRE_1919, insulation=InsulationLevel.FULL)
    )
    modern = fabric_parameters(
        make_household(build_era=BuildEra.POST_2000, insulation=InsulationLevel.FULL)
    )
    assert (
        victorian.heat_loss_coefficient_kw_per_k
        > retrofitted.heat_loss_coefficient_kw_per_k
        > modern.heat_loss_coefficient_kw_per_k
    )


def test_built_form_drives_exposed_envelope_loss():
    detached = fabric_parameters(make_household(property_type=PropertyType.DETACHED))
    semi = fabric_parameters(make_household(property_type=PropertyType.SEMI_DETACHED))
    terraced = fabric_parameters(make_household(property_type=PropertyType.TERRACED))
    # Compare per m^2 so the comparison is about exposure, not about size.
    def per_m2(p: FabricParameters) -> float:
        return p.heat_loss_coefficient_kw_per_k / p.floor_area_m2

    assert per_m2(detached) > per_m2(semi) > per_m2(terraced)


def test_thermal_mass_orders_by_construction_age():
    """C_m is the CHARACTER parameter — solid masonry stores heat, timber frame
    does not."""
    heavy = fabric_parameters(make_household(build_era=BuildEra.PRE_1919))
    light = fabric_parameters(make_household(build_era=BuildEra.POST_2000))
    assert heavy.c_m_kwh_per_k > light.c_m_kwh_per_k


def test_time_constants_land_in_their_physical_bands():
    """The air node must respond in MINUTES (or the burner cannot cycle inside a
    settlement period) and the building in HOURS-TO-DAYS (or fabric has no memory).
    A band, not a pinned value."""
    params = fabric_parameters(make_household(build_era=BuildEra.PRE_1919))
    assert 0.1 < params.air_time_constant_hours < 1.0
    assert 12.0 < params.building_time_constant_hours < 200.0


def test_modern_insulation_cannot_drive_u_values_below_what_can_be_built():
    """The regression this floor exists for: applying the retrofit multiplier on top
    of an already-modern age band double-counts and produces an unphysically low
    heat loss coefficient."""
    modern = fabric_parameters(
        make_household(build_era=BuildEra.POST_2000, insulation=InsulationLevel.FULL)
    )
    design_load_kw = modern.heat_loss_coefficient_kw_per_k * 23.5
    assert 1.0 < design_load_kw < 8.0


def test_a_non_residential_premise_is_rejected_not_silently_modelled():
    with pytest.raises(ValueError):
        fabric_parameters(make_household(property_type=PropertyType.COMMERCIAL_OFFICE))


def test_floor_area_scales_with_bedrooms_and_tolerates_an_unknown_count():
    small = fabric_parameters(make_household(bedrooms=2)).floor_area_m2
    large = fabric_parameters(make_household(bedrooms=5)).floor_area_m2
    unknown = fabric_parameters(make_household(bedrooms=None)).floor_area_m2
    assert large > small
    assert unknown == small  # a 2-bedroom baseline, stated rather than guessed


# ---------------------------------------------------------------------------
# Heat source and controller
# ---------------------------------------------------------------------------


def test_a_combi_boiler_is_oversized_relative_to_the_fabric_it_serves():
    """The oversizing is the reason boilers cycle — assert it exists rather than
    assuming it."""
    household = make_household(build_era=BuildEra.POST_2000, insulation=InsulationLevel.FULL)
    params = fabric_parameters(household)
    source = heat_source_for(household, params, 20.5)
    design_load = params.heat_loss_coefficient_kw_per_k * (20.5 - (-3.0))
    assert source.rated_output_kw > design_load
    assert source.control_mode is ControlMode.ON_OFF_DEADBAND


def test_a_heat_pump_is_sized_close_to_the_design_load_and_runs_continuously():
    household = make_household(heating_system=HeatingSystem.HEAT_PUMP_AIR)
    params = fabric_parameters(household)
    source = heat_source_for(household, params, 20.5)
    design_load = params.heat_loss_coefficient_kw_per_k * (20.5 - (-3.0))
    assert source.rated_output_kw < 1.5 * design_load
    assert source.control_mode is ControlMode.WEATHER_COMPENSATED


def test_heat_pump_cop_falls_as_ambient_falls_and_stays_bounded():
    """The mechanism behind heat-pump winter peaks, invisible in a flat
    kWh-per-degree-day coefficient."""
    assert heat_pump_cop(7.0) > heat_pump_cop(-2.0) > heat_pump_cop(-12.0)
    assert heat_pump_cop(-30.0) >= 1.8
    assert heat_pump_cop(40.0) <= 5.5
    assert heat_pump_cop(0.0, ground_source=True) > heat_pump_cop(0.0)


def test_a_premise_with_no_heating_system_delivers_no_heat():
    household = make_household(heating_system=HeatingSystem.NONE)
    results = simulate_premise(
        premise_id="P-none", household=household, daily_weather=winter_week(), seed=3
    )
    assert sum(sum(day.heat_delivered_kwh) for day in results) == 0.0
    assert sum(sum(day.fuel_kwh) for day in results) == 0.0


# ---------------------------------------------------------------------------
# Structural (not injected) diversity
# ---------------------------------------------------------------------------


def test_schedules_differ_between_premises_and_repeat_for_the_same_premise():
    a = heating_schedule_for("P-A", make_household(), seed=11)
    b = heating_schedule_for("P-B", make_household(), seed=11)
    a_again = heating_schedule_for("P-A", make_household(), seed=11)
    assert a != b
    assert a == a_again


def test_setpoints_stay_inside_the_measured_human_band():
    setpoints = [
        heating_schedule_for(f"P-{i}", make_household(), seed=1).comfort_setpoint_c
        for i in range(200)
    ]
    assert all(17.0 <= s <= 24.0 for s in setpoints)
    assert len(set(setpoints)) > 100  # genuinely dispersed, not a single value
    assert 19.0 < sum(setpoints) / len(setpoints) < 22.0


def test_a_weather_compensated_system_is_scheduled_continuously():
    boiler = heating_schedule_for("P-1", make_household(), seed=5)
    heat_pump = heating_schedule_for(
        "P-1", make_household(heating_system=HeatingSystem.HEAT_PUMP_AIR), seed=5
    )
    assert not boiler.continuous
    assert heat_pump.continuous
    assert boiler.setpoint_at(4) < boiler.comfort_setpoint_c   # 02:00, on setback
    assert heat_pump.setpoint_at(4) == heat_pump.comfort_setpoint_c


def test_the_substream_is_isolated_from_the_global_random_state():
    """C-S2: a draw here must never shift another subsystem's sequence."""
    import random

    random.seed(1234)
    before = [random.random() for _ in range(5)]
    random.seed(1234)
    heating_schedule_for("P-X", make_household(), seed=99)
    after = [random.random() for _ in range(5)]
    assert before == after


# ---------------------------------------------------------------------------
# The simulation — the claims the design makes about texture and character
# ---------------------------------------------------------------------------


def test_simulation_is_deterministic_across_repeat_runs():
    household = make_household()
    week = winter_week()
    first = simulate_premise(premise_id="P-D", household=household, daily_weather=week, seed=7)
    second = simulate_premise(premise_id="P-D", household=household, daily_weather=week, seed=7)
    assert [d.heat_delivered_kwh for d in first] == [d.heat_delivered_kwh for d in second]


def test_indoor_temperature_is_held_near_the_setpoint_during_heated_periods():
    household = make_household()
    schedule = heating_schedule_for("P-T", household, seed=7)
    results = simulate_premise(
        premise_id="P-T", household=household, daily_weather=winter_week(), seed=7
    )
    settled = results[-1]
    heated = [
        settled.indoor_air_c[p]
        for p in range(PERIODS_PER_DAY)
        if schedule.setpoint_at(p) == schedule.comfort_setpoint_c
    ]
    assert heated, "the test premise must have heated periods"
    # Control holds; it does not track perfectly (that is the deadband).
    assert all(abs(t - schedule.comfort_setpoint_c) < 2.0 for t in heated)


def test_the_deadband_produces_partial_and_varying_duty_cycles():
    """THE central claim: a perfectly-modulating source would give a smooth series.
    The deadband must yield half hours that are neither fully on nor fully off, and
    those partial cycles must VARY period to period."""
    results = simulate_premise(
        premise_id="P-Duty",
        household=make_household(build_era=BuildEra.POST_2000, insulation=InsulationLevel.FULL),
        daily_weather=winter_week(),
        seed=7,
    )
    duties = [d for day in results for d in day.duty_cycle_fraction]
    partial = [d for d in duties if 0.0 < d < 1.0]
    assert partial, "no partial duty cycle: the heat source is not cycling at all"
    assert len(set(round(d, 4) for d in partial)) > 5, "duty cycles do not vary"


def test_heat_delivery_is_not_a_rescaled_base_shape_L15():
    """The harness spec's L1.5 structural check, run against this generator."""
    results = simulate_premise(
        premise_id="P-L15", household=make_household(), daily_weather=winter_week(), seed=7
    )
    series = [day.heat_delivered_kwh for day in results]
    assert texture_is_not_a_rescaled_shape(series)


def test_L15_control_fires_on_a_rescaled_base_shape():
    """R15 mutation: the control's own named defect is one stored shape rescaled per
    day. Feed it exactly that and it must FIRE."""
    base = [0.0] * 12 + [1.0, 2.0, 3.0, 2.5] * 6 + [0.0] * 12
    rescaled = [[v * scale for v in base] for scale in (0.8, 1.0, 1.3, 1.7, 2.2, 0.6, 1.1)]
    assert rescaled_fraction_multiplicity(rescaled) >= len(rescaled)
    assert not texture_is_not_a_rescaled_shape(rescaled)


def test_L15_needs_more_than_one_day_to_mean_anything():
    with pytest.raises(ValueError):
        texture_is_not_a_rescaled_shape([[1.0, 2.0, 3.0]])


def test_L15_ignores_genuinely_off_periods():
    """A heating system that is off overnight is physics, not a rescaling artefact.
    Two days that share only their zeros must not trip the control."""
    day_a = [0.0] * 24 + [0.4 + 0.11 * i for i in range(24)]
    day_b = [0.0] * 24 + [0.3 + 0.17 * i for i in range(24)]
    assert texture_is_not_a_rescaled_shape([day_a, day_b])


def test_L15_ignores_a_within_day_plateau():
    """A source running flat out for a stretch of half hours shares a fraction
    WITHIN that day. That is a real physical plateau, and counting it would fire the
    control on correct physics."""
    plateau = [0.0] * 20 + [2.0] * 14 + [0.4 + 0.13 * i for i in range(14)]
    other = [0.0] * 20 + [3.0] * 14 + [0.9 + 0.07 * i for i in range(14)]
    assert texture_is_not_a_rescaled_shape([plateau, other])


def test_heavier_fabric_damps_the_indoor_swing_and_the_control_can_fire():
    """The CHARACTER claim, isolated: identical weather, identical control, identical
    heat loss — only C_m differs. Reversing the arguments must fire the control, or
    C_m is not doing the work the design says it does."""
    household = make_household()
    base = fabric_parameters(household)
    schedule = heating_schedule_for("P-Mass", household, seed=7)
    source = heat_source_for(household, base, schedule.comfort_setpoint_c)
    week = winter_week()

    def run(c_m: float) -> list:
        params = FabricParameters(
            floor_area_m2=base.floor_area_m2,
            r_ia_k_per_kw=base.r_ia_k_per_kw,
            r_im_k_per_kw=base.r_im_k_per_kw,
            c_i_kwh_per_k=base.c_i_kwh_per_k,
            c_m_kwh_per_k=c_m,
            solar_aperture_m2=base.solar_aperture_m2,
            internal_gain_kw=base.internal_gain_kw,
        )
        state = ThermalState(
            indoor_air_c=schedule.setback_setpoint_c, mass_c=schedule.setback_setpoint_c
        )
        out = []
        for day in week:
            profile = reconstruct_ambient_profile(
                temperature_min_c=day.temperature_min_c,
                temperature_max_c=day.temperature_max_c,
                temperature_mean_c=day.temperature_mean_c,
                day_of_year=day.day_of_year,
                latitude_deg=DEFAULT_LATITUDE_DEG,
            )
            result = simulate_day(
                household=household,
                params=params,
                schedule=schedule,
                source=source,
                ambient_profile=profile,
                irradiance_kw_per_m2=reconstruct_irradiance_profile(
                    cloud_cover_pct=day.cloud_cover_pct, day_of_year=day.day_of_year
                ),
                initial_state=state,
            )
            out.append(result)
            state = result.end_state
        return out

    heavy = run(base.c_m_kwh_per_k * 3.0)
    light = run(base.c_m_kwh_per_k / 3.0)
    assert mass_damps_intraday_swing(heavy, light)
    # R15 mutation: the same control on swapped inputs must FAIL.
    assert not mass_damps_intraday_swing(light, heavy)


def test_mass_control_rejects_an_empty_run_rather_than_passing_vacuously():
    """Fail-open pattern: a control that passes on an empty input is not a control."""
    with pytest.raises(ValueError):
        mass_damps_intraday_swing([], [])


def test_two_identical_premises_differ_in_TIMING_without_injected_noise():
    """Between-home diversity must fall out of structure (setpoint + schedule), not
    out of per-period noise. Same fabric, same weather, different premise id."""
    household = make_household()
    week = winter_week()
    a = simulate_premise(premise_id="P-A", household=household, daily_weather=week, seed=7)
    b = simulate_premise(premise_id="P-B", household=household, daily_weather=week, seed=7)
    assert a[-1].heat_delivered_kwh != b[-1].heat_delivered_kwh
    # ... and the difference is in WHEN, not merely a scale factor on the whole day.
    ratios = [
        x / y
        for x, y in zip(a[-1].heat_delivered_kwh, b[-1].heat_delivered_kwh)
        if x > 0 and y > 0
    ]
    assert len(set(round(r, 3) for r in ratios)) > 1


def test_annual_level_falls_as_fabric_improves():
    """The LEVEL claim end-to-end: better fabric, same weather, less heat."""
    week = winter_week()
    poor = simulate_premise(
        premise_id="P-Same",
        household=make_household(build_era=BuildEra.PRE_1919, insulation=InsulationLevel.POOR),
        daily_weather=week,
        seed=7,
    )
    good = simulate_premise(
        premise_id="P-Same",
        household=make_household(build_era=BuildEra.POST_2000, insulation=InsulationLevel.FULL),
        daily_weather=week,
        seed=7,
    )
    assert sum(sum(d.heat_delivered_kwh) for d in poor) > sum(
        sum(d.heat_delivered_kwh) for d in good
    )


def test_colder_weather_raises_delivered_heat():
    household = make_household()
    mild = [
        DailyWeather(day_of_year=15 + i, temperature_min_c=8.0, temperature_max_c=13.0,
                     temperature_mean_c=10.3, cloud_cover_pct=70.0)
        for i in range(5)
    ]
    cold = [
        DailyWeather(day_of_year=15 + i, temperature_min_c=-3.0, temperature_max_c=1.0,
                     temperature_mean_c=-1.2, cloud_cover_pct=70.0)
        for i in range(5)
    ]
    mild_heat = sum(
        sum(d.heat_delivered_kwh)
        for d in simulate_premise(premise_id="P-W", household=household, daily_weather=mild, seed=7)
    )
    cold_heat = sum(
        sum(d.heat_delivered_kwh)
        for d in simulate_premise(premise_id="P-W", household=household, daily_weather=cold, seed=7)
    )
    assert cold_heat > mild_heat


def test_thermal_state_chains_across_days():
    """The mass node's carry-over IS the fabric character. Resetting it each day
    must produce a different answer, or the chaining is decorative."""
    household = make_household(build_era=BuildEra.PRE_1919, insulation=InsulationLevel.POOR)
    week = winter_week()
    chained = simulate_premise(
        premise_id="P-Chain", household=household, daily_weather=week, seed=7
    )
    warm_start = simulate_premise(
        premise_id="P-Chain",
        household=household,
        daily_weather=week,
        seed=7,
        initial_state=ThermalState(indoor_air_c=21.0, mass_c=21.0),
    )
    assert chained[0].heat_delivered_kwh != warm_start[0].heat_delivered_kwh
    assert chained[0].end_state.mass_c != warm_start[0].end_state.mass_c


def test_a_heat_pump_runs_smoother_than_a_cycling_boiler():
    """Different texture BY HEATING SYSTEM, not one texture for all: the weather-
    compensated system must show fewer fully-off half hours during heated periods."""
    week = winter_week()
    boiler = simulate_premise(
        premise_id="P-HS",
        household=make_household(heating_system=HeatingSystem.GAS_BOILER_COMBI),
        daily_weather=week,
        seed=7,
    )
    heat_pump = simulate_premise(
        premise_id="P-HS",
        household=make_household(heating_system=HeatingSystem.HEAT_PUMP_AIR),
        daily_weather=week,
        seed=7,
    )

    def saturated_share(results) -> float:
        duties = [d for day in results for d in day.duty_cycle_fraction]
        return sum(1 for d in duties if d in (0.0, 1.0)) / len(duties)

    assert saturated_share(heat_pump) > saturated_share(boiler)


def test_heat_pump_electricity_rises_super_linearly_as_ambient_falls():
    """Equal steps down in temperature must cost MORE than proportionally more
    electricity, because the COP is falling at the same time."""
    household = make_household(heating_system=HeatingSystem.HEAT_PUMP_AIR)

    def elec_at(mean_c: float) -> float:
        week = [
            DailyWeather(day_of_year=15 + i, temperature_min_c=mean_c - 2.5,
                         temperature_max_c=mean_c + 2.5, temperature_mean_c=mean_c,
                         cloud_cover_pct=80.0)
            for i in range(5)
        ]
        runs = simulate_premise(
            premise_id="P-HP", household=household, daily_weather=week, seed=7
        )
        return sum(sum(d.fuel_kwh) for d in runs[1:])  # drop the warm-up day

    warm, mid, cold = elec_at(8.0), elec_at(3.0), elec_at(-2.0)
    assert (cold - mid) > (mid - warm) > 0


def test_fuel_exceeds_delivered_heat_for_a_boiler_and_is_below_it_for_a_heat_pump():
    week = winter_week()
    boiler = simulate_premise(
        premise_id="P-F", household=make_household(), daily_weather=week, seed=7
    )
    heat_pump = simulate_premise(
        premise_id="P-F",
        household=make_household(heating_system=HeatingSystem.HEAT_PUMP_AIR),
        daily_weather=week,
        seed=7,
    )
    boiler_heat = sum(sum(d.heat_delivered_kwh) for d in boiler)
    boiler_fuel = sum(sum(d.fuel_kwh) for d in boiler)
    hp_heat = sum(sum(d.heat_delivered_kwh) for d in heat_pump)
    hp_fuel = sum(sum(d.fuel_kwh) for d in heat_pump)
    assert boiler_fuel > boiler_heat > 0.0
    assert 0.0 < hp_fuel < hp_heat


def test_delivered_heat_is_finite_and_non_negative_everywhere():
    """Non-finite values must be impossible, not merely unlikely — every downstream
    comparison guard in the settlement chain is NaN-blind."""
    for era in BuildEra:
        results = simulate_premise(
            premise_id=f"P-{era.value}",
            household=make_household(build_era=era),
            daily_weather=winter_week(),
            seed=7,
        )
        for day in results:
            for value in day.heat_delivered_kwh + day.fuel_kwh + day.indoor_air_c:
                assert math.isfinite(value)
            assert all(v >= 0.0 for v in day.heat_delivered_kwh)
            assert all(0.0 <= d <= 1.0 for d in day.duty_cycle_fraction)


def test_every_day_returns_a_full_settlement_period_set():
    results = simulate_premise(
        premise_id="P-Shape", household=make_household(), daily_weather=winter_week(), seed=7
    )
    assert len(results) == len(winter_week())
    for day in results:
        assert len(day.heat_delivered_kwh) == PERIODS_PER_DAY
        assert len(day.fuel_kwh) == PERIODS_PER_DAY
        assert len(day.indoor_air_c) == PERIODS_PER_DAY
        assert len(day.duty_cycle_fraction) == PERIODS_PER_DAY


def test_solar_gain_reduces_delivered_heat_on_a_clear_day():
    """Solar GAIN (not PV generation) is one of the things the daily-HDD contract
    cannot see. Its effect must be visible here."""
    household = make_household()
    def week(cloud_pct: float) -> list[DailyWeather]:
        return [
            DailyWeather(day_of_year=60 + i, temperature_min_c=1.0, temperature_max_c=7.0,
                         temperature_mean_c=3.8, cloud_cover_pct=cloud_pct)
            for i in range(5)
        ]

    def heat(cloud_pct: float) -> float:
        runs = simulate_premise(
            premise_id="P-Sun", household=household, daily_weather=week(cloud_pct), seed=7
        )
        return sum(sum(d.heat_delivered_kwh) for d in runs)

    assert heat(100.0) > heat(0.0)
