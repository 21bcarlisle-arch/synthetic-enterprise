"""Phase HS: coverage expansion for gas_interruption, solr_intake, ee_obligation_tracker."""
import datetime as dt
import pytest

# ===== gas_interruption =====
from company.market.gas_interruption import (
    InterruptClass, InterruptionReason, InterruptionStatus,
    InterruptibilityContract, GasInterruption, GasInterruptionManager,
    _INTERRUPTIBLE_DISCOUNT_PCT,
)

class TestGasInterruptionExpanded:
    def _manager(self):
        m = GasInterruptionManager()
        m.register_contract("C1","M1",InterruptClass.INTERRUPTIBLE,4,48)
        return m

    def _issue(self, m, cid="C1", mprn="M1", vulnerable=False):
        return m.issue_interruption(
            "INT-001", cid, mprn,
            InterruptionReason.NETWORK_CONSTRAINT,
            dt.date(2022,6,1), dt.date(2022,6,3), dt.date(2022,6,10),
            is_vulnerable=vulnerable,
        )

    def test_notice_days(self):
        m = self._manager()
        gi = self._issue(m)
        assert gi.notice_days == 2

    def test_expected_duration(self):
        m = self._manager()
        gi = self._issue(m)
        assert gi.expected_duration_days == 7

    def test_restore_sets_status(self):
        m = self._manager()
        gi = self._issue(m)
        gi.restore(dt.date(2022,6,8))
        assert gi.status == InterruptionStatus.RESTORED
        assert gi.actual_duration_days == 5

    def test_active_interruptions_before_restore(self):
        m = self._manager()
        self._issue(m)
        assert len(m.active_interruptions()) == 1

    def test_active_interruptions_after_restore(self):
        m = self._manager()
        gi = self._issue(m)
        gi.restore(dt.date(2022,6,8))
        assert len(m.active_interruptions()) == 0

    def test_vulnerable_customers_affected(self):
        m = self._manager()
        self._issue(m, vulnerable=True)
        assert "C1" in m.vulnerable_customers_affected()

    def test_interruptible_discount_pct(self):
        c = InterruptibilityContract("C1","M1",InterruptClass.INTERRUPTIBLE,4,48)
        assert c.discount_pct == pytest.approx(8.0)

    def test_firm_discount_zero(self):
        c = InterruptibilityContract("C1","M1",InterruptClass.FIRM,4,48)
        assert c.discount_pct == pytest.approx(0.0)

    def test_interruptions_for_customer_filter(self):
        m = self._manager()
        self._issue(m, cid="C1")
        m.issue_interruption("INT-002","C2","M2",InterruptionReason.NON_PAYMENT,
                             dt.date(2022,6,1),dt.date(2022,6,2),dt.date(2022,6,5))
        assert len(m.interruptions_for_customer("C1", 2022)) == 1

    def test_interruption_summary_keys(self):
        m = self._manager()
        self._issue(m)
        s = m.interruption_summary(2022)
        assert "total" in s and "vulnerable_affected" in s


# ===== solr_intake =====
from company.crm.solr_intake import (
    SoLRIntakeStatus, SoLRBatch, SoLRCustomer, SoLRBook
)

class TestSoLRBookExpanded:
    def _book(self):
        book = SoLRBook("US01")
        book.register_batch("B1","FailedCo",dt.date(2022,1,15),100)
        return book

    def test_register_batch_returns_batch(self):
        book = self._book()
        b = book._batches["B1"]
        assert b.failed_supplier == "FailedCo"
        assert b.customer_count == 100

    def test_batch_not_priced_above_cap_by_default(self):
        book = self._book()
        assert not book._batches["B1"].is_priced_above_cap

    def test_batch_above_cap(self):
        book = SoLRBook("US01")
        book.register_batch("B2","X",dt.date(2022,1,1),50, deemed_tariff_rate_pct_above_cap=5.0)
        assert book._batches["B2"].is_priced_above_cap

    def test_add_customer(self):
        book = self._book()
        c = book.add_customer("C1","B1","M1","resi")
        assert c.status == SoLRIntakeStatus.NOTIFIED
        assert not c.is_retained

    def test_mark_contacted(self):
        book = self._book()
        book.add_customer("C1","B1","M1","resi")
        c = book.mark_contacted("C1",dt.date(2022,1,17))
        assert c.status == SoLRIntakeStatus.CONTACTED

    def test_mark_onboarded(self):
        book = self._book()
        book.add_customer("C1","B1","M1","resi")
        c = book.mark_onboarded("C1",dt.date(2022,1,20))
        assert c.is_retained
        assert c.status == SoLRIntakeStatus.ONBOARDED

    def test_mark_switched_away(self):
        book = self._book()
        book.add_customer("C1","B1","M1","resi")
        c = book.mark_switched_away("C1",dt.date(2022,2,1))
        assert c.status == SoLRIntakeStatus.SWITCHED_AWAY

    def test_retention_rate(self):
        book = self._book()
        book.add_customer("C1","B1","M1","resi")
        book.add_customer("C2","B1","M2","resi")
        book.mark_onboarded("C1",dt.date(2022,1,20))
        assert book.retention_rate("B1") == pytest.approx(50.0)

    def test_contact_rate(self):
        book = self._book()
        book.add_customer("C1","B1","M1","resi")
        book.add_customer("C2","B1","M2","resi")
        book.mark_contacted("C1",dt.date(2022,1,17))
        book.mark_onboarded("C2",dt.date(2022,1,20))
        assert book.contact_rate("B1") == pytest.approx(100.0)

    def test_batch_summary_keys(self):
        book = self._book()
        book.add_customer("C1","B1","M1","resi")
        s = book.batch_summary("B1")
        assert "retention_rate_pct" in s and "actual_customers_received" in s


# ===== ee_obligation_tracker =====
from company.regulatory.ee_obligation_tracker import (
    EEScheme, MeasureType, ReferralStatus, EEReferral, EEObligationTracker
)

class TestEEObligationTrackerExpanded:
    def _tracker(self):
        t = EEObligationTracker()
        t.refer("R001","C1",EEScheme.ECO4,MeasureType.LOFT_INSULATION,dt.date(2022,3,1))
        return t

    def test_refer_returns_referral(self):
        t = self._tracker()
        r = t.get("R001")
        assert r is not None
        assert r.status == ReferralStatus.REFERRED

    def test_typical_saving_kwh(self):
        t = self._tracker()
        r = t.get("R001")
        assert r.typical_annual_saving_kwh == pytest.approx(600.0)

    def test_install_marks_completed(self):
        t = self._tracker()
        r = t.get("R001")
        r.install(dt.date(2022,6,1),"InstallerX", cost_gbp=500.0)
        assert r.is_completed
        assert r.installation_date == dt.date(2022,6,1)

    def test_completed_measures_filter_by_year(self):
        t = self._tracker()
        r = t.get("R001")
        r.install(dt.date(2022,6,1),"InstallerX")
        t.refer("R002","C2",EEScheme.ECO4,MeasureType.CAVITY_WALL,dt.date(2021,1,1))
        r2 = t.get("R002")
        r2.install(dt.date(2021,6,1),"InstallerY")
        assert len(t.completed_measures(2022)) == 1

    def test_total_savings_kwh_completed_only(self):
        t = self._tracker()
        r = t.get("R001")
        r.install(dt.date(2022,6,1),"InstallerX")
        assert t.total_savings_kwh(2022) == pytest.approx(600.0)

    def test_obligation_mwh_delivered(self):
        t = self._tracker()
        r = t.get("R001")
        r.install(dt.date(2022,6,1),"InstallerX")
        delivered = t.obligation_mwh_delivered(EEScheme.ECO4, 2022)
        assert delivered == pytest.approx(0.6)

    def test_vulnerable_customer_count(self):
        t = EEObligationTracker()
        t.refer("R1","C1",EEScheme.WHD,MeasureType.BOILER_UPGRADE,dt.date(2022,1,1),is_vulnerable=True)
        t.refer("R2","C2",EEScheme.WHD,MeasureType.BOILER_UPGRADE,dt.date(2022,1,1),is_vulnerable=False)
        assert t.vulnerable_customer_count(EEScheme.WHD) == 1

    def test_portfolio_summary_by_scheme(self):
        t = self._tracker()
        s = t.portfolio_summary(2022)
        assert s["total_referrals"] == 1
        assert "eco4" in s["by_scheme"]

    def test_get_returns_none_unknown(self):
        t = self._tracker()
        assert t.get("MISSING") is None

    def test_heat_pump_typical_saving(self):
        t = EEObligationTracker()
        t.refer("R1","C1",EEScheme.GBIS,MeasureType.HEAT_PUMP,dt.date(2022,1,1))
        r = t.get("R1")
        assert r.typical_annual_saving_kwh == pytest.approx(3000.0)
