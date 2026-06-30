"""Phase HY: coverage expansion for customer_comm_preferences, portfolio_margin_sensitivity, shipper_code_register."""
import datetime as dt
import pytest

# ===== customer_comm_preferences =====
from company.crm.customer_comm_preferences import (
    CustomerCommPreferenceRegister, CommChannel, CommPurpose
)

class TestCustomerCommPreferences:
    def test_can_contact_billing_always_allowed(self):
        reg = CustomerCommPreferenceRegister()
        # BILLING is ESSENTIAL_PURPOSE — always reachable regardless of preferences
        assert reg.can_contact("C1", CommChannel.EMAIL, CommPurpose.BILLING)

    def test_marketing_blocked_without_opt_in(self):
        reg = CustomerCommPreferenceRegister()
        assert not reg.can_contact("C1", CommChannel.EMAIL, CommPurpose.MARKETING)

    def test_marketing_allowed_after_opt_in(self):
        reg = CustomerCommPreferenceRegister()
        reg.set_marketing_opt_in("C1", True, dt.date(2024, 1, 1))
        assert reg.can_contact("C1", CommChannel.EMAIL, CommPurpose.MARKETING)

    def test_suppress_blocks_marketing(self):
        reg = CustomerCommPreferenceRegister()
        reg.set_marketing_opt_in("C1", True, dt.date(2024, 1, 1))
        reg.suppress_account("C1")
        assert not reg.can_contact("C1", CommChannel.EMAIL, CommPurpose.MARKETING)

    def test_suppress_allows_billing_essential(self):
        reg = CustomerCommPreferenceRegister()
        reg.suppress_account("C1")
        assert reg.can_contact("C1", CommChannel.EMAIL, CommPurpose.BILLING)

    def test_latest_preference_wins(self):
        reg = CustomerCommPreferenceRegister()
        reg.set_preference("C1", CommChannel.SMS, False, dt.date(2023, 1, 1))
        reg.set_preference("C1", CommChannel.SMS, True, dt.date(2024, 1, 1))
        assert reg.can_contact("C1", CommChannel.SMS, CommPurpose.BILLING)

    def test_marketing_opt_in_accounts(self):
        reg = CustomerCommPreferenceRegister()
        reg.set_marketing_opt_in("C1", True, dt.date(2024, 1, 1))
        reg.set_marketing_opt_in("C2", False, dt.date(2024, 1, 1))
        assert "C1" in reg.marketing_opt_in_accounts
        assert "C2" not in reg.marketing_opt_in_accounts

    def test_suppressed_accounts(self):
        reg = CustomerCommPreferenceRegister()
        reg.suppress_account("C1")
        assert "C1" in reg.suppressed_accounts

    def test_paperless_accounts(self):
        reg = CustomerCommPreferenceRegister()
        reg.set_preference("C1", CommChannel.PAPER_BILL, False, dt.date(2024, 1, 1))
        assert "C1" in reg.paperless_accounts

    def test_comm_preference_summary_keys(self):
        reg = CustomerCommPreferenceRegister()
        reg.set_marketing_opt_in("C1", True, dt.date(2024, 1, 1))
        s = reg.comm_preference_summary()
        assert "GDPR" in s and "Marketing opt-in" in s


# ===== portfolio_margin_sensitivity =====
from company.finance.portfolio_margin_sensitivity import (
    PortfolioMarginSensitivityBook, SensitivityFactor
)

def _book(rev=10_000_000, whl=7_000_000, ncc=1_000_000,
          fixed=500_000, bad_debt=100_000, cap=200_000,
          n=10_000, churn=15.0):
    return PortfolioMarginSensitivityBook(
        base_revenue_gbp=rev, base_wholesale_cost_gbp=whl,
        base_non_commodity_cost_gbp=ncc, base_fixed_cost_gbp=fixed,
        base_bad_debt_gbp=bad_debt, base_capital_cost_gbp=cap,
        base_active_customers=n, base_churn_rate_pct=churn,
    )

class TestPortfolioMarginSensitivity:
    def test_base_net_margin(self):
        book = _book()
        # gross = 10M - 7M - 1M = 2M; net = 2M - 200k - 100k - 500k = 1.2M
        assert book.base_net_margin_gbp == pytest.approx(1_200_000.0)

    def test_wholesale_shock_reduces_margin(self):
        book = _book()
        result = book.wholesale_price_shock(10.0)  # +10% wholesale
        assert result.stressed_net_margin_gbp < book.base_net_margin_gbp
        assert result.delta_gbp < 0

    def test_wholesale_shock_factor(self):
        book = _book()
        result = book.wholesale_price_shock(10.0)
        # stressed_whl = 7M * 1.1 = 7.7M; additional cost = 700k
        assert result.delta_gbp == pytest.approx(-700_000.0)

    def test_demand_volume_shock_positive(self):
        book = _book()
        result = book.demand_volume_shock(10.0)  # +10% demand
        # Revenue up 10% = +1M, wholesale up 10% = +700k, net delta = +300k
        assert result.delta_gbp == pytest.approx(300_000.0)

    def test_churn_shock_reduces_margin(self):
        book = _book()
        result = book.churn_shock(5.0)  # +5% churn
        assert result.stressed_net_margin_gbp < book.base_net_margin_gbp

    def test_scenario_is_adverse(self):
        book = _book()
        result = book.wholesale_price_shock(50.0)
        assert result.is_adverse  # delta_gbp < 0

    def test_most_sensitive_factor_type(self):
        book = _book()
        f = book.most_sensitive_factor()
        assert isinstance(f, SensitivityFactor)

    def test_standard_sensitivity_table_returns_scenarios(self):
        book = _book()
        scenarios = book.standard_sensitivity_table()
        assert len(scenarios) >= 3

    def test_delta_pct_computed(self):
        book = _book()
        result = book.wholesale_price_shock(10.0)
        assert result.delta_pct != 0.0

    def test_severity_label_when_adverse(self):
        book = _book()
        result = book.wholesale_price_shock(100.0)
        assert result.severity in ("LOW", "MODERATE", "HIGH", "SEVERE")


# ===== shipper_code_register =====
from company.market.shipper_code_register import (
    ShipperCodeRegister, LDZ, ShipperStatus
)

class TestShipperCodeRegister:
    def test_register_creates_active_shipper(self):
        reg = ShipperCodeRegister()
        s = reg.register("AB", "Test Co", dt.date(2020, 1, 1))
        assert s.status == ShipperStatus.ACTIVE
        assert reg.get("AB") is s

    def test_add_ldz_authorisation(self):
        reg = ShipperCodeRegister()
        s = reg.register("AB", "Test Co", dt.date(2020, 1, 1))
        s.add_ldz(LDZ.EA, dt.date(2020, 1, 1))
        assert LDZ.EA in s.active_ldz_codes

    def test_revoke_ldz(self):
        reg = ShipperCodeRegister()
        s = reg.register("AB", "Test Co", dt.date(2020, 1, 1))
        s.add_ldz(LDZ.EA, dt.date(2020, 1, 1))
        s.revoke_ldz(LDZ.EA)
        assert LDZ.EA not in s.active_ldz_codes

    def test_can_supply_in_after_authorisation(self):
        reg = ShipperCodeRegister()
        s = reg.register("AB", "Test Co", dt.date(2020, 1, 1))
        s.add_ldz(LDZ.NT, dt.date(2020, 1, 1))
        assert s.can_supply_in(LDZ.NT)

    def test_cannot_supply_when_suspended(self):
        reg = ShipperCodeRegister()
        s = reg.register("AB", "Test Co", dt.date(2020, 1, 1))
        s.add_ldz(LDZ.EA, dt.date(2020, 1, 1))
        reg.suspend("AB")
        assert not reg.get("AB").can_supply_in(LDZ.EA)

    def test_suspend_moves_to_suspended(self):
        reg = ShipperCodeRegister()
        reg.register("AB", "Test Co", dt.date(2020, 1, 1))
        reg.suspend("AB")
        assert len(reg.suspended_shippers) == 1
        assert len(reg.active_shippers) == 0

    def test_ldz_coverage_count(self):
        reg = ShipperCodeRegister()
        s = reg.register("AB", "Test Co", dt.date(2020, 1, 1))
        s.add_ldz(LDZ.EA, dt.date(2020, 1, 1))
        s.add_ldz(LDZ.NT, dt.date(2020, 1, 1))
        assert s.ldz_coverage_count == 2

    def test_is_national_when_all_ldz(self):
        reg = ShipperCodeRegister()
        s = reg.register("AB", "Test Co", dt.date(2020, 1, 1))
        for ldz in LDZ:
            s.add_ldz(ldz, dt.date(2020, 1, 1))
        assert s.is_national

    def test_active_shippers_count(self):
        reg = ShipperCodeRegister()
        reg.register("AB", "Co A", dt.date(2020, 1, 1))
        reg.register("CD", "Co B", dt.date(2020, 1, 1))
        assert len(reg.active_shippers) == 2

    def test_shipper_summary_keys(self):
        reg = ShipperCodeRegister()
        reg.register("AB", "Test Co", dt.date(2020, 1, 1))
        s = reg.shipper_summary()
        assert "Shipper Code Register" in s and "Active" in s
