"""Phase N: EV/solar/HP suitability constraints + EV settlement shape."""
import pytest
from simulation.household import (
    Household, PropertyType, BuildEra, HeatingSystem, BoilerAge,
    InsulationLevel, make_household,
)
from simulation.life_events import generate_life_events, LifeEvent
from simulation.run_phase2b import _weather_adjusted_shape_fn


def _flat_base(date_str):
    return [1.0] * 48


def _hh(**kw):
    d = dict(
        customer_id="T1", property_type=PropertyType.SEMI_DETACHED,
        build_era=BuildEra.ERA_1945_1964, epc_rating="C", bedrooms=3,
        heating_system=HeatingSystem.GAS_BOILER_COMBI, boiler_age=BoilerAge.MID,
        has_solar=False, solar_kwp=0.0, solar_install_year=None,
        has_battery=False, battery_kwh=0.0, has_ev=False, ev_charger_kw=0.0,
        has_smart_meter=False, smart_meter_install_year=None,
        insulation=InsulationLevel.PARTIAL, has_driveway=True, roof_aspect="south",
    )
    d.update(kw)
    return Household(**d)


class TestDrivewaySuitability:
    def test_detached_has_driveway(self):
        c={"customer_id":"D1","home_type":"rural_detached","epc_rating":"C","segment":"resi","bedrooms":4}
        assert make_household(c).has_driveway is True
    def test_semi_has_driveway(self):
        c={"customer_id":"S1","home_type":"suburban_semi","epc_rating":"D","segment":"resi","bedrooms":3}
        assert make_household(c).has_driveway is True
    def test_flat_no_driveway(self):
        c={"customer_id":"F1","home_type":"urban_flat","epc_rating":"C","segment":"resi","bedrooms":1}
        assert make_household(c).has_driveway is False
    def test_tenement_no_driveway(self):
        c={"customer_id":"T1","home_type":"tenement_flat","epc_rating":"D","segment":"resi","bedrooms":2}
        assert make_household(c).has_driveway is False
    def test_commercial_no_driveway(self):
        c={"customer_id":"O1","home_type":"small_office","epc_rating":"D","segment":"sme"}
        assert make_household(c).has_driveway is False


class TestRoofAspect:
    def test_detached_south(self):
        c={"customer_id":"D1","home_type":"rural_detached","epc_rating":"C","segment":"resi","bedrooms":4}
        assert make_household(c).roof_aspect=="south"
    def test_semi_east_west(self):
        c={"customer_id":"S1","home_type":"suburban_semi","epc_rating":"D","segment":"resi","bedrooms":3}
        assert make_household(c).roof_aspect=="east_west"
    def test_urban_flat_na(self):
        c={"customer_id":"F1","home_type":"urban_flat","epc_rating":"C","segment":"resi","bedrooms":1}
        assert make_household(c).roof_aspect=="na"
    def test_tenement_na(self):
        c={"customer_id":"T1","home_type":"tenement_flat","epc_rating":"D","segment":"resi","bedrooms":2}
        assert make_household(c).roof_aspect=="na"


class TestHPEligible:
    def test_semi_eligible(self):
        assert _hh(property_type=PropertyType.SEMI_DETACHED,bedrooms=3).hp_eligible is True
    def test_detached_eligible(self):
        assert _hh(property_type=PropertyType.DETACHED,bedrooms=4).hp_eligible is True
    def test_flat_not_eligible(self):
        assert _hh(property_type=PropertyType.FLAT,bedrooms=2).hp_eligible is False
    def test_one_bedroom_not_eligible(self):
        assert _hh(property_type=PropertyType.TERRACED,bedrooms=1).hp_eligible is False
    def test_two_bedroom_eligible(self):
        assert _hh(property_type=PropertyType.SEMI_DETACHED,bedrooms=2).hp_eligible is True
    def test_none_bedrooms_eligible(self):
        assert _hh(property_type=PropertyType.DETACHED,bedrooms=None).hp_eligible is True
    def test_commercial_not_eligible(self):
        assert _hh(property_type=PropertyType.COMMERCIAL_OFFICE).hp_eligible is False


class TestEVDrivewaySuitability:
    def test_flat_no_driveway_never_gets_ev(self):
        hh=_hh(customer_id="FL1",property_type=PropertyType.FLAT,has_driveway=False)
        for seed in range(50):
            events=generate_life_events(hh,2016,2025,seed=seed)
            assert not any(e.event_type=="ev_acquired" for e in events)
    def test_driveway_home_eligible_for_ev(self):
        hh=_hh(customer_id="SM1",property_type=PropertyType.SEMI_DETACHED,has_driveway=True)
        assert isinstance(generate_life_events(hh,2016,2025,seed=42),list)


class TestSolarRoofConstraint:
    def test_na_roof_never_gets_solar(self):
        hh=_hh(customer_id="FL3",property_type=PropertyType.FLAT,has_driveway=False,roof_aspect="na")
        for seed in range(30):
            events=generate_life_events(hh,2016,2025,seed=seed)
            assert not any(e.event_type=="solar_install" for e in events)
    def test_north_facing_never_gets_solar(self):
        hh=_hh(customer_id="TR1",property_type=PropertyType.TERRACED,has_driveway=False,roof_aspect="north")
        for seed in range(30):
            events=generate_life_events(hh,2016,2025,seed=seed)
            assert not any(e.event_type=="solar_install" for e in events)
    def test_south_facing_eligible(self):
        hh=_hh(customer_id="DT1",property_type=PropertyType.DETACHED,has_driveway=True,roof_aspect="south")
        assert isinstance(generate_life_events(hh,2016,2025,seed=0),list)


class TestHPPhysicalConstraint:
    def test_flat_never_gets_hp(self):
        hh=_hh(customer_id="FL4",property_type=PropertyType.FLAT,bedrooms=2,has_driveway=False,roof_aspect="na")
        for seed in range(50):
            events=generate_life_events(hh,2016,2025,seed=seed)
            assert not any(e.event_type=="heat_pump_installed" for e in events)
    def test_eligible_semi_can_get_hp(self):
        hh=_hh(customer_id="SM3",property_type=PropertyType.SEMI_DETACHED,bedrooms=3,has_driveway=True,roof_aspect="east_west")
        assert isinstance(generate_life_events(hh,2016,2025,seed=0),list)


class TestEVSettlementShape:
    def _reg(self,cid="C1"):
        from simulation.household_demand import HouseholdDemandRegister
        cust=[{"customer_id":cid,"segment":"resi","commodity":"electricity","eac_kwh":3100,"home_type":"suburban_semi","epc_rating":"C","bedrooms":3}]
        reg=HouseholdDemandRegister(cust,seed=42)
        reg._events[cid]=[LifeEvent(customer_id=cid,event_date="2021-01-01",event_type="ev_acquired",payload={"ev_charger_kw":7.0})]
        return reg
    def _fn(self,reg,cid="C1"):
        prop={"segment":"resi","commodity":"electricity","assets":{"ev":False,"solar":False,"smart_meter":False},"eac_kwh":3100}
        return _weather_adjusted_shape_fn(_flat_base,{},prop,household_register=reg,customer_id=cid)
    def test_ev_raises_daily_demand_after_acquisition(self):
        fn=self._fn(self._reg())
        daily_before=sum(fn("2020-06-15"))
        daily_after=sum(fn("2021-06-15"))
        ev_per_day=2143.0/365.25
        assert daily_after>daily_before
        assert daily_after-daily_before==pytest.approx(ev_per_day,rel=0.02)
    def test_ev_uplift_flat_across_48_periods(self):
        fn=self._fn(self._reg())
        s_before=fn("2020-06-15")
        s_after=fn("2021-06-15")
        uplift=[a-b for a,b in zip(s_after,s_before)]
        assert all(abs(u-uplift[0])<1e-9 for u in uplift)
    def test_no_ev_no_demand_change(self):
        from simulation.household_demand import HouseholdDemandRegister
        cust=[{"customer_id":"C1","segment":"resi","commodity":"electricity","eac_kwh":3100,"home_type":"suburban_semi","epc_rating":"C","bedrooms":3}]
        reg=HouseholdDemandRegister(cust,seed=42)
        reg._events["C1"]=[]
        prop={"segment":"resi","commodity":"electricity","assets":{"ev":False,"solar":False,"smart_meter":False},"eac_kwh":3100}
        fn=_weather_adjusted_shape_fn(_flat_base,{},prop,household_register=reg,customer_id="C1")
        assert sum(fn("2020-06-15"))==pytest.approx(sum(fn("2021-06-15")),abs=0.001)
