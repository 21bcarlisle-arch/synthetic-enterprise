"""Tests for Debt Age Analysis Register (Phase FO)."""
import datetime as dt
import pytest
from company.finance.debt_age_analysis import (
    DebtAgeBucket, AgedDebt, DebtAgeAnalysisRegister, _PROVISION_RATE,
)

BASE_DATE = dt.date(2024, 1, 1)


def make_debt(days_old=0, amount=500.0, acct="C1"):
    invoice_date = BASE_DATE - dt.timedelta(days=days_old)
    return AgedDebt(account_id=acct, invoice_date=invoice_date,
                    outstanding_gbp=amount)


class TestAgedDebt:
    def test_bucket_current(self):
        d = make_debt(days_old=15)
        assert d.age_bucket(BASE_DATE) == DebtAgeBucket.CURRENT

    def test_bucket_31_60(self):
        d = make_debt(days_old=45)
        assert d.age_bucket(BASE_DATE) == DebtAgeBucket.DAYS_31_60

    def test_bucket_61_90(self):
        d = make_debt(days_old=75)
        assert d.age_bucket(BASE_DATE) == DebtAgeBucket.DAYS_61_90

    def test_bucket_91_180(self):
        d = make_debt(days_old=120)
        assert d.age_bucket(BASE_DATE) == DebtAgeBucket.DAYS_91_180

    def test_bucket_over_180(self):
        d = make_debt(days_old=200)
        assert d.age_bucket(BASE_DATE) == DebtAgeBucket.OVER_180

    def test_ecl_provision_current(self):
        d = make_debt(days_old=15, amount=1000.0)
        expected = 1000.0 * _PROVISION_RATE[DebtAgeBucket.CURRENT]
        assert d.ecl_provision_gbp(BASE_DATE) == pytest.approx(expected)

    def test_ecl_provision_over_180(self):
        d = make_debt(days_old=200, amount=1000.0)
        expected = 1000.0 * _PROVISION_RATE[DebtAgeBucket.OVER_180]
        assert d.ecl_provision_gbp(BASE_DATE) == pytest.approx(expected)

    def test_debt_summary(self):
        d = make_debt(days_old=15)
        s = d.debt_summary(BASE_DATE)
        assert "AgedDebt" in s and "ECL" in s


class TestDebtAgeAnalysisRegister:
    def test_debts_in_bucket(self):
        reg = DebtAgeAnalysisRegister()
        reg.record(make_debt(days_old=15))
        reg.record(make_debt(days_old=45, acct="C2"))
        assert len(reg.debts_in_bucket(DebtAgeBucket.CURRENT, BASE_DATE)) == 1

    def test_total_outstanding(self):
        reg = DebtAgeAnalysisRegister()
        reg.record(make_debt(amount=300.0))
        reg.record(make_debt(amount=200.0, acct="C2"))
        assert reg.total_outstanding_gbp() == pytest.approx(500.0)

    def test_total_ecl_provision(self):
        reg = DebtAgeAnalysisRegister()
        reg.record(make_debt(days_old=200, amount=1000.0))  # 80%
        assert reg.total_ecl_provision_gbp(BASE_DATE) == pytest.approx(800.0)

    def test_high_risk_debts(self):
        reg = DebtAgeAnalysisRegister()
        reg.record(make_debt(days_old=200))  # OVER_180
        reg.record(make_debt(days_old=10, acct="C2"))  # CURRENT
        assert len(reg.high_risk_debts(BASE_DATE)) == 1

    def test_debt_age_summary(self):
        reg = DebtAgeAnalysisRegister()
        reg.record(make_debt(days_old=15))
        s = reg.debt_age_summary(BASE_DATE)
        assert "Debt Age Analysis" in s


# --- Phase MH depth tests ---

def test_account_id_stored():
    d = make_debt(days_old=10, amount=300.0, acct="ACC-MH")
    assert d.account_id == "ACC-MH"


def test_invoice_date_stored():
    invoice = BASE_DATE - dt.timedelta(days=10)
    d = AgedDebt(account_id="C1", invoice_date=invoice, outstanding_gbp=200.0)
    assert d.invoice_date == invoice


def test_outstanding_gbp_stored():
    d = make_debt(days_old=5, amount=750.0)
    assert d.outstanding_gbp == pytest.approx(750.0)


def test_is_domestic_default_true():
    d = make_debt(days_old=5)
    assert d.is_domestic is True


def test_days_overdue_computed():
    d = make_debt(days_old=45)
    assert d.days_overdue(BASE_DATE) == 45


def test_record_returns_aged_debt():
    reg = DebtAgeAnalysisRegister()
    d = make_debt(days_old=10)
    result = reg.record(d)
    assert isinstance(result, AgedDebt)


def test_debt_age_bucket_has_5_members():
    assert len(list(DebtAgeBucket)) == 5


def test_total_in_bucket_gbp():
    reg = DebtAgeAnalysisRegister()
    reg.record(make_debt(days_old=10, amount=100.0))  # CURRENT
    reg.record(make_debt(days_old=15, amount=200.0))  # CURRENT
    reg.record(make_debt(days_old=45, amount=500.0))  # 31-60
    total = reg.total_in_bucket_gbp(DebtAgeBucket.CURRENT, BASE_DATE)
    assert total == pytest.approx(300.0)


def test_ecl_31_60_days_rate():
    d = make_debt(days_old=45, amount=1000.0)
    expected = 1000.0 * _PROVISION_RATE[DebtAgeBucket.DAYS_31_60]
    assert d.ecl_provision_gbp(BASE_DATE) == pytest.approx(expected)


def test_high_risk_debts_includes_over_180():
    reg = DebtAgeAnalysisRegister()
    reg.record(make_debt(days_old=10))    # CURRENT - not high risk
    reg.record(make_debt(days_old=200))   # OVER_180 - high risk
    high_risk = reg.high_risk_debts(BASE_DATE)
    assert len(high_risk) == 1
    assert high_risk[0].age_bucket(BASE_DATE) == DebtAgeBucket.OVER_180
