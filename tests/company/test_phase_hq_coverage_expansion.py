"""Phase HQ: Coverage expansion for 8 thin-test company modules."""
import datetime as dt
import pytest

# ===== switch_governance =====
from company.market.switch_governance import (
    COOLING_OFF_DAYS, OBJECTION_WINDOW_DAYS,
    ObjectionReason, ObjectionOutcome, ErroneousTransferStatus,
    CoolingOffCancellation, SwitchGovernanceBook,
)

class TestSwitchGovernanceExpanded:
    def test_cooling_off_boundary_exact(self):
        c = CoolingOffCancellation("C1","M1", dt.date(2022,1,1), dt.date(2022,1,1)+dt.timedelta(COOLING_OFF_DAYS))
        assert c.within_cooling_off

    def test_cancellations_in_cooling_off_count(self):
        book = SwitchGovernanceBook()
        book.record_cancellation("C1","M1", dt.date(2022,1,1), dt.date(2022,1,5))
        book.record_cancellation("C2","M2", dt.date(2022,1,1), dt.date(2022,2,5))
        assert book.cancellations_in_cooling_off() == 1

    def test_objection_id_format(self):
        book = SwitchGovernanceBook()
        obj = book.raise_objection("M1","S1",dt.date(2022,1,1),dt.date(2022,1,5),ObjectionReason.DEBT)
        assert obj.objection_id.startswith("OBJ-")

    def test_objection_sequential_ids(self):
        book = SwitchGovernanceBook()
        o1 = book.raise_objection("M1","S1",dt.date(2022,1,1),dt.date(2022,1,5),ObjectionReason.DEBT)
        o2 = book.raise_objection("M2","S1",dt.date(2022,1,1),dt.date(2022,1,5),ObjectionReason.DEBT)
        assert o1.objection_id != o2.objection_id

    def test_objection_withdrawn(self):
        book = SwitchGovernanceBook()
        obj = book.raise_objection("M1","S1",dt.date(2022,1,1),dt.date(2022,1,5),ObjectionReason.DEBT)
        book.resolve_objection(obj.objection_id, ObjectionOutcome.WITHDRAWN, dt.date(2022,1,20))
        assert obj.outcome == ObjectionOutcome.WITHDRAWN
        assert len(book.open_objections()) == 0

    def test_et_id_format(self):
        book = SwitchGovernanceBook()
        et = book.report_et("M1","L","G",dt.date(2022,1,1),dt.date(2022,1,7))
        assert et.et_id.startswith("ET-")

    def test_et_closed_no_action_resolves(self):
        book = SwitchGovernanceBook()
        et = book.report_et("M1","L","G",dt.date(2022,1,1),dt.date(2022,1,7))
        book.resolve_et(et.et_id, ErroneousTransferStatus.CLOSED_NO_ACTION, dt.date(2022,1,30))
        assert et.is_resolved

    def test_annual_summary_empty_year(self):
        book = SwitchGovernanceBook()
        s = book.annual_summary(1999)
        assert s["cooling_off_cancellations"] == 0
        assert s["erroneous_transfers"] == 0

    def test_annual_summary_ets_resolved_count(self):
        book = SwitchGovernanceBook()
        et = book.report_et("M1","L","G",dt.date(2022,5,1),dt.date(2022,5,5))
        book.resolve_et(et.et_id, ErroneousTransferStatus.CUSTOMER_RETURNED, dt.date(2022,5,20))
        s = book.annual_summary(2022)
        assert s["ets_resolved"] == 1

    def test_open_objections_cleared_after_resolve(self):
        book = SwitchGovernanceBook()
        obj = book.raise_objection("M1","S1",dt.date(2022,1,1),dt.date(2022,1,5),ObjectionReason.IDENTITY_MISMATCH)
        book.resolve_objection(obj.objection_id, ObjectionOutcome.REJECTED, dt.date(2022,1,15))
        assert book.open_objections() == []


# ===== dsr_book =====
from company.market.dsr_book import (
    DSRStatus, DispatchResult, DSRParticipant, DispatchEvent, DSRBook
)

class TestDSRBookExpanded:
    def _book_with_customer(self):
        book = DSRBook()
        book.enroll("C1","M1", contracted_mw=2.0, enrolled_date=dt.date(2022,1,1), payment_per_mwh_gbp=50.0)
        return book

    def _dispatch(self, book, delivered_mw=1.8, hours=2):
        start = dt.datetime(2022,6,1,10,0)
        end = start + dt.timedelta(hours=hours)
        return book.dispatch("C1", requested_mw=2.0, dispatch_start=start, dispatch_end=end, delivered_mw=delivered_mw)

    def test_participant_starts_active(self):
        book = self._book_with_customer()
        p = book._participants["C1"]
        assert p.status == DSRStatus.ACTIVE

    def test_dispatch_full_delivery(self):
        book = self._book_with_customer()
        ev = self._dispatch(book, delivered_mw=2.0)
        assert ev.result == DispatchResult.DELIVERED

    def test_dispatch_partial_delivery(self):
        book = self._book_with_customer()
        ev = self._dispatch(book, delivered_mw=1.0)
        assert ev.result == DispatchResult.PARTIAL

    def test_dispatch_non_delivery(self):
        book = self._book_with_customer()
        ev = self._dispatch(book, delivered_mw=0.0)
        assert ev.result == DispatchResult.NON_DELIVERY

    def test_payment_calculated_correctly(self):
        book = self._book_with_customer()
        ev = self._dispatch(book, delivered_mw=2.0, hours=2)
        assert ev.payment_gbp == pytest.approx(200.0)

    def test_event_id_format(self):
        book = self._book_with_customer()
        ev = self._dispatch(book)
        assert ev.event_id.startswith("DSR-")

    def test_total_contracted_mw(self):
        book = DSRBook()
        book.enroll("C1","M1",2.0,dt.date(2022,1,1))
        book.enroll("C2","M2",3.0,dt.date(2022,1,1))
        assert book.total_contracted_mw() == pytest.approx(5.0)

    def test_delivery_rate_year_none_when_no_events(self):
        book = self._book_with_customer()
        assert book.delivery_rate_year(2020) is None

    def test_total_payments_gbp_by_year(self):
        book = self._book_with_customer()
        self._dispatch(book, delivered_mw=2.0, hours=1)
        assert book.total_payments_gbp(2022) == pytest.approx(100.0)
        assert book.total_payments_gbp(2021) == 0.0

    def test_duration_hours_and_mwh(self):
        start = dt.datetime(2022,1,1,10,0)
        end = dt.datetime(2022,1,1,12,30)
        ev = DispatchEvent("E1","C1",2.0,2.0,start,end,DispatchResult.DELIVERED,100.0)
        assert ev.duration_hours == pytest.approx(2.5)
        assert ev.delivered_mwh == pytest.approx(5.0)


# ===== licence_health =====
from company.regulatory.licence_health import (
    LicenceCheckStatus, LicenceCheck, LicenceHealthReport,
    build_licence_health_report
)

def _healthy_report():
    return build_licence_health_report(
        as_of=dt.date(2022,3,31), active_customer_count=500,
        net_assets_gbp=500_000, treasury_gbp=500_000,
        weeks_cash_runway=20, bad_debt_ratio_pct=1.0,
        complaints_per_100=0.5,
    )

class TestLicenceHealthExpanded:
    def test_all_green_report(self):
        r = _healthy_report()
        assert r.overall_status == LicenceCheckStatus.PASS
        assert r.is_going_concern

    def test_breach_on_negative_net_assets(self):
        r = build_licence_health_report(dt.date(2022,1,1), 500, -1.0, 500_000, 20, 1.0, 0.5)
        assert r.breach_count > 0
        assert not r.is_going_concern

    def test_watch_on_low_treasury(self):
        r = build_licence_health_report(dt.date(2022,1,1), 500, 500_000, 120_000, 20, 1.0, 0.5)
        assert r.get("treasury_gbp").status == LicenceCheckStatus.WATCH

    def test_breach_on_low_cash_runway(self):
        r = build_licence_health_report(dt.date(2022,1,1), 500, 500_000, 500_000, 3, 1.0, 0.5)
        assert r.get("cash_runway_weeks").status == LicenceCheckStatus.BREACH

    def test_bad_debt_breach_above_5pct(self):
        r = build_licence_health_report(dt.date(2022,1,1), 500, 500_000, 500_000, 20, 6.0, 0.5)
        assert r.get("bad_debt_ratio").status == LicenceCheckStatus.BREACH

    def test_complaints_watch_1_to_3(self):
        r = build_licence_health_report(dt.date(2022,1,1), 500, 500_000, 500_000, 20, 1.0, 2.0)
        assert r.get("complaints_per_100").status == LicenceCheckStatus.WATCH

    def test_complaints_breach_above_3(self):
        r = build_licence_health_report(dt.date(2022,1,1), 500, 500_000, 500_000, 20, 1.0, 4.0)
        assert r.get("complaints_per_100").status == LicenceCheckStatus.BREACH

    def test_summary_keys_present(self):
        r = _healthy_report()
        s = r.summary()
        assert "overall_status" in s and "is_going_concern" in s

    def test_headroom_positive_when_passing(self):
        r = _healthy_report()
        check = r.get("net_assets_gbp")
        assert check.headroom > 0

    def test_get_returns_none_for_unknown(self):
        assert _healthy_report().get("nonexistent") is None


# ===== meter_read_validation =====
from company.billing.meter_read_validation import (
    ReadSource, ValidationResult, ValidationFlag, MeterReadValidation
)

def _mrv(read=10000, prev=9630, read_dt=None, prev_dt=None, expected_kwh=10.0):
    if read_dt is None: read_dt = dt.date(2022,6,1)
    if prev_dt is None: prev_dt = dt.date(2022,5,1)
    return MeterReadValidation(read_dt, read, prev, prev_dt, expected_kwh, ReadSource.CUSTOMER)

class TestMeterReadValidationExpanded:
    def test_accepted_normal_read(self):
        v = _mrv()
        assert v.result == ValidationResult.ACCEPTED
        assert v.flags == []

    def test_reversal_flag_negative_advance(self):
        v = _mrv(read=9000, prev=9630)
        assert ValidationFlag.REVERSAL in v.flags
        assert v.result == ValidationResult.REJECTED

    def test_excessive_rate_rejected(self):
        v = _mrv(read=10500, prev=9000, expected_kwh=5.0)
        assert ValidationFlag.EXCESSIVE_DAILY_RATE in v.flags
        assert v.result == ValidationResult.REJECTED

    def test_zero_advance_flag(self):
        v = _mrv(read=9630, prev=9630)
        assert ValidationFlag.METER_ADVANCE_ZERO in v.flags
        assert v.result == ValidationResult.QUERIED

    def test_low_rate_flag(self):
        v = _mrv(read=9631, prev=9630, expected_kwh=50.0)
        assert ValidationFlag.LOW_DAILY_RATE in v.flags
        assert v.result == ValidationResult.QUERIED

    def test_advance_kwh_and_days(self):
        v = _mrv()
        assert v.days_elapsed == 31
        assert v.advance_kwh == pytest.approx(370.0)

    def test_summary_keys(self):
        v = _mrv()
        s = v.summary()
        assert "result" in s and "flags" in s and "advance_kwh" in s

    def test_smart_meter_source_accepted(self):
        v = MeterReadValidation(dt.date(2022,6,1),10000,9630,dt.date(2022,5,1),10.0,ReadSource.SMART_METER)
        assert v.result == ValidationResult.ACCEPTED
