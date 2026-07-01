import pytest
from company.crm.decarb_recommender import (
    Measure, FundingScheme, MeasureRecommendation, DecarbonisationPlan, recommend_measures,
)


def test_epc_fg_terraced_eco4_eligible():
    plan = recommend_measures('C001', 'F', 'terraced', 'gas_boiler', eco4_eligible=True, is_fuel_poor=True)
    measures = [r.measure for r in plan.recommendations]
    assert Measure.CAVITY_WALL_INSULATION in measures
    cw = next(r for r in plan.recommendations if r.measure == Measure.CAVITY_WALL_INSULATION)
    assert cw.estimated_cost_gbp == 0
    assert FundingScheme.ECO4 in cw.funding_schemes


def test_epc_fg_flat_eco4_eligible():
    plan = recommend_measures('C002', 'G', 'flat', 'gas_boiler', eco4_eligible=True)
    measures = [r.measure for r in plan.recommendations]
    assert Measure.SOLID_WALL_INSULATION in measures
    sw = next(r for r in plan.recommendations if r.measure == Measure.SOLID_WALL_INSULATION)
    assert sw.estimated_cost_gbp == 0


def test_heat_pump_recommended_good_epc():
    plan = recommend_measures('C003', 'C', 'semi_detached', 'gas_boiler')
    measures = [r.measure for r in plan.recommendations]
    assert Measure.HEAT_PUMP in measures
    hp = next(r for r in plan.recommendations if r.measure == Measure.HEAT_PUMP)
    assert FundingScheme.BUS in hp.funding_schemes


def test_no_heat_pump_poor_epc():
    plan = recommend_measures('C004', 'F', 'terraced', 'gas_boiler')
    measures = [r.measure for r in plan.recommendations]
    assert Measure.HEAT_PUMP not in measures


def test_solar_pv_recommended_without_solar():
    plan = recommend_measures('C005', 'C', 'detached', 'heat_pump', has_solar=False)
    measures = [r.measure for r in plan.recommendations]
    assert Measure.SOLAR_PV in measures
    pv = next(r for r in plan.recommendations if r.measure == Measure.SOLAR_PV)
    assert FundingScheme.SEG in pv.funding_schemes


def test_solar_pv_skipped_if_already_installed():
    plan = recommend_measures('C006', 'B', 'detached', 'heat_pump', has_solar=True)
    measures = [r.measure for r in plan.recommendations]
    assert Measure.SOLAR_PV not in measures


def test_smart_controls_always_included():
    plan = recommend_measures('C007', 'A', 'flat', 'heat_pump')
    measures = [r.measure for r in plan.recommendations]
    assert Measure.SMART_CONTROLS in measures


def test_payback_years():
    rec = MeasureRecommendation(
        Measure.LOFT_INSULATION, 150.0, 400.0, (FundingScheme.SELF_FUNDED,), 1
    )
    assert rec.simple_payback_years == pytest.approx(2.7)


def test_plan_total_savings():
    plan = recommend_measures('C008', 'E', 'terraced', 'gas_boiler')
    assert plan.total_potential_savings_gbp > 0


def test_plan_summary_keys():
    plan = recommend_measures('C009', 'C', 'semi_detached', 'gas_boiler')
    s = plan.summary()
    assert 'customer_id' in s
    assert 'total_potential_savings_gbp' in s
    assert 'top_measure' in s


def test_plan_is_frozen():
    plan = recommend_measures('C010', 'B', 'terraced', 'gas_boiler')
    with pytest.raises(Exception):
        plan.customer_id = 'X'


# --- Phase JQ depth tests ---

def test_epc_d_loft_not_wall_insulation():
    plan = recommend_measures('C011', 'D', 'terraced', 'gas_boiler')
    measures = [r.measure for r in plan.recommendations]
    assert Measure.LOFT_INSULATION in measures
    assert Measure.CAVITY_WALL_INSULATION not in measures
    assert Measure.SOLID_WALL_INSULATION not in measures


def test_epc_d_heat_pump_included():
    plan = recommend_measures('C012', 'D', 'semi_detached', 'gas_boiler')
    measures = [r.measure for r in plan.recommendations]
    assert Measure.HEAT_PUMP in measures


def test_eco4_loft_zero_cost():
    plan = recommend_measures('C013', 'E', 'terraced', 'gas_boiler', eco4_eligible=True)
    loft = next(r for r in plan.recommendations if r.measure == Measure.LOFT_INSULATION)
    assert loft.estimated_cost_gbp == 0


def test_oil_boiler_c_epc_heat_pump():
    plan = recommend_measures('C014', 'C', 'detached', 'oil_boiler')
    measures = [r.measure for r in plan.recommendations]
    assert Measure.HEAT_PUMP in measures
    hp = next(r for r in plan.recommendations if r.measure == Measure.HEAT_PUMP)
    assert FundingScheme.BUS in hp.funding_schemes


def test_battery_not_in_recommendations():
    plan = recommend_measures('C015', 'B', 'detached', 'gas_boiler')
    measures = [r.measure for r in plan.recommendations]
    assert Measure.BATTERY_STORAGE not in measures


def test_led_not_in_recommendations():
    plan = recommend_measures('C016', 'A', 'terraced', 'heat_pump')
    measures = [r.measure for r in plan.recommendations]
    assert Measure.LED_LIGHTING not in measures


def test_epc_a_no_insulation():
    plan = recommend_measures('C017', 'A', 'terraced', 'heat_pump')
    measures = [r.measure for r in plan.recommendations]
    assert Measure.CAVITY_WALL_INSULATION not in measures
    assert Measure.SOLID_WALL_INSULATION not in measures
    assert Measure.LOFT_INSULATION not in measures


def test_top_measure_is_first_recommendation():
    plan = recommend_measures('C018', 'F', 'terraced', 'gas_boiler')
    assert plan.top_measure is plan.recommendations[0]


def test_summary_recommendation_count():
    plan = recommend_measures('C019', 'E', 'detached', 'gas_boiler')
    s = plan.summary()
    assert s['recommendation_count'] == len(plan.recommendations)


def test_priority_increments_by_one():
    plan = recommend_measures('C020', 'F', 'terraced', 'gas_boiler')
    priorities = [r.priority for r in plan.recommendations]
    for i in range(len(priorities) - 1):
        assert priorities[i + 1] == priorities[i] + 1
