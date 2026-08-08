"""CHARACTERIZATION tests for the D6 finding: the coupled-triad AGEING dimension's
normalisation is the wrong shape, so its output (live: 1.1538) is not evidence.

These tests pin the CURRENT, DEFECTIVE behaviour of
`background.gap_metric.misapplication_gap` as used for the ageing dimension by
`tools.couple_w2_11_d5.score_triad`. They are deliberately written to FAIL when
the metric is reshaped (atom `D7_ageing_gap_metric_reshape`) -- that failure is
the signal that the fix landed, at which point these are replaced by tests of the
new measures, not "repaired".

Verdict + evidence: docs/design/D6_PAYMENT_AGEING_GAP_VALIDITY_DISCOVER.md
Re-runnable oracle:  tools/d6_ageing_metric_oracle.py

R15 note: each test's expected value comes from an INDEPENDENT reading of what the
company did (found all arrears / off by one bucket / behaviour held fixed), never
from re-running the metric to see what it says. The metric is the thing on trial.
"""
from __future__ import annotations

import pytest

from background.gap_metric import misapplication_gap
from tools.d6_ageing_metric_oracle import (
    N_CURRENT,
    N_FALSE_POSITIVES,
    N_OVERDUE,
    belief_finds_all_arrears,
    labels,
)


def _gap(truth, belief) -> float:
    return misapplication_gap(list(truth), list(belief)).gap


def test_oracle_anchors_hold_the_metric_is_not_broken_everywhere():
    """Sanity anchors -- without these the tests below prove nothing (a metric
    that returned garbage for every input would 'pass' them vacuously)."""
    truth = labels(N_CURRENT, N_OVERDUE)
    assert _gap(truth, truth) == 0.0, "perfect ageing must score 0"
    assert _gap(truth, ["current"] * (N_CURRENT + N_OVERDUE)) == pytest.approx(1.0), (
        "the no-skill baseline must score exactly 1 -- it IS the normaliser"
    )


def test_defect_1_above_one_does_not_mean_worse_than_no_skill():
    """A company that finds EVERY real arrears case with a 1.5% false-positive
    rate is strictly better than one that reports no arrears at all. The metric
    scores it 1.50 -- 'worse than doing nothing'. That is the régime the live
    1.1538 sits in."""
    truth = labels(N_CURRENT, N_OVERDUE)
    good_company = belief_finds_all_arrears(N_CURRENT, N_OVERDUE)

    # Independent reading: zero missed arrears, N_FALSE_POSITIVES false alarms.
    misses = sum(1 for t, b in zip(truth, good_company) if t != "current" and b == "current")
    false_alarms = sum(1 for t, b in zip(truth, good_company) if t == "current" and b != "current")
    assert misses == 0
    assert false_alarms == N_FALSE_POSITIVES

    assert _gap(truth, good_company) == pytest.approx(1.5), (
        "characterization: finds-all-arrears scores 1.5 (worse-than-no-skill) today"
    )


def test_defect_2_score_is_driven_by_world_prevalence_not_by_the_company():
    """Hold the company's belief vector LITERALLY fixed and move only the world's
    arrears prevalence: the gap swings 3.00 -> 0.15, a twentyfold change with the
    company unchanged. A company-fidelity measure must be flat here."""
    expected = {5: 3.0, 10: 1.5, 20: 0.75, 50: 0.3, 100: 0.15}
    observed = {}
    for n_over, want in expected.items():
        truth = labels(N_CURRENT, n_over)
        belief = belief_finds_all_arrears(N_CURRENT, n_over)
        # The company's error set is identical in every case: all arrears found,
        # the same N_FALSE_POSITIVES false alarms on the same settled population.
        assert sum(1 for t, b in zip(truth, belief) if t != b) == N_FALSE_POSITIVES
        observed[n_over] = _gap(truth, belief)
        assert observed[n_over] == pytest.approx(want)

    assert max(observed.values()) / min(observed.values()) == pytest.approx(20.0), (
        "characterization: prevalence alone moves the score twentyfold"
    )


def test_defect_3_metric_is_blind_to_bucket_ORDER():
    """`current < 30-60 < 60-90 < 90+` is an ORDERED space; a Hamming error rate
    is not. Believing a 90+ debt is 60-90 (one bucket out, arrears correctly
    identified) scores identically to not seeing the debt at all."""
    truth = labels(N_CURRENT, N_OVERDUE)
    off_by_one = ["current"] * N_CURRENT + ["60-90"] * N_OVERDUE
    totally_blind = ["current"] * (N_CURRENT + N_OVERDUE)

    assert _gap(truth, off_by_one) == _gap(truth, totally_blind) == pytest.approx(1.0), (
        "characterization: one-bucket-out and stone-blind are indistinguishable"
    )


def test_the_ageing_dimension_still_routes_through_this_metric():
    """Guard against the finding silently detaching from the code it is about: if
    `score_triad` stops scoring ageing with `misapplication_gap`, the tests above
    are no longer characterizing anything live and must be revisited."""
    import inspect

    from tools import couple_w2_11_d5

    src = inspect.getsource(couple_w2_11_d5.score_triad)
    assert "misapplication_gap(true_ageing_labels, belief_ageing_labels)" in src, (
        "ageing no longer scored by misapplication_gap -- re-read "
        "docs/design/D6_PAYMENT_AGEING_GAP_VALIDITY_DISCOVER.md before editing these tests"
    )
