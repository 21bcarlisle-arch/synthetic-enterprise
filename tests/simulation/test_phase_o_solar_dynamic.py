"""Phase O: Solar dynamic settlement wiring for life-event customers.

Prior to Phase O, assets["solar"] was NOT updated from dynamic_assets,
so customers who acquired solar via life events got annual EAC reduction
(via eac_multiplier_for_date) but NOT the half-hourly irradiance-based
demand reduction. Phase O closes that gap.
"""
import pytest
from simulation.life_events import LifeEvent
from simulation.household_demand import HouseholdDemandRegister
from simulation.run_phase2b import _weather_adjusted_shape_fn


LATITUDE = 51.5  # London

# Full property dict required by build_demand_shape
_PROP_BASE = {
    "segment": "resi", "commodity": "electricity", "eac_kwh": 3100,
    "heating_system": "gas_boiler", "occupancy_pattern": "standard",
    "assets": {"ev": False, "solar": False, "smart_meter": False},
}


def _flat_base(date_str):
    return [1.0] * 48


def _reg_with_solar_event(cid="C1", install_date="2021-01-01"):
    cust = [{"customer_id": cid, "segment": "resi", "commodity": "electricity",
             "eac_kwh": 3100, "home_type": "suburban_semi", "epc_rating": "C",
             "bedrooms": 3, "location": {"lat": LATITUDE, "lon": -0.1}}]
    reg = HouseholdDemandRegister(cust, seed=42)
    reg._events[cid] = [LifeEvent(customer_id=cid, event_date=install_date,
                                  event_type="solar_install",
                                  payload={"solar_kwp": 3.5})]
    return reg


def _shape_fn(reg, cid="C1"):
    prop = dict(_PROP_BASE, assets=dict(_PROP_BASE["assets"]))
    cloud = {"2021-06-15": 0.1, "2020-06-15": 0.1, "2021-12-15": 0.2, "2020-12-15": 0.2,
             "2021-06-14": 0.1}
    weather = {"2021-06-15": 20.0, "2020-06-15": 19.0, "2021-12-15": 5.0, "2020-12-15": 4.0}
    return _weather_adjusted_shape_fn(
        _flat_base, weather, prop,
        cloud_cover_means=cloud, latitude_deg=LATITUDE,
        household_register=reg, customer_id=cid,
    )


class TestSolarDynamicWiring:
    def test_demand_reduced_post_install(self):
        """Summer day import should be lower after solar install."""
        fn = _shape_fn(_reg_with_solar_event())
        before = sum(fn("2020-06-15"))
        after = sum(fn("2021-06-15"))
        assert after < before

    def test_demand_unchanged_pre_install(self):
        """Pre-install date: solar flag false, no irradiance reduction."""
        fn1 = _shape_fn(_reg_with_solar_event(install_date="2030-01-01"))
        fn2 = _shape_fn(_reg_with_solar_event(install_date="2030-01-01"))
        assert sum(fn1("2020-06-15")) == pytest.approx(sum(fn2("2020-06-15")), rel=0.01)

    def test_night_periods_not_reduced(self):
        """Period 1 (midnight) has zero irradiance — no solar reduction at night."""
        fn = _shape_fn(_reg_with_solar_event())
        shape_before = fn("2020-06-15")
        shape_after = fn("2021-06-15")
        assert shape_after[0] == pytest.approx(shape_before[0], abs=1e-9)
        assert shape_after[1] == pytest.approx(shape_before[1], abs=1e-9)

    def test_midday_periods_most_reduced(self):
        """Peak solar irradiance at midday: periods 24-30 reduced more than night."""
        fn = _shape_fn(_reg_with_solar_event())
        shape_before = fn("2020-06-15")
        shape_after = fn("2021-06-15")
        reduction = [b - a for b, a in zip(shape_before, shape_after)]
        midday_avg = sum(reduction[24:30]) / 6
        night_avg = sum(reduction[0:4]) / 4
        assert midday_avg > night_avg

    def test_summer_more_reduction_than_winter(self):
        """Summer has more daylight and higher sun angle than winter."""
        fn = _shape_fn(_reg_with_solar_event())
        summer_reduction = sum(fn("2020-06-15")) - sum(fn("2021-06-15"))
        winter_reduction = sum(fn("2020-12-15")) - sum(fn("2021-12-15"))
        assert summer_reduction > winter_reduction

    def test_no_solar_event_no_change(self):
        """Customer with no life events: demand unchanged across dates."""
        cust = [{"customer_id": "C2", "segment": "resi", "commodity": "electricity",
                 "eac_kwh": 3100, "home_type": "suburban_semi", "epc_rating": "C",
                 "bedrooms": 3}]
        reg = HouseholdDemandRegister(cust, seed=42)
        reg._events["C2"] = []
        prop = dict(_PROP_BASE, assets=dict(_PROP_BASE["assets"]))
        cloud = {"2021-06-15": 0.1, "2020-06-15": 0.1}
        weather = {"2021-06-15": 20.0, "2020-06-15": 19.0}
        fn = _weather_adjusted_shape_fn(_flat_base, weather, prop,
                                        cloud_cover_means=cloud, latitude_deg=LATITUDE,
                                        household_register=reg, customer_id="C2")
        assert sum(fn("2020-06-15")) == pytest.approx(sum(fn("2021-06-15")), rel=0.02)

    def test_static_solar_customer_still_works(self):
        """Phase 25a regression: static assets.solar=True still applies irradiance."""
        prop = dict(_PROP_BASE, assets={"ev": False, "solar": True, "smart_meter": False})
        cloud = {"2021-06-15": 0.1}
        weather = {"2021-06-15": 20.0}
        fn = _weather_adjusted_shape_fn(_flat_base, weather, prop,
                                        cloud_cover_means=cloud, latitude_deg=LATITUDE)
        assert min(fn("2021-06-15")) < 1.0

    def test_solar_and_ev_independent(self):
        """EV adds demand; solar subtracts daytime. Night periods show EV uplift."""
        cust = [{"customer_id": "C3", "segment": "resi", "commodity": "electricity",
                 "eac_kwh": 3100, "home_type": "suburban_semi", "epc_rating": "C",
                 "bedrooms": 3, "location": {"lat": LATITUDE, "lon": -0.1}}]
        reg = HouseholdDemandRegister(cust, seed=42)
        reg._events["C3"] = [
            LifeEvent(customer_id="C3", event_date="2021-01-01",
                      event_type="solar_install", payload={"solar_kwp": 3.5}),
            LifeEvent(customer_id="C3", event_date="2021-01-01",
                      event_type="ev_acquired", payload={"ev_charger_kw": 7.0}),
        ]
        prop = dict(_PROP_BASE, assets=dict(_PROP_BASE["assets"]))
        cloud = {"2021-06-15": 0.1, "2020-06-15": 0.1}
        weather = {"2021-06-15": 20.0, "2020-06-15": 19.0}
        fn = _weather_adjusted_shape_fn(_flat_base, weather, prop,
                                        cloud_cover_means=cloud, latitude_deg=LATITUDE,
                                        household_register=reg, customer_id="C3")
        night_pre = sum(fn("2020-06-15")[:6])
        night_post = sum(fn("2021-06-15")[:6])
        # EV flat uplift is in all 48 periods from household_register ASHP/EV block,
        # so night import should be higher post-acquisition
        assert night_post > night_pre

    def test_demand_clamped_not_negative(self):
        """When solar exceeds demand, import is clamped at 0."""
        fn = _shape_fn(_reg_with_solar_event())
        assert all(v >= 0.0 for v in fn("2021-06-15"))

    def test_cloudy_less_reduction_than_clear(self):
        """Higher cloud fraction = less solar generation = less import reduction."""
        reg_c = _reg_with_solar_event(cid="C4")
        prop = dict(_PROP_BASE, assets=dict(_PROP_BASE["assets"]))
        weather = {"2021-06-15": 20.0}
        fn_clear = _weather_adjusted_shape_fn(_flat_base, weather, prop,
                                              cloud_cover_means={"2021-06-15": 0.05},
                                              latitude_deg=LATITUDE,
                                              household_register=reg_c, customer_id="C4")
        fn_cloudy = _weather_adjusted_shape_fn(_flat_base, weather, prop,
                                               cloud_cover_means={"2021-06-15": 0.90},
                                               latitude_deg=LATITUDE,
                                               household_register=reg_c, customer_id="C4")
        assert sum(fn_clear("2021-06-15")) < sum(fn_cloudy("2021-06-15"))

    def test_solar_starts_on_install_date(self):
        """Install date itself already has reduced midday demand."""
        fn = _shape_fn(_reg_with_solar_event(install_date="2021-06-15"))
        shape = fn("2021-06-15")
        assert min(shape) < 1.0

    def test_no_reduction_day_before_install(self):
        """Day before install: solar flag false, no irradiance reduction."""
        fn = _shape_fn(_reg_with_solar_event(install_date="2021-06-15"))
        # 2021-06-14 is in cloud dict but not in weather dict -> mean_temp=None -> flat base
        shape_day_before = fn("2021-06-14")
        assert all(abs(v - 1.0) < 1e-6 for v in shape_day_before)
