"""The company's outbound leg (atom EP6_wall_protocol_typing, Q3).

`company/interfaces/collection_submission.py` is the one place this company SENDS
rather than receives. What these tests are about is the direction the wall does
NOT police here -- outbound is the company's own data -- and the discipline that
replaces it: nothing crosses that has not been declared, in both directions.
"""
from __future__ import annotations

import dataclasses
import datetime as dt
import json

import pytest

from company.interfaces.collection_submission import (
    COLLECTION_REQUEST_WIRE_FIELDS,
    CollectionSubmissionError,
    encode_collection_payload,
    encode_collection_request,
)
from interface.contracts.payment_observable_seam import (
    COLLECTION_REQUEST_TYPE,
    SCHEMA_VERSION,
    CollectionRequest,
    PaymentRail,
)
from interface.contracts.wall_envelope import WallRequest
from simulation.payment_seam_adapter import SeamDecodeError, decode_collection_request

EMITTED = dt.datetime(2026, 3, 2, 9, 0)


def _collection(**over):
    kwargs = dict(
        account_id="ACC-1",
        mandate_ref="MANDATE-ACC-1",
        amount_gbp=42.5,
        rail=PaymentRail.BACS_DIRECT_DEBIT,
        requested_collection_date=dt.date(2026, 3, 6),
    )
    kwargs.update(over)
    return CollectionRequest(**kwargs)


def _request(**over):
    kwargs = dict(
        correlation_id="INV-1",
        request_type=COLLECTION_REQUEST_TYPE,
        schema_version=SCHEMA_VERSION,
        as_of=EMITTED,
        emitted_at=EMITTED,
        payload=_collection(),
    )
    kwargs.update(over)
    return WallRequest(**kwargs)


def test_the_submission_survives_real_json_and_arrives_unchanged():
    """The round trip through TWO INDEPENDENT SIDES: the company's codec encodes
    and the counterparty's own mirror decodes, with real serialisation in
    between. Neither imports the other's decoder, which is what makes the far
    side's refusal a check rather than a handshake with itself."""
    wire = encode_collection_request(_request())
    assert json.loads(json.dumps(wire)) == wire
    assert decode_collection_request(json.loads(json.dumps(wire))) == _request()


def test_the_vintage_stamp_is_on_the_submission_and_is_read_off_it():
    wire = encode_collection_request(_request())
    assert wire["schema_version"] == SCHEMA_VERSION
    assert decode_collection_request(wire).schema_version == SCHEMA_VERSION


# ── the declaration, and the direction that matters ────────────────────────────


def test_MUTATION_a_field_added_to_the_payload_cannot_cross_undeclared():
    """THE FAIL-OPEN DIRECTION. A reflected encoder (`dataclasses.asdict`)
    would have carried a new field silently. The declaration is enumerated
    precisely so that adding one to `CollectionRequest` and nothing else stops
    the submission dead instead of widening what the company puts on the wire
    without anyone deciding it should."""
    widened = dataclasses.make_dataclass(
        "CollectionRequest",
        [(f, str) for f in COLLECTION_REQUEST_WIRE_FIELDS] + [("customer_stress", str)],
        frozen=True,
        bases=(CollectionRequest,),
    )
    mutant = widened(
        account_id="ACC-1",
        mandate_ref="MANDATE-ACC-1",
        amount_gbp=42.5,
        rail=PaymentRail.BACS_DIRECT_DEBIT,
        requested_collection_date=dt.date(2026, 3, 6),
        customer_stress="high",
    )
    with pytest.raises(CollectionSubmissionError, match="customer_stress"):
        encode_collection_payload(mutant)


def test_the_unmutated_payload_encodes_cleanly():
    """NULL CONTROL for the mutation above: without it the refusal could be
    firing on anything else wrong with a synthesised dataclass."""
    assert set(encode_collection_payload(_collection())) == set(
        COLLECTION_REQUEST_WIRE_FIELDS
    )


def test_the_declaration_is_not_derived_from_the_dataclass():
    """R15 TAUTOLOGY. A set computed from `dataclasses.fields(CollectionRequest)`
    would widen with its own subject and could never catch a field being added.
    The two are asserted EQUAL here, which is the check; what makes it a check
    is that they are written down in two places."""
    assert set(COLLECTION_REQUEST_WIRE_FIELDS) == {
        f.name for f in dataclasses.fields(CollectionRequest)
    }


def test_a_non_collection_payload_is_REFUSED():
    with pytest.raises(CollectionSubmissionError, match="CollectionRequest"):
        encode_collection_payload({"account_id": "ACC-1"})


def test_a_non_request_envelope_is_REFUSED():
    with pytest.raises(CollectionSubmissionError, match="WallRequest"):
        encode_collection_request({"correlation_id": "INV-1"})


# ── the counterparty's refusals: absence is never agreement ───────────────────


@pytest.mark.parametrize(
    "field",
    ["correlation_id", "request_type", "schema_version", "as_of", "emitted_at", "payload"],
)
def test_a_submission_MISSING_any_envelope_field_is_REFUSED(field):
    wire = encode_collection_request(_request())
    del wire[field]
    with pytest.raises(SeamDecodeError, match="omits required field"):
        decode_collection_request(wire)


@pytest.mark.parametrize("field", list(COLLECTION_REQUEST_WIRE_FIELDS))
def test_a_submission_MISSING_any_payload_field_is_REFUSED(field):
    wire = encode_collection_request(_request())
    del wire["payload"][field]
    with pytest.raises(SeamDecodeError, match="omits required field"):
        decode_collection_request(wire)


def test_an_UNKNOWN_envelope_field_is_REFUSED_rather_than_ignored():
    """A decoder that ignored what it did not recognise would let the company
    believe it had asked for something this build never read."""
    wire = encode_collection_request(_request())
    wire["priority"] = "urgent"
    with pytest.raises(SeamDecodeError, match="does not define"):
        decode_collection_request(wire)


def test_an_UNKNOWN_payload_field_is_REFUSED_rather_than_ignored():
    wire = encode_collection_request(_request())
    wire["payload"]["customer_stress"] = "high"
    with pytest.raises(SeamDecodeError, match="does not define"):
        decode_collection_request(wire)


def test_a_version_this_bureau_does_not_speak_is_REFUSED_BY_NUMBER():
    """The one thing a version number is for. A submission stamped with a
    release this seam does not speak is refused rather than read hopefully."""
    wire = encode_collection_request(_request())
    wire["schema_version"] = 97
    with pytest.raises(SeamDecodeError, match="not the"):
        decode_collection_request(wire)


@pytest.mark.parametrize("bad", [None, "2", 2.0, True, [2], {"v": 2}])
def test_a_NON_INT_version_is_REFUSED(bad):
    """`True` is in this list on purpose: `isinstance(True, int)` is True in
    Python, so a bare int check accepts a boolean and reads it as version 1."""
    wire = encode_collection_request(_request())
    wire["schema_version"] = bad
    with pytest.raises(SeamDecodeError):
        decode_collection_request(wire)


@pytest.mark.parametrize("bad", [None, "not-a-mapping", 7, [1, 2]])
def test_a_NON_MAPPING_submission_or_payload_is_REFUSED(bad):
    with pytest.raises(SeamDecodeError, match="mapping"):
        decode_collection_request(bad)
    wire = encode_collection_request(_request())
    wire["payload"] = bad
    with pytest.raises(SeamDecodeError, match="mapping"):
        decode_collection_request(wire)


def test_an_UNKNOWN_RAIL_is_REFUSED_rather_than_defaulted_to_OTHER():
    """`PaymentRail.OTHER` exists and is a legitimate value a company can SEND.
    Reading an unrecognised string AS it would silently relabel a rail the
    bureau does not support into one it does."""
    wire = encode_collection_request(_request())
    wire["payload"]["rail"] = "carrier_pigeon"
    with pytest.raises(SeamDecodeError, match="malformed"):
        decode_collection_request(wire)
    wire["payload"]["rail"] = PaymentRail.OTHER.value
    assert decode_collection_request(wire).payload.rail is PaymentRail.OTHER


def test_the_submission_module_does_not_import_the_counterpartys_decoder():
    """Two sides, two implementations. If this module imported the bureau's
    decoder the round-trip test above would be one piece of code agreeing with
    itself, and the wall forbids the reverse import outright."""
    import company.interfaces.collection_submission as mod

    source = open(mod.__file__).read()
    assert "import simulation" not in source
    assert "from simulation" not in source
