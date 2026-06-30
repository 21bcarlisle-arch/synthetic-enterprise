"""Phase IS — Coverage Depth Sprint XVI: clv_calculator, cos_process, nps_tracker."""

import datetime as dt
import unittest

from company.crm.clv_calculator import (
    ClvResult,
    compute_clv,
    clv_to_cac_ratio,
    portfolio_clv_summary,
)
from company.crm.cos_process import (
    CoSProcess,
    CoSRegister,
    CoSStage,
    ObjectionReason,
)
from company.crm.nps_tracker import NPSTracker, classify_nps


# ---------------------------------------------------------------------------
# clv_calculator — 10 tests
# ---------------------------------------------------------------------------

class TestComputeClv(unittest.TestCase):
    def test_basic_positive_margin(self):
        r = compute_clv("C1", annual_net_margin_gbp=150.0)
        self.assertIsInstance(r, ClvResult)
        self.assertGreater(r.clv_gbp, 0)
        self.assertEqual(r.customer_id, "C1")

    def test_net_negative_margin_tier(self):
        r = compute_clv("C2", annual_net_margin_gbp=-50.0)
        self.assertEqual(r.margin_tier, "NET_NEGATIVE")
        self.assertLess(r.clv_gbp, 0)

    def test_low_margin_tier(self):
        r = compute_clv("C3", annual_net_margin_gbp=30.0)
        self.assertEqual(r.margin_tier, "LOW")

    def test_standard_margin_tier(self):
        r = compute_clv("C4", annual_net_margin_gbp=100.0)
        self.assertEqual(r.margin_tier, "STANDARD")

    def test_premium_margin_tier(self):
        r = compute_clv("C5", annual_net_margin_gbp=250.0)
        self.assertEqual(r.margin_tier, "PREMIUM")

    def test_explicit_tenure_overrides_churn(self):
        r_default = compute_clv("C6", annual_net_margin_gbp=100.0)
        r_explicit = compute_clv("C6", annual_net_margin_gbp=100.0, tenure_years=2.0)
        self.assertNotEqual(r_default.expected_tenure_years, r_explicit.expected_tenure_years)
        self.assertAlmostEqual(r_explicit.expected_tenure_years, 2.0, places=1)

    def test_clv_dcf_formula(self):
        r = compute_clv("C7", annual_net_margin_gbp=100.0, churn_rate=0.18, discount_rate=0.10)
        expected_tenure = round(1 / 0.18, 2)
        self.assertAlmostEqual(r.expected_tenure_years, expected_tenure, places=1)

    def test_cac_ratio_healthy(self):
        result = clv_to_cac_ratio(clv_gbp=900.0, cac_gbp=200.0)
        self.assertEqual(result["verdict"], "HEALTHY")
        self.assertAlmostEqual(result["ratio"], 4.5, places=1)

    def test_cac_ratio_loss_making(self):
        result = clv_to_cac_ratio(clv_gbp=50.0, cac_gbp=200.0)
        self.assertEqual(result["verdict"], "LOSS_MAKING")
        self.assertLess(result["ratio"], 1.0)

    def test_cac_ratio_zero_cac_uncapped(self):
        result = clv_to_cac_ratio(clv_gbp=500.0, cac_gbp=0.0)
        self.assertEqual(result["verdict"], "UNCAPPED")
        self.assertEqual(result["ratio"], float("inf"))


class TestPortfolioClvSummary(unittest.TestCase):
    def test_summary_counts_and_totals(self):
        results = [
            compute_clv("A", 200.0),
            compute_clv("B", 100.0),
            compute_clv("C", -20.0),
        ]
        s = portfolio_clv_summary(results)
        self.assertEqual(s["count"], 3)
        self.assertAlmostEqual(s["total_clv_gbp"], sum(r.clv_gbp for r in results), places=1)
        self.assertIn("tiers", s)

    def test_empty_portfolio(self):
        s = portfolio_clv_summary([])
        self.assertEqual(s["count"], 0)
        self.assertEqual(s["total_clv_gbp"], 0.0)


# ---------------------------------------------------------------------------
# cos_process — 10 tests
# ---------------------------------------------------------------------------

class TestCoSProcess(unittest.TestCase):
    def _make(self):
        return CoSProcess("ACC-1", "2024-01-10", gaining_supplier="SupplierA",
                          losing_supplier="SupplierB")

    def test_initial_stage_is_switch_requested(self):
        p = self._make()
        self.assertEqual(p.current_stage, CoSStage.SWITCH_REQUESTED)
        self.assertFalse(p.is_complete)

    def test_clear_objection_window(self):
        p = self._make()
        p.clear_objection_window("2024-01-24")
        self.assertEqual(p.current_stage, CoSStage.OBJECTION_CLEARED)

    def test_object_to_switch(self):
        p = self._make()
        p.object_to_switch("2024-01-20", ObjectionReason.DEBT)
        self.assertTrue(p.is_objected)
        self.assertEqual(p.current_stage, CoSStage.OBJECTED)

    def test_objection_reason_stored_on_event(self):
        p = self._make()
        ev = p.object_to_switch("2024-01-20", ObjectionReason.CONTRACT_IN_FORCE)
        self.assertEqual(ev.objection_reason, ObjectionReason.CONTRACT_IN_FORCE)

    def test_full_happy_path_completes(self):
        p = self._make()
        p.clear_objection_window("2024-01-24")
        p.request_final_read("2024-02-01")
        p.receive_final_read("2024-02-05", kwh=12340.0)
        p.complete("2024-02-10")
        self.assertTrue(p.is_complete)
        self.assertEqual(p.current_stage, CoSStage.SWITCH_COMPLETE)

    def test_receive_final_read_stores_kwh(self):
        p = self._make()
        ev = p.receive_final_read("2024-02-05", kwh=9876.5)
        self.assertAlmostEqual(ev.final_read_kwh, 9876.5)

    def test_cancel_marks_cancelled(self):
        p = self._make()
        p.cancel("2024-01-15")
        self.assertTrue(p.is_cancelled)
        self.assertFalse(p.is_complete)


class TestCoSRegister(unittest.TestCase):
    def test_open_switch_returns_process(self):
        reg = CoSRegister()
        p = reg.open_switch("ACC-2", "2024-01-10", "New", "Old")
        self.assertIsInstance(p, CoSProcess)
        self.assertEqual(p.account_id, "ACC-2")

    def test_active_for_account_excludes_cancelled(self):
        reg = CoSRegister()
        p1 = reg.open_switch("ACC-3", "2024-01-10", "New", "Old")
        p1.cancel("2024-01-11")
        p2 = reg.open_switch("ACC-3", "2024-01-12", "New", "Old")
        active = reg.active_for_account("ACC-3")
        self.assertEqual(len(active), 1)
        self.assertIs(active[0], p2)

    def test_cos_summary_counts(self):
        reg = CoSRegister()
        p1 = reg.open_switch("ACC-4", "2024-01-01", "A", "B")
        p1.clear_objection_window("2024-01-15")
        p1.complete("2024-02-01")
        p2 = reg.open_switch("ACC-5", "2024-01-01", "A", "B")
        p2.object_to_switch("2024-01-10", ObjectionReason.COOLING_OFF_PERIOD)
        s = reg.cos_summary()
        self.assertEqual(s["completed"], 1)
        self.assertEqual(s["objected"], 1)
        self.assertEqual(s["total_switches"], 2)


# ---------------------------------------------------------------------------
# nps_tracker — 10 tests
# ---------------------------------------------------------------------------

class TestNPSClassify(unittest.TestCase):
    def test_promoter_at_9(self):
        self.assertEqual(classify_nps(9), "promoter")

    def test_promoter_at_10(self):
        self.assertEqual(classify_nps(10), "promoter")

    def test_passive_at_7(self):
        self.assertEqual(classify_nps(7), "passive")

    def test_detractor_at_6(self):
        self.assertEqual(classify_nps(6), "detractor")


class TestNPSTracker(unittest.TestCase):
    def _date(self, s):
        return dt.date.fromisoformat(s)

    def test_record_creates_response(self):
        tracker = NPSTracker()
        r = tracker.record("C1", 9, self._date("2024-03-01"), "domestic")
        self.assertEqual(r.score, 9)
        self.assertEqual(r.category, "promoter")

    def test_invalid_score_raises(self):
        tracker = NPSTracker()
        with self.assertRaises(ValueError):
            tracker.record("C1", 11, self._date("2024-03-01"), "domestic")

    def test_nps_in_period_calculation(self):
        tracker = NPSTracker()
        for score, seg in [(9, "d"), (10, "d"), (2, "d"), (8, "d")]:
            tracker.record("C", score, self._date("2024-06-15"), seg)
        nps = tracker.nps_in_period(self._date("2024-06-01"), self._date("2024-06-30"))
        self.assertAlmostEqual(nps, 25.0, places=1)

    def test_nps_in_period_no_responses_returns_none(self):
        tracker = NPSTracker()
        result = tracker.nps_in_period(self._date("2024-01-01"), self._date("2024-01-31"))
        self.assertIsNone(result)

    def test_nps_in_period_segment_filter(self):
        tracker = NPSTracker()
        tracker.record("C1", 10, self._date("2024-06-10"), "domestic")
        tracker.record("C2", 0, self._date("2024-06-10"), "sme")
        nps = tracker.nps_in_period(self._date("2024-06-01"), self._date("2024-06-30"),
                                    segment="domestic")
        self.assertAlmostEqual(nps, 100.0, places=1)

    def test_annual_summary_structure(self):
        tracker = NPSTracker()
        tracker.record("C1", 9, self._date("2024-04-01"), "domestic")
        tracker.record("C2", 3, self._date("2024-05-01"), "domestic")
        s = tracker.annual_summary(2024)
        self.assertEqual(s["year"], 2024)
        self.assertEqual(s["responses"], 2)
        self.assertIsNotNone(s["nps"])
        self.assertIn("by_segment", s)

    def test_by_segment_groups_correctly(self):
        tracker = NPSTracker()
        tracker.record("C1", 10, self._date("2024-01-10"), "domestic")
        tracker.record("C2", 10, self._date("2024-01-10"), "sme")
        tracker.record("C3", 0, self._date("2024-01-10"), "sme")
        seg = tracker.by_segment(2024)
        self.assertEqual(seg["domestic"], 100.0)
        self.assertAlmostEqual(seg["sme"], 0.0, places=1)


if __name__ == "__main__":
    unittest.main()
