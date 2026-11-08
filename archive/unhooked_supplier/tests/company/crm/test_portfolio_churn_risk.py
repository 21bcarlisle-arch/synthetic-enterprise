"""Tests for PortfolioChurnRiskBook — Phase AD."""
import pytest
from company.crm.portfolio_churn_risk import (
    ChurnRiskBand,
    ChurnRiskDriver,
    CustomerChurnRisk,
    PortfolioChurnRiskBook,
    _classify_band,
    _classify_driver,
)


# ---- Classification helpers ----

class TestClassifyBand:
    def test_critical_at_50pct(self):
        assert _classify_band(0.50) == ChurnRiskBand.CRITICAL

    def test_critical_above_50pct(self):
        assert _classify_band(0.80) == ChurnRiskBand.CRITICAL

    def test_high_at_30pct(self):
        assert _classify_band(0.30) == ChurnRiskBand.HIGH

    def test_high_below_50pct(self):
        assert _classify_band(0.45) == ChurnRiskBand.HIGH

    def test_medium_at_15pct(self):
        assert _classify_band(0.15) == ChurnRiskBand.MEDIUM

    def test_medium_below_30pct(self):
        assert _classify_band(0.25) == ChurnRiskBand.MEDIUM

    def test_low_below_15pct(self):
        assert _classify_band(0.10) == ChurnRiskBand.LOW

    def test_low_at_zero(self):
        assert _classify_band(0.0) == ChurnRiskBand.LOW


class TestClassifyDriver:
    def test_rate_shock_primary(self):
        assert _classify_driver(0.25, 800.0, 5.0) == ChurnRiskDriver.RATE_SHOCK

    def test_bill_stress_when_no_rate_shock(self):
        assert _classify_driver(0.10, 3500.0, 5.0) == ChurnRiskDriver.BILL_STRESS

    def test_tenure_short_when_no_other_driver(self):
        assert _classify_driver(0.05, 800.0, 1.0) == ChurnRiskDriver.TENURE_SHORT

    def test_baseline_stable_customer(self):
        assert _classify_driver(0.05, 800.0, 5.0) == ChurnRiskDriver.BASELINE

    def test_rate_shock_takes_priority_over_bill_stress(self):
        # Both conditions met: rate shock wins
        assert _classify_driver(0.25, 4000.0, 5.0) == ChurnRiskDriver.RATE_SHOCK


# ---- CustomerChurnRisk properties ----

class TestCustomerChurnRisk:
    def _make(self, prob=0.35, revenue=900.0, band=ChurnRiskBand.HIGH) -> CustomerChurnRisk:
        return CustomerChurnRisk(
            account_id="C1",
            churn_probability=prob,
            risk_band=band,
            dominant_driver=ChurnRiskDriver.RATE_SHOCK,
            annual_revenue_gbp=revenue,
            tenure_years=2.0,
            segment="resi",
        )

    def test_expected_loss_gbp(self):
        r = self._make(prob=0.40, revenue=1000.0)
        assert r.expected_loss_gbp == pytest.approx(400.0)

    def test_expected_loss_zero_when_zero_prob(self):
        r = self._make(prob=0.0, revenue=1000.0)
        assert r.expected_loss_gbp == 0.0

    def test_is_at_risk_true_high(self):
        r = self._make(band=ChurnRiskBand.HIGH)
        assert r.is_at_risk is True

    def test_is_at_risk_true_critical(self):
        r = self._make(band=ChurnRiskBand.CRITICAL)
        assert r.is_at_risk is True

    def test_is_at_risk_false_medium(self):
        r = self._make(band=ChurnRiskBand.MEDIUM)
        assert r.is_at_risk is False

    def test_is_at_risk_false_low(self):
        r = self._make(band=ChurnRiskBand.LOW)
        assert r.is_at_risk is False


# ---- PortfolioChurnRiskBook ----

class TestPortfolioChurnRiskBook:
    def _populated_book(self) -> PortfolioChurnRiskBook:
        book = PortfolioChurnRiskBook()
        # Rate shock — likely CRITICAL or HIGH
        book.assess("C1", 150.0, 280.0, tenure_years=1.0, annual_consumption_kwh=3500.0,
                    annual_revenue_gbp=980.0, segment="resi")
        # Stable renewal — likely LOW
        book.assess("C2", 180.0, 190.0, tenure_years=7.0, annual_consumption_kwh=4000.0,
                    annual_revenue_gbp=760.0, segment="resi")
        # I&C high-churn base
        book.assess("C_IC", 200.0, 240.0, tenure_years=2.0, annual_consumption_kwh=200000.0,
                    annual_revenue_gbp=4000.0, segment="I&C")
        return book

    def test_assess_returns_risk(self):
        book = PortfolioChurnRiskBook()
        r = book.assess("C1", 150.0, 280.0, 1.0, 3500.0, 980.0)
        assert isinstance(r, CustomerChurnRisk)
        assert r.account_id == "C1"

    def test_all_risks_count(self):
        book = self._populated_book()
        assert len(book.all_risks) == 3

    def test_at_risk_customers_excludes_low(self):
        book = self._populated_book()
        at_risk_ids = {r.account_id for r in book.at_risk_customers()}
        # C2 stable should NOT be at risk
        assert "C2" not in at_risk_ids

    def test_by_band_returns_correct(self):
        book = self._populated_book()
        low = book.by_band(ChurnRiskBand.LOW)
        assert any(r.account_id == "C2" for r in low)

    def test_by_driver_rate_shock(self):
        book = self._populated_book()
        shocked = book.by_driver(ChurnRiskDriver.RATE_SHOCK)
        assert any(r.account_id == "C1" for r in shocked)

    def test_total_expected_loss_positive(self):
        book = self._populated_book()
        assert book.total_expected_loss_gbp > 0.0

    def test_total_revenue_at_risk_positive(self):
        book = self._populated_book()
        assert book.total_revenue_at_risk_gbp >= 0.0

    def test_portfolio_churn_rate_pct_range(self):
        book = self._populated_book()
        assert 0.0 <= book.portfolio_churn_rate_pct <= 100.0

    def test_empty_book_churn_rate(self):
        book = PortfolioChurnRiskBook()
        assert book.portfolio_churn_rate_pct == 0.0

    def test_top_n_by_expected_loss(self):
        book = self._populated_book()
        top = book.top_n_by_expected_loss(n=2)
        assert len(top) == 2
        # Highest loss first
        assert top[0].expected_loss_gbp >= top[1].expected_loss_gbp

    def test_driver_breakdown_keys_present(self):
        book = self._populated_book()
        bd = book.driver_breakdown()
        assert isinstance(bd, dict)
        assert sum(bd.values()) == 3

    def test_churn_risk_summary_keys(self):
        book = self._populated_book()
        s = book.churn_risk_summary()
        assert s["customers_assessed"] == 3
        assert "portfolio_churn_rate_pct" in s
        assert "total_expected_loss_gbp" in s
        assert "driver_breakdown" in s

    def test_empty_book_summary(self):
        book = PortfolioChurnRiskBook()
        s = book.churn_risk_summary()
        assert s["customers_assessed"] == 0
        assert s["total_expected_loss_gbp"] == 0.0

    def test_hedge_fraction_reduces_churn(self):
        book = PortfolioChurnRiskBook()
        no_hedge = book.assess("A", 150.0, 280.0, 1.0, 3500.0, 980.0, hedge_fraction=0.0)
        book2 = PortfolioChurnRiskBook()
        hedged = book2.assess("B", 150.0, 280.0, 1.0, 3500.0, 980.0, hedge_fraction=0.8)
        assert hedged.churn_probability <= no_hedge.churn_probability

    def test_gas_fuel_applies_gas_constants(self):
        book = PortfolioChurnRiskBook()
        gas = book.assess("C1g", 80.0, 100.0, 2.0, 12000.0, 1200.0, fuel="gas")
        elec = book.assess("C1e", 80.0, 100.0, 2.0, 12000.0, 1200.0, fuel="electricity")
        # Gas uses lower churn constants
        assert gas.churn_probability <= elec.churn_probability
