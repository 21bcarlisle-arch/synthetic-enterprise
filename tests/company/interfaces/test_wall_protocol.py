"""Tests for the company's wire protocol for the wall envelope (atom EP6).

The subject is `company/interfaces/wall_protocol.py`. Its single load-bearing
claim is that **absence is never agreement**: a message that does not state its
`schema_version` is refused, rather than silently credited with whatever version
this process happens to be compiled against.

R15 governs how that claim is tested. A control counts as evidence only if a
MUTATION proves it fires on its own named defect, so the defect is built here
and run beside the control (`test_mutant_decoder_...`) rather than described.
Two further R15 patterns are checked by construction:

  TAUTOLOGY   -- the refusal fixtures below are hand-authored dicts, never
                 `encode_request` output, so the decoder is not being checked
                 against its own arithmetic. And the wire field sets are checked
                 against `dataclasses.fields` of the envelope, an independent
                 source, so a field added to the contract cannot silently fail
                 to cross.
  FAIL-OPEN   -- `test_refuses_...` sweeps the empty/null/malformed inputs a
                 permissive decoder waves through.
"""
from __future__ import annotations

import dataclasses
import datetime as dt
import json

import pytest

from company.interfaces.wall_protocol import (
    REQUEST_WIRE_FIELDS,
    RESPONSE_WIRE_FIELDS,
    SUPPORTED_SCHEMA_VERSIONS,
    WallProtocolError,
    decode_request,
    decode_response,
    encode_request,
    encode_response,
)
from interface.contracts.wall_envelope import (
    ErrorDetail,
    WallRequest,
    WallResponse,
    WallStatus,
)

AS_OF = dt.datetime(2024, 3, 1, 12, 0, 0)
EMITTED = dt.datetime(2024, 3, 1, 12, 0, 5)
OBSERVED = dt.datetime(2024, 3, 4, 9, 30, 0)

# A payload codec of the shape a real crossing supplies: the payload is the
# crossing's business, opaque to the protocol.
IDENTITY = dict


def _dictish(value):
    return value


def _wire_request(**overrides) -> dict:
    """A hand-authored request on the wire. NOT produced by `encode_request` --
    the refusal tests must not be checked against the encoder's own arithmetic
    (R15 TAUTOLOGY), so this fixture is the independent sample."""
    message = {
        "correlation_id": "corr-1",
        "request_type": "meter_read.fetch",
        "schema_version": 1,
        "as_of": "2024-03-01T12:00:00",
        "emitted_at": "2024-03-01T12:00:05",
        "payload": {"mpan": "1234"},
    }
    message.update(overrides)
    return message


def _wire_response(**overrides) -> dict:
    message = {
        "correlation_id": "corr-1",
        "status": "OK",
        "schema_version": 1,
        "observed_at": "2024-03-04T09:30:00",
        "valid_time": "2024-03-02",
        "payload": {"kwh": 12.5},
        "error": None,
    }
    message.update(overrides)
    return message


# ---------------------------------------------------------------------------
# the vintage stamp reaches the wire -- the 9-of-9 requirement of EP7..EP15
# ---------------------------------------------------------------------------


def test_the_vintage_stamp_is_on_the_wire_for_both_shapes():
    request = WallRequest(
        correlation_id="corr-1",
        request_type="meter_read.fetch",
        schema_version=1,
        as_of=AS_OF,
        emitted_at=EMITTED,
        payload={"mpan": "1234"},
    )
    response = WallResponse(
        correlation_id="corr-1",
        status=WallStatus.OK,
        schema_version=1,
        observed_at=OBSERVED,
        valid_time=dt.date(2024, 3, 2),
        payload={"kwh": 12.5},
    )
    assert encode_request(request, encode_payload=_dictish)["schema_version"] == 1
    assert encode_response(response, encode_payload=_dictish)["schema_version"] == 1


def test_both_bitemporal_coordinates_cross_so_a_restatement_is_expressible():
    """A restatement is a later `observed_at` for the same `valid_time`. That is
    only expressible if BOTH reach the receiver -- so a wire that dropped either
    would make the bitemporal contract unusable at the far end."""
    first = WallResponse(
        correlation_id="corr-1",
        status=WallStatus.OK,
        schema_version=1,
        observed_at=dt.datetime(2024, 3, 4, 9, 30),
        valid_time=dt.date(2024, 3, 2),
        payload={"kwh": 12.5},
    )
    restated = dataclasses.replace(
        first, observed_at=dt.datetime(2024, 3, 20, 9, 30), payload={"kwh": 13.0}
    )
    a = encode_response(first, encode_payload=_dictish)
    b = encode_response(restated, encode_payload=_dictish)
    assert a["valid_time"] == b["valid_time"] == "2024-03-02"
    assert a["observed_at"] < b["observed_at"]


# ---------------------------------------------------------------------------
# THE NAMED DEFECT, and its mutation
# ---------------------------------------------------------------------------


def test_a_request_without_its_version_is_refused():
    wire = _wire_request()
    del wire["schema_version"]
    with pytest.raises(WallProtocolError) as caught:
        decode_request(wire, decode_payload=_dictish)
    assert caught.value.reason == "MISSING_FIELD"


def test_a_response_without_its_version_is_refused():
    wire = _wire_response()
    del wire["schema_version"]
    with pytest.raises(WallProtocolError) as caught:
        decode_response(wire, decode_payload=_dictish)
    assert caught.value.reason == "MISSING_FIELD"


def test_null_control_the_same_message_with_its_version_decodes():
    """The NULL CONTROL for the two tests above: the sample moves (the field is
    restored), the law does not. Without this, `raises` could be firing on
    anything else wrong with the fixture."""
    assert decode_request(_wire_request(), decode_payload=_dictish).schema_version == 1
    assert decode_response(_wire_response(), decode_payload=_dictish).schema_version == 1


def test_mutant_decoder_with_a_defaulting_read_silently_relabels_an_old_message():
    """THE MUTATION (R15). The defect this module exists to refuse, built here and
    run on the same bytes as the control.

    The mutant is the sibling pattern shipped in `tools/*_port.py`:
    `entry.get("schema_version", <the reader's own current constant>)`. Give it a
    v1-era message that predates the version field and it reports the message as
    the reader's version -- a silent relabel, indistinguishable from a message
    that genuinely agreed. The shipped decoder refuses the identical bytes.

    If the MISSING_FIELD guard were removed from `_require_exact_fields`, the
    second half of this test goes green and the module's whole claim is void.
    """
    readers_own_current_version = 2
    unstamped = _wire_request()
    del unstamped["schema_version"]

    # the mutant: fails open, and cannot tell absence from agreement
    mutant_version = unstamped.get("schema_version", readers_own_current_version)
    assert mutant_version == readers_own_current_version
    stamped_v2 = _wire_request(schema_version=readers_own_current_version)
    assert mutant_version == stamped_v2.get("schema_version", readers_own_current_version)

    # the control: the two are not the same message, and one of them does not cross
    with pytest.raises(WallProtocolError) as caught:
        decode_request(unstamped, decode_payload=_dictish)
    assert caught.value.reason == "MISSING_FIELD"


def test_an_unknown_dialect_is_refused_distinguishably_from_an_absent_one():
    """"You did not say what you speak" and "you speak a dialect I do not know"
    are different failures needing different repairs, so they carry different
    reasons rather than one generic parse error."""
    unknown = max(SUPPORTED_SCHEMA_VERSIONS) + 1
    with pytest.raises(WallProtocolError) as caught:
        decode_request(_wire_request(schema_version=unknown), decode_payload=_dictish)
    assert caught.value.reason == "UNSUPPORTED_VERSION"

    missing = _wire_request()
    del missing["schema_version"]
    with pytest.raises(WallProtocolError) as other:
        decode_request(missing, decode_payload=_dictish)
    assert other.value.reason != caught.value.reason


# ---------------------------------------------------------------------------
# FAIL-OPEN sweep
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("wire", [None, {}, "", 0, [], "{}"])
def test_refuses_the_empty_and_malformed_inputs_a_permissive_decoder_waves_through(wire):
    with pytest.raises(WallProtocolError):
        decode_request(wire, decode_payload=_dictish)
    with pytest.raises(WallProtocolError):
        decode_response(wire, decode_payload=_dictish)


@pytest.mark.parametrize(
    "overrides,reason",
    [
        ({"correlation_id": ""}, "MALFORMED_FIELD"),
        ({"correlation_id": None}, "MALFORMED_FIELD"),
        ({"schema_version": "1"}, "MALFORMED_FIELD"),
        ({"schema_version": True}, "MALFORMED_FIELD"),
        ({"as_of": "not-a-timestamp"}, "MALFORMED_FIELD"),
        ({"as_of": None}, "MALFORMED_FIELD"),
        ({"request_type": ""}, "MALFORMED_FIELD"),
    ],
)
def test_a_present_but_unusable_field_is_refused(overrides, reason):
    with pytest.raises(WallProtocolError) as caught:
        decode_request(_wire_request(**overrides), decode_payload=_dictish)
    assert caught.value.reason == reason


def test_a_boolean_version_is_not_read_as_version_one():
    """`True == 1` in Python, so a decoder that only checked membership in the
    supported set would accept `True` as v1. The int check is what stops it."""
    assert True == 1  # noqa: E712 -- the premise of the test, stated
    with pytest.raises(WallProtocolError) as caught:
        decode_request(_wire_request(schema_version=True), decode_payload=_dictish)
    assert caught.value.reason == "MALFORMED_FIELD"


def test_an_unrecognised_field_is_refused_rather_than_silently_tolerated():
    with pytest.raises(WallProtocolError) as caught:
        decode_request(_wire_request(extra_field="surprise"), decode_payload=_dictish)
    assert caught.value.reason == "UNKNOWN_FIELD"


def test_an_explicit_null_and_an_absent_key_are_different_facts():
    """`valid_time: None` is a legitimate answer (not every payload is about a
    dated fact). An absent `valid_time` KEY is a message that never said. The
    decoder accepts the first and refuses the second."""
    assert decode_response(
        _wire_response(valid_time=None), decode_payload=_dictish
    ).valid_time is None

    absent = _wire_response()
    del absent["valid_time"]
    with pytest.raises(WallProtocolError) as caught:
        decode_response(absent, decode_payload=_dictish)
    assert caught.value.reason == "MISSING_FIELD"


# ---------------------------------------------------------------------------
# the envelope's own invariants survive the crossing
# ---------------------------------------------------------------------------


def test_a_wire_message_violating_the_envelope_never_becomes_an_object():
    """An OK with no payload, and a TIMEOUT carrying one, are refused as
    CONTRACT_VIOLATION -- one exception type at the seam, and no half-built
    object reaches company logic."""
    for overrides in (
        {"status": "OK", "payload": None},
        {"status": "TIMEOUT", "payload": {"kwh": 12.5}},
        {"status": "ERROR", "payload": None, "error": None},
    ):
        with pytest.raises(WallProtocolError) as caught:
            decode_response(_wire_response(**overrides), decode_payload=_dictish)
        assert caught.value.reason == "CONTRACT_VIOLATION", overrides


def test_an_unknown_status_is_refused():
    with pytest.raises(WallProtocolError) as caught:
        decode_response(_wire_response(status="PROBABLY_FINE"), decode_payload=_dictish)
    assert caught.value.reason == "MALFORMED_FIELD"


# ---------------------------------------------------------------------------
# indistinguishability: the round trip is lossless for every status
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "status,payload,error,valid_time",
    [
        (WallStatus.OK, {"kwh": 12.5}, None, dt.date(2024, 3, 2)),
        (WallStatus.OK, {"kwh": 0.0}, None, None),
        (WallStatus.TIMEOUT, None, None, dt.date(2024, 3, 2)),
        (WallStatus.NOT_KNOWABLE_YET, None, None, None),
        (WallStatus.ERROR, None, ErrorDetail(code="E_UPSTREAM", message="bureau down"), None),
    ],
)
def test_a_response_survives_the_round_trip_unchanged_for_every_status(
    status, payload, error, valid_time
):
    """The company must be unable to tell a message that crossed a wire from one
    handed over in-process. That is only true if the crossing is lossless, and it
    must hold for the honest non-answers -- NOT_KNOWABLE_YET and TIMEOUT are the
    statuses a real counterparty produces and a mock one is tempted to skip."""
    original = WallResponse(
        correlation_id="corr-1",
        status=status,
        schema_version=1,
        observed_at=OBSERVED,
        valid_time=valid_time,
        payload=payload,
        error=error,
    )
    wire = encode_response(original, encode_payload=_dictish)
    assert json.loads(json.dumps(wire)) == wire, "the wire form must survive real transport"
    assert decode_response(wire, decode_payload=_dictish) == original


def test_a_request_survives_the_round_trip_unchanged():
    original = WallRequest(
        correlation_id="corr-1",
        request_type="meter_read.fetch",
        schema_version=1,
        as_of=AS_OF,
        emitted_at=EMITTED,
        payload={"mpan": "1234"},
    )
    wire = encode_request(original, encode_payload=_dictish)
    assert json.loads(json.dumps(wire)) == wire
    assert decode_request(wire, decode_payload=_dictish) == original


def test_as_of_and_emitted_at_stay_distinct_across_the_wire():
    """WallRequest never conflates "when I asked" with "as of when I want the
    answer" -- a reconciliation job replaying old requests has them far apart, and
    a wire that collapsed them would silently lift the Blindfold."""
    original = WallRequest(
        correlation_id="corr-1",
        request_type="meter_read.fetch",
        schema_version=1,
        as_of=dt.datetime(2022, 1, 1, 0, 0),
        emitted_at=dt.datetime(2024, 3, 1, 12, 0),
        payload={},
    )
    decoded = decode_request(
        encode_request(original, encode_payload=_dictish), decode_payload=_dictish
    )
    assert decoded.as_of == original.as_of
    assert decoded.emitted_at == original.emitted_at
    assert decoded.as_of != decoded.emitted_at


# ---------------------------------------------------------------------------
# independence: the wire field sets are checked against the CONTRACT
# ---------------------------------------------------------------------------


def test_the_wire_carries_every_field_the_envelope_declares():
    """The anti-drift control, and the reason it is not a tautology: the expected
    sets come from `dataclasses.fields` on the shared contract, not from this
    module's own constants. Add a field to `WallRequest`/`WallResponse` and this
    reds, instead of the new field silently never crossing -- which is exactly
    how `schema_version` came to be populated at all ten construction sites and
    present in zero published bytes."""
    assert REQUEST_WIRE_FIELDS == {f.name for f in dataclasses.fields(WallRequest)}
    assert RESPONSE_WIRE_FIELDS == {f.name for f in dataclasses.fields(WallResponse)}


def test_the_encoders_emit_exactly_the_declared_field_set():
    request = WallRequest(
        correlation_id="corr-1",
        request_type="t",
        schema_version=1,
        as_of=AS_OF,
        emitted_at=EMITTED,
        payload={},
    )
    response = WallResponse(
        correlation_id="corr-1",
        status=WallStatus.NOT_KNOWABLE_YET,
        schema_version=1,
        observed_at=OBSERVED,
        valid_time=None,
        payload=None,
    )
    assert set(encode_request(request, encode_payload=_dictish)) == REQUEST_WIRE_FIELDS
    assert set(encode_response(response, encode_payload=_dictish)) == RESPONSE_WIRE_FIELDS


def test_the_payload_codec_has_no_default_so_nothing_serialises_by_accident():
    """A codec that can serialise anything is a codec that can leak anything, so
    `encode_payload` is a required keyword argument with no fallback."""
    request = WallRequest(
        correlation_id="corr-1",
        request_type="t",
        schema_version=1,
        as_of=AS_OF,
        emitted_at=EMITTED,
        payload=object(),
    )
    with pytest.raises(TypeError):
        encode_request(request)  # type: ignore[call-arg]


def test_a_non_envelope_is_not_encodable():
    with pytest.raises(WallProtocolError) as caught:
        encode_request({"correlation_id": "corr-1"}, encode_payload=_dictish)  # type: ignore[arg-type]
    assert caught.value.reason == "NOT_A_MESSAGE"
