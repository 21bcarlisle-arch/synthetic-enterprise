# Increment 3: the legs of tests/company/test_phase_jc_coverage_expansion.py that test archived modules. Its live legs stay there.
"""Phase JC coverage expansion: capacity_market, company_pl, credit_limits."""
import datetime as dt
import unittest


class TestCompanyPL(unittest.TestCase):

    def _pl(self, revenue=1_000_000.0, wholesale=600_000.0, policy=80_000.0,
             network=120_000.0, opex=100_000.0, marketing=20_000.0,
             bad_debt=10_000.0, whd=5_000.0, gsop=2_000.0):
        from company.finance.company_pl import CompanyPL
        return CompanyPL(2023, revenue, wholesale, policy, network,
                          opex, marketing, bad_debt, whd, gsop)

    def test_gross_margin_gbp(self):
        pl = self._pl()
        # 1M - 600k - 80k - 120k = 200k
        self.assertAlmostEqual(pl.gross_margin_gbp, 200_000.0)

    def test_total_operating_cost_gbp(self):
        pl = self._pl()
        # 100k + 20k + 10k + 5k + 2k = 137k
        self.assertAlmostEqual(pl.total_operating_cost_gbp, 137_000.0)

    def test_ebitda_gbp(self):
        pl = self._pl()
        # 200k - 137k = 63k
        self.assertAlmostEqual(pl.ebitda_gbp, 63_000.0)

    def test_gross_margin_pct(self):
        pl = self._pl()
        self.assertAlmostEqual(pl.gross_margin_pct, 20.0)

    def test_ebitda_margin_pct(self):
        pl = self._pl()
        self.assertAlmostEqual(pl.ebitda_margin_pct, 6.3)

    def test_bad_debt_as_pct_revenue(self):
        pl = self._pl(revenue=1_000_000.0, bad_debt=10_000.0)
        self.assertAlmostEqual(pl.bad_debt_as_pct_revenue, 1.0)

    def test_is_profitable_true(self):
        pl = self._pl()
        self.assertTrue(pl.is_profitable)

    def test_is_profitable_false_loss(self):
        from company.finance.company_pl import CompanyPL
        pl = CompanyPL(2023, 100_000.0, 90_000.0, 10_000.0, 10_000.0, 20_000.0, 0.0, 0.0, 0.0, 0.0)
        self.assertFalse(pl.is_profitable)

    def test_summary_structure(self):
        pl = self._pl()
        s = pl.summary()
        self.assertIn("revenue_gbp", s)
        self.assertIn("gross_margin_gbp", s)
        self.assertIn("ebitda_gbp", s)
        self.assertIn("is_profitable", s)

    def test_build_company_pl(self):
        from company.finance.company_pl import build_company_pl
        pl = build_company_pl(2023, 500_000.0, 300_000.0, 50_000.0, 80_000.0, 60_000.0)
        self.assertEqual(pl.year, 2023)
        self.assertAlmostEqual(pl.gross_margin_gbp, 70_000.0)
