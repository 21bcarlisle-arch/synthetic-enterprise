"""Phase 115: Supplier switching request tracking tests."""

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
    b = SwitchingBook()
    b.record(_req("SW-004"))
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
