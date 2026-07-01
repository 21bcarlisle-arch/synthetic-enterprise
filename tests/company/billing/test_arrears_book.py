import datetime as dt
import pytest
from company.billing.arrears_book import (
    ArrearsStage, ArrearsCase, ArrearsBook
)

D = dt.date


def test_open_case():
    book = ArrearsBook()
    c = book.open_case('C001', 250.0, D(2023, 3, 1))
    assert c.stage == ArrearsStage.DD_FAILED
    assert c.is_open
    assert c.outstanding_gbp == 250.0


def test_advance_stage():
    book = ArrearsBook()
    c = book.open_case('C002', 350.0, D(2023, 3, 1))
    book.advance_stage(c.case_id, ArrearsStage.FIRST_NOTICE, D(2023, 3, 15))
    assert c.stage == ArrearsStage.FIRST_NOTICE


def test_advance_terminal_stage_raises():
    book = ArrearsBook()
    c = book.open_case('C003', 100.0, D(2023, 3, 1))
    book.resolve(c.case_id, D(2023, 4, 1))
    with pytest.raises(ValueError):
        book.advance_stage(c.case_id, ArrearsStage.FIRST_NOTICE, D(2023, 4, 2))


def test_record_recovery():
    book = ArrearsBook()
    c = book.open_case('C004', 500.0, D(2023, 3, 1))
    book.record_recovery(c.case_id, 200.0)
    assert c.outstanding_gbp == pytest.approx(300.0)


def test_resolve_case():
    book = ArrearsBook()
    c = book.open_case('C005', 200.0, D(2023, 3, 1))
    book.resolve(c.case_id, D(2023, 5, 1))
    assert c.stage == ArrearsStage.RESOLVED
    assert not c.is_open


def test_write_off():
    book = ArrearsBook()
    c = book.open_case('C006', 800.0, D(2022, 6, 1))
    book.write_off(c.case_id, D(2023, 1, 1))
    assert c.stage == ArrearsStage.WRITTEN_OFF
    assert not c.is_open


def test_total_outstanding():
    book = ArrearsBook()
    c1 = book.open_case('C007', 400.0, D(2023, 3, 1))
    c2 = book.open_case('C008', 600.0, D(2023, 3, 1))
    book.record_recovery(c1.case_id, 100.0)
    assert book.total_arrears_outstanding_gbp() == pytest.approx(900.0)


def test_open_cases_excludes_resolved():
    book = ArrearsBook()
    c1 = book.open_case('C009', 200.0, D(2023, 3, 1))
    c2 = book.open_case('C010', 300.0, D(2023, 3, 1))
    book.resolve(c1.case_id, D(2023, 4, 1))
    assert len(book.open_cases()) == 1


def test_annual_summary():
    book = ArrearsBook()
    c1 = book.open_case('C011', 500.0, D(2023, 3, 1))
    c2 = book.open_case('C012', 300.0, D(2023, 3, 1))
    book.write_off(c2.case_id, D(2023, 12, 1))
    s = book.annual_summary()
    assert s['total_cases'] == 2
    assert s['open_cases'] == 1
    assert 'dd_failed' in s['by_stage']


def test_case_id_sequential():
    book = ArrearsBook()
    c1 = book.open_case('C001', 100.0, D(2023, 1, 1))
    c2 = book.open_case('C002', 200.0, D(2023, 1, 5))
    assert c1.case_id == 'ARR-0001'
    assert c2.case_id == 'ARR-0002'


def test_cases_for_customer_filter():
    book = ArrearsBook()
    c1 = book.open_case('C001', 200.0, D(2023, 3, 1))
    c2 = book.open_case('C002', 300.0, D(2023, 3, 1))
    assert len(book.cases_for_customer('C001')) == 1
    assert book.cases_for_customer('C001')[0].case_id == c1.case_id


def test_cases_at_stage_filter():
    book = ArrearsBook()
    c1 = book.open_case('C001', 200.0, D(2023, 1, 1))
    book.advance_stage(c1.case_id, ArrearsStage.FIRST_NOTICE, D(2023, 1, 15))
    book.open_case('C002', 300.0, D(2023, 2, 1))
    first_notice = book.cases_at_stage(ArrearsStage.FIRST_NOTICE)
    assert len(first_notice) == 1
    assert first_notice[0].case_id == c1.case_id


def test_outstanding_capped_at_zero():
    book = ArrearsBook()
    c = book.open_case('C001', 100.0, D(2023, 1, 1))
    book.record_recovery(c.case_id, 150.0)
    assert c.outstanding_gbp == pytest.approx(0.0)


def test_days_open_none_when_not_resolved():
    book = ArrearsBook()
    c = book.open_case('C001', 200.0, D(2023, 1, 1))
    assert c.days_open is None


def test_days_open_when_resolved():
    book = ArrearsBook()
    c = book.open_case('C001', 200.0, D(2023, 1, 1))
    book.resolve(c.case_id, D(2023, 4, 1))
    assert c.days_open == (D(2023, 4, 1) - D(2023, 1, 1)).days


def test_vulnerable_flag_stored():
    book = ArrearsBook()
    c = book.open_case('C001', 200.0, D(2023, 1, 1), is_vulnerable=True)
    assert c.is_vulnerable is True


def test_total_outstanding_excludes_written_off():
    book = ArrearsBook()
    c1 = book.open_case('C001', 500.0, D(2023, 1, 1))
    c2 = book.open_case('C002', 300.0, D(2023, 2, 1))
    book.write_off(c2.case_id, D(2023, 12, 1))
    # Only c1 is open; c2 written-off excluded from outstanding
    assert book.total_arrears_outstanding_gbp() == pytest.approx(500.0)


def test_write_off_then_advance_raises():
    book = ArrearsBook()
    c = book.open_case('C001', 200.0, D(2023, 1, 1))
    book.write_off(c.case_id, D(2023, 6, 1))
    with pytest.raises(ValueError):
        book.advance_stage(c.case_id, ArrearsStage.FIRST_NOTICE, D(2023, 7, 1))


def test_stage_date_stored():
    book = ArrearsBook()
    c = book.open_case('C001', 200.0, D(2023, 1, 1))
    stage_date = D(2023, 2, 1)
    book.advance_stage(c.case_id, ArrearsStage.FIRST_NOTICE, stage_date)
    assert c.stage_date == stage_date
