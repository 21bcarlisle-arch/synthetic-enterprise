"""Tests for the scope-of-need scoring frame (Epoch-2 atom A).

The frame is a CONTROL (the campaign's objective function). Per R15 it must be
able to FIRE on its own named defects -- the killer mutation (14 cells good, 1
blind -> must score ~blind), the middle-only-green pathology, an untested cell
silently exiting the MAX, and a wall-leak gap reading as good. Each mutation
test constructs the exact defect the frame exists to catch and asserts it fires.
"""

from __future__ import annotations

import pytest

from background import scope_of_need_scoring_frame as F


# ── the grid itself ──────────────────────────────────────────────────────────
def test_grid_is_5x3_fifteen_cells():
    ids = F.grid_cell_ids()
    assert len(ids) == 15
    assert len(set(ids)) == 15  # no duplicates
    assert "A2_G3" in ids and "A5_G1" in ids
    # archetype-major ordering
    assert ids[0].startswith("A1") and ids[-1].startswith("A5")


def test_every_named_stressor_has_a_row():
    """The director's five named stressors each map to a row; A5 is the only
    addition (the reference anchor)."""
    blob = " ".join(f"{a.label} {a.stresses}".lower() for a in F.ARCHETYPES)
    for stressor in ("affordab", "shape", "export", "pass-through"):
        assert stressor in blob, f"named stressor {stressor!r} not covered by any archetype"
    ids = {a.id for a in F.ARCHETYPES}
    assert ids == {"A1", "A2", "A3", "A4", "A5"}
    assert sum(a.is_reference for a in F.ARCHETYPES) == 1  # exactly A5 is the anchor
    assert next(a for a in F.ARCHETYPES if a.is_reference).id == "A5"


def test_reference_cell_detection():
    assert F.is_reference_cell("A5_G2")
    assert not F.is_reference_cell("A2_G3")


# ── the worst-cell rule (S3.3) ───────────────────────────────────────────────
def test_all_cells_measured_headline_is_the_worst_cell_not_the_mean():
    gaps = {cid: 0.10 for cid in F.grid_cell_ids()}
    gaps["A2_G3"] = 0.95  # one blind edge
    s = F.score_scope_of_need(gaps)
    assert s.worst_cell == "A2_G3"
    assert s.fidelity_score == pytest.approx(0.95)
    assert s.all_measured and not s.leaks and s.clean


def test_killer_mutation_14_good_1_blind_scores_blind_not_good():
    """THE killer mutation (S3.4): a model near-perfect on 14 cells but blind on
    ONE edge must score ~blind. MUTATION: if fidelity_score were the mean it
    would read ~0.16 (a pass); the worst-cell rule must read 0.95."""
    gaps = {cid: 0.10 for cid in F.grid_cell_ids()}
    gaps["A4_G3"] = 0.95
    s = F.score_scope_of_need(gaps)
    mean = sum(gaps.values()) / len(gaps)
    assert mean < 0.2  # the mean would have passed -- the disease
    assert s.fidelity_score == pytest.approx(0.95)  # the worst-cell rule fires
    assert s.fidelity_score > 4 * mean


def test_middle_only_green_does_not_report_clean():
    """The exact pathology the frame is built to catch: A5 (middle) explained,
    every edge untested. The headline must NOT be clean and the worst cell must
    be an edge, not the comfortable middle."""
    gaps = {cid: 0.08 for cid in F.grid_cell_ids() if F.is_reference_cell(cid)}
    s = F.score_scope_of_need(gaps)
    assert not s.clean
    assert not s.all_measured
    assert not F.is_reference_cell(s.worst_cell)  # an edge is worst, never A5
    assert s.middle_to_edge_spread > 0  # explains-the-middle-not-the-edges, numeric


# ── FAIL-OPEN: an untested cell cannot silently exit the MAX (S3.4) ──────────
def test_untested_cell_scores_at_least_the_worst_measured():
    gaps = {cid: 0.30 for cid in F.grid_cell_ids()}
    del gaps["A3_G3"]  # drop one -> untested
    s = F.score_scope_of_need(gaps)
    assert "A3_G3" in s.untested_cells
    # the untested cell is scored strictly worse than the worst measured (0.30)
    assert s.severities["A3_G3"] >= 0.30
    assert s.worst_cell == "A3_G3"
    assert not s.clean


def test_untested_cell_never_dropped_from_the_grid():
    gaps = {"A5_G1": 0.10}  # only one measured
    s = F.score_scope_of_need(gaps)
    assert len(s.severities) == 15          # all 15 present, none silently dropped
    assert len(s.untested_cells) == 14


# ── TAUTOLOGY / leak guard (S3.4) ────────────────────────────────────────────
def test_gap_zero_is_flagged_as_a_wall_leak_not_celebrated():
    """gap->0 is structurally unreachable through the wall (perfect belief would
    mean the company can see SIM truth). It must flag as a leak and block a clean
    headline, never read as the best possible cell."""
    gaps = {cid: 0.20 for cid in F.grid_cell_ids()}
    gaps["A1_G1"] = 0.0
    s = F.score_scope_of_need(gaps)
    assert "A1_G1" in s.leaks
    assert not s.clean


# ── input hygiene ────────────────────────────────────────────────────────────
def test_unknown_cell_id_raises_not_silently_expands_grid():
    with pytest.raises(ValueError):
        F.score_scope_of_need({"A9_G9": 0.5})


# ── the q values-call: default is pure MAX; smoother available ──────────────
def test_default_q_is_pure_max():
    assert F.WORST_CELL_Q == 0.0
    gaps = {cid: 0.10 for cid in F.grid_cell_ids()}
    gaps["A2_G2"] = 0.9
    gaps["A2_G3"] = 0.8
    s = F.score_scope_of_need(gaps)  # default q=0 -> single worst
    assert s.fidelity_score == pytest.approx(0.9)


def test_cvar_smoother_available_and_averages_the_worst_k():
    """The smoother is AVAILABLE (S3.3) but not the default. At q>0 the headline
    aggregate is the mean of the worst k cells -- still >= a passing mean, and it
    degrades to MAX as q->0."""
    gaps = {cid: 0.10 for cid in F.grid_cell_ids()}
    gaps["A2_G2"] = 0.9
    gaps["A2_G3"] = 0.8
    s = F.score_scope_of_need(gaps, q=0.15)  # ceil(0.15*15)=3 worst cells
    # worst 3 are 0.9, 0.8, 0.10 -> mean 0.60
    assert s.grid_aggregate == pytest.approx((0.9 + 0.8 + 0.10) / 3)
    # worst_cell (the argmax) is still the single worst regardless of q
    assert s.worst_cell == "A2_G2"


def test_equal_cell_weighting_default_is_true():
    assert F.EQUAL_CELL_WEIGHTING is True
