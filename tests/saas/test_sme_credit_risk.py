"""C8_sme_credit_risk -- unit + coupled-gap wiring tests.

Two layers:
  1. The assessor reads OBSERVABLES only and disentangles the distress-vs-culture
     confound sensibly (unit tests).
  2. The W2_6 <-> C8 coupled gap wiring is REAL, not theatre: MUTATION tests prove
     the classification gap fires on its named defects -- a perfect assessor drives
     the gap to 0, a blind (predict-majority) assessor to 1, and the 8:1 harm
     asymmetry is load-bearing (reading real distress as mere culture costs more
     than the mirror). Per CLAUDE.md R15: a control that cannot fail is worse than
     none.

The harness (tools.couple_w2_6_c8) may import simulation.*; this test imports it
to exercise the LIVE coupled loop, but the twin under test (saas.sme_credit_risk)
imports nothing from the SIM -- asserted directly below.
"""

from __future__ import annotations

import pathlib

import pytest

from saas.sme_credit_risk import (
    BusinessObservationWindow,
    CreditRiskCause,
    SmeCreditRiskAssessor,
    cause_to_quadrant,
)
from background.gap_metric import classification_gap, harm_cost


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def _pay(result: str, n: int, days_late: int = 20) -> list[dict]:
    return [{"result": result, "days_late": (days_late if result != "ON_TIME" else 0)}
            for _ in range(n)]


def _mix(n_bad: int, n_ok: int) -> list[dict]:
    return _pay("LATE", n_bad) + _pay("ON_TIME", n_ok)


# --------------------------------------------------------------------------
# 1. Unit: observables-only disentangling
# --------------------------------------------------------------------------
def test_on_time_business_is_no_concern():
    a = SmeCreditRiskAssessor()
    r = a.assess(BusinessObservationWindow(
        customer_id="B1", segment="SME", sector="professional_services",
        tenure_years=5.0,
        baseline_payments=_pay("ON_TIME", 12),
        recent_payments=_pay("ON_TIME", 12),
    ))
    assert r.inferred_cause is CreditRiskCause.NONE
    assert r.is_late is False
    assert r.quadrant == ("can", "will")


def test_persistent_late_low_risk_sector_reads_as_culture():
    # Always late in BOTH windows, no worsening, resilient sector -> habitual.
    a = SmeCreditRiskAssessor()
    r = a.assess(BusinessObservationWindow(
        customer_id="B2", segment="SME", sector="professional_services",
        tenure_years=6.0,
        baseline_payments=_mix(10, 2),
        recent_payments=_mix(10, 2),
    ))
    assert r.inferred_cause is CreditRiskCause.CULTURE
    assert r.quadrant == ("can", "wont")


def test_clean_baseline_then_late_reads_as_distress():
    # A sudden deterioration off a clean baseline -> genuine onset.
    a = SmeCreditRiskAssessor()
    r = a.assess(BusinessObservationWindow(
        customer_id="B3", segment="SME", sector="professional_services",
        tenure_years=4.0,
        baseline_payments=_pay("ON_TIME", 12),
        recent_payments=_mix(9, 3),
    ))
    assert r.inferred_cause is CreditRiskCause.DISTRESS
    assert r.quadrant == ("cannot", "wont")


def test_severe_late_with_consumption_collapse_reads_as_insolvency():
    a = SmeCreditRiskAssessor()
    r = a.assess(BusinessObservationWindow(
        customer_id="B4", segment="I&C", sector="construction",
        tenure_years=3.0,
        baseline_payments=_pay("ON_TIME", 12),
        recent_payments=_pay("DD_FAILED", 12),
        baseline_consumption_kwh=12000.0,
        recent_consumption_kwh=800.0,      # ~93% collapse
    ))
    assert r.inferred_cause is CreditRiskCause.INSOLVENCY
    assert r.quadrant == ("cannot", "wont")


def test_the_hard_confound_always_late_business_reads_as_culture():
    # THE confound: a business that has ALWAYS been late looks identical whether it
    # is healthy-habitual or has quietly slid into distress. With no deterioration
    # handle the company reads CULTURE -- i.e. it WILL miss the distressed ones.
    # This is the designed failure the gap measures, asserted here as behaviour.
    a = SmeCreditRiskAssessor()
    r = a.assess(BusinessObservationWindow(
        customer_id="B5", segment="SME", sector="professional_services",
        tenure_years=7.0,
        baseline_payments=_mix(11, 1),
        recent_payments=_mix(11, 1),
    ))
    assert r.inferred_cause is CreditRiskCause.CULTURE


def test_empty_recent_window_yields_no_false_opinion():
    a = SmeCreditRiskAssessor()
    r = a.assess(BusinessObservationWindow(
        customer_id="B6", segment="SME", recent_payments=(), baseline_payments=(),
    ))
    assert r.inferred_cause is CreditRiskCause.NONE  # no observation -> no opinion


def test_cause_to_quadrant_accepts_enum_and_sim_string():
    assert cause_to_quadrant(CreditRiskCause.DISTRESS) == ("cannot", "wont")
    # The SIM answer-key string values project onto the SAME 2x2 space.
    assert cause_to_quadrant("distress") == ("cannot", "wont")
    assert cause_to_quadrant("culture") == ("can", "wont")
    assert cause_to_quadrant("none") == ("can", "will")
    with pytest.raises(ValueError):
        cause_to_quadrant("bankrupt")


# --------------------------------------------------------------------------
# Epistemic wall: the twin imports nothing from the SIM.
# --------------------------------------------------------------------------
def test_twin_module_has_no_sim_import():
    src = pathlib.Path(
        __file__).resolve().parents[2] / "saas" / "sme_credit_risk.py"
    text = src.read_text(encoding="utf-8")
    assert "import simulation" not in text
    assert "from simulation" not in text
    assert "import sim" not in text and "from sim" not in text


# --------------------------------------------------------------------------
# 2. MUTATION / R15: the classification-gap control must be able to FAIL.
# --------------------------------------------------------------------------
def test_harm_asymmetry_is_load_bearing():
    # Reading genuine distress (cannot) as mere culture (can) is the expensive
    # error; the mirror is cheap. If these were equal the control would be blind
    # to the confound that matters.
    distress_as_culture = harm_cost(("cannot", "wont"), ("can", "wont"))
    culture_as_distress = harm_cost(("can", "wont"), ("cannot", "wont"))
    assert distress_as_culture == 8.0
    assert culture_as_distress == 1.0
    assert distress_as_culture > culture_as_distress


def test_perfect_assessor_drives_gap_to_zero():
    truth = [("can", "will"), ("cannot", "wont"), ("can", "wont"),
             ("cannot", "wont"), ("can", "will")]
    perfect = list(truth)
    assert classification_gap(truth, perfect).gap == 0.0


def test_blind_majority_assessor_drives_gap_to_one():
    # Predicting the majority quadrant on every instance == the no-skill baseline,
    # so gap == 1.0 by construction. A control that could not reach 1 here would
    # be fail-open theatre.
    truth = [("can", "will")] * 6 + [("cannot", "wont")] * 4
    blind = [("can", "will")] * 10          # always the majority
    assert classification_gap(truth, blind).gap == pytest.approx(1.0)


def test_mutating_a_distress_label_to_culture_worsens_the_gap():
    # Independence check: flipping ONE truly-distressed instance from a correct
    # (cannot) belief to a (can) belief must RAISE the gap by the 8:1 harm -- if it
    # didn't, the gap would not actually be reading the ability confound.
    truth = [("cannot", "wont")] * 3 + [("can", "will")] * 7
    good = list(truth)
    mutated = list(truth)
    mutated[0] = ("can", "wont")            # distress misread as culture
    assert classification_gap(truth, mutated).gap > classification_gap(truth, good).gap


# --------------------------------------------------------------------------
# 3. The LIVE coupled loop produces a NON-DEGENERATE, deterministic gap.
# --------------------------------------------------------------------------
def test_live_coupled_gap_is_non_degenerate_and_deterministic():
    from tools.couple_w2_6_c8 import measure

    cls_a, attr_a, extras_a = measure(n_customers=400)
    cls_b, attr_b, extras_b = measure(n_customers=400)

    # Deterministic (C-S2): identical inputs -> identical gap.
    assert cls_a.gap == cls_b.gap
    assert attr_a.gap == attr_b.gap

    # Non-degenerate: learned SOME, not all. A 0 would mean the observables leaked
    # the hidden cause (a wall violation); a >=1 would mean no skill at all.
    assert 0.0 < cls_a.gap < 1.0

    # The confound actually bites: the company misses a material share of genuine
    # distress by reading it as culture (the expensive cannot->can error exists).
    assert extras_a["distress_missed_as_culture"] > 0
    assert cls_a.components["fn_ability"] > 0.0


def test_live_scenario_never_reads_the_hidden_cause():
    # The assessor's belief is derived from observables only: its distress rate
    # among late instances must DIFFER from the truth's (if they were equal the
    # company would be reading the answer key -- a tautology / leak).
    from tools.couple_w2_6_c8 import measure
    _, _, extras = measure(n_customers=400)
    assert extras["delta_naive_distress_share"] != extras["delta_true_distress_share"]
