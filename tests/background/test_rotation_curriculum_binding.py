"""The rotation-grid <-> curriculum BINDING (SPINE_1 wiring increment).

WHY THIS EXISTS
---------------
SPINE_1 landed the scenario substrate (`sim/scenario/spine.py` + committed curriculum
artefacts) and the stratified run-rotation landed the grid + cursor + selector. They were
built independently and NOTHING JOINED THEM: the grid named its worlds
``history-default / NESO-central / crisis-replay / glut``; the curriculum named the same
four ``history_replay / neso_central / crisis_2021_22 / supply_glut``. So a rotation cell
could not be resolved to a world at all — `manifest_for_next_run` stamped a ledger row
whose ``world_scenario`` no artefact could answer for, and whose ``true_probability`` no
ratified artefact backed. Every §4 verdict (ROBUSTNESS / COMMERCIAL EV / SURVIVAL) is
computed FROM those rows.

This suite pins the join and both of its fail-closed guards, each mutation-provable (R15).

All curriculum paths are pinned to tmp fixtures except the two tests that deliberately
assert against the REAL committed artefacts (the binding is only useful if it holds on
the real pair of registries) — neither writes to the tree.
"""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

import pytest

from background.run_manifest import MixedBasisError, RunOutcomes, commercial_ev
from background.run_rotation import (
    Cell,
    CurriculumDriftError,
    bind_cell,
    load_grid,
    manifest_for_next_run,
)
from sim.scenario.spine import (
    CURRICULUM_DIR,
    ScenarioArtefactError,
    ScenarioLabelUnbound,
    grid_label_index,
    resolve_grid_label,
)

REPO = Path(__file__).resolve().parents[2]
GRID_PATH = REPO / "docs" / "design" / "run_rotation_grid.json"


def _artefact(dirpath: Path, world_id: str, *, label: str = "", **over) -> Path:
    body = {
        "world_id": world_id,
        "version": "0.0.1-test",
        "provenance": "proposal",
        "ratified": False,
        "in_rotation": False,
        "true_probability": None,
        "paths": {},
    }
    body.update(over)
    lines = [f"{k}: {json.dumps(v)}" for k, v in body.items() if k != "paths"]
    if label:
        lines.append(f"grid_label: {json.dumps(label)}")
    lines.append("paths: {}")
    p = dirpath / f"{world_id}.yaml"
    p.write_text("\n".join(lines) + "\n")
    return p


def _cell(label: str, tp=None) -> Cell:
    return Cell(world_scenario=label, true_probability=tp, population_seed=None)


# --------------------------------------------------------------------------- #
# The join holds on the REAL registries                                       #
# --------------------------------------------------------------------------- #
def test_every_real_grid_label_resolves_to_a_committed_world():
    """The defect this increment fixes: every label the rotation can select must
    resolve to a committed curriculum artefact. FAIL-SILENT guard: asserts the grid
    was non-empty, so a blind/empty read can never pass green."""
    grid = load_grid(GRID_PATH)
    labels = [w for w, _ in grid.worlds]
    assert len(labels) >= 4, f"grid read is blind ({labels}) — treat as FAILED, not green"

    unresolved = []
    for label in labels:
        try:
            resolve_grid_label(label)
        except ScenarioLabelUnbound:
            unresolved.append(label)
    assert unresolved == [], (
        f"rotation grid labels bind to no curriculum artefact: {unresolved} — "
        "a run stamped with these lives through an unidentifiable world"
    )


def test_real_binding_is_one_to_one_and_covers_the_curriculum():
    """No two artefacts claim one label, and the four grid labels map to four
    DISTINCT worlds (a many-to-one binding would silently collapse the rotation)."""
    index = grid_label_index()           # raises on duplicate claims
    grid = load_grid(GRID_PATH)
    labels = [w for w, _ in grid.worlds]
    world_ids = [index[label] for label in labels]
    assert len(set(world_ids)) == len(labels), (
        f"grid labels collapse onto fewer worlds: {dict(zip(labels, world_ids))}"
    )


# --------------------------------------------------------------------------- #
# R15 guard 1 — unbound label fails CLOSED (never falls back to baseline)     #
# --------------------------------------------------------------------------- #
def test_R15_unknown_label_raises_and_does_not_fall_back_to_baseline(tmp_path):
    """KILLER MUTATION: make `resolve_grid_label` return `default_world()` instead of
    raising on an unknown label -> this test goes red.

    A baseline fallback is the fail-silent form of this bug: the run would live through
    real history while its ledger row claimed 'crisis-replay'.
    """
    _artefact(tmp_path, "history_replay", label="history-default",
              provenance="baseline", ratified=True)
    with pytest.raises(ScenarioLabelUnbound) as ei:
        resolve_grid_label("crisis-replay", tmp_path)
    msg = str(ei.value)
    assert "crisis-replay" in msg
    # the refusal must be explicit about NOT defaulting
    assert "baseline" in msg.lower()


def test_R15_unknown_label_check_can_pass_too(tmp_path):
    """Both-ways half: a BOUND label resolves cleanly, so guard 1 is not a
    tautology that rejects everything."""
    _artefact(tmp_path, "crisis_2021_22", label="crisis-replay")
    spine = resolve_grid_label("crisis-replay", tmp_path)
    assert spine.world_id == "crisis_2021_22"


def test_R15_duplicate_label_claim_is_rejected(tmp_path):
    """Two artefacts claiming one label makes 'which world ran?' ambiguous.
    KILLER MUTATION: drop the duplicate check in `grid_label_index` -> red."""
    _artefact(tmp_path, "crisis_2021_22", label="crisis-replay")
    _artefact(tmp_path, "crisis_replay_alt", label="crisis-replay")
    with pytest.raises(ScenarioArtefactError, match="claimed by two"):
        grid_label_index(tmp_path)


# --------------------------------------------------------------------------- #
# R15 guard 2 — true_probability drift between the two director registries    #
# --------------------------------------------------------------------------- #
def test_R15_probability_drift_between_grid_and_artefact_raises(tmp_path):
    """The grid and the curriculum are both director-owned; disagreeing is a defect.
    KILLER MUTATION: make `_reconcile_true_probability` return `grid_tp` unconditionally
    -> this test goes red and a number the director never set reaches COMMERCIAL EV."""
    _artefact(tmp_path, "neso_central", label="NESO-central",
              ratified=True, in_rotation=True, true_probability=0.6,
              ratification={"by": "director", "date": "2026-01-01"})
    with pytest.raises(CurriculumDriftError, match="drift"):
        bind_cell(_cell("NESO-central", tp=0.3), curriculum_dir=tmp_path)


def test_R15_agreeing_probabilities_bind_cleanly(tmp_path):
    """Both-ways half: when the two registries AGREE the weight passes through."""
    _artefact(tmp_path, "neso_central", label="NESO-central",
              ratified=True, in_rotation=True, true_probability=0.6,
              ratification={"by": "director", "date": "2026-01-01"})
    bound = bind_cell(_cell("NESO-central", tp=0.6), curriculum_dir=tmp_path)
    assert bound.true_probability == 0.6
    assert bound.world_id == "neso_central"
    assert bound.rotation_eligible is True


def test_R15_unratified_artefact_may_not_supply_an_ev_weight(tmp_path):
    """R13: an unratified curriculum carrying a probability must not weight EV.
    KILLER MUTATION: delete the `not spine.ratified` branch -> red."""
    _artefact(tmp_path, "supply_glut", label="glut", true_probability=0.4)  # ratified=False
    with pytest.raises(CurriculumDriftError, match="NOT ratified"):
        bind_cell(_cell("glut"), curriculum_dir=tmp_path)


# --------------------------------------------------------------------------- #
# Dormancy — today's real state must be unchanged by this wiring              #
# --------------------------------------------------------------------------- #
def test_real_registries_are_dormant_today_and_ev_still_refuses(tmp_path):
    """Every real world's probability is null right now, so binding yields None and
    COMMERCIAL EV keeps refusing to weight the row (fail-loud). This wiring adds a
    guard; it must not smuggle a weight into a previously-unweighted ledger."""
    grid = load_grid(GRID_PATH)
    for label, _tp in grid.worlds:
        bound = bind_cell(_cell(label))
        assert bound.true_probability is None, (
            f"world {label!r} acquired an EV weight without a director ratification"
        )
        assert bound.rotation_eligible is False, (
            f"world {label!r} is rotation-eligible but no director ratification exists"
        )

    m = manifest_for_next_run(
        RunOutcomes(survived=True, ev_gbp=100.0),
        grid_path=GRID_PATH,
        cursor_path=tmp_path / "cursor.json",
        draw_population_enabled=False,
        code_sha="deadbeef",
    )
    assert m.true_probability is None
    with pytest.raises(MixedBasisError):
        commercial_ev([m.to_row()])


def test_manifest_emission_refuses_an_unresolvable_grid(tmp_path):
    """End-to-end fail-closed: a grid naming a world with no artefact cannot emit a row.
    KILLER MUTATION: remove the `bind_cell` call from `manifest_for_next_run` -> red,
    and unresolvable rows flow into the ledger again."""
    grid_p = tmp_path / "grid.json"
    grid_p.write_text(json.dumps({
        "_meta": {"test": True},
        "world_scenarios": [{"world": "no-such-world", "true_probability": None}],
        "population_seeds": [0],
    }))
    with pytest.raises(ScenarioLabelUnbound):
        manifest_for_next_run(
            RunOutcomes(survived=True, ev_gbp=1.0),
            grid_path=grid_p,
            cursor_path=tmp_path / "cursor.json",
            draw_population_enabled=False,
            code_sha="deadbeef",
        )
