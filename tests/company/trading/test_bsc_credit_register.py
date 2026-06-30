"""Tests for BSC Credit Assurance Register (Phase FI)."""
import datetime as dt
import pytest
from company.trading.bsc_credit_register import (
    CreditInstrumentType, BSCCreditStatus, CreditCoverRecord, BSCCreditRegister,
)

DATE = dt.date(2024, 1, 15)


def make_rec(cap=500_000.0, cover=600_000.0,
             instr=CreditInstrumentType.BANK_GUARANTEE, date=DATE):
    return CreditCoverRecord(
        assessment_date=date,
        credit_assessment_price_gbp=cap,
        credit_cover_posted_gbp=cover,
        instrument_type=instr,
    )


class TestCreditCoverRecord:
    def test_cover_ratio_compliant(self):
        r = make_rec(cap=500_000, cover=600_000)
        assert r.cover_ratio_pct == pytest.approx(120.0)

    def test_cover_ratio_zero_cap(self):
        r = make_rec(cap=0.0, cover=100.0)
        assert r.cover_ratio_pct == pytest.approx(999.0)

    def test_headroom(self):
        r = make_rec(cap=500_000, cover=600_000)
        assert r.headroom_gbp == pytest.approx(100_000.0)

    def test_status_compliant(self):
        r = make_rec(cap=500_000, cover=700_000)  # >120%
        assert r.status == BSCCreditStatus.COMPLIANT

    def test_status_approaching(self):
        r = make_rec(cap=500_000, cover=550_000)  # 110% < 120%
        assert r.status == BSCCreditStatus.APPROACHING_LIMIT

    def test_status_cdn(self):
        r = make_rec(cap=500_000, cover=400_000)  # <100%
        assert r.status == BSCCreditStatus.CREDIT_DEFAULT_NOTICE

    def test_is_compliant(self):
        r = make_rec(cap=500_000, cover=700_000)
        assert r.is_compliant

    def test_credit_summary(self):
        s = make_rec().credit_summary()
        assert "BSCCredit" in s


class TestBSCCreditRegister:
    def test_record_and_latest(self):
        reg = BSCCreditRegister()
        reg.record(make_rec())
        assert reg.latest() is not None

    def test_records_in_default(self):
        reg = BSCCreditRegister()
        reg.record(make_rec(cap=500_000, cover=400_000))
        assert len(reg.records_in_default()) == 1

    def test_records_approaching(self):
        reg = BSCCreditRegister()
        reg.record(make_rec(cap=500_000, cover=550_000))
        assert len(reg.records_approaching_limit()) == 1

    def test_min_cover_ratio(self):
        reg = BSCCreditRegister()
        reg.record(make_rec(cap=500_000, cover=700_000))  # 140%
        reg.record(make_rec(cap=500_000, cover=550_000))  # 110%
        assert reg.min_cover_ratio_pct() == pytest.approx(110.0)

    def test_bsc_credit_summary(self):
        reg = BSCCreditRegister()
        reg.record(make_rec())
        s = reg.bsc_credit_summary(DATE)
        assert "BSC Credit Register" in s
