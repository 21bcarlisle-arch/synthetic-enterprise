"""Phase P: EV overnight smart-charging shape (UK Smart Charge Point Regulations 2021)."""
import pytest
from simulation.life_events import LifeEvent
from simulation.household_demand import HouseholdDemandRegister
from simulation.run_phase2b import _weather_adjusted_shape_fn, _EV_OVERNIGHT_PERIODS


def _flat_base(date_str):
    return [1.0] * 48


def _reg(cid="C1"):
    cust = [{"customer_id": cid, "segment": "resi", "commodity": "electricity",
             "eac_kwh": 3100, "home_type": "suburban_semi", "epc_rating": "C", "bedrooms": 3}]
    reg = HouseholdDemandRegister(cust, seed=42)
    reg._events[cid] = [LifeEvent(customer_id=cid, event_date="2021-01-01",
                                   event_type="ev_acquired", payload={"ev_charger_kw": 7.0})]
    return reg


def _fn(reg, cid="C1"):
    prop = {"segment": "resi", "commodity": "electricity",
            "assets": {"ev": False, "solar": False, "smart_meter": False}, "eac_kwh": 3100}
    return _weather_adjusted_shape_fn(_flat_base, {}, prop, household_register=reg, customer_id=cid)


class TestEVOvernightShape:
    def test_overnight_periods_higher_than_daytime(self):
        fn = _fn(_reg())
        s = fn("2021-06-15")
        b = fn("2020-06-15")
        uplift = [a - b for a, b in zip(s, b)]
        # Period 1 (index 0) is overnight; period 25 (index 24) is noon
        assert uplift[0] > uplift[24]

    def test_annual_total_conserved(self):
        # Annual sum must equal the flat-distribution annual sum within 1%
        fn = _fn(_reg())
        daily_after = sum(fn("2021-06-15"))
        daily_before = sum(fn("2020-06-15"))
        ev_daily = 2143.0 / 365.25
        assert daily_after - daily_before == pytest.approx(ev_daily, rel=0.02)

    def test_triad_periods_get_daytime_fraction(self):
        # Triad peak is periods 33-38 (16:00-19:00) — these should be LOW not high
        fn = _fn(_reg())
        s_before = fn("2020-06-15")
        s_after = fn("2021-06-15")
        uplift = [a - b for a, b in zip(s_after, s_before)]
        triad_uplift = uplift[32]   # index 32 = period 33
        overnight_uplift = uplift[0]  # index 0 = period 1
        assert overnight_uplift > triad_uplift

    def test_no_ev_shape_unchanged(self):
        cust = [{"customer_id": "C1", "segment": "resi", "commodity": "electricity",
                 "eac_kwh": 3100, "home_type": "suburban_semi", "epc_rating": "C", "bedrooms": 3}]
        reg = HouseholdDemandRegister(cust, seed=42)
        reg._events["C1"] = []
        prop = {"segment": "resi", "commodity": "electricity",
                "assets": {"ev": False, "solar": False, "smart_meter": False}, "eac_kwh": 3100}
        fn = _weather_adjusted_shape_fn(_flat_base, {}, prop, household_register=reg, customer_id="C1")
        assert sum(fn("2020-06-15")) == pytest.approx(sum(fn("2021-06-15")), abs=0.001)

    def test_ev_and_solar_independent(self):
        # EV customer who also has solar: both effects still additive and independent
        cust = [{"customer_id": "C1", "segment": "resi", "commodity": "electricity",
                 "eac_kwh": 3100, "home_type": "rural_detached", "epc_rating": "C", "bedrooms": 4}]
        reg = HouseholdDemandRegister(cust, seed=42)
        reg._events["C1"] = [
            LifeEvent(customer_id="C1", event_date="2019-01-01",
                      event_type="solar_install", payload={"solar_kwp": 4.0}),
            LifeEvent(customer_id="C1", event_date="2021-01-01",
                      event_type="ev_acquired", payload={"ev_charger_kw": 7.0}),
        ]
        prop = {"segment": "resi", "commodity": "electricity",
                "assets": {"ev": False, "solar": False, "smart_meter": False}, "eac_kwh": 3100}
        fn = _weather_adjusted_shape_fn(_flat_base, {}, prop, household_register=reg, customer_id="C1")
        # Pre-EV (2020): solar may reduce load; post-EV (2022): EV adds overnight load
        s_2020 = fn("2020-06-15")
        s_2022 = fn("2022-06-15")
        # Overnight periods should be higher in 2022 due to EV
        assert s_2022[0] > s_2020[0]

    def test_ev_shape_winter_same_as_summer(self):
        # EV charging is not weather-dependent — shape fraction should be identical
        fn = _fn(_reg())
        s_winter = fn("2021-12-15")
        s_summer = fn("2021-06-15")
        # Base shape may differ by season but EV overnight/daytime RATIO should match
        b_winter = fn("2020-12-15")
        b_summer = fn("2020-06-15")
        uplift_winter = [a - b for a, b in zip(s_winter, b_winter)]
        uplift_summer = [a - b for a, b in zip(s_summer, b_summer)]
        assert uplift_winter[0] == pytest.approx(uplift_summer[0], rel=0.01)

    def test_period_1_midnight_gets_overnight_weight(self):
        # Period 1 (index 0) = 00:00-00:30 — must be in overnight set
        assert 1 in _EV_OVERNIGHT_PERIODS

    def test_period_25_noon_gets_daytime_weight(self):
        # Period 25 (index 24) = 12:00-12:30 — must NOT be in overnight set
        assert 25 not in _EV_OVERNIGHT_PERIODS

    def test_overnight_periods_count_is_16(self):
        assert len(_EV_OVERNIGHT_PERIODS) == 16

    def test_ashp_and_ev_both_additive(self):
        from simulation.household import Household, PropertyType, BuildEra, HeatingSystem, BoilerAge, InsulationLevel
        cust = [{"customer_id": "C1", "segment": "resi", "commodity": "electricity",
                 "eac_kwh": 3100, "home_type": "suburban_semi", "epc_rating": "C", "bedrooms": 3}]
        reg = HouseholdDemandRegister(cust, seed=42)
        reg._events["C1"] = [
            LifeEvent(customer_id="C1", event_date="2019-01-01",
                      event_type="heat_pump_installed", payload={"heating_system": "heat_pump_air"}),
            LifeEvent(customer_id="C1", event_date="2021-01-01",
                      event_type="ev_acquired", payload={"ev_charger_kw": 7.0}),
        ]
        prop = {"segment": "resi", "commodity": "electricity",
                "assets": {"ev": False, "solar": False, "smart_meter": False}, "eac_kwh": 3100}
        fn = _weather_adjusted_shape_fn(_flat_base, {}, prop, household_register=reg, customer_id="C1")
        # After both events, demand is higher than base
        base_sum = sum(fn("2018-06-15"))
        post_sum = sum(fn("2022-06-15"))
        assert post_sum > base_sum

    def test_ev_before_acquisition_no_uplift(self):
        fn = _fn(_reg())
        s_before = fn("2020-12-31")
        s_base = fn("2019-06-15")
        # Pre-acquisition periods have same overnight profile (no EV uplift)
        assert sum(s_before) == pytest.approx(sum(s_base), rel=0.01)

    def test_overnight_fraction_90pct_of_daily(self):
        fn = _fn(_reg())
        s_before = fn("2020-06-15")
        s_after = fn("2021-06-15")
        uplift = [a - b for a, b in zip(s_after, s_before)]
        # Sum of overnight-period uplift ≈ 90% of total daily uplift
        overnight_sum = sum(uplift[p - 1] for p in _EV_OVERNIGHT_PERIODS)
        total_sum = sum(uplift)
        assert overnight_sum / total_sum == pytest.approx(0.90, rel=0.01)



class TestEVOvernightEdgeCases:
    # 13. Overnight period constant has >= 12 items
    def test_ev_overnight_periods_count(self):
        assert len(_EV_OVERNIGHT_PERIODS) >= 12

    # 14. Shape values are all non-negative
    def test_shape_nonneg(self):
        prop = {"segment": "resi", "commodity": "electricity",
                "assets": {"ev": False, "solar": False, "smart_meter": False}, "eac_kwh": 3100}
        reg = _reg()
        fn = _weather_adjusted_shape_fn(_flat_base, {}, prop, household_register=reg, customer_id="C1")
        shape = fn("2021-06-01")
        assert all(v >= 0.0 for v in shape)

    # 15. EV customer shape sums higher than no-EV (extra load)
    def test_ev_shape_higher_total_than_no_ev(self):
        prop = {"segment": "resi", "commodity": "electricity",
                "assets": {"ev": False, "solar": False, "smart_meter": False}, "eac_kwh": 3100}
        cust_no_ev = [{"customer_id": "NEV", "segment": "resi", "commodity": "electricity",
                       "eac_kwh": 3100, "home_type": "suburban_semi", "epc_rating": "C", "bedrooms": 3}]
        reg_no_ev = HouseholdDemandRegister(cust_no_ev, seed=99)
        fn_no_ev = _weather_adjusted_shape_fn(_flat_base, {}, prop, household_register=reg_no_ev, customer_id="NEV")
        total_no_ev = sum(fn_no_ev("2021-06-01"))

        reg_ev = _reg()
        fn_ev = _weather_adjusted_shape_fn(_flat_base, {}, prop, household_register=reg_ev, customer_id="C1")
        total_ev = sum(fn_ev("2021-06-01"))

        assert total_ev > total_no_ev


def test_ev_load_is_counted_once_and_not_scaled_by_the_epc_band():
    """The defect: on a day WITH weather, `build_demand_shape` added its own 8 kWh/night for the
    register's EV flag and the Phase P block added `ev_annual_kwh()` on top -- 5,065 kWh/yr at EPC C
    and 6,672 at EPC E (the EPC multiplier scaled the first block). Every test above passes no
    weather, which is the one path where the first block never runs."""
    for epc in ("C", "E"):
        cust = [{"customer_id": "C1", "segment": "resi", "commodity": "electricity",
                 "eac_kwh": 3100, "home_type": "suburban_semi", "epc_rating": epc, "bedrooms": 3}]
        reg = HouseholdDemandRegister(cust, seed=42)
        reg._events["C1"] = [LifeEvent(customer_id="C1", event_date="2021-01-01",
                                       event_type="ev_acquired", payload={"ev_charger_kw": 7.0})]
        prop = {"segment": "resi", "commodity": "electricity", "heating_system": "gas_boiler",
                "occupancy_pattern": "working_couple",
                "assets": {"ev": False, "solar": False, "smart_meter": False}, "eac_kwh": 3100}
        weather = {"2020-06-15": 15.5, "2021-06-15": 15.5}
        fn = _weather_adjusted_shape_fn(_flat_base, weather, prop, household_register=reg, customer_id="C1")
        annual = (sum(fn("2021-06-15")) - sum(fn("2020-06-15"))) * 365.25
        ev_kwh = reg.household_at_date("C1", "2021-06-15").ev_annual_kwh()
        assert ev_kwh > 0
        assert annual == pytest.approx(ev_kwh, rel=1e-6)
    assert reg.epc_multiplier("C1", "2021-06-15") != 1.0  # the E band really does scale the rest
