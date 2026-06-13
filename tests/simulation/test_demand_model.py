import pytest

from simulation.demand_model import (
    COOLING_BASE_TEMP_C,
    COOLING_PERIOD_WEIGHTS,
    EV_CHARGING_KWH_PER_NIGHT,
    EV_CHARGING_PERIODS,
    HEATING_BASE_TEMP_C,
    HEATING_PERIOD_WEIGHTS,
    PERIODS_PER_DAY,
    build_demand_shape,
    cooling_degree_days,
    heating_degree_days,
    occupancy_multiplier,
    solar_generation_shape,
)

FLAT_SHAPE = [1.0] * PERIODS_PER_DAY


def gas_property(occupancy="single"):
    return {
        "heating_system": "gas_boiler",
        "occupancy_pattern": occupancy,
        "assets": {"ev": False, "solar": False, "smart_meter": True},
    }


def elec_property(heating_system="electric_storage", occupancy="single", **assets):
    base_assets = {"ev": False, "solar": False, "smart_meter": True}
    base_assets.update(assets)
    return {
        "heating_system": heating_system,
        "occupancy_pattern": occupancy,
        "assets": base_assets,
    }


def test_heating_degree_days_below_base_temp():
    assert heating_degree_days(10.5) == pytest.approx(5.0)


def test_heating_degree_days_above_base_temp_is_zero():
    assert heating_degree_days(20.0) == 0.0


def test_cooling_degree_days_above_base_temp():
    assert cooling_degree_days(25.0) == pytest.approx(25.0 - COOLING_BASE_TEMP_C)


def test_cooling_degree_days_below_base_temp_is_zero():
    assert cooling_degree_days(18.0) == 0.0


def test_heating_period_weights_sum_to_one_and_cover_48_periods():
    assert len(HEATING_PERIOD_WEIGHTS) == PERIODS_PER_DAY
    assert sum(HEATING_PERIOD_WEIGHTS) == pytest.approx(1.0)


def test_cooling_period_weights_sum_to_one_and_cover_48_periods():
    assert len(COOLING_PERIOD_WEIGHTS) == PERIODS_PER_DAY
    assert sum(COOLING_PERIOD_WEIGHTS) == pytest.approx(1.0)


def test_occupancy_multiplier_family_evening_peak_higher_than_daytime():
    evening = occupancy_multiplier("family", 40)  # 19:30-20:00
    daytime = occupancy_multiplier("family", 25)  # midday
    assert evening > daytime


def test_occupancy_multiplier_elderly_flatter_than_family():
    elderly_daytime = occupancy_multiplier("elderly", 25)
    family_daytime = occupancy_multiplier("family", 25)
    assert elderly_daytime > family_daytime


def test_occupancy_multiplier_unknown_pattern_defaults_to_single():
    assert occupancy_multiplier("unknown", 40) == occupancy_multiplier("single", 40)


def test_gas_boiler_adds_heating_load_on_cold_day():
    cold_temp = HEATING_BASE_TEMP_C - 5  # 5 HDD
    shape = build_demand_shape(FLAT_SHAPE, cold_temp, "gas", gas_property())
    base_with_occupancy = sum(
        s * occupancy_multiplier("single", p) for p, s in enumerate(FLAT_SHAPE, start=1)
    )
    # Extra heating load (5 HDD * GAS_HEATING_KWH_PER_DEGREE_DAY) is itself
    # subject to the occupancy multiplier in the periods it lands in, so the
    # total increase isn't exactly 5 * GAS_HEATING_KWH_PER_DEGREE_DAY — just
    # assert it's strictly more than the unheated baseline.
    assert sum(shape) > base_with_occupancy


def test_no_heating_load_added_on_warm_day():
    warm_temp = HEATING_BASE_TEMP_C + 5
    shape = build_demand_shape(FLAT_SHAPE, warm_temp, "gas", gas_property())
    base_with_occupancy = [
        s * occupancy_multiplier("single", p) for p, s in enumerate(FLAT_SHAPE, start=1)
    ]
    assert shape == pytest.approx(base_with_occupancy)


def test_electric_storage_heating_adds_load_on_cold_day():
    cold_temp = HEATING_BASE_TEMP_C - 4
    shape_no_heat = build_demand_shape(FLAT_SHAPE, cold_temp, "electricity", elec_property(heating_system=None))
    shape_with_heat = build_demand_shape(FLAT_SHAPE, cold_temp, "electricity", elec_property())
    assert sum(shape_with_heat) > sum(shape_no_heat)


def test_heat_pump_is_more_efficient_than_electric_storage():
    cold_temp = HEATING_BASE_TEMP_C - 4
    storage = build_demand_shape(FLAT_SHAPE, cold_temp, "electricity", elec_property(heating_system="electric_storage"))
    heat_pump = build_demand_shape(FLAT_SHAPE, cold_temp, "electricity", elec_property(heating_system="heat_pump"))
    assert sum(heat_pump) < sum(storage)


def test_cooling_load_added_on_hot_day_for_electricity():
    hot_temp = COOLING_BASE_TEMP_C + 5
    shape_hot = build_demand_shape(FLAT_SHAPE, hot_temp, "electricity", elec_property())
    shape_mild = build_demand_shape(FLAT_SHAPE, 18.0, "electricity", elec_property())
    assert sum(shape_hot) > sum(shape_mild)


def test_cooling_not_applied_to_gas():
    hot_temp = COOLING_BASE_TEMP_C + 5
    shape = build_demand_shape(FLAT_SHAPE, hot_temp, "gas", gas_property())
    base_with_occupancy = [
        s * occupancy_multiplier("single", p) for p, s in enumerate(FLAT_SHAPE, start=1)
    ]
    assert shape == pytest.approx(base_with_occupancy)


def test_ev_asset_adds_overnight_charging_load():
    mild_temp = 16.0  # no heating/cooling degree days
    no_ev = build_demand_shape(FLAT_SHAPE, mild_temp, "electricity", elec_property(ev=False))
    with_ev = build_demand_shape(FLAT_SHAPE, mild_temp, "electricity", elec_property(ev=True))

    assert sum(with_ev) - sum(no_ev) == pytest.approx(EV_CHARGING_KWH_PER_NIGHT)
    for p in EV_CHARGING_PERIODS:
        assert with_ev[p - 1] > no_ev[p - 1]


def test_solar_asset_reduces_daytime_demand_and_floors_at_zero():
    mild_temp = 16.0
    irradiance = [0.0] * PERIODS_PER_DAY
    # Strong midday sun, period 24 (11:30-12:00)
    irradiance[23] = 1000.0

    no_solar = build_demand_shape(FLAT_SHAPE, mild_temp, "electricity", elec_property(solar=False))
    with_solar = build_demand_shape(
        FLAT_SHAPE, mild_temp, "electricity", elec_property(solar=True),
        irradiance_w_m2_periods=irradiance,
    )

    assert with_solar[23] < no_solar[23]
    assert all(v >= 0.0 for v in with_solar)


def test_solar_generation_shape_scales_with_irradiance():
    irradiance = [0.0, 500.0, 1000.0] + [0.0] * (PERIODS_PER_DAY - 3)
    generation = solar_generation_shape(irradiance, kwp=1.0)
    assert generation[0] == 0.0
    assert generation[2] == pytest.approx(2 * generation[1])


def test_build_demand_shape_does_not_mutate_input():
    original = list(FLAT_SHAPE)
    build_demand_shape(FLAT_SHAPE, 5.0, "electricity", elec_property(ev=True, solar=True))
    assert FLAT_SHAPE == original


def test_output_length_always_48():
    shape = build_demand_shape(FLAT_SHAPE, 5.0, "gas", gas_property())
    assert len(shape) == PERIODS_PER_DAY
