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


class TestBoardKPIs(unittest.TestCase):

    def _kpi(self, value, target, lower_is_better=False):
        from company.finance.board_kpis import KPIValue
        return KPIValue("metric", value, "%", target, lower_is_better=lower_is_better)

    def test_vs_target_pct(self):
        kpi = self._kpi(95.0, 100.0)
        self.assertAlmostEqual(kpi.vs_target_pct, -5.0)

    def test_status_green_within_5pct(self):
        from company.finance.board_kpis import KPIStatus
        kpi = self._kpi(97.0, 100.0)
        self.assertEqual(kpi.status, KPIStatus.GREEN)

    def test_status_amber_between_5_and_20pct(self):
        from company.finance.board_kpis import KPIStatus
        kpi = self._kpi(88.0, 100.0)
        self.assertEqual(kpi.status, KPIStatus.AMBER)

    def test_status_red_below_20pct(self):
        from company.finance.board_kpis import KPIStatus
        kpi = self._kpi(75.0, 100.0)
        self.assertEqual(kpi.status, KPIStatus.RED)

    def test_lower_is_better_inverts(self):
        from company.finance.board_kpis import KPIStatus
        kpi = self._kpi(5.0, 10.0, lower_is_better=True)
        self.assertEqual(kpi.status, KPIStatus.GREEN)

    def test_dashboard_counts(self):
        from company.finance.board_kpis import BoardKPIDashboard, KPIValue
        kpis = (
            KPIValue("a", 100.0, "%", 100.0),
            KPIValue("b", 88.0, "%", 100.0),
            KPIValue("c", 70.0, "%", 100.0),
        )
        dash = BoardKPIDashboard(2023, 1, kpis)
        self.assertEqual(dash.green_count, 1)
        self.assertEqual(dash.amber_count, 1)
        self.assertEqual(dash.red_count, 1)

    def test_overall_status_red_if_any_red(self):
        from company.finance.board_kpis import BoardKPIDashboard, KPIValue, KPIStatus
        kpis = (KPIValue("a", 100.0, "%", 100.0), KPIValue("b", 70.0, "%", 100.0))
        dash = BoardKPIDashboard(2023, 1, kpis)
        self.assertEqual(dash.overall_status, KPIStatus.RED)

    def test_overall_status_green_all_green(self):
        from company.finance.board_kpis import BoardKPIDashboard, KPIValue, KPIStatus
        kpis = (KPIValue("a", 100.0, "%", 100.0), KPIValue("b", 98.0, "%", 100.0))
        dash = BoardKPIDashboard(2023, 2, kpis)
        self.assertEqual(dash.overall_status, KPIStatus.GREEN)

    def test_get_kpi_by_name(self):
        from company.finance.board_kpis import BoardKPIDashboard, KPIValue
        kpis = (KPIValue("gross_margin", 12.5, "%", 10.0),)
        dash = BoardKPIDashboard(2023, 1, kpis)
        found = dash.get_kpi("gross_margin")
        self.assertIsNotNone(found)
        self.assertAlmostEqual(found.value, 12.5)

    def test_build_board_dashboard_creates_seven_kpis(self):
        from company.finance.board_kpis import build_board_dashboard
        dash = build_board_dashboard(
            year=2023, quarter=2,
            customer_count=18, customer_target=20,
            gross_margin_pct=12.0, gm_target_pct=10.0,
            ebitda_margin_pct=8.0, ebitda_target_pct=7.0,
            bad_debt_pct=1.5, bad_debt_target_pct=2.0,
            complaint_resolution_days=3.0, crt_target_days=5.0,
            csat_score=4.2, csat_target=4.0,
            gsop_compliance_pct=99.5, gsop_target_pct=100.0,
        )
        self.assertEqual(len(dash.kpis), 7)


class TestCashFlowForecast(unittest.TestCase):

    def _week(self, receipts=10000.0, wholesale=4000.0, network=2000.0,
               policy=1000.0, opex=2000.0, other=0.0):
        from company.finance.cash_flow_forecast import WeeklyCashFlow
        return WeeklyCashFlow(
            week_start=dt.date(2023, 1, 2),
            customer_receipts_gbp=receipts,
            wholesale_settlements_gbp=wholesale,
            network_charges_gbp=network,
            policy_levies_gbp=policy,
            operating_costs_gbp=opex,
            other_outflows_gbp=other,
        )

    def test_total_inflows(self):
        w = self._week(receipts=10000.0)
        self.assertAlmostEqual(w.total_inflows_gbp, 10000.0)

    def test_total_outflows(self):
        w = self._week(wholesale=4000.0, network=2000.0, policy=1000.0, opex=2000.0, other=500.0)
        self.assertAlmostEqual(w.total_outflows_gbp, 9500.0)

    def test_net_cash_gbp(self):
        w = self._week(receipts=10000.0, wholesale=4000.0, network=2000.0,
                        policy=1000.0, opex=2000.0)
        self.assertAlmostEqual(w.net_cash_gbp, 1000.0)

    def test_is_net_positive(self):
        from company.finance.cash_flow_forecast import WeeklyCashFlow
        positive = self._week(receipts=10000.0)
        negative = WeeklyCashFlow(dt.date(2023, 1, 2), 1000.0, 9000.0, 0.0, 0.0, 0.0)
        self.assertTrue(positive.is_net_positive)
        self.assertFalse(negative.is_net_positive)

    def test_closing_cash_gbp(self):
        from company.finance.cash_flow_forecast import CashFlowForecast
        w = self._week()  # net = 10000 - 9000 = 1000
        fcst = CashFlowForecast(dt.date(2023, 1, 1), 50000.0, (w,))
        self.assertAlmostEqual(fcst.closing_cash_gbp, 51000.0)

    def test_minimum_weekly_balance(self):
        from company.finance.cash_flow_forecast import CashFlowForecast, WeeklyCashFlow
        w_pos = self._week(receipts=10000.0)  # net +1000
        w_neg = WeeklyCashFlow(dt.date(2023, 1, 9), 5000.0, 4000.0, 2000.0, 1000.0, 2000.0)  # net -4000
        fcst = CashFlowForecast(dt.date(2023, 1, 1), 10000.0, (w_pos, w_neg))
        self.assertAlmostEqual(fcst.minimum_weekly_balance_gbp, 7000.0)

    def test_weeks_to_cash_concern_none_when_solvent(self):
        from company.finance.cash_flow_forecast import CashFlowForecast
        w = self._week()
        fcst = CashFlowForecast(dt.date(2023, 1, 1), 50000.0, (w,))
        self.assertIsNone(fcst.weeks_to_cash_concern)

    def test_weeks_to_cash_concern_returns_week_number(self):
        from company.finance.cash_flow_forecast import CashFlowForecast, WeeklyCashFlow
        w = WeeklyCashFlow(dt.date(2023, 1, 2), 1000.0, 2000.0, 1000.0, 0.0, 0.0)
        fcst = CashFlowForecast(dt.date(2023, 1, 1), 1000.0, (w,))
        self.assertEqual(fcst.weeks_to_cash_concern, 1)

    def test_is_solvent_throughout(self):
        from company.finance.cash_flow_forecast import CashFlowForecast
        w = self._week()
        fcst = CashFlowForecast(dt.date(2023, 1, 1), 50000.0, (w,))
        self.assertTrue(fcst.is_solvent_throughout)

    def test_build_forecast_creates_correct_weeks(self):
        from company.finance.cash_flow_forecast import build_cash_flow_forecast
        fcst = build_cash_flow_forecast(
            dt.date(2023, 1, 1), 50000.0,
            10000.0, 4000.0, 2000.0, 1000.0, 2000.0, weeks=4,
        )
        self.assertEqual(len(fcst.weeks), 4)


if __name__ == "__main__":
    unittest.main()
