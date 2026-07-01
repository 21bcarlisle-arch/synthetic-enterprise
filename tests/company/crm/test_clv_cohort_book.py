import pytest
from company.crm.clv_cohort_book import CLVCohortBook, CohortSummary


def _book():
    book = CLVCohortBook()
    book.add('C001', 2019, 'pcw', 'residential', 320.0, 120.0, 3.0)
    book.add('C002', 2019, 'pcw', 'residential', 280.0, 100.0, 3.0)
    book.add('C003', 2020, 'direct', 'residential', 450.0, 180.0, 4.0)
    book.add('C004', 2020, 'pcw', 'sme', 1200.0, 500.0, 4.0)
    book.add('C005', 2022, 'pcw', 'residential', -50.0, -20.0, 1.0)
    return book


def test_by_acquisition_year_count():
    book = _book()
    c = book.by_acquisition_year(2019)
    assert c.customer_count == 2


def test_by_acquisition_year_avg_clv():
    book = _book()
    c = book.by_acquisition_year(2019)
    assert c.avg_clv_gbp == pytest.approx(300.0)


def test_by_channel():
    book = _book()
    c = book.by_channel('pcw')
    assert c.customer_count == 4


def test_by_segment_sme():
    book = _book()
    c = book.by_segment('sme')
    assert c.customer_count == 1
    assert c.avg_clv_gbp == pytest.approx(1200.0)


def test_2022_crisis_cohort_profitable_pct():
    book = _book()
    c = book.by_acquisition_year(2022)
    assert c.profitable_pct == pytest.approx(0.0)


def test_best_cohort_by_year():
    book = _book()
    best = book.best_cohort_by_year()
    assert best is not None
    assert best.key == '2020'


def test_worst_cohort_by_year():
    book = _book()
    worst = book.worst_cohort_by_year()
    assert worst is not None
    assert worst.key == '2022'


def test_portfolio_summary():
    book = _book()
    s = book.portfolio_summary()
    assert s['total_customers'] == 5
    assert 'total_clv_gbp' in s
    assert 'profitable_pct' in s


def test_is_profitable_cohort():
    book = _book()
    c2019 = book.by_acquisition_year(2019)
    c2022 = book.by_acquisition_year(2022)
    assert c2019.is_profitable_cohort is True
    assert c2022.is_profitable_cohort is False


# --- Phase KA depth tests ---

def test_by_acquisition_year_empty():
    book = _book()
    c = book.by_acquisition_year(2099)
    assert c.customer_count == 0
    assert c.avg_clv_gbp == pytest.approx(0.0)


def test_by_channel_empty():
    book = _book()
    c = book.by_channel('unknown_channel')
    assert c.customer_count == 0


def test_by_segment_empty():
    book = _book()
    c = book.by_segment('unknown_segment')
    assert c.customer_count == 0


def test_cohort_summary_median_even():
    # 2019 has 2 records: [280, 320] -> median = (280+320)/2 = 300
    book = _book()
    c = book.by_acquisition_year(2019)
    assert c.median_clv_gbp == pytest.approx(300.0)


def test_cohort_summary_total_clv():
    # 2019: 320 + 280 = 600
    book = _book()
    c = book.by_acquisition_year(2019)
    assert c.total_clv_gbp == pytest.approx(600.0)


def test_all_cohorts_by_year_keys():
    book = _book()
    cohorts = book.all_cohorts_by_year()
    assert 2019 in cohorts
    assert 2020 in cohorts
    assert 2022 in cohorts


def test_best_cohort_none_when_empty():
    book = CLVCohortBook()
    assert book.best_cohort_by_year() is None


def test_worst_cohort_none_when_empty():
    book = CLVCohortBook()
    assert book.worst_cohort_by_year() is None


def test_portfolio_summary_empty_book():
    book = CLVCohortBook()
    s = book.portfolio_summary()
    assert s['total_customers'] == 0


def test_portfolio_summary_total_clv():
    book = _book()
    s = book.portfolio_summary()
    expected = 320 + 280 + 450 + 1200 + (-50)
    assert s['total_clv_gbp'] == pytest.approx(expected)
