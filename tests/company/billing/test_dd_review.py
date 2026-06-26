import pytest
from datetime import date
from company.billing.dd_review import DDAction, DDReviewBook, review


def test_review_increase_when_underpaying():
    # £80/month DD, actual spend £1200/year = £100/month implied → +25% variance
    result = review("C1", date(2022, 3, 1), current_dd_gbp=80.0, actual_annual_spend_gbp=1200.0)
    assert result.action == DDAction.INCREASE
    assert result.variance_pct == pytest.approx(25.0, abs=0.2)


def test_review_decrease_when_overpaying():
    # £120/month DD, actual spend £1200/year = £100/month implied → -16.7% variance
    result = review("C1", date(2022, 3, 1), current_dd_gbp=120.0, actual_annual_spend_gbp=1200.0)
    assert result.action == DDAction.DECREASE
    assert result.variance_pct < -5.0


def test_review_maintain_within_threshold():
    # £100/month DD, actual spend £1030/year = £85.8/month implied → ~-14% wait
    # Actually: £100*12=£1200 implied; actual £1200*1.03=£1236; var=(1236-1200)/1200*100=+3%
    result = review("C1", date(2022, 3, 1), current_dd_gbp=100.0, actual_annual_spend_gbp=1236.0)
    assert result.action == DDAction.MAINTAIN
    assert -5.0 <= result.variance_pct <= 5.0


def test_recommended_monthly_is_annual_over_12():
    result = review("C1", date(2022, 3, 1), current_dd_gbp=80.0, actual_annual_spend_gbp=1200.0)
    assert result.recommended_monthly_gbp == 100.0


def test_recommended_monthly_rounds_up():
    # £1210/year / 12 = £100.83 -> ceiling rounds to £101
    result = review("C1", date(2022, 3, 1), current_dd_gbp=80.0, actual_annual_spend_gbp=1210.0)
    assert result.recommended_monthly_gbp >= 101.0


def test_run_review_records_result():
    book = DDReviewBook()
    r = book.run_review("C1", date(2022, 3, 1), 80.0, 1200.0)
    assert r.action == DDAction.INCREASE
    assert book.latest_review("C1") is r


def test_latest_review_returns_most_recent():
    book = DDReviewBook()
    book.run_review("C1", date(2021, 3, 1), 80.0, 1200.0)
    r2 = book.run_review("C1", date(2022, 3, 1), 100.0, 1200.0)
    assert book.latest_review("C1") is r2


def test_latest_review_none_if_not_reviewed():
    book = DDReviewBook()
    assert book.latest_review("UNKNOWN") is None


def test_overdue_for_review_triggers_after_12_months():
    book = DDReviewBook()
    last = {"C1": date(2021, 1, 1)}
    overdue = book.overdue_for_review(date(2022, 2, 1), last)
    assert "C1" in overdue


def test_not_overdue_within_12_months():
    book = DDReviewBook()
    last = {"C1": date(2021, 3, 1)}
    overdue = book.overdue_for_review(date(2022, 2, 1), last)
    assert "C1" not in overdue


def test_summary_counts(book=None):
    book = DDReviewBook()
    book.run_review("C1", date(2022, 1, 1), 80.0, 1200.0)   # INCREASE
    book.run_review("C2", date(2022, 1, 1), 120.0, 1200.0)  # DECREASE
    book.run_review("C3", date(2022, 1, 1), 100.0, 1236.0)  # MAINTAIN
    s = book.summary()
    assert s["total_reviews"] == 3
    assert s["increase_count"] == 1
    assert s["decrease_count"] == 1
    assert s["maintain_count"] == 1


def test_summary_empty_book():
    book = DDReviewBook()
    s = book.summary()
    assert s["total_reviews"] == 0
    assert s["avg_variance_pct"] == 0.0
