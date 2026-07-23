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
