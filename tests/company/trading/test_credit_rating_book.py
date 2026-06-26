import datetime as dt
import pytest
from company.trading.credit_rating_book import (
    CreditRating, is_investment_grade, CounterpartyCreditProfile, CreditRatingBook
)


def test_investment_grade_bbb():
    assert is_investment_grade(CreditRating.BBB)


def test_not_investment_grade_bb():
    assert not is_investment_grade(CreditRating.BB)


def test_aaa_pd():
    p = CounterpartyCreditProfile(
        'CP001', 'Shell Gas Trading', CreditRating.AAA, 'S&P',
        dt.date(2022, 1, 1), 5_000_000.0
    )
    assert p.pd_pct == pytest.approx(0.01)
    assert p.score == 10
    assert p.is_investment_grade


def test_register_and_get():
    book = CreditRatingBook()
    p = book.register('CP002', 'BP Energy', CreditRating.A, 'Moodys',
                       dt.date(2022, 6, 1), 2_000_000.0)
    assert book.get('CP002') is p


def test_record_exposure():
    book = CreditRatingBook()
    book.register('CP003', 'Centrica', CreditRating.BBB, 'S&P',
                   dt.date(2022, 1, 1), 1_000_000.0)
    book.record_exposure('CP003', dt.date(2022, 3, 1), 300_000.0, 'gas_forward')
    assert book.total_exposure_gbp('CP003') == pytest.approx(300_000.0)


def test_within_limit():
    book = CreditRatingBook()
    book.register('CP004', 'TraderCo', CreditRating.BB, 'Fitch',
                   dt.date(2022, 1, 1), 500_000.0)
    book.record_exposure('CP004', dt.date(2022, 1, 15), 300_000.0, 'elec_forward')
    assert book.is_within_limit('CP004', 150_000.0)  # 300k + 150k = 450k < 500k
    assert not book.is_within_limit('CP004', 300_000.0)  # 600k > 500k


def test_sub_investment_grade_list():
    book = CreditRatingBook()
    book.register('CP005', 'SmallCo', CreditRating.B, 'S&P',
                   dt.date(2022, 1, 1), 50_000.0)
    book.register('CP006', 'BigCo', CreditRating.AA, 'Moodys',
                   dt.date(2022, 1, 1), 2_000_000.0)
    sub_ig = book.sub_investment_grade_counterparties()
    assert len(sub_ig) == 1
    assert sub_ig[0].counterparty_id == 'CP005'


def test_credit_summary():
    book = CreditRatingBook()
    book.register('CP007', 'Alpha', CreditRating.A, 'S&P',
                   dt.date(2022, 1, 1), 1_000_000.0)
    book.register('CP008', 'Beta', CreditRating.CCC, 'Fitch',
                   dt.date(2022, 1, 1), 100_000.0)
    book.record_exposure('CP007', dt.date(2022, 6, 1), 500_000.0, 'gas')
    s = book.credit_summary()
    assert s['total_counterparties'] == 2
    assert s['investment_grade'] == 1
    assert s['total_exposure_gbp'] == pytest.approx(500_000.0)
