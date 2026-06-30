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
