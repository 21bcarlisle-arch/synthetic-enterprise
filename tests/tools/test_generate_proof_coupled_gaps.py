"""Tests for the COUPLED-TRIAD Proof-door panel data
(tools/generate_proof_data.py::_coupled_gaps).

The panel is a CONTROL surface (COUPLED_TRIAD_DESIGN.md 5.2, "the gap between
what the world knows and what the company believes"). Per R15 a control counts
as evidence only if a MUTATION TEST proves it FIRES on its own named defect, and
it must not be a tautology (the rendered value must come from an INDEPENDENT
source -- the harness gap ledger -- not be recomputed here), nor fail-open (an
empty/absent ledger must fail CLOSED and show untested pairs, never a silently
empty panel).

Named defects this panel must fire on:
  D1  a coupled world atom >=L2 with NO measured gap ("depth nobody copes with
      yet" -- the binding-rule-1 failure mode) -> shown untested/amber, counted.
  D2  a gap of exactly 0 (observables leaked theta -- an epistemic-wall breach)
      -> shown "leak"/red, NOT a triumph.
  D3  a gap > 1 (the company is worse than blind) -> shown red.
  D4  an empty/unavailable ledger -> fail CLOSED: every coupled pair still
      appears, marked untested; the panel is never silently empty.
"""

from __future__ import annotations

import copy

import yaml

import tools.generate_proof_data as gpd
import background.coupled_triad as ct

MATURITY_MAP = gpd.MATURITY_MAP_YAML


def _atoms():
    return yaml.safe_load(MATURITY_MAP.read_text())


def _real_ledger():
    return ct.load_gap_ledger()


# ---------------------------------------------------------------------------
# Faithfulness / independence (tautology guard)
# ---------------------------------------------------------------------------
def test_reflects_real_ledger_exactly():
    atoms = _atoms()
    ledger = _real_ledger()
    cg = gpd._coupled_gaps(atoms)
    assert cg["available"] is True
    # 8 map-coupled W2 pairs + W1_5<->C13 + W1_6<->C13 (both wired into
    # _AUTHORITATIVE_COUPLING; W1_6 promoted 2026-07-21 by director console "wire
    # the ledger pair") = 10 map pairs, all measured. Count is DERIVED from the
    # authoritative coupling registry, never a frozen literal.
    n_map = len(ct.build_coupling(atoms))
    assert cg["pair_count"] == n_map
    assert cg["measured"] == n_map
    assert cg["unmeasured"] == 0
    # Every rendered value is the ledger's value -- read, not recomputed.
    by_world = {r["world_atom"]: r for r in cg["pairs"]}
    for world_id, entry in ledger.items():
        assert world_id in by_world, f"{world_id} missing from panel"
        assert by_world[world_id]["value"] == entry["gap"]
        assert by_world[world_id]["metric"] == entry.get("metric")
        assert by_world[world_id]["company_atom"] == entry.get("twin_atom_id")


def test_value_tracks_a_mutated_ledger(monkeypatch):
    """Independence: if the harness measured a DIFFERENT gap, the panel shows the
    different gap. A stuck value that ignores the ledger would be a tautology."""
    atoms = _atoms()
    mutated = copy.deepcopy(_real_ledger())
    mutated["W2_7_willingness_classification"]["gap"] = 0.42
    monkeypatch.setattr(ct, "load_gap_ledger", lambda *a, **k: mutated)
    cg = gpd._coupled_gaps(atoms)
    row = next(r for r in cg["pairs"] if r["world_atom"] == "W2_7_willingness_classification")
    assert row["value"] == 0.42


# ---------------------------------------------------------------------------
# D1: unmeasured coupled pair (depth nobody copes with) -> fires amber/untested
# ---------------------------------------------------------------------------
def test_null_gap_fires_untested_and_counts(monkeypatch):
    atoms = _atoms()
    mutated = copy.deepcopy(_real_ledger())
    mutated["W2_7_willingness_classification"]["gap"] = None
    monkeypatch.setattr(ct, "load_gap_ledger", lambda *a, **k: mutated)
    cg = gpd._coupled_gaps(atoms)
    row = next(r for r in cg["pairs"] if r["world_atom"] == "W2_7_willingness_classification")
    assert row["value"] is None
    assert row["chip"] == "untested"
    assert row["severity"] == "amber"
    total = len(ct.build_coupling(atoms))
    assert cg["measured"] == total - 1   # all live pairs but the nulled W2_7
    assert cg["unmeasured"] == 1
    # W2_7 sits at L3 (>=L2) in the map -> anti-decay list flags it.
    assert "W2_7_willingness_classification" in cg["unmeasured_ge_l2"]


def test_missing_entry_still_appears_untested(monkeypatch):
    atoms = _atoms()
    mutated = copy.deepcopy(_real_ledger())
    del mutated["W2_8_self_rationing"]
    monkeypatch.setattr(ct, "load_gap_ledger", lambda *a, **k: mutated)
    cg = gpd._coupled_gaps(atoms)
    # W2_8 still appears (map coupling, now untested); W1_5 and W1_6 both appear
    # (map coupling). The pair count is the map-coupled count regardless of which
    # ledger entries are missing -- deleting a ledger entry marks a pair untested,
    # it never drops the pair (fail-closed).
    assert cg["pair_count"] == len(ct.build_coupling(atoms))
    row = next(r for r in cg["pairs"] if r["world_atom"] == "W2_8_self_rationing")
    assert row["value"] is None
    assert row["chip"] == "untested"


def test_boolean_gap_treated_as_malformed(monkeypatch):
    atoms = _atoms()
    mutated = copy.deepcopy(_real_ledger())
    mutated["W2_5_life_event_stream"]["gap"] = True  # bool is not a measurement
    monkeypatch.setattr(ct, "load_gap_ledger", lambda *a, **k: mutated)
    cg = gpd._coupled_gaps(atoms)
    row = next(r for r in cg["pairs"] if r["world_atom"] == "W2_5_life_event_stream")
    assert row["value"] is None
    assert row["chip"] == "untested"


# ---------------------------------------------------------------------------
# D2: gap == 0 is an epistemic-wall LEAK, not a triumph -> fires red
# ---------------------------------------------------------------------------
def test_zero_gap_fires_leak_red(monkeypatch):
    atoms = _atoms()
    mutated = copy.deepcopy(_real_ledger())
    mutated["W2_4_household_budget"]["gap"] = 0.0
    monkeypatch.setattr(ct, "load_gap_ledger", lambda *a, **k: mutated)
    cg = gpd._coupled_gaps(atoms)
    row = next(r for r in cg["pairs"] if r["world_atom"] == "W2_4_household_budget")
    assert row["chip"] == "leak"
    assert row["severity"] == "red"
    assert cg["wall_leak_count"] == 1


# ---------------------------------------------------------------------------
# D3: gap > 1 -> worse than blind -> fires red
# ---------------------------------------------------------------------------
def test_gap_above_one_fires_worse_than_blind(monkeypatch):
    atoms = _atoms()
    mutated = copy.deepcopy(_real_ledger())
    mutated["W2_6_sme_distress_twin"]["gap"] = 1.5
    monkeypatch.setattr(ct, "load_gap_ledger", lambda *a, **k: mutated)
    cg = gpd._coupled_gaps(atoms)
    row = next(r for r in cg["pairs"] if r["world_atom"] == "W2_6_sme_distress_twin")
    assert row["chip"] == "worse_than_blind"
    assert row["severity"] == "red"
    # The mutated W2_6 is counted worse-than-blind. (>=1 not ==1: the live ledger also
    # carries W1_5<->C13 at a real worst-cell gap>1, so the aggregate is data-driven.)
    assert cg["worse_than_blind_count"] >= 1
    assert row["world_atom"] in {p["world_atom"] for p in cg["pairs"]
                                 if isinstance(p["value"], (int, float)) and p["value"] > 1}


# ---------------------------------------------------------------------------
# D4: empty / unavailable ledger -> FAIL CLOSED (pairs still shown untested)
# ---------------------------------------------------------------------------
def test_empty_ledger_fails_closed_not_silent(monkeypatch):
    atoms = _atoms()
    monkeypatch.setattr(ct, "load_gap_ledger", lambda *a, **k: {})
    cg = gpd._coupled_gaps(atoms)
    assert cg["available"] is True
    # Every MAP-coupled pair still present on an empty ledger (fail-closed, shown
    # untested). Since W1_6<->C13 was promoted into _AUTHORITATIVE_COUPLING
    # (2026-07-21, "wire the ledger pair"), it too now survives an empty ledger --
    # it no longer silently drops via the old ledger-only defensive branch. The
    # count is the map-coupled count, derived from the coupling registry.
    n_map = len(ct.build_coupling(atoms))
    assert cg["pair_count"] == n_map      # every MAP-coupled pair still present
    assert cg["measured"] == 0            # none measured
    assert cg["unmeasured"] == n_map
    assert all(r["chip"] == "untested" for r in cg["pairs"])
    # Anti-decay set (design 5.1): every coupled world atom that is mechanically
    # real (>=L2) but unmeasured. On an empty ledger that is EXACTLY the map-coupled
    # world atoms sitting >=L2 -- derived from the live map levels, not a frozen
    # count (the old literal 8 went stale twice: W1_5 was ratified to L3, and W1_6
    # was wired in).
    by_id = {a["id"]: a for a in atoms if isinstance(a, dict) and a.get("id")}
    ge_l2_world = {
        w for w in ct.build_coupling(atoms)
        if isinstance(by_id.get(w, {}).get("level_current"), int)
        and by_id[w]["level_current"] >= 2
    }
    assert set(cg["unmeasured_ge_l2"]) == ge_l2_world


# ---------------------------------------------------------------------------
# blocks_l3 mirrors the live BUILD draw gate (panel cannot drift from mechanism)
# ---------------------------------------------------------------------------
def test_blocks_l3_reflects_live_gate_and_panel_row(monkeypatch):
    # A real coupled pair (W2_7 <-> C9) rewound to L2 -> L3 with an EMPTY gap
    # ledger: the draw gate must block its L3 step (unmeasured gap), and the
    # panel's blocks_l3 field for that row must mirror the gate exactly.
    atoms = [
        dict(id="W2_7_willingness_classification", name="willingness",
             lane="W2_customer_generator", level_current=2, level_target=3,
             depends_on=[]),
        dict(id="C9_cantpay_wontpay_classifier", name="cant/wont classifier",
             lane="C_customer_ops", level_current=2, level_target=3,
             depends_on=["W2_7_willingness_classification"]),
    ]
    monkeypatch.setattr(ct, "load_gap_ledger", lambda *a, **k: {})
    blocked, reason = ct.world_l3_blocked(atoms[0], atoms, {})
    assert blocked is True
    assert "unmeasured" in reason.lower()
    # And the panel row for the same pair reports blocks_l3 True.
    cg = gpd._coupled_gaps(atoms)
    row = next(r for r in cg["pairs"]
               if r["world_atom"] == "W2_7_willingness_classification")
    assert row["blocks_l3"] is True
    assert cg["blocks_l3_count"] == 1
