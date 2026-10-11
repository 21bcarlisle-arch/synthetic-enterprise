"""Phase H: Electricity EAC Multiplier at Term Signing.

The household EAC multiplier (EV/solar/ASHP) is the WORLD's: these tests pin its behaviour. The
company's first-term volume no longer reads it (2026-10-11).
"""

from simulation.run_phase2b import _company_eac_estimate, EFFECTIVE_EAC_KWH


def _rec(cid, date, kwh):
    return {"customer_id": cid, "settlement_date": date, "consumption_kwh": float(kwh)}


class TestCompanyEACEstimateFirstTerm:
    """The override these tests pinned is gone (2026-10-11): it handed the hedge the household's
    own EV/solar/heat-pump multiplier, which no supplier can see. The company's first-term volume
    is the declared EAC; `tests/simulation/test_the_hedge_volume_reads_only_what_the_company_holds.py`
    holds the rest."""

    def test_first_term_uses_declared(self):
        eac = _company_eac_estimate("C1", "2016-07-01", [])
        assert eac == EFFECTIVE_EAC_KWH.get("C1", 0.0)


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
            has_driveway=True, roof_aspect="south",
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
                has_driveway=bh.has_driveway, roof_aspect=bh.roof_aspect,
            )
            reg._events["C1"] = []
            return hh
        reg._households["C1"] = _hh(True)
        m_solar = reg.eac_multiplier_for_date("C1", "2022-01-01")
        reg._households["C1"] = _hh(False)
        m_no = reg.eac_multiplier_for_date("C1", "2022-01-01")
        assert m_solar < m_no


class TestEACMultiplierEdgeCases:
    """Additional tests for _company_eac_estimate edge cases."""

    def test_known_customer_positive_eac(self):
        eac = _company_eac_estimate("C1", "2018-01-01", [])
        assert eac > 0.0

    def test_single_record_uses_history(self):
        recs = [_rec("C1", "2017-06-15", 100.0)]
        eac = _company_eac_estimate("C1", "2018-01-01", recs)
        assert eac > 0.0

    def test_effective_eac_nonempty(self):
        assert len(EFFECTIVE_EAC_KWH) > 0
