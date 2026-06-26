import pytest
from company.finance.margin_call_book import (
    MarginCallBook, MarginCallEvent, MarginCallStatus
)


def _call(cid="MC001", date="2022-09-15", cpty="BARCLAYS", contract="FWD001",
          init=100_000.0, var=800_000.0, deadline="2022-09-16"):
    return MarginCallEvent(
        call_id=cid, call_date=date, counterparty=cpty, contract_id=contract,
        initial_margin_gbp=init, variation_margin_gbp=var, settlement_deadline=deadline
    )


def test_total_margin_required():
    c = _call(init=100_000.0, var=800_000.0)
    assert abs(c.total_margin_required_gbp - 900_000.0) < 0.01


def test_is_stress_event():
    c = _call(var=800_000.0)
    assert c.is_stress_event is True


def test_not_stress_event():
    c = _call(var=100_000.0)
    assert c.is_stress_event is False


def test_is_settled_initial():
    c = _call()
    assert c.is_settled is False


def test_settle_call():
    book = MarginCallBook()
    book.record_call(_call())
    settled = book.settle_call("MC001")
    assert settled is not None
    assert settled.is_settled is True
    assert len(book.outstanding_calls()) == 0


def test_settle_unknown_call():
    book = MarginCallBook()
    assert book.settle_call("UNKNOWN") is None


def test_total_outstanding():
    book = MarginCallBook()
    book.record_call(_call(cid="MC001", init=100_000.0, var=200_000.0))
    book.record_call(_call(cid="MC002", init=50_000.0, var=100_000.0))
    book.settle_call("MC001")
    assert abs(book.total_outstanding_gbp() - 150_000.0) < 0.01


def test_headroom():
    book = MarginCallBook(credit_facility_gbp=5_000_000.0)
    book.record_call(_call(init=200_000.0, var=300_000.0))
    assert abs(book.headroom_gbp() - 4_500_000.0) < 0.01


def test_is_liquidity_stressed():
    book = MarginCallBook(credit_facility_gbp=1_000_000.0)
    book.record_call(_call(init=400_000.0, var=500_000.0))
    assert book.is_liquidity_stressed() is True


def test_margin_call_summary_keys():
    book = MarginCallBook()
    book.record_call(_call())
    s = book.margin_call_summary()
    for k in ("total_calls", "outstanding_calls", "total_outstanding_gbp",
               "credit_facility_gbp", "headroom_gbp", "is_liquidity_stressed", "stress_events"):
        assert k in s


def test_stress_events():
    book = MarginCallBook()
    book.record_call(_call(cid="MC001", var=1_000_000.0))
    book.record_call(_call(cid="MC002", var=100_000.0))
    assert len(book.stress_events()) == 1
