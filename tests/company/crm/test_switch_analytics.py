import datetime as dt
import pytest
from company.crm.switch_analytics import (
    SwitchDirection, SwitchStatus, SwitchEvent, SwitchAnalytics
)


def _book():
    return SwitchAnalytics('SUPPLIER_A')


def test_record_gain():
    book = _book()
    ev = book.record('1200012345', 'C001', SwitchDirection.GAIN,
                     'SUPPLIER_B', 'SUPPLIER_A', dt.date(2022, 3, 1))
    assert ev.direction == SwitchDirection.GAIN
    assert ev.status == SwitchStatus.INITIATED


def test_complete_switch():
    book = _book()
    ev = book.record('1200012345', 'C001', SwitchDirection.GAIN,
                     'SUPPLIER_B', 'SUPPLIER_A', dt.date(2022, 3, 1))
    done = book.complete(ev.event_id, dt.date(2022, 3, 6))
    assert done.is_completed is True
    assert done.days_to_complete == 5


def test_object_blocks_completion():
    book = _book()
    ev = book.record('1200099999', None, SwitchDirection.LOSS,
                     'SUPPLIER_A', 'SUPPLIER_C', dt.date(2022, 4, 1))
    objected = book.object(ev.event_id)
    assert objected.status == SwitchStatus.OBJECTED


def test_mark_erroneous():
    book = _book()
    ev = book.record('1200055555', None, SwitchDirection.LOSS,
                     'SUPPLIER_A', 'SUPPLIER_D', dt.date(2022, 5, 1))
    err = book.mark_erroneous(ev.event_id)
    assert err.erroneous_transfer is True
    assert len(book.erroneous_transfers_in_year(2022)) == 1


def test_gains_and_losses_in_year():
    book = _book()
    book.record('A', 'C001', SwitchDirection.GAIN, 'SB', 'SA', dt.date(2022, 1, 1))
    book.record('B', 'C002', SwitchDirection.GAIN, 'SC', 'SA', dt.date(2022, 3, 1))
    book.record('C', 'C003', SwitchDirection.LOSS, 'SA', 'SD', dt.date(2022, 6, 1))
    assert len(book.gains_in_year(2022)) == 2
    assert len(book.losses_in_year(2022)) == 1


def test_net_customer_change():
    book = _book()
    book.record('A', 'C001', SwitchDirection.GAIN, 'SB', 'SA', dt.date(2022, 1, 1))
    book.record('B', 'C002', SwitchDirection.GAIN, 'SC', 'SA', dt.date(2022, 3, 1))
    book.record('C', 'C003', SwitchDirection.LOSS, 'SA', 'SD', dt.date(2022, 6, 1))
    assert book.net_customer_change(2022) == 1


def test_avg_days_to_complete():
    book = _book()
    ev1 = book.record('A', 'C001', SwitchDirection.GAIN, 'SB', 'SA', dt.date(2022, 1, 1))
    ev2 = book.record('B', 'C002', SwitchDirection.GAIN, 'SC', 'SA', dt.date(2022, 2, 1))
    book.complete(ev1.event_id, dt.date(2022, 1, 6))
    book.complete(ev2.event_id, dt.date(2022, 2, 8))
    assert book.avg_days_to_complete(2022) == pytest.approx(6.0)


def test_annual_summary_keys():
    book = _book()
    book.record('A', 'C001', SwitchDirection.GAIN, 'SB', 'SA', dt.date(2022, 1, 1))
    s = book.annual_summary(2022)
    assert 'gains' in s
    assert 'losses' in s
    assert 'net' in s
    assert 'erroneous_transfers' in s
    assert 'avg_days_to_complete' in s
