"""build_atom_hold_reasons: the auditable answer to "why is the loop at rest?"

DIRECTOR_DIRECTIVE_KEEP_BUILDING (2026-07-21). The overnight-rest incident was
NOT a draw bug -- every build-stage atom was correctly held -- but no diagnostic
could SHOW it, so a correct hold read as "drawable work ignored". This classifier
maps every build-stage, level-gap atom to either DRAWABLE (in the draw pool, must
never be left undrawn at rest) or the FIRST gate that removes it.

R15 (a control that can FIRE): the invariant is "no DRAWABLE atom coexists with a
drained loop". test_a_genuinely_drawable_atom_is_visible is the positive control
(a real drawable atom is classified DRAWABLE, so the invariant CAN go red); the
per-gate tests prove each hold reason is reported for its own named defect.
"""
from __future__ import annotations

import pytest

from background import fronts_reconciler
from background import supervisor


@pytest.fixture(autouse=True)
def _isolate_map(tmp_path, monkeypatch):
    monkeypatch.setattr(supervisor, "MATURITY_MAP_PATH", tmp_path / "maturity_map.yaml")
    # Isolate the live fronts-enforcement flag: these unit cases exercise the
    # hold-reason classifier, not front membership, so the global fronts filter
    # must be OFF or a synthetic build atom (in no real open front) is reported
    # off_open_front. See test_fronts_draw_filter.py / test_draw_external_block.py.
    monkeypatch.setattr(
        fronts_reconciler, "FRONTS_ENFORCEMENT_FLAG", tmp_path / ".fronts_enforcement_enabled"
    )
    return tmp_path


_DRAWABLE = (
    "- id: OPEN_BUILD\n  lane: H\n  dial_inherited: 1\n"
    "  level_current: 0\n  level_target: 3\n  loop_stage: build\n"
)
_DIRECTOR_GATED = (
    "- id: GATED_BUILD\n  lane: H\n  dial_inherited: 100\n"
    "  level_current: 2\n  level_target: 3\n  loop_stage: build\n"
    "  blocked_on: director_level_up\n"
)
_DEP = (
    "- id: UPSTREAM\n  lane: H\n  dial_inherited: 1\n"
    "  level_current: 0\n  level_target: 3\n  loop_stage: build\n"
    "- id: DOWNSTREAM\n  lane: H\n  dial_inherited: 1\n"
    "  level_current: 0\n  level_target: 3\n  loop_stage: build\n"
    "  depends_on: [UPSTREAM]\n"
)
# A WORLD atom (W1_ prefix) stepping into L3 with no coupled company twin -- the
# exact shape of the overnight-rest frontier atom (W1_4).
_WORLD_L3 = (
    "- id: W1_synthetic_field\n  lane: W1\n  dial_inherited: 3\n"
    "  level_current: 2\n  level_target: 3\n  loop_stage: build\n"
)


def _reasons(text: str) -> dict:
    supervisor.MATURITY_MAP_PATH.write_text(text)
    return supervisor.build_atom_hold_reasons()


def test_a_genuinely_drawable_atom_is_visible():
    """Positive control (R15): a build-stage, unblocked, deps-met, non-world atom
    is classified DRAWABLE -- so the "no DRAWABLE at rest" invariant CAN fail."""
    assert _reasons(_DRAWABLE) == {"OPEN_BUILD": "DRAWABLE"}


def test_director_gated_atom_is_named_not_reported_drawable():
    r = _reasons(_DIRECTOR_GATED)
    assert r["GATED_BUILD"].startswith("director_gate: blocked_on=director_level_up")
    assert "DRAWABLE" not in r.values()


def test_dependency_blocked_atom_names_its_root():
    r = _reasons(_DEP)
    assert r["UPSTREAM"] == "DRAWABLE"  # the frontier IS buildable
    assert r["DOWNSTREAM"].startswith("blocked_by_dependency")
    assert "UPSTREAM" in r["DOWNSTREAM"]


def test_world_atom_stepping_to_l3_without_a_twin_is_walled_not_drawable():
    """The overnight-rest frontier case: a world atom's L3 step is held by the
    coupled-triad wall, NOT reported as a buildable/drawn atom."""
    r = _reasons(_WORLD_L3)
    assert r["W1_synthetic_field"].startswith("coupled_triad_l3_wall")
    assert "DRAWABLE" not in r.values()


def test_only_gated_atoms_means_no_drawable_and_a_correct_rest():
    """The whole incident in miniature: every build-stage atom is held, so the
    loop is CORRECTLY at rest -- the classifier yields zero DRAWABLE atoms, which
    is the invariant a rested loop must satisfy."""
    r = _reasons(_DIRECTOR_GATED + _WORLD_L3)
    drawable = [aid for aid, reason in r.items() if reason == "DRAWABLE"]
    assert drawable == []


def test_the_held_frontier_surfaces_in_the_blocked_set_diagnosis():
    """diagnose_map_blocked_set now names a deps-met-but-gated frontier atom that
    would otherwise be invisible (neither in `blocked` nor the candidate pool) --
    the observability hole that made the correct hold read as a draw bug."""
    supervisor.MATURITY_MAP_PATH.write_text(_WORLD_L3)
    out = supervisor.diagnose_map_blocked_set()
    assert "held frontier" in out
    assert "W1_synthetic_field" in out
    assert "coupled_triad_l3_wall" in out


# ── Publish-gate scope (R10): DAEMON-LIFECYCLE / pipeline-machinery module.
# Validates the draw diagnostics, never a published business surface -- so it
# must never wedge the live publish. The gate runs `-m 'not operational'`.
pytestmark = pytest.mark.operational
