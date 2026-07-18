"""R15 mutation test for H23_frame_saturation_draw_marker.

The DIAL defect (observed, R9 -- H23's own history, occurrences 1-5 in one
day): background/supervisor.py's idle DISCOVER/FRAME self-refill re-drew the
SAME set of FRAME-saturated, BUILD-gated atoms over and over, producing zero
new FRAME-stage work each time (each re-hand is churn SELF_INTERRUPT_DISCIPLINE
+ R12 forbid). An idle atom is FRAME-saturated when it already carries its own
complete FRAME doc: the only remaining path to target is BUILT code the epoch
gate defers, so no honest FRAME output remains.

Per R15 (a control that cannot fail is worse than none) this exercises BOTH
directions plus the all-saturated case -- the exact DoD in
docs/design/frame/H23_frame_saturation_draw_marker_FRAME.md §4:

  FIRES  -- given un-saturated + saturated idle atoms, the draw hands ONLY the
            un-saturated one; the saturated pair is never re-handed.
  QUIET  -- a saturated atom whose BUILD-gate has re-opened (loop_stage flips
            off `idle`, or the explicit `frame_saturated: false` R11 escape)
            re-enters the draw -- the guard must not permanently starve a
            legitimately-ready atom (fail-open on the wrong side = a stuck
            atom, the very idle-hole this subsystem exists to prevent).
  ALL    -- every idle atom saturated + gates closed -> the draw returns
            empty (a TRUE empty FRAME feasible set, Rule 0), NOT a re-hand.

Both draw entry points are covered: `_idle_discover_frame_draw` (single) and
`_idle_discover_frame_draw_concurrent` (the production path via
`_self_refill_draw`).
"""
import random

import pytest

from background import supervisor


@pytest.fixture(autouse=True)
def _isolate_map_and_root(tmp_path, monkeypatch):
    """Isolate BOTH the map path and the repo-root anchor: `_atom_has_frame_doc`
    resolves `evidence` FRAME paths against `PROJECT_DIR`, so the test creates
    real files under a tmp PROJECT_DIR (R7: the guard checks real disk state,
    so the test must too -- no mocked existence)."""
    monkeypatch.setattr(supervisor, "MATURITY_MAP_PATH", tmp_path / "maturity_map.yaml")
    monkeypatch.setattr(supervisor, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(supervisor, "ATOM_STALL_STATE_FILE", tmp_path / ".atom_stall_tracker.json")
    monkeypatch.setattr(supervisor, "log", lambda msg: None)
    (tmp_path / "docs" / "design" / "frame").mkdir(parents=True)
    return tmp_path


def _write_frame_doc(root, atom_id):
    """Create a real per-atom FRAME doc on disk and return its repo-relative
    evidence path (the `<id>_FRAME.md` convention the guard keys on)."""
    rel = f"docs/design/frame/{atom_id}_FRAME.md"
    (root / rel).write_text(f"# FRAME -- {atom_id}\n")
    return rel


def _idle_atom(atom_id, *, frame_saturated=None, evidence=None, level=0, target=2):
    a = {
        "id": atom_id,
        "lane": "H_harness",
        "level_current": level,
        "level_target": target,
        "loop_stage": "idle",
        "dial_inherited": 2,
        "evidence": list(evidence or []),
    }
    if frame_saturated is not None:
        a["frame_saturated"] = frame_saturated
    return a


def _write_map(root, atoms):
    import yaml

    (root / "maturity_map.yaml").write_text(yaml.safe_dump(atoms))


# ── _atom_has_frame_doc / _is_frame_saturated (unit) ──────────────────────────


def test_has_frame_doc_true_when_own_frame_doc_exists(_isolate_map_and_root):
    root = _isolate_map_and_root
    rel = _write_frame_doc(root, "H18_harness_self_mutation_audit")
    atom = _idle_atom("H18_harness_self_mutation_audit", evidence=[rel])
    assert supervisor._atom_has_frame_doc(atom) is True
    assert supervisor._is_frame_saturated(atom) is True


def test_has_frame_doc_false_when_evidence_path_absent_on_disk(_isolate_map_and_root):
    # Evidence LISTS a FRAME doc, but no such file exists -> not saturated
    # (the guard verifies disk state, never a bare string match).
    atom = _idle_atom("B4_x", evidence=["docs/design/frame/B4_x_FRAME.md"])
    assert supervisor._atom_has_frame_doc(atom) is False
    assert supervisor._is_frame_saturated(atom) is False


def test_shared_survey_evidence_is_not_a_frame_doc(_isolate_map_and_root):
    # A shared SURVEY listed as evidence (no `FRAME` in its filename) is NOT
    # the atom's own FRAME-stage output -> the atom still has FRAME work left.
    root = _isolate_map_and_root
    rel = "docs/design/frame/LANE3_H17_BUILD_GATE_SURVEY_20260716.md"
    (root / rel).write_text("# survey\n")
    atom = _idle_atom("B5_x", evidence=[rel])
    assert supervisor._atom_has_frame_doc(atom) is False
    assert supervisor._is_frame_saturated(atom) is False


def test_explicit_marker_overrides_intrinsic_both_ways(_isolate_map_and_root):
    root = _isolate_map_and_root
    rel = _write_frame_doc(root, "W1_2")
    # frame doc exists (intrinsically saturated) but explicit false -> offered
    force_offer = _idle_atom("W1_2", frame_saturated=False, evidence=[rel])
    assert supervisor._is_frame_saturated(force_offer) is False
    # no frame doc (intrinsically un-saturated) but explicit true -> skipped
    force_skip = _idle_atom("W1_x", frame_saturated=True, evidence=[])
    assert supervisor._is_frame_saturated(force_skip) is True


# ── FIRES: saturated atoms are skipped, un-saturated is handed ────────────────


@pytest.mark.parametrize("draw", ["single", "concurrent"])
def test_fires_hands_only_the_unsaturated_atom(_isolate_map_and_root, draw):
    root = _isolate_map_and_root
    ev_a = _write_frame_doc(root, "SAT_A")
    ev_b = _write_frame_doc(root, "SAT_B")
    atoms = [
        _idle_atom("SAT_A", evidence=[ev_a]),          # saturated
        _idle_atom("SAT_B", evidence=[ev_b]),          # saturated
        _idle_atom("FRESH", evidence=[]),              # un-saturated: real FRAME work
    ]
    _write_map(root, atoms)
    rng = random.Random(1234)
    # Draw many times: the saturated pair must NEVER be handed while FRESH exists.
    for _ in range(50):
        if draw == "single":
            picked = supervisor._idle_discover_frame_draw(rng=rng)
            ids = {picked["id"]} if picked else set()
        else:
            picked = supervisor._idle_discover_frame_draw_concurrent(rng=rng, width=3)
            ids = {a["id"] for a in picked}
        assert ids == {"FRESH"}, f"saturated atom re-handed: {ids}"


# ── QUIET: a re-opened atom re-enters the draw (no permanent starve) ──────────


def test_quiet_build_gate_open_atom_re_enters_build_draw(_isolate_map_and_root):
    # "Gate opens" == loop_stage flips off idle. The saturated atom leaves the
    # idle FRAME pool (correctly skipped there) and is picked up by the BUILD
    # draw -- proving re-offer-when-gate-opens, not a permanent hold.
    root = _isolate_map_and_root
    ev = _write_frame_doc(root, "REOPENED")
    reopened = _idle_atom("REOPENED", evidence=[ev])
    reopened["loop_stage"] = "build"      # BUILD-gate opened
    reopened["provenance"] = "proposal"
    _write_map(root, [reopened])
    # Not in the idle FRAME pool any more...
    assert supervisor._idle_discover_frame_draw(rng=random.Random(0)) is None
    # ...but the BUILD draw now selects it (the actual re-entry path).
    build = supervisor._maturity_map_draw_concurrent(rng=random.Random(0))
    assert {a["id"] for a in build} == {"REOPENED"}


def test_quiet_explicit_false_marker_re_offers_saturated_atom(_isolate_map_and_root):
    # The R11 escape: an atom with a FRAME doc but `frame_saturated: false`
    # (a turn judged a FRAME revision genuinely warranted) is offered again --
    # the guard is a cache, never a permanent hold.
    root = _isolate_map_and_root
    ev = _write_frame_doc(root, "REVISE")
    atoms = [_idle_atom("REVISE", frame_saturated=False, evidence=[ev])]
    _write_map(root, atoms)
    picked = supervisor._idle_discover_frame_draw(rng=random.Random(0))
    assert picked is not None and picked["id"] == "REVISE"


# ── ALL-SATURATED: true empty FRAME feasible set -> empty, never a re-hand ────


@pytest.mark.parametrize("draw", ["single", "concurrent"])
def test_all_saturated_returns_empty_not_a_rehand(_isolate_map_and_root, draw):
    root = _isolate_map_and_root
    ev_a = _write_frame_doc(root, "ONLY_A")
    ev_b = _write_frame_doc(root, "ONLY_B")
    atoms = [
        _idle_atom("ONLY_A", evidence=[ev_a]),
        _idle_atom("ONLY_B", evidence=[ev_b]),
    ]
    _write_map(root, atoms)
    rng = random.Random(7)
    if draw == "single":
        assert supervisor._idle_discover_frame_draw(rng=rng) is None
    else:
        assert supervisor._idle_discover_frame_draw_concurrent(rng=rng, width=3) == []


def test_regression_pre_guard_would_have_re_handed(_isolate_map_and_root):
    # Guard-removed control: with the saturation filter bypassed, the old
    # behaviour DID hand a saturated atom -- proving the test would fail if the
    # guard were reverted (the mutation the R15 doctrine requires the test to
    # detect). We simulate the pre-guard state by monkeypatching the predicate
    # to a no-op and asserting a saturated atom is then handed.
    root = _isolate_map_and_root
    ev = _write_frame_doc(root, "SAT_ONLY")
    _write_map(root, [_idle_atom("SAT_ONLY", evidence=[ev])])
    # With the guard live: empty (correct).
    assert supervisor._idle_discover_frame_draw(rng=random.Random(0)) is None
    # Mutate the guard off (revert simulation): the saturated atom IS handed.
    import unittest.mock as mock

    with mock.patch.object(supervisor, "_is_frame_saturated", return_value=False):
        picked = supervisor._idle_discover_frame_draw(rng=random.Random(0))
        assert picked is not None and picked["id"] == "SAT_ONLY"


# ── H23 residual FALSE-NEGATIVE fix (2026-07-16, note[4]): a per-atom FRAME
#    doc under docs/design/ DIRECTLY (non-canonical path, not docs/design/frame/)
#    must read as saturated -- else the treadmill relocates to that atom set.
#    Live repro: W1_10 (docs/design/W1_10_FRAME.md), H20/H21 were re-handed
#    indefinitely while genuinely FRAME-complete. ──────────────────────────────


def _write_noncanonical_frame_doc(root, filename):
    """Create a per-atom FRAME doc directly under docs/design/ (the older,
    non-canonical location the residual false-negative missed) and return its
    repo-relative evidence path."""
    rel = f"docs/design/{filename}"
    (root / rel).write_text("# FRAME (non-canonical path)\n")
    return rel


def test_has_frame_doc_true_for_noncanonical_path_frame_doc(_isolate_map_and_root):
    # FIXES the residual false-negative: pre-fix the `docs/design/frame/` prefix
    # excluded these, so W1_10/H20/H21 (complete FRAME docs under docs/design/)
    # read un-saturated and churned. The filename still carries FRAME, so the
    # broadened prefix correctly marks them saturated.
    root = _isolate_map_and_root
    for fn, aid in [
        ("W1_10_FRAME.md", "W1_10_ev_heatpump_geography"),
        ("H20_PARALLEL_MAINTENANCE_LANE_FRAME.md", "H20_parallel_maintenance_lane"),
        ("H21_SELF_CONTAINED_ESCALATION_FRAME.md", "H21_self_contained_escalation"),
    ]:
        rel = _write_noncanonical_frame_doc(root, fn)
        atom = _idle_atom(aid, evidence=[rel])
        assert supervisor._atom_has_frame_doc(atom) is True, fn
        assert supervisor._is_frame_saturated(atom) is True, fn


def test_discover_stage_doc_under_design_is_not_a_frame_doc(_isolate_map_and_root):
    # FALSE-POSITIVE guard (note[4] DoD): broadening the prefix must NOT mark a
    # genuinely-unframed atom saturated. A DISCOVER-stage doc under docs/design/
    # (filename has no FRAME) leaves real FRAME work -> still un-saturated.
    # Live case: C13 has only docs/design/C13_WEATHER_NORMALISATION_DISCOVER.md.
    root = _isolate_map_and_root
    rel = "docs/design/C13_WEATHER_NORMALISATION_DISCOVER.md"
    (root / rel).write_text("# DISCOVER pass\n")
    atom = _idle_atom("C13_weather_normalisation", evidence=[rel])
    assert supervisor._atom_has_frame_doc(atom) is False
    assert supervisor._is_frame_saturated(atom) is False


@pytest.mark.parametrize("draw", ["single", "concurrent"])
def test_fires_skips_noncanonical_frame_atom_hands_discover_only(_isolate_map_and_root, draw):
    # Integration, both entry points: an atom saturated ONLY via a non-canonical
    # path FRAME doc is never re-handed, while a DISCOVER-only atom (real FRAME
    # work remaining) is the one handed. Encodes the exact live draw membership.
    root = _isolate_map_and_root
    sat = _write_noncanonical_frame_doc(root, "W1_10_FRAME.md")
    disc = "docs/design/C13_WEATHER_NORMALISATION_DISCOVER.md"
    (root / disc).write_text("# DISCOVER\n")
    atoms = [
        _idle_atom("W1_10_ev_heatpump_geography", evidence=[sat]),   # saturated (non-canonical)
        _idle_atom("C13_weather_normalisation", evidence=[disc]),    # un-saturated (DISCOVER only)
    ]
    _write_map(root, atoms)
    rng = random.Random(99)
    for _ in range(50):
        if draw == "single":
            picked = supervisor._idle_discover_frame_draw(rng=rng)
            ids = {picked["id"]} if picked else set()
        else:
            picked = supervisor._idle_discover_frame_draw_concurrent(rng=rng, width=3)
            ids = {a["id"] for a in picked}
        assert ids == {"C13_weather_normalisation"}, f"non-canonical FRAME atom re-handed: {ids}"


def test_regression_noncanonical_prefix_would_have_re_handed(_isolate_map_and_root):
    # Guard-mutation control for THIS fix specifically: restore the pre-fix
    # `docs/design/frame/`-only prefix behaviour by patching _atom_has_frame_doc
    # to the narrow rule, and assert the non-canonical FRAME atom IS then handed
    # -- proving this test fails if the prefix broadening is reverted (R15).
    import unittest.mock as mock
    root = _isolate_map_and_root
    sat = _write_noncanonical_frame_doc(root, "W1_10_FRAME.md")
    _write_map(root, [_idle_atom("W1_10_ev_heatpump_geography", evidence=[sat])])
    # Guard live (broadened prefix): saturated -> empty draw.
    assert supervisor._idle_discover_frame_draw(rng=random.Random(0)) is None

    def _narrow_pre_fix(atom):
        from pathlib import Path as _P
        for e in atom.get("evidence") or []:
            s = str(e)
            if not s.startswith("docs/design/frame/"):   # the reverted prefix
                continue
            if "FRAME" not in _P(s).name.upper():
                continue
            if (supervisor.PROJECT_DIR / s).exists():
                return True
        return False

    with mock.patch.object(supervisor, "_atom_has_frame_doc", side_effect=_narrow_pre_fix):
        picked = supervisor._idle_discover_frame_draw(rng=random.Random(0))
        assert picked is not None and picked["id"] == "W1_10_ev_heatpump_geography"

# ── Publish-gate scope (R10, 2026-07-18): DAEMON-LIFECYCLE test module ──────────
# Validates pipeline MACHINERY (process/session lifecycle, scheduling, notify transport,
# reconciliation), never a published business surface -- so it must never wedge the live
# publish. The gate runs `-m 'not operational'`. See tests/conftest.py for the marker.
import pytest  # noqa: E402,F811
pytestmark = pytest.mark.operational
