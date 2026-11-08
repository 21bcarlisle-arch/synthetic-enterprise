"""Phase 115: Supplier switching request tracking tests."""

from datetime import date, timedelta

from company.billing.switching import SwitchRequest, SwitchingBook


def _req(ref, direction="gain", status="pending"):
    return SwitchRequest(
        reference=ref, customer_id="C1", commodity="electricity",
        direction=direction, mpan_or_mprn="1012345678901",
        requested_transfer_date="2026-07-10",
        submitted_date="2026-06-26",
        status=status,
    )


def test_record_and_pending():
    b = SwitchingBook()
    b.record(_req("SW-001"))
    assert len(b.pending()) == 1


def test_complete_sets_status():
    b = SwitchingBook()
    b.record(_req("SW-001"))
    assert b.complete("SW-001", "2026-07-10") is True
    assert b.pending() == []


def test_completed_gains():
    b = SwitchingBook()
    b.record(_req("SW-001", "gain"))
    b.complete("SW-001", "2026-07-10")
    assert len(b.completed_gains()) == 1


def test_completed_losses():
    b = SwitchingBook()
    b.record(_req("SW-002", "loss"))
    b.complete("SW-002", "2026-07-10")
    assert len(b.completed_losses()) == 1


def test_pending_losses():
    b = SwitchingBook()
    b.record(_req("SW-003", "loss"))
    assert len(b.pending_losses()) == 1


def test_object_to_pending():
    """object_to() requires the request still be within its live 14-day
    objection window (is_objectable checks date.today() against
    submitted_date + 14 days) -- a hardcoded submitted_date here would
    silently expire as real wall-clock time passes (found live: this test
    started failing on 2026-07-11 against a submitted_date of 2026-06-26,
    used since the test was written). submitted_date is computed relative
    to today instead, so the window is always open."""
    b = SwitchingBook()
    b.record(SwitchRequest(
        reference="SW-004", customer_id="C1", commodity="electricity",
        direction="gain", mpan_or_mprn="1012345678901",
        requested_transfer_date="2026-07-10",
        submitted_date=(date.today() - timedelta(days=1)).isoformat(),
    ))
    assert b.object_to("SW-004", "debt outstanding") is True
    assert b._requests[0].status == "objected"


def test_object_to_already_completed_fails():
    b = SwitchingBook()
    b.record(_req("SW-005", status="completed"))
    assert b.object_to("SW-005", "too late") is False


def test_withdraw():
    b = SwitchingBook()
    b.record(_req("SW-006"))
    assert b.withdraw("SW-006") is True
    assert b._requests[0].status == "withdrawn"


def test_switching_summary():
    b = SwitchingBook()
    b.record(_req("SW-007", "gain"))
    b.record(_req("SW-008", "loss"))
    b.record(_req("SW-009", "gain"))
    b.complete("SW-007", "2026-07-10")
    b.complete("SW-008", "2026-07-10")
    s = b.switching_summary()
    assert s["gains_completed"] == 1
    assert s["losses_completed"] == 1
    assert s["net_completed"] == 0
    assert s["gains_pending"] == 1


def test_net_positive_when_gaining():
    b = SwitchingBook()
    b.record(_req("SW-010", "gain"))
    b.record(_req("SW-011", "gain"))
    b.complete("SW-010", "2026-07-10")
    b.complete("SW-011", "2026-07-10")
    assert b.switching_summary()["net_completed"] == 2


def test_objection_deadline_14_days():
    r = _req("SW-012")
    assert r.objection_deadline == "2026-07-10"

import pytest

# --- Phase LI depth tests ---

def test_customer_id_stored():
    r = _req("SW-100")
    assert r.customer_id == "C1"


def test_mpan_stored():
    r = _req("SW-101")
    assert r.mpan_or_mprn == "1012345678901"


def test_requested_transfer_date_stored():
    r = _req("SW-102")
    assert r.requested_transfer_date == "2026-07-10"


def test_submitted_date_stored():
    r = _req("SW-103")
    assert r.submitted_date == "2026-06-26"


def test_status_default_pending():
    r = _req("SW-104")
    assert r.status == "pending"


def test_objection_reason_default_empty():
    r = _req("SW-105")
    assert r.objection_reason == ""


def test_completed_date_default_empty():
    r = _req("SW-106")
    assert r.completed_date == ""


def test_gains_method():
    b = SwitchingBook()
    b.record(_req("SW-107", "gain"))
    b.record(_req("SW-108", "loss"))
    assert len(b.gains()) == 1
    assert len(b.losses()) == 1


def test_losses_method():
    b = SwitchingBook()
    b.record(_req("SW-109", "loss"))
    b.record(_req("SW-110", "loss"))
    assert len(b.losses()) == 2


def test_summary_total():
    b = SwitchingBook()
    b.record(_req("SW-111", "gain"))
    b.record(_req("SW-112", "loss"))
    assert b.switching_summary()["total"] == 2
