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


# --- Phase ML depth tests ---

def test_assessment_date_stored():
    r = CreditCoverRecord(
        assessment_date=dt.date(2022, 11, 1),
        credit_assessment_price_gbp=500_000.0,
        credit_cover_posted_gbp=600_000.0,
        instrument_type=CreditInstrumentType.CASH_DEPOSIT,
    )
    assert r.assessment_date == dt.date(2022, 11, 1)


def test_credit_assessment_price_stored():
    r = CreditCoverRecord(
        assessment_date=dt.date(2022, 11, 1),
        credit_assessment_price_gbp=400_000.0,
        credit_cover_posted_gbp=500_000.0,
        instrument_type=CreditInstrumentType.BANK_GUARANTEE,
    )
    assert r.credit_assessment_price_gbp == pytest.approx(400_000.0)


def test_credit_cover_posted_stored():
    r = CreditCoverRecord(
        assessment_date=dt.date(2022, 11, 1),
        credit_assessment_price_gbp=400_000.0,
        credit_cover_posted_gbp=480_000.0,
        instrument_type=CreditInstrumentType.LETTER_OF_CREDIT,
    )
    assert r.credit_cover_posted_gbp == pytest.approx(480_000.0)


def test_instrument_type_stored():
    r = CreditCoverRecord(
        assessment_date=dt.date(2022, 11, 1),
        credit_assessment_price_gbp=400_000.0,
        credit_cover_posted_gbp=500_000.0,
        instrument_type=CreditInstrumentType.LETTER_OF_CREDIT,
    )
    assert r.instrument_type == CreditInstrumentType.LETTER_OF_CREDIT


def test_credit_instrument_type_has_3_members():
    assert len(list(CreditInstrumentType)) == 3


def test_bsc_credit_status_has_4_members():
    assert len(list(BSCCreditStatus)) == 4


def test_record_returns_credit_cover_record():
    reg = BSCCreditRegister()
    r = CreditCoverRecord(
        assessment_date=dt.date(2022, 11, 1),
        credit_assessment_price_gbp=400_000.0,
        credit_cover_posted_gbp=500_000.0,
        instrument_type=CreditInstrumentType.CASH_DEPOSIT,
    )
    result = reg.record(r)
    assert isinstance(result, CreditCoverRecord)


def test_cdn_date_recorded_when_in_default():
    reg = BSCCreditRegister()
    r = CreditCoverRecord(
        assessment_date=dt.date(2022, 11, 1),
        credit_assessment_price_gbp=500_000.0,
        credit_cover_posted_gbp=400_000.0,  # below CAP = CDN
        instrument_type=CreditInstrumentType.CASH_DEPOSIT,
    )
    reg.record(r)
    assert dt.date(2022, 11, 1) in reg._cdn_dates


def test_headroom_negative_when_short():
    r = CreditCoverRecord(
        assessment_date=dt.date(2022, 11, 1),
        credit_assessment_price_gbp=500_000.0,
        credit_cover_posted_gbp=400_000.0,
        instrument_type=CreditInstrumentType.CASH_DEPOSIT,
    )
    assert r.headroom_gbp == pytest.approx(-100_000.0)


def test_records_approaching_limit_filter():
    reg = BSCCreditRegister()
    # 110% ratio = APPROACHING (between 100-120%)
    r1 = CreditCoverRecord(dt.date(2022, 11, 1), 100_000.0, 110_000.0, CreditInstrumentType.CASH_DEPOSIT)
    # 150% ratio = COMPLIANT
    r2 = CreditCoverRecord(dt.date(2022, 11, 2), 100_000.0, 150_000.0, CreditInstrumentType.CASH_DEPOSIT)
    reg.record(r1)
    reg.record(r2)
    approaching = reg.records_approaching_limit()
    assert len(approaching) == 1
    assert approaching[0].status == BSCCreditStatus.APPROACHING_LIMIT


def test_min_cover_ratio_pct_returns_lowest():
    reg = BSCCreditRegister()
    reg.record(CreditCoverRecord(dt.date(2022, 11, 1), 100_000.0, 150_000.0, CreditInstrumentType.CASH_DEPOSIT))
    reg.record(CreditCoverRecord(dt.date(2022, 11, 2), 100_000.0, 125_000.0, CreditInstrumentType.CASH_DEPOSIT))
    assert reg.min_cover_ratio_pct() == pytest.approx(125.0)
