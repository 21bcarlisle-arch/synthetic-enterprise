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
    FORBIDDEN_TRUTH_FIELDS,
    Channel,
    ConversationMessage,
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


#: The participant this seam's replies arrive from, and the credential it
#: presents. HAND-WRITTEN LITERALS, not imported from
#: `simulation/conversation_response.py`: this file is the COMPANY's side, and a
#: fixture that reads the sender's own constants would prove the two agree with
#: themselves rather than that the company refuses a stranger (R15 TAUTOLOGY).
#: `tests/simulation/test_conversation_response.py` owns the cross-side fact
#: that the real counterparty presents exactly these.
_SENDER = "CONTACT-PLATFORM-01"
_CREDENTIAL = "contact-platform-01::participant-credential::v1"


def _envelope(**over):
    """A well-formed response DOCUMENT as the counterparty publishes it.
    Hand-written against the SCHEMA -- deliberately not produced by calling the
    sim's encoder, so a refusal proven here is a property of the decoder and not
    of the pair."""
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


def _wire(**over):
    """That document inside the transport FRAME -- what actually arrives at this
    seam since EP6 pass 67, and what every test below hands to `observe_wire`.

    Frame fields are overridable via `frame=` so a stranger, a forged credential
    or a missing frame key is one keyword rather than a hand-built dict; every
    other keyword still addresses the envelope, which is why the document-shaped
    tests above and below did not change when this seam was framed.
    """
    frame_over = over.pop("frame", {})
    frame = {
        "sender": _SENDER,
        "credential": _CREDENTIAL,
        "handed_over_at": "2026-01-01T12:00:00",
        "envelope": _envelope(**over),
    }
    frame.update(frame_over)
    return frame


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
    del wire["envelope"]["schema_version"]
    with pytest.raises(WallProtocolError) as exc:
        SusceptibilityEstimator().observe_wire("c1", _msg(), wire)
    assert exc.value.reason == "MISSING_FIELD"


# A version number this build genuinely does not speak. It was the LITERAL 2
# until EP6 pass 44, when the payment seam's release put 2 inside
# `SUPPORTED_SCHEMA_VERSIONS` and both tests below stopped refusing anything --
# one failed loudly (DID NOT RAISE) and the other would have gone quietly green
# on a message it was supposed to reject. The assertion under it is the repair
# that matters: a literal picked to be outside a set has to CHECK it is still
# outside that set, or it silently becomes a test of nothing the next time the
# set grows.
_UNSPOKEN_VERSION = 97


def test_the_unspoken_version_is_actually_unspoken():
    """The null control for the two tests below: if this build ever learns to
    speak `_UNSPOKEN_VERSION`, they are no longer testing a refusal and this
    says so instead of letting them pass vacuously."""
    from company.interfaces.wall_protocol import SUPPORTED_SCHEMA_VERSIONS

    assert _UNSPOKEN_VERSION not in SUPPORTED_SCHEMA_VERSIONS


def test_a_version_the_company_does_not_speak_is_refused_distinguishably():
    """"You speak a dialect I do not know" and "you did not say what you
    speak" are different failures calling for different repairs, so they carry
    different reasons."""
    with pytest.raises(WallProtocolError) as exc:
        SusceptibilityEstimator().observe_wire("c1", _msg(), _wire(schema_version=_UNSPOKEN_VERSION))
    assert exc.value.reason == "UNSUPPORTED_VERSION"


def test_a_refused_message_is_not_recorded_as_observed():
    """A refusal is NOT an observation. If a malformed delivery marked its
    `response_id` seen, the counterparty's CORRECTED re-delivery would be
    silently dropped as a duplicate -- a reply the company should have learned
    from, lost to a transport error."""
    est = SusceptibilityEstimator()
    with pytest.raises(WallProtocolError):
        est.observe_wire("c1", _msg(), _wire(schema_version=_UNSPOKEN_VERSION))
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
    del wire["envelope"]["payload"]["fields"]["latency"]
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
    leaky = _envelope(payload_fields={"framing_susceptibility": 87})["payload"]
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
    del wire["envelope"]["schema_version"]

    def observe_with_default(w):
        w = dict(w)
        w["envelope"] = dict(w["envelope"])
        w["envelope"].setdefault("schema_version", 1)   # the mutation
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
        body = w["envelope"]["payload"]["fields"]
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


# ── THE PARTICIPANT CHECK on this leg (EP6 pass 67, the blind review's Q13) ──
# WHY THIS BATTERY EXISTS. Every refusal above is about the DOCUMENT: its key
# set, its version, its payload's declared fields, its denylisted traits. A
# document cannot say who handed it over, so until this pass a correctly formed
# reply from ANY process that could put bytes in front of this seam became a
# belief -- and every check above stayed green while it did. The payment seam
# closed this at pass 39 and the flex seam at pass 53; this was the last live
# leg without it.
#
# THE MUTATION THAT MATTERS IS THE LAST ONE. Each refusal below could in
# principle be produced by some unrelated strictness, so the battery ends by
# running the OLD code path -- the bare decoder, on the same stranger's message
# -- and showing the belief folds. That is the difference between "this seam
# refuses some things" and "this refusal is the participant check".


def test_a_stranger_presenting_a_PERFECT_document_is_refused():
    """The whole exposure in one node: nothing is wrong with this message
    except who sent it.

    NULL CONTROL is the file's own happy path -- the byte-identical envelope
    from the registered sender updates the belief (first test in this file), so
    what this proves is the SENDER and not a newly strict decoder."""
    with pytest.raises(WallProtocolError) as exc:
        SusceptibilityEstimator().observe_wire(
            "c1", _msg(), _wire(frame={"sender": "SOMEONE-ELSE-01"})
        )
    assert exc.value.reason == "UNKNOWN_SENDER"
    assert "SOMEONE-ELSE-01" in str(exc.value)


def test_a_REGISTERED_sender_that_cannot_prove_it_is_refused():
    """Being named in the registry is not the check -- presenting the
    credential is. Without this, "sender" would be a field anyone could type.
    """
    with pytest.raises(WallProtocolError) as exc:
        SusceptibilityEstimator().observe_wire(
            "c1", _msg(), _wire(frame={"credential": _CREDENTIAL + "-forged"})
        )
    assert exc.value.reason == "BAD_CREDENTIAL"


def test_a_version_THIS_PARTICIPANT_is_not_on_is_refused_distinguishably():
    """Two different facts with two different repairs: `UNSUPPORTED_VERSION`
    means change the build, `VERSION_NOT_SPOKEN` means wait for that
    counterparty's cutover. The conversation platform is on v1 only, and 2 is
    inside `SUPPORTED_SCHEMA_VERSIONS` -- so this message is readable by this
    build and still wrong.

    NULL CONTROL: the assertion below checks 2 really is a version the build
    can read. The day the platform's row moves to v2, this stops testing a
    refusal and says so rather than passing vacuously."""
    from company.interfaces.wall_protocol import (
        CONVERSATION_PLATFORM_SENDER,
        COUNTERPARTY_REGISTRY,
        SUPPORTED_SCHEMA_VERSIONS,
    )

    assert 2 in SUPPORTED_SCHEMA_VERSIONS
    assert 2 not in COUNTERPARTY_REGISTRY[CONVERSATION_PLATFORM_SENDER].speaks_schema_versions

    with pytest.raises(WallProtocolError) as exc:
        SusceptibilityEstimator().observe_wire("c1", _msg(), _wire(schema_version=2))
    assert exc.value.reason == "VERSION_NOT_SPOKEN"


def test_an_UNFRAMED_message_is_refused_rather_than_read_as_a_document():
    """The pre-pass-67 wire shape, handed to the post-pass-67 seam. This is
    what a caller that quietly reverted the producer would deliver, and it is
    refused rather than parsed -- absence of a frame is never agreement."""
    with pytest.raises(WallProtocolError) as exc:
        SusceptibilityEstimator().observe_wire("c1", _msg(), _envelope())
    assert exc.value.reason in ("MISSING_FIELD", "UNKNOWN_FIELD", "MALFORMED_FIELD")


def test_a_frame_missing_a_key_is_refused_and_a_frame_with_an_EXTRA_one_too():
    """Exact key set on the frame, both directions, for the reason the envelope
    has one: a missing key would be defaulted and an extra key would be
    tolerated, and both are how a transport check stops checking."""
    short = _wire()
    del short["handed_over_at"]
    with pytest.raises(WallProtocolError):
        SusceptibilityEstimator().observe_wire("c1", _msg(), short)

    with pytest.raises(WallProtocolError):
        SusceptibilityEstimator().observe_wire(
            "c1", _msg(), _wire(frame={"relayed_by": "MITM-01"})
        )


def test_the_SENDER_is_checked_BEFORE_the_document_is_parsed():
    """Order is the point, not an implementation detail: a decoder that parses
    first and authenticates afterwards has already done the work an unknown
    sender wanted done.

    Constructed so the two answers differ. The message is from a stranger AND
    its envelope is missing `schema_version` -- a defect this file proves is
    refused as MISSING_FIELD when the sender is legitimate. Getting
    UNKNOWN_SENDER back is the evidence that no envelope field was read."""
    stranger = _wire(frame={"sender": "SOMEONE-ELSE-01"})
    del stranger["envelope"]["schema_version"]

    with pytest.raises(WallProtocolError) as exc:
        SusceptibilityEstimator().observe_wire("c1", _msg(), stranger)
    assert exc.value.reason == "UNKNOWN_SENDER"

    # NULL CONTROL: the same broken envelope from the REGISTERED sender is
    # refused for the envelope's reason, so the ordering above is a real
    # difference and not this seam having one error for everything.
    legitimate = _wire()
    del legitimate["envelope"]["schema_version"]
    with pytest.raises(WallProtocolError) as exc:
        SusceptibilityEstimator().observe_wire("c1", _msg(), legitimate)
    assert exc.value.reason == "MISSING_FIELD"


def test_R15_MUTATION_the_BARE_decoder_folds_the_strangers_reply_into_a_belief():
    """THE MUTATION, RUN NOT ASSERTED, and it is the code this pass replaced.

    `decode_response(wire["envelope"], ...)` is exactly what
    `observe_wire` did until pass 67. Run against the stranger's message the
    test above refuses, it decodes clean and the belief MOVES -- the company
    has learned something a process it has never heard of told it about one of
    its customers.

    NULL CONTROL: the shipped path refuses the same bytes. Without that line,
    "the bare decoder accepts this" and "this message is fine" would be the
    same observation.
    """
    from company.comms.susceptibility_estimator import decode_observable_payload
    from company.interfaces.wall_protocol import decode_response

    stranger = _wire(frame={"sender": "SOMEONE-ELSE-01", "credential": "anything"})

    # THE MUTATION: the old read, on the old shape, from an unknown participant.
    est = SusceptibilityEstimator()
    response = decode_response(
        stranger["envelope"], decode_payload=decode_observable_payload
    )
    assert est.observe_response("c1", _msg(), response.payload) is True
    assert est.posterior_report("c1")["framing_means"]["loss_framed"] > 0.5

    # THE CONTROL: the shipped path, same bytes, refused before the parse.
    with pytest.raises(WallProtocolError) as exc:
        SusceptibilityEstimator().observe_wire("c1", _msg(), stranger)
    assert exc.value.reason == "UNKNOWN_SENDER"
