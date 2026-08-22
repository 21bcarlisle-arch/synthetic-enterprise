"""F1a -- SIM customer response model, exit tests (each R15-provable).

The L2 exit test (proposal §4): *typed message->response over the wall;
susceptibility scales benchmarked uplift within published bands; response is a
distinct-in-time event.* The R15 MUTATION that must FAIL: *inject a shared-RNG
variant -> the C-S2 independence test fails (a new conversation draw shifts
another subsystem's output).* ``test_r15_shared_rng_mutation_breaks_isolation``
builds exactly that mutation and proves the isolation test catches it -- without
that passing test the C-S2 claim is theatre (R15 doctrine).

The model holds TRUTH behind the wall; these tests assert (a) it responds over
the typed contract, (b) the hidden susceptibility scales the uplift within the
nudge_physics published bands, (c) the response is a separate, later event
(C-S3), (d) draws are isolated named substreams (C-S2) and the response is a
pure function of (customer, message) (C-S1/replay), and (e) NO hidden trait
leaks onto the response.
"""
import datetime as dt
import random

import pytest

from interface.contracts.conversation_seam import (
    Channel,
    ConversationMessage,
    ConversationResponse,
    FORBIDDEN_TRUTH_FIELDS,
    Product,
    ResponseAction,
    Situation,
    validate_response_follows_message,
)
from interface.contracts.wall_envelope import WallResponse, WallStatus
from simulation import conversation_response as cr
from simulation.nudge_physics import (
    _MATCHED_FRAMING_UPLIFT_RANGE,
    _MATCHED_TONE_UPLIFT_RANGE,
    framing_effectiveness_multiplier,
    susceptibility_for,
    tone_effectiveness_multiplier,
    tone_susceptibility_for,
    FramingSusceptibility,
    ToneSusceptibility,
)


def _msg(
    situation=Situation.RENEWAL,
    channel=Channel.EMAIL,
    tone="neutral_toned",
    framing="neutral_framed",
    step=100,
    mid="M1",
    product=Product.DUAL_FUEL,
    offer=None,
):
    return ConversationMessage(
        message_id=mid,
        situation=situation,
        channel=channel,
        product=product,
        tone=tone,
        framing=framing,
        emitted_step=step,
        offer=offer,
    )


def _loss_averse_customer(prefix="LA"):
    for i in range(2000):
        cid = f"{prefix}{i}"
        if susceptibility_for(cid) == FramingSusceptibility.LOSS_AVERSE:
            return cid
    raise AssertionError("no loss-averse customer found in sweep")


def _empathetic_customer(prefix="EM"):
    for i in range(2000):
        cid = f"{prefix}{i}"
        if tone_susceptibility_for(cid) == ToneSusceptibility.EMPATHETIC_RESPONSIVE:
            return cid
    raise AssertionError("no empathetic-responsive customer found in sweep")


# ── 1. Typed message -> response over the wall (exit test, part 1) ────────────

def test_respond_returns_typed_conversation_response():
    resp = cr.respond("C1", _msg())
    assert isinstance(resp, ConversationResponse)
    assert resp.responds_to == "M1"
    assert resp.action in set(ResponseAction)


def test_respond_over_wall_wraps_in_typed_envelope():
    msg = _msg()
    env = cr.respond_over_wall(
        "C1", msg, correlation_id="corr-1", observed_at=dt.datetime(2026, 7, 23, 9, 0)
    )
    assert isinstance(env, WallResponse)
    assert env.status == WallStatus.OK
    assert env.correlation_id == "corr-1"
    assert isinstance(env.payload, ConversationResponse)
    # Envelope carries no payload leak of hidden truth; the pairing is valid.
    validate_response_follows_message(msg, env.payload)


def test_action_is_valid_for_every_situation():
    # Every situation resolves to a representable action across a customer sweep.
    for situation in Situation:
        for i in range(50):
            resp = cr.respond(f"S{i}", _msg(situation=situation, mid=f"{situation.value}:{i}"))
            assert resp.action in set(ResponseAction)


# ── 2. Susceptibility scales uplift WITHIN published bands (exit test, part 2) ─

def test_matched_framing_lifts_positive_probability_within_published_band():
    cid = _loss_averse_customer()
    neutral = cr.positive_action_probability(cid, _msg(framing="neutral_framed"))
    matched = cr.positive_action_probability(cid, _msg(framing="loss_framed"))
    assert matched > neutral, "matched framing must lift the positive probability"
    # The lift ratio is exactly the nudge_physics multiplier -> within its band.
    ratio = matched / neutral
    lo, hi = _MATCHED_FRAMING_UPLIFT_RANGE
    assert ratio == pytest.approx(framing_effectiveness_multiplier(cid, "loss_framed"))
    assert 1.0 + lo <= ratio <= 1.0 + hi


def test_mismatched_framing_gives_no_lift():
    cid = _loss_averse_customer()
    neutral = cr.positive_action_probability(cid, _msg(framing="neutral_framed"))
    # A loss-averse customer sent the GAIN frame gets no lift (mismatch -> 1.0).
    mismatched = cr.positive_action_probability(cid, _msg(framing="gain_framed"))
    assert mismatched == pytest.approx(neutral)


def test_matched_tone_lifts_payment_probability_within_published_band():
    cid = _empathetic_customer()
    # Isolate the tone lever from budget stress by comparing matched vs neutral
    # for the SAME customer (the budget-stress haircut is identical in both).
    neutral = cr.positive_action_probability(cid, _msg(situation=Situation.MISSED_PAYMENT, tone="neutral_toned"))
    matched = cr.positive_action_probability(cid, _msg(situation=Situation.MISSED_PAYMENT, tone="empathetic_toned"))
    assert matched > neutral
    ratio = matched / neutral
    lo, hi = _MATCHED_TONE_UPLIFT_RANGE
    assert ratio == pytest.approx(tone_effectiveness_multiplier(cid, "empathetic_toned"))
    assert 1.0 + lo <= ratio <= 1.0 + hi


def test_positive_probability_saturates_at_one():
    # Even with a maximal matched lever the probability can never exceed 1.0.
    for i in range(500):
        cid = _loss_averse_customer(prefix=f"SAT{i}_")
        p = cr.positive_action_probability(cid, _msg(situation=Situation.INBOUND_COMPLAINT, tone="empathetic_toned"))
        assert 0.0 <= p <= 1.0


def test_matched_framing_raises_realised_positive_action_rate():
    # Population-level: matched framing produces MORE positive actions than the
    # mismatched frame across loss-averse customers (the uplift is real, not
    # just a probability arithmetic).
    matched_hits = mismatched_hits = 0
    n = 0
    for i in range(4000):
        cid = f"POP{i}"
        if susceptibility_for(cid) != FramingSusceptibility.LOSS_AVERSE:
            continue
        n += 1
        pos = _SITUATION_positive(Situation.RENEWAL)
        if cr.respond(cid, _msg(framing="loss_framed", mid=f"m{cid}")).action == pos:
            matched_hits += 1
        if cr.respond(cid, _msg(framing="gain_framed", mid=f"g{cid}")).action == pos:
            mismatched_hits += 1
    assert n > 100
    assert matched_hits > mismatched_hits


def _SITUATION_positive(situation):
    return cr._SITUATION_PROFILE[situation].positive_action


# ── 3. C-S3 async: response is a distinct, LATER event ────────────────────────

def test_response_is_a_distinct_later_event():
    msg = _msg(step=100)
    resp = cr.respond("C1", msg)
    assert resp.latency >= 1
    assert resp.responded_step == msg.emitted_step + resp.latency
    assert resp.responded_step > msg.emitted_step
    validate_response_follows_message(msg, resp)  # would raise on a same-step reply


def test_no_reply_is_still_a_later_event():
    # A NO_REPLY is observed only after the situation's silence-timeout window --
    # still strictly later in time (a non-response is an event too).
    found = False
    for i in range(500):
        msg = _msg(situation=Situation.WIN_BACK, mid=f"nr{i}", step=10)
        resp = cr.respond(f"NR{i}", msg)
        if resp.action == ResponseAction.NO_REPLY:
            found = True
            assert resp.responded_step > msg.emitted_step
            assert resp.latency >= 1
    assert found, "expected some NO_REPLY responses on the hard win-back situation"


def test_letter_channel_answers_slower_than_sms():
    # Declared per-channel latency offset (C-S5): a letter lands slower than SMS.
    sms = cr._latency_steps("C1", _msg(channel=Channel.SMS), ResponseAction.REPLY)
    letter = cr._latency_steps("C1", _msg(channel=Channel.LETTER), ResponseAction.REPLY)
    assert letter > sms


# ── 4. C-S2 replay / idempotency + C-S1 order-independence ────────────────────

def test_respond_is_deterministic_replay():
    msg = _msg(mid="REPLAY")
    a = cr.respond("Cdet", msg)
    b = cr.respond("Cdet", msg)
    assert a == b


def test_respond_is_independent_of_processing_order():
    # C-S1: the response for one customer does not depend on whether another was
    # processed first -- pure function of (customer, message).
    msg_a = _msg(mid="A", situation=Situation.RENEWAL)
    msg_b = _msg(mid="B", situation=Situation.MISSED_PAYMENT)
    a_first = cr.respond("CA", msg_a)
    # Process a batch of other customers/messages in between.
    for i in range(200):
        cr.respond(f"noise{i}", _msg(mid=f"n{i}"))
    a_again = cr.respond("CA", msg_a)
    _ = cr.respond("CB", msg_b)
    assert a_first == a_again


def test_substream_names_are_unique():
    assert len(cr._CONVERSATION_SUBSTREAMS) == len(set(cr._CONVERSATION_SUBSTREAMS))


def test_substream_value_is_stable_across_processes():
    # sha256-derived, NOT Python's salted hash(): a regression to a salted seed
    # would break C-S2 replay and fail this exact value.
    assert round(cr._substream(12345, "conversation_positive").random(), 12) == 0.914491956426


# ── 5. THE R15 mutation: a shared/global RNG variant must FAIL isolation ──────

def test_conversation_draw_does_not_shift_another_subsystems_stream():
    # The headline C-S2 guarantee: heavy conversation draws for a base_seed leave
    # an UNRELATED subsystem's named substream (here, a life-event-style name)
    # byte-for-byte unchanged, because each name seeds an independent generator.
    base = 424242
    before = [cr._substream(base, "job_loss").random() for _ in range(50)]
    _ = [cr._substream(base, "conversation_positive").random() for _ in range(500)]
    _ = [cr._substream(base, "conversation_adverse").random() for _ in range(500)]
    after = [cr._substream(base, "job_loss").random() for _ in range(50)]
    assert before == after, "a conversation draw shifted another subsystem's stream"


def test_r15_shared_rng_mutation_breaks_isolation():
    """R15 mutation: replace the per-(customer,message) named substream design
    with a SHARED process-global RNG the way the pre-C-S2 code did. Under that
    mutation a customer's response depends on how many OTHER conversations were
    drawn first -- the isolation/replay property the real design guarantees is
    violated, and this test proves the guard catches it.

    The REAL design passes ``test_respond_is_independent_of_processing_order``;
    the mutation below must make an equivalent assertion FAIL."""

    shared = random.Random(0)

    def mutated_respond(customer_id, message):
        # A shared, order-sensitive stream -- the exact C-S2 violation. Each call
        # advances the ONE process-global stream, so repeating the SAME
        # (customer, message) yields DIFFERENT results (replay is broken).
        profile = cr._SITUATION_PROFILE[message.situation]
        if shared.random() < cr.positive_action_probability(customer_id, message):
            action = profile.positive_action
        elif shared.random() < cr._adverse_share(customer_id, message):
            action = profile.adverse_action
        else:
            action = ResponseAction.NO_REPLY
        return action

    msg_a = _msg(mid="A", situation=Situation.RENEWAL)

    # REAL design: respond is a pure function of (customer, message) -- repeating
    # the identical call N times gives ONE distinct result (C-S2 replay holds).
    real_distinct = {cr.respond("CA", msg_a).action for _ in range(40)}
    assert len(real_distinct) == 1, "real design must be a pure function (replay stable)"

    # MUTATION: the shared RNG advances every call, so the SAME (customer,
    # message) resolves to MORE THAN ONE result across N draws -- replay/
    # isolation is broken, and the guard above catches exactly this. (With
    # RENEWAL base ~0.30 the chance all 40 coincide is < 1e-6.)
    mutated_distinct = {mutated_respond("CA", msg_a) for _ in range(40)}
    assert len(mutated_distinct) > 1, (
        "shared-RNG mutation did not break replay isolation -- the C-S2 guard "
        "would be theatre (R15). The real named-substream design keeps it stable."
    )


# ── 6. Epistemic wall: NO hidden trait leaks onto the response ────────────────

def test_response_carries_no_forbidden_truth_field():
    resp = cr.respond("Cwall", _msg())
    fields = {f.lower() for f in resp.__dataclass_fields__}
    for forbidden in FORBIDDEN_TRUTH_FIELDS:
        assert forbidden.lower() not in fields, (
            f"response leaked a hidden trait field: {forbidden}"
        )


def test_module_imports_no_company_or_saas():
    import inspect

    src = inspect.getsource(cr)
    assert "import company" not in src and "from company" not in src
    assert "import saas" not in src and "from saas" not in src


# ── 7. Sanity: hidden traits shape behaviour but stay behind the wall ─────────

def test_budget_stress_reduces_pay_probability(monkeypatch):
    # The tone lever cannot fix a real inability to pay: for ONE customer,
    # raising the hidden budget stress lowers the matched-tone PAY probability.
    # Isolated by monkeypatching the hidden trait on a single customer, so the
    # per-customer tone-uplift multiplier is held constant.
    cid = _empathetic_customer()
    msg = _msg(situation=Situation.MISSED_PAYMENT, tone="empathetic_toned")
    monkeypatch.setattr(cr, "_budget_stress", lambda c: 0.0)
    p_no_stress = cr.positive_action_probability(cid, msg)
    monkeypatch.setattr(cr, "_budget_stress", lambda c: 1.0)
    p_full_stress = cr.positive_action_probability(cid, msg)
    assert p_full_stress < p_no_stress
    # ~40% haircut at maximal stress (declared in positive_action_probability).
    assert p_full_stress == pytest.approx(p_no_stress * 0.6)


# ── 8. R15 audit (2026-07-30 BUILD pass): mutation-prove each control ─────────
#
# CLAUDE.md R15 doctrine: no control counts as evidence unless a MUTATION
# TEST proves it fires on its own named defect. The three tests below prove
# (a) the wall guard would catch an injected truth field on the response
# shape, (b) this module's own latency clamp is load-bearing -- if it
# regressed, the seam's construction-time C-S3 guard stops a same-step reply
# leaving ``respond()`` rather than silently returning one, and (c) the
# standing NaN-blindness killer pattern is closed: a non-finite lever
# multiplier is rejected loudly, before it can silently mis-route a customer
# via a NaN comparison (comparisons against NaN are always False in Python).


def test_r15_added_truth_field_would_be_caught_by_wall_guard():
    """R15 mutation (a), the wall guard: prove the field-name check used by
    ``test_response_carries_no_forbidden_truth_field`` is not tautological --
    it must FIRE on a mutant response shape that leaks a hidden trait, and
    still PASS on the real (unmutated) ``respond()`` output. Without the
    positive (catches-the-mutant) half, the negative-only check above would
    be theatre: it would pass equally on a real design and a broken one that
    simply never happened to add a forbidden field name."""
    from dataclasses import dataclass as _dc, fields as _fields

    @_dc(frozen=True)
    class _MutantResponseWithLeakedTrust:
        response_id: str
        responds_to: str
        action: ResponseAction
        channel_chosen: Channel
        latency: int
        responded_step: int
        trust: float  # the injected hidden-trait leak

    mutant_fields = {f.name.lower() for f in _fields(_MutantResponseWithLeakedTrust)}
    leaked = {f for f in FORBIDDEN_TRUTH_FIELDS if f.lower() in mutant_fields}
    assert leaked, (
        "R15: the wall guard's field-name check failed to catch an injected "
        "truth field on a mutant response shape -- it would be theatre"
    )

    # The REAL, unmutated response must still pass the identical check.
    real_fields = {f.lower() for f in cr.respond("Cwall2", _msg()).__dataclass_fields__}
    assert not (set(f.lower() for f in FORBIDDEN_TRUTH_FIELDS) & real_fields)


def test_r15_broken_latency_clamp_mutation_is_caught_at_construction(monkeypatch):
    """R15 mutation (b), the C-S3 guard: if this module's own ``max(1, ...)``
    latency clamp in ``_latency_steps`` ever regressed to allow a same-step
    (zero) value, the seam's construction-time guard
    (``ConversationResponse.__post_init__``, ``latency <= 0`` rejected) must
    catch it before a same-step reply can leave ``respond()`` -- proving the
    clamp is load-bearing, not decorative, and that removing it fails LOUDLY
    (a raised ``ValueError``), never silently."""
    monkeypatch.setattr(cr, "_latency_steps", lambda *a, **k: 0)
    with pytest.raises(ValueError):
        cr.respond("Cmut", _msg())


def test_r15_nonfinite_positive_probability_rejected_before_comparison(monkeypatch):
    """R15 mutation (c-i), NaN-blindness: if a matched-lever multiplier ever
    produced a non-finite value (NaN/inf -- e.g. a future div-by-zero-width
    band bug), the OLD unguarded code path
    (``_substream(...).random() < positive_action_probability(...)``) would
    silently misroute the customer: ``min(nan, 1.0)`` is itself ``nan``, and
    ``x < nan`` is ALWAYS False in Python, so a corrupted probability would
    silently steer every customer away from the positive action without ever
    raising -- fail-silent, one of the R15 standing killer patterns. The
    guard added to ``positive_action_probability`` must reject it FIRST,
    loudly, before any comparison or clamp."""
    monkeypatch.setattr(cr, "framing_effectiveness_multiplier", lambda *a, **k: float("nan"))
    with pytest.raises(ValueError):
        cr.positive_action_probability("Cnan1", _msg(situation=Situation.RENEWAL, framing="loss_framed"))


def test_r15_nonfinite_adverse_share_rejected_before_comparison(monkeypatch):
    """R15 mutation (c-ii), NaN-blindness on the adverse-share path: a
    non-finite hidden ``_trust`` value must be rejected by ``_adverse_share``
    before its own comparison/clamp (``max(0.0, min(nan, 1.0))`` is itself
    ``nan``), the same standing pattern as the positive-probability guard
    above."""
    monkeypatch.setattr(cr, "_trust", lambda c: float("inf"))
    with pytest.raises(ValueError):
        cr._adverse_share("Cnan2", _msg(situation=Situation.RENEWAL))


# ===========================================================================
# THE WIRE (atom EP6_wall_protocol_typing, 2026-08-20) -- the counterparty's
# own codec, both legs.
#
# What these prove, and what they deliberately do NOT: they prove this module
# puts a version-bearing message on the wire and refuses a malformed one
# coming back the other way. They do NOT prove the far side agrees -- that is
# a cross-side fact and lives in
# `tests/background/test_conversation_gap_ledger_wire.py`, because a test that
# encoded and decoded with the same module's code would be an R15 TAUTOLOGY:
# green through any schema change, since both halves changed together.
# ===========================================================================


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


def _framed_response(customer="Cwire1", mid="MW1", corr="corr-1"):
    """What this counterparty actually hands over: an envelope inside its
    transport frame (EP6 pass 67)."""
    return cr.respond_over_wire(
        customer, _msg(mid=mid), correlation_id=corr,
        observed_at=dt.datetime(2026, 1, 1, 12, 0),
    )


def _wire_response(customer="Cwire1", mid="MW1", corr="corr-1"):
    """The ENVELOPE inside that frame -- the subject of every envelope-shaped
    assertion below. Kept as its own helper rather than inlining `["envelope"]`
    at each site, so framing the seam did not turn a dozen document assertions
    into assertions about the frame."""
    return _framed_response(customer, mid, corr)["envelope"]


def test_the_handed_over_message_is_FRAMED_and_names_this_participant():
    """Q13's sender half for the conversation seam, and the last of the three
    live seams to get it (EP6 pass 67). A document says what happened; only the
    frame says WHO says so."""
    framed = _framed_response()
    assert set(framed) == {"sender", "credential", "envelope", "handed_over_at"}
    assert framed["sender"] == cr.PARTICIPANT_ID
    assert framed["credential"] == cr.PARTICIPANT_CREDENTIAL
    assert framed["envelope"]["correlation_id"] == "corr-1"


def test_the_company_holds_only_a_FINGERPRINT_of_this_participants_credential():
    """The check is a real one and not a handshake with itself: the receiver
    stores sha256 of this string and never the string.

    THE FINGERPRINT IS COMPUTED HERE, never imported from the receiver's
    registry -- reading the company's stored value and comparing it to itself
    would be the R15 TAUTOLOGY this whole seam is built to refuse. What is
    imported is the registry ROW, which is the thing under test."""
    import hashlib

    from company.interfaces.wall_protocol import (
        CONVERSATION_PLATFORM_SENDER,
        COUNTERPARTY_REGISTRY,
    )

    record = COUNTERPARTY_REGISTRY[CONVERSATION_PLATFORM_SENDER]
    assert cr.PARTICIPANT_ID == CONVERSATION_PLATFORM_SENDER
    assert record.credential_sha256 == hashlib.sha256(
        cr.PARTICIPANT_CREDENTIAL.encode("utf-8")
    ).hexdigest()
    # And the credential itself is NOT what the company holds -- the failing
    # shape this assertion exists to exclude.
    assert cr.PARTICIPANT_CREDENTIAL != record.credential_sha256


def test_a_frame_with_no_hand_over_time_is_UNSENDABLE_not_defaulted():
    """`handed_over_at` has no default, and the reason is the payment seam's:
    "now" would make every historical replay claim it was delivered at import
    time, and defaulting it to `observed_at` would make a prompt hand-over
    unfalsifiable by construction.

    NULL CONTROL: the same call WITH a datetime frames cleanly, so what this
    proves is the missing argument and not a broken framer."""
    with pytest.raises(TypeError):
        cr.frame_wire_message({"correlation_id": "c"})
    assert cr.frame_wire_message(
        {"correlation_id": "c"}, handed_over_at=dt.datetime(2026, 1, 1)
    )["envelope"] == {"correlation_id": "c"}


def test_a_non_datetime_hand_over_and_a_non_envelope_are_both_refused():
    """Fail-closed on both arguments: a frame built from junk is a frame that
    would be refused at the far side for the wrong reason."""
    with pytest.raises(cr.SeamCodecError):
        cr.frame_wire_message("not a dict", handed_over_at=dt.datetime(2026, 1, 1))
    with pytest.raises(cr.SeamCodecError):
        cr.frame_wire_message({"correlation_id": "c"}, handed_over_at="2026-01-01")


def test_the_encoded_response_states_every_envelope_field_including_its_nulls():
    """ABSENCE IS NEVER AGREEMENT: a wire message states its whole envelope,
    nulls included. A key omitted because "it is None anyway" is a key the far
    side must either refuse or default, and defaulting is the fail-open this
    seam exists to make impossible."""
    wire = _wire_response()
    assert set(wire) == {
        "correlation_id", "status", "schema_version",
        "observed_at", "valid_time", "payload", "error",
    }
    assert wire["valid_time"] is None and "valid_time" in wire
    assert wire["error"] is None and "error" in wire


def test_the_version_is_on_the_wire_and_comes_from_the_contract():
    """The whole point of the atom for this seam: `schema_version` is not a
    field populated at construction and left in the process -- it is IN the
    message, and its value is the CONTRACT's constant, never a reader's own
    default at read time."""
    from interface.contracts.conversation_seam import SCHEMA_VERSION
    assert _wire_response()["schema_version"] == SCHEMA_VERSION


def test_the_encoder_PRESERVES_a_foreign_vintage_instead_of_relabelling_it():
    """R10 sibling of the same class fix landed in `sim.flex_dispatch` and
    `simulation.payment_seam_adapter` (EP6 pass 44): all three world-side seam
    encoders wrote their OWN `SCHEMA_VERSION` and discarded the message's.

    The test above cannot see that defect and never could, because its fixture
    stamps the module constant -- the one input on which a preserving and a
    relabelling encoder agree. It would have stayed green through the whole
    class. This is its null-differentiating twin: a response whose vintage is
    deliberately NOT the current constant, which is the only message that can
    tell the two implementations apart. Without it, the decoder's version check
    could never fire on anything this seam emitted -- an encoder that overwrites
    the stamp makes the field structurally unable to differ from the reader's.

    Fixed here rather than filed because R10 forbids closing a class defect with
    an instance fix, and this seam is one of the three instances.
    """
    import dataclasses as _dc

    from interface.contracts.conversation_seam import SCHEMA_VERSION
    built = cr.respond_over_wall(
        "Cwire1", _msg(mid="MW1"), correlation_id="corr-1",
        observed_at=dt.datetime(2026, 1, 1, 12, 0),
    )
    foreign = _dc.replace(built, schema_version=7)
    assert cr.encode_wall_response(foreign)["schema_version"] == 7
    # NULL CONTROL: 7 is chosen for being a vintage this seam does not speak. The
    # day the constant reaches it, the assertion above tests nothing and this
    # line is what says so rather than letting it go quietly green.
    assert SCHEMA_VERSION != 7


def test_the_wire_message_is_json_round_trippable():
    """A wire form that cannot survive JSON is not a wire form. Everything on
    it must be a primitive: no enum objects, no datetimes, no dataclasses."""
    import json
    wire = _wire_response()
    assert json.loads(json.dumps(wire)) == wire


def test_the_payload_is_tagged_with_its_declared_contract_type():
    wire = _wire_response()
    assert wire["payload"]["payload_type"] == "ConversationResponse"
    assert set(wire["payload"]["fields"]) == {
        "response_id", "responds_to", "action", "channel_chosen",
        "latency", "responded_step",
    }


def test_the_encoder_refuses_a_payload_the_contract_does_not_declare():
    """An encoder that can serialise anything is the mirror of a decoder that
    can accept anything. The permitted set is read from the contract's
    OBSERVABLE_RESPONSE_PAYLOAD_TYPES, so it grows with the contract and not
    with this module."""
    with pytest.raises(cr.SeamCodecError):
        cr.encode_observable_payload(_msg())          # a MESSAGE is not an observable


def test_the_encoder_refuses_a_bool_where_the_contract_declares_an_int():
    """bool is an int subclass, so a True latency would encode as `true` and
    decode back as 1 -- a value the far side would accept and act on. The
    boundary the rule is most easily wrong about."""
    with pytest.raises(cr.SeamCodecError):
        cr._encode_scalar(True, "ConversationResponse.latency")
    assert cr._encode_scalar(11, "ConversationResponse.latency") == 11


def test_no_hidden_trait_reaches_the_wire():
    """The epistemic wall, asserted on the BYTES rather than on the object.
    The contract's FORBIDDEN_TRUTH_FIELDS check proves no such FIELD exists;
    this proves the encoder invented no such KEY on the way out."""
    fields_on_wire = _wire_response()["payload"]["fields"]
    for forbidden in FORBIDDEN_TRUTH_FIELDS:
        assert forbidden not in fields_on_wire


# -- the inbound leg: the counterparty receiving the company's message -------


def _wire_request(**over):
    base = {
        "correlation_id": "corr-1",
        "request_type": "conversation_message",
        "schema_version": 1,
        "as_of": "2026-01-01T09:00:00",
        "emitted_at": "2026-01-01T09:30:00",
        "payload": {
            "payload_type": "ConversationMessage",
            "fields": {
                "message_id": "MW1", "situation": "renewal", "channel": "email",
                "product": "dual_fuel", "tone": "neutral_toned",
                "framing": "neutral_framed", "emitted_step": 100, "offer": None,
            },
        },
    }
    base.update(over)
    return base


def test_a_well_formed_request_decodes_to_the_typed_envelope():
    request = cr.decode_wire_request(_wire_request())
    assert request.correlation_id == "corr-1"
    assert request.schema_version == 1
    assert request.payload == _msg(mid="MW1")


def test_a_request_missing_its_version_is_refused_not_defaulted():
    """The named defect this whole module exists against: `entry.get("field",
    MY_OWN_CONSTANT)`. An absent field and an agreeing field are the same
    bytes, so a version that can be defaulted is not a version."""
    wire = _wire_request()
    del wire["schema_version"]
    with pytest.raises(cr.SeamCodecError, match="schema_version"):
        cr.decode_wire_request(wire)


def test_a_version_this_seam_does_not_speak_is_refused():
    with pytest.raises(cr.SeamCodecError, match="not the 1 this seam speaks"):
        cr.decode_wire_request(_wire_request(schema_version=2))


def test_a_boolean_version_is_malformed_not_version_one():
    """`True == 1` in Python, so a bool version would pass an `== 1` check and
    be read as v1. It is a malformed field, not a version."""
    with pytest.raises(cr.SeamCodecError, match="must be an int"):
        cr.decode_wire_request(_wire_request(schema_version=True))


def test_an_unknown_key_is_refused_rather_than_tolerated():
    """A schema that grew announces itself by its VERSION, never by a key
    appearing quietly -- otherwise the version number has no job."""
    with pytest.raises(cr.SeamCodecError, match="does not define"):
        cr.decode_wire_request(_wire_request(extra_field="hello"))


def test_a_missing_payload_field_is_refused_never_defaulted():
    wire = _wire_request()
    del wire["payload"]["fields"]["framing"]
    with pytest.raises(cr.SeamCodecError, match="omits required field"):
        cr.decode_wire_request(wire)


def test_the_optional_field_accepts_null_and_the_required_ones_do_not():
    """BOUNDARY: `offer` is `Optional[str]` in the contract and `tone` is not.
    A decoder that treated every null alike would either refuse every
    offer-less message (most situations carry no offer) or silently accept a
    tone-less one. The difference is read from the contract's own type hints."""
    assert cr.decode_wire_request(_wire_request()).payload.offer is None
    wire = _wire_request()
    wire["payload"]["fields"]["tone"] = None
    with pytest.raises(cr.SeamCodecError, match="contract declares it required"):
        cr.decode_wire_request(wire)


def test_an_enum_value_off_the_contract_is_refused():
    wire = _wire_request()
    wire["payload"]["fields"]["situation"] = "not_a_situation"
    with pytest.raises(cr.SeamCodecError, match="is not one of"):
        cr.decode_wire_request(wire)


def test_a_non_message_is_refused_rather_than_read_as_empty():
    for junk in (None, "a string", 7, ["a", "list"]):
        with pytest.raises(cr.SeamCodecError):
            cr.decode_wire_request(junk)


def test_bytes_in_bytes_out_is_the_whole_crossing():
    """`respond_to_wire_request` is the shape a real counterparty presents: it
    never sees or returns an in-process envelope object."""
    out = cr.respond_to_wire_request("Cwire2", _wire_request())
    assert isinstance(out, dict) and out["envelope"]["correlation_id"] == "corr-1"
    assert out["envelope"]["payload"]["fields"]["responds_to"] == "MW1"


def test_the_answer_is_a_separate_later_event_on_the_wire_too():
    """C-S3 survives serialisation: `responded_step` strictly exceeds the
    message's `emitted_step` in the encoded bytes, not just in the object."""
    out = cr.respond_to_wire_request("Cwire3", _wire_request())["envelope"]
    assert out["payload"]["fields"]["responded_step"] > 100
    assert out["payload"]["fields"]["latency"] >= 1


def test_R15_MUTATION_defaulting_the_absent_version_makes_the_refusal_vanish():
    """The mutation this seam's decoder exists to fail, RUN not asserted.

    Replace the version read with the sibling `from_log_entry` pattern --
    `wire.get("schema_version", SCHEMA_VERSION)` -- and a message that never
    stated its version decodes CLEAN, silently relabelled as the one version
    this process happens to speak today. That is the exact fail-open the
    module docstring names.

    NULL CONTROL: the same wrapper WITHOUT the default leaves the refusal
    intact, so what the mutation proves is the defaulting and not the wrapping.
    """
    wire = _wire_request()
    del wire["schema_version"]

    def decode_with_default(w):
        w = dict(w)
        w.setdefault("schema_version", 1)             # the mutation
        return cr.decode_wire_request(w)

    def decode_without_default(w):
        return cr.decode_wire_request(dict(w))        # the null control

    assert decode_with_default(wire).schema_version == 1     # mutation: accepted
    with pytest.raises(cr.SeamCodecError):
        decode_without_default(wire)                          # control: still refused


def test_R15_MUTATION_a_lenient_superset_check_would_accept_a_widened_message():
    """EXCUSE-EVERYTHING: relax the exact-key-set rule to "the required keys
    are present" and a message carrying an undeclared extra key sails through.
    A decoder that tolerates keys it does not understand cannot tell a v2
    counterparty from a v1 one, which is the negotiation the version exists
    for."""
    widened = _wire_request(unknown_key="from a future schema")

    def lenient(w):
        missing = cr._REQUEST_WIRE_FIELDS - set(w)
        assert not missing                            # the mutation: subset check only
        return True

    assert lenient(widened) is True                   # mutation: accepted
    with pytest.raises(cr.SeamCodecError):
        cr.decode_wire_request(widened)               # shipped rule: refused


def test_the_module_still_imports_nothing_from_the_company_side():
    """The counterparty writes its OWN codec, and this is the rule that makes
    that non-negotiable rather than stylistic: a mock that encoded with the
    company's encoder would make every round-trip a tautology, and a real
    customer-contact platform never links the supplier's library."""
    assert _imported_roots("simulation/conversation_response.py").isdisjoint(
        {"company", "saas"}
    )


# ---------------------------------------------------------------------------
# The CLOSED observable field set (EP6 pass 25). Before it, this seam's ENCODE
# leg had no field-level scrutiny at all -- FORBIDDEN_TRUTH_FIELDS was checked
# only by tests, and only against names someone had predicted. A latent trait
# under an unpredicted name crossed to the company.
# ---------------------------------------------------------------------------


def _response_shaped(**extra):
    """A ConversationResponse-shaped payload under the REAL type name, because
    the mutation modelled is someone editing the real class."""
    import dataclasses

    from interface.contracts.conversation_seam import Channel, ResponseAction

    dropped = extra.pop("_drop", ())
    base = [
        ("response_id", str), ("responds_to", str), ("action", ResponseAction),
        ("channel_chosen", Channel), ("latency", int), ("responded_step", int),
    ]
    base = [f for f in base if f[0] not in dropped]
    return dataclasses.make_dataclass(
        "ConversationResponse", base + [(n, float) for n in extra], frozen=True
    )


def _encode_conv(mutant_type, monkeypatch, **values):
    import simulation.conversation_response as _cr

    registry = dict(_cr._ENCODABLE_RESPONSE_PAYLOAD_TYPES)
    registry["ConversationResponse"] = mutant_type
    monkeypatch.setattr(_cr, "_ENCODABLE_RESPONSE_PAYLOAD_TYPES", registry)
    return _cr.encode_observable_payload(mutant_type(**values))


_BASE_RESPONSE = dict(response_id="r1", responds_to="m1", latency=2, responded_step=7)


def _enums():
    from interface.contracts.conversation_seam import Channel, ResponseAction

    return dict(action=ResponseAction.REPLY, channel_chosen=Channel.EMAIL)


def test_null_control_the_declared_response_still_crosses():
    """The control must admit the real thing, or refusing proves nothing."""
    from interface.contracts.conversation_seam import ConversationResponse
    from simulation.conversation_response import encode_observable_payload

    wire = encode_observable_payload(
        ConversationResponse(**_BASE_RESPONSE, **_enums())
    )
    assert set(wire["fields"]) == {
        "response_id", "responds_to", "action", "channel_chosen",
        "latency", "responded_step",
    }


def test_mutation_a_latent_trait_under_an_unpredicted_name_is_refused(monkeypatch):
    """THE named defect. `propensity_scalar` is a hidden trait by meaning and is
    on NO denylist -- the closed set refuses it for never having been declared
    observable, which is the R10 form: the class fails, not the instance."""
    from interface.contracts.conversation_seam import FORBIDDEN_TRUTH_FIELDS
    from simulation.conversation_response import SeamCodecError

    assert "propensity_scalar" not in FORBIDDEN_TRUTH_FIELDS, (
        "this test's point is a trait the DENYLIST cannot see; if it is now "
        "listed, pick another unpredicted trait name"
    )
    mutant = _response_shaped(propensity_scalar=float)
    with pytest.raises(SeamCodecError, match="has not declared observable"):
        _encode_conv(
            mutant, monkeypatch,
            propensity_scalar=0.83, **_BASE_RESPONSE, **_enums(),
        )


def test_mutation_a_known_forbidden_trait_still_trips_the_denylist_belt(monkeypatch):
    """The SECOND belt is separately observable: a field that is both undeclared
    and a known trait name must report the TRUTH-LEAK, not the generic refusal,
    or the denylist has been silently subsumed and can no longer be said to fire."""
    from interface.contracts.conversation_seam import FORBIDDEN_TRUTH_FIELDS
    from simulation.conversation_response import SeamCodecError

    assert "true_intent" in FORBIDDEN_TRUTH_FIELDS
    mutant = _response_shaped(true_intent=float)
    with pytest.raises(SeamCodecError, match="hidden-trait field"):
        _encode_conv(
            mutant, monkeypatch, true_intent=1.0, **_BASE_RESPONSE, **_enums()
        )


def test_mutation_a_stale_declaration_is_refused(monkeypatch):
    """FAIL-CLOSED the other way: a payload that LOSES a certified field is
    refused rather than silently emitting a narrower wire form."""
    from simulation.conversation_response import SeamCodecError

    mutant = _response_shaped(_drop=("responded_step",))
    values = {k: v for k, v in _BASE_RESPONSE.items() if k != "responded_step"}
    with pytest.raises(SeamCodecError, match="omits declared observable field"):
        _encode_conv(mutant, monkeypatch, **values, **_enums())


def test_the_declaration_is_not_derived_from_the_payload_it_certifies():
    """R15 TAUTOLOGY guard -- the closed set must be WRITTEN OUT, not computed
    from the dataclass it certifies. This seam's DECODE leg builds its allowlist
    with `get_type_hints(ConversationMessage)`, which is exactly the derived
    form: it widens whenever the class widens and could not have caught the
    defect above. That is why the encode leg does not reuse it."""
    import ast
    from pathlib import Path

    tree = ast.parse(Path("interface/contracts/conversation_seam.py").read_text())
    node = next(
        n for n in ast.walk(tree)
        if isinstance(n, ast.AnnAssign)
        and getattr(n.target, "id", None) == "OBSERVABLE_PAYLOAD_FIELDS"
    )
    assert isinstance(node.value, ast.Dict), "must be a literal declaration"
    for entry in node.value.values:
        assert isinstance(entry, ast.Tuple), "each payload's fields must be literal"
        for element in entry.elts:
            assert isinstance(element, ast.Constant) and isinstance(element.value, str)
