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


# ===== revenue_accruals =====
from company.finance.revenue_accruals import (
    RevenueType, RecognitionBasis, RevenueEntry, RevenueAccrualsLedger
)

class TestRevenueAccrualsExpanded:
    def _ledger(self):
        ledger = RevenueAccrualsLedger()
        ledger.post("C1",dt.date(2022,1,1),dt.date(2022,1,31),
                    RevenueType.COMMODITY, RecognitionBasis.BILLED, 100.0)
        ledger.post("C1",dt.date(2022,1,1),dt.date(2022,1,31),
                    RevenueType.COMMODITY, RecognitionBasis.ACCRUED, 30.0)
        return ledger

    def test_billed_revenue(self):
        l = self._ledger()
        assert l.billed_revenue_gbp(dt.date(2022,1,1),dt.date(2022,1,31)) == pytest.approx(100.0)

    def test_accrued_revenue(self):
        l = self._ledger()
        assert l.accrued_revenue_gbp(dt.date(2022,1,1),dt.date(2022,1,31)) == pytest.approx(30.0)

    def test_total_revenue(self):
        l = self._ledger()
        assert l.total_revenue_gbp(dt.date(2022,1,1),dt.date(2022,1,31)) == pytest.approx(130.0)

    def test_accrual_ratio(self):
        l = self._ledger()
        ratio = l.accrual_ratio(dt.date(2022,1,1),dt.date(2022,1,31))
        assert ratio == pytest.approx(30/130*100, rel=0.01)

    def test_accrual_ratio_none_when_empty(self):
        l = RevenueAccrualsLedger()
        assert l.accrual_ratio(dt.date(2022,1,1),dt.date(2022,1,31)) is None

    def test_by_type_separates_commodity(self):
        l = self._ledger()
        bt = l.by_type(dt.date(2022,1,1),dt.date(2022,1,31))
        assert "commodity" in bt
        assert bt["commodity"] == pytest.approx(130.0)

    def test_monthly_summary_keys(self):
        l = self._ledger()
        s = l.monthly_summary(2022, 1)
        assert "billed_gbp" in s and "accrued_gbp" in s and "total_gbp" in s

    def test_entries_in_period_boundary(self):
        ledger = RevenueAccrualsLedger()
        ledger.post("C1",dt.date(2022,1,1),dt.date(2022,1,31),
                    RevenueType.COMMODITY, RecognitionBasis.BILLED, 50.0)
        ledger.post("C1",dt.date(2022,3,1),dt.date(2022,3,31),
                    RevenueType.COMMODITY, RecognitionBasis.BILLED, 50.0)
        found = ledger.entries_in_period(dt.date(2022,1,1),dt.date(2022,1,31))
        assert len(found) == 1

    def test_period_days_and_daily_revenue(self):
        e = RevenueEntry("C1",dt.date(2022,1,1),dt.date(2022,1,10),
                         RevenueType.COMMODITY, RecognitionBasis.BILLED, 100.0, "electricity")
        assert e.period_days == 10
        assert e.daily_revenue_gbp == pytest.approx(10.0)


# ===== capacity_to_pay =====
from company.billing.capacity_to_pay import (
    AffordabilityOutcome, RecommendedAction, CtPAssessment
)

class TestCapacityToPayExpanded:
    def _assess(self, income=2000, outgoings=1500, debt=500, vulnerable=False):
        return CtPAssessment("C1", dt.date(2022,1,1), income, outgoings, debt, vulnerable)

    def test_can_pay_in_full(self):
        a = self._assess(income=3000, outgoings=1000, debt=200)
        assert a.outcome == AffordabilityOutcome.CAN_PAY_IN_FULL
        assert a.recommended_action == RecommendedAction.STANDARD_PLAN

    def test_cannot_pay_zero_disposable(self):
        a = self._assess(income=1000, outgoings=1000, debt=500)
        assert a.outcome == AffordabilityOutcome.CANNOT_PAY
        assert a.recommended_action == RecommendedAction.WRITE_OFF_CONSIDERATION

    def test_fuel_poverty_triggers_debt_advice(self):
        a = self._assess(income=500, outgoings=100, debt=1000)
        assert a.outcome == AffordabilityOutcome.FUEL_POVERTY
        assert a.recommended_action == RecommendedAction.DEBT_ADVICE_REFERRAL

    def test_fuel_poverty_vulnerable_gets_ppm(self):
        a = self._assess(income=500, outgoings=100, debt=1000, vulnerable=True)
        assert a.recommended_action == RecommendedAction.PPM_CONVERSION

    def test_can_pay_partial(self):
        a = self._assess(income=1100, outgoings=1000, debt=500)
        assert a.outcome == AffordabilityOutcome.CAN_PAY_PARTIAL

    def test_disposable_income(self):
        a = self._assess(income=2000, outgoings=1500)
        assert a.disposable_income_gbp == pytest.approx(500.0)

    def test_energy_share_pct(self):
        a = self._assess(income=1000, outgoings=500, debt=240)
        assert a.energy_share_of_income_pct == pytest.approx(2.0)

    def test_energy_share_none_zero_income(self):
        a = self._assess(income=0, outgoings=0, debt=100)
        assert a.energy_share_of_income_pct is None

    def test_summary_keys(self):
        a = self._assess()
        s = a.summary()
        assert "outcome" in s and "recommended_action" in s


# ===== eep_book =====
from company.crm.eep_book import EEPMeasure, EEPScheme, EEPBook

class TestEEPBookExpanded:
    def _book_with_record(self):
        book = EEPBook()
        book.record("C1","M1",EEPMeasure.LOFT_INSULATION,EEPScheme.ECO4,
                    dt.date(2022,6,1), estimated_annual_saving_gbp=200.0,
                    cost_gbp=1000.0, subsidy_gbp=800.0)
        return book

    def test_record_returns_installation(self):
        book = self._book_with_record()
        assert len(book._installs) == 1

    def test_installation_id_format(self):
        book = self._book_with_record()
        assert book._installs[0].installation_id.startswith("EEP-")

    def test_customer_cost(self):
        book = self._book_with_record()
        inst = book._installs[0]
        assert inst.customer_cost_gbp == pytest.approx(200.0)

    def test_simple_payback(self):
        book = self._book_with_record()
        inst = book._installs[0]
        assert inst.simple_payback_years == pytest.approx(1.0)

    def test_simple_payback_none_zero_saving(self):
        book = EEPBook()
        book.record("C1","M1",EEPMeasure.SOLAR_PV,EEPScheme.BUS,
                    dt.date(2022,1,1), 0.0, 5000.0, 0.0)
        assert book._installs[0].simple_payback_years is None

    def test_total_subsidy_by_scheme(self):
        book = self._book_with_record()
        assert book.total_subsidy_gbp(scheme=EEPScheme.ECO4) == pytest.approx(800.0)
        assert book.total_subsidy_gbp(scheme=EEPScheme.BUS) == 0.0

    def test_estimated_savings_portfolio(self):
        book = self._book_with_record()
        assert book.estimated_savings_portfolio_gbp() == pytest.approx(200.0)

    def test_installs_for_customer_filter(self):
        book = self._book_with_record()
        book.record("C2","M2",EEPMeasure.HEAT_PUMP,EEPScheme.BUS,
                    dt.date(2022,1,1), 400.0, 8000.0, 5000.0)
        assert len(book.installs_for_customer("C1")) == 1
        assert len(book.installs_for_customer("C2")) == 1

    def test_annual_summary_by_measure(self):
        book = self._book_with_record()
        s = book.annual_summary(2022)
        assert s["installations"] == 1
        assert "loft_insulation" in s["by_measure"]


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


# ===== portal_analytics =====
from company.crm.portal_analytics import PortalAction, PortalAnalytics

class TestPortalAnalyticsExpanded:
    def _analytics_with_events(self):
        pa = PortalAnalytics()
        base = dt.datetime(2022,3,1,10,0)
        pa.record("C1",PortalAction.LOGIN, base, "S1")
        pa.record("C1",PortalAction.SUBMIT_METER_READ, base+dt.timedelta(minutes=5), "S1")
        pa.record("C2",PortalAction.VIEW_BILL, base+dt.timedelta(hours=1), "S2")
        return pa, base

    def test_record_returns_event(self):
        pa = PortalAnalytics()
        ev = pa.record("C1",PortalAction.LOGIN,dt.datetime(2022,1,1,10,0),"S1")
        assert ev.event_id.startswith("PE-")

    def test_self_serve_action_flag(self):
        pa = PortalAnalytics()
        ev = pa.record("C1",PortalAction.SUBMIT_METER_READ,dt.datetime(2022,1,1,10,0),"S1")
        assert ev.is_self_serve

    def test_non_self_serve(self):
        pa = PortalAnalytics()
        ev = pa.record("C1",PortalAction.VIEW_BILL,dt.datetime(2022,1,1,10,0),"S1")
        assert not ev.is_self_serve

    def test_unique_users(self):
        pa, base = self._analytics_with_events()
        assert pa.unique_users(base-dt.timedelta(hours=1), base+dt.timedelta(hours=5)) == 2

    def test_self_serve_rate(self):
        pa, base = self._analytics_with_events()
        rate = pa.self_serve_rate(base-dt.timedelta(hours=1), base+dt.timedelta(hours=5))
        assert rate == pytest.approx(33.3, abs=0.1)

    def test_self_serve_rate_none_empty(self):
        pa = PortalAnalytics()
        assert pa.self_serve_rate(dt.datetime(2022,1,1), dt.datetime(2022,1,31)) is None

    def test_action_counts(self):
        pa, base = self._analytics_with_events()
        counts = pa.action_counts(base-dt.timedelta(hours=1), base+dt.timedelta(hours=5))
        assert counts["login"] == 1
        assert counts.get("view_bill") == 1

    def test_monthly_summary_keys(self):
        pa, base = self._analytics_with_events()
        s = pa.monthly_summary(2022, 3)
        assert "total_events" in s and "unique_users" in s and "self_serve_rate_pct" in s

    def test_events_in_period_filtered_by_action(self):
        pa, base = self._analytics_with_events()
        from_ = base - dt.timedelta(hours=1)
        to_ = base + dt.timedelta(hours=5)
        logins = pa.events_in_period(from_, to_, action=PortalAction.LOGIN)
        assert len(logins) == 1
