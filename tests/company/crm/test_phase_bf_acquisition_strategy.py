"""Phase BF: Acquisition Strategy Intelligence Book tests."""
import pytest
from company.crm.acquisition_strategy_book import (
    AcquisitionStrategyBook, ChannelROIAnalysis, PortfolioGrowthScenario,
    _TYPICAL_CAC_GBP, _TYPICAL_TENURE_YEARS,
)


def _book(win_rates=None):
    return AcquisitionStrategyBook(win_rate_by_segment=win_rates)


# 1. analyse_channel returns ChannelROIAnalysis
def test_analyse_channel_returns_result():
    book = _book()
    r = book.analyse_channel("pcw", "resi", 200.0)
    assert isinstance(r, ChannelROIAnalysis)
    assert r.channel == "pcw"


# 2. CLV = annual_margin × tenure
def test_clv_is_margin_times_tenure():
    book = _book()
    r = book.analyse_channel("pcw", "resi", 200.0, expected_tenure_years=3.0)
    assert abs(r.expected_clv_gbp - 600.0) < 0.01


# 3. is_viable requires CLV >= CAC × 3
def test_viability_3x_hurdle():
    book = _book()
    # PCW CAC ≈ £55; annual margin × tenure needs to be ≥ £165 for viable
    # With £200/yr × 3.2yr = £640 >> £165 → viable
    r = book.analyse_channel("pcw", "resi", 200.0)
    assert r.is_viable  # 640 >> 3 × 55


# 4. Not viable when CLV < CAC
def test_not_viable_low_margin():
    book = _book()
    r = book.analyse_channel("broker", "resi", 5.0, expected_tenure_years=1.0)
    # broker CAC ≈ £160; CLV = £5 → not viable
    assert not r.is_viable


# 5. payback_months computed
def test_payback_months():
    book = _book()
    # PCW cac ≈ 55; monthly margin = 200/12 ≈ 16.67; payback ≈ 3.3 months
    r = book.analyse_channel("pcw", "resi", 200.0)
    assert r.payback_months is not None
    assert 2 < r.payback_months < 5


# 6. Referral cheapest channel
def test_referral_lowest_cac():
    assert _TYPICAL_CAC_GBP["referral"] < _TYPICAL_CAC_GBP["pcw"]
    assert _TYPICAL_CAC_GBP["referral"] < _TYPICAL_CAC_GBP["broker"]


# 7. rank_channels returns all 5 channels sorted by ROI
def test_rank_channels_five_entries():
    book = _book()
    ranked = book.rank_channels("resi", 150.0)
    assert len(ranked) == 5
    # sorted by ROI descending
    rois = [r.roi_pct for r in ranked if r.roi_pct is not None]
    assert rois == sorted(rois, reverse=True)


# 8. model_growth_scenario computes total spend
def test_growth_scenario_spend():
    book = _book(win_rates={"resi": 0.20})
    scenario = book.model_growth_scenario(5, "pcw", "resi", 200.0)
    # Need 5 / 0.20 = 25 attempts; spend = 25 × £55 = £1,375
    assert scenario.required_attempts == 25
    assert abs(scenario.total_cac_spend_gbp - 25 * _TYPICAL_CAC_GBP["pcw"]) < 0.01


# 9. model_growth_scenario net_value = CLV - CAC_spend
def test_growth_scenario_net_value():
    book = _book(win_rates={"resi": 0.20})
    scenario = book.model_growth_scenario(5, "pcw", "resi", 200.0, expected_tenure_years=3.0)
    expected_clv = 5 * 200.0 * 3.0
    expected_net = expected_clv - scenario.total_cac_spend_gbp
    assert abs(scenario.net_value_gbp - expected_net) < 0.01


# 10. minimum_viable_clv is CAC × hurdle
def test_minimum_viable_clv():
    book = _book()
    min_clv = book.minimum_viable_clv("pcw", hurdle_multiple=3.0)
    assert abs(min_clv - _TYPICAL_CAC_GBP["pcw"] * 3.0) < 0.01


# 11. negative margin gives not_viable
def test_negative_margin_not_viable():
    book = _book()
    r = book.analyse_channel("direct", "resi", -50.0)
    assert not r.is_viable
    assert r.roi_pct is None


# 12. strategy_summary contains channel recommendation
def test_strategy_summary():
    book = _book()
    summary = book.strategy_summary("resi", 200.0)
    assert "resi" in summary
    assert "Best channel" in summary


# 13. CAC override respected
def test_cac_override():
    book = _book()
    r = book.analyse_channel("pcw", "resi", 200.0, cac_override_gbp=100.0)
    assert abs(r.cac_gbp - 100.0) < 0.01


# 14. I&C segment has higher tenure than resi
def test_ic_higher_tenure():
    assert _TYPICAL_TENURE_YEARS["I&C"] > _TYPICAL_TENURE_YEARS["resi"]


# 15. net_value_gbp property
def test_net_value_property():
    book = _book()
    r = book.analyse_channel("referral", "resi", 200.0, expected_tenure_years=3.0)
    expected_net = r.expected_clv_gbp - r.cac_gbp
    assert abs(r.net_value_gbp - expected_net) < 0.01


# --- Phase MQ depth tests ---

def test_channel_roi_segment_stored():
    book = _book()
    r = book.analyse_channel("pcw", "SME", 200.0)
    assert r.segment == "SME"


def test_channel_roi_cac_gbp_matches_typical():
    book = _book()
    r = book.analyse_channel("pcw", "resi", 200.0)
    assert r.cac_gbp == pytest.approx(_TYPICAL_CAC_GBP["pcw"])


def test_channel_roi_payback_none_negative_margin():
    book = _book()
    r = book.analyse_channel("direct", "resi", -10.0)
    assert r.payback_months is None


def test_channel_roi_recommendation_not_empty():
    book = _book()
    r = book.analyse_channel("pcw", "resi", 200.0)
    assert len(r.recommendation) > 0


def test_portfolio_scenario_target_new_customers_stored():
    book = _book(win_rates={"resi": 0.20})
    scenario = book.model_growth_scenario(10, "pcw", "resi", 200.0)
    assert scenario.target_new_customers == 10


def test_portfolio_scenario_channel_stored():
    book = _book(win_rates={"resi": 0.20})
    scenario = book.model_growth_scenario(5, "referral", "resi", 200.0)
    assert scenario.channel == "referral"


def test_portfolio_scenario_segment_stored():
    book = _book(win_rates={"SME": 0.12})
    scenario = book.model_growth_scenario(5, "pcw", "SME", 200.0)
    assert scenario.segment == "SME"


def test_portfolio_scenario_win_rate_pct():
    book = _book(win_rates={"resi": 0.20})
    scenario = book.model_growth_scenario(5, "pcw", "resi", 200.0)
    assert scenario.win_rate_assumption_pct == pytest.approx(20.0)


def test_typical_cac_has_5_channels():
    assert len(_TYPICAL_CAC_GBP) == 5


def test_portfolio_scenario_expected_clv():
    book = _book(win_rates={"resi": 0.20})
    scenario = book.model_growth_scenario(5, "pcw", "resi", 100.0, expected_tenure_years=3.0)
    assert scenario.expected_total_clv_gbp == pytest.approx(5 * 100.0 * 3.0)
