import pytest
from company.sustainability.decarbonisation_score import (
    DScoreBand, DScoreBreakdown, DScoreBook, DecarbScorer
)


def _scorer():
    return DecarbScorer()


def test_rego_full_coverage():
    s = _scorer()
    pts = s.score_rego_coverage(100.0, 100.0)
    assert abs(pts - 25.0) < 0.01


def test_rego_zero_coverage():
    s = _scorer()
    assert s.score_rego_coverage(0.0, 100.0) == 0.0


def test_rego_zero_total():
    s = _scorer()
    assert s.score_rego_coverage(100.0, 0.0) == 0.0


def test_epc_improvement_half():
    s = _scorer()
    pts = s.score_epc_improvement(5, 10)
    assert abs(pts - 12.5) < 0.01


def test_heat_pump_5pct_scores_full():
    s = _scorer()
    pts = s.score_heat_pump_adoption(20, 100)
    assert abs(pts - 25.0) < 0.01


def test_heat_pump_zero():
    s = _scorer()
    assert s.score_heat_pump_adoption(0, 100) == 0.0


def test_carbon_reduction_20pct():
    s = _scorer()
    pts = s.score_carbon_reduction(1000.0, 800.0)
    assert pts > 0


def test_band_a():
    bd = DScoreBreakdown(
        rego_coverage_pts=25.0, epc_improvement_pts=25.0,
        heat_pump_pts=20.0, carbon_reduction_pts=15.0
    )
    assert bd.band == DScoreBand.A
    assert bd.total == 85.0


def test_band_d():
    bd = DScoreBreakdown(
        rego_coverage_pts=5.0, epc_improvement_pts=5.0,
        heat_pump_pts=0.0, carbon_reduction_pts=5.0
    )
    assert bd.band == DScoreBand.D


def test_to_dict_keys():
    bd = DScoreBreakdown(
        rego_coverage_pts=10.0, epc_improvement_pts=8.0,
        heat_pump_pts=5.0, carbon_reduction_pts=3.0
    )
    d = bd.to_dict()
    for k in ("total", "band", "rego_coverage_pts", "epc_improvement_pts",
               "heat_pump_pts", "carbon_reduction_pts"):
        assert k in d


def test_book_records_and_trend():
    book = DScoreBook()
    scorer = DecarbScorer()
    for yr, cov, imp, hp, pc, cc in [
        (2020, 50.0, 2, 1, 500.0, 480.0),
        (2021, 70.0, 3, 2, 480.0, 450.0),
        (2022, 90.0, 4, 3, 450.0, 400.0),
    ]:
        bd = scorer.compute(cov, 100.0, imp, 20, hp, pc, cc)
        book.record(yr, bd)
    trend = book.trend()
    assert len(trend) == 3
    assert trend[0]["year"] == 2020
    assert trend[2]["total"] > trend[0]["total"]


def test_book_improving():
    book = DScoreBook()
    scorer = DecarbScorer()
    bd1 = scorer.compute(30.0, 100.0, 1, 20, 0, 500.0, 490.0)
    bd2 = scorer.compute(80.0, 100.0, 5, 20, 2, 490.0, 440.0)
    book.record(2021, bd1)
    book.record(2022, bd2)
    assert book.improving() is True


def test_book_summary_keys():
    book = DScoreBook()
    scorer = DecarbScorer()
    book.record(2022, scorer.compute(50.0, 100.0, 2, 20, 1, 500.0, 480.0))
    s = book.summary()
    for k in ("years_recorded", "latest_score", "latest_band", "improving", "trend"):
        assert k in s


# --- Phase KA depth tests ---

def test_band_b_at_exactly_60():
    bd = DScoreBreakdown(
        rego_coverage_pts=25.0, epc_improvement_pts=25.0,
        heat_pump_pts=0.0, carbon_reduction_pts=10.0
    )
    assert bd.total == pytest.approx(60.0)
    assert bd.band == DScoreBand.B


def test_band_c_at_exactly_40():
    bd = DScoreBreakdown(
        rego_coverage_pts=10.0, epc_improvement_pts=15.0,
        heat_pump_pts=10.0, carbon_reduction_pts=5.0
    )
    assert bd.total == pytest.approx(40.0)
    assert bd.band == DScoreBand.C


def test_rego_capped_at_max():
    s = DecarbScorer()
    pts = s.score_rego_coverage(200.0, 100.0)
    assert pts == pytest.approx(25.0)


def test_epc_zero_total_returns_zero():
    s = DecarbScorer()
    assert s.score_epc_improvement(5, 0) == pytest.approx(0.0)


def test_heat_pump_zero_total_returns_zero():
    s = DecarbScorer()
    assert s.score_heat_pump_adoption(2, 0) == pytest.approx(0.0)


def test_carbon_zero_prior_returns_zero():
    s = DecarbScorer()
    assert s.score_carbon_reduction(0.0, 100.0) == pytest.approx(0.0)


def test_carbon_increase_gives_zero_score():
    s = DecarbScorer()
    pts = s.score_carbon_reduction(500.0, 600.0)
    assert pts == pytest.approx(0.0)


def test_book_latest_none_when_empty():
    book = DScoreBook()
    assert book.latest() is None


def test_book_score_for_year_none_when_missing():
    book = DScoreBook()
    scorer = DecarbScorer()
    book.record(2022, scorer.compute(50.0, 100.0, 2, 20, 1, 500.0, 480.0))
    assert book.score_for_year(2099) is None


def test_book_improving_false_with_one_record():
    book = DScoreBook()
    scorer = DecarbScorer()
    book.record(2022, scorer.compute(50.0, 100.0, 2, 20, 1, 500.0, 480.0))
    assert book.improving() is False
