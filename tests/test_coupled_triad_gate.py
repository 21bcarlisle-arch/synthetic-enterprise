"""Tests for the COUPLED-TRIAD draw-coupling gate (binding rule 1).

Covers background/coupled_triad.py: the coupling derivation + cross-check, the
gap-ledger contract, and world_l3_blocked's block/allow decisions. Uses a tmp
ledger path -- NEVER writes into the real docs/observability/coupled_gap_ledger.json.
"""

import json

import pytest

from background import coupled_triad as ct


# --- Minimal in-memory atom sets (mirror maturity_map.yaml shape) ------------

def _world_atom(atom_id="W2_7_willingness_classification", lc=2, lt=3,
                lane="W2_customer_generator"):
    return {"id": atom_id, "lane": lane, "level_current": lc, "level_target": lt,
            "loop_stage": "build", "depends_on": []}


def _twin_atom(atom_id="C9_cantpay_wontpay_classifier", lc=1, lt=3,
               world_dep="W2_7_willingness_classification"):
    return {"id": atom_id, "lane": "C_customer_ops", "level_current": lc,
            "level_target": lt, "loop_stage": "build",
            "depends_on": [world_dep, "A6_coupled_triad_gap_metric"]}


def _atoms(world_lc=2, twin_lc=1):
    return [_world_atom(lc=world_lc), _twin_atom(lc=twin_lc)]


def _write_ledger(tmp_path, obj):
    p = tmp_path / "coupled_gap_ledger.json"
    p.write_text(json.dumps(obj), encoding="utf-8")
    return p


# --- Coupling derivation + cross-check ---------------------------------------

def test_coupling_derived_from_map_matches_authoritative():
    atoms = [
        _twin_atom("C9_cantpay_wontpay_classifier", world_dep="W2_7_willingness_classification"),
        _twin_atom("C10_self_rationing_detection", world_dep="W2_8_self_rationing"),
        _world_atom("W2_7_willingness_classification"),
        _world_atom("W2_8_self_rationing"),
    ]
    coupling = ct.build_coupling(atoms)
    assert coupling["W2_7_willingness_classification"] == "C9_cantpay_wontpay_classifier"
    assert coupling["W2_8_self_rationing"] == "C10_self_rationing_detection"


def test_coupling_disagreement_raises():
    # Map wires C9 to the WRONG world atom -> must raise (task: "raise if they disagree").
    atoms = [
        _twin_atom("C9_cantpay_wontpay_classifier", world_dep="W2_8_self_rationing"),
        _world_atom("W2_8_self_rationing"),
    ]
    with pytest.raises(ValueError):
        ct.build_coupling(atoms)


def test_live_map_coupling_has_all_seven_pairs():
    # The real map must load clean and expose all 7 authoritative pairs.
    assert ct.COUPLING["W2_7_willingness_classification"] == "C9_cantpay_wontpay_classifier"
    assert ct.COUPLING["W2_9_segment_debt_tnc"] == "C11_segment_debt_policy"
    assert len([k for k in ct.COUPLING if k.startswith("W2_")]) == 7


# --- Gap ledger contract -----------------------------------------------------

def test_load_gap_ledger_missing_file_is_empty(tmp_path):
    assert ct.load_gap_ledger(tmp_path / "nope.json") == {}


def test_gap_measured_true_only_for_nonnull_numeric(tmp_path):
    ledger = {
        "W2_7_willingness_classification": {"twin_atom_id": "C9", "gap": 0.62},
        "W2_8_self_rationing": {"twin_atom_id": "C10", "gap": None},
    }
    assert ct.gap_measured("W2_7_willingness_classification", ledger) is True
    assert ct.gap_measured("W2_8_self_rationing", ledger) is False   # null gap
    assert ct.gap_measured("W2_6_sme_distress_twin", ledger) is False  # absent


def test_gap_measured_rejects_boolean_gap():
    # bool is an int subclass; a boolean gap is malformed, not a measurement.
    ledger = {"W2_7_willingness_classification": {"gap": True}}
    assert ct.gap_measured("W2_7_willingness_classification", ledger) is False


# --- world_l3_blocked: the gate ----------------------------------------------

def test_world_l3_blocked_when_no_gap_entry(tmp_path):
    atoms = _atoms(world_lc=2, twin_lc=1)
    ledger = ct.load_gap_ledger(_write_ledger(tmp_path, {}))
    blocked, reason = ct.world_l3_blocked(atoms[0], atoms, ledger)
    assert blocked is True
    assert "gap" in reason.lower()


def test_world_l3_allowed_when_gap_measured_and_twin_ready(tmp_path):
    atoms = _atoms(world_lc=2, twin_lc=1)
    ledger = ct.load_gap_ledger(_write_ledger(tmp_path, {
        "W2_7_willingness_classification": {
            "twin_atom_id": "C9_cantpay_wontpay_classifier",
            "gap": 0.62, "measured_at": "2026-07-13T00:00:00Z",
            "run_git_commit": "deadbeef", "baseline": "always-predict-majority",
        }
    }))
    blocked, reason = ct.world_l3_blocked(atoms[0], atoms, ledger)
    assert blocked is False


def test_world_targeting_only_l2_never_blocked(tmp_path):
    world = _world_atom(lc=1, lt=2)          # aims at L2, not L3
    atoms = [world, _twin_atom(lc=0)]        # twin unbuilt, gap unmeasured
    ledger = ct.load_gap_ledger(_write_ledger(tmp_path, {}))
    blocked, _ = ct.world_l3_blocked(world, atoms, ledger)
    assert blocked is False


def test_world_below_l2_boundary_builds_freely(tmp_path):
    # lc=0, lt=3: next step targets L1 (<3) -> free to build toward L2.
    world = _world_atom(lc=0, lt=3)
    atoms = [world, _twin_atom(lc=0)]
    ledger = ct.load_gap_ledger(_write_ledger(tmp_path, {}))
    blocked, _ = ct.world_l3_blocked(world, atoms, ledger)
    assert blocked is False


def test_company_atom_never_blocked_by_this_gate(tmp_path):
    twin = _twin_atom(lc=0, lt=3)
    atoms = [_world_atom(lc=2), twin]
    ledger = ct.load_gap_ledger(_write_ledger(tmp_path, {}))
    blocked, reason = ct.world_l3_blocked(twin, atoms, ledger)
    assert blocked is False
    assert "not a world atom" in reason


def test_world_blocked_when_twin_missing(tmp_path):
    world = _world_atom(lc=2, lt=3)
    atoms = [world]                          # no twin registered at all
    ledger = ct.load_gap_ledger(_write_ledger(tmp_path, {}))
    blocked, reason = ct.world_l3_blocked(world, atoms, ledger)
    assert blocked is True
    assert "twin" in reason.lower()


def test_world_blocked_when_twin_below_l1(tmp_path):
    atoms = _atoms(world_lc=2, twin_lc=0)    # twin exists but unbuilt (lc=0<1)
    ledger = ct.load_gap_ledger(_write_ledger(tmp_path, {
        "W2_7_willingness_classification": {"gap": 0.5}  # gap measured...
    }))
    blocked, reason = ct.world_l3_blocked(atoms[0], atoms, ledger)
    assert blocked is True                   # ...but twin not ready -> still blocked
    assert "C9" in reason


def test_real_ledger_ships_empty():
    # The shipped ledger must be an empty object -- no fabricated gaps.
    data = json.loads(ct.GAP_LEDGER_PATH.read_text(encoding="utf-8"))
    assert data == {}
