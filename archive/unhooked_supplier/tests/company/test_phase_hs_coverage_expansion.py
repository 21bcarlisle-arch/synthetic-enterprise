# Increment 3: the legs of tests/company/test_phase_hs_coverage_expansion.py that test archived modules. Its live legs stay there.
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
