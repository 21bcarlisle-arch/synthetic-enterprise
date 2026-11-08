"""Tests for PortfolioRepricingBook — Phase AC."""
import pytest
from company.crm.eac_drift_assessor import EACDriftAssessment, EACDriftBook
from company.crm.portfolio_repricing import (
    PortfolioRepricingBook,
    RepricingAction,
    RepricingPriority,
)


# ---- helpers ----

def make_assessment(
    account_id="C1",
    original_aq=3000.0,
    current_eac=11000.0,
    has_ev=True,
    has_ashp=False,
    has_solar=False,
) -> EACDriftAssessment:
    return EACDriftAssessment(
        account_id=account_id,
        original_aq_kwh=original_aq,
        current_eac_kwh=current_eac,
        has_ev=has_ev,
        has_ashp=has_ashp,
        has_solar=has_solar,
    )


# ---- RepricingAction unit tests ----

class TestRepricingActionProperties:
    def test_tariff_delta_positive(self):
        assessment = make_assessment()
        book = PortfolioRepricingBook()
        action = book.plan_reprice(
            "C1", assessment,
            current_tariff_gbp_pa=750.0,
            days_to_renewal=45,
            unit_rate_p_per_kwh=25.0,
        )
        # recommended_tariff = 11000 * 0.25 = 2750
        assert action.tariff_delta_gbp_pa == pytest.approx(2000.0)

    def test_tariff_delta_negative_solar(self):
        assessment = make_assessment("C2", 4500.0, 2200.0, has_ev=False, has_solar=True)
        book = PortfolioRepricingBook()
        action = book.plan_reprice(
            "C2", assessment,
            current_tariff_gbp_pa=1125.0,
            days_to_renewal=120,
            unit_rate_p_per_kwh=25.0,
        )
        # recommended_tariff = 2200 * 0.25 = 550 → delta = -575
        assert action.tariff_delta_gbp_pa < 0

    def test_margin_recovery_positive(self):
        assessment = make_assessment()
        book = PortfolioRepricingBook()
        action = book.plan_reprice(
            "C1", assessment,
            current_tariff_gbp_pa=750.0,
            days_to_renewal=45,
            unit_rate_p_per_kwh=25.0,
        )
        # 2000 * 0.70 = 1400
        assert action.estimated_margin_recovery_gbp_pa == pytest.approx(1400.0)

    def test_margin_recovery_zero_when_tariff_falls(self):
        assessment = make_assessment("C2", 4500.0, 2200.0, has_ev=False, has_solar=True)
        book = PortfolioRepricingBook()
        action = book.plan_reprice(
            "C2", assessment,
            current_tariff_gbp_pa=1125.0,
            days_to_renewal=120,
            unit_rate_p_per_kwh=25.0,
        )
        assert action.estimated_margin_recovery_gbp_pa == 0.0

    def test_recommended_aq_equals_current_eac(self):
        assessment = make_assessment()
        book = PortfolioRepricingBook()
        action = book.plan_reprice("C1", assessment, 750.0, 45, 25.0)
        assert action.recommended_aq_kwh == 11000.0

    def test_standing_charge_included_in_recommended_tariff(self):
        assessment = make_assessment()
        book = PortfolioRepricingBook()
        action = book.plan_reprice("C1", assessment, 750.0, 45, 25.0, standing_charge_gbp_pa=100.0)
        assert action.recommended_tariff_gbp_pa == pytest.approx(2850.0)


# ---- Priority assignment tests ----

class TestRepricingPriority:
    def test_critical_urgent_drift_imminent_renewal(self):
        # +267% drift, 45 days to renewal -> CRITICAL
        assessment = make_assessment()
        book = PortfolioRepricingBook()
        action = book.plan_reprice("C1", assessment, 750.0, 45, 25.0)
        assert action.priority == RepricingPriority.CRITICAL

    def test_critical_edge_at_60_days(self):
        assessment = make_assessment()
        book = PortfolioRepricingBook()
        action = book.plan_reprice("C1", assessment, 750.0, 60, 25.0)
        assert action.priority == RepricingPriority.CRITICAL

    def test_high_urgent_drift_upcoming_renewal(self):
        # +267% drift, 120 days to renewal -> HIGH (not imminent but upcoming)
        assessment = make_assessment()
        book = PortfolioRepricingBook()
        action = book.plan_reprice("C1", assessment, 750.0, 120, 25.0)
        assert action.priority == RepricingPriority.HIGH

    def test_medium_moderate_drift_far_renewal(self):
        # +20% drift (REPRICE_UPWARD), 300 days -> MEDIUM
        assessment = make_assessment("C2", 5000.0, 6000.0, has_ev=True)
        book = PortfolioRepricingBook()
        action = book.plan_reprice("C2", assessment, 1250.0, 300, 25.0)
        assert action.priority == RepricingPriority.MEDIUM

    def test_monitor_stable_customer(self):
        # +3% drift -> MAINTAIN -> MONITOR
        assessment = make_assessment("C3", 4000.0, 4120.0, has_ev=False)
        book = PortfolioRepricingBook()
        action = book.plan_reprice("C3", assessment, 1030.0, 45, 25.0)
        assert action.priority == RepricingPriority.MONITOR

    def test_is_urgent_true_for_critical(self):
        assessment = make_assessment()
        book = PortfolioRepricingBook()
        action = book.plan_reprice("C1", assessment, 750.0, 45, 25.0)
        assert action.is_urgent is True

    def test_is_urgent_false_for_monitor(self):
        assessment = make_assessment("C3", 4000.0, 4120.0, has_ev=False)
        book = PortfolioRepricingBook()
        action = book.plan_reprice("C3", assessment, 1030.0, 45, 25.0)
        assert action.is_urgent is False

    def test_is_actionable_critical_and_high(self):
        book = PortfolioRepricingBook()
        a1 = book.plan_reprice("C1", make_assessment(), 750.0, 45, 25.0)
        a2 = book.plan_reprice("C2", make_assessment("C2"), 750.0, 120, 25.0)
        assert a1.is_actionable is True
        assert a2.is_actionable is True

    def test_is_actionable_false_monitor(self):
        assessment = make_assessment("C3", 4000.0, 4120.0, has_ev=False)
        book = PortfolioRepricingBook()
        action = book.plan_reprice("C3", assessment, 1030.0, 45, 25.0)
        assert action.is_actionable is False


# ---- PortfolioRepricingBook collection tests ----

class TestPortfolioRepricingBook:
    def _populated_book(self) -> PortfolioRepricingBook:
        book = PortfolioRepricingBook()
        # C1: +267% EV, 45 days -> CRITICAL
        book.plan_reprice("C1", make_assessment("C1", 3000.0, 11000.0, True), 750.0, 45, 25.0)
        # C2: +20% EV, 120 days -> HIGH
        book.plan_reprice("C2", make_assessment("C2", 5000.0, 6000.0, True), 1250.0, 120, 25.0)
        # C3: -25% solar, 90 days -> HIGH (downward, upcoming)
        book.plan_reprice("C3", make_assessment("C3", 4500.0, 3375.0, False, False, True), 1125.0, 90, 25.0)
        # C4: +3% stable, 30 days -> MONITOR
        book.plan_reprice("C4", make_assessment("C4", 4000.0, 4120.0, False), 1030.0, 30, 25.0)
        return book

    def test_critical_actions(self):
        book = self._populated_book()
        critical = book.critical_actions()
        assert len(critical) == 1
        assert critical[0].account_id == "C1"

    def test_actionable_actions(self):
        book = self._populated_book()
        actionable = book.actionable_actions()
        ids = {a.account_id for a in actionable}
        assert "C1" in ids
        assert "C2" in ids
        assert "C3" in ids
        assert "C4" not in ids

    def test_by_priority(self):
        book = self._populated_book()
        high = book.by_priority(RepricingPriority.HIGH)
        ids = {a.account_id for a in high}
        assert "C2" in ids
        assert "C3" in ids

    def test_total_margin_at_risk_only_upward_critical(self):
        book = self._populated_book()
        # CRITICAL is C1 only; tariff_delta = 2750 - 750 = 2000
        assert book.total_margin_at_risk_gbp() == pytest.approx(2000.0)

    def test_total_expected_recovery(self):
        book = self._populated_book()
        # Only positive tariff deltas contribute
        expected = book.total_expected_recovery_gbp()
        assert expected > 0.0

    def test_top_n_by_margin_recovery(self):
        book = self._populated_book()
        top = book.top_n_by_margin_recovery(n=2)
        assert len(top) == 2
        # C1 has biggest delta (2000 GBP) -> should be first
        assert top[0].account_id == "C1"

    def test_portfolio_reprice_summary_keys(self):
        book = self._populated_book()
        s = book.portfolio_reprice_summary()
        assert s["customers_planned"] == 4
        assert s["critical_count"] == 1
        assert s["actionable_count"] == 3
        assert "total_margin_at_risk_gbp" in s
        assert "total_expected_recovery_gbp" in s

    def test_empty_book_summary(self):
        book = PortfolioRepricingBook()
        s = book.portfolio_reprice_summary()
        assert s["customers_planned"] == 0
        assert s["total_margin_at_risk_gbp"] == 0.0

    def test_all_actions_returns_list(self):
        book = self._populated_book()
        assert len(book.all_actions) == 4
