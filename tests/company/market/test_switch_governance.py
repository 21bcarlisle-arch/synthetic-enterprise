import datetime as dt
import pytest
from company.market.switch_governance import (
    COOLING_OFF_DAYS, OBJECTION_WINDOW_DAYS,
    ObjectionReason, ObjectionOutcome, ErroneousTransferStatus,
    CoolingOffCancellation, SwitchObjection, ErroneousTransfer,
    SwitchGovernanceBook
)


def test_cooling_off_within():
    c = CoolingOffCancellation('C001', 'MPAN001', dt.date(2022, 10, 1), dt.date(2022, 10, 10))
    assert c.days_after_sale == 9
    assert c.within_cooling_off


def test_cooling_off_exceeded():
    c = CoolingOffCancellation('C001', 'MPAN001', dt.date(2022, 10, 1), dt.date(2022, 10, 20))
    assert c.days_after_sale == 19
    assert not c.within_cooling_off


def test_raise_and_resolve_objection():
    book = SwitchGovernanceBook()
    obj = book.raise_objection('MPAN001', 'SUPP01', dt.date(2022, 10, 1),
                                dt.date(2022, 10, 10), ObjectionReason.DEBT)
    assert obj.within_objection_window
    assert not obj.is_resolved
    book.resolve_objection(obj.objection_id, ObjectionOutcome.UPHELD, dt.date(2022, 10, 15))
    assert obj.is_resolved
    assert obj.outcome == ObjectionOutcome.UPHELD


def test_late_objection_outside_window():
    obj = SwitchObjection('OBJ-001', 'MPAN001', 'S1',
                           dt.date(2022, 10, 1), dt.date(2022, 11, 1),
                           ObjectionReason.CONTRACT_IN_TERM)
    assert not obj.within_objection_window


def test_report_and_resolve_et():
    book = SwitchGovernanceBook()
    et = book.report_et('MPAN001', 'LOSING_SUPP', 'GAINING_SUPP',
                         dt.date(2022, 10, 1), dt.date(2022, 10, 8))
    assert et.days_to_report == 7
    assert not et.is_resolved
    book.resolve_et(et.et_id, ErroneousTransferStatus.CUSTOMER_RETURNED, dt.date(2022, 10, 30))
    assert et.is_resolved
    assert len(book.open_ets()) == 0


def test_open_objections():
    book = SwitchGovernanceBook()
    book.raise_objection('MPAN001', 'S1', dt.date(2022, 10, 1), dt.date(2022, 10, 5),
                          ObjectionReason.DEBT)
    book.raise_objection('MPAN002', 'S1', dt.date(2022, 10, 1), dt.date(2022, 10, 5),
                          ObjectionReason.CONTRACT_IN_TERM)
    objs = book.open_objections()
    assert len(objs) == 2


def test_annual_summary():
    book = SwitchGovernanceBook()
    book.record_cancellation('C001', 'MPAN001', dt.date(2022, 10, 1), dt.date(2022, 10, 8))
    book.record_cancellation('C002', 'MPAN002', dt.date(2022, 10, 1), dt.date(2022, 10, 20))
    obj = book.raise_objection('MPAN003', 'S1', dt.date(2022, 10, 1), dt.date(2022, 10, 10),
                                ObjectionReason.DEBT)
    book.resolve_objection(obj.objection_id, ObjectionOutcome.UPHELD, dt.date(2022, 10, 20))
    book.report_et('MPAN004', 'L', 'G', dt.date(2022, 10, 1), dt.date(2022, 10, 7))
    s = book.annual_summary(2022)
    assert s['cooling_off_cancellations'] == 2
    assert s['cooling_off_rate_pct'] == pytest.approx(50.0)
    assert s['objections_upheld'] == 1
    assert s['erroneous_transfers'] == 1
    assert s['ets_resolved'] == 0
