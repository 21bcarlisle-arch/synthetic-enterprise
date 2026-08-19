"""The company's WIRE protocol for the wall envelope (atom EP6_wall_protocol_typing).

`interface/contracts/wall_envelope.py` (atom W4_4) already gives the wall its
typed, versioned message SHAPE -- `WallRequest[P]` / `WallResponse[R]`, with
`schema_version` a required field on both, `correlation_id` the sole link
between a request and a response that is its own event in time, and a
`__post_init__` that refuses a malformed envelope at construction.

What did not exist, and is the whole of this module, is the WIRE. Every
envelope in this repository is an in-process Python object handed straight to
its consumer; nothing ever serialised one. The 2026-08-18 path trace recorded
the consequence precisely: population of `schema_version` is complete and
structurally guaranteed at all ten construction sites, and the value has never
left the process -- "not a switch that is off, a wire that was never built".
A version field that is never transmitted cannot be negotiated, and version
negotiation is the property EP6 exists to provide.

WHY THIS LIVES ON THE COMPANY SIDE. The atom's claim is that "a mock
counterparty and a real one are indistinguishable to the company". Whether that
holds is decided at the point where the company DECODES what arrived, because
that is the only place a real endpoint and an in-process call differ in a way
the company can observe. A real counterparty hands over bytes; today's SIM hands
over an object. Put the codec here and both arrive as the same typed envelope,
having passed the same refusals -- which is what "indistinguishable" has to mean
if it is to be testable rather than hoped for. The envelope stays shared in
`interface/`; this module reads it and never widens it.

WHAT THE COMPANY LEARNS BY DECODING: nothing it did not already receive. This
is transport, not an observable. The payload is opaque to it -- callers supply
their own crossing's payload codec as an argument -- so no SIM internal can
enter through this module that was not already inside the envelope handed to it.

--------------------------------------------------------------------------
THE ONE RULE THIS MODULE ENFORCES: ABSENCE IS NEVER AGREEMENT.
--------------------------------------------------------------------------

A wire message must state every field of its envelope, including its nulls, and
must state its `schema_version`. A missing key is REFUSED -- never defaulted,
never inferred, never filled in from what this process happens to believe today.

That refusal is aimed at a named, measured defect in the sibling pattern rather
than at a hypothetical. `tools/*_port.py`'s `from_log_entry` reads
`entry.get("schema_version", SCHEMA_VERSION)` -- the reader's OWN module
constant, at read time. Today that is harmless because one version exists. The
first bump to "2.0" silently relabels every archived v1.0 entry as 2.0, because
an absent field and an agreeing field are the same bytes. A version field that
cannot disagree is not a version field, and a decoder that supplies the answer
it is checking is R15's FAIL-OPEN pattern in its purest form.

So: an absent key and an explicit null are different facts here, and this
decoder refuses to conflate them. Unknown keys are refused for the mirror-image
reason -- if a later schema adds a field, the version number is how a decoder
finds out, not silent tolerance of bytes it does not understand.

SCOPE, deliberately narrow (SIMPLICITY GUARD; the atom's own origin_note
forbids a protocol cathedral by name). No registry, no plugin lookup, no
transport, no retry policy, no new message types. Four functions and a
refusal. The payload codec is a function ARGUMENT, not a registered type, so
adding a crossing requires no edit here.
"""
from __future__ import annotations

import datetime as dt
from typing import Any, Callable, Mapping, Optional, TypeVar

from interface.contracts.wall_envelope import (
    ErrorDetail,
    WallRequest,
    WallResponse,
    WallStatus,
)

__all__ = [
    "SUPPORTED_SCHEMA_VERSIONS",
    "REQUEST_WIRE_FIELDS",
    "RESPONSE_WIRE_FIELDS",
    "WallProtocolError",
    "encode_request",
    "decode_request",
    "encode_response",
    "decode_response",
]

P = TypeVar("P")
R = TypeVar("R")

#: Envelope schema versions this company build can read. An `schema_version`
#: outside this set is refused as UNSUPPORTED_VERSION -- distinguishably from
#: an absent one, because "you speak a dialect I do not know" and "you did not
#: say what you speak" are different failures and call for different repairs.
SUPPORTED_SCHEMA_VERSIONS: frozenset[int] = frozenset({1})

#: The exact key set of a request on the wire. Derived from nothing -- it is
#: stated here and asserted against the dataclass in the test suite, so a field
#: added to the envelope reds the suite instead of silently never crossing.
REQUEST_WIRE_FIELDS: frozenset[str] = frozenset(
    {"correlation_id", "request_type", "schema_version", "as_of", "emitted_at", "payload"}
)

#: The exact key set of a response on the wire. `payload`, `valid_time` and
#: `error` are frequently null and their keys are still REQUIRED: see the
#: module docstring on absence-is-never-agreement.
RESPONSE_WIRE_FIELDS: frozenset[str] = frozenset(
    {
        "correlation_id",
        "status",
        "schema_version",
        "observed_at",
        "valid_time",
        "payload",
        "error",
    }
)


class WallProtocolError(ValueError):
    """A message that did not cross. Carries a machine-readable ``reason`` so a
    caller can tell a malformed counterparty apart from an unknown dialect
    without parsing prose, and so tests can assert WHICH refusal fired rather
    than merely that something raised.

    Reasons:
      ``NOT_A_MESSAGE``        -- the wire value is not a mapping at all.
      ``MISSING_FIELD``        -- a required key is absent (incl. schema_version).
      ``UNKNOWN_FIELD``        -- a key this schema version does not define.
      ``MALFORMED_FIELD``      -- a key is present with an unusable value.
      ``UNSUPPORTED_VERSION``  -- a version outside SUPPORTED_SCHEMA_VERSIONS.
      ``CONTRACT_VIOLATION``   -- well-formed on the wire, but the envelope's own
                                 invariants reject it (e.g. an OK with no
                                 payload). Raised so a bad message NEVER reaches
                                 company logic as a half-built object.
    """

    def __init__(self, reason: str, message: str) -> None:
        super().__init__(f"{reason}: {message}")
        self.reason = reason


# ---------------------------------------------------------------------------
# field-level codecs. Each refuses rather than coerces.
# ---------------------------------------------------------------------------


def _require_mapping(wire: Any, what: str) -> Mapping[str, Any]:
    if not isinstance(wire, Mapping):
        raise WallProtocolError(
            "NOT_A_MESSAGE", f"{what} must be a mapping, got {type(wire).__name__}"
        )
    return wire


def _require_exact_fields(wire: Mapping[str, Any], expected: frozenset[str], what: str) -> None:
    present = frozenset(wire)
    missing = sorted(expected - present)
    if missing:
        raise WallProtocolError(
            "MISSING_FIELD",
            f"{what} omits required field(s) {missing} -- an absent field is never "
            "read as agreement with this process's own defaults",
        )
    unknown = sorted(present - expected)
    if unknown:
        raise WallProtocolError(
            "UNKNOWN_FIELD",
            f"{what} carries field(s) {unknown} that schema version(s) "
            f"{sorted(SUPPORTED_SCHEMA_VERSIONS)} do not define",
        )


def _decode_schema_version(raw: Any) -> int:
    # bool is an int subclass; a True here is a malformed version, not v1.
    if not isinstance(raw, int) or isinstance(raw, bool):
        raise WallProtocolError(
            "MALFORMED_FIELD", f"schema_version must be an int, got {raw!r}"
        )
    if raw not in SUPPORTED_SCHEMA_VERSIONS:
        raise WallProtocolError(
            "UNSUPPORTED_VERSION",
            f"schema_version {raw} is not one of {sorted(SUPPORTED_SCHEMA_VERSIONS)}",
        )
    return raw


def _decode_correlation_id(raw: Any) -> str:
    if not isinstance(raw, str) or not raw:
        raise WallProtocolError(
            "MALFORMED_FIELD",
            f"correlation_id must be a non-empty str, got {raw!r} -- it is both the "
            "idempotency key and the only link to the response",
        )
    return raw


def _decode_str(raw: Any, field: str) -> str:
    if not isinstance(raw, str) or not raw:
        raise WallProtocolError(
            "MALFORMED_FIELD", f"{field} must be a non-empty str, got {raw!r}"
        )
    return raw


def _encode_datetime(value: dt.datetime, field: str) -> str:
    if not isinstance(value, dt.datetime):
        raise WallProtocolError(
            "MALFORMED_FIELD", f"{field} must be a datetime, got {type(value).__name__}"
        )
    return value.isoformat()


def _decode_datetime(raw: Any, field: str) -> dt.datetime:
    if not isinstance(raw, str):
        raise WallProtocolError(
            "MALFORMED_FIELD", f"{field} must be an ISO-8601 str, got {raw!r}"
        )
    try:
        return dt.datetime.fromisoformat(raw)
    except ValueError as exc:
        raise WallProtocolError("MALFORMED_FIELD", f"{field} is not ISO-8601: {raw!r}") from exc


def _encode_date(value: Optional[dt.date], field: str) -> Optional[str]:
    if value is None:
        return None
    # datetime is a date subclass; valid_time is a DATE and must not smuggle a time.
    if not isinstance(value, dt.date) or isinstance(value, dt.datetime):
        raise WallProtocolError(
            "MALFORMED_FIELD", f"{field} must be a date or None, got {type(value).__name__}"
        )
    return value.isoformat()


def _decode_date(raw: Any, field: str) -> Optional[dt.date]:
    if raw is None:
        return None
    if not isinstance(raw, str):
        raise WallProtocolError(
            "MALFORMED_FIELD", f"{field} must be an ISO-8601 date str or null, got {raw!r}"
        )
    try:
        return dt.date.fromisoformat(raw)
    except ValueError as exc:
        raise WallProtocolError("MALFORMED_FIELD", f"{field} is not an ISO date: {raw!r}") from exc


def _decode_status(raw: Any) -> WallStatus:
    if not isinstance(raw, str):
        raise WallProtocolError("MALFORMED_FIELD", f"status must be a str, got {raw!r}")
    try:
        return WallStatus(raw)
    except ValueError as exc:
        raise WallProtocolError(
            "MALFORMED_FIELD",
            f"status {raw!r} is not one of {[s.value for s in WallStatus]}",
        ) from exc


def _encode_error(error: Optional[ErrorDetail]) -> Optional[dict[str, str]]:
    if error is None:
        return None
    if not isinstance(error, ErrorDetail):
        raise WallProtocolError(
            "MALFORMED_FIELD", f"error must be an ErrorDetail or None, got {type(error).__name__}"
        )
    return {"code": error.code, "message": error.message}


def _decode_error(raw: Any) -> Optional[ErrorDetail]:
    if raw is None:
        return None
    wire = _require_mapping(raw, "error")
    _require_exact_fields(wire, frozenset({"code", "message"}), "error")
    return ErrorDetail(
        code=_decode_str(wire["code"], "error.code"),
        message=_decode_str(wire["message"], "error.message"),
    )


# ---------------------------------------------------------------------------
# the four public codecs
# ---------------------------------------------------------------------------


def encode_request(
    request: WallRequest[P], *, encode_payload: Callable[[P], Any]
) -> dict[str, Any]:
    """Serialise a request onto the wire, vintage stamp included, always.

    ``encode_payload`` is REQUIRED and has no default: every crossing states how
    its own payload crosses. There is deliberately no fallback that would
    stringify or `dataclasses.asdict` an unknown payload, because a codec that
    can serialise anything is a codec that can leak anything.
    """
    if not isinstance(request, WallRequest):
        raise WallProtocolError(
            "NOT_A_MESSAGE", f"expected a WallRequest, got {type(request).__name__}"
        )
    return {
        "correlation_id": request.correlation_id,
        "request_type": request.request_type,
        "schema_version": request.schema_version,
        "as_of": _encode_datetime(request.as_of, "as_of"),
        "emitted_at": _encode_datetime(request.emitted_at, "emitted_at"),
        "payload": encode_payload(request.payload),
    }


def decode_request(
    wire: Any, *, decode_payload: Callable[[Any], P]
) -> WallRequest[P]:
    """Parse a request off the wire, or refuse it. Never defaults a field."""
    message = _require_mapping(wire, "request")
    _require_exact_fields(message, REQUEST_WIRE_FIELDS, "request")
    version = _decode_schema_version(message["schema_version"])
    try:
        return WallRequest(
            correlation_id=_decode_correlation_id(message["correlation_id"]),
            request_type=_decode_str(message["request_type"], "request_type"),
            schema_version=version,
            as_of=_decode_datetime(message["as_of"], "as_of"),
            emitted_at=_decode_datetime(message["emitted_at"], "emitted_at"),
            payload=decode_payload(message["payload"]),
        )
    except ValueError as exc:
        if isinstance(exc, WallProtocolError):
            raise
        raise WallProtocolError("CONTRACT_VIOLATION", str(exc)) from exc


def encode_response(
    response: WallResponse[R], *, encode_payload: Callable[[R], Any]
) -> dict[str, Any]:
    """Serialise a response onto the wire, vintage stamp included, always.

    Both bitemporal coordinates cross: ``observed_at`` (when this answer became
    known) and ``valid_time`` (what period it is about). A restatement is a new
    message with a later ``observed_at`` for the same ``valid_time``; that is
    only expressible if both actually reach the receiver, which is why neither
    is optional on the wire.
    """
    if not isinstance(response, WallResponse):
        raise WallProtocolError(
            "NOT_A_MESSAGE", f"expected a WallResponse, got {type(response).__name__}"
        )
    return {
        "correlation_id": response.correlation_id,
        "status": response.status.value,
        "schema_version": response.schema_version,
        "observed_at": _encode_datetime(response.observed_at, "observed_at"),
        "valid_time": _encode_date(response.valid_time, "valid_time"),
        "payload": None if response.payload is None else encode_payload(response.payload),
        "error": _encode_error(response.error),
    }


def decode_response(
    wire: Any, *, decode_payload: Callable[[Any], R]
) -> WallResponse[R]:
    """Parse a response off the wire, or refuse it.

    A message that is well-formed but violates the envelope's own invariants
    (an OK carrying no payload, a TIMEOUT carrying one) is re-raised as
    CONTRACT_VIOLATION rather than escaping as a bare ValueError, so a caller
    has exactly one exception type to handle at the seam and a malformed
    counterparty can never hand company logic a half-built object.
    """
    message = _require_mapping(wire, "response")
    _require_exact_fields(message, RESPONSE_WIRE_FIELDS, "response")
    version = _decode_schema_version(message["schema_version"])
    raw_payload = message["payload"]
    try:
        return WallResponse(
            correlation_id=_decode_correlation_id(message["correlation_id"]),
            status=_decode_status(message["status"]),
            schema_version=version,
            observed_at=_decode_datetime(message["observed_at"], "observed_at"),
            valid_time=_decode_date(message["valid_time"], "valid_time"),
            payload=None if raw_payload is None else decode_payload(raw_payload),
            error=_decode_error(message["error"]),
        )
    except ValueError as exc:
        if isinstance(exc, WallProtocolError):
            raise
        raise WallProtocolError("CONTRACT_VIOLATION", str(exc)) from exc
