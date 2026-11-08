"""Phase JB coverage expansion: bm_unit_log, board_kpis, cash_flow_forecast."""
import datetime as dt
import unittest


class TestBMUnitLog(unittest.TestCase):

    def _log(self):
        from company.market.bm_unit_log import BMUnitLog, BMActionType, BMDispatchStatus
        return BMUnitLog("BMU-001", 10.0), BMActionType, BMDispatchStatus

    def _offer(self, log, action_type, offered_mw=5.0, price=100.0, date=None, period=1):
        if date is None:
            date = dt.date(2023, 1, 15)
        ts = dt.datetime(2023, 1, 15, 9, 0)
        return log.submit_offer(date, period, action_type, offered_mw, price, ts)

    def test_submit_offer_stores_bmu_id(self):
        log, A, _ = self._log()
        offer = self._offer(log, A.OFFER)
        self.assertEqual(offer.bmu_id, "BMU-001")

    def test_offered_mwh_half_period(self):
        log, A, _ = self._log()
        offer = self._offer(log, A.OFFER, offered_mw=10.0)
        self.assertAlmostEqual(offer.offered_mwh, 5.0)

    def test_is_expensive_true(self):
        log, A, _ = self._log()
        offer = self._offer(log, A.OFFER, price=600.0)
        self.assertTrue(offer.is_expensive)

    def test_is_expensive_false(self):
        log, A, _ = self._log()
        offer = self._offer(log, A.OFFER, price=499.0)
        self.assertFalse(offer.is_expensive)

    def test_record_dispatch_status_dispatched(self):
        log, A, S = self._log()
        offer = self._offer(log, A.OFFER, offered_mw=10.0)
        d = log.record_dispatch(offer, 10.0, dt.datetime(2023, 1, 15, 9, 30))
        self.assertEqual(d.status, S.DISPATCHED)

    def test_record_dispatch_status_part_dispatched(self):
        log, A, S = self._log()
        offer = self._offer(log, A.OFFER, offered_mw=10.0)
        d = log.record_dispatch(offer, 5.0, dt.datetime(2023, 1, 15, 9, 30))
        self.assertEqual(d.status, S.PART_DISPATCHED)

    def test_dispatch_revenue_gbp(self):
        log, A, _ = self._log()
        offer = self._offer(log, A.OFFER, offered_mw=10.0, price=200.0)
        d = log.record_dispatch(offer, 10.0, dt.datetime(2023, 1, 15, 9, 30))
        self.assertAlmostEqual(d.revenue_gbp, 1000.0)

    def test_utilisation_pct(self):
        log, A, _ = self._log()
        offer = self._offer(log, A.OFFER, offered_mw=10.0)
        d = log.record_dispatch(offer, 7.5, dt.datetime(2023, 1, 15, 9, 30))
        self.assertAlmostEqual(d.utilisation_pct, 75.0)

    def test_total_revenue_gbp_filters_by_year(self):
        log, A, _ = self._log()
        o1 = self._offer(log, A.OFFER, offered_mw=10.0, price=100.0, date=dt.date(2023, 1, 1))
        o2 = self._offer(log, A.OFFER, offered_mw=10.0, price=100.0, date=dt.date(2024, 1, 1))
        log.record_dispatch(o1, 10.0, dt.datetime(2023, 1, 1, 9, 0))
        log.record_dispatch(o2, 10.0, dt.datetime(2024, 1, 1, 9, 0))
        self.assertAlmostEqual(log.total_revenue_gbp(2023), 500.0)

    def test_avg_dispatch_price_none_when_no_dispatches(self):
        log, A, _ = self._log()
        self._offer(log, A.OFFER, price=150.0)
        self.assertIsNone(log.avg_dispatch_price(2023))


if __name__ == "__main__":
    unittest.main()
