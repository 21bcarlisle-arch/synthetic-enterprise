import datetime as dt
import pytest
from company.crm.css_tracker import (
    CSSResponse, CSSBook, CSSPerformanceBand
)

YEAR = 2023
SURVEY_DATE = dt.date(2023, 9, 15)


def _response(**kwargs):
    defaults = dict(
        customer_id="C1",
        survey_year=YEAR,
        survey_date=SURVEY_DATE,
        overall_score=7.5,
        billing_accuracy=8.0,
        ease_of_contact=7.0,
        value_for_money=6.5,
        meter_accuracy=8.5,
    )
    defaults.update(kwargs)
    return CSSResponse(**defaults)


def test_response_validation_out_of_range():
    with pytest.raises(ValueError):
        _response(overall_score=11.0)
    with pytest.raises(ValueError):
        _response(billing_accuracy=0.0)


def test_response_complaint_handling_optional():
    r = _response(complaint_handling=None)
    assert r.complaint_handling is None


def test_composite_score_without_complaints():
    r = _response(overall_score=8.0, billing_accuracy=8.0, ease_of_contact=8.0,
                  value_for_money=8.0, meter_accuracy=8.0)
    assert r.composite_score == pytest.approx(8.0, rel=0.01)


def test_composite_score_with_complaints():
    r = _response(overall_score=8.0, billing_accuracy=8.0, ease_of_contact=8.0,
                  value_for_money=8.0, meter_accuracy=8.0, complaint_handling=6.0)
    # complaint handling 6.0 pulls composite below 8.0
    assert r.composite_score < 8.0


def test_would_recommend_above_7():
    r = _response(overall_score=7.5)
    assert r.would_recommend is True


def test_would_recommend_below_7():
    r = _response(overall_score=6.5)
    assert r.would_recommend is False


def test_book_avg_score():
    book = CSSBook()
    book.record_response("C1", YEAR, SURVEY_DATE, 7.0, 8.0, 7.0, 6.5, 8.0)
    book.record_response("C2", YEAR, SURVEY_DATE, 8.0, 8.0, 7.0, 7.5, 8.5)
    avg = book.avg_score(YEAR, "overall_score")
    assert avg == pytest.approx(7.5)


def test_book_performance_band_top():
    book = CSSBook()
    book.record_response("C1", YEAR, SURVEY_DATE, 8.5, 9.0, 8.0, 8.0, 9.0)
    book.record_response("C2", YEAR, SURVEY_DATE, 8.0, 8.5, 8.5, 8.0, 8.5)
    assert book.performance_band(YEAR) == CSSPerformanceBand.TOP


def test_book_performance_band_bottom():
    book = CSSBook()
    book.record_response("C1", YEAR, SURVEY_DATE, 5.0, 5.5, 5.0, 4.5, 5.0)
    assert book.performance_band(YEAR) == CSSPerformanceBand.BOTTOM


def test_book_vs_industry_avg_2022_crisis():
    book = CSSBook()
    # 2022: industry avg is 5.2; supplier at 5.5 = +0.3 above average even in crisis
    book.record_response("C1", 2022, dt.date(2022, 9, 1), 5.5, 5.0, 5.0, 4.0, 6.0)
    delta = book.vs_industry_avg(2022)
    assert delta == pytest.approx(0.3, abs=0.01)


def test_book_recommend_rate():
    book = CSSBook()
    book.record_response("C1", YEAR, SURVEY_DATE, 8.0, 8.0, 7.0, 7.0, 8.0)
    book.record_response("C2", YEAR, SURVEY_DATE, 6.0, 7.0, 6.0, 6.0, 7.0)
    book.record_response("C3", YEAR, SURVEY_DATE, 7.5, 7.5, 7.5, 7.0, 7.5)
    rate = book.recommend_rate(YEAR)
    assert rate == pytest.approx(2 / 3, rel=0.01)


def test_book_css_summary_keys():
    book = CSSBook()
    book.record_response("C1", YEAR, SURVEY_DATE, 7.5, 8.0, 7.0, 7.0, 8.0)
    s = book.css_summary(YEAR)
    assert s["year"] == YEAR
    assert s["responses"] == 1
    assert "avg_overall" in s
    assert "performance_band" in s
    assert "vs_industry" in s
    assert "recommend_rate" in s
