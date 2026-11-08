"""Tests for SoLR Levy Reconciliation Register (Phase ER)."""
import datetime as dt
import pytest
from company.regulatory.solr_levy_register import (
    LevyType, SoLRLevyCharge, SoLRLevyRegister,
)

DATE = dt.date(2022, 1, 15)


def make_charge(name="BulbEnergy", levy_type=LevyType.SOLR_LEVY,
                rate=0.05, mwh=10000.0, total_mwh=50_000_000.0, date=DATE):
    return SoLRLevyCharge(
        levy_type=levy_type,
        failed_supplier_name=name,
        levy_date=date,
        company_mwh_in_period=mwh,
        levy_rate_gbp_per_mwh=rate,
        total_market_mwh=total_mwh,
        company_share_fraction=mwh / total_mwh,
    )


class TestSoLRLevyCharge:
    def test_company_levy_gbp(self):
        c = make_charge(rate=0.10, mwh=5000.0)
        assert c.company_levy_gbp == pytest.approx(500.0)

    def test_market_total_levy_gbp(self):
        c = make_charge(rate=0.10, total_mwh=1_000_000.0)
        assert c.market_total_levy_gbp == pytest.approx(100_000.0)

    def test_is_significant_true(self):
        c = make_charge(rate=5.0, mwh=10000.0)   # 50000 > 10000
        assert c.is_significant

    def test_is_significant_false(self):
        c = make_charge(rate=0.001, mwh=100.0)   # 0.1 << 10000
        assert not c.is_significant

    def test_company_share_fraction(self):
        c = make_charge(mwh=5_000_000.0, total_mwh=50_000_000.0)
        assert c.company_share_fraction == pytest.approx(0.10)

    def test_levy_summary(self):
        c = make_charge()
        s = c.levy_summary()
        assert "BulbEnergy" in s
        assert "solr_levy" in s


class TestSoLRLevyRegister:
    def test_record_and_total(self):
        reg = SoLRLevyRegister()
        reg.record(make_charge(rate=0.10, mwh=5000.0))  # GBP 500
        assert reg.total_levy_paid_gbp() == pytest.approx(500.0)

    def test_year_filter(self):
        reg = SoLRLevyRegister()
        reg.record(make_charge(date=dt.date(2021, 11, 1), rate=1.0, mwh=100.0))
        reg.record(make_charge(date=dt.date(2022, 3, 1), rate=1.0, mwh=200.0))
        assert reg.total_levy_paid_gbp(year=2021) == pytest.approx(100.0)
        assert reg.total_levy_paid_gbp(year=2022) == pytest.approx(200.0)

    def test_solr_levies_filter(self):
        reg = SoLRLevyRegister()
        reg.record(make_charge(levy_type=LevyType.SOLR_LEVY))
        reg.record(make_charge(levy_type=LevyType.BSC_MUTUALISATION))
        assert len(reg.solr_levies()) == 1
        assert len(reg.mutualisation_charges()) == 1

    def test_significant_levies(self):
        reg = SoLRLevyRegister()
        reg.record(make_charge(rate=5.0, mwh=10000.0))  # significant
        reg.record(make_charge(rate=0.001, mwh=10.0))   # not significant
        assert len(reg.significant_levies()) == 1

    def test_unique_failed_suppliers(self):
        reg = SoLRLevyRegister()
        reg.record(make_charge(name="BulbEnergy"))
        reg.record(make_charge(name="BulbEnergy"))
        reg.record(make_charge(name="PurposeEnergy"))
        assert len(reg.unique_failed_suppliers()) == 2

    def test_market_loss_recovered(self):
        reg = SoLRLevyRegister()
        reg.record(make_charge(rate=1.0, total_mwh=1_000_000.0))
        assert reg.total_market_loss_recovered_gbp() == pytest.approx(1_000_000.0)

    def test_levy_register_summary(self):
        reg = SoLRLevyRegister()
        reg.record(make_charge())
        s = reg.levy_register_summary(DATE)
        assert "SoLR Levy Register" in s
        assert "1 failed" in s or "failed supplier" in s


# --- Phase MK depth tests ---

def test_levy_type_stored():
    c = make_charge(levy_type=LevyType.BSC_MUTUALISATION)
    assert c.levy_type == LevyType.BSC_MUTUALISATION


def test_failed_supplier_name_stored():
    c = make_charge(name="HarlequinEnergy")
    assert c.failed_supplier_name == "HarlequinEnergy"


def test_levy_date_stored():
    c = make_charge(date=dt.date(2022, 11, 1))
    assert c.levy_date == dt.date(2022, 11, 1)


def test_company_mwh_in_period_stored():
    c = make_charge(mwh=25000.0)
    assert c.company_mwh_in_period == pytest.approx(25000.0)


def test_levy_rate_gbp_per_mwh_stored():
    c = make_charge(rate=0.08)
    assert c.levy_rate_gbp_per_mwh == pytest.approx(0.08)


def test_total_market_mwh_stored():
    c = make_charge(total_mwh=80_000_000.0)
    assert c.total_market_mwh == pytest.approx(80_000_000.0)


def test_company_share_fraction_computed():
    c = make_charge(mwh=10000.0, total_mwh=1_000_000.0)
    assert c.company_share_fraction == pytest.approx(0.01)


def test_levy_type_has_3_members():
    assert len(list(LevyType)) == 3


def test_mutualisation_charges_filter():
    reg = SoLRLevyRegister()
    reg.record(make_charge(levy_type=LevyType.SOLR_LEVY))
    reg.record(make_charge(levy_type=LevyType.BSC_MUTUALISATION))
    assert len(reg.mutualisation_charges()) == 1
    assert reg.mutualisation_charges()[0].levy_type == LevyType.BSC_MUTUALISATION


def test_record_returns_solr_levy_charge():
    reg = SoLRLevyRegister()
    c = make_charge()
    result = reg.record(c)
    assert isinstance(result, SoLRLevyCharge)
