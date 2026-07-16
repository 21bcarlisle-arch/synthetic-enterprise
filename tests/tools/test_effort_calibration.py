"""Tests for tools/effort_calibration.py (G5_effort_sizing_discipline,
CALIBRATION half).

Covers: short-code derivation + ambiguity detection, bounded-window commit
parsing (the "which atom does this arrow belong to" problem when several
transitions are bundled in one commit subject, a real pattern in this repo's
history), duration computation (first-transition-has-no-anchor, non-positive
gaps dropped), the per-lane / per-size distribution builders (including the
size field's honest "not populated yet" degrade), and one end-to-end test
against a real temp git repo built to mimic this project's own
"<id> -> L<n>" commit-subject convention.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest
import yaml

from tools.effort_calibration import (
    LevelTransition,
    build_report,
    build_short_code_index,
    calibration_by_lane,
    calibration_by_size,
    compute_durations,
    git_log_transitions,
    load_atom_registry,
    parse_transitions_from_message,
    _distribution,
)


# ---------------------------------------------------------------------------
# Short-code derivation + ambiguity
# ---------------------------------------------------------------------------
def test_short_code_index_derives_expected_codes():
    index = build_short_code_index(
        [
            "H10_worktree_isolation",
            "W2_10_dd_attribution_confound",
            "F6_bill_integrity_structural",
            "A6_coupled_triad_gap_metric",
            "G5_effort_sizing_discipline",
        ]
    )
    assert index["H10"] == ["H10_worktree_isolation"]
    assert index["W2_10"] == ["W2_10_dd_attribution_confound"]
    assert index["F6"] == ["F6_bill_integrity_structural"]
    assert index["A6"] == ["A6_coupled_triad_gap_metric"]
    assert index["G5"] == ["G5_effort_sizing_discipline"]


def test_short_code_index_flags_real_ambiguity():
    # Real collision observed in this repo's actual map: two atoms share "F5".
    index = build_short_code_index(
        ["F5_ofgem_licence_readiness", "F5_vat_control_independent_signal"]
    )
    assert index["F5"] == [
        "F5_ofgem_licence_readiness",
        "F5_vat_control_independent_signal",
    ]
    assert len(index["F5"]) > 1  # caller is expected to exclude this code


# ---------------------------------------------------------------------------
# Commit-subject parsing (pure function, no git needed)
# ---------------------------------------------------------------------------
def test_parse_single_transition_simple_arrow():
    result = parse_transitions_from_message("H10 -> L3 (worktree scope guard)", ["H10"])
    assert result == [("H10", 3)]


def test_parse_does_not_confuse_h1_with_h10():
    # "H1" must not falsely match inside "H10 -> L3"
    result = parse_transitions_from_message("H10 -> L3", ["H1", "H10"])
    assert result == [("H10", 3)]


def test_parse_handles_prose_between_code_and_arrow():
    result = parse_transitions_from_message(
        "W2_10 DD-attribution-confound -> L2 (L3 gated on C12)", ["W2_10", "C12"]
    )
    assert ("W2_10", 2) in result


def test_parse_handles_embedded_from_level():
    # "Record H14 judge-validation L0->L2" -- the L0 before the arrow is the
    # FROM level and must not be mistaken for the atom's target.
    result = parse_transitions_from_message(
        "Record H14 judge-validation L0->L2 (closes H12 LLM-judge residual)",
        ["H14", "H12"],
    )
    assert ("H14", 2) in result
    # H12 is mentioned but has no arrow attached to it in this subject.
    assert all(code != "H12" for code, _ in result)


def test_parse_bundled_multi_atom_commit_attributes_correctly():
    # A real subject pattern from this repo's history: four atoms, two
    # arrows visually adjacent to each pair -- each atom must get ITS OWN
    # target level, not its neighbour's.
    msg = "C9->L3+W2_7->L3, C10->L3+W2_8->L3: final affordability pairs closed (7/7)"
    result = parse_transitions_from_message(msg, ["C9", "W2_7", "C10", "W2_8"])
    assert set(result) == {("C9", 3), ("W2_7", 3), ("C10", 3), ("W2_8", 3)}


def test_parse_ignores_atom_mentioned_without_arrow():
    result = parse_transitions_from_message(
        "wave-1 integration: A6/H12 L3-progress (no arrow here)", ["A6", "H12"]
    )
    assert result == []


# ---------------------------------------------------------------------------
# Duration computation
# ---------------------------------------------------------------------------
def _t(atom_id, lane, to_level, sha, ts):
    return LevelTransition(
        atom_id=atom_id, lane=lane, size=None, to_level=to_level,
        commit_sha=sha, timestamp=ts, message="",
    )


def test_compute_durations_basic_two_transitions():
    transitions = [
        _t("X1_atom", "H_harness", 1, "sha1", 1000),
        _t("X1_atom", "H_harness", 2, "sha2", 1000 + 3600 * 5),  # 5h later
    ]
    durations = compute_durations(transitions)
    assert len(durations) == 1
    assert durations[0]["hours"] == pytest.approx(5.0, abs=0.01)
    assert durations[0]["from_level"] == 1
    assert durations[0]["to_level"] == 2
    assert durations[0]["lane"] == "H_harness"


def test_compute_durations_first_transition_has_no_anchor():
    # A single recorded transition for an atom yields zero durations -- no
    # start time is guessed.
    transitions = [_t("X2_atom", "H_harness", 1, "sha1", 1000)]
    assert compute_durations(transitions) == []


def test_compute_durations_drops_non_positive_gaps():
    # Two "transitions" landing in the same commit (or an out-of-order/
    # backdated commit) must not produce a zero/negative duration.
    transitions = [
        _t("X3_atom", "H_harness", 1, "sha1", 2000),
        _t("X3_atom", "H_harness", 2, "sha2", 2000),  # same timestamp
    ]
    assert compute_durations(transitions) == []


def test_compute_durations_out_of_order_input_is_sorted():
    transitions = [
        _t("X4_atom", "C_customer_ops", 2, "sha_later", 5000),
        _t("X4_atom", "C_customer_ops", 1, "sha_earlier", 1000),
    ]
    durations = compute_durations(transitions)
    assert len(durations) == 1
    assert durations[0]["hours"] == pytest.approx((5000 - 1000) / 3600.0, abs=0.01)


# ---------------------------------------------------------------------------
# Distribution / lane / size aggregation
# ---------------------------------------------------------------------------
def test_distribution_empty():
    assert _distribution([]) == {"n": 0}


def test_distribution_single_value_has_no_stdev():
    d = _distribution([4.0])
    assert d["n"] == 1
    assert d["mean_hours"] == 4.0
    assert "stdev_hours" not in d


def test_distribution_multi_value_stats():
    d = _distribution([1.0, 2.0, 3.0])
    assert d["n"] == 3
    assert d["mean_hours"] == pytest.approx(2.0)
    assert d["median_hours"] == pytest.approx(2.0)
    assert d["min_hours"] == pytest.approx(1.0)
    assert d["max_hours"] == pytest.approx(3.0)
    assert "stdev_hours" in d


def test_calibration_by_lane_groups_by_lane():
    durations = [
        {"lane": "H_harness", "hours": 2.0, "size": None},
        {"lane": "H_harness", "hours": 4.0, "size": None},
        {"lane": "C_customer_ops", "hours": 1.0, "size": None},
        {"lane": None, "hours": 9.0, "size": None},
    ]
    by_lane = calibration_by_lane(durations)
    assert by_lane["H_harness"]["n"] == 2
    assert by_lane["C_customer_ops"]["n"] == 1
    assert by_lane["unknown_lane"]["n"] == 1


def test_calibration_by_size_reports_no_data_yet_when_unset():
    durations = [{"lane": "H_harness", "hours": 2.0, "size": None}]
    result = calibration_by_size(durations)
    assert result == {"status": "no_size_data_yet", "bands": {}}


def test_calibration_by_size_activates_once_populated():
    durations = [
        {"lane": "H_harness", "hours": 2.0, "size": "M"},
        {"lane": "H_harness", "hours": 30.0, "size": "L"},
        {"lane": "C_customer_ops", "hours": 1.0, "size": "M"},
    ]
    result = calibration_by_size(durations)
    assert result["status"] == "ok"
    assert result["bands"]["M"]["n"] == 2
    assert result["bands"]["L"]["n"] == 1


# ---------------------------------------------------------------------------
# Registry loader (read-only against the real map)
# ---------------------------------------------------------------------------
def test_load_atom_registry_reads_real_map_without_mutating():
    from tools.effort_calibration import MATURITY_MAP_YAML

    before = MATURITY_MAP_YAML.read_text()
    registry = load_atom_registry(MATURITY_MAP_YAML)
    after = MATURITY_MAP_YAML.read_text()
    assert before == after  # never mutated
    assert "G5_effort_sizing_discipline" in registry
    assert registry["G5_effort_sizing_discipline"]["lane"] == "H_harness"
    # No atom carries a size field yet (2026-07-16) -- honest baseline.
    assert registry["G5_effort_sizing_discipline"]["size"] is None


# ---------------------------------------------------------------------------
# End-to-end against a synthetic git repo (deterministic, mimics this
# project's own commit-subject convention without depending on real history
# continuing to look any particular way).
# ---------------------------------------------------------------------------
def _run_git(args, cwd):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


def _commit(cwd, message, timestamp, map_path=None, atom_id=None, level=None):
    """Commit `message` at `timestamp`. If `map_path`/`atom_id`/`level` are
    given, actually bump that atom's `level_current` in the map first and
    stage it -- `git log -- <path>` (what the tool under test uses) only
    shows commits that TOUCH the path, matching this repo's real convention
    where every transition commit edits maturity_map.yaml."""
    if map_path is not None:
        atoms = yaml.safe_load(map_path.read_text())
        for atom in atoms:
            if atom["id"] == atom_id:
                atom["level_current"] = level
        map_path.write_text(yaml.safe_dump(atoms, sort_keys=False))
        _run_git(["add", "docs/design/maturity_map.yaml"], cwd)

    env_ts = f"@{timestamp} +0000"
    subprocess.run(
        ["git", "commit", "--allow-empty", "-m", message],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
        env={
            **__import__("os").environ,
            "GIT_AUTHOR_DATE": env_ts,
            "GIT_COMMITTER_DATE": env_ts,
        },
    )


@pytest.fixture
def synthetic_repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _run_git(["init", "-q"], repo)
    _run_git(["config", "user.email", "test@example.com"], repo)
    _run_git(["config", "user.name", "Test"], repo)

    design_dir = repo / "docs" / "design"
    design_dir.mkdir(parents=True)
    map_path = design_dir / "maturity_map.yaml"
    atoms = [
        {"id": "Z1_synthetic_alpha", "lane": "H_harness", "level_current": 0},
        {"id": "Z2_synthetic_beta", "lane": "C_customer_ops", "level_current": 0},
    ]
    map_path.write_text(yaml.safe_dump(atoms, sort_keys=False))
    _run_git(["add", "docs/design/maturity_map.yaml"], repo)
    _commit(repo, "seed map with Z1/Z2 at L0", 1_000_000)

    # Z1: L0 -> L1 (registered) then L1 -> L2, 10 hours later.
    _commit(repo, "Z1 -> L1 (first cut)", 1_000_000 + 3600 * 1, map_path, "Z1_synthetic_alpha", 1)
    _commit(repo, "Z1 -> L2 (hardened)", 1_000_000 + 3600 * 11, map_path, "Z1_synthetic_alpha", 2)
    # Z2: single transition only -- must yield zero durations.
    _commit(repo, "Z2 -> L1 (first cut)", 1_000_000 + 3600 * 2, map_path, "Z2_synthetic_beta", 1)
    return repo, map_path


def test_git_log_transitions_end_to_end(synthetic_repo):
    repo, map_path = synthetic_repo
    transitions = git_log_transitions(map_path=map_path, repo_root=repo)
    by_atom = {}
    for t in transitions:
        by_atom.setdefault(t.atom_id, []).append(t.to_level)
    assert sorted(by_atom["Z1_synthetic_alpha"]) == [1, 2]
    assert by_atom["Z2_synthetic_beta"] == [1]


def test_build_report_end_to_end_computes_real_duration(synthetic_repo):
    repo, map_path = synthetic_repo
    report = build_report(repo_root=repo, map_path=map_path)
    assert report["n_durations_computed"] == 1  # only Z1 has 2 transitions
    assert "H_harness" in report["by_lane"]
    assert report["by_lane"]["H_harness"]["n"] == 1
    assert report["by_lane"]["H_harness"]["mean_hours"] == pytest.approx(10.0, abs=0.05)
    assert report["by_size"] == {"status": "no_size_data_yet", "bands": {}}
    assert "DIAL not a WALL" in report["guardrail"]


# ---------------------------------------------------------------------------
# Sanity check against the REAL repo (this project's own git history) -- the
# evidence cited for the L1 bump. Skipped gracefully if git is unavailable.
# ---------------------------------------------------------------------------
def test_build_report_against_real_repo_produces_nonempty_lane_distribution():
    report = build_report()
    assert report["n_transitions_parsed"] > 0
    assert report["n_durations_computed"] > 0
    assert any(dist.get("n", 0) > 0 for dist in report["by_lane"].values())
