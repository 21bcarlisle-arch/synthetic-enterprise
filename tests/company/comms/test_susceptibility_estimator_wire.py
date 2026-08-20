"""F1b OFF THE WIRE -- the company's inbound leg of the conversation seam
(atom EP6_wall_protocol_typing, 2026-08-20).

WHY THIS FILE EXISTS SEPARATELY FROM `test_conversation_comms.py`, and it is
not tidiness: `tools/pre_commit_test_gate.py::tests_for` maps a changed module
to `tests/**/test_<stem>.py` and `tests/**/test_<stem>_*.py`. There is no
`test_susceptibility_estimator*.py` in this repo, so every change to
`company/comms/susceptibility_estimator.py` mapped to ZERO tests and could be
committed untested -- the exact blind spot that file's own docstring records
from the 2026-08-09 publish wedge. Naming this file after the module's stem
puts the module back inside the gate.

WHAT THESE PROVE: the company refuses a malformed crossing rather than folding
a belief it was never told. They do NOT prove the counterparty agrees -- that
is a cross-side fact, and encoding here with the company's own encoder to
decode it again would be an R15 TAUTOLOGY. The cross-side fact lives in
`tests/background/test_conversation_gap_ledger_wire.py`.
"""
import pytest

from company.comms.susceptibility_estimator import (
    SusceptibilityEstimator,
    decode_observable_payload,
)
from company.interfaces.wall_protocol import WallProtocolError
from interface.contracts.conversation_seam import (
    Channel,
    ConversationMessage,
    FORBIDDEN_TRUTH_FIELDS,
    Product,
    Situation,
)


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


def _msg(mid="MW1", framing="loss_framed", tone="empathetic_toned", step=100):
    return ConversationMessage(
        message_id=mid,
        situation=Situation.RENEWAL,
        channel=Channel.EMAIL,
        product=Product.DUAL_FUEL,
        tone=tone,
        framing=framing,
        emitted_step=step,
    )


def _wire(**over):
    """A well-formed response as the counterparty publishes it. Hand-written
    against the SCHEMA -- deliberately not produced by calling the sim's
    encoder, so a refusal proven here is a property of the decoder and not of
    the pair."""
    payload_fields = {
        "response_id": "R1",
        "responds_to": "MW1",
        "action": "reply",
        "channel_chosen": "email",
        "latency": 3,
        "responded_step": 103,
    }
    payload_fields.update(over.pop("payload_fields", {}))
    base = {
        "correlation_id": "corr-1",
        "status": "OK",
        "schema_version": 1,
        "observed_at": "2026-01-01T12:00:00",
        "valid_time": None,
        "payload": {"payload_type": "ConversationResponse", "fields": payload_fields},
        "error": None,
    }
    base.update(over)
    return base


def test_a_well_formed_reply_off_the_wire_updates_the_belief():
    est = SusceptibilityEstimator()
    assert est.observe_wire("c1", _msg(), _wire()) is True
    assert est.posterior_report("c1")["framing_means"]["loss_framed"] > 0.5


def test_the_same_reply_twice_is_an_idempotent_no_op_off_the_wire_too():
    """C-S2 survives the transport: idempotency is keyed on the payload's
    `response_id`, so a re-delivered message is harmless."""
    est = SusceptibilityEstimator()
    assert est.observe_wire("c1", _msg(), _wire()) is True
    assert est.observe_wire("c1", _msg(), _wire()) is False


def test_a_reply_missing_its_version_is_refused_not_defaulted():
    """The named fail-open: an absent field and an agreeing field are the same
    bytes, so a version that can be defaulted is not a version."""
    wire = _wire()
    del wire["schema_version"]
    with pytest.raises(WallProtocolError) as exc:
        SusceptibilityEstimator().observe_wire("c1", _msg(), wire)
    assert exc.value.reason == "MISSING_FIELD"


def test_a_version_the_company_does_not_speak_is_refused_distinguishably():
    """"You speak a dialect I do not know" and "you did not say what you
    speak" are different failures calling for different repairs, so they carry
    different reasons."""
    with pytest.raises(WallProtocolError) as exc:
        SusceptibilityEstimator().observe_wire("c1", _msg(), _wire(schema_version=2))
    assert exc.value.reason == "UNSUPPORTED_VERSION"


def test_a_refused_message_is_not_recorded_as_observed():
    """A refusal is NOT an observation. If a malformed delivery marked its
    `response_id` seen, the counterparty's CORRECTED re-delivery would be
    silently dropped as a duplicate -- a reply the company should have learned
    from, lost to a transport error."""
    est = SusceptibilityEstimator()
    with pytest.raises(WallProtocolError):
        est.observe_wire("c1", _msg(), _wire(schema_version=2))
    assert est.observe_wire("c1", _msg(), _wire()) is True


def test_a_payload_less_envelope_is_refused_on_this_seam():
    """On THIS seam silence is an ACTION (`no_reply`), not an absent payload,
    so every honest answer carries an observation. Accepting a payload-less
    envelope quietly would let a broken counterparty erase replies."""
    with pytest.raises(WallProtocolError) as exc:
        SusceptibilityEstimator().observe_wire(
            "c1", _msg(), _wire(status="NOT_KNOWABLE_YET", payload=None)
        )
    assert exc.value.reason == "CONTRACT_VIOLATION"


def test_a_missing_payload_field_is_refused_never_defaulted():
    wire = _wire()
    del wire["payload"]["fields"]["latency"]
    with pytest.raises(WallProtocolError) as exc:
        SusceptibilityEstimator().observe_wire("c1", _msg(), wire)
    assert exc.value.reason == "MISSING_FIELD"


def test_an_undeclared_payload_field_is_refused_rather_than_tolerated():
    """The mirror-image reason: if a later schema adds a field, the version
    number is how a decoder finds out -- never silent tolerance of bytes it
    does not understand. This is also the smuggling route a hidden trait would
    take, so tolerance here would be a hole in the wall as well as in the
    protocol."""
    wire = _wire(payload_fields={"tone_susceptibility": 0.8})
    with pytest.raises(WallProtocolError) as exc:
        SusceptibilityEstimator().observe_wire("c1", _msg(), wire)
    assert exc.value.reason == "UNKNOWN_FIELD"


def test_every_forbidden_truth_field_is_refused_by_name():
    """R10-shaped: the class fails, not one instance. Every field the contract
    names as a hidden trait is refused if it appears on the wire, because the
    permitted field set comes from the contract and nothing else can join it."""
    for forbidden in FORBIDDEN_TRUTH_FIELDS:
        with pytest.raises(WallProtocolError):
            SusceptibilityEstimator().observe_wire(
                "c1", _msg(), _wire(payload_fields={forbidden: 0.9})
            )


def test_a_latency_the_contract_cannot_represent_is_refused_at_the_seam():
    """C-S3 made structural: `ConversationResponse.__post_init__` rejects a
    non-positive latency, and the seam re-raises it as CONTRACT_VIOLATION so a
    same-step reply can never reach the belief update as a half-built object
    NOR escape as a bare ValueError the caller was not expecting."""
    wire = _wire(payload_fields={"latency": 0, "responded_step": 100})
    with pytest.raises(WallProtocolError) as exc:
        SusceptibilityEstimator().observe_wire("c1", _msg(), wire)
    assert exc.value.reason == "CONTRACT_VIOLATION"


def test_a_boolean_latency_is_malformed_not_the_integer_one():
    """BOUNDARY: bool is an int subclass, so `True` would decode to a latency
    of 1 -- a plausible, actionable value the company would fold into a
    belief. It is a malformed field, not a fast reply."""
    wire = _wire(payload_fields={"latency": True})
    with pytest.raises(WallProtocolError) as exc:
        SusceptibilityEstimator().observe_wire("c1", _msg(), wire)
    assert exc.value.reason == "MALFORMED_FIELD"


def test_an_action_off_the_contract_is_refused():
    wire = _wire(payload_fields={"action": "ghosted"})
    with pytest.raises(WallProtocolError) as exc:
        SusceptibilityEstimator().observe_wire("c1", _msg(), wire)
    assert exc.value.reason == "MALFORMED_FIELD"


def test_an_untagged_payload_is_refused():
    """The tag is how a payload is routed to a declared type. A receiver that
    guessed from the field set would mis-route the day a second payload type
    joins this seam's OBSERVABLE_RESPONSE_PAYLOAD_TYPES."""
    with pytest.raises(WallProtocolError) as exc:
        decode_observable_payload({"fields": {}})
    assert exc.value.reason == "MISSING_FIELD"


def test_a_payload_tagged_as_a_type_this_seam_does_not_observe_is_refused():
    with pytest.raises(WallProtocolError) as exc:
        decode_observable_payload(
            {"payload_type": "ConversationMessage", "fields": {}}
        )
    assert exc.value.reason == "UNKNOWN_FIELD"


def test_a_non_message_is_refused_rather_than_read_as_empty():
    for junk in (None, "a string", 7, ["a", "list"]):
        with pytest.raises(WallProtocolError):
            SusceptibilityEstimator().observe_wire("c1", _msg(), junk)


def test_the_wire_path_and_the_object_path_reach_the_same_belief():
    """"Indistinguishable to the company" made concrete: the belief after a
    reply that arrived as BYTES is identical to the belief after the same
    reply handed over as an object. If the two ever diverge, the transport is
    doing something to the observation, which is precisely what it must not."""
    from interface.contracts.conversation_seam import ConversationResponse, ResponseAction

    over_wire = SusceptibilityEstimator()
    over_wire.observe_wire("c1", _msg(), _wire())

    in_process = SusceptibilityEstimator()
    in_process.observe_response(
        "c1",
        _msg(),
        ConversationResponse(
            response_id="R1", responds_to="MW1", action=ResponseAction.REPLY,
            channel_chosen=Channel.EMAIL, latency=3, responded_step=103,
        ),
    )
    assert over_wire.posterior_report("c1") == in_process.posterior_report("c1")


def test_R15_MUTATION_defaulting_the_absent_version_makes_the_refusal_vanish():
    """The mutation, RUN not asserted. `wire.setdefault("schema_version", 1)`
    is the sibling `from_log_entry` pattern, and it silently relabels a message
    that never stated its version as the one version this build speaks today.

    NULL CONTROL: the same wrapper WITHOUT the default leaves the refusal
    intact, so the mutation proves the DEFAULTING and not the wrapping.
    """
    wire = _wire()
    del wire["schema_version"]

    def observe_with_default(w):
        w = dict(w)
        w.setdefault("schema_version", 1)             # the mutation
        return SusceptibilityEstimator().observe_wire("c1", _msg(), w)

    def observe_without_default(w):
        return SusceptibilityEstimator().observe_wire("c1", _msg(), dict(w))

    assert observe_with_default(wire) is True         # mutation: accepted
    with pytest.raises(WallProtocolError):
        observe_without_default(wire)                 # control: still refused


def test_R15_MUTATION_a_permissive_payload_decoder_admits_a_hidden_trait():
    """FAIL-OPEN at payload depth: relax the exact-field-set rule to "the
    declared fields are present" and a payload carrying a susceptibility
    scalar decodes clean. The company would then hold the very number the
    epistemic wall exists to keep from it -- and the message would look
    perfectly well-formed at the envelope level, which is why the refusal has
    to live at payload depth and not only at the envelope."""
    smuggled = _wire(payload_fields={"tone_susceptibility": 0.83})

    def lenient(w):
        declared = {
            "response_id", "responds_to", "action",
            "channel_chosen", "latency", "responded_step",
        }
        body = w["payload"]["fields"]
        assert not declared - set(body)               # the mutation: subset check only
        return body.get("tone_susceptibility")

    assert lenient(smuggled) == 0.83                  # mutation: the trait arrives
    with pytest.raises(WallProtocolError):
        SusceptibilityEstimator().observe_wire("c1", _msg(), smuggled)


def test_the_company_side_never_imports_the_world():
    """The wall, restated for the module this file guards: the company decodes
    with its OWN codec and reads only the neutral contract. An import of
    `simulation.*` here would make the belief a read of ground truth."""
    assert _imported_roots("company/comms/susceptibility_estimator.py").isdisjoint({"simulation", "sim"})
