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


# Write primitives that would ESCAPE a `.write_text(`-only scan. The
# FRAME-stage structural control counted `.write_text(` alone, so a
# `json.dump(fp)` / `open(path, "w")` / `os.replace` write into a company/ or
# simulation/ file would have sailed straight through it -- a FAIL-OPEN in the
# wall assertion itself (R15: the control must be able to fail).
_FORBIDDEN_WRITE_PRIMITIVES = (
    "json.dump(",
    "shutil.",
    "os.remove(",
    "os.replace(",
    "os.rename(",
    ".unlink(",
    ".rename(",
    ".touch(",
    "pickle.dump(",
)


def test_module_uses_no_write_primitive_that_escapes_the_write_text_scan():
    """R15 hardening of the structural control ABOVE: prove the wall assertion
    cannot be bypassed by simply writing through a different primitive."""
    source = Path(gap_ledger.__file__).read_text(encoding="utf-8")
    found = [p for p in _FORBIDDEN_WRITE_PRIMITIVES if p in source]
    assert not found, f"module uses write primitives the write_text scan would miss: {found}"
    # A bare `open(` in write mode likewise escapes the scan. This module has
    # no legitimate need for it (it reads via `.read_text` and writes via the
    # single `.write_text`), so the strict form is the honest assertion.
    assert "open(" not in source, "module calls open() -- a write mode would escape the write_text scan"


def test_module_never_imported_by_the_supervisor_draw():
    """SEVERANCE (R12): the gap is a DIAGNOSTIC, never a target -- it must
    never feed priority, reward, selection, or scheduling. Mirrors
    tests/background/test_dd_h_solvency_gap.py's own severance test.

    R15 FAIL-SILENT fix: the FRAME-stage version wrapped the supervisor check
    in `if supervisor_path.exists()`, so a renamed/moved supervisor.py would
    have made this control silently pass without checking anything. The file's
    existence is now ASSERTED -- an unavailable check is a failed check."""
    source = Path(gap_ledger.__file__).read_text(encoding="utf-8")
    assert "import supervisor" not in source
    assert "from background.supervisor" not in source

    supervisor_path = Path(gap_ledger.__file__).resolve().parent / "supervisor.py"
    assert supervisor_path.exists(), (
        f"supervisor.py not found at {supervisor_path} -- this severance control cannot run, "
        "which is a FAILED check, not a pass"
    )
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


# --- R15 FAIL-OPEN REGRESSIONS on the MANDATORY intent-leak control --------
# Every test in this block was RUN against the FRAME-stage implementation
# first and FAILED there: `detect_intent_leak` was
# `rate_row.get(key, 0.0) > threshold`, which returned a reassuring False
# ("clean, no leak") on an empty population, an empty/malformed row, a NaN
# rate, and an all-neutral-truth population. A control that reports CLEAN when
# it measured nothing is the R15 FAIL-OPEN pattern verbatim -- these pin the
# fix so the class cannot come back (R10: the class, not the instance).


def test_intent_leak_rate_reports_None_not_zero_for_an_axis_that_scored_nobody():
    """0.0 must mean "measured, no leak found"; an axis that scored nobody
    must be `None` -- the two are NOT the same claim."""
    rate = gap_ledger.intent_leak_rate(
        gap_ledger.honest_zero_evidence_generate, [], Situation.RENEWAL, Product.DUAL_FUEL
    )
    assert rate["framing_scored"] == 0 and rate["tone_scored"] == 0
    assert rate["framing_leak_rate"] is None, "an unscored axis must not report a confident 0.0"
    assert rate["tone_leak_rate"] is None


def test_R15_control_refuses_an_empty_population_instead_of_reporting_clean():
    rate = gap_ledger.intent_leak_rate(
        gap_ledger.honest_zero_evidence_generate, [], Situation.RENEWAL, Product.DUAL_FUEL
    )
    with pytest.raises(gap_ledger.ConversationGapUnmeasurable):
        gap_ledger.detect_intent_leak(rate)


def test_R15_control_refuses_an_all_neutral_truth_population():
    """A population in which the control CANNOT discriminate (every customer's
    true category is neutral, so neither axis has a denominator) is an
    unavailable check, not a clean bill of health."""
    pop = gap_ledger._synthetic_population(400)
    all_neutral = [
        c for c in pop
        if gap_ledger.true_framing_category(c) == "neutral"
        and gap_ledger.true_tone_category(c) == "neutral"
    ]
    assert all_neutral, "fixture sanity: population must contain some all-neutral-truth customers"
    rate = gap_ledger.intent_leak_rate(
        gap_ledger.honest_zero_evidence_generate, all_neutral, Situation.RENEWAL, Product.DUAL_FUEL
    )
    assert rate["framing_scored"] == 0 and rate["tone_scored"] == 0
    with pytest.raises(gap_ledger.ConversationGapUnmeasurable):
        gap_ledger.detect_intent_leak(rate)


@pytest.mark.parametrize("bad_row", [{}, {"wrong_key": 1.0}, {"framing_leak_rate": None, "tone_leak_rate": None}])
def test_R15_control_refuses_a_malformed_or_wholly_unmeasured_row(bad_row):
    with pytest.raises(gap_ledger.ConversationGapUnmeasurable):
        gap_ledger.detect_intent_leak(bad_row)


@pytest.mark.parametrize("bad_row", [[], None, "0.0", 0.0])
def test_R15_control_refuses_a_row_that_is_not_a_mapping(bad_row):
    with pytest.raises(gap_ledger.ConversationGapUnmeasurable):
        gap_ledger.detect_intent_leak(bad_row)


@pytest.mark.parametrize("bad_rate", [float("nan"), float("inf"), float("-inf")])
def test_R15_control_refuses_a_nonfinite_rate_which_would_read_as_clean(bad_rate):
    """NaN is the sharp one: EVERY comparison with NaN is False, so a NaN rate
    silently read as "below threshold" = clean. Non-finite must be rejected
    FIRST, before any comparison."""
    with pytest.raises(gap_ledger.ConversationGapUnmeasurable):
        gap_ledger.detect_intent_leak({"framing_leak_rate": bad_rate, "tone_leak_rate": 0.0})


@pytest.mark.parametrize("bad_rate", [-0.1, 1.5, 42.0])
def test_R15_control_refuses_an_out_of_range_rate(bad_rate):
    with pytest.raises(gap_ledger.ConversationGapUnmeasurable):
        gap_ledger.detect_intent_leak({"framing_leak_rate": bad_rate, "tone_leak_rate": 0.0})


@pytest.mark.parametrize("bad_threshold", [1.0, 1.5, -0.1, float("nan"), float("inf"), True, "0.5"])
def test_R15_control_refuses_a_threshold_that_could_never_fire(bad_threshold):
    """An alarm whose threshold is >= 1.0 can never fire on a rate in [0, 1] --
    that is a control that cannot fail, which R15 forbids outright."""
    with pytest.raises(gap_ledger.ConversationGapUnmeasurable):
        gap_ledger.detect_intent_leak(
            {"framing_leak_rate": 0.0, "tone_leak_rate": 0.0}, threshold=bad_threshold
        )


def test_R15_a_partial_check_is_decided_by_the_axis_that_DID_measure():
    """One axis unmeasurable must not veto (nor mask) a real leak the other
    axis genuinely caught."""
    assert gap_ledger.detect_intent_leak({"framing_leak_rate": 0.9, "tone_leak_rate": None}) is True
    assert gap_ledger.detect_intent_leak({"framing_leak_rate": None, "tone_leak_rate": 0.9}) is True
    assert gap_ledger.detect_intent_leak({"framing_leak_rate": 0.0, "tone_leak_rate": None}) is False


def test_R15_a_measured_zero_still_reads_as_clean():
    """The guard must not have made the control unable to PASS -- a genuinely
    measured 0.0 on both axes is still a clean verdict."""
    assert gap_ledger.detect_intent_leak({"framing_leak_rate": 0.0, "tone_leak_rate": 0.0}) is False


# --- R15 mutation proof for the TONE axis (the FRAME proved framing only) ---

_TONE_LEVER_FOR_CATEGORY = {
    "empathetic_responsive": "empathetic_toned",
    "firm_responsive": "firm_toned",
    "neutral": "neutral_toned",
}


def _tone_peeking_generate(customer_id, segment, situation, product, step):
    """The same named defect as `_peeking_generate`, but leaking through the
    TONE lever -- the axis the FRAME-stage exit tests never mutation-proved.
    A control proven on only one of its two axes is half a control."""
    honest = gap_ledger.honest_zero_evidence_generate(customer_id, segment, situation, product, step)
    truth = nudge_physics.tone_susceptibility_for(customer_id)
    return replace(honest, tone=_TONE_LEVER_FOR_CATEGORY[truth.value])


def test_R15_tone_axis_peeking_variant_IS_caught_and_honest_is_not():
    """Both arms over the IDENTICAL population/situation, so the contrast
    cannot be a fixture artefact."""
    pop = gap_ledger._synthetic_population(80)
    honest = gap_ledger.intent_leak_rate(
        gap_ledger.honest_zero_evidence_generate, pop, Situation.MISSED_PAYMENT, Product.DUAL_FUEL
    )
    peeking = gap_ledger.intent_leak_rate(
        _tone_peeking_generate, pop, Situation.MISSED_PAYMENT, Product.DUAL_FUEL
    )
    assert honest["tone_leak_rate"] == 0.0
    assert gap_ledger.detect_intent_leak(honest) is False
    assert peeking["tone_leak_rate"] == 1.0
    assert gap_ledger.detect_intent_leak(peeking) is True
    # and the leak is confined to the axis that actually peeked
    assert peeking["framing_leak_rate"] == 0.0


# --- C-S1 / C-S2: arrival order, lateness, replay -------------------------


def test_CS1_gap_rows_are_invariant_to_customer_arrival_order():
    """C-S1: no logic here may assume a batch arrives complete or in order.
    Per-customer rows must be identical however the population is ordered."""
    pop = gap_ledger._synthetic_population(40)
    est = SusceptibilityEstimator()
    for cust in pop[:20]:
        _feed_confident_framing_belief(est, cust, "loss_framed")

    forward = {r["customer_id"]: r for r in gap_ledger.belief_vs_truth_gap(pop, est)}
    reversed_ = {r["customer_id"]: r for r in gap_ledger.belief_vs_truth_gap(list(reversed(pop)), est)}
    assert forward == reversed_


def test_CS1_intent_leak_rate_is_invariant_to_customer_arrival_order():
    pop = gap_ledger._synthetic_population(60)
    a = gap_ledger.intent_leak_rate(_peeking_generate, pop, Situation.RENEWAL, Product.DUAL_FUEL)
    b = gap_ledger.intent_leak_rate(
        _peeking_generate, list(reversed(pop)), Situation.RENEWAL, Product.DUAL_FUEL
    )
    assert a == b


def test_CS1_gap_measurement_of_a_subset_matches_the_same_customers_in_the_full_batch():
    """Events arriving SINGLY or LATE must give the same per-customer answer
    as the complete batch -- the measurement is per-customer, never a
    batch-completeness assumption."""
    pop = gap_ledger._synthetic_population(30)
    est = SusceptibilityEstimator()
    for cust in pop[:15]:
        _feed_confident_framing_belief(est, cust, "loss_framed")

    full = {r["customer_id"]: r for r in gap_ledger.belief_vs_truth_gap(pop, est)}
    singly = {}
    for cust in pop:  # one at a time, as if each arrived on its own
        (row,) = gap_ledger.belief_vs_truth_gap([cust], est)
        singly[cust] = row
    assert full == singly


# --- ledger durability: a corrupt history must not be silently clobbered ----


def test_record_gap_refuses_to_clobber_a_corrupt_ledger(tmp_path):
    """R15 FAIL-SILENT regression: the FRAME-stage `_load_ledger` swallowed a
    JSONDecodeError into `[]`, so the very next append REWROTE the file and
    the prior history vanished with no error at all."""
    ledger_path = tmp_path / "conversation_gap_ledger.json"
    ledger_path.write_text("{not valid json at all", encoding="utf-8")
    with pytest.raises(gap_ledger.ConversationGapUnmeasurable):
        gap_ledger.record_gap(
            measured_at="t1", ledger_path=ledger_path,
            customer_count=20, situations=[Situation.RENEWAL], training_rounds=5,
        )
    # the corrupt file is left untouched for a human to look at, not overwritten
    assert ledger_path.read_text(encoding="utf-8") == "{not valid json at all"


def test_record_gap_refuses_a_non_list_ledger(tmp_path):
    ledger_path = tmp_path / "conversation_gap_ledger.json"
    ledger_path.write_text('{"rows": []}', encoding="utf-8")
    with pytest.raises(gap_ledger.ConversationGapUnmeasurable):
        gap_ledger.record_gap(
            measured_at="t1", ledger_path=ledger_path,
            customer_count=20, situations=[Situation.RENEWAL], training_rounds=5,
        )


def test_record_gap_still_creates_a_fresh_ledger_when_none_exists(tmp_path):
    """The durability guard must not have broken the legitimate first write."""
    ledger_path = tmp_path / "nested" / "conversation_gap_ledger.json"
    row = gap_ledger.record_gap(
        measured_at="t1", ledger_path=ledger_path,
        customer_count=20, situations=[Situation.RENEWAL], training_rounds=5,
    )
    assert row["measurable"] is True
    assert len(json.loads(ledger_path.read_text(encoding="utf-8"))) == 1


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
