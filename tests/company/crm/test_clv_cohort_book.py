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
