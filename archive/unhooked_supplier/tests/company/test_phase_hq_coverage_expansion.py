# Increment 3: the legs of tests/company/test_phase_hq_coverage_expansion.py that test archived modules. Its live legs stay there.
"""Phase HQ: Coverage expansion for 8 thin-test company modules."""
import datetime as dt
import pytest


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
