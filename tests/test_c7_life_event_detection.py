"""C7_life_event_detection -- unit + coupled-gap wiring tests.

Two layers:
  1. The detector reads OBSERVABLES only and behaves sensibly (unit tests).
  2. The W2_5 <-> C7 coupled gap wiring is REAL, not theatre: MUTATION tests
     prove the detection-gap fires on its named defects -- a perfect detector
     drives the gap to 0, a blind (flag-nobody) detector to 1, and the harm
     weighting is load-bearing (missing high-harm events costs more than missing
     low-harm ones). Per CLAUDE.md R15: a control that cannot fail is worse than
     none.
"""

import datetime as dt

import pytest

from company.crm.life_event_detector import (
    LifeEventDetector,
    ObservationWindow,
    _bad_rate,
)
from company.crm.life_events import LifeEventType
from company.crm.vulnerability_register import VulnerabilityFlag, VulnerabilityRegister


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def _pay(result, n):
    return [{"result": result, "days_late": 0} for _ in range(n)]


def _mix(on_time, late, dd):
    return (_pay("ON_TIME", on_time) + _pay("LATE", late) + _pay("DD_FAILED", dd))


# --------------------------------------------------------------------------
# 1. detector unit behaviour
# --------------------------------------------------------------------------

def test_bad_rate_none_on_empty():
    assert _bad_rate([]) is None


def test_clean_customer_not_flagged():
    det = LifeEventDetector()
    w = ObservationWindow(
        "C1",
        baseline_payments=_pay("ON_TIME", 12),
        recent_payments=_pay("ON_TIME", 12),
    )
    r = det.detect(w)
    assert r.distress_detected is False
    assert r.inferred_event_type is None
    assert r.vulnerability_flags == ()
    assert r.confidence == 0.0


def test_severe_deterioration_flags_distress():
    det = LifeEventDetector()
    w = ObservationWindow(
        "C2",
        baseline_payments=_pay("ON_TIME", 12),
        recent_payments=_mix(1, 3, 8),   # 11/12 bad -> severe
    )
    r = det.detect(w)
    assert r.distress_detected is True
    assert r.confidence >= 0.7
    assert r.inferred_event_type == LifeEventType.JOB_LOSS
    assert VulnerabilityFlag.PAYMENT_DIFFICULTY in r.vulnerability_flags
    assert VulnerabilityFlag.JOB_LOSS in r.vulnerability_flags


def test_delta_trigger_on_clean_baseline():
    # Recent bad rate ~0.33 with a spotless baseline -> the jump alone triggers.
    det = LifeEventDetector()
    w = ObservationWindow(
        "C3",
        baseline_payments=_pay("ON_TIME", 12),
        recent_payments=_mix(8, 2, 2),   # 4/12 bad = 0.33
    )
    r = det.detect(w)
    assert r.distress_detected is True
    assert r.signals["bad_rate_delta"] == pytest.approx(4 / 12, abs=1e-3)


def test_consumption_drop_plus_contact_reads_as_divorce():
    det = LifeEventDetector()
    w = ObservationWindow(
        "C4",
        baseline_payments=_pay("ON_TIME", 12),
        recent_payments=_pay("ON_TIME", 12),   # payments fine
        baseline_consumption_kwh=3000.0,
        recent_consumption_kwh=2400.0,          # -20%
        inbound_hardship_contacts=1,
    )
    r = det.detect(w)
    assert r.distress_detected is True          # consumption shift + contact
    assert r.inferred_event_type == LifeEventType.DIVORCE


def test_consumption_shift_without_contact_not_flagged_on_its_own():
    det = LifeEventDetector()
    w = ObservationWindow(
        "C5",
        baseline_payments=_pay("ON_TIME", 12),
        recent_payments=_pay("ON_TIME", 12),
        baseline_consumption_kwh=3000.0,
        recent_consumption_kwh=3600.0,          # +20% but no payment/contact
    )
    r = det.detect(w)
    assert r.distress_detected is False


def test_missing_baseline_still_detects_on_absolute_rate():
    # C-S1: partial observation. No baseline window, but recent is clearly bad.
    det = LifeEventDetector()
    w = ObservationWindow(
        "C6",
        baseline_payments=(),
        recent_payments=_mix(2, 4, 6),
    )
    r = det.detect(w)
    assert r.distress_detected is True
    assert r.signals["baseline_bad_rate"] is None


def test_apply_to_register_writes_flags_then_noop_on_clean():
    det = LifeEventDetector()
    reg = VulnerabilityRegister()

    flagged = det.detect(ObservationWindow(
        "C7", baseline_payments=_pay("ON_TIME", 12),
        recent_payments=_mix(1, 3, 8)))
    det.apply_to_register(reg, flagged, dt.date(2020, 6, 1))
    rec = reg.get("C7")
    assert rec is not None
    assert VulnerabilityFlag.PAYMENT_DIFFICULTY in rec.flags
    # required_actions from the register wire a real support response.
    assert "payment_plan" in rec.required_actions

    clean = det.detect(ObservationWindow(
        "C8", baseline_payments=_pay("ON_TIME", 12),
        recent_payments=_pay("ON_TIME", 12)))
    det.apply_to_register(reg, clean, dt.date(2020, 6, 1))
    assert reg.get("C8") is None                 # no-op on no-detection


# --------------------------------------------------------------------------
# 2. coupled W2_5 <-> C7 gap wiring (with R15 mutation tests)
# --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def scenario():
    from tools.couple_w2_5_c7 import build_scenario
    return build_scenario(400, 2016, 2025)


def test_scenario_is_non_degenerate(scenario):
    from background.gap_metric import detection_gap
    truth, flagged, harm, stats = scenario
    assert stats["n_truth"] > 50                 # a real truth set exists
    r = detection_gap(truth, flagged, harm=harm)
    assert r.gap is not None
    assert 0.0 < r.gap < 1.0                     # honest steady state, not leak/blind
    assert r.metric == "detection"


def test_scenario_is_deterministic():
    # C-S2: same seed -> byte-identical coupled outcome.
    from tools.couple_w2_5_c7 import build_scenario
    from background.gap_metric import detection_gap
    t1, f1, h1, _ = build_scenario(300, 2016, 2025)
    t2, f2, h2, _ = build_scenario(300, 2016, 2025)
    assert t1 == t2 and f1 == f2 and h1 == h2
    assert detection_gap(t1, f1, harm=h1).gap == detection_gap(t2, f2, harm=h2).gap


def test_mutation_perfect_detector_drives_gap_to_zero(scenario):
    # If the company flagged EXACTLY the true distress set, the miss-gap is 0.
    from background.gap_metric import detection_gap
    truth, _flagged, harm, _ = scenario
    r = detection_gap(truth, set(truth), harm=harm)   # perfect recall
    assert r.gap == 0.0


def test_mutation_blind_detector_drives_gap_to_one(scenario):
    # If the company flagged NOBODY, all detectable harm is missed -> gap 1.
    from background.gap_metric import detection_gap
    truth, _flagged, harm, _ = scenario
    r = detection_gap(truth, set(), harm=harm)
    assert r.gap == 1.0


def test_mutation_harm_weighting_is_load_bearing(scenario):
    # Missing the HIGHEST-harm events must cost strictly more than missing the
    # same number of LOWEST-harm events -> the harm weighting is real, not a
    # tautology that would pass on any monotone relabelling (R15 independence).
    from background.gap_metric import detection_gap
    truth, _flagged, harm, _ = scenario
    ordered = sorted(truth, key=lambda i: harm[i])
    k = 20
    low = ordered[:k]                # lowest-harm instances
    high = ordered[-k:]             # highest-harm instances
    gap_miss_low = detection_gap(truth, set(truth) - set(low), harm=harm).gap
    gap_miss_high = detection_gap(truth, set(truth) - set(high), harm=harm).gap
    assert gap_miss_high > gap_miss_low > 0.0


def test_detector_recall_is_high_but_not_perfect(scenario):
    # The measured finding: distress is HIGHLY observable via the payment
    # channel, so recall is near-perfect -- but strictly < 1.0 (some low-harm
    # events are missed), confirming this is NOT a theta leak (a leak would give
    # perfect recall with zero false positives).
    truth, flagged, _harm, stats = scenario
    recall = stats["true_positives"] / stats["n_truth"]
    assert 0.90 <= recall < 1.0
    # ... and the miss-only metric is blind to a real false-positive cost:
    assert stats["false_positives"] > 0
