"""Tests for EACDriftAssessor — Phase AB."""
import pytest
from company.crm.eac_drift_assessor import (
    DriftDirection,
    EACDriftAssessment,
    EACDriftBook,
    RenewalAction,
)


# --- EACDriftAssessment unit tests ---

class TestDriftCalculations:
    def test_drift_kwh_positive(self):
        a = EACDriftAssessment("C1", 3000.0, 11000.0, has_ev=True, has_ashp=False, has_solar=False)
        assert a.drift_kwh == 8000.0

    def test_drift_kwh_negative(self):
        a = EACDriftAssessment("C2", 4000.0, 2500.0, has_ev=False, has_ashp=False, has_solar=True)
        assert a.drift_kwh == -1500.0

    def test_drift_kwh_zero(self):
        a = EACDriftAssessment("C3", 5000.0, 5000.0, False, False, False)
        assert a.drift_kwh == 0.0

    def test_drift_pct_increase(self):
        a = EACDriftAssessment("C1", 4000.0, 6000.0, True, False, False)
        assert a.drift_pct == pytest.approx(50.0)

    def test_drift_pct_decrease(self):
        a = EACDriftAssessment("C2", 4000.0, 3200.0, False, False, True)
        assert a.drift_pct == pytest.approx(-20.0)

    def test_drift_pct_small_aq_returns_zero(self):
        a = EACDriftAssessment("C3", 50.0, 100.0, False, False, False)
        assert a.drift_pct == 0.0


class TestDriftDirection:
    def test_increased_direction(self):
        # +267% = well above 15% threshold
        a = EACDriftAssessment("C1", 3000.0, 11000.0, True, False, False)
        assert a.drift_direction == DriftDirection.INCREASED

    def test_decreased_direction(self):
        # -25% = below -10% threshold
        a = EACDriftAssessment("C2", 4000.0, 3000.0, False, False, True)
        assert a.drift_direction == DriftDirection.DECREASED

    def test_stable_direction_small_increase(self):
        # +5% = below 15% threshold
        a = EACDriftAssessment("C3", 4000.0, 4200.0, False, False, False)
        assert a.drift_direction == DriftDirection.STABLE

    def test_stable_direction_small_decrease(self):
        # -5% = above -10% threshold
        a = EACDriftAssessment("C4", 4000.0, 3800.0, False, False, False)
        assert a.drift_direction == DriftDirection.STABLE

    def test_at_increase_threshold_is_increased(self):
        # Exactly +15%
        a = EACDriftAssessment("C5", 4000.0, 4600.0, True, False, False)
        assert a.drift_direction == DriftDirection.INCREASED

    def test_at_decrease_threshold_is_decreased(self):
        # Exactly -10%
        a = EACDriftAssessment("C6", 4000.0, 3600.0, False, False, True)
        assert a.drift_direction == DriftDirection.DECREASED


class TestLikelyCause:
    def test_ev_acquired(self):
        a = EACDriftAssessment("C1", 3000.0, 11000.0, has_ev=True, has_ashp=False, has_solar=False)
        assert a.likely_cause == "ev_acquired"

    def test_ashp_installed(self):
        a = EACDriftAssessment("C2", 3000.0, 10000.0, has_ev=False, has_ashp=True, has_solar=False)
        assert a.likely_cause == "ashp_installed"

    def test_ev_and_ashp(self):
        a = EACDriftAssessment("C3", 3000.0, 15000.0, has_ev=True, has_ashp=True, has_solar=False)
        assert a.likely_cause == "ev_and_ashp_acquired"

    def test_solar_installed(self):
        a = EACDriftAssessment("C4", 4000.0, 2500.0, has_ev=False, has_ashp=False, has_solar=True)
        assert a.likely_cause == "solar_installed"

    def test_unknown_increase(self):
        a = EACDriftAssessment("C5", 3000.0, 6000.0, False, False, False)
        assert a.likely_cause == "consumption_uplift_unknown"

    def test_unknown_decrease(self):
        a = EACDriftAssessment("C6", 5000.0, 3000.0, False, False, False)
        assert a.likely_cause == "consumption_reduction_unknown"

    def test_stable_cause(self):
        a = EACDriftAssessment("C7", 4000.0, 4100.0, False, False, False)
        assert a.likely_cause == "stable"


class TestRenewalAction:
    def test_urgent_reprice_at_30pct(self):
        # +267% drift
        a = EACDriftAssessment("C1", 3000.0, 11000.0, True, False, False)
        assert a.renewal_action == RenewalAction.URGENT_REPRICE

    def test_reprice_upward_moderate_increase(self):
        # +20% (above 15%, below 30%)
        a = EACDriftAssessment("C2", 5000.0, 6000.0, True, False, False)
        assert a.renewal_action == RenewalAction.REPRICE_UPWARD

    def test_reprice_downward_solar(self):
        a = EACDriftAssessment("C3", 4000.0, 2800.0, False, False, True)
        assert a.renewal_action == RenewalAction.REPRICE_DOWNWARD

    def test_maintain_stable(self):
        a = EACDriftAssessment("C4", 4000.0, 4100.0, False, False, False)
        assert a.renewal_action == RenewalAction.MAINTAIN

    def test_is_material_true(self):
        a = EACDriftAssessment("C5", 3000.0, 11000.0, True, False, False)
        assert a.is_material is True

    def test_is_material_false_stable(self):
        a = EACDriftAssessment("C6", 4000.0, 4100.0, False, False, False)
        assert a.is_material is False


# --- EACDriftBook tests ---

class TestEACDriftBook:
    def _book_with_portfolio(self) -> EACDriftBook:
        book = EACDriftBook()
        # EV customer — big increase
        book.assess("C1", 3000.0, 11000.0, has_ev=True)
        # ASHP customer — moderate increase
        book.assess("C2", 4000.0, 9500.0, has_ashp=True)
        # Solar customer — decrease
        book.assess("C3", 4500.0, 2500.0, has_solar=True)
        # Stable customer
        book.assess("C4", 5000.0, 5200.0)
        return book

    def test_assess_returns_assessment(self):
        book = EACDriftBook()
        a = book.assess("C1", 3000.0, 11000.0, has_ev=True)
        assert isinstance(a, EACDriftAssessment)
        assert a.account_id == "C1"

    def test_significant_increases(self):
        book = self._book_with_portfolio()
        increases = book.significant_increases()
        ids = {a.account_id for a in increases}
        assert "C1" in ids
        assert "C2" in ids
        assert "C3" not in ids
        assert "C4" not in ids

    def test_significant_decreases(self):
        book = self._book_with_portfolio()
        decreases = book.significant_decreases()
        assert len(decreases) == 1
        assert decreases[0].account_id == "C3"

    def test_renewal_reprice_candidates_excludes_stable(self):
        book = self._book_with_portfolio()
        candidates = book.renewal_reprice_candidates()
        ids = {a.account_id for a in candidates}
        assert "C4" not in ids
        assert "C1" in ids
        assert "C2" in ids
        assert "C3" in ids

    def test_urgent_reprice_candidates(self):
        book = self._book_with_portfolio()
        urgent = book.urgent_reprice_candidates()
        ids = {a.account_id for a in urgent}
        assert "C1" in ids  # +267%
        assert "C2" in ids  # +137.5% also above 30% threshold
        assert "C4" not in ids  # stable

    def test_mean_drift_pct(self):
        book = EACDriftBook()
        book.assess("A", 4000.0, 4800.0)  # +20%
        book.assess("B", 4000.0, 3200.0)  # -20%
        assert book.mean_drift_pct == pytest.approx(0.0)

    def test_empty_book_mean_drift(self):
        book = EACDriftBook()
        assert book.mean_drift_pct == 0.0

    def test_drift_summary_keys(self):
        book = self._book_with_portfolio()
        s = book.drift_summary()
        assert s["customers_assessed"] == 4
        assert s["significant_increases"] == 2
        assert s["significant_decreases"] == 1
        assert s["reprice_candidates"] == 3  # C1, C2, C3

    def test_all_assessments_returns_list(self):
        book = self._book_with_portfolio()
        assert len(book.all_assessments) == 4

    def test_empty_book_drift_summary(self):
        book = EACDriftBook()
        s = book.drift_summary()
        assert s["customers_assessed"] == 0
        assert s["reprice_candidates"] == 0
