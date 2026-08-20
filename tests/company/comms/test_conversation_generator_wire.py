"""F1b ONTO THE WIRE -- the company's outbound leg of the conversation seam
(atom EP6_wall_protocol_typing, 2026-08-20).

Named for `company/comms/conversation_generator.py`'s stem for the reason
`test_susceptibility_estimator_wire.py` records: `pre_commit_test_gate.
tests_for` selects by stem, and no `test_conversation_generator*.py` existed,
so that module mapped to zero tests.

THE OUTBOUND LEG IS NOT AN EPISTEMIC CROSSING and these tests do not treat it
as one: the message is data the company already owns and chose to send. What
they check is the PROTOCOL property -- that the nudge leaves as a versioned
message a counterparty could refuse, rather than as an object handed down the
call frame with a version nobody reads.
"""
import datetime as dt
import json

import pytest

from company.comms.conversation_generator import (
    ConversationGenerator,
    CustomerSegment,
    encode_message_payload,
)
from company.interfaces.wall_protocol import REQUEST_WIRE_FIELDS, WallProtocolError
from interface.contracts.conversation_seam import (
    SCHEMA_VERSION,
    Channel,
    ConversationMessage,
    Product,
    Situation,
)

AS_OF = dt.datetime(2026, 1, 1, 9, 0)
EMITTED_AT = dt.datetime(2026, 1, 1, 9, 30)


def _imported_roots(rel_path):
    """The top-level package of every module `rel_path` imports, from its AST.
    Read structurally, not by scanning for lines that start with `import`: a
    docstring can wrap onto a line beginning "from ``x``", and a control a
    stray sentence can turn red gets weakened until it means nothing."""
    import ast
    import pathlib
    tree = ast.parse(pathlib.Path(rel_path).read_text())
    roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    return roots


def _wire(situation=Situation.RENEWAL, **kw):
    return ConversationGenerator().generate_wire_request(
        kw.pop("customer_id", "c1"),
        kw.pop("segment", CustomerSegment()),
        situation,
        kw.pop("product", Product.DUAL_FUEL),
        kw.pop("emitted_step", 5),
        as_of=AS_OF,
        emitted_at=EMITTED_AT,
        **kw,
    )


def test_the_request_states_every_envelope_field_including_its_nulls():
    """ABSENCE IS NEVER AGREEMENT on the way out too. The expected key set is
    read from the codec's own `REQUEST_WIRE_FIELDS` rather than restated here,
    so a field added to the envelope moves this assertion with it instead of
    leaving it agreeing with a stale copy of itself."""
    assert set(_wire()) == set(REQUEST_WIRE_FIELDS)


def test_the_version_leaves_the_process_and_comes_from_the_contract():
    assert _wire()["schema_version"] == SCHEMA_VERSION


def test_the_request_is_json_round_trippable():
    wire = _wire()
    assert json.loads(json.dumps(wire)) == wire


def test_the_two_clocks_stay_distinct_on_the_wire():
    """`as_of` is the point-in-time decision clock (the Blindfold) and
    `emitted_at` is when the request was raised. WallRequest never conflates
    them, and neither does the wire form -- a reconciliation job replaying old
    requests depends on the difference surviving transport."""
    wire = _wire()
    assert wire["as_of"] == AS_OF.isoformat()
    assert wire["emitted_at"] == EMITTED_AT.isoformat()
    assert wire["as_of"] != wire["emitted_at"]


def test_the_payload_is_tagged_and_carries_the_contracts_whole_field_set():
    """The tag routes the payload; the field set is the contract's, read from
    the dataclass rather than listed here."""
    from dataclasses import fields

    payload = _wire()["payload"]
    assert payload["payload_type"] == "ConversationMessage"
    assert set(payload["fields"]) == {f.name for f in fields(ConversationMessage)}


def test_an_absent_offer_crosses_as_an_explicit_null_not_a_missing_key():
    """BOUNDARY, and the value the rule is most easily wrong about: most
    situations carry no offer. Dropping the key "because it is None anyway" is
    exactly the absence the far side would have to default -- so the key is
    written, with null in it."""
    wire = _wire(situation=Situation.MISSED_PAYMENT)
    assert "offer" in wire["payload"]["fields"]
    assert wire["payload"]["fields"]["offer"] is None


def test_the_correlation_id_defaults_to_the_message_id_on_the_wire():
    """It is both the idempotency key and the ONLY link to a response that
    arrives on its own, later (C-S1/C-S2). It has to survive transport as
    itself."""
    wire = _wire()
    assert wire["correlation_id"] == wire["payload"]["fields"]["message_id"]


def test_the_encoder_refuses_a_payload_that_is_not_this_seams_message():
    with pytest.raises(WallProtocolError):
        encode_message_payload({"message_id": "M1"})


def test_the_encoder_refuses_a_bool_where_the_contract_declares_an_int():
    """bool is an int subclass, so a True step would ship as `true` and decode
    back as 1 -- a value the far side would accept and act on."""
    with pytest.raises(WallProtocolError):
        encode_message_payload(
            ConversationMessage(
                message_id="M1", situation=Situation.RENEWAL, channel=Channel.EMAIL,
                product=Product.DUAL_FUEL, tone="neutral_toned",
                framing="neutral_framed", emitted_step=True,
            )
        )


def test_the_wire_request_and_the_object_request_carry_the_same_message():
    """The two forms differ in TRANSPORT and in nothing else. `generate_wall_
    request` stays for the offline harness; what changed is that a counterparty
    no longer receives one."""
    gen = ConversationGenerator()
    args = ("c1", CustomerSegment(), Situation.RENEWAL, Product.DUAL_FUEL, 5)
    obj = gen.generate_wall_request(*args, as_of=AS_OF, emitted_at=EMITTED_AT)
    wire = gen.generate_wire_request(*args, as_of=AS_OF, emitted_at=EMITTED_AT)
    assert wire["payload"]["fields"]["message_id"] == obj.payload.message_id
    assert wire["payload"]["fields"]["framing"] == obj.payload.framing
    assert wire["correlation_id"] == obj.correlation_id


def test_R15_MUTATION_dropping_the_null_offer_key_would_look_identical_to_a_reader():
    """FAIL-OPEN, run not asserted: strip keys whose value is null -- the
    single most natural "tidy" encoder change -- and the message still looks
    well-formed to anything that inspects it casually. The far side then has
    to decide what an absent `offer` means, and every answer it can give is a
    default. The shipped encoder writes the key.

    NULL CONTROL: the same comprehension WITHOUT the null filter leaves the key
    set intact, so what the mutation shows is the dropping and not the rebuild.
    """
    wire = _wire(situation=Situation.MISSED_PAYMENT)
    body = wire["payload"]["fields"]

    tidied = {k: v for k, v in body.items() if v is not None}   # the mutation
    control = {k: v for k, v in body.items()}                   # the null control

    assert "offer" not in tidied                                # mutation: key gone
    assert control["offer"] is None and "offer" in control      # control: key stated
    assert "offer" in body                                      # shipped: key stated


def test_the_company_side_never_imports_the_world():
    assert _imported_roots("company/comms/conversation_generator.py").isdisjoint({"simulation", "sim"})
