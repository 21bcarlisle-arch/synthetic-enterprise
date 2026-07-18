"""Tests for the generic wall envelope (`interface/contracts/wall_envelope.py`)
-- the shared WallRequest/WallResponse shape every seam crossing specialises.
"""
from __future__ import annotations

import datetime as dt

import pytest

from interface.contracts.wall_envelope import (
    ErrorDetail,
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
