"""Coupled-triad tests for the W2_4 <-> C6 pair (household budget / affordability).

These test the GAP MEASUREMENT, not the company inference in isolation. The
central R15 concern: the gap must be a real, mutation-sensitive measurement --
it FIRES (rises) when the company's belief degrades, and it can reach 0 only if
the belief equals the truth (so a near-zero reading would be a leak to diagnose,
never a stuck-pass tautology).
"""

from __future__ import annotations

import ast
import inspect
import json

import company.crm.affordability_inference as ai_mod
from company.crm.affordability_inference import (
    AffordabilityBand,
    BAND_ORDER,
    composition_vector,
)
from background.gap_metric import belief_gap

import tools.couple_w2_4_c6 as pair


# Small population keeps the suite fast while staying statistically meaningful.
_N = 1200
_YEAR = 2022


# ---------------------------------------------------------------------------
# Wall: the company side of this pair reads no SIM internals.
# ---------------------------------------------------------------------------

def test_company_twin_respects_wall():
    tree = ast.parse(inspect.getsource(ai_mod))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                assert not a.name.startswith("simulation"), a.name
        elif isinstance(node, ast.ImportFrom) and node.module:
            assert not node.module.startswith("simulation"), node.module


# ---------------------------------------------------------------------------
# The gap is well-formed and non-degenerate.
# ---------------------------------------------------------------------------

def test_gap_is_non_degenerate():
    result, stats = pair.measure(_N, _YEAR)
    # A wall-respecting pair lands strictly inside (0, 1): learned some, not all.
    assert result.gap is not None
    assert 0.0 < result.gap < 1.0, (result.gap, stats)
    # raw TV and the blind-prior TV are both real, positive numbers.
    assert result.components["tv"] > 0.0
    assert result.components["tv_prior"] > 0.0


def test_truth_and_belief_are_valid_distributions():
    truth_dist, belief_dist, _ = pair.build_scenario(_N, _YEAR)
    assert abs(sum(truth_dist.values()) - 1.0) < 1e-9
    assert abs(sum(belief_dist.values()) - 1.0) < 1e-9
    # Both books contain a real cannot-pay minority (not a degenerate all-one-band).
    assert truth_dist[AffordabilityBand.NEGATIVE] > 0.0
    assert 0.0 < truth_dist[AffordabilityBand.COMFORTABLE] < 1.0


def test_deterministic():
    r1, _ = pair.measure(_N, _YEAR)
    r2, _ = pair.measure(_N, _YEAR)
    assert r1.gap == r2.gap
    assert r1.components["tv"] == r2.components["tv"]


# ---------------------------------------------------------------------------
# R15 mutation: the gap must FIRE on a worse belief and reach 0 on a perfect one.
# A control that cannot fail is worse than none (CLAUDE.md R15).
# ---------------------------------------------------------------------------

def test_gap_reaches_zero_only_on_perfect_belief():
    truth_dist, _, _ = pair.build_scenario(_N, _YEAR)
    truth_vec = composition_vector(truth_dist)
    prior_vec = composition_vector(pair._NATIONAL_PRIOR)
    # Belief == truth -> gap exactly 0 (the metric is NOT stuck away from 0).
    perfect = belief_gap(truth_vec, truth_vec, prior=prior_vec)
    assert perfect.gap == 0.0


def test_gap_fires_when_belief_degrades():
    """The real inference must score a LOWER gap than a degenerate belief that
    ignores the observables (always 'managing'). If a worse belief did not raise
    the gap, the gap would be a tautology, not a measurement (R15)."""
    result, _ = pair.measure(_N, _YEAR)
    truth_dist, _, _ = pair.build_scenario(_N, _YEAR)
    truth_vec = composition_vector(truth_dist)
    prior_vec = composition_vector(pair._NATIONAL_PRIOR)

    all_managing = {b: (1.0 if b == AffordabilityBand.MANAGING else 0.0)
                    for b in BAND_ORDER}
    degraded = belief_gap(truth_vec, composition_vector(all_managing), prior=prior_vec)

    assert degraded.gap > result.gap, (degraded.gap, result.gap)


def test_blind_prior_scores_gap_one():
    """By construction the blind national prior scores exactly gap == 1 (it IS
    the g0 baseline). The real inference must beat it."""
    truth_dist, _, _ = pair.build_scenario(_N, _YEAR)
    truth_vec = composition_vector(truth_dist)
    prior_vec = composition_vector(pair._NATIONAL_PRIOR)
    blind = belief_gap(truth_vec, prior_vec, prior=prior_vec)
    assert abs(blind.gap - 1.0) < 1e-9
    result, _ = pair.measure(_N, _YEAR)
    assert result.gap < blind.gap


# ---------------------------------------------------------------------------
# Ledger write matches the coupled_triad.py contract.
# ---------------------------------------------------------------------------

def test_ledger_entry_shape(tmp_path):
    from background.gap_metric import write_gap_entry
    result, _ = pair.measure(_N, _YEAR)
    ledger_path = tmp_path / "gap.json"
    ledger = write_gap_entry(
        pair.WORLD_ATOM_ID, pair.TWIN_ATOM_ID, result,
        measured_at="2026-07-13T00:00:00+00:00", run_git_commit="deadbeef",
        ledger_path=ledger_path,
    )
    entry = ledger[pair.WORLD_ATOM_ID]
    assert entry["twin_atom_id"] == pair.TWIN_ATOM_ID
    assert entry["metric"] == "belief"
    assert isinstance(entry["gap"], float) and 0.0 < entry["gap"] < 1.0
    assert entry["measured_at"] == "2026-07-13T00:00:00+00:00"
    assert entry["run_git_commit"] == "deadbeef"
    # Round-trips as valid JSON.
    reloaded = json.loads(ledger_path.read_text())
    assert reloaded[pair.WORLD_ATOM_ID]["gap"] == entry["gap"]


# ---------------------------------------------------------------------------
# gap_measured() (the coupled_triad reader) accepts our written entry.
# ---------------------------------------------------------------------------

def test_written_entry_satisfies_l3_gate_reader(tmp_path):
    from background.gap_metric import write_gap_entry
    from background.coupled_triad import gap_measured
    result, _ = pair.measure(_N, _YEAR)
    ledger_path = tmp_path / "gap.json"
    ledger = write_gap_entry(
        pair.WORLD_ATOM_ID, pair.TWIN_ATOM_ID, result,
        measured_at="2026-07-13T00:00:00+00:00", run_git_commit="abc123",
        ledger_path=ledger_path,
    )
    # The L3-ceiling gate would now see this pair's gap as MEASURED.
    assert gap_measured(pair.WORLD_ATOM_ID, ledger) is True
