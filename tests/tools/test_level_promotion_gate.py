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


VALID_LEVEL_UP = {
    "atom": "E4_supplier_reporting_standard", "action": "LEVEL_UP_PROPOSED", "level": 3,
    "authorized_by": "director", "channel": "console",
    "provenance": "director console message 2026-07-18: 'E4 -> L3 approved -- move the cell.'",
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
    assert "no director LEVEL_UP authorization" in result["message"]
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
