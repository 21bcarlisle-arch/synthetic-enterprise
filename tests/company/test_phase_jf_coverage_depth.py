"""Phase JF coverage depth: economy7, payment_behaviour, renewal_engine."""
import datetime as dt
import unittest


class TestEconomy7Rates(unittest.TestCase):

    def test_day_rate_2022_crisis_peak(self):
        from company.billing.economy7 import e7_unit_rate_ppm, TariffRegister
        self.assertAlmostEqual(e7_unit_rate_ppm(2022, TariffRegister.DAY), 34.0)

    def test_night_rate_2022(self):
        from company.billing.economy7 import e7_unit_rate_ppm, TariffRegister
        self.assertAlmostEqual(e7_unit_rate_ppm(2022, TariffRegister.NIGHT), 19.0)

    def test_day_rate_2016(self):
        from company.billing.economy7 import e7_unit_rate_ppm, TariffRegister
        self.assertAlmostEqual(e7_unit_rate_ppm(2016, TariffRegister.DAY), 12.0)

    def test_night_rate_2025(self):
        from company.billing.economy7 import e7_unit_rate_ppm, TariffRegister
        self.assertAlmostEqual(e7_unit_rate_ppm(2025, TariffRegister.NIGHT), 10.0)

    def test_unknown_year_fallback_day(self):
        from company.billing.economy7 import e7_unit_rate_ppm, TariffRegister
        self.assertAlmostEqual(e7_unit_rate_ppm(1999, TariffRegister.DAY), 14.5)

    def test_unknown_year_fallback_night(self):
        from company.billing.economy7 import e7_unit_rate_ppm, TariffRegister
        self.assertAlmostEqual(e7_unit_rate_ppm(1999, TariffRegister.NIGHT), 8.0)

    def test_night_cheaper_than_day(self):
        from company.billing.economy7 import e7_unit_rate_ppm, TariffRegister
        for year in [2016, 2020, 2022, 2025]:
            with self.subTest(year=year):
                self.assertLess(
                    e7_unit_rate_ppm(year, TariffRegister.NIGHT),
                    e7_unit_rate_ppm(year, TariffRegister.DAY),
                )

class TestE7MeterRead(unittest.TestCase):

    def _read(self, day=400.0, night=600.0):
        from company.billing.economy7 import E7MeterRead
        return E7MeterRead("C1", dt.date(2023, 1, 1), day_kwh=day, night_kwh=night)

    def test_total_kwh(self):
        self.assertAlmostEqual(self._read(400.0, 600.0).total_kwh, 1000.0)

    def test_night_pct(self):
        self.assertAlmostEqual(self._read(400.0, 600.0).night_pct, 60.0)

    def test_night_pct_zero_total(self):
        self.assertAlmostEqual(self._read(0.0, 0.0).night_pct, 0.0)

    def test_day_heavy_night_pct(self):
        self.assertAlmostEqual(self._read(900.0, 100.0).night_pct, 10.0)


class TestE7Bill(unittest.TestCase):

    def _bill(self, day_kwh=1000.0, night_kwh=500.0, day_rate=28.0, night_rate=15.0):
        from company.billing.economy7 import E7Bill
        return E7Bill("C1", dt.date(2023, 1, 1), dt.date(2023, 4, 1),
                      day_kwh=day_kwh, night_kwh=night_kwh,
                      day_rate_ppm=day_rate, night_rate_ppm=night_rate)

    def test_day_charge_gbp(self):
        self.assertAlmostEqual(self._bill().day_charge_gbp, 2.80)

    def test_night_charge_gbp(self):
        self.assertAlmostEqual(self._bill().night_charge_gbp, 0.75)

    def test_total_gbp_is_sum(self):
        bill = self._bill()
        self.assertAlmostEqual(bill.total_gbp, bill.day_charge_gbp + bill.night_charge_gbp)

    def test_blended_rate_ppm_weighted(self):
        bill = self._bill(day_kwh=1000.0, night_kwh=1000.0, day_rate=20.0, night_rate=10.0)
        self.assertAlmostEqual(bill.blended_rate_ppm, 15.0)

    def test_blended_rate_zero_total(self):
        bill = self._bill(day_kwh=0.0, night_kwh=0.0)
        self.assertAlmostEqual(bill.blended_rate_ppm, 0.0)

    def test_generate_bill_picks_year_rates(self):
        from company.billing.economy7 import (
            generate_e7_bill, e7_unit_rate_ppm, TariffRegister,
        )
        bill = generate_e7_bill("C1", dt.date(2023, 1, 1), dt.date(2023, 3, 31), 1000.0, 500.0)
        self.assertAlmostEqual(bill.day_rate_ppm, e7_unit_rate_ppm(2023, TariffRegister.DAY))
        self.assertAlmostEqual(bill.night_rate_ppm, e7_unit_rate_ppm(2023, TariffRegister.NIGHT))

    def test_generate_bill_2022_crisis_rates(self):
        from company.billing.economy7 import generate_e7_bill
        bill = generate_e7_bill("C1", dt.date(2022, 4, 1), dt.date(2022, 6, 30), 500.0, 300.0)
        self.assertAlmostEqual(bill.day_rate_ppm, 34.0)
        self.assertAlmostEqual(bill.night_rate_ppm, 19.0)

class TestPaymentBehaviourExtra(unittest.TestCase):

    def _a(self):
        from company.billing.payment_behaviour import PaymentBehaviourAnalytics
        return PaymentBehaviourAnalytics()

    def test_dd_failed_days_late_is_none(self):
        from company.billing.payment_behaviour import PaymentRecord, PaymentResult
        r = PaymentRecord("C1", dt.date(2023, 1, 1), 100.0, 0.0, None, PaymentResult.DD_FAILED)
        self.assertIsNone(r.days_late)

    def test_missed_days_late_is_none(self):
        from company.billing.payment_behaviour import PaymentRecord, PaymentResult
        r = PaymentRecord("C1", dt.date(2023, 1, 1), 100.0, 0.0, None, PaymentResult.MISSED)
        self.assertIsNone(r.days_late)

    def test_on_time_rate_none_unknown(self):
        self.assertIsNone(self._a().on_time_rate("UNKNOWN"))

    def test_dd_failure_rate_none_unknown(self):
        self.assertIsNone(self._a().dd_failure_rate("UNKNOWN"))

    def test_behaviour_score_none_unknown(self):
        self.assertIsNone(self._a().behaviour_score("UNKNOWN"))

    def test_behaviour_score_good(self):
        from company.billing.payment_behaviour import PaymentBehaviour, PaymentResult
        a = self._a()
        a.record("C1", dt.date(2023, 1, 1), 100.0, 0.0, None, PaymentResult.DD_FAILED)
        for i in range(2, 13):
            a.record("C1", dt.date(2023, i, 1), 100.0, 100.0,
                     dt.date(2023, i, 1), PaymentResult.ON_TIME)
        self.assertEqual(a.behaviour_score("C1"), PaymentBehaviour.GOOD)

    def test_behaviour_score_fair(self):
        from company.billing.payment_behaviour import PaymentBehaviour, PaymentResult
        a = self._a()
        for _ in range(2):
            a.record("C1", dt.date(2023, 1, 1), 100.0, 0.0, None, PaymentResult.MISSED)
        for i in range(8):
            a.record("C1", dt.date(2023, 2, 1), 100.0, 100.0,
                     dt.date(2023, 2, 1), PaymentResult.ON_TIME)
        self.assertEqual(a.behaviour_score("C1"), PaymentBehaviour.FAIR)

    def test_behaviour_score_poor(self):
        from company.billing.payment_behaviour import PaymentBehaviour, PaymentResult
        a = self._a()
        for _ in range(2):
            a.record("C1", dt.date(2023, 1, 1), 100.0, 0.0, None, PaymentResult.MISSED)
        for i in range(3):
            a.record("C1", dt.date(2023, 2, 1), 100.0, 100.0,
                     dt.date(2023, 2, 1), PaymentResult.ON_TIME)
        self.assertEqual(a.behaviour_score("C1"), PaymentBehaviour.POOR)

    def test_avg_days_late_none_all_on_time(self):
        from company.billing.payment_behaviour import PaymentResult
        a = self._a()
        a.record("C1", dt.date(2023, 1, 1), 100.0, 100.0,
                 dt.date(2023, 1, 1), PaymentResult.ON_TIME)
        self.assertIsNone(a.avg_days_late("C1"))

    def test_records_for_unknown_empty(self):
        self.assertEqual(self._a().records_for_customer("UNKNOWN"), [])

    def test_shortfall_zero_fully_paid(self):
        from company.billing.payment_behaviour import PaymentRecord, PaymentResult
        r = PaymentRecord("C1", dt.date(2023, 1, 1), 100.0, 100.0,
                          dt.date(2023, 1, 1), PaymentResult.ON_TIME)
        self.assertAlmostEqual(r.shortfall_gbp, 0.0)

class TestRenewalEngineExtra(unittest.TestCase):

    def _pack(self, segment="RESI", spot=20.0, consumption=3500.0, cid="C1"):
        from company.billing.renewal_engine import generate_renewal_pack
        return generate_renewal_pack(
            customer_id=cid, segment=segment, spot_price_p_kwh=spot,
            annual_consumption_kwh=consumption, expiry_date="2024-06-30",
            days_to_expiry=42, quote_valid_until="2024-05-31",
        )

    def test_sme_margin_3p(self):
        pack = self._pack(segment="SME", spot=20.0)
        fixed = next(q for q in pack.quotes if q.tariff_type == "fixed_1yr")
        self.assertAlmostEqual(fixed.unit_rate_p_kwh, 23.0)

    def test_ic_margin_1p8(self):
        pack = self._pack(segment="IC", spot=20.0)
        fixed = next(q for q in pack.quotes if q.tariff_type == "fixed_1yr")
        self.assertAlmostEqual(fixed.unit_rate_p_kwh, 21.8)

    def test_sme_standing_charge(self):
        pack = self._pack(segment="SME")
        self.assertTrue(all(q.standing_charge_p_day == 92.0 for q in pack.quotes))

    def test_ic_no_standing_charge(self):
        pack = self._pack(segment="IC")
        self.assertTrue(all(q.standing_charge_p_day == 0.0 for q in pack.quotes))

    def test_fixed_2yr_0p5_premium(self):
        pack = self._pack(spot=20.0)
        rates = {q.tariff_type: q.unit_rate_p_kwh for q in pack.quotes}
        self.assertAlmostEqual(rates["fixed_2yr"] - rates["fixed_1yr"], 0.5)

    def test_svt_2p5_premium(self):
        pack = self._pack(spot=20.0)
        rates = {q.tariff_type: q.unit_rate_p_kwh for q in pack.quotes}
        self.assertAlmostEqual(rates["variable_svt"] - rates["fixed_1yr"], 2.5)

    def test_svt_quote_id_contains_var(self):
        pack = self._pack(cid="C1")
        svt = next(q for q in pack.quotes if q.tariff_type == "variable_svt")
        self.assertIn("VAR", svt.quote_id)

    def test_ic_annual_cost_no_sc(self):
        pack = self._pack(segment="IC", spot=20.0, consumption=10000.0)
        fixed = next(q for q in pack.quotes if q.tariff_type == "fixed_1yr")
        expected = round(10000.0 * 21.8 / 100.0, 2)
        self.assertAlmostEqual(fixed.annual_est_cost_gbp, expected)

    def test_resi_annual_cost_with_sc(self):
        pack = self._pack(segment="RESI", spot=20.0, consumption=3500.0)
        fixed = next(q for q in pack.quotes if q.tariff_type == "fixed_1yr")
        expected = round((3500.0 * 22.5 / 100.0) + (61.0 / 100.0 * 365.0), 2)
        self.assertAlmostEqual(fixed.annual_est_cost_gbp, expected)

    def test_all_quotes_carry_customer_id(self):
        pack = self._pack(cid="TEST99")
        self.assertTrue(all(q.customer_id == "TEST99" for q in pack.quotes))


if __name__ == "__main__":
    unittest.main()
