# Increment 3: the legs of tests/company/test_phase_ju_coverage_depth.py that test archived modules. Its live legs stay there.
"""Phase JU: Coverage Depth Sprint XLIII -- 30 tests."""
import datetime as dt
import pytest
from company.finance.revenue_accruals import (
    RevenueType, RecognitionBasis, RevenueEntry, RevenueAccrualsLedger,
)
from company.crm.portal_analytics import PortalAction, PortalAnalytics


def _ledger():
    ledger = RevenueAccrualsLedger()
    ledger.post("C001", dt.date(2022, 1, 1), dt.date(2022, 1, 31),
                RevenueType.COMMODITY, RecognitionBasis.BILLED, 400.0)
    ledger.post("C002", dt.date(2022, 1, 1), dt.date(2022, 1, 31),
                RevenueType.COMMODITY, RecognitionBasis.ACCRUED, 100.0)
    return ledger


def test_ra_period_days_single_day():
    e = RevenueEntry("C001", dt.date(2022, 1, 15), dt.date(2022, 1, 15),
                     RevenueType.COMMODITY, RecognitionBasis.BILLED, 10.0, "electricity")
    assert e.period_days == 1
    assert e.daily_revenue_gbp == pytest.approx(10.0)


def test_ra_accrual_ratio_none_zero_total():
    ledger = RevenueAccrualsLedger()
    assert ledger.accrual_ratio(dt.date(2022, 1, 1), dt.date(2022, 1, 31)) is None


def test_ra_entries_overlap_start():
    ledger = RevenueAccrualsLedger()
    ledger.post("C001", dt.date(2021, 12, 15), dt.date(2022, 1, 15),
                RevenueType.COMMODITY, RecognitionBasis.BILLED, 200.0)
    assert len(ledger.entries_in_period(dt.date(2022, 1, 1), dt.date(2022, 1, 31))) == 1


def test_ra_entries_overlap_end():
    ledger = RevenueAccrualsLedger()
    ledger.post("C001", dt.date(2022, 1, 20), dt.date(2022, 2, 10),
                RevenueType.COMMODITY, RecognitionBasis.ACCRUED, 150.0)
    assert len(ledger.entries_in_period(dt.date(2022, 1, 1), dt.date(2022, 1, 31))) == 1


def test_ra_billed_excludes_accrued():
    ledger = _ledger()
    assert ledger.billed_revenue_gbp(dt.date(2022, 1, 1), dt.date(2022, 1, 31)) == pytest.approx(400.0)


def test_ra_accrued_excludes_billed():
    ledger = _ledger()
    assert ledger.accrued_revenue_gbp(dt.date(2022, 1, 1), dt.date(2022, 1, 31)) == pytest.approx(100.0)


def test_ra_by_type_exit_fee():
    ledger = RevenueAccrualsLedger()
    ledger.post("C001", dt.date(2022, 1, 1), dt.date(2022, 1, 31),
                RevenueType.EXIT_FEE, RecognitionBasis.BILLED, 75.0)
    bt = ledger.by_type(dt.date(2022, 1, 1), dt.date(2022, 1, 31))
    assert bt.get("exit_fee") == pytest.approx(75.0)


def test_ra_monthly_summary_december():
    ledger = RevenueAccrualsLedger()
    ledger.post("C001", dt.date(2022, 12, 1), dt.date(2022, 12, 31),
                RevenueType.COMMODITY, RecognitionBasis.BILLED, 900.0)
    s = ledger.monthly_summary(2022, 12)
    assert s["billed_gbp"] == pytest.approx(900.0)
    assert s["month"] == 12


def test_ra_multiple_customers_total():
    ledger = RevenueAccrualsLedger()
    ledger.post("C001", dt.date(2022, 3, 1), dt.date(2022, 3, 31),
                RevenueType.COMMODITY, RecognitionBasis.BILLED, 300.0)
    ledger.post("C002", dt.date(2022, 3, 1), dt.date(2022, 3, 31),
                RevenueType.COMMODITY, RecognitionBasis.BILLED, 700.0)
    assert ledger.total_revenue_gbp(dt.date(2022, 3, 1), dt.date(2022, 3, 31)) == pytest.approx(1000.0)


def test_ra_commodity_stored():
    ledger = RevenueAccrualsLedger()
    entry = ledger.post("C001", dt.date(2022, 1, 1), dt.date(2022, 1, 31),
                        RevenueType.COMMODITY, RecognitionBasis.BILLED, 300.0, "gas")
    assert entry.commodity == "gas"


def _pa():
    pa = PortalAnalytics()
    pa.record("C001", PortalAction.LOGIN, dt.datetime(2022, 3, 1, 9, 0), "S001")
    pa.record("C001", PortalAction.SUBMIT_METER_READ, dt.datetime(2022, 3, 1, 9, 5), "S001")
    pa.record("C002", PortalAction.CHANGE_DIRECT_DEBIT, dt.datetime(2022, 3, 2, 10, 0), "S002")
    pa.record("C003", PortalAction.VIEW_BILL, dt.datetime(2022, 3, 5, 14, 0), "S003")
    return pa


def _period():
    return dt.datetime(2022, 3, 1), dt.datetime(2022, 3, 31, 23, 59, 59)


def test_pa_event_id_pe000001():
    pa = PortalAnalytics()
    ev = pa.record("C001", PortalAction.LOGIN, dt.datetime(2022, 3, 1, 9, 0), "S001")
    assert ev.event_id == "PE-000001"


def test_pa_event_ids_sequential():
    pa = PortalAnalytics()
    e1 = pa.record("C001", PortalAction.LOGIN, dt.datetime(2022, 3, 1, 9, 0), "S001")
    e2 = pa.record("C001", PortalAction.VIEW_BILL, dt.datetime(2022, 3, 1, 9, 1), "S001")
    assert e1.event_id == "PE-000001" and e2.event_id == "PE-000002"


def test_pa_change_dd_is_self_serve():
    pa = PortalAnalytics()
    ev = pa.record("C001", PortalAction.CHANGE_DIRECT_DEBIT, dt.datetime(2022, 3, 1, 9, 0), "S001")
    assert ev.is_self_serve is True


def test_pa_enrol_paperless_is_self_serve():
    pa = PortalAnalytics()
    ev = pa.record("C001", PortalAction.ENROL_PAPERLESS, dt.datetime(2022, 3, 1, 9, 0), "S001")
    assert ev.is_self_serve is True


def test_pa_login_not_self_serve():
    pa = PortalAnalytics()
    ev = pa.record("C001", PortalAction.LOGIN, dt.datetime(2022, 3, 1, 9, 0), "S001")
    assert ev.is_self_serve is False


def test_pa_view_bill_not_self_serve():
    pa = PortalAnalytics()
    ev = pa.record("C001", PortalAction.VIEW_BILL, dt.datetime(2022, 3, 1, 9, 0), "S001")
    assert ev.is_self_serve is False


def test_pa_self_serve_rate_none_empty():
    pa = PortalAnalytics()
    assert pa.self_serve_rate(*_period()) is None


def test_pa_events_action_filter():
    pa = _pa()
    logins = pa.events_in_period(*_period(), action=PortalAction.LOGIN)
    assert len(logins) == 1 and all(e.action == PortalAction.LOGIN for e in logins)


def test_pa_unique_users_same_customer_twice():
    pa = PortalAnalytics()
    pa.record("C001", PortalAction.LOGIN, dt.datetime(2022, 3, 1, 9, 0), "S001")
    pa.record("C001", PortalAction.VIEW_BILL, dt.datetime(2022, 3, 1, 9, 5), "S001")
    assert pa.unique_users(*_period()) == 1


def test_pa_monthly_summary_year_month():
    s = _pa().monthly_summary(2022, 3)
    assert s["year"] == 2022 and s["month"] == 3
