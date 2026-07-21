"""Coupled-triad tests for the segmentation cohort pair
(SEGMENTATION_GENERATOR_BUILD_PLAN.md step 4; `tools/couple_cohort.py`).

Tests the GAP MEASUREMENT mechanism, not the SIM draw or the company twin in
isolation (those have their own unit tests). The central R15 concern: the
worst-cell score must be a real, mutation-sensitive measurement -- it moves
when the company's belief changes, and it is not a tautology (truth and
belief come from independently-authored code paths).
"""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

import tools.couple_cohort as cc
from background.gap_metric import GapResult


_N = 2000


def test_build_scenario_produces_matched_truth_and_belief_lists():
    truths, beliefs = cc.build_scenario(_N)
    assert len(truths) == len(beliefs) == _N
    assert all(t.customer_id == b.customer_id for t, b in zip(truths, beliefs))


def test_build_scenario_is_deterministic():
    t1, b1 = cc.build_scenario(500, base_seed=123)
    t2, b2 = cc.build_scenario(500, base_seed=123)
    assert t1 == t2
    assert b1 == b2


def test_build_scenario_differs_across_seeds():
    t1, _ = cc.build_scenario(200, base_seed=1)
    t2, _ = cc.build_scenario(200, base_seed=2)
    assert t1 != t2


def test_score_worst_cell_returns_expected_shape():
    truths, beliefs = cc.build_scenario(_N)
    worst = cc.score_worst_cell(truths, beliefs)
    assert set(worst) >= {
        "worst_cell_id", "worst_cell_gap", "worst3_mean_gap",
        "n_in_cell", "n_min", "n_cells_eligible", "n_cells_total", "all_cells",
    }
    assert worst["worst_cell_gap"] >= 0.0
    assert worst["n_cells_eligible"] <= worst["n_cells_total"]
    assert worst["n_in_cell"] >= worst["n_min"]


def test_score_worst_cell_raises_when_no_cell_clears_n_min():
    truths, beliefs = cc.build_scenario(10)  # too small for any n_min=30 cell
    with pytest.raises(ValueError):
        cc.score_worst_cell(truths, beliefs, n_min=10_000)


def test_no_discovery_axes_sit_at_or_near_the_blind_baseline():
    """accommodation/cars/nssec have NO discovery mechanism -- their gap must
    be ~1.0 (no better than the blind national prior) for EVERY cell, never
    near 0 (which would mean the harness accidentally leaked truth into the
    belief) and never wildly above 1 (which would mean the belief is a
    degenerate point-mass mismatched against a smooth prior baseline)."""
    truths, beliefs = cc.build_scenario(_N)
    worst = cc.score_worst_cell(truths, beliefs)
    for cell in worst["all_cells"]:
        if cell["axis"] in cc._NO_DISCOVERY_AXES and cell["eligible"]:
            assert cell["gap"] == pytest.approx(1.0, abs=1e-9)


def test_discovered_axes_beat_the_blind_baseline():
    """price_sensitivity/channel_pref DO have a discovery mechanism -- their
    gap must be measurably below the no-discovery axes' ~1.0 ceiling for at
    least one cell (proving real, non-tautological learning happened)."""
    truths, beliefs = cc.build_scenario(_N)
    worst = cc.score_worst_cell(truths, beliefs)
    discovered_gaps = [c["gap"] for c in worst["all_cells"]
                       if c["axis"] in ("price_sensitivity", "channel_pref") and c["eligible"]]
    assert any(g < 0.9 for g in discovered_gaps)


def test_measure_returns_gap_result_matching_score_worst_cell():
    result, worst = cc.measure(_N)
    assert isinstance(result, GapResult)
    assert result.gap == worst["worst_cell_gap"]
    assert result.components["worst_cell_id"] == worst["worst_cell_id"]
    assert result.components["worst3_mean_gap"] == worst["worst3_mean_gap"]


# ---------------------------------------------------------------------------
# R15 mutation sensitivity: degrade the company's belief and confirm the
# worst-cell gap responds (never a stuck value).
# ---------------------------------------------------------------------------

def test_worst_cell_gap_responds_to_a_degraded_belief(monkeypatch):
    """A company discovery function that ALWAYS returns 'low' price_sensitivity
    (ignoring the real churn-estimate signal) must score WORSE (higher gap) on
    that axis than the real, signal-using discovery function -- proving the
    measurement is sensitive to the quality of the belief, not a tautology."""
    truths, real_beliefs = cc.build_scenario(_N)

    from company.analytics import cohort_discovery as cd
    import dataclasses

    degraded_beliefs = [
        dataclasses.replace(b, price_sensitivity="low") for b in real_beliefs
    ]

    real_worst = cc.score_worst_cell(truths, real_beliefs)
    degraded_worst = cc.score_worst_cell(truths, degraded_beliefs)

    def _ps_gaps(worst):
        return {c["tenure_cell"]: c["gap"] for c in worst["all_cells"] if c["axis"] == "price_sensitivity"}

    real_ps = _ps_gaps(real_worst)
    degraded_ps = _ps_gaps(degraded_worst)
    # At least one tenure cell must show the degraded belief scoring worse.
    assert any(degraded_ps[t] > real_ps[t] for t in real_ps)


def test_worst_cell_gap_reaches_near_zero_when_belief_equals_truth():
    """A company that (illegitimately) copied the SIM truth exactly would
    score gap~0 -- confirming 0 is reachable in principle (so the measurement
    is not artificially floored) even though the REAL discovery mechanism
    never does this (that would be a wall leak, per gap_metric.py's own
    documented interpretation)."""
    truths, _ = cc.build_scenario(_N)
    import dataclasses
    from company.analytics.cohort_discovery import BelievedCohort

    leaked_beliefs = [
        BelievedCohort(
            customer_id=t.customer_id, region=t.region, heating_fuel=t.heating_fuel,
            tenure=t.tenure, accommodation=t.accommodation, cars=t.cars, nssec=t.nssec,
            price_sensitivity=t.price_sensitivity, channel_pref=t.channel_pref,
        )
        for t in truths
    ]
    worst = cc.score_worst_cell(truths, leaked_beliefs)
    for cell in worst["all_cells"]:
        if cell["axis"] not in cc._NO_DISCOVERY_AXES and cell["eligible"]:
            assert cell["gap"] == pytest.approx(0.0, abs=1e-9)


# ---------------------------------------------------------------------------
# Ledger write mechanism (tested against a TEMP path -- the live
# docs/observability/coupled_gap_ledger.json is deliberately not written by
# this test suite, see the module's own report note on Proof-door blast
# radius).
# ---------------------------------------------------------------------------

def test_write_gap_entry_mechanism_against_temp_ledger():
    from background.gap_metric import write_gap_entry
    result, worst = cc.measure(500)
    with tempfile.TemporaryDirectory() as d:
        ledger_path = Path(d) / "temp_gap_ledger.json"
        ledger = write_gap_entry(
            cc.WORLD_ATOM_ID, cc.TWIN_ATOM_ID, result,
            measured_at="2026-07-21T00:00:00+00:00", run_git_commit="deadbeef",
            ledger_path=ledger_path,
        )
        assert ledger_path.is_file()
        on_disk = json.loads(ledger_path.read_text())
        assert on_disk[cc.WORLD_ATOM_ID]["gap"] == worst["worst_cell_gap"]
        assert on_disk[cc.WORLD_ATOM_ID]["twin_atom_id"] == cc.TWIN_ATOM_ID
        assert ledger == on_disk
