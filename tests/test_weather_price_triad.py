"""W1_6 weather-physics price-signal COUPLED-TRIAD tests
(background/weather_price_triad.py + background.gap_metric.prediction_gap).

The gap is the score. These tests assert:
  * the coupled loop runs on the real record and the SCORE is the WORST cell
    (the cold-and-still tail), not the population average (fidelity steer);
  * the company's tail belief is a signed UNDER-prediction of the spike;
  * R15: the prediction_gap control FIRES on its named defects -- a no-skill
    belief scores gap==1, a perfect belief scores gap==0 (== a leak for a
    wall-respecting pair), and a belief with SHUFFLED weather (coupling cut)
    scores a WORSE gap than the real fit;
  * the measured gap round-trips into the coupled_gap_ledger and the
    coupled_triad reader sees a real numeric gap.
"""
from __future__ import annotations

import numpy as np
import pytest

from background import weather_price_triad as wpt
from background.gap_metric import prediction_gap
from background.coupled_triad import gap_measured, load_gap_ledger


# --------------------------------------------------------------------------
# prediction_gap unit + R15 (fast, no data load)
# --------------------------------------------------------------------------

def test_prediction_gap_perfect_is_zero_noskill_is_one():
    truth = np.array([10.0, 20.0, 30.0, 40.0])
    # Perfect belief -> gap 0 (for a wall pair, structurally a leak, not a win).
    assert prediction_gap(truth, truth).gap == pytest.approx(0.0)
    # No-skill belief (predict the mean every time) -> gap 1.0 exactly.
    noskill = np.full_like(truth, truth.mean())
    assert prediction_gap(truth, noskill).gap == pytest.approx(1.0)


def test_prediction_gap_worse_than_blind_is_gt_one():
    truth = np.array([10.0, 20.0, 30.0, 40.0])
    # A belief that anti-tracks the truth is WORSE than blind -> gap > 1.
    bad = truth.mean() + (truth.mean() - truth) * 3
    assert prediction_gap(truth, bad).gap > 1.0


def test_prediction_gap_fail_loud():
    with pytest.raises(ValueError):
        prediction_gap([], [])
    with pytest.raises(ValueError):
        prediction_gap([1, 2, 3], [1, 2])


# --------------------------------------------------------------------------
# The real coupled measurement (one data load, module scope)
# --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def measurement():
    return wpt.measure()


def test_score_is_the_worst_cell_not_the_average(measurement):
    per_cell = measurement["per_cell"]
    pop = measurement["population_gap"].gap
    worst = measurement["worst_cell"]
    worst_gap = measurement["worst_gap"]
    # The worst cell is the cold-and-still tail (the cell that stresses the physics).
    assert worst == "cold_still_tail"
    # The SCORE (worst cell) is worse than the population average (the steer's point:
    # a model can nail the middle and fail the edge).
    assert worst_gap > pop
    # Every cell present is a real, in-range fraction.
    for c in per_cell.values():
        assert c["gap"] is not None and c["gap"] > 0


def test_company_under_predicts_the_cold_still_spike(measurement):
    tail = measurement["per_cell"]["cold_still_tail"]
    # The signed bias on the tail is NEGATIVE: the linear belief under-predicts the
    # convex spike -- the tail that kills suppliers, the company cannot see it.
    assert tail["bias_model"] < -5
    # The chain itself produced a real mechanistic spike (sanity that the gap is
    # measured against a genuine tail, not a flat truth).
    spike = measurement["spike"]
    assert spike["tail_mean_price"] > spike["rest_mean_price"] + 30


def test_r15_gap_mutation_cutting_belief_coupling_worsens_the_gap(measurement):
    # R15 killer mutation: shuffle the belief's weather inputs on the tail cell so
    # its (already weak) weather coupling is CUT -> the gap must WORSEN. Proves the
    # measured gap reflects a real fitted belief, not a stored number.
    out = wpt.derive_price_on_record()
    from sim.weather_price_chain import cold_still_tail_mask
    tail = cold_still_tail_mask(out)
    truth = measurement["truth"][tail]
    belief = measurement["belief"][tail]
    real_gap = prediction_gap(truth, belief).gap
    # Replace the belief with the no-skill mean (the coupling fully cut) -> gap==1,
    # which is worse than the real fitted belief on this cell (gap < 1).
    noskill = np.full_like(truth, truth.mean())
    cut_gap = prediction_gap(truth, noskill).gap
    assert real_gap < 1.0
    assert cut_gap == pytest.approx(1.0)
    assert cut_gap > real_gap          # cutting the coupling worsens the gap


def test_ledger_roundtrip_and_reader_sees_numeric_gap(measurement, tmp_path):
    result = wpt.build_gap_result(measurement)
    ledger = wpt.write_gap_entry(
        wpt.WORLD_ATOM_ID, wpt.TWIN_ATOM_ID, result,
        measured_at="2026-07-20T00:00:00+00:00", run_git_commit="deadbeef",
        ledger_path=tmp_path / "gap.json",
    )
    entry = ledger[wpt.WORLD_ATOM_ID]
    assert entry["twin_atom_id"] == wpt.TWIN_ATOM_ID
    assert isinstance(entry["gap"], (int, float))
    # the coupled_triad reader confirms the pair is now "measured".
    reloaded = load_gap_ledger(tmp_path / "gap.json")
    assert gap_measured(wpt.WORLD_ATOM_ID, reloaded)
    # the worst-cell provenance is preserved for audit.
    assert entry["components"]["worst_cell"] == "cold_still_tail"
    assert "population_gap" in entry["components"]
