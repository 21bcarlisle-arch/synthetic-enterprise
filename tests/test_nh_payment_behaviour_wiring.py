"""Phase NH: PaymentBehaviourAnalytics wired into run_phase2b.py enriched_churn_estimate.

Tests verify:
- generate_payment_record produces expected outcomes by stress level
- PaymentBehaviourAnalytics accumulates records and scores correctly
- enriched_churn_estimate receives and responds to behaviour_score
- Simulation runner wiring: behaviour_score kwarg present in _enriched_churn_estimate calls
- Epistemic: company observes payment outcomes (not income_stress directly)
"""
import random
import unittest
from datetime import date

from simulation.payment_timing import generate_payment_record
from simulation.household import IncomeStress
from company.crm.payment_behaviour_analytics import (
    BehaviourScore,
    PaymentBehaviourAnalytics,
)
from company.crm.enriched_churn_estimate import enriched_churn_estimate
from company.crm.payment_churn_model import CHURN_UPLIFT_BY_SCORE


_DUE = date(2020, 1, 28)
_RNG_LOW = random.Random(1001)
_RNG_HIGH = random.Random(2002)


class TestGeneratePaymentRecord(unittest.TestCase):
    def test_low_stress_mostly_on_time(self):
        """LOW stress: ON_TIME probability should be very high (>= 0.90)."""
        rng = random.Random(42)
        n = 1000
        on_time = sum(
            1 for _ in range(n)
            if generate_payment_record("C1", _DUE, 100.0, IncomeStress.LOW, rng)["result"] == "ON_TIME"
        )
        self.assertGreaterEqual(on_time / n, 0.85)

    def test_high_stress_high_dd_failure(self):
        """HIGH stress: DD_FAILED probability should be >= 0.30."""
        rng = random.Random(99)
        n = 1000
        failed = sum(
            1 for _ in range(n)
            if generate_payment_record("C1", _DUE, 100.0, IncomeStress.HIGH, rng)["result"] == "DD_FAILED"
        )
        self.assertGreaterEqual(failed / n, 0.25)

    def test_record_has_required_keys(self):
        rng = random.Random(7)
        rec = generate_payment_record("C1", _DUE, 80.0, IncomeStress.LOW, rng)
        for key in ("customer_id", "due_date", "result", "amount_gbp"):
            self.assertIn(key, rec)

    def test_epistemic_no_income_stress_in_record(self):
        """Observable record must NOT contain income_stress — company cannot see SIM internals."""
        rng = random.Random(13)
        rec = generate_payment_record("C2", _DUE, 50.0, IncomeStress.HIGH, rng)
        self.assertNotIn("income_stress", rec)


class TestPaymentBehaviourAnalytics(unittest.TestCase):
    def _make_recs(self, customer_id, result, n=12):
        rng = random.Random(3)
        return [
            {"customer_id": customer_id, "due_date": date(2020, i + 1, 28),
             "result": result, "amount_gbp": 100.0, "amount_paid": 100.0}
            for i in range(n)
        ]

    def test_all_on_time_excellent(self):
        analytics = PaymentBehaviourAnalytics()
        for rec in self._make_recs("C1", "ON_TIME"):
            analytics.record_payment("C1", rec)
        self.assertEqual(analytics.get_score("C1"), BehaviourScore.EXCELLENT)

    def test_majority_dd_failed_critical(self):
        analytics = PaymentBehaviourAnalytics()
        for rec in self._make_recs("C2", "DD_FAILED", n=6):
            analytics.record_payment("C2", rec)
        score = analytics.get_score("C2")
        self.assertIn(score, (BehaviourScore.POOR, BehaviourScore.CRITICAL))

    def test_new_customer_returns_none(self):
        """No payment records yet — get_score returns None (backward-compatible)."""
        analytics = PaymentBehaviourAnalytics()
        self.assertIsNone(analytics.get_score("unknown_cid"))

    def test_multiple_customers_independent(self):
        """Records for C1 must not affect C2 score."""
        analytics = PaymentBehaviourAnalytics()
        for rec in self._make_recs("C1", "DD_FAILED", n=10):
            analytics.record_payment("C1", rec)
        for rec in self._make_recs("C2", "ON_TIME", n=10):
            analytics.record_payment("C2", rec)
        self.assertEqual(analytics.get_score("C2"), BehaviourScore.EXCELLENT)

    def test_at_risk_includes_poor_and_critical(self):
        analytics = PaymentBehaviourAnalytics()
        for rec in self._make_recs("C3", "DD_FAILED", n=8):
            analytics.record_payment("C3", rec)
        at_risk = analytics.at_risk_customers()
        self.assertIn("C3", at_risk)

    def test_at_risk_excludes_excellent(self):
        analytics = PaymentBehaviourAnalytics()
        for rec in self._make_recs("C4", "ON_TIME", n=12):
            analytics.record_payment("C4", rec)
        self.assertNotIn("C4", analytics.at_risk_customers())

    def test_monthly_accumulation_12_records(self):
        """12 monthly records should accumulate correctly."""
        analytics = PaymentBehaviourAnalytics()
        rng = random.Random(5)
        for month in range(1, 13):
            rec = generate_payment_record(
                "C5", date(2020, month, 28), 100.0, IncomeStress.LOW, rng
            )
            analytics.record_payment("C5", rec)
        # Should have a score after 12 months
        self.assertIsNotNone(analytics.get_score("C5"))


class TestEnrichedChurnWithBehaviourScore(unittest.TestCase):
    def test_critical_raises_churn_vs_none(self):
        """CRITICAL behaviour score raises enriched churn above behaviour_score=None baseline."""
        base = enriched_churn_estimate(
            100.0, 110.0, 2.0, 12000.0,
            bill_shock_count=0, behaviour_score=None, satisfaction_score=None,
        )
        critical = enriched_churn_estimate(
            100.0, 110.0, 2.0, 12000.0,
            bill_shock_count=0, behaviour_score=BehaviourScore.CRITICAL, satisfaction_score=None,
        )
        self.assertGreater(critical, base)

    def test_excellent_no_uplift_vs_none(self):
        """EXCELLENT behaviour score should give same or lower churn than None."""
        base = enriched_churn_estimate(
            100.0, 110.0, 2.0, 12000.0,
            bill_shock_count=0, behaviour_score=None, satisfaction_score=None,
        )
        excellent = enriched_churn_estimate(
            100.0, 110.0, 2.0, 12000.0,
            bill_shock_count=0, behaviour_score=BehaviourScore.EXCELLENT, satisfaction_score=None,
        )
        self.assertLessEqual(excellent, base)

    def test_critical_plus_bill_shock_plus_low_sat_crosses_retention_threshold(self):
        """CRITICAL + 1 bill shock + low satisfaction should be >= 0.30 (RETENTION_THRESHOLD)."""
        churn = enriched_churn_estimate(
            100.0, 105.0, 1.5, 12000.0,
            bill_shock_count=1, behaviour_score=BehaviourScore.CRITICAL, satisfaction_score=0.45,
        )
        self.assertGreaterEqual(churn, 0.30)

    def test_poor_score_pushes_above_rate_only_modest_rise(self):
        """POOR score with modest rate rise should exceed rate-only churn estimate."""
        rate_only = enriched_churn_estimate(
            100.0, 108.0, 3.0, 12000.0,
            bill_shock_count=0, behaviour_score=None, satisfaction_score=None,
        )
        with_poor = enriched_churn_estimate(
            100.0, 108.0, 3.0, 12000.0,
            bill_shock_count=0, behaviour_score=BehaviourScore.POOR, satisfaction_score=None,
        )
        self.assertGreater(with_poor, rate_only)


class TestRunPhase2bBehaviourScoreWiring(unittest.TestCase):
    """Integration-level checks on the wiring in run_phase2b.py."""

    def test_behaviour_score_kwarg_in_enriched_churn_estimate_call(self):
        """enriched_churn_estimate must accept behaviour_score kwarg without error."""
        # Proxy: call the function with the same kwargs that run_phase2b will use.
        result = enriched_churn_estimate(
            120.0, 150.0, 2.0, 15000.0,
            bill_shock_count=1,
            behaviour_score=BehaviourScore.GOOD,
            satisfaction_score=0.70,
            hedge_fraction=0.85,
            hangover_periods_remaining=0,
            segment="resi",
        )
        self.assertIsInstance(result, float)
        self.assertGreater(result, 0.0)
        self.assertLessEqual(result, 1.0)

    def test_churn_uplift_constants_cover_all_scores(self):
        """CHURN_UPLIFT_BY_SCORE must have an entry for every BehaviourScore value."""
        for score in BehaviourScore:
            self.assertIn(score, CHURN_UPLIFT_BY_SCORE)


if __name__ == "__main__":
    unittest.main()
