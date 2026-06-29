"""Phase H: Electricity EAC Multiplier at Term Signing.

Tests that _company_eac_estimate applies the household EAC multiplier (EV/solar/ASHP)
to the declared base EAC on first terms, while leaving billing-history-based
renewal estimates unchanged (no double-counting).
"""

from simulation.run_phase2b import _company_eac_estimate, EFFECTIVE_EAC_KWH


def _rec(cid, date, kwh):
    return {"customer_id": cid, "settlement_date": date, "consumption_kwh": float(kwh)}


class TestCompanyEACEstimateBaseOverride:
    def test_first_term_without_override_uses_declared(self):
        eac = _company_eac_estimate("C1", "2016-07-01", [])
        assert eac == EFFECTIVE_EAC_KWH.get("C1", 0.0)

    def test_first_term_with_override_uses_override(self):
        eac = _company_eac_estimate("C1", "2016-07-01", [], base_eac_override=6000.0)
        assert eac == 6000.0

    def test_renewal_term_uses_billing_history_not_override(self):
        hist = [_rec("C1", f"2017-01-{d+1:02d}", 10.0) for d in range(28)]
        eac = _company_eac_estimate("C1", "2017-02-01", hist, base_eac_override=9999.0)
        assert eac != 9999.0 and eac > 0

    def test_ev_uplift_raises_first_term_eac(self):
        declared = EFFECTIVE_EAC_KWH.get("C2", 3500.0)
        ev_adj = float(round(declared * 1.8))
        eac = _company_eac_estimate("C2", "2019-01-01", [], base_eac_override=ev_adj)
        assert eac == ev_adj and eac > declared

    def test_solar_reduction_lowers_first_term_eac(self):
        declared = EFFECTIVE_EAC_KWH.get("C4", 5500.0)
        solar_adj = float(round(declared * 0.6))
        eac = _company_eac_estimate("C4", "2020-01-01", [], base_eac_override=solar_adj)
        assert eac == solar_adj and eac < declared

    def test_none_override_matches_no_kwarg(self):
        assert (_company_eac_estimate("C1", "2016-07-01", []) ==
                _company_eac_estimate("C1", "2016-07-01", [], base_eac_override=None))

    def test_override_of_one_honoured(self):
        assert _company_eac_estimate("C1", "2016-07-01", [], base_eac_override=1.0) == 1.0


class TestEACMultiplierForDate:
    def test_multiplier_positive_and_finite(self):
        from simulation.household_demand import HouseholdDemandRegister
        reg = HouseholdDemandRegister(
            [{"customer_id": "C1", "segment": "resi", "commodity": "electricity", "eac_kwh": 3100}], seed=42
        )
        m = reg.eac_multiplier_for_date("C1", "2022-01-01")
        assert 0.0 < m < 10.0

    def test_multiplier_returns_float(self):
        from simulation.household_demand import HouseholdDemandRegister
        reg = HouseholdDemandRegister(
            [{"customer_id": "C1", "segment": "resi", "commodity": "electricity", "eac_kwh": 3100}], seed=42
        )
        assert isinstance(reg.eac_multiplier_for_date("C1", "2018-06-01"), float)

    def test_ashp_customer_multiplier_exceeds_one(self):
        from simulation.household_demand import HouseholdDemandRegister
        from simulation.household import Household, BoilerAge, HeatingSystem, InsulationLevel
        cust = [{"customer_id": "C1", "segment": "resi", "commodity": "electricity", "eac_kwh": 3100}]
        reg = HouseholdDemandRegister(cust, seed=42)
        bh = reg._households["C1"]
        reg._households["C1"] = Household(
            customer_id="C1", property_type=bh.property_type, build_era=bh.build_era,
            epc_rating="D", bedrooms=bh.bedrooms,
            heating_system=HeatingSystem.HEAT_PUMP_AIR,
            boiler_age=BoilerAge.NEW, insulation=InsulationLevel.PARTIAL,
            has_solar=False, solar_kwp=0.0, solar_install_year=None,
            has_battery=False, battery_kwh=0.0,
            has_ev=False, ev_charger_kw=0.0,
            has_smart_meter=True, smart_meter_install_year=None,
        )
        reg._events["C1"] = []
        assert reg.eac_multiplier_for_date("C1", "2022-01-01") > 1.0

    def test_solar_reduces_multiplier_vs_no_solar(self):
        from simulation.household_demand import HouseholdDemandRegister
        from simulation.household import Household
        cust = [{"customer_id": "C1", "segment": "resi", "commodity": "electricity", "eac_kwh": 3100}]
        reg = HouseholdDemandRegister(cust, seed=42)
        bh = reg._households["C1"]
        def _hh(solar):
            hh = Household(
                customer_id="C1", property_type=bh.property_type, build_era=bh.build_era,
                epc_rating="D", bedrooms=bh.bedrooms,
                heating_system=bh.heating_system, boiler_age=bh.boiler_age,
                insulation=bh.insulation,
                has_solar=solar, solar_kwp=(3.5 if solar else 0.0), solar_install_year=(2018 if solar else None),
                has_battery=False, battery_kwh=0.0,
                has_ev=False, ev_charger_kw=0.0,
                has_smart_meter=True, smart_meter_install_year=None,
            )
            reg._events["C1"] = []
            return hh
        reg._households["C1"] = _hh(True)
        m_solar = reg.eac_multiplier_for_date("C1", "2022-01-01")
        reg._households["C1"] = _hh(False)
        m_no = reg.eac_multiplier_for_date("C1", "2022-01-01")
        assert m_solar < m_no

    def test_adjusted_base_equals_declared_times_multiplier(self):
        from simulation.household_demand import HouseholdDemandRegister
        cust = [{"customer_id": "C1", "segment": "resi", "commodity": "electricity", "eac_kwh": 3100}]
        reg = HouseholdDemandRegister(cust, seed=42)
        m = reg.eac_multiplier_for_date("C1", "2018-01-01")
        declared = EFFECTIVE_EAC_KWH.get("C1", 0.0)
        override = float(max(1, round(declared * m)))
        eac = _company_eac_estimate("C1", "2018-01-01", [], base_eac_override=override)
        assert eac == override
