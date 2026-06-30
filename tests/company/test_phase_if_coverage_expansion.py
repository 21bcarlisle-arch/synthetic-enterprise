"""Phase IF: deeper coverage for dsr_book, licence_health, revenue_accruals."""
import datetime as dt
import pytest

# ===== dsr_book =====
from company.market.dsr_book import (
    DSRBook, DSRStatus, DispatchResult
)

def _dsr():
    book = DSRBook()
    book.enroll("C1","M001",2.0,dt.date(2022,1,1),payment_per_mwh_gbp=50.0)
    book.enroll("C2","M002",1.5,dt.date(2022,1,1),payment_per_mwh_gbp=40.0)
    start = dt.datetime(2022,11,4,17,0)
    end = dt.datetime(2022,11,4,19,0)  # 2 hours
    book.dispatch("C1",2.0,start,end,delivered_mw=1.98)  # >=95% = DELIVERED
    book.dispatch("C1",2.0,start,end,delivered_mw=0.5)   # partial
    return book

class TestDSRBookExpanded:
    def test_enroll_creates_active_participant(self):
        book = _dsr()
        p = book._participants["C1"]
        assert p.status == DSRStatus.ACTIVE

    def test_dispatch_delivered_when_gte_95pct(self):
        book = _dsr()
        ev = book._events[0]
        assert ev.result == DispatchResult.DELIVERED

    def test_dispatch_partial_when_some(self):
        book = _dsr()
        ev = book._events[1]
        assert ev.result == DispatchResult.PARTIAL

    def test_dispatch_duration_hours(self):
        book = _dsr()
        ev = book._events[0]
        assert ev.duration_hours == pytest.approx(2.0)

    def test_dispatch_delivered_mwh(self):
        book = _dsr()
        ev = book._events[0]
        assert ev.delivered_mwh == pytest.approx(1.98 * 2.0, rel=0.01)

    def test_delivery_rate_pct(self):
        book = _dsr()
        ev = book._events[0]
        assert ev.delivery_rate == pytest.approx(99.0)

    def test_dispatch_payment(self):
        book = _dsr()
        ev = book._events[0]
        # 1.98 mw * 2h * £50/MWh
        assert ev.payment_gbp == pytest.approx(1.98 * 2.0 * 50.0)

    def test_total_contracted_mw(self):
        book = _dsr()
        assert book.total_contracted_mw() == pytest.approx(3.5)

    def test_events_for_customer(self):
        book = _dsr()
        assert len(book.events_for_customer("C1")) == 2

    def test_annual_summary_keys(self):
        book = _dsr()
        s = book.annual_summary(2022)
        assert "dispatch_events" in s and "total_payments_gbp" in s


# ===== licence_health =====
from company.regulatory.licence_health import (
    build_licence_health_report, LicenceCheckStatus
)

def _healthy():
    return build_licence_health_report(
        as_of=dt.date(2022,6,30),
        active_customer_count=500,
        net_assets_gbp=1_000_000.0,
        treasury_gbp=500_000.0,
        weeks_cash_runway=20.0,
        bad_debt_ratio_pct=1.5,
        complaints_per_100=0.5,
    )

def _stressed():
    return build_licence_health_report(
        as_of=dt.date(2022,6,30),
        active_customer_count=60,
        net_assets_gbp=50_000.0,  # positive but near 0
        treasury_gbp=120_000.0,   # just above 100k threshold but watch zone
        weeks_cash_runway=6.0,    # below 8w threshold -> breach
        bad_debt_ratio_pct=4.0,   # watch zone (3-5%)
        complaints_per_100=1.5,   # watch zone (1-3)
    )

class TestLicenceHealthExpanded:
    def test_all_pass_healthy(self):
        report = _healthy()
        assert report.pass_count == 6
        assert report.breach_count == 0

    def test_overall_status_pass(self):
        report = _healthy()
        assert report.overall_status == LicenceCheckStatus.PASS

    def test_is_going_concern_when_no_breach(self):
        report = _healthy()
        assert report.is_going_concern

    def test_cash_runway_breach(self):
        report = _stressed()
        check = report.get("cash_runway_weeks")
        assert check.status == LicenceCheckStatus.BREACH
        assert not report.is_going_concern

    def test_bad_debt_watch_zone(self):
        report = _stressed()
        check = report.get("bad_debt_ratio")
        assert check.status == LicenceCheckStatus.WATCH

    def test_complaints_watch_zone(self):
        report = _stressed()
        check = report.get("complaints_per_100")
        assert check.status == LicenceCheckStatus.WATCH

    def test_headroom_calculation(self):
        report = _healthy()
        check = report.get("treasury_gbp")
        assert check.headroom == pytest.approx(400_000.0)

    def test_overall_breach_if_any_breach(self):
        report = _stressed()
        assert report.overall_status == LicenceCheckStatus.BREACH

    def test_summary_keys(self):
        report = _healthy()
        s = report.summary()
        assert "is_going_concern" in s and "overall_status" in s

    def test_get_by_name(self):
        report = _healthy()
        check = report.get("customer_count")
        assert check is not None and check.value == 500


# ===== revenue_accruals =====
from company.finance.revenue_accruals import (
    RevenueAccrualsLedger, RevenueType, RecognitionBasis
)

def _ledger():
    ledger = RevenueAccrualsLedger()
    q1_start, q1_end = dt.date(2022,1,1), dt.date(2022,3,31)
    ledger.post("C1",q1_start,q1_end,RevenueType.COMMODITY,RecognitionBasis.BILLED,1200.0)
    ledger.post("C2",q1_start,q1_end,RevenueType.COMMODITY,RecognitionBasis.ACCRUED,400.0)
    ledger.post("C1",q1_start,q1_end,RevenueType.STANDING_CHARGE,RecognitionBasis.BILLED,36.0)
    return ledger

class TestRevenueAccrualsLedgerExpanded:
    def test_period_days_90(self):
        ledger = _ledger()
        e = ledger._entries[0]
        assert e.period_days == 90  # Jan 1 to Mar 31 = 90 days

    def test_daily_revenue_gbp(self):
        ledger = _ledger()
        e = ledger._entries[0]
        assert e.daily_revenue_gbp == pytest.approx(1200.0/90, rel=0.01)

    def test_billed_revenue_in_period(self):
        ledger = _ledger()
        billed = ledger.billed_revenue_gbp(dt.date(2022,1,1),dt.date(2022,3,31))
        assert billed == pytest.approx(1236.0)  # 1200 + 36

    def test_accrued_revenue_in_period(self):
        ledger = _ledger()
        accrued = ledger.accrued_revenue_gbp(dt.date(2022,1,1),dt.date(2022,3,31))
        assert accrued == pytest.approx(400.0)

    def test_total_revenue_in_period(self):
        ledger = _ledger()
        total = ledger.total_revenue_gbp(dt.date(2022,1,1),dt.date(2022,3,31))
        assert total == pytest.approx(1636.0)

    def test_by_type_keys(self):
        ledger = _ledger()
        by_type = ledger.by_type(dt.date(2022,1,1),dt.date(2022,3,31))
        assert "commodity" in by_type and "standing_charge" in by_type

    def test_accrual_ratio(self):
        ledger = _ledger()
        ratio = ledger.accrual_ratio(dt.date(2022,1,1),dt.date(2022,3,31))
        assert ratio == pytest.approx(400/1636*100, rel=0.01)

    def test_accrual_ratio_none_when_no_entries(self):
        ledger = RevenueAccrualsLedger()
        assert ledger.accrual_ratio(dt.date(2022,1,1),dt.date(2022,3,31)) is None

    def test_monthly_summary_keys(self):
        ledger = _ledger()
        s = ledger.monthly_summary(2022,1)
        assert "billed_gbp" in s and "accrual_ratio_pct" in s

    def test_entries_in_period_excludes_non_overlapping(self):
        ledger = _ledger()
        # Q2 should not include Q1 entries
        entries = ledger.entries_in_period(dt.date(2022,4,1),dt.date(2022,6,30))
        assert len(entries) == 0
