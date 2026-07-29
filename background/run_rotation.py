"""STRATIFIED RUN-ROTATION MECHANISM (§2 of the population-activation ruling).

Builds `PLANNER_MINTED_stratified_run_rotation_mechanism_2026-07-25` scope items
2 (wire the selector into manifest emission) and 3 (coverage-of-worlds R15
test), on the FRAME `docs/design/frame/stratified_run_rotation_FRAME.md`.

WHY THIS EXISTS (director §2, verbatim)
---------------------------------------
"Runs rotate a stratified grid: world scenario x population seed. Coverage of
the ratified worlds (history-default, NESO-central, crisis-replay, glut) is
guaranteed rather than hoped for, and runs stay comparable. Randomness lives
inside a cell (which households, which weather path), never in the choice of
cell."

The run manifest/ledger and the three scores (`run_manifest.py`, §3/§4) are
BUILT but nothing governed WHICH cell filled them — the manifest fields were
optional and hand-set. Random or ad-hoc cell choice leaves the tail
under-sampled and the §4 verdicts un-computable. This module is the missing
governor: a deterministic stratified sweep with an IaC-committed cursor.

GUARANTEES
----------
- DETERMINISTIC & REPLAYABLE (C-S2): given the cursor state committed in the
  tree, the next cell is a PURE function of (grid, cursor). No wall-clock, no
  RNG in the CHOICE of cell. Re-running from a cursor reproduces the cell order.
- IaC (OPERATIONAL_LAYER): the grid and the cursor are the ONLY rotation state
  and both live in the readable repo. Reconstruct-from-repo-alone holds.
- COVERAGE GUARANTEE: one full grid period visits every ratified world exactly
  once (checked against the ENUMERATED grid, not against whatever the cursor
  happened to visit — the independence the R15 skipped-cell mutation pins).

WALLS UNTOUCHED (director-reserved)
-----------------------------------
- Scenario VALUES + true-probability TAGS are R13 director-reserved. This module
  transcribes the four world LABELS from the ruling and carries whatever
  `true_probability` the grid file holds (null until the director sets it); it
  NEVER authors a scenario or a probability. A null tag flows straight through
  and COMMERCIAL EV refuses to weight it (fail-loud) — the R15 untagged-EV pin.
- SE_DRAW_POPULATION activation: the population-seed axis is DORMANT. Until the
  caller passes `draw_population_enabled=True` (the flag flip is the
  director-reserved release rung), the seed axis is a single no-op cell
  (population_seed=None) and only the world axis rotates. Honest partial
  coverage, never a silent gap.
- No run entrypoint is wired here and SE_DRAW_POPULATION is not flipped — those
  are the activation core (director-reserved §1). This module provides the
  rotation->manifest SEAM (`manifest_for_next_run`); wiring it into a live run
  is activation, not this build.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from background.run_manifest import RunManifest, RunOutcomes, build_manifest

_REPO_ROOT = Path(__file__).resolve().parents[1]
GRID_PATH = _REPO_ROOT / "docs" / "design" / "run_rotation_grid.json"
CURSOR_PATH = _REPO_ROOT / "docs" / "observability" / "run_rotation_cursor.json"


class CoverageError(AssertionError):
    """Raised when a rotation period fails to cover every ratified world (R15)."""


# --------------------------------------------------------------------------- #
# The grid (director-named worlds; R13 values carried, never authored)        #
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Cell:
    """One (world_scenario, population_seed) cell of the stratified grid.

    `true_probability` is carried from the grid file as DATA (null unless the
    director has set it). Randomness lives INSIDE the cell (households, weather
    path via the C-S2 named substream); it never chooses the cell.
    """

    world_scenario: str
    true_probability: Optional[float]
    population_seed: Optional[int]


@dataclass(frozen=True)
class Grid:
    """The enumerated grid — the independent oracle for coverage checks."""

    worlds: List[Tuple[str, Optional[float]]]   # (world_label, true_probability)
    population_seeds: List[int]

    @property
    def ratified_world_set(self) -> set:
        """The director-named world labels — coverage is checked against THIS,
        not against whatever the cursor visited (R15 independence)."""
        return {w for w, _ in self.worlds}


def load_grid(grid_path: Optional[Path] = None) -> Grid:
    path = Path(grid_path) if grid_path is not None else GRID_PATH
    data = json.loads(path.read_text())
    worlds = [(w["world"], w.get("true_probability")) for w in data["world_scenarios"]]
    if not worlds:
        raise CoverageError("run-rotation grid enumerates zero worlds (fail-closed)")
    seeds = list(data.get("population_seeds", []))
    return Grid(worlds=worlds, population_seeds=seeds)


def enumerate_cells(grid: Grid, *, draw_population_enabled: bool) -> List[Cell]:
    """The flattened, ordered cell list — the fixed round-robin the cursor sweeps.

    Order is (for each world in ruling order, for each seed): stable and
    deterministic, so the cursor index means the same cell on every replay.

    While `draw_population_enabled` is False the seed axis is a SINGLE no-op cell
    (population_seed=None) — the dormant honest-partial-coverage state. One full
    period is then exactly the four ratified worlds.
    """
    seeds: List[Optional[int]] = (
        list(grid.population_seeds) if draw_population_enabled else [None]
    )
    if draw_population_enabled and not seeds:
        raise CoverageError(
            "draw_population_enabled but grid enumerates zero population seeds"
        )
    return [
        Cell(world_scenario=world, true_probability=tp, population_seed=seed)
        for world, tp in grid.worlds
        for seed in seeds
    ]


def period_length(grid: Grid, *, draw_population_enabled: bool) -> int:
    """Cells in one full grid period (after which coverage is guaranteed)."""
    return len(enumerate_cells(grid, draw_population_enabled=draw_population_enabled))


# --------------------------------------------------------------------------- #
# The IaC-committed cursor + the deterministic next-cell selector             #
# --------------------------------------------------------------------------- #
def _read_index(cursor_path: Path) -> int:
    try:
        return int(json.loads(cursor_path.read_text()).get("index", 0))
    except FileNotFoundError:
        return 0


def _write_index(cursor_path: Path, index: int) -> None:
    cursor_path.parent.mkdir(parents=True, exist_ok=True)
    cursor_path.write_text(
        json.dumps(
            {
                "_meta": "IaC-committed run-rotation cursor. The ONLY rotation "
                "state; committed in the readable tree so the next cell is a "
                "pure function of the repo (C-S2 replay). Advanced one cell per "
                "run by background/run_rotation.py::select_next_cell. Do not "
                "hand-edit while a run is in flight.",
                "index": int(index),
            },
            indent=2,
        )
        + "\n"
    )


def peek_next_cell(
    *,
    grid_path: Optional[Path] = None,
    cursor_path: Optional[Path] = None,
    draw_population_enabled: bool = False,
) -> Cell:
    """The cell the next run WOULD get, without advancing the cursor.

    PURE function of (grid, cursor) — no side effects, no wall-clock, no RNG
    (C-S2 determinism). Two peeks from the same cursor return the same cell.
    """
    grid = load_grid(grid_path)
    cells = enumerate_cells(grid, draw_population_enabled=draw_population_enabled)
    idx = _read_index(Path(cursor_path) if cursor_path is not None else CURSOR_PATH)
    return cells[idx % len(cells)]


def select_next_cell(
    *,
    grid_path: Optional[Path] = None,
    cursor_path: Optional[Path] = None,
    draw_population_enabled: bool = False,
    persist: bool = True,
) -> Cell:
    """Return the current cell and ADVANCE the committed cursor by one.

    The choice is deterministic; only the cursor advance is a side effect. With
    `persist=False` the cursor file is not written (used by the coverage sweep
    and by tests). The advance wraps modulo the period so coverage of every
    ratified world is guaranteed within one period.
    """
    grid = load_grid(grid_path)
    cells = enumerate_cells(grid, draw_population_enabled=draw_population_enabled)
    cpath = Path(cursor_path) if cursor_path is not None else CURSOR_PATH
    idx = _read_index(cpath)
    cell = cells[idx % len(cells)]
    if persist:
        _write_index(cpath, (idx + 1) % len(cells))
    return cell


# --------------------------------------------------------------------------- #
# Coverage of the ratified worlds (R15 item 3)                                #
# --------------------------------------------------------------------------- #
def worlds_visited_in_period(
    *,
    grid_path: Optional[Path] = None,
    cursor_path: Optional[Path] = None,
    draw_population_enabled: bool = False,
) -> List[str]:
    """Sweep the REAL selector for one full period from the current cursor and
    return the world labels it visits (cursor unchanged: persist=False)."""
    grid = load_grid(grid_path)
    n = period_length(grid, draw_population_enabled=draw_population_enabled)
    # Sweep from a throwaway in-memory index so the committed cursor is untouched.
    cells = enumerate_cells(grid, draw_population_enabled=draw_population_enabled)
    start = _read_index(Path(cursor_path) if cursor_path is not None else CURSOR_PATH)
    return [cells[(start + i) % len(cells)].world_scenario for i in range(n)]


def assert_period_covers_all_worlds(
    visited_worlds: List[str], grid: Grid
) -> None:
    """R15 control (skipped-cell mutation): every ratified world MUST appear in
    one period. Checked against the ENUMERATED grid (the independent oracle),
    not against whatever the cursor happened to visit — a FAIL-OPEN selector
    that silently drops the crisis-replay tail is exactly the defect §4 exists
    to prevent, so it must go RED here.
    """
    missing = grid.ratified_world_set - set(visited_worlds)
    if missing:
        raise CoverageError(
            f"run-rotation period does not cover every ratified world; missing "
            f"{sorted(missing)} (visited {sorted(set(visited_worlds))}). A "
            "selector that skips a world under-samples the tail and leaves the "
            "§4 verdicts un-computable (R15, §5.1)."
        )


# --------------------------------------------------------------------------- #
# The rotation -> manifest emission SEAM (item 2)                             #
# --------------------------------------------------------------------------- #
def manifest_for_next_run(
    outcomes: RunOutcomes,
    *,
    grid_path: Optional[Path] = None,
    cursor_path: Optional[Path] = None,
    draw_population_enabled: bool = False,
    persist_cursor: bool = True,
    code_sha: Optional[str] = None,
    curriculum_version: Optional[str] = None,
    generated_at: Optional[str] = None,
) -> RunManifest:
    """Select the next cell from the cursor and stamp a §3 ledger manifest from
    it — the wiring the FRAME item 2 names.

    Each row now carries its `world_scenario` and `true_probability` tag FROM
    THE ROTATION rather than a hand-set constant, feeding forward exactly the
    tag the §4 `commercial_ev` guard requires. When the grid's `true_probability`
    is null (director-reserved, unset), the row carries None and COMMERCIAL EV
    refuses to weight it — the rotation cannot bypass the R15 guard.

    This is the SEAM only: it does not run the sim, flip SE_DRAW_POPULATION, or
    wire a live entrypoint (those are the director-reserved activation core).
    """
    cell = select_next_cell(
        grid_path=grid_path,
        cursor_path=cursor_path,
        draw_population_enabled=draw_population_enabled,
        persist=persist_cursor,
    )
    return build_manifest(
        cell.world_scenario,
        outcomes,
        true_probability=cell.true_probability,
        population_seed=cell.population_seed,
        draw_population_enabled=draw_population_enabled,
        code_sha=code_sha,
        curriculum_version=curriculum_version,
        generated_at=generated_at,
    )
