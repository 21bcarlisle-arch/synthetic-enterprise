"""F1b exit tests — COMPANY comms generator + Bayesian susceptibility estimator.

Covers the atom's gate (proposal §4):
  * generator fires the correct situation-keyed, SEGMENT-GATED message and MAY
    NOT assume one channel;
  * the Bayesian belief updates on OBSERVED replies only, is idempotent, and
    infers a susceptibility category the harness can score;
  * THE EPISTEMIC WALL — the real F1b files PASS the epistemic verifier, and the
    R15 mutation (a belief-update that reads the true scalar) is CAUGHT by it.
    Without that failing-mutation proof the wall is theatre (R15 doctrine).
"""
from __future__ import annotations

import os
import textwrap
from pathlib import Path

import pytest

from interface.contracts.conversation_seam import (
    Channel,
    ConversationMessage,
    ConversationResponse,
    Product,
    ResponseAction,
    Situation,
)
from company.comms.conversation_generator import (
    ConversationGenerator,
    CustomerSegment,
    SITUATION_CONFIG,
    allowed_channels,
)
from company.comms.susceptibility_estimator import (
    FRAMING_VALUES,
    TONE_VALUES,
    SusceptibilityEstimator,
)


# --- helpers --------------------------------------------------------------


def _msg(mid="m1", situation=Situation.RENEWAL, channel=Channel.EMAIL,
         product=Product.DUAL_FUEL, tone="neutral_toned", framing="neutral_framed",
         emitted_step=0, offer=None):
    return ConversationMessage(
        message_id=mid, situation=situation, channel=channel, product=product,
        tone=tone, framing=framing, emitted_step=emitted_step, offer=offer,
    )


def _resp(rid="r1", responds_to="m1", action=ResponseAction.REPLY,
          channel=Channel.EMAIL, latency=1, emitted_step=0):
    return ConversationResponse(
        response_id=rid, responds_to=responds_to, action=action,
        channel_chosen=channel, latency=latency,
        responded_step=emitted_step + latency,
    )


# --- generator: situation-keyed, product-carried --------------------------


def test_generator_fires_situation_keyed_message():
    gen = ConversationGenerator()
    for situation in Situation:
        m = gen.generate("cust-A", CustomerSegment(), situation, Product.ELECTRICITY, emitted_step=5)
        assert m.situation is situation
        assert m.product is Product.ELECTRICITY  # portability: product always carried
        assert m.emitted_step == 5
        assert m.message_id == f"cust-A:{situation.value}:5"  # stable/idempotent id


def test_offer_attached_only_when_situation_carries_one():
    gen = ConversationGenerator()
    renewal = gen.generate("c", CustomerSegment(), Situation.RENEWAL, Product.GAS, 0)
    tariff = gen.generate("c", CustomerSegment(), Situation.TARIFF_CHANGE, Product.GAS, 0)
    assert renewal.offer == SITUATION_CONFIG[Situation.RENEWAL].offer_label
    assert renewal.offer is not None
    assert tariff.offer is None  # tariff-change carries no offer


# --- segment-gated channel: MAY NOT assume one channel --------------------


def test_allowed_channels_always_more_than_one():
    for segment in (
        CustomerSegment("residential", psr=False, digital_engaged=True),
        CustomerSegment("residential", psr=False, digital_engaged=False),
        CustomerSegment("sme"),
        CustomerSegment("i_and_c"),
        CustomerSegment("residential", psr=True),
    ):
        assert len(set(allowed_channels(segment))) > 1


def test_psr_channels_are_accessible_formats_no_app_or_sms_only():
    psr = allowed_channels(CustomerSegment("residential", psr=True))
    assert Channel.APP not in psr        # app-only can exclude a PSR customer
    assert Channel.SMS not in psr
    assert Channel.LETTER in psr and Channel.PHONE in psr


def test_same_situation_different_segments_get_different_channels():
    """The load-bearing 'may not assume one channel' property: a digital
    residential customer and a PSR customer, same situation, provably differ."""
    gen = ConversationGenerator()
    resi = gen.generate("c1", CustomerSegment("residential", digital_engaged=True),
                        Situation.MISSED_PAYMENT, Product.ELECTRICITY, 0)
    psr = gen.generate("c2", CustomerSegment("residential", psr=True),
                       Situation.MISSED_PAYMENT, Product.ELECTRICITY, 0)
    sme = gen.generate("c3", CustomerSegment("sme"),
                       Situation.MISSED_PAYMENT, Product.ELECTRICITY, 0)
    assert resi.channel == Channel.SMS       # digital-first urgent -> SMS
    assert psr.channel == Channel.PHONE      # accessible urgent -> PHONE (no SMS)
    assert sme.channel == Channel.PHONE      # business -> no SMS
    assert resi.channel != psr.channel       # the property, proven


def test_generated_channel_always_within_segment_allowance():
    gen = ConversationGenerator()
    for cls in ("residential", "sme", "i_and_c"):
        for psr in (True, False):
            seg = CustomerSegment(cls, psr=psr)
            for situation in Situation:
                m = gen.generate("c", seg, situation, Product.GAS, 0)
                assert m.channel in allowed_channels(seg)


# --- generator consults the belief (segment-BELIEF keying) ----------------


def test_generator_sends_the_lever_the_belief_prefers():
    est = SusceptibilityEstimator()
    gen = ConversationGenerator(est)
    # No data yet -> neutral levers (honest ignorance).
    m0 = gen.generate("cust", CustomerSegment(), Situation.RENEWAL, Product.DUAL_FUEL, 0)
    assert m0.framing == "neutral_framed" and m0.tone == "neutral_toned"
    # Feed positive replies to loss_framed / empathetic_toned, negatives elsewhere.
    for i in range(6):
        sent = _msg(mid=f"s{i}", framing="loss_framed", tone="empathetic_toned", emitted_step=i)
        est.observe_response("cust", sent, _resp(rid=f"p{i}", responds_to=f"s{i}",
                                                 action=ResponseAction.PAY, latency=1, emitted_step=i))
        sent2 = _msg(mid=f"g{i}", framing="gain_framed", tone="firm_toned", emitted_step=i)
        est.observe_response("cust", sent2, _resp(rid=f"n{i}", responds_to=f"g{i}",
                                                  action=ResponseAction.NO_REPLY, latency=2, emitted_step=i))
    m1 = gen.generate("cust", CustomerSegment(), Situation.RENEWAL, Product.DUAL_FUEL, 10)
    assert m1.framing == "loss_framed"
    assert m1.tone == "empathetic_toned"
    assert est.inferred_framing_susceptibility("cust") == "loss_averse"
    assert est.inferred_tone_susceptibility("cust") == "empathetic_responsive"


# --- estimator: updates on replies ONLY, idempotent, honest defaults ------


def test_positive_reply_raises_belief_negative_lowers_it():
    est = SusceptibilityEstimator()
    base = est.belief("c").framing_means()  # empty
    assert base == {}
    est.observe_response("c", _msg(mid="a", framing="loss_framed"),
                         _resp(rid="ra", responds_to="a", action=ResponseAction.PAY))
    after_pos = est.belief("c").framing.get("loss_framed").mean
    assert after_pos > 0.5  # a positive reply pushes the mean above the 0.5 prior
    est.observe_response("c", _msg(mid="b", framing="gain_framed"),
                         _resp(rid="rb", responds_to="b", action=ResponseAction.NO_REPLY))
    after_neg = est.belief("c").framing.get("gain_framed").mean
    assert after_neg < 0.5  # a negative reply pushes the other lever's mean below prior


def test_idempotent_duplicate_response_is_a_noop():
    est = SusceptibilityEstimator()
    m = _msg(mid="a", framing="loss_framed")
    r = _resp(rid="dup", responds_to="a", action=ResponseAction.PAY)
    assert est.observe_response("c", m, r) is True
    mean_once = est.belief("c").framing.get("loss_framed").mean
    assert est.observe_response("c", m, r) is False   # C-S2: already folded in
    mean_twice = est.belief("c").framing.get("loss_framed").mean
    assert mean_once == mean_twice


def test_observe_order_independent():
    """C-S1/C-S3: replies may arrive out of order; Beta counts commute."""
    pairs = [
        ("c", _msg(mid="a", framing="loss_framed"), _resp(rid="1", responds_to="a", action=ResponseAction.PAY)),
        ("c", _msg(mid="b", framing="loss_framed"), _resp(rid="2", responds_to="b", action=ResponseAction.NO_REPLY)),
        ("c", _msg(mid="d", framing="loss_framed"), _resp(rid="3", responds_to="d", action=ResponseAction.CLICK)),
    ]
    fwd = SusceptibilityEstimator(); fwd.observe_many(pairs)
    rev = SusceptibilityEstimator(); rev.observe_many(list(reversed(pairs)))
    assert fwd.belief("c").framing.get("loss_framed").mean == pytest.approx(
        rev.belief("c").framing.get("loss_framed").mean
    )


def test_faster_positive_reply_counts_for_more():
    fast = SusceptibilityEstimator()
    slow = SusceptibilityEstimator()
    fast.observe_response("c", _msg(mid="a", framing="loss_framed"),
                          _resp(rid="f", responds_to="a", action=ResponseAction.PAY, latency=1))
    slow.observe_response("c", _msg(mid="a", framing="loss_framed"),
                          _resp(rid="s", responds_to="a", action=ResponseAction.PAY, latency=50))
    assert fast.belief("c").framing.get("loss_framed").mean > slow.belief("c").framing.get("loss_framed").mean


def test_mispaired_or_same_step_response_rejected():
    est = SusceptibilityEstimator()
    m = _msg(mid="a", emitted_step=5)
    # wrong responds_to
    with pytest.raises(ValueError):
        est.observe_response("c", m, _resp(rid="x", responds_to="WRONG", action=ResponseAction.PAY))
    # response not strictly after the message (same-step): responded_step <= emitted_step
    bad = ConversationResponse(response_id="y", responds_to="a", action=ResponseAction.PAY,
                               channel_chosen=Channel.EMAIL, latency=1, responded_step=5)
    with pytest.raises(ValueError):
        est.observe_response("c", m, bad)


def test_unmessaged_customer_infers_neutral():
    est = SusceptibilityEstimator()
    assert est.inferred_framing_susceptibility("stranger") == "neutral"
    assert est.inferred_tone_susceptibility("stranger") == "neutral"
    assert est.best_framing_value("stranger") == "neutral_framed"


def test_dead_heat_infers_neutral():
    """Two levers separated by less than the epsilon -> no signal -> neutral,
    never over-committing on thin evidence."""
    est = SusceptibilityEstimator()
    for i in range(3):
        est.observe_response("c", _msg(mid=f"a{i}", framing="loss_framed"),
                             _resp(rid=f"la{i}", responds_to=f"a{i}", action=ResponseAction.PAY, latency=1))
        est.observe_response("c", _msg(mid=f"b{i}", framing="gain_framed"),
                             _resp(rid=f"gb{i}", responds_to=f"b{i}", action=ResponseAction.PAY, latency=1))
    assert est.inferred_framing_susceptibility("c") == "neutral"


def test_posterior_report_is_pure_belief():
    est = SusceptibilityEstimator()
    est.observe_response("c", _msg(mid="a", framing="loss_framed", tone="empathetic_toned"),
                         _resp(rid="r", responds_to="a", action=ResponseAction.PAY))
    rep = est.posterior_report("c")
    assert set(rep) == {"framing_means", "tone_means", "inferred"}
    assert "loss_framed" in rep["framing_means"]
    assert rep["inferred"]["framing_susceptibility"] in {"loss_averse", "gain_responsive", "neutral"}


def test_lever_vocab_matches_category_maps():
    # every lever value maps to a category (no orphan value)
    est = SusceptibilityEstimator()
    for v in FRAMING_VALUES:
        est.observe_response("c", _msg(mid=v, framing=v),
                             _resp(rid=f"r{v}", responds_to=v, action=ResponseAction.PAY))
    for v in TONE_VALUES:
        est.observe_response("c", _msg(mid=v, tone=v),
                             _resp(rid=f"t{v}", responds_to=v, action=ResponseAction.PAY))


# --- THE EPISTEMIC WALL (R15: the control must be able to FAIL) ------------

F1B_FILES = [
    "company/comms/conversation_generator.py",
    "company/comms/susceptibility_estimator.py",
]


def test_f1b_files_pass_the_epistemic_verifier():
    """The real F1b diff is clean: no company file reads a SIM internal."""
    from tools.epistemic_verifier import scan
    passed, violations = scan(files=F1B_FILES)
    assert passed, f"F1b must not breach the wall; got: {violations}"


def test_f1b_source_imports_no_simulation():
    import re
    for f in F1B_FILES:
        src = Path(f).read_text()
        for line in src.splitlines():
            assert not re.match(r"\s*(from|import)\s+sim(ulation)?\b", line), line


def test_R15_peeking_belief_update_is_caught_by_the_verifier():
    """R15 MUTATION (the gate): a belief-update that reaches for the customer's
    TRUE hidden scalar can only do so by importing the SIM internal that holds
    it -- and the epistemic verifier FAILS on exactly that. If this peeking
    variant scanned clean, the wall would be theatre.

    Proven two ways: (1) directly on the mutated SOURCE via the verifier's own
    AST scan (no disk write); (2) end-to-end on a real temp file under
    company/comms/ via the public scan(), then removed."""
    from tools.epistemic_verifier import scan, _scan_source

    peeking_src = textwrap.dedent(
        '''
        """A PEEKING estimator variant: it reads the customer's TRUE hidden
        susceptibility instead of inferring it from replies. This is the named
        defect the wall must catch."""
        from interface.contracts.conversation_seam import ConversationResponse
        from simulation.nudge_physics import tone_susceptibility_for  # THE LEAK

        def peeking_update(customer_id, response):
            truth = tone_susceptibility_for(customer_id)  # reads the true scalar
            return truth
        '''
    )

    # (1) direct AST scan of the mutated source
    violations = _scan_source(peeking_src, "company/comms/_peeking_variant.py")
    assert violations, "the verifier must catch a SIM import in a company file"
    assert any("simulation" in v["code"] or "simulation" in v["description"] for v in violations)

    # (2) end-to-end through the public scan() on a real temp company file
    probe = Path(f"company/comms/_peek_probe_{os.getpid()}.py")
    try:
        probe.write_text(peeking_src)
        passed, viols = scan(files=[str(probe)])
        assert not passed, "a peeking company file MUST fail the epistemic verifier"
        assert viols
    finally:
        if probe.exists():
            probe.unlink()
