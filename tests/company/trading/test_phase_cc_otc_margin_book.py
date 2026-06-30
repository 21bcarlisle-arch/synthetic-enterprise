"""Phase CC: OTC Margin Book tests."""
import pytest
from datetime import date
from company.trading.otc_margin_book import (
    OTCMarginBook, VariationMarginCall, MarginCallDirection, MarginCallStatus
)


def _book():
    return OTCMarginBook()


def _call(direction=MarginCallDirection.CALL, status=MarginCallStatus.MET,
          mtm=100000, cpty="Vitol", yr=2022, settled_yr=2022):
    b = _book()
    b.record_call("MC001", date(yr, 3, 1), cpty, 5000, mtm, direction, status,
                  date(settled_yr, 3, 2) if status == MarginCallStatus.MET else None)
    return b


# 1. Cash impact negative for settled CALL
def test_call_negative_cash_impact():
    b = _call()
    assert b.total_cash_impact_gbp < 0


# 2. Cash impact positive for settled RETURN
def test_return_positive_cash_impact():
    b = _call(direction=MarginCallDirection.RETURN)
    assert b.total_cash_impact_gbp > 0


# 3. Pending calls not counted in settled cash impact
def test_pending_not_in_settled():
    b = _call(status=MarginCallStatus.PENDING, settled_yr=None)
    assert b.total_cash_impact_gbp == 0.0


# 4. Pending outflow sums pending CALL amounts
def test_pending_outflow():
    b = _call(status=MarginCallStatus.PENDING)
    assert b.total_pending_outflow_gbp == 100_000


# 5. settle_call changes status to MET
def test_settle_call():
    b = _book()
    b.record_call("MC001", date(2022, 3, 1), "Vitol", 5000, 100000,
                  MarginCallDirection.CALL, MarginCallStatus.PENDING)
    b.settle_call("MC001", date(2022, 3, 2))
    assert b.pending_calls == []


# 6. calls_by_counterparty sums per counterparty
def test_calls_by_counterparty():
    b = _book()
    b.record_call("MC001", date(2022, 3, 1), "Vitol", 5000, 100000,
                  MarginCallDirection.CALL, MarginCallStatus.MET, date(2022, 3, 2))
    b.record_call("MC002", date(2022, 3, 5), "Vitol", 3000, 50000,
                  MarginCallDirection.CALL, MarginCallStatus.MET, date(2022, 3, 6))
    cpty = b.calls_by_counterparty
    assert "Vitol" in cpty
    assert abs(cpty["Vitol"] - (-150_000)) < 1


# 7. net_cash_for_year filters correctly
def test_net_cash_for_year():
    b = _book()
    b.record_call("MC001", date(2022, 3, 1), "Vitol", 5000, 250000,
                  MarginCallDirection.CALL, MarginCallStatus.MET, date(2022, 3, 2))
    b.record_call("MC002", date(2023, 3, 1), "Vitol", 5000, 100000,
                  MarginCallDirection.RETURN, MarginCallStatus.MET, date(2023, 3, 2))
    assert abs(b.net_cash_for_year(2022) - (-250000)) < 1
    assert abs(b.net_cash_for_year(2023) - 100000) < 1


# 8. calls_for_year filters by year
def test_calls_for_year():
    b = _book()
    b.record_call("MC001", date(2022, 3, 1), "Vitol", 5000, 100000,
                  MarginCallDirection.CALL, MarginCallStatus.MET, date(2022, 3, 2))
    b.record_call("MC002", date(2023, 5, 1), "Vitol", 3000, 50000,
                  MarginCallDirection.CALL, MarginCallStatus.MET, date(2023, 5, 2))
    assert len(b.calls_for_year(2022)) == 1
    assert len(b.calls_for_year(2023)) == 1


# 9. is_call_on_company property
def test_is_call_on_company():
    b = _book()
    c = b.record_call("MC001", date(2022, 3, 1), "Vitol", 5000, 100000,
                      MarginCallDirection.CALL, MarginCallStatus.MET, date(2022, 3, 2))
    assert c.is_call_on_company is True
    r = b.record_call("MC002", date(2022, 3, 5), "Vitol", 5000, 50000,
                      MarginCallDirection.RETURN, MarginCallStatus.MET, date(2022, 3, 6))
    assert r.is_call_on_company is False


# 10. is_settled returns True for MET status
def test_is_settled():
    b = _book()
    c = b.record_call("MC001", date(2022, 3, 1), "Vitol", 5000, 100000,
                      MarginCallDirection.CALL, MarginCallStatus.MET, date(2022, 3, 2))
    assert c.is_settled is True
    p = b.record_call("MC002", date(2022, 3, 3), "Vitol", 5000, 50000,
                      MarginCallDirection.CALL, MarginCallStatus.PENDING)
    assert p.is_settled is False


# 11. margin_book_summary contains key fields
def test_margin_book_summary():
    b = _call()
    summary = b.margin_book_summary()
    assert "Total calls" in summary
    assert "cash impact" in summary


# 12. Total pending outflow is zero when all settled
def test_no_pending_outflow_when_settled():
    b = _call()  # all settled
    assert b.total_pending_outflow_gbp == 0.0
