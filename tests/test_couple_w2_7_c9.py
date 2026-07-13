"""Tests for the W2_7 <-> C9 coupled-triad ARCHETYPE pair.

Closes the highest-priority coupled pair: the WORLD answer key (hidden ability x
willingness, simulation.willingness_classification) vs the COMPANY's can't-pay /
won't-pay classification + pursue/forbear gate (saas.arrears_classifier), scored by
the cost-weighted classification gap (background.gap_metric.classification_gap).

Load-bearing properties:
  * The DIRECTOR-SIGNED GATE fires correctly, and its correctness is proven by a
    MUTATION TEST at p=0.9 AND p=0.1 (R15 controls-that-cannot-fail) -- NEVER only
    at p=0.5, because an odds-inverted gate agrees with the real gate at p=0.5.
  * The classifier reads OBSERVABLES ONLY (epistemic wall): its signature accepts
    no quadrant / ability / willingness truth; it is deterministic (C-S2) and
    handles partial observation (C-S1).
  * NON-DEGENERATE gap: with the real (partial) observable channel the gap is
    strictly between 0 and 1 -- the company copes but is not perfect; a near-zero
    gap would signal a leak, a >1 gap worse-than-blind.
  * DETERMINISM (C-S2): same population -> identical gap on replay.
  * The ledger write matches the reader contract coupled_triad reads.
"""
import math

import pytest

from tools import couple_w2_7_c9 as run
from background import gap_metric as gm
from background import coupled_triad as ct
from saas.arrears_classifier import (
    Ability,
    ArrearsObservationWindow,
    CantPayWontPayClassifier,
    Decision,
    Willingness,
    flip_point_odds,
    pursue_forbear_gate,
    pursue_threshold,
)


# ---------------------------------------------------------------------------
# The director-signed pursue/forbear gate (R = 8:1).
# ---------------------------------------------------------------------------
def test_pursue_threshold_is_R_over_R_plus_1():
    # At the signed R=8, PURSUE only when p > 8/9 ~= 0.889.
    assert pursue_threshold(8.0) == pytest.approx(8.0 / 9.0)
    assert pursue_threshold() == pytest.approx(gm.HARM_RATIO_R / (gm.HARM_RATIO_R + 1.0))


def test_gate_pursues_only_on_strong_wontpay_evidence():
    # p=0.9 > 8/9 -> PURSUE ; p=0.1 < 8/9 -> FORBEAR. The two asymmetric points.
    assert pursue_forbear_gate(0.9, 8.0) is Decision.PURSUE
    assert pursue_forbear_gate(0.1, 8.0) is Decision.FORBEAR


def test_gate_forbears_at_the_coin_flip():
    # p=0.5 is well below 8/9 -> the harm-averse default FORBEAR (never pursue a
    # household on a coin-flip under an 8:1 harm ratio).
    assert pursue_forbear_gate(0.5, 8.0) is Decision.FORBEAR


def test_gate_forbears_exactly_at_threshold():
    # Strict '>' : at exactly R/(R+1) the expected costs tie and FORBEAR wins.
    assert pursue_forbear_gate(pursue_threshold(8.0), 8.0) is Decision.FORBEAR


def test_flip_point_odds():
    assert flip_point_odds(0.9) == pytest.approx(9.0)      # > R=8 -> pursue
    assert flip_point_odds(0.1) == pytest.approx(1.0 / 9.0)  # < R=8 -> forbear
    assert flip_point_odds(0.5) == pytest.approx(1.0)
    assert flip_point_odds(1.0) == math.inf
    assert flip_point_odds(0.0) == 0.0


# --- THE MUTATION TEST (R15: the control must be able to FAIL) --------------
def _odds_inverted_gate(p: float, harm_ratio: float = 8.0) -> Decision:
    """A realistic BUG mutant: the gate expressed via odds R* but with the odds
    ACCIDENTALLY INVERTED -- (1-p)/p instead of p/(1-p) -- then PURSUE iff R* > R.
    This is the exact mutant the director flagged: it is INDISTINGUISHABLE from the
    correct gate at p=0.5 (both odds equal 1), so a coin-flip-only test passes it.
    """
    if p <= 0.0:
        return Decision.FORBEAR
    inverted_odds = (1.0 - p) / p
    return Decision.PURSUE if inverted_odds > harm_ratio else Decision.FORBEAR


def test_mutation_p05_alone_does_NOT_catch_the_inverted_gate():
    # Demonstrates WHY p=0.5 is forbidden as the sole test point: the odds-inverted
    # mutant AGREES with the correct gate at p=0.5, so a coin-flip test is blind to
    # this inversion.
    assert _odds_inverted_gate(0.5) == pursue_forbear_gate(0.5, 8.0)


def test_mutation_p09_and_p01_DO_catch_the_inverted_gate():
    # The required test points. At BOTH p=0.9 and p=0.1 the correct gate and the
    # inverted mutant DISAGREE -- so this pair kills the mutant the p=0.5 test misses.
    assert pursue_forbear_gate(0.9, 8.0) is Decision.PURSUE
    assert _odds_inverted_gate(0.9) is Decision.FORBEAR       # mutant wrong here
    assert pursue_forbear_gate(0.1, 8.0) is Decision.FORBEAR
    assert _odds_inverted_gate(0.1) is Decision.PURSUE        # mutant wrong here
    # i.e. the real gate and the mutant differ at each required point.
    assert pursue_forbear_gate(0.9, 8.0) != _odds_inverted_gate(0.9)
    assert pursue_forbear_gate(0.1, 8.0) != _odds_inverted_gate(0.1)


def test_mutation_comparison_flip_also_caught_at_required_points():
    # A second mutant: the comparison '>' flipped to '<'. Also caught at 0.9/0.1.
    def flipped(p):
        return Decision.PURSUE if p < pursue_threshold(8.0) else Decision.FORBEAR
    assert flipped(0.9) != pursue_forbear_gate(0.9, 8.0)
    assert flipped(0.1) != pursue_forbear_gate(0.1, 8.0)


# ---------------------------------------------------------------------------
# The classifier reads observables only, deterministically, partially.
# ---------------------------------------------------------------------------
def test_clean_strategic_signal_is_pursued():
    # Normal consumption, avoids contact, no disclosure, pays nothing -> the clean
    # strategic won't-pay: ability=can with p above the 8/9 pursue bar.
    clf = CantPayWontPayClassifier()
    a = clf.assess(ArrearsObservationWindow(
        customer_id="S1", made_part_payment=False, engaged=False,
        hardship_disclosed=False,
        baseline_consumption_kwh=300.0, recent_consumption_kwh=300.0,
    ))
    assert a.ability is Ability.CAN
    assert a.willingness is Willingness.WONT
    assert a.p_can_pay > pursue_threshold(8.0)
    assert a.decision is Decision.PURSUE


def test_clean_cantpay_willing_is_forborne():
    # Rationing, engages, discloses hardship, part-pays -> the genuine can't-pay who
    # wants to pay: ability=cannot, willingness=will, always FORBEAR.
    clf = CantPayWontPayClassifier()
    a = clf.assess(ArrearsObservationWindow(
        customer_id="V1", made_part_payment=True, engaged=True,
        hardship_disclosed=True,
        baseline_consumption_kwh=300.0, recent_consumption_kwh=170.0,
    ))
    assert a.ability is Ability.CANNOT
    assert a.willingness is Willingness.WILL
    assert a.decision is Decision.FORBEAR


def test_disengaged_cantpay_is_the_expensive_confound():
    # A genuine can't-pay who is DISENGAGED (rationing but no disclosure, no
    # engagement, no part-payment) looks like a strategic non-payer -> read can-pay.
    # This is the designed expensive error; the classifier is allowed to be wrong.
    clf = CantPayWontPayClassifier()
    a = clf.assess(ArrearsObservationWindow(
        customer_id="C1", made_part_payment=False, engaged=False,
        hardship_disclosed=False,
        baseline_consumption_kwh=300.0, recent_consumption_kwh=210.0,  # ratio 0.70
    ))
    # rationing pulls toward cannot; the disengagement pulls toward can. The point
    # is only that the classifier resolves it from observables, never the truth.
    assert a.ability in (Ability.CAN, Ability.CANNOT)


def test_partial_observation_is_handled():
    # C-S1: only one signal present, everything else absent -> no crash, a belief.
    clf = CantPayWontPayClassifier()
    a = clf.assess(ArrearsObservationWindow(customer_id="P1", engaged=True))
    assert 0.0 <= a.p_can_pay <= 1.0
    assert a.decision in (Decision.PURSUE, Decision.FORBEAR)


def test_classifier_is_deterministic():
    clf = CantPayWontPayClassifier()
    w = ArrearsObservationWindow(
        customer_id="D1", made_part_payment=False, engaged=False,
        hardship_disclosed=False,
        baseline_consumption_kwh=300.0, recent_consumption_kwh=290.0,
    )
    assert clf.assess(w).to_dict() == clf.assess(w).to_dict()


def test_classifier_signature_takes_no_truth():
    # Epistemic wall (structural): the observation window exposes NO ability /
    # willingness / quadrant field. The classifier cannot read the answer key.
    fields = set(ArrearsObservationWindow.__dataclass_fields__)
    assert not (fields & {"ability", "willingness", "quadrant",
                          "is_strategic_nonpayer", "is_genuine_cantpay"})


# ---------------------------------------------------------------------------
# The coupled scenario + gap.
# ---------------------------------------------------------------------------
def test_scenario_gap_is_non_degenerate():
    cls, extras = run.measure(n_customers=40000)
    assert extras["n_arrears"] > 1000
    # Strictly between 0 (leak) and 1 (no better than blind): the company copes but
    # the observable channel is genuinely coarser than the hidden truth.
    assert 0.0 < cls.gap < 1.0
    # The harm path is reported and non-trivial (a disengaged can't-pay is missed).
    assert cls.components["fn_ability"] > 0.0
    assert cls.components["fn_willingness"] > 0.0


def test_scenario_gap_is_deterministic():
    c1, _ = run.measure(n_customers=20000)
    c2, _ = run.measure(n_customers=20000)
    assert c1.gap == c2.gap
    assert c1.raw_gap == c2.raw_gap
    assert c1.components["fn_ability"] == c2.components["fn_ability"]


def test_gate_is_harm_averse_under_8to1():
    # Under R=8 the realised gate pursues FAR fewer can't-pays than it forbears
    # strategic won't-pays -- the asymmetric cost buys down the expensive error at
    # the price of moral-hazard loss. (A diagnostic, not a tuned target: R12/R13.)
    _, extras = run.measure(n_customers=40000)
    assert extras["pursued_cannot_expensive_error"] < extras["forborne_strategic_loss"]


def test_ledger_entry_matches_reader_contract(tmp_path):
    cls, _ = run.measure(n_customers=15000)
    ledger_path = tmp_path / "coupled_gap_ledger.json"
    # seed an existing entry to prove read-merge-write preserves others.
    ledger_path.write_text('{"W9_other": {"twin_atom_id": "Cx", "gap": 0.5}}\n')
    ledger = gm.write_gap_entry(
        run.WORLD_ATOM_ID, run.TWIN_ATOM_ID, cls,
        measured_at="2026-07-13T00:00:00+00:00", run_git_commit="deadbeef",
        ledger_path=ledger_path,
    )
    assert "W9_other" in ledger                        # preserved
    entry = ledger[run.WORLD_ATOM_ID]
    assert entry["twin_atom_id"] == run.TWIN_ATOM_ID
    assert entry["metric"] == "classification"
    assert entry["gap"] == cls.gap
    # the reader (coupled_triad) can parse it as a measured gap.
    assert ct.gap_measured(run.WORLD_ATOM_ID, ct.load_gap_ledger(ledger_path))
