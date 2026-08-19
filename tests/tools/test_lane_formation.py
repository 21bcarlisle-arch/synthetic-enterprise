#!/usr/bin/env python3
"""R15 proof for the lane-formation measure (director ruling, 2026-08-19).

The ruling asked for one thing: make the SHAPE of the draw across lanes visible, so that "a
single lane going deeper and deeper across multiple epochs while the rest stands still" can be
acted on. So the mutations drive the two conditions that describe that failure -- one lane
pooling, and lanes that could be drawn taking nothing -- and both are driven from BOTH sides,
because a slip detector that never says HELD is as useless as one that never says SLIPPED.

The fail-closed direction is toward UNAVAILABLE and is tested three ways. This project has
already shipped a governor that was silent because it never ran; the lesson taken from it is
that silence must never be reachable from a broken source, so every source this reads has a
test proving it RAISES rather than returning a comfortable shape.
"""
from __future__ import annotations

import pytest

from tools import lane_formation as lf


def _atom(aid, lane, stage="build", cur=0, tgt=3, epoch=2):
    return {"id": aid, "lane": lane, "loop_stage": stage,
            "level_current": cur, "level_target": tgt, "epoch": epoch}


def _wire(monkeypatch, atoms, subjects):
    monkeypatch.setattr(lf, "_atoms", lambda: atoms)
    monkeypatch.setattr(lf, "_subjects", lambda window_days=7: subjects)


# ---------------------------------------------------------------------------
# Condition 1: POOLING -- one lane taking the draw
# ---------------------------------------------------------------------------
def test_MUTATION_one_lane_over_the_share_is_a_slip(monkeypatch):
    atoms = [_atom("A1_x", "L_deep"), _atom("B1_y", "L_other")]
    _wire(monkeypatch, atoms, ["A1 work"] * 9 + ["B1 work"])
    s = lf.formation()
    assert s["slipped"] and "POOLING" in s["reasons"][0]
    assert s["top_lane"] == "L_deep" and s["top_share"] == pytest.approx(0.9)


def test_a_balanced_draw_is_NOT_a_slip(monkeypatch):
    """The other side of the boundary. A detector that always fires gets muted, and muting this
    one restores exactly the blindness the ruling was written about."""
    atoms = [_atom("A1_x", "L_one"), _atom("B1_y", "L_two"), _atom("C1_z", "L_three")]
    _wire(monkeypatch, atoms, ["A1 w", "B1 w", "C1 w", "A1 w", "B1 w", "C1 w"])
    s = lf.formation()
    assert not s["slipped"], s["reasons"]


def test_MUTATION_the_pooling_threshold_is_a_real_boundary(monkeypatch):
    """Just under the line holds; just over it slips. Pins the comparison itself, so a `>=`/`>`
    slip or a silently widened constant fails here rather than in six days of quiet."""
    atoms = [_atom("A1_x", "L_a"), _atom("B1_y", "L_b"), _atom("C1_z", "L_c")]
    _wire(monkeypatch, atoms, ["A1 w"] * 4 + ["B1 w"] * 3 + ["C1 w"] * 3)   # top = 40%, not over
    assert not lf.formation()["slipped"]
    _wire(monkeypatch, atoms, ["A1 w"] * 5 + ["B1 w"] * 3 + ["C1 w"] * 2)   # top = 50%, over
    assert lf.formation()["slipped"]


# ---------------------------------------------------------------------------
# Condition 2: STARVATION -- lanes that could be drawn and were not
# ---------------------------------------------------------------------------
def test_MUTATION_enough_starved_lanes_is_a_slip(monkeypatch):
    atoms = [_atom("A1_x", "L_f1"), _atom("A2_x", "L_f2"), _atom("A3_x", "L_f3")] + [
        _atom(f"S{i}_z", f"L_starved{i}") for i in range(1, 4)
    ]
    _wire(monkeypatch, atoms, ["A1 w", "A2 w", "A3 w"] * 2)   # 33% each -- no pooling
    s = lf.formation()
    assert s["slipped"]
    assert s["reasons"] == [r for r in s["reasons"] if "STARVATION" in r], (
        "POOLING also fired -- this fixture no longer isolates starvation"
    )
    assert s["starved_lanes"] == ["L_starved1", "L_starved2", "L_starved3"]


def test_two_starved_lanes_is_noise_not_a_slip(monkeypatch):
    atoms = [_atom("A1_x", "L_f1"), _atom("A2_x", "L_f2"), _atom("A3_x", "L_f3")] + [
        _atom(f"S{i}_z", f"L_starved{i}") for i in (1, 2)
    ]
    _wire(monkeypatch, atoms, ["A1 w", "A2 w", "A3 w"] * 2)
    assert not lf.formation()["slipped"]


def test_MUTATION_a_lane_with_nothing_buildable_is_finished_not_starved(monkeypatch):
    """THE distinction that decides whether this measure survives contact. A lane whose atoms
    are all at target, or all parked, has nothing to draw -- counting it as starved would mean
    the alarm fires forever, gets muted, and the real slip goes unseen. Three such lanes here:
    without this rule they trip STARVED_LANE_COUNT exactly."""
    atoms = [
        _atom("A1_x", "L_f1"), _atom("A2_x", "L_f2"), _atom("A3_x", "L_f3"),
        _atom("D1_a", "L_done", cur=3, tgt=3),          # at target
        _atom("D2_b", "L_parked", stage="idle"),        # parked
        _atom("D3_c", "L_harden", stage="harden"),      # not a BUILD lane right now
    ]
    _wire(monkeypatch, atoms, ["A1 w", "A2 w", "A3 w"] * 2)
    s = lf.formation()
    assert s["starved_lanes"] == []
    assert not s["slipped"], "a finished lane was counted as starved"


# ---------------------------------------------------------------------------
# FAIL-CLOSED: unavailable, never "held"
# ---------------------------------------------------------------------------
def test_MUTATION_FAIL_CLOSED_an_unreadable_map_raises(monkeypatch, tmp_path):
    monkeypatch.setattr(lf, "MAP_PATH", tmp_path / "gone.yaml")
    with pytest.raises(lf.FormationUnavailable):
        lf.formation()


def test_MUTATION_FAIL_CLOSED_a_git_failure_raises(monkeypatch):
    monkeypatch.setattr(lf, "_atoms", lambda: [_atom("A1_x", "L")])

    class _R:
        returncode, stdout, stderr = 128, "", "not a git repository"

    monkeypatch.setattr(lf.subprocess, "run", lambda *a, **k: _R())
    with pytest.raises(lf.FormationUnavailable):
        lf.formation()


def test_MUTATION_FAIL_CLOSED_commits_naming_no_atom_raise_rather_than_reading_healthy(monkeypatch):
    """The subtlest fail-open available here, and the one worth spelling out: if attribution
    breaks, every counter is zero, no lane pools, no lane is over any threshold -- and a naive
    implementation returns a serene HELD. Zero evidence must never render as good news."""
    _wire(monkeypatch, [_atom("A1_x", "L")], ["chore: tidy", "docs: wording", "fix: typo"])
    with pytest.raises(lf.FormationUnavailable):
        lf.formation()


def test_MUTATION_FAIL_CLOSED_an_empty_window_raises(monkeypatch):
    monkeypatch.setattr(lf, "_atoms", lambda: [_atom("A1_x", "L")])

    class _R:
        returncode, stdout, stderr = 0, "", ""

    monkeypatch.setattr(lf.subprocess, "run", lambda *a, **k: _R())
    with pytest.raises(lf.FormationUnavailable):
        lf.formation()


# ---------------------------------------------------------------------------
# Honesty of the reading
# ---------------------------------------------------------------------------
def test_partial_attribution_is_reported_not_hidden(monkeypatch):
    _wire(monkeypatch, [_atom("A1_x", "L")], ["A1 w", "A1 w", "chore: tidy", "docs: x"])
    s = lf.formation()
    assert s["attributed"] == 2 and s["commits"] == 4
    assert s["coverage"] == pytest.approx(0.5)


def test_colliding_prefixes_are_named_so_per_atom_counts_are_not_trusted(monkeypatch):
    """`H27_payment_belief_gap` and `H27_phone_act_channel` both answer to "H27". The lane view
    survives it when both sit in one lane; the per-atom view does not, and says so."""
    _wire(monkeypatch,
          [_atom("H27_payment_belief_gap", "H_harness"),
           _atom("H27_phone_act_channel", "H_harness")],
          ["H27 something"] * 3)
    assert lf.formation()["collided_prefixes"] == ["H27"]


# ---------------------------------------------------------------------------
# R5 -- transition only
# ---------------------------------------------------------------------------
def test_the_alarm_fires_on_transition_only(monkeypatch, tmp_path):
    monkeypatch.setattr(lf, "STATE_FILE", tmp_path / "state.json")
    atoms = [_atom("A1_x", "L_deep"), _atom("B1_y", "L_other")]
    _wire(monkeypatch, atoms, ["A1 w"] * 9 + ["B1 w"])
    first = lf.observe()
    assert first["verdict"] == "SLIPPED" and first["changed"] and "alarm" in first
    second = lf.observe()
    assert second["verdict"] == "SLIPPED" and not second["changed"] and "alarm" not in second


def test_an_unavailable_reading_alarms_rather_than_passing_silently(monkeypatch, tmp_path):
    monkeypatch.setattr(lf, "STATE_FILE", tmp_path / "state.json")
    monkeypatch.setattr(lf, "MAP_PATH", tmp_path / "gone.yaml")
    r = lf.observe()
    assert r["verdict"] == "UNAVAILABLE" and r["changed"]
    assert "FORMATION UNREADABLE" in r["alarm"]


# ---------------------------------------------------------------------------
# The live reading
# ---------------------------------------------------------------------------
def test_the_live_draw_is_measurable_and_its_verdict_is_recorded():
    """Runs against the REAL repo, because a measure that only ever sees fixtures has not been
    shown to survive its own data -- 22 colliding prefixes and 32% attribution are facts this
    found, not conditions it was built for. Deliberately asserts SHAPE rather than a verdict:
    pinning SLIPPED here would make the test go red on the day the formation recovers, which is
    the pinned-literal defect this project keeps finding in its own controls."""
    s = lf.formation()
    assert s["attributed"] > 0 and 0 < s["coverage"] <= 1
    assert abs(sum(s["shares"].values()) - 1.0) < 1e-9
    assert s["top_lane"] in s["lanes"]
    assert isinstance(s["slipped"], bool)
