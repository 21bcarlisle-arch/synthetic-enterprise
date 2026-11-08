"""Tests: Phase DC — EMIR Trade Repository Reporting Register."""
import datetime as dt
import pytest
from company.trading.emir_reporting_register import (
    EMIRReportingRegister, EMIRTradeRecord, ProductType, CounterpartyType,
    ReportingStatus, _add_working_days, _FCA_EMIR_MAX_FINE_GBP,
)

_EXEC_DATE = dt.date(2023, 6, 15)   # Thursday
_EXEC_DT = dt.datetime(2023, 6, 15, 9, 0, 0, tzinfo=dt.timezone.utc)
_DELIVERY_START = dt.date(2024, 1, 1)
_DELIVERY_END = dt.date(2024, 12, 31)
_CP_LEI = "9695005MSX1OYEMAUT49"


def _reg():
    return EMIRReportingRegister(our_lei="213800SYNTH00000001")


def _trade(reg, notional=500_000.0, product=ProductType.ELECTRICITY_FORWARD,
           cp_type=CounterpartyType.FINANCIAL_COUNTERPARTY, exec_date=_EXEC_DATE):
    return reg.record_trade(
        product_type=product,
        counterparty_id="CPY-001",
        counterparty_type=cp_type,
        counterparty_lei=_CP_LEI,
        notional_gbp=notional,
        price_gbp_per_mwh=120.0,
        delivery_start=_DELIVERY_START,
        delivery_end=_DELIVERY_END,
        execution_date=exec_date,
    )


# ── working day helper ───────────────────────────────────────────────────────

def test_add_working_day_skips_weekend():
    # Friday -> Monday (skip Sat/Sun)
    friday = dt.datetime(2023, 6, 16, 9, 0, tzinfo=dt.timezone.utc)
    result = _add_working_days(friday, 1)
    assert result.date() == dt.date(2023, 6, 19)  # Monday

def test_add_working_day_normal():
    # Thursday -> Friday
    result = _add_working_days(_EXEC_DT, 1)
    assert result.date() == dt.date(2023, 6, 16)


# ── record_trade ─────────────────────────────────────────────────────────────

def test_record_assigns_id():
    reg = _reg()
    t = _trade(reg)
    assert t.trade_id == "TRD-00001"

def test_record_pending_status():
    reg = _reg()
    t = _trade(reg)
    assert t.status == ReportingStatus.PENDING

def test_record_uti_format():
    reg = _reg()
    t = _trade(reg)
    assert "213800" in t.uti
    assert "20230615" in t.uti
    assert "TRD-00001" in t.uti

def test_record_our_lei():
    reg = _reg()
    t = _trade(reg)
    assert t.our_lei == "213800SYNTH00000001"

def test_record_deadline_is_next_working_day():
    # Thursday execution -> Friday deadline
    reg = _reg()
    t = _trade(reg)
    assert t.reporting_deadline.date() == dt.date(2023, 6, 16)

def test_record_increments_ids():
    reg = _reg()
    t1 = _trade(reg)
    t2 = _trade(reg)
    assert t1.trade_id == "TRD-00001"
    assert t2.trade_id == "TRD-00002"
    assert t1.uti != t2.uti

def test_record_different_products():
    reg = _reg()
    t = _trade(reg, product=ProductType.GAS_FORWARD)
    assert t.product_type == ProductType.GAS_FORWARD


# ── report ───────────────────────────────────────────────────────────────────

def test_report_within_deadline():
    reg = _reg()
    t = _trade(reg)
    # Report same day (within T+1 deadline)
    reported_at = _EXEC_DT + dt.timedelta(hours=6)
    updated = reg.report(t.trade_id, reported_at=reported_at, trade_repository_ref="TR-001")
    assert updated.status == ReportingStatus.REPORTED
    assert updated.trade_repository_ref == "TR-001"
    assert updated.is_late is False
    assert updated.is_reported is True

def test_report_after_deadline_late():
    reg = _reg()
    t = _trade(reg)
    # Report 3 days later (clearly late)
    reported_at = _EXEC_DT + dt.timedelta(days=3)
    updated = reg.report(t.trade_id, reported_at=reported_at)
    assert updated.status == ReportingStatus.LATE_REPORTED
    assert updated.is_late is True

def test_is_reported_true_for_reported():
    reg = _reg()
    t = _trade(reg)
    updated = reg.report(t.trade_id, reported_at=_EXEC_DT + dt.timedelta(hours=1))
    assert updated.is_reported is True

def test_is_reported_false_for_pending():
    reg = _reg()
    t = _trade(reg)
    assert t.is_reported is False


# ── amend / cancel / fail ────────────────────────────────────────────────────

def test_amend():
    reg = _reg()
    t = _trade(reg)
    reg.report(t.trade_id, reported_at=_EXEC_DT + dt.timedelta(hours=2))
    amended = reg.amend(t.trade_id, reported_at=_EXEC_DT + dt.timedelta(days=1),
                        reason="Notional correction")
    assert amended.status == ReportingStatus.AMENDED
    assert amended.amendment_reason == "Notional correction"
    assert amended.is_reported is True

def test_cancel():
    reg = _reg()
    t = _trade(reg)
    reg.report(t.trade_id, reported_at=_EXEC_DT + dt.timedelta(hours=1))
    cancelled = reg.cancel(t.trade_id, reported_at=_EXEC_DT + dt.timedelta(days=5))
    assert cancelled.status == ReportingStatus.CANCELLED
    assert cancelled.is_reported is True

def test_mark_failed():
    reg = _reg()
    t = _trade(reg)
    failed = reg.mark_failed(t.trade_id)
    assert failed.status == ReportingStatus.FAILED


# ── is_overdue ───────────────────────────────────────────────────────────────

def test_is_overdue_before_deadline():
    reg = _reg()
    t = _trade(reg)
    as_of = _EXEC_DT + dt.timedelta(hours=3)  # before deadline
    assert t.is_overdue(as_of) is False

def test_is_overdue_after_deadline():
    reg = _reg()
    t = _trade(reg)
    as_of = _EXEC_DT + dt.timedelta(days=3)  # well after deadline
    assert t.is_overdue(as_of) is True

def test_is_overdue_false_when_reported():
    reg = _reg()
    t = _trade(reg)
    updated = reg.report(t.trade_id, reported_at=_EXEC_DT + dt.timedelta(days=3))
    as_of = _EXEC_DT + dt.timedelta(days=4)
    assert updated.is_overdue(as_of) is False


# ── queries ──────────────────────────────────────────────────────────────────

def test_overdue_query():
    reg = _reg()
    t1 = _trade(reg)
    t2 = _trade(reg)
    reg.report(t2.trade_id, reported_at=_EXEC_DT + dt.timedelta(hours=1))
    as_of = _EXEC_DT + dt.timedelta(days=5)
    ov = reg.overdue(as_of)
    assert len(ov) == 1
    assert ov[0].trade_id == t1.trade_id

def test_pending_query():
    reg = _reg()
    _trade(reg)
    _trade(reg)
    assert len(reg.pending()) == 2

def test_late_reports_query():
    reg = _reg()
    t = _trade(reg)
    reg.report(t.trade_id, reported_at=_EXEC_DT + dt.timedelta(days=5))
    assert len(reg.late_reports()) == 1

def test_failed_reports_query():
    reg = _reg()
    t = _trade(reg)
    reg.mark_failed(t.trade_id)
    assert len(reg.failed_reports()) == 1

def test_by_product():
    reg = _reg()
    _trade(reg, product=ProductType.ELECTRICITY_FORWARD)
    _trade(reg, product=ProductType.GAS_FORWARD)
    _trade(reg, product=ProductType.ELECTRICITY_FORWARD)
    by_prod = reg.by_product()
    assert by_prod["elec_forward"] == 2
    assert by_prod["gas_forward"] == 1


# ── financial ────────────────────────────────────────────────────────────────

def test_total_notional_excludes_cancelled():
    reg = _reg()
    t1 = _trade(reg, notional=1_000_000.0)
    t2 = _trade(reg, notional=500_000.0)
    reg.report(t2.trade_id, reported_at=_EXEC_DT + dt.timedelta(hours=1))
    reg.cancel(t2.trade_id, reported_at=_EXEC_DT + dt.timedelta(days=2))
    assert reg.total_notional_gbp == 1_000_000.0

def test_compliance_rate_all_pending():
    reg = _reg()
    _trade(reg)
    _trade(reg)
    assert reg.reporting_compliance_rate == 0.0

def test_compliance_rate_all_reported():
    reg = _reg()
    t1 = _trade(reg)
    t2 = _trade(reg)
    reg.report(t1.trade_id, reported_at=_EXEC_DT + dt.timedelta(hours=1))
    reg.report(t2.trade_id, reported_at=_EXEC_DT + dt.timedelta(hours=2))
    assert reg.reporting_compliance_rate == 1.0

def test_compliance_rate_empty():
    reg = _reg()
    assert reg.reporting_compliance_rate == 1.0

def test_summary_format():
    reg = _reg()
    _trade(reg)
    s = reg.emir_reporting_summary()
    assert "EMIR Reporting" in s
    assert "1 trades" in s
    assert "Notional" in s
