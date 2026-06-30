"""Phase IA: coverage expansion for gas_exit_analysis, dadc_contract_register, regulatory_breach_log."""
import datetime as dt
import pytest

from company.finance.gas_exit_analysis import (
    GasExitDecisionBook, GasAccountProfile
)

def _book(gas_net=50.0, elec_net=120.0, gas_rev=300.0):
    pcp = {
        "C1":  {"electricity": {"gross": 150.0, "capital": 0.0, "net": elec_net, "revenue": 400.0}},
        "C1g": {"gas": {"gross": 80.0, "capital": 200.0, "net": gas_net, "revenue": gas_rev}},
    }
    pcl = {"C1": {"segment": "resi"}}
    return GasExitDecisionBook(pcp, pcl, dual_fuel_pairs=[("C1", "C1g")])

class TestGasExitDecisionBook:
    def test_status_quo_net(self):
        book = _book(gas_net=50.0, elec_net=120.0)
        sq = book.status_quo()
        assert sq.total_net_gbp == pytest.approx(170.0)
        assert sq.customers_lost == 0

    def test_loss_making_accounts_when_gas_negative(self):
        book = _book(gas_net=-30.0, elec_net=120.0)
        assert len(book.loss_making_accounts()) == 1

    def test_accretive_accounts_when_gas_positive(self):
        book = _book(gas_net=50.0, elec_net=120.0)
        assert len(book.accretive_accounts()) == 1

    def test_is_gas_accretive_property(self):
        profile = GasAccountProfile("C1","resi",80.0,200.0,50.0,300.0,120.0,170.0)
        assert profile.is_gas_accretive

    def test_breakeven_revenue_uplift_when_loss_making(self):
        profile = GasAccountProfile("C1","resi",80.0,200.0,-30.0,300.0,120.0,90.0)
        assert profile.breakeven_revenue_uplift_pct == pytest.approx(0.10, rel=0.01)

    def test_exit_gas_scenario_has_customers_lost(self):
        book = _book(gas_net=-20.0, elec_net=100.0)
        result = book.exit_gas()
        assert result.scenario_name == "EXIT_GAS"
        assert result.gas_net_gbp == 0.0

    def test_reprice_gas_keeps_accretive(self):
        book = _book(gas_net=50.0, elec_net=120.0)
        result = book.reprice_gas()
        assert result.gas_net_gbp == pytest.approx(50.0)

    def test_reprice_gas_drops_loss_making(self):
        book = _book(gas_net=-20.0, elec_net=100.0)
        result = book.reprice_gas()
        assert result.gas_net_gbp == pytest.approx(0.0)

    def test_scenario_comparison_keys(self):
        book = _book()
        comp = book.scenario_comparison()
        assert "status_quo_net_gbp" in comp and "recommended_action" in comp

    def test_gas_exit_summary_keys(self):
        book = _book(gas_net=-20.0)
        s = book.gas_exit_summary()
        assert "Gas Exit Decision" in s and "Recommended action" in s


# ===== dadc_contract_register =====
from company.market.dadc_contract_register import (
    DADCContractRegister, MeteringAgentType, AgentAppointment
)
import datetime as dt

def _dadc():
    reg = DADCContractRegister()
    reg.appoint("M001", MeteringAgentType.DC, "Stark Metering", dt.date(2022,1,1))
    reg.appoint("M001", MeteringAgentType.DA, "Elexon Agent", dt.date(2022,1,1))
    reg.appoint("M002", MeteringAgentType.DA_DC, "Combined Co", dt.date(2022,3,1))
    return reg

class TestDADCContractRegister:
    def test_active_after_appoint(self):
        reg = _dadc()
        assert len(reg.active_appointments) == 3

    def test_agent_for_mpan_dc(self):
        reg = _dadc()
        appt = reg.agent_for_mpan("M001", MeteringAgentType.DC)
        assert appt is not None
        assert appt.agent_name == "Stark Metering"

    def test_agent_for_mpan_none_when_absent(self):
        reg = _dadc()
        assert reg.agent_for_mpan("M999", MeteringAgentType.DC) is None

    def test_terminate_removes_from_active(self):
        reg = _dadc()
        reg.terminate("M001", MeteringAgentType.DC, dt.date(2022,12,31))
        assert reg.agent_for_mpan("M001", MeteringAgentType.DC) is None

    def test_terminated_appointment_is_not_active(self):
        reg = _dadc()
        reg.terminate("M001", MeteringAgentType.DA, dt.date(2022,12,31))
        active = [a for a in reg.active_appointments if a.mpan == "M001"]
        assert all(a.agent_type != MeteringAgentType.DA for a in active)

    def test_mpans_without_dc_when_da_dc_covers(self):
        reg = _dadc()
        # M002 has DA_DC which counts as having DC
        no_dc = reg.mpans_without_dc()
        assert "M002" not in no_dc

    def test_mpans_without_da_none_when_all_covered(self):
        reg = _dadc()
        no_da = reg.mpans_without_da()
        assert "M001" not in no_da
        assert "M002" not in no_da

    def test_mpan_without_da_when_only_dc(self):
        reg = DADCContractRegister()
        reg.appoint("M003", MeteringAgentType.DC, "DC Only Co", dt.date(2022,1,1))
        assert "M003" in reg.mpans_without_da()

    def test_agents_by_name_count(self):
        reg = _dadc()
        by_name = reg.agents_by_name()
        assert by_name["Stark Metering"] == 1
        assert by_name["Combined Co"] == 1

    def test_da_dc_summary_contains_key_fields(self):
        reg = _dadc()
        s = reg.da_dc_summary()
        assert "Supply points" in s and "MPANs missing DC" in s


# ===== regulatory_breach_log =====
from company.regulatory.regulatory_breach_log import (
    RegulatoryBreachLog, BreachSeverity, BreachStatus, BreachSource
)
import datetime as dt

def _log():
    log = RegulatoryBreachLog()
    log.record("B001","SLC 14","Late bill", dt.date(2022,1,10), BreachSeverity.LOW, estimated_penalty_gbp=5000.0)
    log.record("B002","SLC 27A","Failure to report", dt.date(2022,2,1), BreachSeverity.HIGH, estimated_penalty_gbp=50000.0)
    log.record("B003","SLC 14","Systemic billing error", dt.date(2022,3,1), BreachSeverity.CRITICAL, estimated_penalty_gbp=200000.0)
    return log

class TestRegulatoryBreachLog:
    def test_record_creates_potential_status(self):
        log = _log()
        open_b = log.open_breaches
        assert all(b.status in (BreachStatus.POTENTIAL,) or b.is_open for b in open_b)

    def test_confirm_changes_status(self):
        log = _log()
        log.confirm("B001")
        b = next(b for b in log.open_breaches if b.breach_id == "B001")
        assert b.status == BreachStatus.CONFIRMED

    def test_report_to_ofgem(self):
        log = _log()
        log.report_to_ofgem("B002")
        b = next(b for b in log.open_breaches if b.breach_id == "B002")
        assert b.status == BreachStatus.REPORTED_TO_OFGEM

    def test_remediated_not_in_open_breaches(self):
        log = _log()
        log.remediate("B001", dt.date(2022,4,1))
        ids = [b.breach_id for b in log.open_breaches]
        assert "B001" not in ids

    def test_remediation_date_stored(self):
        log = _log()
        r = log.remediate("B001", dt.date(2022,4,1))
        assert r.remediation_date == dt.date(2022,4,1)

    def test_critical_breaches_filter(self):
        log = _log()
        crits = log.critical_breaches
        assert all(b.severity == BreachSeverity.CRITICAL for b in crits)
        assert len(crits) == 1

    def test_reportable_breaches_are_high_or_critical(self):
        log = _log()
        rep = log.reportable_breaches
        assert all(b.severity in (BreachSeverity.HIGH, BreachSeverity.CRITICAL) for b in rep)

    def test_total_estimated_penalty_open_only(self):
        log = _log()
        log.remediate("B003", dt.date(2022,5,1))
        total = log.total_estimated_penalty_gbp
        assert total == pytest.approx(55000.0)

    def test_by_slc_counts(self):
        log = _log()
        slc = log.by_slc()
        assert slc["SLC 14"] == 2
        assert slc["SLC 27A"] == 1

    def test_breach_summary_contains_key_words(self):
        log = _log()
        s = log.breach_summary()
        assert "Open" in s and "Reportable" in s and "penalty" in s
