"""Phase ID: deeper coverage for gas_interruption, ee_obligation_tracker, credit_rating_book."""
import datetime as dt
import pytest

# ===== gas_interruption =====
from company.market.gas_interruption import (
    GasInterruptionManager, InterruptClass, InterruptionReason,
    InterruptionStatus, InterruptibilityContract
)

def _gim():
    mgr = GasInterruptionManager()
    mgr.register_contract("C1","M001",InterruptClass.INTERRUPTIBLE,max_per_year=4,min_notice_hours=4)
    mgr.register_contract("C2","M002",InterruptClass.FIRM,max_per_year=0,min_notice_hours=0)
    mgr.issue_interruption("I001","C1","M001",InterruptionReason.NETWORK_CONSTRAINT,
                            dt.date(2022,1,5),dt.date(2022,1,6),dt.date(2022,1,8))
    mgr.issue_interruption("I002","C2","M002",InterruptionReason.HEALTH_SAFETY,
                            dt.date(2022,2,1),dt.date(2022,2,2),dt.date(2022,2,5),is_vulnerable=True)
    return mgr

class TestGasInterruptionExpanded:
    def test_notice_days(self):
        mgr = _gim()
        i = mgr._interruptions[0]
        assert i.notice_days == 1

    def test_expected_duration_days(self):
        mgr = _gim()
        i = mgr._interruptions[0]
        assert i.expected_duration_days == 2

    def test_active_interruptions_initial(self):
        mgr = _gim()
        assert len(mgr.active_interruptions()) == 2

    def test_restore_removes_from_active(self):
        mgr = _gim()
        mgr._interruptions[0].restore(dt.date(2022,1,7))
        assert len(mgr.active_interruptions()) == 1

    def test_restore_sets_actual_duration(self):
        mgr = _gim()
        mgr._interruptions[0].restore(dt.date(2022,1,8))
        assert mgr._interruptions[0].actual_duration_days == 2

    def test_interruptions_for_customer(self):
        mgr = _gim()
        assert len(mgr.interruptions_for_customer("C1",2022)) == 1

    def test_vulnerable_customers_affected(self):
        mgr = _gim()
        vuln = mgr.vulnerable_customers_affected()
        assert "C2" in vuln

    def test_interruptible_discount_pct(self):
        mgr = _gim()
        c = mgr._contracts[0]
        assert c.discount_pct == pytest.approx(8.0)

    def test_firm_discount_zero(self):
        mgr = _gim()
        c = mgr._contracts[1]
        assert c.discount_pct == pytest.approx(0.0)

    def test_interruption_summary_keys(self):
        mgr = _gim()
        s = mgr.interruption_summary(2022)
        assert "total" in s and "vulnerable_affected" in s and s["total"] == 2


# ===== ee_obligation_tracker =====
from company.regulatory.ee_obligation_tracker import (
    EEObligationTracker, EEScheme, MeasureType, ReferralStatus
)

def _eet():
    tracker = EEObligationTracker()
    r1 = tracker.refer("R001","C1",EEScheme.ECO4,MeasureType.LOFT_INSULATION,dt.date(2023,1,10))
    r1.install(dt.date(2023,3,1),"InstallCo",cost_gbp=1200.0)
    r2 = tracker.refer("R002","C2",EEScheme.ECO4,MeasureType.SOLID_WALL,dt.date(2023,2,1),is_vulnerable=True)
    r2.install(dt.date(2023,4,15),"InstallCo",cost_gbp=5000.0)
    tracker.refer("R003","C3",EEScheme.WHD,MeasureType.BOILER_UPGRADE,dt.date(2023,3,1))
    return tracker

class TestEEObligationTrackerExpanded:
    def test_is_completed_after_install(self):
        tracker = _eet()
        r = tracker.get("R001")
        assert r.is_completed

    def test_not_completed_when_only_referred(self):
        tracker = _eet()
        r = tracker.get("R003")
        assert not r.is_completed

    def test_typical_saving_loft(self):
        tracker = _eet()
        r = tracker.get("R001")
        assert r.typical_annual_saving_kwh == pytest.approx(600.0)

    def test_typical_saving_solid_wall(self):
        tracker = _eet()
        r = tracker.get("R002")
        assert r.typical_annual_saving_kwh == pytest.approx(1200.0)

    def test_completed_measures_year_filter(self):
        tracker = _eet()
        done = tracker.completed_measures(2023)
        assert len(done) == 2

    def test_total_savings_kwh(self):
        tracker = _eet()
        total = tracker.total_savings_kwh(2023)
        assert total == pytest.approx(600.0 + 1200.0)

    def test_obligation_mwh_delivered(self):
        tracker = _eet()
        mwh = tracker.obligation_mwh_delivered(EEScheme.ECO4,2023)
        assert mwh == pytest.approx((600.0+1200.0)/1000, rel=0.01)

    def test_vulnerable_customer_count(self):
        tracker = _eet()
        assert tracker.vulnerable_customer_count(EEScheme.ECO4) == 1

    def test_portfolio_summary_keys(self):
        tracker = _eet()
        s = tracker.portfolio_summary(2023)
        assert "total_referrals" in s and "by_scheme" in s

    def test_portfolio_summary_by_scheme(self):
        tracker = _eet()
        s = tracker.portfolio_summary(2023)
        assert s["by_scheme"].get("eco4",0) == 2


# ===== credit_rating_book =====
from company.trading.credit_rating_book import (
    CreditRatingBook, CreditRating, is_investment_grade
)

def _crb():
    book = CreditRatingBook()
    book.register("CP1","Centrica Energy",CreditRating.A,"Moodys",dt.date(2022,1,1),5_000_000.0)
    book.register("CP2","Speculative Co",CreditRating.BB,"S&P",dt.date(2022,1,1),500_000.0)
    book.record_exposure("CP1",dt.date(2022,6,1),2_000_000.0,"forward")
    book.record_exposure("CP1",dt.date(2022,7,1),1_000_000.0,"spot")
    return book

class TestCreditRatingBookExpanded:
    def test_get_profile(self):
        book = _crb()
        p = book.get("CP1")
        assert p is not None and p.name == "Centrica Energy"

    def test_investment_grade_a_rating(self):
        book = _crb()
        assert book.get("CP1").is_investment_grade

    def test_sub_investment_grade_bb(self):
        book = _crb()
        assert not book.get("CP2").is_investment_grade

    def test_pd_pct_a_rating(self):
        book = _crb()
        assert book.get("CP1").pd_pct == pytest.approx(0.09)

    def test_total_exposure_gbp(self):
        book = _crb()
        assert book.total_exposure_gbp("CP1") == pytest.approx(3_000_000.0)

    def test_within_limit_true(self):
        book = _crb()
        assert book.is_within_limit("CP1",1_000_000.0)

    def test_within_limit_false_when_over(self):
        book = _crb()
        assert not book.is_within_limit("CP1",2_500_000.0)

    def test_sub_investment_grade_counterparties(self):
        book = _crb()
        subs = book.sub_investment_grade_counterparties()
        assert len(subs) == 1 and subs[0].counterparty_id == "CP2"

    def test_is_investment_grade_function_bbb(self):
        assert is_investment_grade(CreditRating.BBB)

    def test_credit_summary_keys(self):
        book = _crb()
        s = book.credit_summary()
        assert "investment_grade" in s and "total_exposure_gbp" in s and s["investment_grade"] == 1
