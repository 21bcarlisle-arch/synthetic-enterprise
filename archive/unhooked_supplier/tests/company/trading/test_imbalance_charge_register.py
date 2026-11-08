"""Tests for Imbalance Charge Register (Phase EN)."""
import datetime as dt
import pytest
from company.trading.imbalance_charge_register import (
    ImbalanceType, ImbalanceRecord, ImbalanceChargeRegister,
    _IMBALANCE_FLAT_TOLERANCE_MWH,
)

DATE = dt.date(2022, 9, 1)


def make_rec(nom=10.0, act=10.0, sbp=50.0, ssp=45.0, sp=12, date=DATE):
    return ImbalanceRecord(
        settlement_period=sp,
        settlement_date=date,
        nominated_mwh=nom,
        actual_mwh=act,
        sbp_gbp_per_mwh=sbp,
        ssp_gbp_per_mwh=ssp,
    )


class TestImbalanceRecord:
    def test_imbalance_mwh_short(self):
        r = make_rec(nom=10.0, act=12.0)
        assert r.imbalance_mwh == pytest.approx(2.0)

    def test_imbalance_mwh_long(self):
        r = make_rec(nom=10.0, act=8.0)
        assert r.imbalance_mwh == pytest.approx(-2.0)

    def test_type_short(self):
        r = make_rec(nom=10.0, act=12.0)
        assert r.imbalance_type == ImbalanceType.SHORT

    def test_type_long(self):
        r = make_rec(nom=10.0, act=8.0)
        assert r.imbalance_type == ImbalanceType.LONG

    def test_type_flat_within_tolerance(self):
        r = make_rec(nom=10.0, act=10.3)  # 0.3 < 0.5 tolerance
        assert r.imbalance_type == ImbalanceType.FLAT

    def test_charge_short_buys_at_sbp(self):
        r = make_rec(nom=10.0, act=12.0, sbp=50.0)
        assert r.charge_gbp == pytest.approx(2.0 * 50.0)

    def test_charge_long_credit_at_ssp(self):
        r = make_rec(nom=10.0, act=8.0, ssp=45.0)
        # negative imbalance * ssp -> negative charge (credit)
        assert r.charge_gbp == pytest.approx(-2.0 * 45.0)

    def test_charge_flat_is_zero(self):
        r = make_rec(nom=10.0, act=10.3)
        assert r.charge_gbp == 0.0

    def test_is_crisis_period_true(self):
        r = make_rec(sbp=1500.0)
        assert r.is_crisis_period

    def test_is_crisis_period_false(self):
        r = make_rec(sbp=50.0)
        assert not r.is_crisis_period

    def test_record_summary(self):
        r = make_rec(nom=10.0, act=12.0)
        s = r.record_summary()
        assert "short" in s
        assert str(DATE) in s


class TestImbalanceChargeRegister:
    def test_record_and_date_filter(self):
        reg = ImbalanceChargeRegister()
        reg.record(make_rec(date=DATE))
        assert len(reg.records_for_date(DATE)) == 1

    def test_month_filter(self):
        reg = ImbalanceChargeRegister()
        reg.record(make_rec(date=dt.date(2022, 9, 1)))
        reg.record(make_rec(date=dt.date(2022, 10, 1)))
        assert len(reg.records_for_month(2022, 9)) == 1

    def test_short_periods(self):
        reg = ImbalanceChargeRegister()
        reg.record(make_rec(nom=10, act=12))  # short
        reg.record(make_rec(nom=10, act=8))   # long
        assert len(reg.short_periods()) == 1

    def test_long_periods(self):
        reg = ImbalanceChargeRegister()
        reg.record(make_rec(nom=10, act=8))   # long
        assert len(reg.long_periods()) == 1

    def test_crisis_exposures(self):
        reg = ImbalanceChargeRegister()
        reg.record(make_rec(sbp=1500.0, nom=10, act=12))
        reg.record(make_rec(sbp=50.0, nom=10, act=12))
        assert len(reg.crisis_exposures()) == 1

    def test_total_charge_gbp(self):
        reg = ImbalanceChargeRegister()
        reg.record(make_rec(nom=10, act=12, sbp=50.0))  # 2 MWh * 50 = 100
        assert reg.total_charge_gbp() == pytest.approx(100.0)

    def test_total_charge_year_filter(self):
        reg = ImbalanceChargeRegister()
        reg.record(make_rec(nom=10, act=12, sbp=50.0, date=dt.date(2022, 1, 1)))
        reg.record(make_rec(nom=10, act=12, sbp=50.0, date=dt.date(2023, 1, 1)))
        assert reg.total_charge_gbp(year=2022) == pytest.approx(100.0)

    def test_net_imbalance_mwh(self):
        reg = ImbalanceChargeRegister()
        reg.record(make_rec(nom=10, act=12))   # +2
        reg.record(make_rec(nom=10, act=8))    # -2
        assert reg.net_imbalance_mwh() == pytest.approx(0.0)

    def test_average_sbp(self):
        reg = ImbalanceChargeRegister()
        reg.record(make_rec(sbp=50.0))
        reg.record(make_rec(sbp=100.0))
        assert reg.average_sbp() == pytest.approx(75.0)

    def test_average_sbp_empty(self):
        reg = ImbalanceChargeRegister()
        assert reg.average_sbp() == 0.0

    def test_imbalance_summary(self):
        reg = ImbalanceChargeRegister()
        reg.record(make_rec(nom=10, act=12))
        s = reg.imbalance_summary()
        assert "Imbalance Register" in s
