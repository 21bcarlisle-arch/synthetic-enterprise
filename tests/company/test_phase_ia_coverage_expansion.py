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
import datetime as dt
import datetime as dt
