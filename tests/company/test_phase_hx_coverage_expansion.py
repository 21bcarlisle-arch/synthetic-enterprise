"""Phase HX: coverage expansion for acquisition_strategy_book, dual_fuel_bill, market_share_estimator."""
import datetime as dt
import pytest

# ===== acquisition_strategy_book =====
from company.crm.acquisition_strategy_book import (
    AcquisitionStrategyBook, ChannelROIAnalysis, PortfolioGrowthScenario
)

class TestAcquisitionStrategyBook:
    def test_analyse_channel_viable(self):
        book = AcquisitionStrategyBook()
        r = book.analyse_channel("referral", "resi", expected_annual_margin_gbp=200.0)
        assert isinstance(r, ChannelROIAnalysis)
        assert r.is_viable  # referral CAC=20, CLV=200*3.2=640 ≥ 3×20=60

    def test_analyse_channel_not_viable_negative_margin(self):
        book = AcquisitionStrategyBook()
        r = book.analyse_channel("broker", "resi", expected_annual_margin_gbp=-10.0)
        assert not r.is_viable
        assert r.payback_months is None

    def test_cac_override(self):
        book = AcquisitionStrategyBook()
        r = book.analyse_channel("pcw", "resi", expected_annual_margin_gbp=100.0, cac_override_gbp=999.0)
        assert r.cac_gbp == 999.0

    def test_roi_pct_positive_when_viable(self):
        book = AcquisitionStrategyBook()
        r = book.analyse_channel("referral", "resi", expected_annual_margin_gbp=200.0)
        assert r.roi_pct is not None
        assert r.roi_pct > 0

    def test_rank_channels_sorted_by_roi(self):
        book = AcquisitionStrategyBook()
        ranked = book.rank_channels("resi", expected_annual_margin_gbp=200.0)
        rois = [r.roi_pct for r in ranked if r.roi_pct is not None]
        assert rois == sorted(rois, reverse=True)

    def test_rank_channels_includes_all_standard_channels(self):
        book = AcquisitionStrategyBook()
        ranked = book.rank_channels("resi", expected_annual_margin_gbp=200.0)
        channels = {r.channel for r in ranked}
        assert "referral" in channels and "pcw" in channels and "broker" in channels

    def test_model_growth_scenario_returns_scenario(self):
        book = AcquisitionStrategyBook()
        s = book.model_growth_scenario(100, "pcw", "resi", expected_annual_margin_gbp=150.0)
        assert isinstance(s, PortfolioGrowthScenario)
        assert s.target_new_customers == 100

    def test_model_growth_scenario_total_cac(self):
        book = AcquisitionStrategyBook()
        s = book.model_growth_scenario(100, "pcw", "resi", expected_annual_margin_gbp=150.0,
                                       win_rate_override=0.20)
        # required_attempts = 100/0.20=500; pcw CAC=55; total=500*55=27500
        assert s.required_attempts == 500
        assert s.total_cac_spend_gbp == pytest.approx(27_500.0)

    def test_minimum_viable_clv(self):
        book = AcquisitionStrategyBook()
        mvclv = book.minimum_viable_clv("referral")  # CAC=20, hurdle=3× → 60
        assert mvclv == pytest.approx(60.0)

    def test_strategy_summary_not_empty(self):
        book = AcquisitionStrategyBook()
        s = book.strategy_summary("resi", 150.0)
        assert "resi" in s and "Viable channels" in s


# ===== dual_fuel_bill =====
from company.billing.dual_fuel_bill import DualFuelBill, FuelBillSection

def _section(fuel="electricity", total=120.0, paid="paid"):
    return FuelBillSection(
        fuel=fuel, period_start="2024-01-01", period_end="2024-02-01",
        days_in_period=31, consumption_kwh=350.0, unit_rate_pence=28.0,
        standing_charge_pence_per_day=60.0, standing_charge_gbp=18.6,
        energy_charge_gbp=98.0, levies_gbp=5.0, subtotal_gbp=103.0,
        vat_rate=0.05, vat_gbp=5.15, total_gbp=total,
        invoice_number=101, payment_status=paid,
    )

def _bill(elec_total=100.0, gas_total=60.0, paid=120.0, gas=True):
    elec = _section("electricity", elec_total, "paid")
    gas_sec = _section("gas", gas_total, "unpaid") if gas else None
    return DualFuelBill(
        account_id="C1", market_type="resi",
        billing_period_start="2024-01-01", billing_period_end="2024-02-01",
        electricity=elec, gas=gas_sec,
        total_billed_gbp=elec_total + (gas_total if gas else 0),
        total_paid_gbp=paid,
    )

class TestDualFuelBill:
    def test_is_dual_fuel(self):
        bill = _bill()
        assert bill.is_dual_fuel

    def test_is_electricity_only(self):
        bill = _bill(gas=False)
        assert bill.is_electricity_only
        assert not bill.is_dual_fuel

    def test_balance_gbp_in_credit(self):
        bill = DualFuelBill("C1","resi","2024-01-01","2024-02-01",
                            _section(), None, 100.0, 120.0)
        assert bill.balance_gbp == pytest.approx(20.0)
        assert bill.in_credit

    def test_balance_gbp_owing(self):
        bill = DualFuelBill("C1","resi","2024-01-01","2024-02-01",
                            _section(), None, 100.0, 80.0)
        assert bill.amount_owing_gbp == pytest.approx(20.0)
        assert not bill.in_credit

    def test_all_paid_when_both_sections_paid(self):
        bill = DualFuelBill("C1","resi","2024-01-01","2024-02-01",
                            _section(paid="paid"), _section("gas", paid="paid"),
                            160.0, 160.0)
        assert bill.all_paid

    def test_not_all_paid_when_gas_unpaid(self):
        bill = DualFuelBill("C1","resi","2024-01-01","2024-02-01",
                            _section(paid="paid"), _section("gas", paid="unpaid"),
                            160.0, 100.0)
        assert not bill.all_paid

    def test_billing_calendar_resi_monthly(self):
        bill = _bill()
        assert bill.billing_calendar == "monthly"

    def test_fuel_section_is_paid_property(self):
        s = _section(paid="paid")
        assert s.is_paid

    def test_fuel_section_effective_rate(self):
        s = _section(total=108.15, fuel="electricity")
        assert s.effective_rate_pence == pytest.approx(30.9, rel=0.01)

    def test_gas_only_when_no_electricity(self):
        bill = DualFuelBill("C1","resi","2024-01-01","2024-02-01",
                            None, _section("gas"), 108.15, 0.0)
        assert bill.is_gas_only


# ===== market_share_estimator =====
from company.market.market_share_estimator import (
    MarketShareEstimator, MarketSegment, MarketShareSnapshot
)

class TestMarketShareEstimator:
    def test_record_year_creates_snapshot(self):
        est = MarketShareEstimator()
        snap = est.record_year(2023, {MarketSegment.DOMESTIC: 5000})
        assert isinstance(snap, MarketShareSnapshot)
        assert snap.year == 2023

    def test_total_own_customers(self):
        est = MarketShareEstimator()
        snap = est.record_year(2023, {
            MarketSegment.DOMESTIC: 5000, MarketSegment.SME: 200
        })
        assert snap.total_own_customers == 5200

    def test_blended_share_pct(self):
        est = MarketShareEstimator()
        # Use market_overrides to control denominator; set non-domestic to same as own count (0)
        snap = est.record_year(2023,
            {MarketSegment.DOMESTIC: 29_000},
            market_overrides={
                MarketSegment.DOMESTIC: 2_900_000,
                MarketSegment.SME: 0,
                MarketSegment.INDUSTRIAL_COMMERCIAL: 0,
            })
        # 29k / 2900k = 1.0%
        assert snap.blended_share_pct == pytest.approx(1.0, abs=0.01)

    def test_snapshot_for_year(self):
        est = MarketShareEstimator()
        est.record_year(2022, {MarketSegment.DOMESTIC: 3000})
        est.record_year(2023, {MarketSegment.DOMESTIC: 4000})
        snap = est.snapshot_for_year(2022)
        assert snap.total_own_customers == 3000

    def test_latest_snapshot_most_recent(self):
        est = MarketShareEstimator()
        est.record_year(2022, {MarketSegment.DOMESTIC: 3000})
        est.record_year(2023, {MarketSegment.DOMESTIC: 4000})
        assert est.latest_snapshot.year == 2023

    def test_growth_rate_pct(self):
        est = MarketShareEstimator()
        est.record_year(2022, {MarketSegment.DOMESTIC: 2000})
        est.record_year(2023, {MarketSegment.DOMESTIC: 2500})
        gr = est.growth_rate_pct(2022, 2023)
        assert gr == pytest.approx(25.0, rel=0.01)

    def test_is_micro_supplier(self):
        est = MarketShareEstimator()
        snap = est.record_year(2023, {MarketSegment.DOMESTIC: 100})  # tiny share
        resi = snap.estimate_for_segment(MarketSegment.DOMESTIC)
        assert resi.is_micro_supplier

    def test_largest_segment_by_share(self):
        est = MarketShareEstimator()
        snap = est.record_year(2023, {
            MarketSegment.DOMESTIC: 500,
            MarketSegment.SME: 1000,   # SME market is much smaller → higher share
        })
        assert snap.largest_segment is not None

    def test_share_trend_sorted_by_year(self):
        est = MarketShareEstimator()
        est.record_year(2022, {MarketSegment.DOMESTIC: 2000})
        est.record_year(2023, {MarketSegment.DOMESTIC: 3000})
        trend = est.share_trend()
        assert list(trend.keys()) == [2022, 2023]

    def test_market_summary_keys(self):
        est = MarketShareEstimator()
        est.record_year(2023, {MarketSegment.DOMESTIC: 5000})
        s = est.market_summary()
        assert "Market Share" in s and "customers" in s
