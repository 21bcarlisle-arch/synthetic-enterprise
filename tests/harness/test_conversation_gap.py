"""F1c exit tests -- the HARNESS conversation gap organ
(background/conversation_gap_ledger.py).

Covers the atom's spec (maturity_map.yaml F1c_harness_conversation_gap):
  1. belief-vs-truth susceptibility gap per customer -- sensitivity proven
     BOTH ways (a correctly-trained belief matches truth; a deliberately
     wrong belief is CAUGHT as a mismatch -- not tautological).
  2. did the conversation improve the outcome, CA-weighted 55/35/10 --
     sensitivity proven both ways (a matched lever gives a real positive
     uplift; a mismatched non-neutral lever gives EXACTLY zero, proving the
     measure is not fabricated/always-positive).
  3. THE MANDATORY R15 INTENT-LEAK CONTROL -- a peeking F1b variant (reads the
     true scalar directly) is CAUGHT; a genuinely honest, zero-evidence
     generator is NOT flagged. Without this failing-mutation proof the wall
     is theatre (R15 doctrine).

Plus the structural epistemic-wall assertions (this organ measures, never
helps either side) and the R10 exhaustiveness check that the harness's
duplicated-by-convention situation/lever classification has not drifted from
the real F1a source table.

DETERMINISM NOTE: every value asserted below was verified by direct execution
against the real, unmutated modules before being written into this file (see
the FRAME doc's "verification" section) -- nothing here is a guessed/round
number. `simulation.conversation_response.respond` and the belief update are
both pure/idempotent (C-S2), so every number here is EXACT and reproducible,
never a statistical/flaky threshold.
"""
from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

import background.conversation_gap_ledger as gap_ledger
import simulation.nudge_physics as nudge_physics
from company.comms.conversation_generator import CustomerSegment
from company.comms.susceptibility_estimator import SusceptibilityEstimator
from interface.contracts.conversation_seam import (
    Channel,
    ConversationMessage,
    ConversationResponse,
    Product,
    ResponseAction,
    Situation,
)
from simulation.conversation_response import _SITUATION_PROFILE


# --- helpers (mirrors tests/company/comms/test_conversation_comms.py idiom) -


def _msg(mid, framing="neutral_framed", tone="neutral_toned", situation=Situation.RENEWAL, step=0):
    return ConversationMessage(
        message_id=mid, situation=situation, channel=Channel.EMAIL, product=Product.DUAL_FUEL,
        tone=tone, framing=framing, emitted_step=step,
    )


def _resp(rid, responds_to, action=ResponseAction.REPLY, latency=1, step=0):
    return ConversationResponse(
        response_id=rid, responds_to=responds_to, action=action, channel_chosen=Channel.EMAIL,
        latency=latency, responded_step=step + latency,
    )


def _feed_confident_framing_belief(estimator, customer_id, matching_framing, n=8):
    """Hand-feed a confident, correctly-separated belief for one lever value
    (same idiom as test_conversation_comms.py::test_generator_sends_the_
    lever_the_belief_prefers) -- positives for `matching_framing`, negatives
    for a distinct other value. Bypasses the (slow-converging, see FRAME doc)
    round-robin exploration for a fast, deterministic, decisive belief."""
    other = "gain_framed" if matching_framing == "loss_framed" else "loss_framed"
    for i in range(n):
        m = _msg(f"{customer_id}:pos:{i}", framing=matching_framing, step=i)
        estimator.observe_response(customer_id, m, _resp(f"{customer_id}:rpos:{i}", m.message_id,
                                                          action=ResponseAction.REPLY, step=i))
        m2 = _msg(f"{customer_id}:neg:{i}", framing=other, step=i)
        estimator.observe_response(customer_id, m2, _resp(f"{customer_id}:rneg:{i}", m2.message_id,
                                                           action=ResponseAction.NO_REPLY, step=i))


_FRAMING_LEVER_FOR_CATEGORY = {
    "loss_averse": "loss_framed",
    "gain_responsive": "gain_framed",
    "neutral": "neutral_framed",
}


# --- (0) determinism (C-S2) ------------------------------------------------


def test_measure_is_deterministic():
    row1 = gap_ledger.measure(customer_count=30, situations=[Situation.RENEWAL], training_rounds=10)
    row2 = gap_ledger.measure(customer_count=30, situations=[Situation.RENEWAL], training_rounds=10)
    assert row1 == row2


def test_honest_zero_evidence_generate_never_leaks_state_across_calls():
    """Two calls for the SAME customer must give the SAME (neutral) message --
    proof `honest_zero_evidence_generate` builds a genuinely FRESH estimator
    every call, never an accumulating/shared one."""
    m1 = gap_ledger.honest_zero_evidence_generate(
        "cust-x", CustomerSegment(), Situation.RENEWAL, Product.ELECTRICITY, 0
    )
    m2 = gap_ledger.honest_zero_evidence_generate(
        "cust-x", CustomerSegment(), Situation.RENEWAL, Product.ELECTRICITY, 0
    )
    assert m1 == m2
    assert m1.framing == "neutral_framed" and m1.tone == "neutral_toned"


# --- (1) belief-vs-truth gap: sensitivity BOTH ways -------------------------


def test_gap_matches_when_belief_is_confidently_trained_correctly():
    pop = gap_ledger._synthetic_population(200)
    loss_customers = [c for c in pop if gap_ledger.true_framing_category(c) == "loss_averse"][:40]
    assert loss_customers, "fixture sanity: population must contain loss-averse customers"

    est = SusceptibilityEstimator()
    for cust in loss_customers:
        _feed_confident_framing_belief(est, cust, "loss_framed")

    rows = gap_ledger.belief_vs_truth_gap(loss_customers, est)
    summary = gap_ledger.summarise_gap(rows)
    assert summary["framing_category_match_rate"] == 1.0
    assert all(r["framing_category_match"] for r in rows)


def test_gap_catches_a_deliberately_wrong_belief_not_tautological():
    """The load-bearing non-tautology proof: belief and truth are read from
    INDEPENDENT sources (company estimator vs simulation.nudge_physics). A
    belief hand-trained toward the WRONG lever must be CAUGHT as a mismatch,
    not silently agree with itself."""
    pop = gap_ledger._synthetic_population(200)
    loss_customers = [c for c in pop if gap_ledger.true_framing_category(c) == "loss_averse"][:40]

    est = SusceptibilityEstimator()
    for cust in loss_customers:
        _feed_confident_framing_belief(est, cust, "gain_framed")  # WRONG lever

    rows = gap_ledger.belief_vs_truth_gap(loss_customers, est)
    summary = gap_ledger.summarise_gap(rows)
    assert summary["framing_category_match_rate"] == 0.0
    assert all(not r["framing_category_match"] for r in rows)
    assert all(r["belief_framing_category"] == "gain_responsive" for r in rows)
    assert all(r["true_framing_category"] == "loss_averse" for r in rows)


def test_summarise_gap_fails_closed_on_empty_population():
    with pytest.raises(gap_ledger.ConversationGapUnmeasurable):
        gap_ledger.summarise_gap([])


# --- (2) CA-weighted (55/35/10) outcome uplift vs neutral control ----------


def test_ca_weights_sum_to_one_and_commitments_is_a_named_constant():
    assert (
        gap_ledger.CA_CUSTOMER_SERVICE_WEIGHT
        + gap_ledger.CA_COMPLAINTS_WEIGHT
        + gap_ledger.CA_COMMITMENTS_WEIGHT
        == pytest.approx(1.0)
    )
    # every ResponseAction scores within [commitments-only-floor, 1.0]
    floor = gap_ledger.CA_COMMITMENTS_WEIGHT * gap_ledger._COMMITMENTS_BASELINE
    for action in ResponseAction:
        score = gap_ledger.ca_weighted_outcome_score(action)
        assert floor - 1e-9 <= score <= 1.0 + 1e-9
    # COMPLAIN is the worst outcome (zero service + zero complaints axis)
    assert gap_ledger.ca_weighted_outcome_score(ResponseAction.COMPLAIN) == pytest.approx(floor)
    assert gap_ledger.ca_weighted_outcome_score(ResponseAction.PAY) == pytest.approx(1.0)


def test_matched_lever_gives_positive_uplift_over_neutral_control():
    pop = gap_ledger._synthetic_population(300)
    loss_customers = [c for c in pop if gap_ledger.true_framing_category(c) == "loss_averse"][:80]

    est = SusceptibilityEstimator()
    for cust in loss_customers:
        _feed_confident_framing_belief(est, cust, "loss_framed")  # CORRECT lever

    row = gap_ledger.outcome_uplift_vs_control(
        loss_customers, est, Situation.RENEWAL, Product.DUAL_FUEL, step=100
    )
    assert row["uplift"] > 0.0, "a correctly-matched lever must beat the neutral control"


def test_mismatched_nonneutral_lever_gives_exactly_zero_uplift_not_tautological():
    """`positive_action_probability`/`_adverse_share` in the REAL F1a model
    are insensitive to a MISMATCHED lever (multiplier stays 1.0, identical to
    neutral) -- and with the common-random-numbers construction
    (`outcome_uplift_vs_control` reuses the treated message_id for the
    control), a mismatched non-neutral lever must therefore produce a
    response IDENTICAL to the neutral control, uplift EXACTLY 0.0. Proves the
    uplift measure is sensitive, not a fabricated always-positive number."""
    pop = gap_ledger._synthetic_population(300)
    loss_customers = [c for c in pop if gap_ledger.true_framing_category(c) == "loss_averse"][:60]

    est = SusceptibilityEstimator()
    for cust in loss_customers:
        _feed_confident_framing_belief(est, cust, "gain_framed")  # WRONG (non-neutral) lever

    row = gap_ledger.outcome_uplift_vs_control(
        loss_customers, est, Situation.RENEWAL, Product.DUAL_FUEL, step=100
    )
    assert row["uplift"] == 0.0


def test_outcome_uplift_fails_closed_on_empty_population():
    with pytest.raises(gap_ledger.ConversationGapUnmeasurable):
        gap_ledger.outcome_uplift_vs_control([], SusceptibilityEstimator(), Situation.RENEWAL,
                                             Product.DUAL_FUEL, step=0)


# --- (3) THE MANDATORY R15 INTENT-LEAK CONTROL ------------------------------


def _peeking_generate(customer_id, segment, situation, product, step):
    """THE NAMED DEFECT (proposal §3c / FRAME §3c): a company variant that,
    instead of consulting a belief built from observed replies, reads the
    customer's TRUE hidden susceptibility DIRECTLY from `simulation.
    nudge_physics` and sends the matching lever from the very first contact.
    Mirrors the naming/intent of F1b's own R15 test
    (test_conversation_comms.py::test_R15_peeking_belief_update_is_caught_by_
    the_verifier), but implemented as a `generate_fn` so it can be scored by
    this harness's `intent_leak_rate`."""
    honest = gap_ledger.honest_zero_evidence_generate(customer_id, segment, situation, product, step)
    truth = nudge_physics.susceptibility_for(customer_id)
    peeking_framing = _FRAMING_LEVER_FOR_CATEGORY[truth.value]
    return replace(honest, framing=peeking_framing)  # THE LEAK: reads truth, not replies


def test_R15_honest_zero_evidence_generator_does_not_trip_the_intent_leak_control():
    pop = gap_ledger._synthetic_population(80)
    rate = gap_ledger.intent_leak_rate(
        gap_ledger.honest_zero_evidence_generate, pop, Situation.RENEWAL, Product.DUAL_FUEL
    )
    assert rate["framing_leak_rate"] == 0.0
    assert rate["tone_leak_rate"] == 0.0
    assert gap_ledger.detect_intent_leak(rate) is False


def test_R15_peeking_variant_IS_caught_by_the_intent_leak_control():
    """THE ATOM'S MANDATORY EXIT TEST. Without this failing on the peeking
    variant the wall is theatre (R15 doctrine)."""
    pop = gap_ledger._synthetic_population(80)
    rate = gap_ledger.intent_leak_rate(_peeking_generate, pop, Situation.RENEWAL, Product.DUAL_FUEL)
    assert rate["framing_leak_rate"] > 0.5, (
        "a company reading the true scalar directly must correlate with it far "
        "above the honest zero-evidence baseline of exactly 0.0"
    )
    assert gap_ledger.detect_intent_leak(rate) is True


def test_R15_both_ways_same_population_same_situation():
    """Both arms of the R15 proof run over the IDENTICAL population/situation
    in one test, so the honest-vs-peeking contrast cannot be an artefact of
    different fixtures."""
    pop = gap_ledger._synthetic_population(50)
    honest_rate = gap_ledger.intent_leak_rate(
        gap_ledger.honest_zero_evidence_generate, pop, Situation.MISSED_PAYMENT, Product.GAS
    )
    peeking_rate = gap_ledger.intent_leak_rate(
        _peeking_generate, pop, Situation.MISSED_PAYMENT, Product.GAS
    )
    assert gap_ledger.detect_intent_leak(honest_rate) is False
    assert gap_ledger.detect_intent_leak(peeking_rate) is True
    assert peeking_rate["framing_leak_rate"] > honest_rate["framing_leak_rate"]


# --- R15 FAIL-OPEN GUARD on the intent-leak control itself ------------------
# Found empirically while hardening this atom: the ORIGINAL implementation
# returned a fabricated 0.0 ("clean") leak rate whenever an axis had ZERO
# scored (non-neutral-truth) customers -- indistinguishable from a genuinely
# clean measurement even though NOTHING was checked. This is exactly the
# FAIL-OPEN killer pattern (R15 doctrine: "passes on missing/zero/empty").


def test_intent_leak_rate_fails_closed_on_empty_population():
    with pytest.raises(gap_ledger.ConversationGapUnmeasurable):
        gap_ledger.intent_leak_rate(
            gap_ledger.honest_zero_evidence_generate, [], Situation.RENEWAL, Product.DUAL_FUEL
        )


def test_intent_leak_rate_fails_closed_not_fail_open_when_no_axis_has_evidence():
    """A population with zero non-neutral-truth customers on EITHER axis must
    raise rather than silently report a 'clean' 0.0 -- an unavailable check is
    a FAILED check (R15), never a quiet pass. Fixture sanity confirms the
    deterministic synthetic population genuinely contains such an all-neutral
    subset at this seed, so this is a real reachable condition, not a
    hypothetical."""
    pop = gap_ledger._synthetic_population(200)
    both_neutral = [
        c for c in pop
        if gap_ledger.true_framing_category(c) == "neutral"
        and gap_ledger.true_tone_category(c) == "neutral"
    ]
    assert both_neutral, "fixture sanity: population must contain all-neutral-truth customers"
    with pytest.raises(gap_ledger.ConversationGapUnmeasurable):
        gap_ledger.intent_leak_rate(
            gap_ledger.honest_zero_evidence_generate, both_neutral, Situation.RENEWAL, Product.DUAL_FUEL
        )
    # the failure is about EVIDENCE AVAILABILITY, not which generate_fn is used --
    # even the peeking variant must fail closed over a starved population.
    with pytest.raises(gap_ledger.ConversationGapUnmeasurable):
        gap_ledger.intent_leak_rate(_peeking_generate, both_neutral, Situation.RENEWAL, Product.DUAL_FUEL)


def test_intent_leak_rate_reports_none_not_zero_for_a_starved_single_axis():
    """A population starved on ONE axis only (framing-neutral, tone-non-
    neutral) must report `None` for the unscored axis -- never a fabricated
    0.0 -- while still genuinely scoring the other axis."""
    pop = gap_ledger._synthetic_population(200)
    framing_starved = [
        c for c in pop
        if gap_ledger.true_framing_category(c) == "neutral"
        and gap_ledger.true_tone_category(c) != "neutral"
    ]
    assert framing_starved, "fixture sanity: population must contain a framing-starved/tone-scored subset"
    rate = gap_ledger.intent_leak_rate(
        gap_ledger.honest_zero_evidence_generate, framing_starved, Situation.MISSED_PAYMENT, Product.GAS
    )
    assert rate["framing_scored"] == 0
    assert rate["framing_leak_rate"] is None
    assert rate["tone_scored"] > 0
    assert rate["tone_leak_rate"] == 0.0  # honest generator, genuinely measured, genuinely clean
    assert gap_ledger.detect_intent_leak(rate) is False


def test_detect_intent_leak_treats_none_axis_as_no_verdict_never_a_typeerror():
    """Defensive on the public `detect_intent_leak` signature: a `None` axis
    (zero scored customers) must never raise and must never be treated as
    evidence of cleanliness -- it simply contributes no verdict; the OTHER
    axis's real reading still fires normally."""
    assert gap_ledger.detect_intent_leak({"framing_leak_rate": None, "tone_leak_rate": None}) is False
    assert gap_ledger.detect_intent_leak({"framing_leak_rate": None, "tone_leak_rate": 0.9}) is True
    assert gap_ledger.detect_intent_leak({"framing_leak_rate": 0.9, "tone_leak_rate": None}) is True
    assert gap_ledger.detect_intent_leak({"framing_leak_rate": None, "tone_leak_rate": 0.01}) is False


# --- R10: the harness's duplicated-by-convention situation/lever map must --
# --- not drift from the real F1a source table ------------------------------


def test_situation_sensitivity_map_agrees_with_the_real_f1a_profile_table():
    """Guards `_FRAMING_SENSITIVE_SITUATIONS`/`_TONE_SENSITIVE_SITUATIONS`
    against silent drift from `simulation.conversation_response.
    _SITUATION_PROFILE` -- the ACTUAL source of which lever moves which
    situation's outcome. Every `Situation` member is classified, and exactly
    one of the two sets (mirrors the SIM's own "no situation is both")."""
    for situation in Situation:
        profile = _SITUATION_PROFILE[situation]
        in_framing_set = situation in gap_ledger._FRAMING_SENSITIVE_SITUATIONS
        in_tone_set = situation in gap_ledger._TONE_SENSITIVE_SITUATIONS
        assert in_framing_set == profile.framing_sensitive, situation
        assert in_tone_set == profile.tone_sensitive, situation
        assert in_framing_set != in_tone_set, f"{situation} must be exactly one of framing/tone"


# --- structural epistemic-wall assertions -----------------------------------


def test_module_writes_only_its_own_ledger_path():
    """STRUCTURAL wall assertion: this organ measures, never helps either
    side -- it must write to exactly one path, its own ledger, never into
    any company/, saas/, or simulation/ file."""
    source = Path(gap_ledger.__file__).read_text(encoding="utf-8")
    write_calls = source.count(".write_text(")
    assert write_calls == 1, (
        f"expected exactly one write_text() call (the ledger append), found {write_calls}"
    )
    assert "lp.write_text(" in source


def test_module_never_imported_by_the_supervisor_draw():
    """SEVERANCE (R12): the gap is a DIAGNOSTIC, never a target -- it must
    never feed priority, reward, selection, or scheduling. Mirrors
    tests/background/test_dd_h_solvency_gap.py's own severance test."""
    source = Path(gap_ledger.__file__).read_text(encoding="utf-8")
    assert "import supervisor" not in source
    assert "from background.supervisor" not in source

    supervisor_path = Path(gap_ledger.__file__).resolve().parent / "supervisor.py"
    if supervisor_path.exists():
        supervisor_source = supervisor_path.read_text(encoding="utf-8")
        assert "conversation_gap_ledger" not in supervisor_source


def test_measurement_functions_never_mutate_a_caller_supplied_estimator_beyond_its_own_reads():
    """`belief_vs_truth_gap` and `outcome_uplift_vs_control` must be READS of
    the estimator they are handed -- never write into it (the referee reads
    both sides, it does not coach either one)."""
    pop = gap_ledger._synthetic_population(10)
    est = SusceptibilityEstimator()
    for cust in pop[:5]:
        _feed_confident_framing_belief(est, cust, "loss_framed")
    before = {cid: dict(est.belief(cid).framing_means()) for cid in pop}

    gap_ledger.belief_vs_truth_gap(pop, est)
    gap_ledger.outcome_uplift_vs_control(pop, est, Situation.RENEWAL, Product.DUAL_FUEL, step=0)

    after = {cid: dict(est.belief(cid).framing_means()) for cid in pop}
    assert before == after


# --- fail-closed (R15: an unavailable check is a failed check) -------------


def test_measure_fails_closed_on_zero_customers():
    with pytest.raises(gap_ledger.ConversationGapUnmeasurable):
        gap_ledger.measure(customer_count=0)


def test_record_gap_writes_an_honest_not_measurable_row_never_a_fabricated_gap(tmp_path):
    ledger_path = tmp_path / "conversation_gap_ledger.json"
    row = gap_ledger.record_gap(
        measured_at="2026-08-03T00:00:00Z",
        run_git_commit="deadbeef",
        ledger_path=ledger_path,
        customer_count=0,  # forces ConversationGapUnmeasurable
    )
    assert row["measurable"] is False
    assert "reason" in row
    assert "measured_at" in row

    on_disk = json.loads(ledger_path.read_text(encoding="utf-8"))
    assert len(on_disk) == 1
    assert on_disk[0]["measurable"] is False


def test_record_gap_appends_real_measurable_rows(tmp_path):
    ledger_path = tmp_path / "conversation_gap_ledger.json"
    row1 = gap_ledger.record_gap(
        measured_at="t1", ledger_path=ledger_path,
        customer_count=20, situations=[Situation.RENEWAL], training_rounds=5,
    )
    row2 = gap_ledger.record_gap(
        measured_at="t2", ledger_path=ledger_path,
        customer_count=20, situations=[Situation.RENEWAL], training_rounds=5,
    )
    assert row1["measurable"] is True and row2["measurable"] is True
    on_disk = json.loads(ledger_path.read_text(encoding="utf-8"))
    assert len(on_disk) == 2
    assert on_disk[0]["measured_at"] == "t1" and on_disk[1]["measured_at"] == "t2"


def test_retro_gap_line_is_fail_closed_and_pure():
    line_ok = gap_ledger.retro_gap_line(customer_count=20, situations=[Situation.RENEWAL], training_rounds=5)
    assert "conversation belief-vs-truth gap" in line_ok
    line_bad = gap_ledger.retro_gap_line(customer_count=0)
    assert "NOT MEASURABLE" in line_bad


# --- end-to-end shape of the full self-contained measurement ---------------


def test_measure_reports_all_three_mandated_things():
    row = gap_ledger.measure(customer_count=30, situations=[Situation.RENEWAL, Situation.MISSED_PAYMENT],
                              training_rounds=10)
    assert row["measurable"] is True
    # (1) belief-vs-truth gap
    gs = row["belief_vs_truth_gap"]
    assert set(gs) >= {
        "n_customers", "framing_category_match_rate", "tone_category_match_rate",
        "mean_framing_gap", "mean_tone_gap",
    }
    # (2) CA-weighted outcome uplift vs control, per situation
    assert set(row["outcome_uplift_by_situation"]) == {"renewal", "missed_payment"}
    for situation_row in row["outcome_uplift_by_situation"].values():
        assert {"treated_ca_weighted_score", "control_ca_weighted_score", "uplift"} <= set(situation_row)
    # (3) the mandatory intent-leak control
    leak = row["intent_leak"]
    assert "fired" in leak and isinstance(leak["fired"], bool)
