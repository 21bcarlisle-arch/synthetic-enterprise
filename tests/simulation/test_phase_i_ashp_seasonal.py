"""Phase I: ASHP Seasonal Electricity Shape (HDD-Weighted).

Tests that the ASHP additive load in _weather_adjusted_shape_fn uses an HDD-weighted
seasonal profile (70% heating, 30% DHW) rather than a flat annual average.
Annual total is conserved at ~5,500 kWh/yr.
"""
from __future__ import annotations

from calendar import monthrange

import pytest
from sim.weather_hdd import REFERENCE_MONTHLY_HDD, get_hdd
from simulation.run_phase2b import _weather_adjusted_shape_fn
from saas.customers import CUSTOMERS
from saas.property_model import build_properties
from simulation.weather_inputs import load_weather_means
from sim.profile_class_1 import load_pc1_shape


ASHP_ANNUAL_KWH = 5_500.0
HDD_ANNUAL_REF = sum(REFERENCE_MONTHLY_HDD.values())

_props = build_properties(CUSTOMERS)
_c1_weather = load_weather_means("C1")
_c1_prop = _props["C1"]


def _make_ashp_register(cid="C1", epc="C"):
    """EPC C (multiplier=1.0) isolates ASHP uplift from EPC effects in shape comparisons."""
    from simulation.household_demand import HouseholdDemandRegister
    from simulation.household import BoilerAge, Household, HeatingSystem, InsulationLevel
    cust = [next(c for c in CUSTOMERS if c["customer_id"] == cid)]
    reg = HouseholdDemandRegister(cust, seed=42)
    bh = reg._households[cid]
    reg._households[cid] = Household(
        customer_id=cid,
        property_type=bh.property_type, build_era=bh.build_era,
        epc_rating=epc, bedrooms=bh.bedrooms,
        heating_system=HeatingSystem.HEAT_PUMP_AIR,
        boiler_age=bh.boiler_age, insulation=bh.insulation,
        has_solar=False, solar_kwp=0.0, solar_install_year=None,
        has_battery=False, battery_kwh=0.0,
        has_ev=False, ev_charger_kw=0.0,
        has_smart_meter=True, smart_meter_install_year=None,
        has_driveway=True, roof_aspect="south",
    )
    reg._events[cid] = []
    return reg


def _shape_for(date_str: str, register=None, cid="C1"):
    fn = _weather_adjusted_shape_fn(
        load_pc1_shape, _c1_weather, _c1_prop,
        household_register=register, customer_id=cid,
    )
    return fn(date_str)


class TestASHPSeasonalShape:
    def test_winter_day_ashp_load_exceeds_flat(self):
        """January daily ASHP uplift should exceed the flat-average daily kWh."""
        reg = _make_ashp_register()
        daily_with = sum(_shape_for("2020-01-15", reg))
        daily_without = sum(_shape_for("2020-01-15"))
        flat_daily = ASHP_ANNUAL_KWH / 365.25
        assert daily_with - daily_without > flat_daily

    def test_summer_day_ashp_load_below_flat(self):
        """July daily ASHP uplift should be below the flat-average daily kWh."""
        reg = _make_ashp_register()
        daily_with = sum(_shape_for("2020-07-15", reg))
        daily_without = sum(_shape_for("2020-07-15"))
        flat_daily = ASHP_ANNUAL_KWH / 365.25
        assert daily_with - daily_without < flat_daily

    def test_winter_exceeds_summer_ashp_uplift(self):
        """January ASHP uplift should exceed July ASHP uplift."""
        reg = _make_ashp_register()
        jan_uplift = sum(_shape_for("2020-01-15", reg)) - sum(_shape_for("2020-01-15"))
        jul_uplift = sum(_shape_for("2020-07-15", reg)) - sum(_shape_for("2020-07-15"))
        assert jan_uplift > jul_uplift

    def test_summer_dhw_floor_is_positive(self):
        """Even in July, DHW component means ASHP uplift > 0."""
        reg = _make_ashp_register()
        daily_uplift = sum(_shape_for("2020-07-15", reg)) - sum(_shape_for("2020-07-15"))
        assert daily_uplift > 0.0

    def test_non_ashp_customer_unchanged(self):
        """Gas-boiler customer (EPC C, mult=1.0) gets zero ASHP uplift from Phase I."""
        from simulation.household_demand import HouseholdDemandRegister
        from simulation.household import BoilerAge, Household, HeatingSystem, InsulationLevel
        cust = [next(c for c in CUSTOMERS if c["customer_id"] == "C1")]
        reg = HouseholdDemandRegister(cust, seed=42)
        bh = reg._households["C1"]
        reg._households["C1"] = Household(
            customer_id="C1",
            property_type=bh.property_type, build_era=bh.build_era,
            epc_rating="C",  # EPC C -> multiplier 1.0 -> no EPC effect, isolates ASHP
            bedrooms=bh.bedrooms,
            heating_system=HeatingSystem.GAS_BOILER_COMBI,
            boiler_age=bh.boiler_age, insulation=bh.insulation,
            has_solar=False, solar_kwp=0.0, solar_install_year=None,
            has_battery=False, battery_kwh=0.0,
            has_ev=False, ev_charger_kw=0.0,
            has_smart_meter=True, smart_meter_install_year=None,
            has_driveway=bh.has_driveway, roof_aspect=bh.roof_aspect,
        )
        reg._events["C1"] = []
        shape_with_reg = _shape_for("2020-01-15", reg)
        shape_without_reg = _shape_for("2020-01-15")
        assert abs(sum(shape_with_reg) - sum(shape_without_reg)) < 0.01

    def test_no_register_unchanged(self):
        """Without household register, shape function works normally."""
        shape = _shape_for("2020-01-15")
        assert sum(shape) > 0 and len(shape) == 48

    def test_annual_conservation(self):
        """Over a reference year (2015, pre-weather-data so HDD fallback used),
        ASHP uplift should sum to ~5,500 kWh (within 3%).
        Real weather years may differ because actual HDD != reference HDD.
        """
        reg = _make_ashp_register()
        total_kwh = 0.0
        for month in range(1, 13):
            _, mdays = monthrange(2015, month)
            for day in range(1, mdays + 1):
                date_str = f"2015-{month:02d}-{day:02d}"
                uplift = sum(_shape_for(date_str, reg)) - sum(_shape_for(date_str))
                total_kwh += uplift
        assert abs(total_kwh - ASHP_ANNUAL_KWH) / ASHP_ANNUAL_KWH < 0.03, (
            f"Annual total {total_kwh:.1f} kWh diverges from {ASHP_ANNUAL_KWH} by more than 3%"
        )

    def test_hdd_model_jan_hotter_than_jul(self):
        """Reference HDD: January > July (confirms HDD-weighting direction)."""
        assert get_hdd("2020-01-15", "C1") > get_hdd("2020-07-15", "C1")

    def test_reference_hdd_sum_is_reasonable(self):
        """Reference annual HDD should be in typical UK range 1,800-2,400."""
        assert 1800 < HDD_ANNUAL_REF < 2400

    def test_48_slots_equal_within_day(self):
        """ASHP uplift should be evenly spread across 48 half-hours within a day."""
        reg = _make_ashp_register()
        shape_with = _shape_for("2020-01-15", reg)
        shape_without = _shape_for("2020-01-15")
        uplifts = [w - b for w, b in zip(shape_with, shape_without)]
        assert max(uplifts) - min(uplifts) < 1e-9



def test_reference_monthly_hdd_has_12_months():
    assert len(REFERENCE_MONTHLY_HDD) == 12


def test_hdd_annual_ref_is_positive():
    assert HDD_ANNUAL_REF > 0


def test_ashp_annual_kwh_constant_is_5500():
    assert ASHP_ANNUAL_KWH == 5_500.0
