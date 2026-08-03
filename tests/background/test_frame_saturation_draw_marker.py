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
    # Isolate the live fronts-enforcement flag (director console act, on main
    # since 2026-07-18): this file tests FRAME-saturation draw re-entry, not
    # front membership, so the global fronts filter must be OFF or the synthetic
    # BUILD atom (in no real open front) is zeroed. See test_fronts_draw_filter.py.
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


# ── FRAME-token vs embedded-word FALSE-POSITIVE fix (2026-07-25 HARDEN red-team):
#    the has-FRAME-doc check keyed on a bare `"FRAME" in name.upper()` SUBSTRING,
#    so `ONE_FRAMEWORK.md` / `TIMEFRAME.md` / `..._REFRAMED_...md` (a real repo
#    file, ONE_FRAMEWORK.md, is heavily cited) would read as a per-atom FRAME doc
#    and FALSELY mark the atom saturated -- starving a genuinely-unframed atom
#    from the idle DISCOVER/FRAME draw (fail-toward-starve = the idle-hole this
#    atom exists to prevent). Fix: match FRAME as a delimited token, not a
#    substring. R15 both directions. ─────────────────────────────────────────────


@pytest.mark.parametrize(
    "fname",
    ["ONE_FRAMEWORK.md", "PRICING_FRAMEWORK.md", "TIMEFRAME.md", "PLAN_REFRAMED_v2.md"],
)
def test_embedded_frame_substring_is_not_a_frame_doc(_isolate_map_and_root, fname):
    # FIXES the false-positive: a filename where FRAME is embedded in a larger
    # word (FRAMEWORK/TIMEFRAME/REFRAMED) is NOT a per-atom FRAME doc -> the atom
    # keeps its FRAME work and must stay OFFERED, never starved.
    root = _isolate_map_and_root
    rel = f"docs/design/{fname}"
    (root / rel).write_text("# not a FRAME-stage doc\n")
    atom = _idle_atom("SOME_ATOM", evidence=[rel])
    assert supervisor._atom_has_frame_doc(atom) is False, fname
    assert supervisor._is_frame_saturated(atom) is False, fname


def test_delimited_frame_token_still_reads_as_frame_doc(_isolate_map_and_root):
    # The tightening must NOT regress the real convention: `_FRAME.md` and the
    # `_FRAME_DISCOVER.md` mid-name token both remain delimited FRAME tokens.
    root = _isolate_map_and_root
    for fn, aid in [
        ("ARCH1_FRAME.md", "ARCH1_internal_seams"),
        ("EPOCH2_A_SCOPE_OF_NEED_SCORING_FRAME_DISCOVER.md", "EPOCH2_A_scope"),
    ]:
        rel = f"docs/design/{fn}"
        (root / rel).write_text("# FRAME\n")
        atom = _idle_atom(aid, evidence=[rel])
        assert supervisor._atom_has_frame_doc(atom) is True, fn
        assert supervisor._is_frame_saturated(atom) is True, fn


@pytest.mark.parametrize("draw", ["single", "concurrent"])
def test_fires_offers_atom_evidenced_only_by_framework_doc(_isolate_map_and_root, draw):
    # Integration, both entry points: an atom whose ONLY docs/design evidence is
    # a FRAMEWORK-named doc (embedded FRAME) has real FRAME work left, so it is
    # the one HANDED, never starved -- while a genuinely saturated (_FRAME.md)
    # atom beside it is skipped.
    root = _isolate_map_and_root
    fw = "docs/design/ONE_FRAMEWORK.md"
    (root / fw).write_text("# framework, not a per-atom FRAME doc\n")
    sat = _write_frame_doc(root, "REALLY_SAT")
    atoms = [
        _idle_atom("HAS_FRAME_WORK", evidence=[fw]),   # un-saturated (embedded word)
        _idle_atom("REALLY_SAT", evidence=[sat]),      # saturated (_FRAME.md)
    ]
    _write_map(root, atoms)
    rng = random.Random(2026)
    for _ in range(50):
        if draw == "single":
            picked = supervisor._idle_discover_frame_draw(rng=rng)
            ids = {picked["id"]} if picked else set()
        else:
            picked = supervisor._idle_discover_frame_draw_concurrent(rng=rng, width=3)
            ids = {a["id"] for a in picked}
        assert ids == {"HAS_FRAME_WORK"}, f"framework-doc atom starved / sat re-handed: {ids}"


def test_regression_substring_rule_would_have_starved_framework_atom(_isolate_map_and_root):
    # Guard-mutation control for THIS fix (R15): restore the pre-fix bare
    # substring rule via monkeypatch and assert the FRAMEWORK-only atom is then
    # (wrongly) marked saturated and STARVED -> the draw returns None. Proves
    # this test fails if the token-boundary tightening is reverted.
    import unittest.mock as mock
    root = _isolate_map_and_root
    fw = "docs/design/ONE_FRAMEWORK.md"
    (root / fw).write_text("# framework\n")
    _write_map(root, [_idle_atom("HAS_FRAME_WORK", evidence=[fw])])
    # Guard live (token rule): un-saturated -> the atom IS offered.
    picked = supervisor._idle_discover_frame_draw(rng=random.Random(0))
    assert picked is not None and picked["id"] == "HAS_FRAME_WORK"

    def _substring_pre_fix(atom):
        from pathlib import Path as _P
        for e in atom.get("evidence") or []:
            s = str(e)
            if not s.startswith("docs/design/"):
                continue
            if "FRAME" not in _P(s).name.upper():   # the reverted SUBSTRING rule
                continue
            if (supervisor.PROJECT_DIR / s).exists():
                return True
        return False

    with mock.patch.object(supervisor, "_atom_has_frame_doc", side_effect=_substring_pre_fix):
        assert supervisor._idle_discover_frame_draw(rng=random.Random(0)) is None


# ── EMPTY / STUB FRAME-doc FALSE-POSITIVE fix (2026-07-27 HARDEN red-team):
#    `_atom_has_frame_doc` counted ANY existing evidence path as a complete FRAME
#    doc -- so a 0-byte / whitespace-only stub (an interrupted turn's placeholder)
#    or an evidence entry resolving to a DIRECTORY (`docs/design/frame/`) marked
#    the atom FRAME-saturated and STARVED it from the idle FRAME draw. That is the
#    fail-toward-starve wrong-side failure this atom exists to prevent (R15
#    FAIL-OPEN-on-empty: a check that passes on empty/malformed input is worse
#    than none). Fix: require a regular file with non-whitespace content. Live
#    tree safe -- every real FRAME doc is >5KB. R15 both directions. ───────────────


@pytest.mark.parametrize("body", ["", "   \n\t\n"])
def test_empty_or_whitespace_frame_doc_is_not_a_frame_doc(_isolate_map_and_root, body):
    # FIXES the false-positive: an existing but empty/whitespace-only `_FRAME.md`
    # is a stub, not an honest FRAME output -> the atom keeps its FRAME work and
    # must stay OFFERED, never starved.
    root = _isolate_map_and_root
    rel = "docs/design/frame/STUB_ATOM_FRAME.md"
    (root / rel).write_text(body)
    atom = _idle_atom("STUB_ATOM", evidence=[rel])
    assert supervisor._atom_has_frame_doc(atom) is False
    assert supervisor._is_frame_saturated(atom) is False


def test_directory_evidence_entry_is_not_a_frame_doc(_isolate_map_and_root):
    # An evidence entry resolving to a DIRECTORY (name carries the FRAME token,
    # exists() is True for a dir) is not a doc -> not saturated.
    root = _isolate_map_and_root
    (root / "docs" / "design" / "frame").mkdir(parents=True, exist_ok=True)
    atom = _idle_atom("DIR_ATOM", evidence=["docs/design/frame"])
    assert supervisor._atom_has_frame_doc(atom) is False
    assert supervisor._is_frame_saturated(atom) is False


def test_nonempty_frame_doc_still_reads_as_saturated(_isolate_map_and_root):
    # The tightening must NOT regress the real convention: a FRAME doc with actual
    # content still reads as saturated (the FIRES direction of this fix).
    root = _isolate_map_and_root
    rel = _write_frame_doc(root, "REAL_ATOM")   # writes "# FRAME -- REAL_ATOM\n"
    atom = _idle_atom("REAL_ATOM", evidence=[rel])
    assert supervisor._atom_has_frame_doc(atom) is True
    assert supervisor._is_frame_saturated(atom) is True


@pytest.mark.parametrize("draw", ["single", "concurrent"])
def test_fires_offers_atom_with_only_a_stub_frame_doc(_isolate_map_and_root, draw):
    # Integration, both entry points: an atom whose ONLY FRAME evidence is an
    # empty stub has real FRAME work left, so it is the one HANDED, never starved
    # -- while a genuinely-complete (_FRAME.md with content) atom beside it is
    # skipped.
    root = _isolate_map_and_root
    stub = "docs/design/frame/STUB_ONLY_FRAME.md"
    (root / stub).write_text("")                       # empty stub
    real = _write_frame_doc(root, "COMPLETE")          # real content
    atoms = [
        _idle_atom("STUB_ONLY", evidence=[stub]),      # un-saturated (empty stub)
        _idle_atom("COMPLETE", evidence=[real]),       # saturated (real doc)
    ]
    _write_map(root, atoms)
    rng = random.Random(31337)
    for _ in range(50):
        if draw == "single":
            picked = supervisor._idle_discover_frame_draw(rng=rng)
            ids = {picked["id"]} if picked else set()
        else:
            picked = supervisor._idle_discover_frame_draw_concurrent(rng=rng, width=3)
            ids = {a["id"] for a in picked}
        assert ids == {"STUB_ONLY"}, f"stub-only atom starved / real re-handed: {ids}"


def test_regression_existence_only_rule_would_have_starved_stub_atom(_isolate_map_and_root):
    # Guard-mutation control for THIS fix (R15): restore the pre-fix existence-only
    # rule via monkeypatch and assert the stub-only atom is then (wrongly) marked
    # saturated and STARVED -> the draw returns None. Proves this test fails if the
    # content-nonempty tightening is reverted.
    import unittest.mock as mock
    root = _isolate_map_and_root
    stub = "docs/design/frame/STUB_ONLY_FRAME.md"
    (root / stub).write_text("")
    _write_map(root, [_idle_atom("STUB_ONLY", evidence=[stub])])
    # Guard live (content rule): un-saturated -> the atom IS offered.
    picked = supervisor._idle_discover_frame_draw(rng=random.Random(0))
    assert picked is not None and picked["id"] == "STUB_ONLY"

    def _existence_only_pre_fix(atom):
        from pathlib import Path as _P
        import re as _re
        for e in atom.get("evidence") or []:
            s = str(e)
            if not s.startswith("docs/design/"):
                continue
            if "FRAME" not in _re.split(r"[^A-Z0-9]+", _P(s).name.upper()):
                continue
            if (supervisor.PROJECT_DIR / s).exists():   # the reverted existence-only rule
                return True
        return False

    with mock.patch.object(supervisor, "_atom_has_frame_doc", side_effect=_existence_only_pre_fix):
        assert supervisor._idle_discover_frame_draw(rng=random.Random(0)) is None


# ── frame_saturated OVERRIDE robustness (2026-07-27 HARDEN red-team, R15
#    FAIL-SILENT): the R11 escape must survive being typed the way a map-writer
#    would typo it (a QUOTED "false"/"true", a bare 0/1). `_is_frame_saturated`
#    previously honoured the override ONLY for a genuine Python bool and silently
#    fell through to intrinsic otherwise -- so a mistyped force-OFFER STARVED the
#    atom and a mistyped force-SKIP RE-HANDED it (the treadmill). This is the
#    SIBLING half of the class every prior H23 pass hardened (_atom_has_frame_doc).
#    ──────────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("token", ["false", "False", "FALSE", " no ", "off", "0"])
def test_override_string_falsey_forces_offer(_isolate_map_and_root, token):
    # force-OFFER via a QUOTED/token frame_saturated on a FRAME-doc'd atom: the
    # atom is intrinsically saturated (real FRAME doc) but the escape must win ->
    # NOT saturated -> offered. Pre-fix: the string was ignored -> stayed
    # saturated -> STARVED (the wrong-side failure).
    root = _isolate_map_and_root
    ev = _write_frame_doc(root, "FORCE_OFFER")
    atom = _idle_atom("FORCE_OFFER", frame_saturated=token, evidence=[ev])
    assert supervisor._is_frame_saturated(atom) is False


@pytest.mark.parametrize("token", ["true", "True", "TRUE", " yes ", "on", "1"])
def test_override_string_truthy_forces_skip(_isolate_map_and_root, token):
    # force-SKIP via a QUOTED/token frame_saturated on an atom with NO canonical
    # FRAME doc (the live use case -- a DISCOVER-named doc the filename heuristic
    # can't see): the escape must win -> saturated -> skipped. Pre-fix: the string
    # was ignored -> intrinsic false -> RE-HANDED every tick (the treadmill).
    atom = _idle_atom("FORCE_SKIP", frame_saturated=token, evidence=[])
    assert supervisor._is_frame_saturated(atom) is True


def test_override_bare_int_0_1(_isolate_map_and_root):
    # A bare integer 0/1 (bool is an int subclass but 0/1 are not bools) is a
    # plausible hand-edit: honour it the same way.
    root = _isolate_map_and_root
    ev = _write_frame_doc(root, "INT_OFFER")
    assert supervisor._is_frame_saturated(_idle_atom("INT_OFFER", frame_saturated=0, evidence=[ev])) is False
    assert supervisor._is_frame_saturated(_idle_atom("INT_SKIP", frame_saturated=1, evidence=[])) is True


def test_override_unrecognised_value_logs_and_falls_through(_isolate_map_and_root, monkeypatch):
    # A genuinely unrecognised override (garbage, an out-of-range int) must NOT be
    # silently swallowed: it LOGS (surfaced, not vanished) and falls through to the
    # intrinsic check -- fail-loud on garbage, per R15.
    root = _isolate_map_and_root
    ev = _write_frame_doc(root, "GARBAGE")
    logged = []
    monkeypatch.setattr(supervisor, "log", lambda msg: logged.append(msg))
    for bad in ("maybe", "", 2, [], {"x": 1}):
        assert supervisor._coerce_frame_saturated_override(bad) is None
    # A FRAME-doc'd atom with a garbage override falls through to intrinsic -> True.
    assert supervisor._is_frame_saturated(_idle_atom("GARBAGE", frame_saturated="maybe", evidence=[ev])) is True
    assert logged and all("FAIL-SILENT" in m for m in logged), "garbage override must be logged, not swallowed"


def test_override_none_and_missing_use_intrinsic(_isolate_map_and_root):
    # No override present (or explicit None) -> intrinsic check governs, unchanged.
    root = _isolate_map_and_root
    ev = _write_frame_doc(root, "NO_OVERRIDE")
    assert supervisor._coerce_frame_saturated_override(None) is None
    assert supervisor._is_frame_saturated(_idle_atom("NO_OVERRIDE", evidence=[ev])) is True
    assert supervisor._is_frame_saturated(_idle_atom("NO_DOC", evidence=[])) is False


@pytest.mark.parametrize("draw", ["single", "concurrent"])
def test_fires_string_force_offer_atom_is_handed_not_starved(_isolate_map_and_root, draw):
    # Integration, both entry points: a FRAME-doc'd atom carrying a QUOTED
    # `frame_saturated: "false"` (string force-OFFER) must be the one HANDED,
    # while a genuinely-saturated atom (real FRAME doc, no override) beside it is
    # skipped. Pre-fix the string override was ignored -> BOTH read saturated ->
    # the draw returned empty and the force-offer atom was starved.
    root = _isolate_map_and_root
    ev_offer = _write_frame_doc(root, "STR_OFFER")
    ev_sat = _write_frame_doc(root, "TRULY_SAT")
    atoms = [
        _idle_atom("STR_OFFER", frame_saturated="false", evidence=[ev_offer]),  # force-offered
        _idle_atom("TRULY_SAT", evidence=[ev_sat]),                             # saturated
    ]
    _write_map(root, atoms)
    rng = random.Random(4242)
    for _ in range(50):
        if draw == "single":
            picked = supervisor._idle_discover_frame_draw(rng=rng)
            ids = {picked["id"]} if picked else set()
        else:
            picked = supervisor._idle_discover_frame_draw_concurrent(rng=rng, width=3)
            ids = {a["id"] for a in picked}
        assert ids == {"STR_OFFER"}, f"string force-offer starved / saturated re-handed: {ids}"


def test_regression_bool_only_gate_would_have_starved_string_override(_isolate_map_and_root):
    # Guard-mutation control for THIS fix (R15): restore the pre-fix bool-ONLY
    # override gate and assert a string force-OFFER atom is then (wrongly) marked
    # saturated -> STARVED (the draw returns None). Proves this test fails if the
    # token-coercion is reverted to `isinstance(explicit, bool)`.
    import unittest.mock as mock
    root = _isolate_map_and_root
    ev = _write_frame_doc(root, "STR_ONLY")
    _write_map(root, [_idle_atom("STR_ONLY", frame_saturated="false", evidence=[ev])])
    # Coercion live: the string force-offer is honoured -> the atom IS offered.
    picked = supervisor._idle_discover_frame_draw(rng=random.Random(0))
    assert picked is not None and picked["id"] == "STR_ONLY"

    # Revert simulation: bool-only gate ignores the string -> intrinsic True -> starved.
    def _bool_only_pre_fix(value):
        return value if isinstance(value, bool) else None

    with mock.patch.object(supervisor, "_coerce_frame_saturated_override", side_effect=_bool_only_pre_fix):
        assert supervisor._idle_discover_frame_draw(rng=random.Random(0)) is None


# ── 2026-07-27 HARDEN red-team #3: the cooldown scope_sha signal was DEAD for H23 ──
# Sibling class to the OVERRIDE-parse (#2) and _atom_has_frame_doc (#1, 07-25) passes:
# THIS one is the OTHER half of H23's rotation KEY -- the `scope_sha` re-verify signal
# the 2026-07-27 H1 red-team (commit 2caa174e5) added to _harden_in_cooldown so a commit
# hardening a SIBLING atom on shared code (H1/H19/OPS1 all share supervisor.py) re-offers
# this atom. That signal is computed by _file_scope_sha, which read_bytes() each scope
# entry -- and a DIRECTORY entry raises OSError -> `continue` -> contributes NOTHING. H23's
# file_scope was 4 directories, so _file_scope_sha(H23) == '' and the scope_sha half of its
# cooldown key was silently DEAD (R15 FAIL-SILENT: a check that always yields the empty/
# no-op signal is worse than none). 45 live map atoms share a directory file_scope entry.


def test_file_scope_sha_fail_silent_on_directory_scope(tmp_path):
    """R15 BOTH-ways for the scope_sha FAIL-SILENT this pass closes.

    DEAD side (the defect): a directory-only file_scope yields '' -- no signal.
    LIVE side (the fix path): a real FILE yields a non-empty content-derived sha
    that MOVES when the file's bytes change (re-verify fires on sibling edits).
    MIXED-scope trap: appending a directory entry does NOT change the sha (the dir
    is silently dropped) -- partial coverage that reads as complete."""
    (tmp_path / "background").mkdir()
    f = tmp_path / "background" / "supervisor.py"
    f.write_text("x = 1\n")

    # DEAD side: directory-only scope -> '' (the exact H23 pre-fix state).
    assert supervisor._file_scope_sha({"file_scope": ["background"]}, root=tmp_path) == ""

    # LIVE side: a real controlled file -> non-empty, content-derived.
    sha1 = supervisor._file_scope_sha({"file_scope": ["background/supervisor.py"]}, root=tmp_path)
    assert sha1 != ""
    f.write_text("x = 2\n")
    sha2 = supervisor._file_scope_sha({"file_scope": ["background/supervisor.py"]}, root=tmp_path)
    assert sha2 != sha1, "scope_sha did not move on a controlled-file edit -> re-verify blind"

    # MIXED-scope fail-silent: the directory entry contributes nothing, so the
    # sha is identical to the file-only scope -> a change UNDER that dir is invisible.
    sha_mixed = supervisor._file_scope_sha(
        {"file_scope": ["background/supervisor.py", "background"]}, root=tmp_path)
    assert sha_mixed == sha2


def test_h23_file_scope_is_narrowed_to_real_files_so_scope_sha_is_live():
    """H23's own rotation-memory invariant (reds if H23 is re-broadened to a
    directory file_scope, which would silently re-kill its scope_sha signal).
    Reads the LIVE map by a __file__-derived repo path, independent of the
    autouse map-isolation fixture."""
    import pathlib
    import yaml
    repo = pathlib.Path(__file__).resolve().parents[2]
    atoms = yaml.safe_load((repo / "docs/design/maturity_map.yaml").read_text(encoding="utf-8"))
    h23 = next(a for a in atoms if a.get("id") == "H23_frame_saturation_draw_marker")
    assert h23["file_scope"], "H23 file_scope empty"
    for rel in h23["file_scope"]:
        assert (repo / rel).is_file(), \
            f"H23 file_scope entry is a directory, not a file (dead scope_sha): {rel}"
    assert supervisor._file_scope_sha(h23, root=repo) != "", \
        "H23 scope_sha is dead ('') -- the sibling-change re-verify signal is absent"


# ── SCALAR-string evidence FALSE-NEGATIVE fix (2026-07-28 HARDEN red-team, R15
#    FAIL-SILENT): `_atom_has_frame_doc` iterated `atom.get("evidence") or []`
#    directly. A LIST iterates entries, but a scalar STRING (`evidence:
#    docs/design/frame/X_FRAME.md` -- the natural YAML hand-edit typo, a one-item
#    list written without the `- `) iterates its CHARACTERS, none of which start
#    with `docs/design/`, so an atom carrying a REAL complete FRAME doc pointed at
#    by a scalar read as UN-saturated and was RE-HANDED every idle cycle: the exact
#    treadmill (this atom's DIAL defect, occurrences 1-5) it exists to stop, reached
#    through a scalar typo. SIBLING of the 07-27 override-parse (`"false"`/`0`) and
#    _atom_has_frame_doc substring/stub passes -- the same hand-edit-typo class
#    reaching a different consumer. Fix: `_normalize_evidence_list` coerces a scalar
#    string to a one-item list and fail-loud-logs a genuinely unexpected type. R15
#    both directions. ──────────────────────────────────────────────────────────────


def test_scalar_string_evidence_pointing_at_frame_doc_reads_saturated(_isolate_map_and_root):
    # FIXES the false-negative: an atom whose `evidence` is a SCALAR STRING (not a
    # list) pointing at a real complete FRAME doc must read as SATURATED -> skipped,
    # not char-iterated to False -> re-handed (the treadmill).
    root = _isolate_map_and_root
    rel = _write_frame_doc(root, "SCALAR_SAT")
    atom = {"id": "SCALAR_SAT", "lane": "H_harness", "level_current": 0,
            "level_target": 2, "loop_stage": "idle", "dial_inherited": 2,
            "evidence": rel}                      # scalar string, NOT a list
    assert supervisor._atom_has_frame_doc(atom) is True
    assert supervisor._is_frame_saturated(atom) is True


def test_scalar_string_evidence_non_frame_path_stays_unsaturated(_isolate_map_and_root):
    # NO starve introduced: a scalar string pointing at a NON-FRAME path (a
    # DISCOVER doc) still reads un-saturated -> the atom stays OFFERED, unchanged.
    root = _isolate_map_and_root
    rel = "docs/design/SCALAR_DISCOVER.md"
    (root / rel).write_text("# discover\n")
    atom = {"id": "SCALAR_DISC", "lane": "H_harness", "level_current": 0,
            "level_target": 2, "loop_stage": "idle", "dial_inherited": 2,
            "evidence": rel}                      # scalar string, non-FRAME
    assert supervisor._atom_has_frame_doc(atom) is False
    assert supervisor._is_frame_saturated(atom) is False


def test_normalize_evidence_list_forms(_isolate_map_and_root, monkeypatch):
    # Unit: None/list pass through; a scalar string becomes a one-item list; a
    # genuinely unexpected type (dict/int) LOGS (fail-loud) and reads as empty.
    assert supervisor._normalize_evidence_list(None) == []
    assert supervisor._normalize_evidence_list(["a", "b"]) == ["a", "b"]
    assert supervisor._normalize_evidence_list("docs/design/frame/X_FRAME.md") == \
        ["docs/design/frame/X_FRAME.md"]
    logged = []
    monkeypatch.setattr(supervisor, "log", lambda m: logged.append(m))
    for bad in ({"x": 1}, 7, 3.5):
        assert supervisor._normalize_evidence_list(bad) == []
    assert logged and all("FAIL-SILENT" in m for m in logged), \
        "unexpected evidence type must be logged, not swallowed"


@pytest.mark.parametrize("draw", ["single", "concurrent"])
def test_fires_scalar_saturated_atom_is_skipped(_isolate_map_and_root, draw):
    # Integration, both entry points: an atom saturated ONLY via a scalar-string
    # FRAME-doc evidence is never re-handed, while a genuinely-unframed atom beside
    # it is the one handed. Encodes the exact live-draw membership under the typo.
    root = _isolate_map_and_root
    sat = _write_frame_doc(root, "SCALAR_ONLY")
    atoms = [
        {"id": "SCALAR_ONLY", "lane": "H_harness", "level_current": 0,
         "level_target": 2, "loop_stage": "idle", "dial_inherited": 2,
         "evidence": sat},                        # saturated (scalar)
        _idle_atom("FRESH2", evidence=[]),        # un-saturated: real FRAME work
    ]
    _write_map(root, atoms)
    rng = random.Random(818)
    for _ in range(50):
        if draw == "single":
            picked = supervisor._idle_discover_frame_draw(rng=rng)
            ids = {picked["id"]} if picked else set()
        else:
            picked = supervisor._idle_discover_frame_draw_concurrent(rng=rng, width=3)
            ids = {a["id"] for a in picked}
        assert ids == {"FRESH2"}, f"scalar-saturated atom re-handed / fresh starved: {ids}"


def test_regression_char_iteration_would_have_re_handed_scalar_atom(_isolate_map_and_root):
    # Guard-mutation control for THIS fix (R15): restore the pre-fix direct
    # `evidence or []` char-iteration via monkeypatch and assert a scalar-only
    # saturated atom is then (wrongly) read un-saturated and RE-HANDED -> the draw
    # returns it. Proves this test fails if the normaliser is reverted.
    import unittest.mock as mock
    root = _isolate_map_and_root
    sat = _write_frame_doc(root, "SCALAR_REG")
    atom = {"id": "SCALAR_REG", "lane": "H_harness", "level_current": 0,
            "level_target": 2, "loop_stage": "idle", "dial_inherited": 2,
            "evidence": sat}
    _write_map(root, [atom])
    # Normaliser live: scalar recognised -> saturated -> empty draw.
    assert supervisor._idle_discover_frame_draw(rng=random.Random(0)) is None

    def _char_iter_pre_fix(value):
        # The reverted behaviour: `evidence or []` -- a scalar str is returned
        # as-is and later char-iterated by the caller.
        return value or []

    with mock.patch.object(supervisor, "_normalize_evidence_list", side_effect=_char_iter_pre_fix):
        picked = supervisor._idle_discover_frame_draw(rng=random.Random(0))
        assert picked is not None and picked["id"] == "SCALAR_REG"


# ── Publish-gate scope (R10, 2026-07-18): DAEMON-LIFECYCLE test module ──────────
# Validates pipeline MACHINERY (process/session lifecycle, scheduling, notify transport,
# reconciliation), never a published business surface -- so it must never wedge the live
# publish. The gate runs `-m 'not operational'`. See tests/conftest.py for the marker.
import pytest  # noqa: E402,F811
pytestmark = pytest.mark.operational
