"""§0 LEVEL-PROMOTION PREVENTION gate -- R15 mutation tests (2026-07-18).

The gate's job: an UNAUTHORIZED level_current increase in docs/design/maturity_map.yaml is refused
at commit time (exit 1); a director-authorized increase, a decrease/revert, and any non-map commit
pass. These tests exercise the PURE predicate + `evaluate` (git-free) so they mutation-test the
core, and prove the neuter (always-allow) turns the "rejected" test RED (independence).

The validity of an authorization is REUSED from background.gate_authorization.is_valid_level_up --
so a forged ledger entry (channel != console / no provenance) authorizes nothing here, exactly as
in the reconciler. These tests confirm that reuse fires, they do not re-assert its internals.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GATE_PATH = ROOT / "tools" / "level_promotion_gate.py"

spec = importlib.util.spec_from_file_location("level_promotion_gate", GATE_PATH)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


# ── map fixtures ─────────────────────────────────────────────────────────────────────────────
def _map(level: int) -> str:
    return f"""- id: E4_supplier_reporting_standard
  name: "E4"
  level_current: {level}
  level_target: 3
  loop_stage: harden
- id: D1_bill_correctness
  level_current: 2
  loop_stage: harden
"""


# 2026-08-03: the valid RECORD is now a self-certification, not a director-console act. The gate's
# question changed from "did the director permit this?" to "was this move RECORDED, honestly and
# with evidence?" -- so the fixture that stands for a valid entry changed with it. A legacy
# LEVEL_UP_PROPOSED console entry is history, and authorizes nothing (see
# tests/background/test_gate_authorization.py::test_legacy_director_and_twin_entries_are_history).
VALID_LEVEL_UP = {
    "atom": "E4_supplier_reporting_standard", "action": "LEVEL_UP_SELF_CERTIFIED", "level": 3,
    "authorized_by": "agent_self_certified", "channel": "self",
    "provenance": "E4 -> L3: 41 tests green, R15 mutation proof both ways, live surface fetched.",
}
# Same intent, but FORGED: written by the worker, self-declaring a non-console channel / no
# provenance -- is_valid_level_up must reject it, so it authorizes nothing.
FORGED_LEVEL_UP = {
    "atom": "E4_supplier_reporting_standard", "action": "LEVEL_UP_PROPOSED", "level": 3,
    "authorized_by": "autonomous_worker", "channel": "worker", "provenance": "",
}


# ── the four R15 mutation tests + neuter proof ─────────────────────────────────────────────────
def test_unauthorized_increase_is_REJECTED():
    """§0: level 2->3 with an EMPTY ledger -> the gate refuses the commit. This is the test the
    neuter (always-allow) must turn RED -- it asserts a non-empty unauthorized set + REJECT status."""
    result = gate.evaluate(old_text=_map(2), new_text=_map(3), ledger=[])
    assert result["status"] == "REJECT"
    assert any(u["atom"] == "E4_supplier_reporting_standard" and u["from"] == 2 and u["to"] == 3
               for u in result["unauthorized"])
    assert "no recorded LEVEL_UP" in result["message"]
    # And the pure predicate the neuter would break:
    incs = gate.level_increases(gate.atom_levels(_map(2)), gate.atom_levels(_map(3)))
    assert gate.unauthorized_level_increases(incs, ledger=[]) != []


def test_same_increase_WITH_valid_authorization_is_ALLOWED():
    result = gate.evaluate(old_text=_map(2), new_text=_map(3), ledger=[VALID_LEVEL_UP])
    assert result["status"] == "CLEAN"
    assert result["unauthorized"] == []


def test_level_DECREASE_revert_is_ALLOWED():
    """L3->L2 un-promotion is not a self-promotion -> allowed even with an empty ledger."""
    result = gate.evaluate(old_text=_map(3), new_text=_map(2), ledger=[])
    assert result["status"] == "CLEAN"
    assert gate.level_increases(gate.atom_levels(_map(3)), gate.atom_levels(_map(2))) == []


def test_forged_ledger_entry_does_NOT_authorize():
    """A worker-forged entry (channel != console / no provenance) fails is_valid_level_up, so the
    2->3 increase stays unauthorized and the commit is refused -- reuse of the reconciler predicate."""
    result = gate.evaluate(old_text=_map(2), new_text=_map(3), ledger=[FORGED_LEVEL_UP])
    assert result["status"] == "REJECT"
    assert result["unauthorized"] and result["unauthorized"][0]["atom"] == "E4_supplier_reporting_standard"


# ── boundary / no-false-positive coverage ──────────────────────────────────────────────────────
# ── self-certification (2026-07-29 ruling item 2): recording, not director permission, is required ──
SELF_CERTIFIED_LEVEL_UP = {
    "atom": "E4_supplier_reporting_standard", "action": "LEVEL_UP_SELF_CERTIFIED", "level": 3,
    "authorized_by": "agent_self_certified", "channel": "self",
    "provenance": "tests green 12/12, R15 mutation both-ways proven",
}


def test_self_certified_increase_is_ALLOWED():
    """A self-certified entry (no director act) now clears the gate -- recording, not permission,
    is what R16 requires (2026-07-29 ruling item 2)."""
    result = gate.evaluate(old_text=_map(2), new_text=_map(3), ledger=[SELF_CERTIFIED_LEVEL_UP])
    assert result["status"] == "CLEAN"
    assert result["unauthorized"] == []


def test_self_certified_with_no_evidence_does_NOT_clear():
    """A self-cert entry missing its provenance (no evidence) is dishonest bookkeeping, not a record
    -- is_valid_self_certified_level_up rejects it, so the gate still refuses."""
    unevidenced = {**SELF_CERTIFIED_LEVEL_UP, "provenance": ""}
    result = gate.evaluate(old_text=_map(2), new_text=_map(3), ledger=[unevidenced])
    assert result["status"] == "REJECT"


def test_authorization_below_new_level_does_NOT_clear():
    """A LEVEL_UP bounded to level 2 does not authorize a 2->3 move (to_level > authorized level)."""
    low = dict(VALID_LEVEL_UP, level=2)
    result = gate.evaluate(old_text=_map(2), new_text=_map(3), ledger=[low])
    assert result["status"] == "REJECT"


def test_level_bounded_authorization_at_or_above_clears():
    """level=None (any-increase) and level>=new both clear."""
    any_lvl = {k: v for k, v in VALID_LEVEL_UP.items() if k != "level"}
    assert gate.evaluate(_map(2), _map(3), ledger=[any_lvl])["status"] == "CLEAN"
    higher = dict(VALID_LEVEL_UP, level=4)
    assert gate.evaluate(_map(2), _map(3), ledger=[higher])["status"] == "CLEAN"


def test_no_change_is_CLEAN():
    assert gate.evaluate(_map(3), _map(3), ledger=[])["status"] == "CLEAN"


def test_new_atom_appearing_is_ALLOWED():
    """An atom absent from the HEAD map (new atom) is not a self-promotion here (reconciler/baseline
    own new atoms) -- it must not false-reject a legitimate seed."""
    old = """- id: D1_bill_correctness
  level_current: 2
  loop_stage: harden
"""
    new = old + """- id: NEW_atom_x
  level_current: 3
  loop_stage: build
"""
    assert gate.evaluate(old_text=old, new_text=new, ledger=[])["status"] == "CLEAN"


def test_new_file_no_baseline_is_ALLOWED():
    # A new map file has no baseline -> not a REJECT (the commit passes); status is the distinct
    # CLEAN_NEW_FILE marker, and main() only refuses on a REJECT* status.
    assert gate.evaluate(old_text=None, new_text=_map(3), ledger=[])["status"] == "CLEAN_NEW_FILE"


def test_unparseable_staged_map_FAILS_CLOSED():
    """A syntactically broken STAGED map cannot be verified -> REJECT (an increase could hide in it)."""
    result = gate.evaluate(old_text=_map(2), new_text="::: not: valid: yaml: [", ledger=[])
    assert result["status"] == "REJECT_UNPARSEABLE"


def test_atom_levels_parses_ids_and_levels():
    levels = gate.atom_levels(_map(3))
    assert levels["E4_supplier_reporting_standard"] == 3
    assert levels["D1_bill_correctness"] == 2


# ══════════════════════════════════════════════════════════════════════════════════════════════
# SECOND CONTROL (2026-08-10): RECORDED-BUT-UNBUILT -- a level declared for uncommitted code.
#
# R15 BOTH WAYS, which for this control means three obligations, not one:
#   (a) it FIRES on its own named defect (the H39 shape: source dirty in the atom's file_scope);
#   (b) it PASSES on an ordinary clean level move -- a control that can only fail gets routed
#       around within a day, so the passing direction is part of the proof, not a nicety;
#   (c) the NEUTER (always-clean) turns (a) RED -- independence.
# ══════════════════════════════════════════════════════════════════════════════════════════════

_SCOPED_MAP = """- id: H39_the_texture
  level_current: {lvl}
  file_scope:
    - background/fabric_gap_ledger.py
    - tests/harness/test_premise_two_level.py
"""


def _scoped_map(level: int) -> str:
    return _SCOPED_MAP.format(lvl=level)


# The porcelain block git would emit for that file_scope in the H39 incident: the program was
# verified green in the tree and never committed.
DIRTY_PORCELAIN = " M background/fabric_gap_ledger.py\n?? tests/harness/test_premise_two_level.py\n"


def test_dirty_file_scope_REFUSES_the_increase():
    """(a) THE named defect: the atom's file_scope holds source that is not landing -> unbuilt.
    This is the test the neuter must turn RED."""
    incs = [{"atom": "H39_the_texture", "from": 1, "to": 2}]
    unbuilt = gate.unbuilt_level_increases(incs, {"H39_the_texture": DIRTY_PORCELAIN})
    assert len(unbuilt) == 1
    assert unbuilt[0]["dirty"] == ["background/fabric_gap_ledger.py",
                                   "tests/harness/test_premise_two_level.py"]
    assert unbuilt[0]["unverifiable"] is False


def test_clean_file_scope_ALLOWS_the_increase():
    """(b) THE PASSING DIRECTION: an ordinary level move whose source is fully staged in this
    commit. Porcelain X=M,Y=' ' means the worktree equals what is being committed."""
    staged_and_clean = "M  background/fabric_gap_ledger.py\nM  tests/harness/test_premise_two_level.py\n"
    assert gate.unbuilt_level_increases(
        [{"atom": "H39_the_texture", "from": 1, "to": 2}],
        {"H39_the_texture": staged_and_clean}) == []
    # ...and the wholly-clean tree, the commonest clean case of all.
    assert gate.unbuilt_level_increases(
        [{"atom": "H39_the_texture", "from": 1, "to": 2}], {"H39_the_texture": ""}) == []


def test_neuter_always_clean_turns_the_defect_test_RED():
    """(c) INDEPENDENCE: replace the dirt predicate with one that finds nothing (the fail-open
    mutation) and the (a) assertion collapses -- so (a) is really carried by the predicate."""
    original = gate.dirty_source_paths
    try:
        gate.dirty_source_paths = lambda porcelain: []  # the mutation
        assert gate.unbuilt_level_increases(
            [{"atom": "H39_the_texture", "from": 1, "to": 2}],
            {"H39_the_texture": DIRTY_PORCELAIN}) == []  # <- what (a) asserts is NOT empty
    finally:
        gate.dirty_source_paths = original
    # restored: the real predicate fires again
    assert gate.unbuilt_level_increases(
        [{"atom": "H39_the_texture", "from": 1, "to": 2}],
        {"H39_the_texture": DIRTY_PORCELAIN}) != []


def test_PARTIALLY_staged_source_is_unbuilt():
    """X=M,Y=M -- half the verified program lands, half stays in the tree. A pathspec-vs-file_scope
    comparison would wave this through; the worktree column catches it."""
    assert gate.dirty_source_paths("MM background/fabric_gap_ledger.py\n") == [
        "background/fabric_gap_ledger.py"]


def test_probe_failure_is_UNBUILT_not_clean():
    """R15 fail-silent: an unavailable check is a FAILED check, never a pass."""
    unbuilt = gate.unbuilt_level_increases([{"atom": "H39_the_texture", "from": 1, "to": 2}],
                                           {"H39_the_texture": None})
    assert len(unbuilt) == 1 and unbuilt[0]["unverifiable"] is True


def test_daemon_written_output_does_NOT_block_a_level_move():
    """The scoping decision, asserted so it cannot be silently widened back: regenerated publisher
    output and observability state are permanently dirty on this shared tree. If they counted, the
    control would be red for 61 of 209 atoms for reasons the committer cannot fix, and would be
    routed around. Only program text blocks."""
    noise = (" M site/data/dashboard.json\n"
             " M docs/observability/agent_status.json\n"
             " M background/.dispatcher_seen.json\n"
             " M docs/design/BAND_NULL_SWEEP.md\n"
             "?? docs/observability/run_history.json\n")
    assert gate.dirty_source_paths(noise) == []
    # ...but one .py among the noise still fires.
    assert gate.dirty_source_paths(noise + " M background/fabric_gap_ledger.py\n") == [
        "background/fabric_gap_ledger.py"]


def test_ignored_and_rename_entries_are_handled():
    """'!!' is not the commit's business; a rename's DESTINATION is the path that must be clean."""
    assert gate.dirty_source_paths("!! background/ignored_thing.py\n") == []
    assert gate.dirty_source_paths("RM background/old_name.py -> background/new_name.py\n") == [
        "background/new_name.py"]
    assert gate.dirty_source_paths('?? "background/odd name.py"\n') == ["background/odd name.py"]


def test_empty_file_scope_is_a_declared_hole_not_a_silent_pass():
    """53 atoms carry no file_scope. The predicate passes them (nothing to check) -- the CALLER
    reports it; what must never happen is them being counted as verified-clean."""
    assert gate.unbuilt_level_increases([{"atom": "no_scope_atom", "from": 1, "to": 2}], {}) == []
    assert gate.atom_file_scopes("- id: a\n  level_current: 1\n")["a"] == []


def test_atom_file_scopes_reads_the_scope_from_the_map():
    scopes = gate.atom_file_scopes(_scoped_map(2))
    assert scopes["H39_the_texture"] == ["background/fabric_gap_ledger.py",
                                         "tests/harness/test_premise_two_level.py"]


def test_evaluate_exposes_increases_for_the_built_check():
    """main() runs the built-check over evaluate()'s own increase set -- if that key regressed to
    absent, the second control would silently never run (fail-open by omission)."""
    result = gate.evaluate(old_text=_map(2), new_text=_map(3), ledger=[VALID_LEVEL_UP])
    assert result["increases"] == [{"atom": "E4_supplier_reporting_standard", "from": 2, "to": 3}]


# ══════════════════════════════════════════════════════════════════════════════════════════════
# THIRD CONTROL (OPS11): a level may not be RAISED in a lane a live BLOCKING finding holds.
# ══════════════════════════════════════════════════════════════════════════════════════════════
#
# These exercise the PURE predicate with an INJECTED `blockers_for`, so the commit gate's half is
# tested without a staging root on disk. What a blocker IS stays defined in exactly one place
# (`gate_authorization.lane_blockers`, mutation-proven in tests/background/test_gate_authorization
# .py both ways) -- re-deriving it here would be the second copy that drifts.

_LANE_MAP = """- id: H99_thing
  lane: H_harness
  level_current: 1
- id: D9_bill
  lane: D_billing_metering
  level_current: 1
- id: X_no_lane
  level_current: 1
"""

_H_BLOCKER = gate.LaneBlocker("H_harness", "WORKER_FINDING_THE_INSTRUMENT_LIES.md",
                              "docs/staging/WORKER_FINDING_THE_INSTRUMENT_LIES.md",
                              "BLOCKING in H_harness")


def _blockers_only_in_h(lane):
    return [_H_BLOCKER] if lane == "H_harness" else []


def test_atom_lane_names_reads_the_lane_off_the_staged_map():
    lanes = gate.atom_lane_names(_LANE_MAP)
    assert lanes["H99_thing"] == "H_harness" and lanes["D9_bill"] == "D_billing_metering"
    assert lanes.get("X_no_lane") is None  # no `lane` key -> unknown, never a silent default


def test_a_raise_in_a_HELD_lane_is_REFUSED_and_names_the_finding():
    """(a) THE named defect. Exit criterion 1: the refusal must say which finding blocks it and
    where it lives, or nobody can discharge it."""
    held = gate.lane_blocked_level_increases(
        [{"atom": "H99_thing", "from": 1, "to": 2}], gate.atom_lane_names(_LANE_MAP),
        _blockers_only_in_h)
    assert len(held) == 1 and held[0]["lane"] == "H_harness"
    described = held[0]["blockers"][0].describe()
    assert "WORKER_FINDING_THE_INSTRUMENT_LIES.md" in described
    assert "docs/staging/WORKER_FINDING_THE_INSTRUMENT_LIES.md" in described


def test_a_raise_in_an_UNHELD_lane_PASSES_while_the_other_lane_is_held():
    """(b) THE PASSING DIRECTION, and exit criterion 2's second half in the gate: the SAME
    blocker set that refuses H_harness leaves D_billing_metering alone, in one call, so the
    lane bound is proven rather than the two directions being separately arranged."""
    both = [{"atom": "H99_thing", "from": 1, "to": 2}, {"atom": "D9_bill", "from": 1, "to": 2}]
    held = gate.lane_blocked_level_increases(both, gate.atom_lane_names(_LANE_MAP),
                                             _blockers_only_in_h)
    assert [h["atom"] for h in held] == ["H99_thing"]


def test_a_wholly_clean_severity_index_blocks_NOTHING():
    """The commonest case of all: no BLOCKING findings anywhere -> every lane raises freely.
    A control that cannot pass is worth nothing (`feedback_control_that_can_only_fail_wedges`)."""
    both = [{"atom": "H99_thing", "from": 1, "to": 2}, {"atom": "D9_bill", "from": 1, "to": 2}]
    assert gate.lane_blocked_level_increases(both, gate.atom_lane_names(_LANE_MAP),
                                             lambda lane: []) == []


def test_neuter_no_blockers_turns_the_defect_test_RED():
    """(c) INDEPENDENCE: with the blocker source neutered, (a)'s assertion collapses -- so (a)
    is carried by the predicate and not by the fixture's shape."""
    assert gate.lane_blocked_level_increases(
        [{"atom": "H99_thing", "from": 1, "to": 2}], gate.atom_lane_names(_LANE_MAP),
        lambda lane: []) == []


def test_an_atom_with_no_lane_is_refused_under_UNKNOWN_LANE():
    """FAIL-CLOSED. An atom the staged map gives no lane cannot be shown to be in a clear lane,
    and an unavailable check is a FAILED check (R15). The refusal is dischargeable by
    record-and-accept exactly like any other, so it holds without wedging."""
    held = gate.lane_blocked_level_increases(
        [{"atom": "X_no_lane", "from": 1, "to": 2}], gate.atom_lane_names(_LANE_MAP),
        lambda lane: [])  # even with a totally clean index
    assert len(held) == 1 and held[0]["lane"] == gate.UNKNOWN_LANE
    assert gate.UNREADABLE_INDEX_FINDING in held[0]["blockers"][0].finding


def test_one_lane_is_scanned_ONCE_however_many_atoms_it_holds():
    """Not a micro-optimisation: `lane_blockers` walks the whole staging root, so a per-atom
    call would turn a ten-atom commit into ten filesystem scans inside a pre-commit hook."""
    calls = []

    def counting(lane):
        calls.append(lane)
        return []

    gate.lane_blocked_level_increases(
        [{"atom": "H99_thing", "from": 1, "to": 2}, {"atom": "H99_thing", "from": 2, "to": 3},
         {"atom": "D9_bill", "from": 1, "to": 2}], gate.atom_lane_names(_LANE_MAP), counting)
    assert calls == ["H_harness", "D_billing_metering"]


# ═══════════════════════════════════════════════════════════════════════════════════════════════
# FIFTH CONTROL (2026-09-09): ABSENT EVIDENCE + the MINIMUM LANDABLE UNIT in the refusal.
# ═══════════════════════════════════════════════════════════════════════════════════════════════
_ABSENT_SCOPES = {"B3_forecast": ["sim/forecast_publication.py", "tests/sim/test_forecast.py"]}
_B3 = [{"atom": "B3_forecast", "from": 0, "to": 1}]


def test_evidence_ABSENT_from_the_commit_tree_REFUSES_the_increase():
    """(a) THE named defect: the raise declares a level for evidence that is in no tree at all --
    not at HEAD, not in the index. This is the test the neuter must turn RED."""
    absent = gate.absent_evidence_increases(
        _B3, _ABSENT_SCOPES, {"sim/forecast_publication.py": False, "tests/sim/test_forecast.py": False})
    assert len(absent) == 1
    assert absent[0]["absent"] == ["sim/forecast_publication.py", "tests/sim/test_forecast.py"]
    assert absent[0]["unverifiable"] is False


def test_the_absent_path_is_INVISIBLE_to_the_dirty_check_so_this_is_not_an_equivalence():
    """THE GENERATOR, asserted directly so this control can never be mistaken for a restatement of
    the SECOND one. `git status --porcelain -- <path that exists nowhere>` exits 0 with NO output,
    measured on the live tree 2026-09-09. The dirty predicate therefore reads the B3 raise CLEAN,
    and only the absence predicate refuses it -- which is the whole reason the fifth control
    exists. If a future edit made `unbuilt_level_increases` catch this, the two would be the same
    control wearing two names and one of them should go."""
    assert gate.dirty_source_paths("") == []
    assert gate.unbuilt_level_increases(_B3, {"B3_forecast": ""}) == []   # the fail-open, live
    assert gate.absent_evidence_increases(                                # what actually catches it
        _B3, _ABSENT_SCOPES, {"sim/forecast_publication.py": False,
                              "tests/sim/test_forecast.py": False}) != []


def test_evidence_PRESENT_ALLOWS_the_increase():
    """(b) THE PASSING DIRECTION, and the reason this control is passable at all: measured over
    all 348 atoms, every row carrying an absent file_scope path stands at level_current 0, so an
    ordinary raise on landed evidence sails through. A path already at HEAD and a path landing in
    THIS commit are both `present` -- the index is the tree the commit creates."""
    assert gate.absent_evidence_increases(
        _B3, _ABSENT_SCOPES, {"sim/forecast_publication.py": True,
                              "tests/sim/test_forecast.py": True}) == []


def test_neuter_everything_present_turns_the_defect_test_RED():
    """(c) INDEPENDENCE: replace the presence probe with one that finds everything (the fail-open
    mutation) and the (a) assertion collapses -- so (a) is really carried by the predicate."""
    all_present = dict.fromkeys(_ABSENT_SCOPES["B3_forecast"], True)
    assert gate.absent_evidence_increases(_B3, _ABSENT_SCOPES, all_present) == []
    # restored: the real answer refuses again
    assert gate.absent_evidence_increases(
        _B3, _ABSENT_SCOPES, dict.fromkeys(_ABSENT_SCOPES["B3_forecast"], False)) != []


def test_the_absence_probe_FAILING_is_a_refusal_not_a_pass():
    """R15 fail-silent: an unavailable check is a FAILED check. `presence` None is the probe
    itself failing, which is not evidence that the evidence is there."""
    out = gate.absent_evidence_increases(_B3, _ABSENT_SCOPES, None)
    assert len(out) == 1 and out[0]["unverifiable"] is True and out[0]["absent"] == []


def test_the_whole_partition_is_REACHABLE_not_only_the_refusing_leg():
    """ONE control over all three outcomes, because a predicate that refuses EVERYTHING passes
    every refusal test above and a predicate that refuses NOTHING passes the clean one. Both
    directions and the fail-closed middle have to be reachable from the same predicate."""
    scopes = _ABSENT_SCOPES
    refuses = gate.absent_evidence_increases(_B3, scopes, dict.fromkeys(scopes["B3_forecast"], False))
    clears = gate.absent_evidence_increases(_B3, scopes, dict.fromkeys(scopes["B3_forecast"], True))
    cannot_tell = gate.absent_evidence_increases(_B3, scopes, None)
    assert refuses and not clears and cannot_tell


def test_an_atom_with_no_file_scope_is_the_DECLARED_hole_not_a_second_silent_one():
    """53 atoms carry an empty file_scope. They pass here for the same stated reason they pass the
    built-check -- there is nothing to look for -- and `main()` prints that hole on stderr."""
    assert gate.absent_evidence_increases(_B3, {"B3_forecast": []}, {}) == []
    assert gate.absent_evidence_increases(_B3, {}, {}) == []


# ── the minimum landable unit ────────────────────────────────────────────────────────────────
def test_a_NEGATED_exists_is_NOT_in_the_minimum_landable_unit():
    """THE INVERSION, and the reason this is an AST walk and not a grep. `assert not (REPO /
    "saas" / "demand_response.py").exists()` asserts the path is GONE. A grep would put it in the
    set of paths the commit must CONTAIN, i.e. demand the opposite of the control it came from --
    and `tests/architecture/test_demand_response_is_world_physics.py` carries exactly that line."""
    src = ('from pathlib import Path\nR = Path(".")\n'
           'def t():\n    assert not (R / "saas" / "demand_response.py").exists()\n')
    assert gate.exists_cited_paths(src) == []
    positive = src.replace("assert not (", "assert (")
    assert gate.exists_cited_paths(positive) == ["saas/demand_response.py"]


def test_the_rejoined_path_is_read_in_SOURCE_order():
    """`R / "saas" / "demand_response.py"` is a left-leaning BinOp chain, and `ast.walk`'s
    breadth-first order returns its parts REVERSED -- rejoining that yields
    `demand_response.py/saas`, which matches no path, silently turning the whole multi-component
    leg into a no-op that still looks implemented."""
    assert gate._path_literals(
        __import__("ast").parse('R / "saas" / "demand_response.py"').body[0].value
    ) == ["saas", "demand_response.py"]


def test_a_module_level_constant_path_is_recovered():
    """The dominant real shape: measured over all 1,693 controls in the tree, the inline-literal
    rule alone found 6 citations; resolving module-level constants found 10. `PAGE = PROJECT /
    "..."` at the top and `PAGE.exists()` in the body is how these are actually written."""
    src = ('from pathlib import Path\nPROJECT = Path(".")\n'
           'PAGE = PROJECT / "site/ladder/index.html"\ndef t():\n    assert PAGE.exists()\n')
    assert gate.exists_cited_paths(src) == ["site/ladder/index.html"]


def test_a_runtime_computed_citation_is_the_stated_hole_not_a_crash():
    """`(project / path).exists()` over a loop variable yields nothing -- the printed unit is a
    FLOOR on what the commit needs and never a ceiling, which is why this is a report and not a
    predicate. Unparseable source contributes nothing rather than raising into a pre-commit hook."""
    assert gate.exists_cited_paths(
        'def t():\n    for p in x:\n        assert (project / p).exists()\n') == []
    assert gate.exists_cited_paths("def t(:\n  syntax error") == []


def test_the_minimum_landable_unit_names_all_THREE_sources():
    """§(b): file_scope, the row's PROSE citations, and a control's `.exists()` citation. The
    incident that produced this recovered its four paths by hand-reading a thirty-line YAML
    comment -- the prose leg is the one that reads that comment. Measured on the live map: 31 of
    348 atoms get a wider unit than their file_scope, recovering 54 paths nothing else names."""
    row = {"id": "X", "level_current": 1,
           "file_scope": ["tools/thing.py"],
           "block_reason": "waiting on docs/staging/SEAT_FINDING_A_THING_2026-09-01.md to discharge"}
    unit = gate.minimum_landable_unit(
        ["tools/thing.py"], row,
        {"tools/thing.py": 'from pathlib import Path\nP = Path(".") / "site/data/world.json"\n'
                           'def t():\n    assert P.exists()\n'})
    assert unit == ["docs/staging/SEAT_FINDING_A_THING_2026-09-01.md",
                    "site/data/world.json", "tools/thing.py"]


def test_the_unit_is_WIDER_than_the_refusal_and_that_is_the_scoping_decision():
    """KEYED TO THE PROPERTY: the refusal is over `file_scope`; the PRINTED unit is over all three
    sources. Measured 2026-09-09: KNIFE3_wall_crossing_paydown's prose cites
    `sim/cache/elexon_ssp_full.json`, which is not tracked -- so a refusal keyed to the wider unit
    would wedge that atom permanently, which is the control-that-cannot-pass shape this project
    routes around within a day. A report cannot wedge anything."""
    scopes = {"X": ["tools/thing.py"]}
    incs = [{"atom": "X", "from": 1, "to": 2}]
    # the prose-cited path is absent, the file_scope path is present -> NO refusal
    assert gate.absent_evidence_increases(incs, scopes, {"tools/thing.py": True}) == []
    # ...but it is still printed, marked MISSING, so the reader sees it
    rendered = gate.format_minimum_landable_unit(
        ["docs/staging/GONE.md", "tools/thing.py"],
        {"docs/staging/GONE.md": False, "tools/thing.py": True})
    assert "[MISSING] docs/staging/GONE.md" in rendered
    assert "[present] tools/thing.py" in rendered


def test_the_unit_says_UNKNOWN_when_the_probe_failed_rather_than_guessing():
    """A failed probe must not render as `present` (a fail-open the reader would act on) nor as
    `MISSING` (sending them to land a path that is already there)."""
    assert gate.format_minimum_landable_unit(["a/b.py"], None).strip() == "[?] a/b.py"
    assert "declares no file_scope" in gate.format_minimum_landable_unit([], {})


def test_cited_paths_reads_prose_and_ignores_the_file_scope_key():
    """The row's own file_scope is passed separately, so counting it twice from the prose walk
    would make the two legs indistinguishable in the printed unit."""
    assert gate.cited_paths("see tools/a.py and docs/design/B_2026-01-01.md, not a.out") == [
        "docs/design/B_2026-01-01.md", "tools/a.py"]
    assert gate.row_cited_paths({"file_scope": ["tools/only_here.py"],
                                 "note": "cites tools/in_prose.py"}) == ["tools/in_prose.py"]


def test_a_DIRECTORY_file_scope_entry_is_present_when_the_tree_holds_files_under_it():
    """THE MEASUREMENT THAT DECIDED THE PROBE (real git, read-only). 106 of the map's file_scope
    entries are directories. An exact-match membership test reads all 106 as absent and this
    control becomes unpassable; the prefix test reads 20, every one of them genuinely absent."""
    got = gate._tracked_in_commit(["tools", "tools/level_promotion_gate.py",
                                   "sim/forecast_publication.py"])
    assert got == {"tools": True, "tools/level_promotion_gate.py": True,
                   "sim/forecast_publication.py": False}
    assert gate._tracked_in_commit([]) == {}


def test_atom_rows_returns_the_whole_row_not_only_its_level():
    """The unit is computed over the WHOLE row: a level's evidence is cited in prose at least as
    often as it is declared in file_scope."""
    rows = gate.atom_rows(_SCOPED_MAP.format(lvl=2))
    assert set(rows) == {"H39_the_texture"}
    assert rows["H39_the_texture"]["level_current"] == 2
    assert rows["H39_the_texture"]["file_scope"]


# ── the size warning on the surface this gate already owns ───────────────────────────────────
#
# SEAT_FINDING_THE_MAP_IS_185_BYTES_FROM_ITS_RATCHET_CEILING_2026-09-17. The gate is where the
# warning goes because it already holds the staged bytes of BOTH halves and already runs on
# exactly the commits that move a row. The two defects these guard are the ones that would make
# it worse than nothing: a warning that never reaches the author (the finding), and a warning
# that refuses (a second ratchet under a softer name, on a number this gate has no authority
# over -- and the level move it exists to record would then be blocked by the map's SIZE).
def _gate_main_over(monkeypatch, map_text: str) -> tuple[int, str]:
    """Drive main() with a staged map of our choosing and no level change at all, so the only
    thing it can possibly print is the size line.

    `low_water_failures` is stubbed to CLEAN deliberately, and not to make anything pass: it reads
    the retired register out of git and fail-closes when it cannot, so in any tree without a `.git`
    (a `git archive` extract, which is how a landing gates itself) HEAD's own gate returns 1 for a
    reason that has nothing to do with the size warning. Measured: HEAD's unmodified gate refuses in
    such a tree with "the staged copy could not be read". A test whose subject is the warning must
    not be answerable by a different control's git dependency."""
    monkeypatch.setattr(gate, "_staged_names", lambda: {gate.MAP_REL})
    monkeypatch.setattr(gate, "_whole_map", lambda rev_prefix: map_text)
    monkeypatch.setattr(gate, "read_ledger", lambda: [])
    monkeypatch.setattr(gate, "low_water_failures", lambda **kw: [])
    err: list[str] = []
    monkeypatch.setattr(gate.sys.stderr, "write", err.append)
    return gate.main(), "".join(err)


def _map_of_bytes(n: int) -> str:
    """A parseable one-atom map padded with comment bytes to exactly `n` bytes."""
    body = _map(2)
    return body + "#" + "x" * (n - len(body.encode("utf-8")) - 2) + "\n"


def test_the_gate_PRINTS_the_headroom_on_a_commit_it_ALLOWS(monkeypatch):
    """The finding in one line: the author of the row that still fits must hear the number while
    there is room to act on it."""
    from tools import maturity_map_store as map_store

    inside = map_store.MAP_SIZE_CEILING - (map_store.MAP_SIZE_WARN_HEADROOM // 2)
    rc, err = _gate_main_over(monkeypatch, _map_of_bytes(inside))
    assert rc == 0, "the size warning changed the exit code -- it is advisory, never a refusal"
    assert "[map-size]" in err and "headroom" in err


def test_the_gate_is_SILENT_about_size_when_the_map_has_room(monkeypatch):
    """Not an equivalence: the same call path with a small map must say nothing, or the test above
    is passing on a line the gate prints unconditionally."""
    rc, err = _gate_main_over(monkeypatch, _map(2))
    assert rc == 0
    assert "[map-size]" not in err, f"warned with the whole ceiling free: {err}"


def test_a_map_OVER_the_ceiling_is_still_ALLOWED_by_THIS_gate(monkeypatch):
    """The boundary of this gate's authority, asserted so nobody later 'strengthens' the warning
    into a refusal. The ratchet in tests/design/ refuses an oversized map; if this gate refused
    too, a lane whose only crime was recording a level would meet two reds for one cause, and the
    one that named the remedy is not this one."""
    from tools import maturity_map_store as map_store

    rc, err = _gate_main_over(monkeypatch, _map_of_bytes(map_store.MAP_SIZE_CEILING + 500))
    assert rc == 0, "the gate refused a commit for the map's SIZE -- not its subject"
    assert "OVER" in err and "EVERY LANE" in err
