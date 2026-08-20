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
import enum
import json
import typing

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


# ===========================================================================
# THE FIRST MIGRATED CROSSING (2026-08-19, EP6 level 1 -> 2)
#
# Everything above tests the codec in isolation, which is why the atom stood at
# L1 "built and DARK": the only callers were its own tests. This section is the
# codec carrying a REAL crossing -- the live payment triad, which runs inside
# `simulation/run_phase2b.py` once per run -- and it is what an L2 "genuine
# artefacts, happy path" claim rests on.
#
# THE CLAIM UNDER TEST is the atom's own sentence: "a mock counterparty and a
# real one are indistinguishable to the company." Made falsifiable, that is
# `test_the_wire_fed_company_and_the_object_fed_company_believe_the_same_thing`
# -- two identical companies, one handed objects and one handed JSON bytes,
# reaching the same belief.
#
# INDEPENDENCE, and why it is real here rather than asserted. The encoder lives
# in `simulation/payment_seam_adapter.py` and the decoder in
# `company/billing/payment_observation_consumer.py`. Neither imports the other
# (proven below); the sim side may not import `company.*` at all. They agree
# only through `interface/contracts/payment_observable_seam.py` -- the way a
# real supplier agrees with a real bank: via the published schema. So this
# round-trip is not the decoder checked against its own arithmetic.
# ===========================================================================

from company.billing.payment_observation_consumer import (  # noqa: E402
    PaymentObservationConsumer,
    decode_observable_payload,
)
from interface.contracts.payment_observable_seam import (  # noqa: E402
    OBSERVABLE_RESPONSE_PAYLOAD_TYPES,
    PaymentRail,
    RemittanceAdvice,
)
from simulation.payment_seam_adapter import (  # noqa: E402
    PARTICIPANT_CREDENTIAL,
    PARTICIPANT_ID,
    SeamEncodeError,
    encode_observable_payload,
    encode_wall_response,
    frame_wire_message,
)

_VALUE_DATE = dt.date(2024, 3, 11)
_ADVICE = RemittanceAdvice(
    bank_reference="INV-9001",
    account_id="ACC-9001",
    amount_gbp=142.75,
    rail=PaymentRail.BACS_DIRECT_DEBIT,
    value_date=_VALUE_DATE,
)
_OK_RESPONSE = WallResponse(
    correlation_id="INV-9001",
    status=WallStatus.OK,
    schema_version=1,
    observed_at=dt.datetime(2024, 3, 11, 6, 0),
    valid_time=_VALUE_DATE,
    payload=_ADVICE,
)


def _through_real_json(response):
    """Encode with the counterparty's encoder and put the result through actual
    JSON, so what the company decodes is bytes it could have received off a
    socket -- not a dict that merely looks like one."""
    return json.loads(json.dumps(encode_wall_response(response)))


def _framed_json(response):
    """The same, FRAMED by the counterparty (atom EP6, pass 39) -- the shape
    that actually reaches `observe_wire`, participant identity and all."""
    return json.loads(json.dumps(frame_wire_message(encode_wall_response(response))))


def _decode_from_wire(wire):
    return decode_response(wire, decode_payload=decode_observable_payload)


def test_the_vintage_stamp_survives_real_json_and_is_read_from_the_message():
    """`schema_version` is populated at ten construction sites and, until this
    crossing was migrated, had never left a process -- "not a switch that is
    off, a wire that was never built". This asserts both halves: the stamp is IN
    the serialised bytes, and the value the company ends up with was READ from
    those bytes rather than supplied by the reader's own constant."""
    raw = json.dumps(encode_wall_response(_OK_RESPONSE))
    assert '"schema_version"' in raw
    assert _decode_from_wire(json.loads(raw)).schema_version == 1


def test_the_round_trip_is_lossless_through_the_two_independent_sides():
    assert _decode_from_wire(_through_real_json(_OK_RESPONSE)) == _OK_RESPONSE


def test_the_honest_non_answers_cross_too():
    """A `NOT_KNOWABLE_YET` is the answer a real counterparty gives and a mock is
    tempted to skip; it carries no payload by envelope invariant, and the wire
    must still state that null rather than omit the key."""
    unresolved = WallResponse(
        correlation_id="INV-9002",
        status=WallStatus.NOT_KNOWABLE_YET,
        schema_version=1,
        observed_at=dt.datetime(2024, 3, 11, 6, 0),
        valid_time=None,
        payload=None,
    )
    wire = _through_real_json(unresolved)
    assert wire["payload"] is None and wire["valid_time"] is None
    assert set(wire) == set(RESPONSE_WIRE_FIELDS)
    assert _decode_from_wire(wire) == unresolved


def test_the_wire_fed_company_and_the_object_fed_company_believe_the_same_thing():
    """THE ATOM'S CLAIM. Two identical consumers see the same observation, one
    as an in-process object (the mock) and one as JSON bytes (the real
    counterparty). If the transport were distinguishable to the company, these
    two snapshots would differ."""
    object_fed = PaymentObservationConsumer()
    wire_fed = PaymentObservationConsumer()

    assert object_fed.observe(_OK_RESPONSE) is True
    assert wire_fed.observe_wire(_framed_json(_OK_RESPONSE)) is True

    assert wire_fed.snapshot(_ADVICE.account_id) == object_fed.snapshot(_ADVICE.account_id)


def test_idempotency_survives_the_transport_swap():
    """`correlation_id` is the idempotency key, and it has to keep working when
    the same fact is re-DELIVERED as bytes -- a real feed redelivers."""
    consumer = PaymentObservationConsumer()
    wire = _framed_json(_OK_RESPONSE)
    assert consumer.observe_wire(wire) is True
    assert consumer.observe_wire(json.loads(json.dumps(wire))) is False


def test_the_two_sides_are_independent_code():
    """The agreement above must come from the published contract, not from one
    side importing the other -- otherwise the round-trip is a tautology."""
    import ast
    import inspect

    import simulation.payment_seam_adapter as adapter

    imported = set()
    for node in ast.walk(ast.parse(inspect.getsource(adapter))):
        if isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
        elif isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
    assert not [m for m in imported if m.split(".")[0] in {"company", "saas"}]
    assert "interface.contracts.payment_observable_seam" in imported


def test_every_payload_type_the_contract_defines_can_cross():
    """A decoder covering the three types this crossing happens to emit today
    would be a hole the day a fourth is emitted. The subject is the CONTRACT's
    own enumeration, so adding a payload type to the seam reds this test until
    it crosses."""
    assert len(OBSERVABLE_RESPONSE_PAYLOAD_TYPES) == 6
    for payload_type in OBSERVABLE_RESPONSE_PAYLOAD_TYPES:
        hints = typing.get_type_hints(payload_type)
        built = payload_type(**{
            name: _specimen_for(name, declared) for name, declared in hints.items()
        })
        wire = json.loads(json.dumps(encode_observable_payload(built)))
        assert decode_observable_payload(wire) == built


def _specimen_for(name, declared):
    """A value of the type the CONTRACT declares, resolved from the dataclass
    rather than hand-listed, so a new field on any payload is covered without
    editing this file -- and a new field TYPE fails here loudly."""
    if declared is str:
        return f"specimen-{name}"
    if declared is float:
        return 12.5
    if declared is dt.date:
        return _VALUE_DATE
    if isinstance(declared, type) and issubclass(declared, enum.Enum):
        return list(declared)[0]
    raise AssertionError(
        f"{name}: no specimen for declared type {declared!r} -- a field "
        "type was added to the seam contract without deciding how it crosses"
    )


# ---------------------------------------------------------------------------
# R15 -- the payload guards, each killed and the defect shown
# ---------------------------------------------------------------------------


def _good_payload_wire():
    return json.loads(json.dumps(encode_observable_payload(_ADVICE)))


def test_R15_a_payload_missing_its_type_tag_is_refused():
    wire = _good_payload_wire()
    del wire["payload_type"]
    with pytest.raises(WallProtocolError) as caught:
        decode_observable_payload(wire)
    assert caught.value.reason == "MISSING_FIELD"


def test_R15_null_control_the_same_payload_with_its_tag_decodes():
    """The refusal above is about the TAG, not about a generally bad fixture:
    the identical dict with only the deleted key restored decodes."""
    assert decode_observable_payload(_good_payload_wire()) == _ADVICE


def test_R15_a_payload_type_off_this_seam_is_refused_not_guessed():
    wire = _good_payload_wire()
    wire["payload_type"] = "MeterRead"
    with pytest.raises(WallProtocolError) as caught:
        decode_observable_payload(wire)
    assert caught.value.reason == "UNKNOWN_FIELD"


def test_R15_a_missing_payload_field_is_never_defaulted():
    """The mirror of the envelope's absence-is-never-agreement rule, at payload
    depth: a bank advice missing its amount must not become GBP 0.00, which is
    a number the company would post to a ledger."""
    wire = _good_payload_wire()
    del wire["fields"]["amount_gbp"]
    with pytest.raises(WallProtocolError) as caught:
        decode_observable_payload(wire)
    assert caught.value.reason == "MISSING_FIELD"
    restored = _good_payload_wire()
    assert decode_observable_payload(restored).amount_gbp == _ADVICE.amount_gbp


def test_R15_an_unknown_payload_field_is_refused():
    wire = _good_payload_wire()
    wire["fields"]["settlement_hint"] = "pay it"
    with pytest.raises(WallProtocolError) as caught:
        decode_observable_payload(wire)
    assert caught.value.reason == "UNKNOWN_FIELD"


def test_R15_an_enum_value_the_contract_does_not_define_is_refused():
    wire = _good_payload_wire()
    wire["fields"]["rail"] = "carrier_pigeon"
    with pytest.raises(WallProtocolError) as caught:
        decode_observable_payload(wire)
    assert caught.value.reason == "MALFORMED_FIELD"


def test_R15_a_true_is_not_an_amount():
    """`True == 1` in Python, so a permissive numeric check credits a boolean as
    GBP 1.00. Separately guarded, separately proven -- as with the envelope's
    own int check on `schema_version`."""
    wire = _good_payload_wire()
    wire["fields"]["amount_gbp"] = True
    with pytest.raises(WallProtocolError) as caught:
        decode_observable_payload(wire)
    assert caught.value.reason == "MALFORMED_FIELD"


def test_R15_a_malformed_date_is_refused_not_dropped():
    wire = _good_payload_wire()
    wire["fields"]["value_date"] = "11/03/2024"
    with pytest.raises(WallProtocolError) as caught:
        decode_observable_payload(wire)
    assert caught.value.reason == "MALFORMED_FIELD"


def test_R15_the_encoder_refuses_a_payload_this_seam_does_not_define():
    """The encoder's half of the same rule: a counterparty that can serialise
    anything can leak anything."""
    with pytest.raises(SeamEncodeError):
        encode_observable_payload(object())


def test_R15_the_encoder_refuses_an_undefined_field_value_rather_than_stringifying():
    """`str(value)` is how an object's repr silently ships as a field and the
    receiver silently accepts a string.

    Reached through a GENUINE contract payload: the seam's dataclasses are
    frozen but not type-enforcing, so a counterparty can put anything in a
    field, and this is the case the type check exists for. (The look-alike
    test below is refused earlier, by class identity -- so it does NOT prove
    this guard, which is why both exist.)"""
    unshippable = dataclasses.replace(_ADVICE, rail=object())
    assert isinstance(unshippable, RemittanceAdvice)
    with pytest.raises(SeamEncodeError):
        encode_observable_payload(unshippable)


def test_R15_the_encoder_refuses_a_payload_class_that_only_looks_like_the_contracts():
    # A LOOK-ALIKE: same NAME and same field names as the contract's
    # RemittanceAdvice, but a different class, carrying one field the contract
    # does not define and has no wire form for. The encoder keys on class
    # IDENTITY, not on the name, so this is refused before the extra field is
    # ever reached -- a name check alone would have let it through.
    @dataclasses.dataclass(frozen=True)
    class RemittanceAdvice:  # noqa: F811 -- deliberately shadows the contract's
        bank_reference: str
        account_id: str
        amount_gbp: float
        rail: PaymentRail
        value_date: dt.date
        internal_scoring_note: object

    look_alike = RemittanceAdvice(
        bank_reference="INV-9001", account_id="ACC-9001", amount_gbp=1.0,
        rail=PaymentRail.CARD, value_date=_VALUE_DATE,
        internal_scoring_note=object(),
    )
    assert type(look_alike).__name__ == "RemittanceAdvice"
    with pytest.raises(SeamEncodeError):
        encode_observable_payload(look_alike)


def test_R15_MUTANT_a_defaulting_payload_decoder_posts_cash_the_bank_never_advised():
    """The defect the missing-field guard exists to stop, BUILT and run beside
    the shipped decoder on identical bytes.

    The mutant does what a tolerant reader does -- fills an absent field from
    its own idea of a sensible default. The result is not an exception the
    company can act on; it is a RemittanceAdvice for GBP 0.00 that the bank
    never sent, indistinguishable at every later read site from a real one."""
    wire = _good_payload_wire()
    del wire["fields"]["amount_gbp"]

    def _mutant_decode(raw):
        body = dict(raw["fields"])
        body.setdefault("amount_gbp", 0.0)          # <-- the defect
        return RemittanceAdvice(
            bank_reference=body["bank_reference"],
            account_id=body["account_id"],
            amount_gbp=body["amount_gbp"],
            rail=PaymentRail(body["rail"]),
            value_date=dt.date.fromisoformat(body["value_date"]),
        )

    mutant = _mutant_decode(wire)
    assert mutant.amount_gbp == 0.0
    # ...and nothing downstream can tell that from a genuine zero-value advice.
    assert mutant == dataclasses.replace(_ADVICE, amount_gbp=0.0)

    with pytest.raises(WallProtocolError) as caught:
        decode_observable_payload(wire)
    assert caught.value.reason == "MISSING_FIELD"


def test_R15_a_refused_message_is_not_marked_processed():
    """A refusal is not an observation. If a malformed message consumed its
    `correlation_id`, a corrected re-delivery of the same fact -- which is what
    a real feed sends after a bad file -- could never land."""
    consumer = PaymentObservationConsumer()
    broken = _framed_json(_OK_RESPONSE)
    del broken["envelope"]["payload"]["fields"]["amount_gbp"]

    with pytest.raises(WallProtocolError):
        consumer.observe_wire(broken)
    assert consumer.observe_wire(_framed_json(_OK_RESPONSE)) is True


# ===========================================================================
# WHO IS SPEAKING (atom EP6, pass 39) -- the blind review's Q13.
#
# The 2026-08-20 cold-eyes walk went at this atom's headline claim and said:
# indistinguishability from a stand-in "is the property you get for free from
# any well-factored port". Q13 made it concrete -- there was no counterparty
# authentication anywhere below the port, so the company could not tell a real
# bank from anything at all that could format a dict. That is a control gap,
# not an abstraction, and the tests below are what closing it has to survive.
#
# R15 GOVERNS THIS SECTION TOO. Every refusal is exercised on a frame that is
# otherwise perfectly valid, so a test cannot pass because the message was
# broken in some other way; and each refusal asserts its own REASON, because a
# bare `raises` cannot tell two stacked belts apart. The NULL CONTROLS are the
# other half: if the genuine frame did not decode, "everything is refused"
# would read identically to "the check works".
# ===========================================================================

from company.interfaces.wall_protocol import (  # noqa: E402
    COUNTERPARTY_REGISTRY,
    FRAME_WIRE_FIELDS,
    CounterpartyRecord,
    decode_frame,
    decode_framed_response,
)


def _frame(**overrides) -> dict:
    """A hand-authored frame, NOT `frame_wire_message` output -- same R15
    TAUTOLOGY rule the envelope fixtures above follow."""
    message = {
        "sender": PARTICIPANT_ID,
        "credential": PARTICIPANT_CREDENTIAL,
        "envelope": _wire_response(),
    }
    message.update(overrides)
    return message


def test_the_genuine_participant_is_accepted_NULL_CONTROL():
    """Without this, every assertion below would also pass on a port that
    refused absolutely everything."""
    sender, envelope = decode_frame(_frame())
    assert sender == PARTICIPANT_ID
    assert envelope == _wire_response()


def test_a_sender_this_build_has_never_heard_of_is_refused():
    with pytest.raises(WallProtocolError) as caught:
        decode_frame(_frame(sender="TOTALLY-LEGITIMATE-BANK"))
    assert caught.value.reason == "UNKNOWN_SENDER"


def test_a_known_participant_presenting_the_wrong_credential_is_refused():
    """The sender name is right and everything else about the message is
    valid. Only the proof is wrong, and that alone must be enough."""
    with pytest.raises(WallProtocolError) as caught:
        decode_frame(_frame(credential="bacs-bureau-01::participant-credential::v2"))
    assert caught.value.reason == "BAD_CREDENTIAL"


def test_an_unknown_sender_and_a_bad_credential_are_DIFFERENT_reasons():
    """One AUTH_FAILED would collapse "I have never heard of you" into "you are
    not who you say you are". Those need different repairs -- a registry entry
    versus a credential rotation -- so the port must keep them apart."""
    with pytest.raises(WallProtocolError) as unknown:
        decode_frame(_frame(sender="NOBODY"))
    with pytest.raises(WallProtocolError) as bad:
        decode_frame(_frame(credential="wrong"))
    assert unknown.value.reason != bad.value.reason


@pytest.mark.parametrize("dropped", sorted(FRAME_WIRE_FIELDS))
def test_a_frame_missing_any_field_is_refused_never_defaulted(dropped):
    """Absence is never agreement applies to the frame as much as the envelope.
    An unsigned frame is not a frame, and the sender is not inferred from the
    fact that only one participant is registered."""
    frame = _frame()
    del frame[dropped]
    with pytest.raises(WallProtocolError) as caught:
        decode_frame(frame)
    assert caught.value.reason == "MISSING_FIELD"


def test_an_extra_frame_field_is_refused():
    with pytest.raises(WallProtocolError) as caught:
        decode_frame(_frame(hint="trust me"))
    assert caught.value.reason == "UNKNOWN_FIELD"


@pytest.mark.parametrize("bad", [None, "", 0, [], {}, b"BACS-BUREAU-01"])
def test_FAIL_OPEN_sweep_an_empty_or_wrongly_typed_sender_is_never_a_participant(bad):
    """The inputs a permissive port waves through. An empty string is the one
    that matters most: `registry.get("")` is a miss, but only if the value was
    required to be a non-empty str before the lookup happened."""
    with pytest.raises(WallProtocolError):
        decode_frame(_frame(sender=bad))


@pytest.mark.parametrize("bad", [None, "", 0, [], {}])
def test_FAIL_OPEN_sweep_an_empty_or_wrongly_typed_credential_proves_nothing(bad):
    with pytest.raises(WallProtocolError):
        decode_frame(_frame(credential=bad))


def test_a_frame_that_is_not_a_mapping_at_all_is_refused():
    for junk in (None, "", [], 7, "{}"):
        with pytest.raises(WallProtocolError) as caught:
            decode_frame(junk)
        assert caught.value.reason == "NOT_A_MESSAGE"


def test_the_registry_holds_a_fingerprint_and_never_the_credential():
    """R15 TAUTOLOGY, checked rather than asserted in a docstring. If the
    company's registry held the credential itself, the check would be the two
    sides comparing one value that lives in one place."""
    import hashlib
    import inspect

    import company.interfaces.wall_protocol as wp

    source = inspect.getsource(wp)
    assert PARTICIPANT_CREDENTIAL not in source
    record = COUNTERPARTY_REGISTRY[PARTICIPANT_ID]
    assert record.credential_sha256 == hashlib.sha256(
        PARTICIPANT_CREDENTIAL.encode("utf-8")
    ).hexdigest()


def test_MUTATION_a_rotated_credential_the_company_was_not_told_about_BREAKS_the_seam():
    """THE MUTATION. Rotate the counterparty's credential without updating the
    company's registry and the live crossing must stop working. A version of
    this control that kept working through the rotation would not be checking
    anything -- it is the whole difference between an identity check and a
    field that happens to be present."""
    consumer = PaymentObservationConsumer()
    genuine = _framed_json(_OK_RESPONSE)
    rotated = dict(genuine, credential=PARTICIPANT_CREDENTIAL + "-rotated")

    with pytest.raises(WallProtocolError) as caught:
        consumer.observe_wire(rotated)
    assert caught.value.reason == "BAD_CREDENTIAL"
    # NULL CONTROL: the un-rotated message on the same consumer still lands, so
    # the refusal above is about the credential and not about the consumer.
    assert consumer.observe_wire(genuine) is True


def test_MUTATION_the_unframed_envelope_that_used_to_be_accepted_is_now_REFUSED():
    """The defect this pass closed, run as its own mutant. Before pass 39 the
    company's route to a payment observation took a bare envelope from anybody;
    that exact message is what an unauthenticated sender emits, and it must no
    longer be readable."""
    consumer = PaymentObservationConsumer()
    unframed = _through_real_json(_OK_RESPONSE)

    with pytest.raises(WallProtocolError) as caught:
        consumer.observe_wire(unframed)
    assert caught.value.reason in {"MISSING_FIELD", "UNKNOWN_FIELD"}
    assert consumer.observe_wire(_framed_json(_OK_RESPONSE)) is True


def test_a_refused_sender_never_reaches_the_belief_code():
    """The check is BELOW the port, which means the refusal has to happen
    before anything is believed -- not after, with a compensating rollback."""
    consumer = PaymentObservationConsumer()
    impostor = dict(_framed_json(_OK_RESPONSE), sender="IMPOSTOR-BANK")

    with pytest.raises(WallProtocolError):
        consumer.observe_wire(impostor)
    refused = consumer.snapshot(_ADVICE.account_id)
    assert refused.allocation.allocations == []
    assert refused.allocation.unallocated_credit_gbp == 0.0
    # ...and the correlation id was not consumed, so the genuine delivery lands
    # and DOES move the belief -- which is what makes the two lines above a
    # measurement of the refusal rather than of an inert consumer.
    assert consumer.observe_wire(_framed_json(_OK_RESPONSE)) is True
    assert consumer.snapshot(_ADVICE.account_id).allocation.unallocated_credit_gbp > 0.0


# ---------------------------------------------------------------------------
# Q10's half: the version a COUNTERPARTY is on, which is not the version this
# BUILD can read. Proven on a two-participant fixture registry, because the
# real one has one row -- and a table whose only demonstration is its single
# live entry has not been shown to have a per-counterparty dimension at all.
# ---------------------------------------------------------------------------

_STAGGERED_REGISTRY = {
    "EARLY-ADOPTER": CounterpartyRecord(
        credential_sha256=COUNTERPARTY_REGISTRY[PARTICIPANT_ID].credential_sha256,
        speaks_schema_versions=frozenset({1, 2}),
    ),
    "NOT-CUT-OVER-YET": CounterpartyRecord(
        credential_sha256=COUNTERPARTY_REGISTRY[PARTICIPANT_ID].credential_sha256,
        speaks_schema_versions=frozenset({2}),
    ),
}


def test_two_counterparties_on_different_releases_are_read_differently():
    """A DTC/SEC/BSC release does not land on every participant on one day. The
    SAME bytes must be acceptable from the participant that has cut over and
    refused from the one that has not -- which is impossible to express with a
    single global constant, and is the shape of Q10's objection."""
    frame = _frame(sender="EARLY-ADOPTER")
    _sender, response = decode_framed_response(
        frame, decode_payload=_dictish, registry=_STAGGERED_REGISTRY
    )
    assert response.schema_version == 1

    with pytest.raises(WallProtocolError) as caught:
        decode_framed_response(
            _frame(sender="NOT-CUT-OVER-YET"),
            decode_payload=_dictish,
            registry=_STAGGERED_REGISTRY,
        )
    assert caught.value.reason == "VERSION_NOT_SPOKEN"


def test_VERSION_NOT_SPOKEN_is_distinct_from_UNSUPPORTED_VERSION():
    """"This build cannot read that dialect" and "this build can read it, and
    this participant is not on it" are different facts with different repairs.
    Collapsing them would send someone to change `SUPPORTED_SCHEMA_VERSIONS`
    when the answer was a release schedule."""
    with pytest.raises(WallProtocolError) as not_spoken:
        decode_framed_response(
            _frame(sender="NOT-CUT-OVER-YET"),
            decode_payload=_dictish,
            registry=_STAGGERED_REGISTRY,
        )
    with pytest.raises(WallProtocolError) as unsupported:
        decode_framed_response(
            _frame(sender="EARLY-ADOPTER", envelope=_wire_response(schema_version=99)),
            decode_payload=_dictish,
            registry=_STAGGERED_REGISTRY,
        )
    assert not_spoken.value.reason == "VERSION_NOT_SPOKEN"
    assert unsupported.value.reason == "UNSUPPORTED_VERSION"


def test_an_EMPTY_registry_refuses_everything_rather_than_accepting_it():
    """The injectable registry must have no value that means "skip the check".
    Empty is the tempting fail-open: a lookup table with nothing in it is
    exactly what a half-initialised process holds."""
    with pytest.raises(WallProtocolError) as caught:
        decode_frame(_frame(), registry={})
    assert caught.value.reason == "UNKNOWN_SENDER"


def test_the_verified_sender_is_returned_and_not_merely_checked():
    """A port that authenticates and then throws the answer away leaves the
    consumer unable to tell two counterparties apart later -- and this is the
    only point in the path where the fact exists."""
    sender, response = decode_framed_response(_frame(), decode_payload=_dictish)
    assert sender == PARTICIPANT_ID
    assert response.correlation_id == "corr-1"


# ---------------------------------------------------------------------------
# THE RATCHET: which company-side crossings check who is speaking, and which do
# not. One crossing is framed today; the other two are named here rather than
# left to be inferred, so adding a third unframed one is a decision somebody
# has to make on purpose instead of a silence.
# ---------------------------------------------------------------------------

_FRAMED_CROSSINGS = {"company/billing/payment_observation_consumer.py"}
_UNFRAMED_CROSSINGS = {
    "company/comms/susceptibility_estimator.py",
    "company/market/flex_participation.py",
}


def test_the_framed_and_unframed_crossings_are_exactly_as_declared():
    """A count that moves is a decision that has to be taken. If a new company
    module starts decoding wall responses without a participant check, this
    reds -- which is the only thing standing between "one crossing framed, two
    named" and a wall that quietly stops authenticating as it grows."""
    import pathlib

    root = pathlib.Path(__file__).resolve().parents[3]
    framed, unframed = set(), set()
    for path in sorted((root / "company").rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(root).as_posix()
        if rel == "company/interfaces/wall_protocol.py":
            continue
        if "decode_framed_response(" in text:
            framed.add(rel)
        elif "decode_response(" in text:
            unframed.add(rel)

    assert framed == _FRAMED_CROSSINGS
    assert unframed == _UNFRAMED_CROSSINGS
