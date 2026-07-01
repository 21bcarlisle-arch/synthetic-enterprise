"""Phase JU: Coverage Depth Sprint XLIII -- 30 tests."""
import datetime as dt
import pytest
from company.finance.revenue_accruals import (
    RevenueType, RecognitionBasis, RevenueEntry, RevenueAccrualsLedger,
)
from company.market.dsr_book import DispatchResult, DSRBook
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


def _dsr():
    book = DSRBook()
    book.enroll("IC001", "1200011111", 2.0, dt.date(2021, 1, 1), payment_per_mwh_gbp=60.0)
    return book


def _dispatch(book, mw_req=2.0, mw_del=2.0, hours=1):
    start = dt.datetime(2022, 6, 1, 17, 0)
    end = start + dt.timedelta(hours=hours)
    return book.dispatch("IC001", mw_req, start, end, mw_del)


def test_dsr_event_id_dsr0001():
    assert _dispatch(_dsr()).event_id == "DSR-0001"


def test_dsr_event_ids_sequential():
    book = _dsr()
    e1 = _dispatch(book)
    e2 = _dispatch(book)
    assert e1.event_id == "DSR-0001" and e2.event_id == "DSR-0002"


def test_dsr_dispatch_95pct_is_delivered():
    ev = _dispatch(_dsr(), mw_req=2.0, mw_del=1.9)
    assert ev.delivery_rate == pytest.approx(95.0)
    assert ev.result == DispatchResult.DELIVERED


def test_dsr_dispatch_below_95pct_is_partial():
    ev = _dispatch(_dsr(), mw_req=2.0, mw_del=1.89)
    assert ev.result == DispatchResult.PARTIAL


def test_dsr_payment_calculated():
    ev = _dispatch(_dsr(), mw_req=2.0, mw_del=2.0, hours=2)
    assert ev.delivered_mwh == pytest.approx(4.0)
    assert ev.payment_gbp == pytest.approx(4.0 * 60.0)


def test_dsr_duration_hours_2h():
    assert _dispatch(_dsr(), hours=2).duration_hours == pytest.approx(2.0)


def test_dsr_delivered_mwh_3h():
    ev = _dispatch(_dsr(), mw_del=2.0, hours=3)
    assert ev.delivered_mwh == pytest.approx(6.0)


def test_dsr_events_for_customer_filter():
    book = DSRBook()
    book.enroll("IC001", "1200011111", 2.0, dt.date(2021, 1, 1))
    book.enroll("IC002", "1200022222", 1.5, dt.date(2021, 1, 1))
    s, e = dt.datetime(2022, 6, 1, 17, 0), dt.datetime(2022, 6, 1, 18, 0)
    book.dispatch("IC001", 2.0, s, e, 2.0)
    book.dispatch("IC002", 1.5, s, e, 1.5)
    book.dispatch("IC001", 2.0, s, e, 2.0)
    assert len(book.events_for_customer("IC001")) == 2
    assert len(book.events_for_customer("IC002")) == 1


def test_dsr_delivery_rate_year_none_empty():
    assert _dsr().delivery_rate_year(2023) is None


def test_dsr_delivery_rate_100_full():
    book = _dsr()
    _dispatch(book, mw_req=2.0, mw_del=2.0)
    assert book.delivery_rate_year(2022) == pytest.approx(100.0)


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
