import datetime as dt
import pytest
from company.crm.renewals_book import (
    RenewalOutcome, OfferType, RenewalRecord, RenewalsBook
)


def _book():
    book = RenewalsBook()
    book.add('C001', 'residential', dt.date(2022, 3, 31),
             RenewalOutcome.RENEWED, OfferType.SAME_TARIFF, 28.5, 12, 42, True)
    book.add('C002', 'residential', dt.date(2022, 3, 31),
             RenewalOutcome.SWITCHED_AWAY, OfferType.SAME_TARIFF, 28.5, None, 42, False)
    book.add('C003', 'residential', dt.date(2022, 6, 30),
             RenewalOutcome.RENEWED, OfferType.LOYALTY_DISCOUNT, 26.0, 12, 42, False)
    book.add('C004', 'residential', dt.date(2022, 6, 30),
             RenewalOutcome.LAPSED, None, None, None, 42, False)
    book.add('C005', 'sme', dt.date(2022, 9, 30),
             RenewalOutcome.RENEWED, OfferType.PRICE_MATCH, 30.0, 24, 42, True)
    return book


def test_renewal_rate():
    book = _book()
    rate = book.renewal_rate(2022)
    assert rate == pytest.approx(60.0)


def test_lapse_rate():
    book = _book()
    assert book.lapse_rate(2022) == pytest.approx(40.0)


def test_renewal_rate_by_segment():
    book = _book()
    resi_rate = book.renewal_rate(2022, segment='residential')
    assert resi_rate == pytest.approx(50.0)


def test_outbound_lift():
    book = _book()
    lift = book.outbound_lift(2022)
    assert lift is not None
    assert isinstance(lift, float)


def test_by_offer_type():
    book = _book()
    by_type = book.by_offer_type(2022)
    assert 'same_tariff' in by_type
    assert by_type['same_tariff']['total'] == 2
    assert by_type['same_tariff']['renewal_rate'] == pytest.approx(50.0)


def test_accepted_property():
    r = RenewalRecord(
        customer_id='C001', segment='residential',
        term_end_date=dt.date(2022, 3, 31),
        outcome=RenewalOutcome.RENEWED,
        offer_type=OfferType.SAME_TARIFF,
        offered_rate_ppm=28.5, new_term_months=12,
        days_notice_given=42
    )
    assert r.accepted is True


def test_moved_out_excluded_from_rate():
    book = RenewalsBook()
    book.add('C001', 'residential', dt.date(2022, 6, 30), RenewalOutcome.MOVED_OUT)
    book.add('C002', 'residential', dt.date(2022, 6, 30), RenewalOutcome.RENEWED)
    rate = book.renewal_rate(2022)
    assert rate == pytest.approx(100.0)


def test_annual_summary_keys():
    book = _book()
    s = book.annual_summary(2022)
    assert 'renewal_rate_pct' in s
    assert 'lapse_rate_pct' in s
    assert 'outbound_lift_pct' in s
    assert 'by_offer_type' in s
