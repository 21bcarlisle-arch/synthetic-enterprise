"""Coverage-of-worlds + R15 mutation tests for the stratified run-rotation
mechanism (`background/run_rotation.py`), scope item 3 of
PLANNER_MINTED_stratified_run_rotation_mechanism_2026-07-25.

All grid/cursor paths are pinned to tmp fixtures — the real committed cursor is
never touched by the suite (test-isolation: a new draw rung isolates its own
register/cursor path).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from background.run_manifest import MixedBasisError, RunOutcomes, commercial_ev
from background.run_rotation import (
    Cell,
    CoverageError,
    Grid,
    assert_period_covers_all_worlds,
    enumerate_cells,
    load_grid,
    manifest_for_next_run,
    peek_next_cell,
    period_length,
    select_next_cell,
    worlds_visited_in_period,
)

RATIFIED = ["history-default", "NESO-central", "crisis-replay", "glut"]


def _write_grid(tmp: Path, *, worlds=None, true_probs=None, seeds=(0, 1, 2, 3)) -> Path:
    worlds = worlds or RATIFIED
    tps = true_probs if true_probs is not None else [None] * len(worlds)
    grid = {
        "_meta": {"test": True},
        "world_scenarios": [
            {"world": w, "true_probability": tp} for w, tp in zip(worlds, tps)
        ],
        "population_seeds": list(seeds),
    }
    p = tmp / "grid.json"
    p.write_text(json.dumps(grid))
    return p


def _cursor(tmp: Path, index: int = 0) -> Path:
    p = tmp / "cursor.json"
    p.write_text(json.dumps({"index": index}))
    return p


# --------------------------------------------------------------------------- #
# Coverage guarantee (the point of the mechanism)                             #
# --------------------------------------------------------------------------- #
def test_one_period_visits_every_ratified_world_dormant_seed_axis(tmp_path):
    """Dormant seed axis: one period is exactly the four ratified worlds, each once."""
    grid_p = _write_grid(tmp_path)
    cur_p = _cursor(tmp_path)
    grid = load_grid(grid_p)
    assert period_length(grid, draw_population_enabled=False) == 4

    visited = [
        select_next_cell(
            grid_path=grid_p, cursor_path=cur_p, draw_population_enabled=False
        ).world_scenario
        for _ in range(4)
    ]
    assert sorted(visited) == sorted(RATIFIED)          # coverage
    assert len(set(visited)) == 4                        # each exactly once
    # and the REAL selector's period is what the coverage assert accepts
    assert_period_covers_all_worlds(visited, grid)


def test_sweep_helper_covers_and_leaves_cursor_untouched(tmp_path):
    grid_p = _write_grid(tmp_path)
    cur_p = _cursor(tmp_path, index=2)
    grid = load_grid(grid_p)
    visited = worlds_visited_in_period(
        grid_path=grid_p, cursor_path=cur_p, draw_population_enabled=False
    )
    assert_period_covers_all_worlds(visited, grid)       # covers regardless of start
    assert json.loads(cur_p.read_text())["index"] == 2   # cursor NOT advanced


def test_cursor_wraps_and_is_persisted(tmp_path):
    grid_p = _write_grid(tmp_path)
    cur_p = _cursor(tmp_path, index=3)
    select_next_cell(grid_path=grid_p, cursor_path=cur_p, draw_population_enabled=False)
    assert json.loads(cur_p.read_text())["index"] == 0   # wrapped 3 -> 0 (period 4)


# --------------------------------------------------------------------------- #
# Determinism / replay (C-S2)                                                 #
# --------------------------------------------------------------------------- #
def test_peek_is_pure_no_advance(tmp_path):
    grid_p = _write_grid(tmp_path)
    cur_p = _cursor(tmp_path, index=1)
    a = peek_next_cell(grid_path=grid_p, cursor_path=cur_p)
    b = peek_next_cell(grid_path=grid_p, cursor_path=cur_p)
    assert a == b == Cell("NESO-central", None, None)
    assert json.loads(cur_p.read_text())["index"] == 1   # untouched


def test_replay_from_same_cursor_reproduces_cell_order(tmp_path):
    grid_p = _write_grid(tmp_path)
    order1 = [
        select_next_cell(
            grid_path=grid_p, cursor_path=_cursor(tmp_path, 0), draw_population_enabled=False
        ).world_scenario
        for _ in range(1)
    ]
    # fresh cursor at 0 -> identical first cell (pure function of grid+cursor)
    order2 = [
        select_next_cell(
            grid_path=grid_p, cursor_path=_cursor(tmp_path, 0), draw_population_enabled=False
        ).world_scenario
    ]
    assert order1 == order2 == ["history-default"]


# --------------------------------------------------------------------------- #
# Seed axis: dormant vs active                                                #
# --------------------------------------------------------------------------- #
def test_seed_axis_dormant_is_single_noop_cell(tmp_path):
    grid = load_grid(_write_grid(tmp_path))
    cells = enumerate_cells(grid, draw_population_enabled=False)
    assert all(c.population_seed is None for c in cells)
    assert len(cells) == 4


def test_seed_axis_active_expands_grid(tmp_path):
    grid = load_grid(_write_grid(tmp_path, seeds=(0, 1, 2, 3)))
    cells = enumerate_cells(grid, draw_population_enabled=True)
    assert len(cells) == 16                               # 4 worlds x 4 seeds
    # still covers every world within the (longer) period
    assert_period_covers_all_worlds([c.world_scenario for c in cells], grid)


# --------------------------------------------------------------------------- #
# R15 mutation 1 — skipped-cell (the tail-drop defect) must go RED            #
# --------------------------------------------------------------------------- #
def test_R15_skipped_crisis_replay_cell_fails_coverage(tmp_path):
    """A selector that silently drops the crisis-replay tail cell must FAIL the
    coverage check — which is measured against the ENUMERATED grid, not against
    what the cursor visited (independence)."""
    grid = load_grid(_write_grid(tmp_path))
    mutated_visited = [w for w in RATIFIED if w != "crisis-replay"]  # tail dropped
    with pytest.raises(CoverageError) as ei:
        assert_period_covers_all_worlds(mutated_visited, grid)
    assert "crisis-replay" in str(ei.value)


def test_R15_coverage_passes_on_the_real_selector(tmp_path):
    """The both-ways half: the real selector's period DOES cover, so the control
    is not vacuously red."""
    grid_p = _write_grid(tmp_path)
    grid = load_grid(grid_p)
    visited = worlds_visited_in_period(
        grid_path=grid_p, cursor_path=_cursor(tmp_path), draw_population_enabled=False
    )
    assert_period_covers_all_worlds(visited, grid)        # no raise


def test_R15_coverage_independent_of_visit_order_not_self_referential(tmp_path):
    """Independence: coverage compares to the grid oracle, so even a visited list
    that repeats one world and omits another FAILS (a tautology that checked the
    visited-set against itself would pass)."""
    grid = load_grid(_write_grid(tmp_path))
    tautology_bait = ["glut", "glut", "glut", "glut"]     # cursor 'visited' only glut
    with pytest.raises(CoverageError):
        assert_period_covers_all_worlds(tautology_bait, grid)


# --------------------------------------------------------------------------- #
# R15 mutation 2 — untagged-EV: rotation cannot bypass the §4 weight guard    #
# --------------------------------------------------------------------------- #
def test_R15_rotation_emitted_null_true_prob_keeps_commercial_ev_refusing(tmp_path):
    """The grid's true_probability is null (director-reserved, unset). A manifest
    stamped from the rotation therefore carries None, and COMMERCIAL EV must keep
    REFUSING to weight it (fail-loud) — the rotation does not smuggle an
    unweighted row into a weighted score."""
    grid_p = _write_grid(tmp_path)          # all true_probability null
    cur_p = _cursor(tmp_path)
    m = manifest_for_next_run(
        RunOutcomes(survived=True, ev_gbp=100.0),
        grid_path=grid_p,
        cursor_path=cur_p,
        draw_population_enabled=False,
        code_sha="deadbeef",
    )
    assert m.true_probability is None
    assert m.world_scenario == "history-default"          # from the rotation, not hand-set
    with pytest.raises(MixedBasisError):
        commercial_ev([m.to_row()])


def test_R15_rotation_carries_director_set_true_prob_when_present(tmp_path):
    """Both-ways half: when the director HAS set a true_probability in the grid,
    the rotation carries it forward and COMMERCIAL EV weights it (no refusal)."""
    grid_p = _write_grid(
        tmp_path, true_probs=[0.7, 0.1, 0.1, 0.1]         # hypothetical director-set tags
    )
    cur_p = _cursor(tmp_path)
    m = manifest_for_next_run(
        RunOutcomes(survived=True, ev_gbp=100.0),
        grid_path=grid_p,
        cursor_path=cur_p,
        draw_population_enabled=False,
        code_sha="deadbeef",
    )
    assert m.true_probability == 0.7
    score = commercial_ev([m.to_row()])                   # does not raise
    assert score.value == pytest.approx(100.0)


# --------------------------------------------------------------------------- #
# IaC: the committed grid enumerates the four director-named ratified worlds  #
# --------------------------------------------------------------------------- #
def test_committed_grid_matches_ruling_worlds():
    """The real committed grid transcribes exactly the four ruling §2 worlds and
    leaves every true_probability null (R13 director-reserved, unset)."""
    grid = load_grid()                                    # the real docs/design file
    assert grid.ratified_world_set == set(RATIFIED)
    assert all(tp is None for _, tp in grid.worlds)       # no authored probabilities
