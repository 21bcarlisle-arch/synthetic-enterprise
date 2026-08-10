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
