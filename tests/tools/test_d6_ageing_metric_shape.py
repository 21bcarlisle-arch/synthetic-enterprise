"""CHARACTERIZATION tests for the D6 finding: the coupled-triad AGEING dimension's
normalisation is the wrong shape, so its output (live: 1.1538) is not evidence.

These tests pin the behaviour of `background.gap_metric.misapplication_gap` that
made it the wrong shape for the ageing dimension.

STATUS 2026-08-08: the reshape LANDED (`D7_ageing_gap_metric_reshape`). The
ageing dimension now uses `background.gap_metric.ageing_gap` and the last test in
this file is inverted to prove it left. The three defect tests stay, and stay
green, because `misapplication_gap` is UNCHANGED -- it still scores the W2_9<->C11
segment-debt pair, so these three are a live record of what that metric does to
whoever calls it, not a historical note. The measures that replaced it, and the
mutants proving they measure, are in `tests/tools/test_d7_ageing_measures.py`.

Verdict + evidence: docs/design/D6_PAYMENT_AGEING_GAP_VALIDITY_DISCOVER.md
Re-runnable oracle:  tools/d6_ageing_metric_oracle.py (now prints BOTH criteria
                     over the same rows, old above new)

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


def test_the_ageing_dimension_has_LEFT_this_metric():
    """The D7 reshape landed (2026-08-08), so this test is INVERTED from what it
    was: the ageing dimension must no longer route through `misapplication_gap`.

    Its predecessor asserted the opposite -- that ageing DID route through this
    metric -- and was written to fail the moment the reshape landed. It did; this
    is the replacement, not a repair. The three defects above stay as live
    characterization because `misapplication_gap` itself is UNCHANGED and still
    scores the W2_9<->C11 segment-debt pair: they now document why the ageing
    dimension left, and they will fail loudly if anyone ever "fixes" the metric
    in place under those other callers (see MISAPPLICATION_PREVALENCE_CAVEAT,
    which is stamped into every one of its results).
    """
    import inspect

    from tools import couple_w2_11_d5

    # Whitespace-insensitive since D16 made the call multi-line -- see the twin
    # of this control in tests/tools/test_d7_ageing_measures.py.
    src = inspect.getsource(couple_w2_11_d5.score_triad)
    compact = "".join(src.split())
    assert "misapplication_gap(true_ageing_labels" not in src, (
        "the retired prevalence-normalised scalar is back on the ageing dimension"
    )
    assert "ageing_gap(true_ageing_labels,belief_ageing_labels," in compact, (
        "ageing is scored by neither metric -- re-read docs/design/"
        "D6_PAYMENT_AGEING_GAP_VALIDITY_DISCOVER.md and tests/tools/"
        "test_d7_ageing_measures.py"
    )
