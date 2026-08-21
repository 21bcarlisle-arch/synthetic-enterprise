"""Tests for the generic wall envelope (`interface/contracts/wall_envelope.py`)
-- the shared WallRequest/WallResponse shape every seam crossing specialises.
"""
from __future__ import annotations

import datetime as dt

import pytest

from interface.contracts.wall_envelope import (
    ErrorDetail,
    WallInterim,
    WallNotification,
    WallRequest,
    WallResponse,
    WallStatus,
)


def test_wall_request_roundtrip():
    req = WallRequest(
        correlation_id="corr-1",
        request_type="payment_collection.v1",
        schema_version=1,
        as_of=dt.datetime(2026, 7, 1, 9, 0),
        emitted_at=dt.datetime(2026, 7, 1, 9, 0),
        payload={"account_id": "A1"},
    )
    assert req.correlation_id == "corr-1"
    assert req.request_type == "payment_collection.v1"
    assert req.schema_version == 1
    assert req.payload == {"account_id": "A1"}


def test_wall_request_is_frozen():
    req = WallRequest(
        correlation_id="corr-1",
        request_type="t",
        schema_version=1,
        as_of=dt.datetime(2026, 7, 1),
        emitted_at=dt.datetime(2026, 7, 1),
        payload=None,
    )
    with pytest.raises(Exception):
        req.correlation_id = "corr-2"  # type: ignore[misc]


def test_wall_response_ok_roundtrip():
    resp = WallResponse(
        correlation_id="corr-1",
        status=WallStatus.OK,
        schema_version=1,
        observed_at=dt.datetime(2026, 7, 4, 10, 0),
        valid_time=dt.date(2026, 7, 1),
        payload={"amount_gbp": 42.0},
    )
    assert resp.status == WallStatus.OK
    assert resp.payload == {"amount_gbp": 42.0}
    assert resp.error is None


def test_wall_response_not_knowable_yet_carries_no_payload():
    resp = WallResponse(
        correlation_id="corr-1",
        status=WallStatus.NOT_KNOWABLE_YET,
        schema_version=1,
        observed_at=dt.datetime(2026, 7, 1, 9, 0),
        valid_time=None,
        payload=None,
    )
    assert resp.payload is None


def test_wall_response_ok_without_payload_rejected():
    """FAIL-CLOSED: an OK status without a payload is a malformed envelope --
    caught at construction, not at some later, quieter read site."""
    with pytest.raises(ValueError):
        WallResponse(
            correlation_id="corr-1",
            status=WallStatus.OK,
            schema_version=1,
            observed_at=dt.datetime(2026, 7, 1),
            valid_time=None,
            payload=None,
        )


def test_wall_response_non_ok_with_payload_rejected():
    """FAIL-CLOSED: a non-OK status must never carry a payload -- this is
    exactly the leak shape a NOT_KNOWABLE_YET / TIMEOUT / ERROR response must
    never have (a payload smuggled in alongside a status saying there isn't
    one yet)."""
    with pytest.raises(ValueError):
        WallResponse(
            correlation_id="corr-1",
            status=WallStatus.NOT_KNOWABLE_YET,
            schema_version=1,
            observed_at=dt.datetime(2026, 7, 1),
            valid_time=None,
            payload={"leak": "should not be here"},
        )


def test_wall_response_error_requires_error_detail():
    with pytest.raises(ValueError):
        WallResponse(
            correlation_id="corr-1",
            status=WallStatus.ERROR,
            schema_version=1,
            observed_at=dt.datetime(2026, 7, 1),
            valid_time=None,
            payload=None,
            error=None,
        )


def test_wall_response_error_roundtrip():
    resp = WallResponse(
        correlation_id="corr-1",
        status=WallStatus.ERROR,
        schema_version=1,
        observed_at=dt.datetime(2026, 7, 1),
        valid_time=None,
        payload=None,
        error=ErrorDetail(code="RAIL_UNAVAILABLE", message="Bacs feed unreachable"),
    )
    assert resp.error.code == "RAIL_UNAVAILABLE"


def test_wall_response_is_frozen():
    resp = WallResponse(
        correlation_id="corr-1",
        status=WallStatus.OK,
        schema_version=1,
        observed_at=dt.datetime(2026, 7, 1),
        valid_time=None,
        payload=1,
    )
    with pytest.raises(Exception):
        resp.status = WallStatus.ERROR  # type: ignore[misc]


# ---------------------------------------------------------------------------
# WallNotification -- UNSOLICITED INBOUND (blind review Q2, atom EP6).
#
# The primitive exists to make three things structurally impossible, so the
# tests are mostly REFUSALS: a contract that can only be used correctly is the
# whole reason this is a third type rather than a flag on WallResponse.
# ---------------------------------------------------------------------------

def _notif(**over):
    kw = dict(
        notification_id="ADDACS-1",
        notification_type="addacs_advice",
        schema_version=1,
        sender="BACS-BUREAU-01",
        sequence=0,
        observed_at=dt.datetime(2026, 7, 1),
        valid_time=None,
        payload={"mandate": "M1"},
    )
    kw.update(over)
    return WallNotification(**kw)


def test_wall_notification_carries_no_correlation_id():
    """THE point of the type. A correlation id would re-assert the link to a
    request that was never sent -- the blind review's named fail shape."""
    assert not hasattr(_notif(), "correlation_id")


def test_wall_notification_carries_no_status():
    """A status answers a question. Nobody asked, so there is no question for
    this message to be honestly unable to answer."""
    assert not hasattr(_notif(), "status")


def test_a_payloadless_notification_is_REFUSED():
    """The mirror of WallResponse(OK) needing a payload: an unsolicited
    message that says nothing is not a message."""
    with pytest.raises(ValueError, match="must carry a payload"):
        _notif(payload=None)


def test_a_notification_with_no_id_is_REFUSED():
    """The id is the idempotency key for an at-least-once stream. Without it a
    redelivery is undetectable, which is C-S2 lost at construction."""
    with pytest.raises(ValueError, match="notification_id"):
        _notif(notification_id="")


def test_a_notification_with_no_sender_is_REFUSED():
    """`sequence` is a position in ONE counterparty's stream; unsendered, two
    feeds' numbering would be compared and invent gaps out of nothing."""
    with pytest.raises(ValueError, match="must name its sender"):
        _notif(sender="")


def test_a_negative_sequence_is_REFUSED():
    with pytest.raises(ValueError, match="non-negative"):
        _notif(sequence=-1)


def test_wall_notification_is_frozen():
    n = _notif()
    with pytest.raises(Exception):
        n.sequence = 5  # type: ignore[misc]


def test_sequence_zero_is_LEGAL_and_not_confused_with_absent():
    """NULL CONTROL for the refusals above: 0 is a real first position. A
    guard written as `if not self.sequence` would reject the first message of
    every stream, so the success case is asserted rather than assumed."""
    assert _notif(sequence=0).sequence == 0


# ── THE INTERIM LEG (blind review Q3) ──────────────────────────────────────────


def _interim(**over):
    kwargs = dict(
        correlation_id="INV-1",
        leg=2,
        interim_type="bacs_input_report",
        schema_version=2,
        observed_at=dt.datetime(2026, 3, 3, 6, 0),
        payload={"submission_ref": "SUB-1"},
    )
    kwargs.update(over)
    return WallInterim(**kwargs)


def test_an_interim_carries_no_status_so_it_cannot_resolve_anything():
    """THE LOAD-BEARING ABSENCE. A status is a resolution; give an interim one
    and nothing distinguishes it from a `WallResponse`, so the third leg
    collapses back into the second and the conversation is two legs again under
    a longer name. Asserted structurally rather than trusted to a docstring."""
    assert not hasattr(_interim(), "status")


def test_an_interim_carries_a_correlation_id_and_a_notification_does_not():
    """The two new primitives are told apart by exactly this. An interim is BY
    DEFINITION about a request that was made; a message with no request behind
    it is unsolicited, and giving it a correlation id is the Q2 fail shape
    ("a response to a synthetic request") in mirror image."""
    assert _interim().correlation_id == "INV-1"
    assert not hasattr(_notif(), "correlation_id")


def test_an_interim_with_no_payload_is_REFUSED():
    """An in-progress report that reports nothing is not a leg -- and unlike a
    response it has no status to be honestly empty behind."""
    with pytest.raises(ValueError, match="must carry a payload"):
        _interim(payload=None)


def test_an_interim_with_no_correlation_id_is_REFUSED():
    with pytest.raises(ValueError, match="must carry a correlation_id"):
        _interim(correlation_id="")


@pytest.mark.parametrize("leg", [1, 0, -1, -7])
def test_an_interim_can_never_be_LEG_ONE_or_earlier(leg):
    """Leg 1 is the `WallRequest`. This is the structural claim the whole
    ordering rests on, so it is refused at construction rather than documented:
    an interim that could call itself leg 1 could describe an exchange nobody
    started."""
    with pytest.raises(ValueError, match="leg must be >= 2"):
        _interim(leg=leg)


def test_leg_TWO_is_LEGAL_and_so_is_a_much_later_leg():
    """NULL CONTROL for the refusals above: the boundary value is the one the
    rule is most likely to be wrong about, and a long conversation must stay
    expressible or the primitive caps at three legs."""
    assert _interim(leg=2).leg == 2
    assert _interim(leg=9).leg == 9


def test_wall_interim_is_frozen():
    i = _interim()
    with pytest.raises(Exception):
        i.leg = 5  # type: ignore[misc]
