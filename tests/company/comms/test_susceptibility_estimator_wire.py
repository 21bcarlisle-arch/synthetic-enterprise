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
    does not understand.

    NULL CONTROL FOR THE OTHER BELT (EP6 pass 28), and the reason the field
    here is `segment_score` rather than the `tone_susceptibility` it used to
    be: that name is ON the denylist, so once the belt landed this test would
    have gone on passing while measuring the wrong belt entirely. A name the
    denylist has never heard of is the only input that can tell the closed set
    apart from the denylist -- without it, "the belt fired" and "anything
    unusual is refused" are the same observation.
    """
    wire = _wire(payload_fields={"segment_score": 0.8})
    with pytest.raises(WallProtocolError) as exc:
        SusceptibilityEstimator().observe_wire("c1", _msg(), wire)
    assert exc.value.reason == "UNKNOWN_FIELD"
    assert "segment_score" not in FORBIDDEN_TRUTH_FIELDS


# ── the SECOND BELT on this leg (EP6 pass 28) ────────────────────────────────
# WHY THIS BATTERY EXISTS. Until this pass the company's decode leg had NO
# non-derived check of any kind: its permitted key set is
# `get_type_hints(ConversationResponse)`, which WIDENS whenever that dataclass
# widens and is an R15 TAUTOLOGY for the question "could a real supplier know
# this". The world's encode leg has refused by name since it was built. That
# asymmetry left the seam carrying a customer's hidden latent traits defended
# only on the side that gets REPLACED at go-live -- and it was found by the
# census reporting its enforcer list, not by anything failing.


def test_every_forbidden_truth_field_is_refused_BY_NAME_and_not_merely_refused():
    """R10-shaped: the class fails, not one instance -- and the reason code is
    the load-bearing assertion, not the raise. Every one of these names was
    ALREADY refused by the closed set, so a bare `pytest.raises` (what this
    test asserted before pass 28) passed identically with no belt present at
    all. Asserting CONTRACT_VIOLATION is what makes the denylist the thing
    being measured."""
    for forbidden in FORBIDDEN_TRUTH_FIELDS:
        with pytest.raises(WallProtocolError) as exc:
            SusceptibilityEstimator().observe_wire(
                "c1", _msg(), _wire(payload_fields={forbidden: 0.9})
            )
        assert exc.value.reason == "CONTRACT_VIOLATION", forbidden
        assert forbidden in str(exc.value), forbidden


@pytest.fixture()
def widened_seam():
    """A WORLD THAT SHIPS THE ANSWER KEY. The one edit neither the closed set
    nor the derived hints can see: `framing_susceptibility` added to the
    response dataclass AND declared observable in the same change, so every
    check derived FROM the dataclass moves with it and stays green.

    A real dataclass, not a patched dict -- the decoder ends by calling
    `payload_type(**fields)`, so a hint map widened alone would be refused by
    the CONSTRUCTOR and every assertion below would be measuring Python rather
    than the wall. The trait is typed `int` (susceptibility in basis points)
    because this seam's field decoder declares no `float` branch, and a
    refusal on THAT would be a third unrelated reason.

    Yields the module, the leaky payload, and a callable that restores.
    """
    import dataclasses

    from company.comms import susceptibility_estimator as se

    tag = "ConversationResponse"
    base = se._OBSERVABLE_PAYLOAD_TYPES[tag]

    @dataclasses.dataclass(frozen=True)
    class LeakyResponse:
        response_id: str
        responds_to: str
        action: object
        channel_chosen: object
        latency: int
        responded_step: int
        framing_susceptibility: int

    hints = dict(se._OBSERVABLE_PAYLOAD_HINTS[tag])
    hints["framing_susceptibility"] = int

    original_type = base
    original_hints = se._OBSERVABLE_PAYLOAD_HINTS[tag]
    original_belt = se.FORBIDDEN_TRUTH_FIELDS
    se._OBSERVABLE_PAYLOAD_TYPES[tag] = LeakyResponse
    se._OBSERVABLE_PAYLOAD_HINTS[tag] = hints
    leaky = _wire(payload_fields={"framing_susceptibility": 87})["payload"]
    try:
        yield se, leaky, hints
    finally:
        se._OBSERVABLE_PAYLOAD_TYPES[tag] = original_type
        se._OBSERVABLE_PAYLOAD_HINTS[tag] = original_hints
        se.FORBIDDEN_TRUTH_FIELDS = original_belt


def test_MUTATION_a_trait_field_DECLARED_OBSERVABLE_in_the_same_edit_is_still_refused(
    widened_seam,
):
    """THE DOCTRINE MUTATION, and the only case that makes this belt worth
    having. The body asserts the DERIVED check is genuinely green on this
    payload first -- without that, the refusal could be the closed set firing
    and the belt could be absent entirely."""
    se, leaky, hints = widened_seam

    # THE DERIVED CHECK IS GREEN ON THIS PAYLOAD: no field absent, none extra.
    assert set(leaky["fields"]) == set(hints)

    with pytest.raises(WallProtocolError) as exc:
        se.decode_observable_payload(leaky)
    assert exc.value.reason == "CONTRACT_VIOLATION"
    assert "framing_susceptibility" in str(exc.value)


def test_MUTATION_without_the_belt_the_SAME_payload_is_ACCEPTED(widened_seam):
    """THE OTHER HALF, and what makes the half above a proof rather than an
    observation: same widened seam, denylist emptied, and the payload carrying
    a customer's hidden susceptibility scalar decodes CLEANLY into an object
    the company would go on to fold into its belief. That is the state this leg
    was in until pass 28, and it is what the belt -- and only the belt -- now
    stops."""
    se, leaky, _hints = widened_seam
    se.FORBIDDEN_TRUTH_FIELDS = ()

    decoded = se.decode_observable_payload(leaky)

    assert decoded.framing_susceptibility == 87, (
        "the belt is the only thing refusing this payload -- if it were "
        "redundant with the closed set, this line would never be reached"
    )


def test_the_belt_never_names_a_field_the_contract_declares_OBSERVABLE():
    """The list's own null control, and pass 27's `days_late` lesson applied
    here: a denylist that reds on a legal payload is one that gets RELAXED, and
    the relaxation takes the real entries with it. Every field of
    `ConversationResponse` is a DELIBERATE NON-MEMBER with a reason -- each is
    something a real supplier reads off its own contact-centre systems."""
    from interface.contracts.conversation_seam import OBSERVABLE_PAYLOAD_FIELDS

    why = {
        "response_id": "the company's own idempotency key for the inbound event",
        "responds_to": "the id of a message the company itself sent",
        "action": "what the customer was OBSERVED to do -- replied, paid, left",
        "channel_chosen": "which of its own lines the customer answered on",
        "latency": "how long the company waited before it saw an answer",
        "responded_step": "when the observed event landed on the company's clock",
        "message_id": "the company's own outbound id",
        "situation": "the reason the company chose to make contact",
        "channel": "the line the company chose to send on",
        "product": "what the company sells this customer",
        "tone": "a lever the company PICKED -- never the susceptibility to it",
        "framing": "the same, on the other lever",
        "emitted_step": "when the company sent it",
        "offer": "what the company offered",
    }
    for tag, fields in OBSERVABLE_PAYLOAD_FIELDS.items():
        for name in fields:
            assert name not in FORBIDDEN_TRUTH_FIELDS, (
                f"{tag}.{name} is declared observable AND forbidden -- one of "
                "the two is wrong and the belt will be relaxed to fix it"
            )
            assert name in why, f"{tag}.{name} has no stated reason to be observable"


def test_the_belt_is_read_from_the_CONTRACT_and_not_respelled_here():
    """R15 INDEPENDENCE. A decoder carrying its own copy of the denylist would
    agree with the contract on the day it was written and silently diverge
    after -- and the divergence is invisible, because both sides still refuse
    SOMETHING. The seam's tuple is the single source, imported by name."""
    import ast
    import pathlib

    source = pathlib.Path("company/comms/susceptibility_estimator.py").read_text()
    imported_from = {
        node.module
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.ImportFrom)
        and any(a.name == "FORBIDDEN_TRUTH_FIELDS" for a in node.names)
    }
    assert imported_from == {"interface.contracts.conversation_seam"}
    assert "FORBIDDEN_TRUTH_FIELDS: " not in source, (
        "the decoder declares its own denylist -- it must import the contract's"
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
