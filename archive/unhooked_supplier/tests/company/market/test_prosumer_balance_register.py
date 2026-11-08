"""Tests for Prosumer Balance Register (Phase EH)."""
import datetime as dt
import pytest
from company.market.prosumer_balance_register import (
    ProsumerStatus, V2GParticipationStatus,
    ProsumerPeriodBalance, ProsumerBalanceRegister,
)

START = dt.date(2024, 1, 1)
END = dt.date(2024, 1, 31)


def make_balance(account="C1", gross_import=1000.0, gross_export=200.0,
                 seg_rate=0.075, standing=0.50, v2g=0.0):
    return ProsumerPeriodBalance(
        account_id=account,
        period_start=START,
        period_end=END,
        gross_import_kwh=gross_import,
        gross_export_kwh=gross_export,
        seg_rate_gbp_per_kwh=seg_rate,
        standing_charge_gbp_per_day=standing,
        v2g_export_kwh=v2g,
    )


@pytest.fixture
def reg():
    return ProsumerBalanceRegister()


class TestProsumerPeriodBalance:
    def test_net_kwh(self):
        b = make_balance(gross_import=1000, gross_export=200)
        assert b.net_kwh == pytest.approx(800.0)

    def test_status_net_importer(self):
        b = make_balance(gross_import=1000, gross_export=200)
        assert b.status == ProsumerStatus.NET_IMPORTER

    def test_status_net_exporter(self):
        b = make_balance(gross_import=100, gross_export=800)
        assert b.status == ProsumerStatus.NET_EXPORTER

    def test_status_balanced(self):
        b = make_balance(gross_import=500, gross_export=450)  # net=50 within ±100
        assert b.status == ProsumerStatus.BALANCED

    def test_seg_payment(self):
        b = make_balance(gross_export=200.0, seg_rate=0.075)
        assert b.seg_payment_gbp == pytest.approx(15.0)

    def test_standing_charge_30_days(self):
        b = make_balance(standing=0.50)
        assert b.standing_charge_total_gbp == pytest.approx(15.0)  # 30 days * 0.5

    def test_net_bill_positive(self):
        b = make_balance(gross_export=0, standing=0.50)
        # standing only = +15; no SEG
        assert b.net_bill_gbp == pytest.approx(15.0)

    def test_net_bill_negative_when_high_export(self):
        b = make_balance(gross_export=1000.0, seg_rate=0.10, standing=0.10)
        # SEG = 100; standing = 3; net = -97
        assert b.net_bill_gbp < 0

    def test_v2g_fraction(self):
        b = make_balance(gross_export=200, v2g=100)
        assert b.v2g_fraction_pct == pytest.approx(50.0)

    def test_v2g_fraction_zero_export(self):
        b = make_balance(gross_export=0, v2g=0)
        assert b.v2g_fraction_pct == pytest.approx(0.0)


class TestProsumerBalanceRegister:
    def test_record_and_retrieve(self, reg):
        b = make_balance()
        reg.record_period(b)
        assert len(reg.balances_for("C1")) == 1

    def test_latest_balance(self, reg):
        b1 = make_balance("C1")
        b2 = ProsumerPeriodBalance(
            account_id="C1",
            period_start=dt.date(2024, 2, 1),
            period_end=dt.date(2024, 2, 28),
            gross_import_kwh=900,
            gross_export_kwh=300,
            seg_rate_gbp_per_kwh=0.075,
            standing_charge_gbp_per_day=0.5,
        )
        reg.record_period(b1)
        reg.record_period(b2)
        latest = reg.latest_balance("C1")
        assert latest is not None
        assert latest.period_end == dt.date(2024, 2, 28)

    def test_net_exporters(self, reg):
        reg.record_period(make_balance("C1", gross_import=100, gross_export=800))  # exporter
        reg.record_period(make_balance("C2", gross_import=1000, gross_export=200))  # importer
        assert "C1" in reg.net_exporters()
        assert "C2" not in reg.net_exporters()

    def test_v2g_enrolled(self, reg):
        reg.set_v2g_status("C1", V2GParticipationStatus.ENROLLED)
        reg.set_v2g_status("C2", V2GParticipationStatus.NOT_ENROLLED)
        assert "C1" in reg.v2g_enrolled()
        assert "C2" not in reg.v2g_enrolled()

    def test_total_seg_owed(self, reg):
        b = make_balance(gross_export=1000.0, seg_rate=0.10, standing=0.10)
        # SEG=100; standing=3; net=-97 owed to customer
        reg.record_period(b)
        assert reg.total_seg_owed_gbp() == pytest.approx(97.0)

    def test_prosumer_summary(self, reg):
        reg.record_period(make_balance())
        s = reg.prosumer_summary()
        assert "Prosumer Balance Register" in s
        assert "SEG" in s
