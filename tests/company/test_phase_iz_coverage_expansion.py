"""Phase IZ coverage expansion: switch_analytics, risk_appetite, credit_rating_book."""
import datetime as dt
import unittest


class TestSwitchAnalytics(unittest.TestCase):

    def _make(self):
        from company.crm.switch_analytics import SwitchAnalytics, SwitchDirection, SwitchStatus
        sa = SwitchAnalytics(our_supplier_id="ACME")
        return sa, SwitchDirection, SwitchStatus

    def test_sequential_ids(self):
        sa, D, _ = self._make()
        e1 = sa.record("M1", "C1", D.GAIN, "OLD", "ACME", dt.date(2023, 1, 10))
        e2 = sa.record("M2", "C2", D.LOSS, "ACME", "NEW", dt.date(2023, 2, 1))
        self.assertEqual(e1.event_id, "SW-00001")
        self.assertEqual(e2.event_id, "SW-00002")

    def test_is_completed_false_on_initiation(self):
        sa, D, _ = self._make()
        ev = sa.record("M1", "C1", D.GAIN, "OLD", "ACME", dt.date(2023, 1, 10))
        self.assertFalse(ev.is_completed)

    def test_complete_marks_completed(self):
        sa, D, S = self._make()
        ev = sa.record("M1", "C1", D.GAIN, "OLD", "ACME", dt.date(2023, 1, 10))
        done = sa.complete(ev.event_id, dt.date(2023, 1, 15))
        self.assertEqual(done.status, S.COMPLETED)
        self.assertTrue(done.is_completed)

    def test_days_to_complete(self):
        sa, D, _ = self._make()
        ev = sa.record("M1", "C1", D.GAIN, "OLD", "ACME", dt.date(2023, 1, 10))
        done = sa.complete(ev.event_id, dt.date(2023, 1, 15))
        self.assertEqual(done.days_to_complete, 5)

    def test_days_to_complete_none_when_not_completed(self):
        sa, D, _ = self._make()
        ev = sa.record("M1", "C1", D.GAIN, "OLD", "ACME", dt.date(2023, 1, 10))
        self.assertIsNone(ev.days_to_complete)

    def test_gains_in_year(self):
        sa, D, _ = self._make()
        sa.record("M1", "C1", D.GAIN, "OLD", "ACME", dt.date(2023, 3, 1))
        sa.record("M2", "C2", D.LOSS, "ACME", "NEW", dt.date(2023, 4, 1))
        sa.record("M3", "C3", D.GAIN, "OLD", "ACME", dt.date(2024, 1, 1))
        self.assertEqual(len(sa.gains_in_year(2023)), 1)

    def test_losses_in_year(self):
        sa, D, _ = self._make()
        sa.record("M1", "C1", D.LOSS, "ACME", "NEW", dt.date(2023, 1, 1))
        sa.record("M2", "C2", D.LOSS, "ACME", "NEW", dt.date(2023, 6, 1))
        self.assertEqual(len(sa.losses_in_year(2023)), 2)

    def test_mark_erroneous(self):
        sa, D, S = self._make()
        ev = sa.record("M1", "C1", D.GAIN, "OLD", "ACME", dt.date(2023, 1, 1))
        et = sa.mark_erroneous(ev.event_id)
        self.assertTrue(et.erroneous_transfer)
        self.assertEqual(et.status, S.ERRONEOUS)

    def test_erroneous_transfers_in_year(self):
        sa, D, _ = self._make()
        ev = sa.record("M1", "C1", D.GAIN, "OLD", "ACME", dt.date(2023, 1, 1))
        sa.mark_erroneous(ev.event_id)
        sa.record("M2", "C2", D.GAIN, "OLD", "ACME", dt.date(2023, 2, 1))
        self.assertEqual(len(sa.erroneous_transfers_in_year(2023)), 1)

    def test_avg_days_to_complete_and_net_change(self):
        sa, D, _ = self._make()
        e1 = sa.record("M1", "C1", D.GAIN, "OLD", "ACME", dt.date(2023, 1, 1))
        e2 = sa.record("M2", "C2", D.GAIN, "OLD", "ACME", dt.date(2023, 2, 1))
        sa.record("M3", "C3", D.LOSS, "ACME", "NEW", dt.date(2023, 3, 1))
        sa.complete(e1.event_id, dt.date(2023, 1, 6))
        sa.complete(e2.event_id, dt.date(2023, 2, 11))
        self.assertEqual(sa.avg_days_to_complete(2023), 7.5)
        self.assertEqual(sa.net_customer_change(2023), 1)


class TestRiskAppetite(unittest.TestCase):

    def _raf(self):
        from company.risk.risk_appetite import RiskAppetiteFramework, RiskCategory, RiskRAG
        raf = RiskAppetiteFramework(approved_date=dt.date(2023, 1, 1))
        return raf, RiskCategory, RiskRAG

    def test_warning_value(self):
        raf, C, _ = self._raf()
        lim = raf.add_limit("L1", C.MARKET, "test", 100.0, "MWh", warning_threshold_pct=80.0)
        self.assertAlmostEqual(lim.warning_value, 80.0)

    def test_utilisation_pct(self):
        raf, C, _ = self._raf()
        raf.add_limit("L1", C.MARKET, "test", 200.0, "MWh")
        m = raf.record_measurement("L1", 150.0, dt.date(2023, 6, 1))
        self.assertAlmostEqual(m.utilisation_pct, 75.0)

    def test_rag_within_appetite(self):
        raf, C, R = self._raf()
        raf.add_limit("L1", C.MARKET, "test", 100.0, "MWh", warning_threshold_pct=80.0)
        m = raf.record_measurement("L1", 50.0, dt.date(2023, 6, 1))
        self.assertEqual(m.rag, R.WITHIN_APPETITE)
        self.assertFalse(m.is_breach)

    def test_rag_approaching_limit(self):
        raf, C, R = self._raf()
        raf.add_limit("L1", C.MARKET, "test", 100.0, "MWh", warning_threshold_pct=80.0)
        m = raf.record_measurement("L1", 85.0, dt.date(2023, 6, 1))
        self.assertEqual(m.rag, R.APPROACHING_LIMIT)
        self.assertFalse(m.is_breach)

    def test_rag_limit_breach(self):
        raf, C, R = self._raf()
        raf.add_limit("L1", C.MARKET, "test", 100.0, "MWh")
        m = raf.record_measurement("L1", 110.0, dt.date(2023, 6, 1))
        self.assertEqual(m.rag, R.LIMIT_BREACH)
        self.assertTrue(m.is_breach)

    def test_latest_measurement_returns_most_recent(self):
        raf, C, _ = self._raf()
        raf.add_limit("L1", C.CREDIT, "credit test", 500.0, "GBP")
        raf.record_measurement("L1", 100.0, dt.date(2023, 1, 1))
        raf.record_measurement("L1", 200.0, dt.date(2023, 6, 1))
        latest = raf.latest_measurement("L1")
        self.assertEqual(latest.measured_value, 200.0)

    def test_latest_measurement_none_when_no_measurements(self):
        raf, C, _ = self._raf()
        raf.add_limit("L1", C.CREDIT, "credit test", 500.0, "GBP")
        self.assertIsNone(raf.latest_measurement("L1"))

    def test_active_breaches(self):
        raf, C, _ = self._raf()
        raf.add_limit("L1", C.MARKET, "market", 100.0, "MWh")
        raf.add_limit("L2", C.CREDIT, "credit", 1000.0, "GBP")
        raf.record_measurement("L1", 120.0, dt.date(2023, 6, 1))
        raf.record_measurement("L2", 500.0, dt.date(2023, 6, 1))
        breaches = raf.active_breaches()
        self.assertEqual(len(breaches), 1)
        self.assertEqual(breaches[0].limit_id, "L1")

    def test_risk_dashboard_structure(self):
        raf, C, _ = self._raf()
        raf.add_limit("L1", C.MARKET, "market", 100.0, "MWh")
        raf.record_measurement("L1", 50.0, dt.date(2023, 6, 1))
        dash = raf.risk_dashboard(dt.date(2023, 12, 31))
        self.assertIn("total_limits", dash)
        self.assertIn("measured_limits", dash)
        self.assertIn("breaches", dash)
        self.assertIn("items", dash)
        self.assertEqual(dash["total_limits"], 1)
        self.assertEqual(len(dash["items"]), 1)

    def test_risk_dashboard_excludes_future_measurements(self):
        raf, C, _ = self._raf()
        raf.add_limit("L1", C.MARKET, "market", 100.0, "MWh")
        raf.record_measurement("L1", 110.0, dt.date(2024, 1, 1))
        dash = raf.risk_dashboard(dt.date(2023, 12, 31))
        self.assertEqual(dash["measured_limits"], 0)
        self.assertEqual(dash["breaches"], 0)


class TestCreditRatingBook(unittest.TestCase):

    def _book(self):
        from company.trading.credit_rating_book import CreditRating, CreditRatingBook
        book = CreditRatingBook()
        return book, CreditRating

    def _reg(self, book, cid, rating, limit, rated_by="Moodys"):
        return book.register(cid, cid + " Ltd", rating, rated_by, dt.date(2023, 1, 1), limit)

    def test_is_investment_grade_bbb_and_above(self):
        from company.trading.credit_rating_book import CreditRating, is_investment_grade
        self.assertTrue(is_investment_grade(CreditRating.BBB))
        self.assertTrue(is_investment_grade(CreditRating.A))
        self.assertTrue(is_investment_grade(CreditRating.AA))
        self.assertTrue(is_investment_grade(CreditRating.AAA))

    def test_is_investment_grade_bb_and_below(self):
        from company.trading.credit_rating_book import CreditRating, is_investment_grade
        self.assertFalse(is_investment_grade(CreditRating.BB))
        self.assertFalse(is_investment_grade(CreditRating.B))
        self.assertFalse(is_investment_grade(CreditRating.CCC))
        self.assertFalse(is_investment_grade(CreditRating.D))

    def test_register_and_get(self):
        book, R = self._book()
        p = self._reg(book, "CPY1", R.A, 1_000_000)
        got = book.get("CPY1")
        self.assertIs(p, got)
        self.assertEqual(p.counterparty_id, "CPY1")

    def test_profile_is_investment_grade_flag(self):
        book, R = self._book()
        ig = self._reg(book, "IG1", R.A, 500_000)
        sub = self._reg(book, "SG1", R.BB, 100_000)
        self.assertTrue(ig.is_investment_grade)
        self.assertFalse(sub.is_investment_grade)

    def test_profile_pd_pct(self):
        book, R = self._book()
        p = self._reg(book, "D1", R.D, 10_000)
        self.assertAlmostEqual(p.pd_pct, 100.0)

    def test_record_exposure_and_total(self):
        book, R = self._book()
        self._reg(book, "CPY1", R.A, 1_000_000)
        book.record_exposure("CPY1", dt.date(2023, 3, 1), 200_000, "FORWARD")
        book.record_exposure("CPY1", dt.date(2023, 4, 1), 150_000, "OPTION")
        self.assertAlmostEqual(book.total_exposure_gbp("CPY1"), 350_000.0)

    def test_is_within_limit_true(self):
        book, R = self._book()
        self._reg(book, "CPY1", R.A, 500_000)
        book.record_exposure("CPY1", dt.date(2023, 1, 1), 200_000, "FORWARD")
        self.assertTrue(book.is_within_limit("CPY1", 250_000))

    def test_is_within_limit_false(self):
        book, R = self._book()
        self._reg(book, "CPY1", R.A, 500_000)
        book.record_exposure("CPY1", dt.date(2023, 1, 1), 400_000, "FORWARD")
        self.assertFalse(book.is_within_limit("CPY1", 200_000))

    def test_sub_investment_grade_counterparties(self):
        book, R = self._book()
        self._reg(book, "IG", R.BBB, 1_000_000)
        self._reg(book, "SG", R.BB, 50_000)
        subs = book.sub_investment_grade_counterparties()
        self.assertEqual(len(subs), 1)
        self.assertEqual(subs[0].counterparty_id, "SG")

    def test_credit_summary(self):
        book, R = self._book()
        self._reg(book, "IG1", R.A, 1_000_000)
        self._reg(book, "SG1", R.B, 100_000)
        book.record_exposure("IG1", dt.date(2023, 1, 1), 300_000, "FWD")
        s = book.credit_summary()
        self.assertEqual(s["total_counterparties"], 2)
        self.assertEqual(s["investment_grade"], 1)
        self.assertEqual(s["sub_investment_grade"], 1)
        self.assertAlmostEqual(s["total_exposure_gbp"], 300_000.0)


if __name__ == "__main__":
    unittest.main()
