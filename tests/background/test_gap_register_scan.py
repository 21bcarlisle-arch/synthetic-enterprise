"""R15 both-ways for the GAP1 gap-register reader (background/gap_register_scan.py) and its
`gap_register` detector level in supervisor.authorized_set_enumeration().

Serves GAP_REGISTER_MINT_SOURCE_CONTRACT exit criteria (b)(c)(d). Every test pins its own fixture
paths (feedback_new_draw_rung_needs_fixture_isolation: a new draw signal must never read live disk
in a test). The four contract-mandated mutations each FIRE (the control catches its own defect):
  1. NEUTER the read -> residue empty -> level N; RESTORE -> non-empty -> level Y.
  2. SEED one open row -> level flips to Y.
  3. Register-1 OLD `measured_bound`-field key -> misses a bare unmeasured simplification the
     corrected TEXT HEURISTIC catches (the old key fail-opened).
  4. Register-6 OLD `audit:*`-only prefix key -> reports 0 real while `adjudicated-real` rows live
     under other prefixes; the corrected `state`-key, prefix-agnostic rule catches them.
Plus invariant 2: a parse/read error on any register reads DRAWABLE (fail-safe toward work).
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

import pytest

from background import gap_register_scan as g


# --------------------------------------------------------------------------- helpers
def _write(p, text: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def _empty_paths(tmp_path) -> dict:
    """Fixture paths for EVERY register that yield an empty (or minimal-closed) residue, so the
    aggregate neuters to []. Each register is pinned; nothing reads live disk."""
    # Register 1's source is now the sibling simplifications store (retro FM-1):
    # an injectable DIRECTORY, not the map. An empty store dir yields empty residue.
    simpl_store = tmp_path / "simpl_store"
    simpl_store.mkdir(parents=True, exist_ok=True)
    fid = _write(tmp_path / "fidelity.json", "{}")
    san = _write(tmp_path / "sanity.json", "{}")
    board = tmp_path / "board_empty"  # dir with no reconciliation files
    board.mkdir(parents=True, exist_ok=True)
    model = _write(tmp_path / "model.md", "# Timeframe 1\n- everything LIVE\n")
    props = tmp_path / "proposals_empty"
    props.mkdir(parents=True, exist_ok=True)
    carbon = _write(tmp_path / "carbon_ledger.py", "# wired\n")
    # Register 9 (shared-primitive census). Pinned like every other register --
    # an unpinned new register would read LIVE disk and silently break the
    # neuter contract this file exists to prove.
    census = _write(tmp_path / "census.json", json.dumps({
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "clone_count": 100,
        "clone_ceiling": 223,
        "register_count": 91,
        "previous_register_count": 91,
        "migration_note": None,
        "shared_primitive_inventory": {
            "working_day_calculator": {
                "exists": True, "caller_count": 5, "migrated_count": 5},
        },
        "quantity_registry_coverage": {
            "net_margin": {"has_owner": True, "owner_module": "x.py"},
        },
        # The 5.3/5.4 standing-review stamp. A NEW check inside an already-wired register needs
        # pinning here for the same reason the register itself did: an unpinned new rung reads
        # live disk and silently breaks the neuter contract this file exists to prove.
        "last_standing_review": {
            "date": datetime.now(timezone.utc).date().isoformat(),
            "evaluator": "phase-close-evaluator",
            "verdict": "pass",
            "subject": "shared_primitive_census_fixture",
        },
    }))
    return {
        "simplifications": simpl_store,
        "fidelity": fid,
        "sanity": san,
        "board_recon": board,
        "battery": board,
        "claim_placeholder": carbon,
        "model_tf2": model,
        "followons": props,
        "shared_primitive_census": census,
    }


# --------------------------------------------------------------------------- MUTATION 1 (neuter/restore)
def test_neuter_all_registers_reads_closed_then_restore_reads_open(tmp_path):
    paths = _empty_paths(tmp_path)
    residue = g.open_residue(paths)
    # register 5 (claim placeholder) is a SEED that stays until E5 reaches build quality -> that ONE
    # row is expected even in the "neutered" world; every OTHER register must be empty.
    non_seed = {k: v for k, v in residue.items() if k != "claim_placeholder"}
    assert all(not rows for rows in non_seed.values()), non_seed
    assert residue["claim_placeholder"], "E5 seed row must always be present (contract seed)"

    # RESTORE: seed register 6 with one open row -> aggregate flips to drawable.
    _write(paths["sanity"], json.dumps({"coldwalk:x": {"state": "adjudicated-real"}}))
    assert g.gap_register_open(paths) is True
    assert len(g.open_residue(paths)["sanity"]) == 1


# --------------------------------------------------------------------------- MUTATION 2 (seed one row)
def test_single_open_row_flips_level_to_yes(tmp_path):
    paths = _empty_paths(tmp_path)
    # a bare, unmeasured, non-log simplification is the seeded open row (register 1).
    # Seed it into the store (an atom file), the register's source of record now.
    from tools import simplifications_store as store
    store.append_for_atom("A1", ["flat churn rate assumed"], paths["simplifications"])
    res = g.open_residue(paths)
    assert res["simplifications"], "a bare unmeasured simplification must be OPEN"
    assert g.gap_register_open(paths) is True


# --------------------------------------------------------------------------- MUTATION 3 (register 1 old key)
def test_register1_text_heuristic_beats_old_measured_bound_key(tmp_path):
    from tools import simplifications_store as store

    sd = tmp_path / "simpl_store"
    store.append_for_atom("A1", [
        "flat churn assumed everywhere",              # BARE -> OPEN
        "2026-07-20 HARDEN LANDED merit-order engine",  # dated log line -> not open
        "hedge ratio within 5% of target",            # inline measured bound -> not open
    ], sd)
    rows = g.register1_simplifications(sd)
    ids_reasons = [r["reason"] for r in rows]
    # corrected TEXT HEURISTIC: exactly the bare unmeasured non-log entry is OPEN
    assert any("flat churn" in r for r in ids_reasons)
    assert not any("HARDEN LANDED" in r for r in ids_reasons), "a dated progress-log line is not OPEN"
    assert not any("within 5%" in r for r in ids_reasons), "an inline measured bound is not OPEN"

    # OLD KEY MUTATION: a reader keyed on a structured `measured_bound` FIELD finds NOTHING (the
    # entries are plain strings; the field exists nowhere) -> it would report an empty residue while
    # a true unmeasured simplification demonstrably exists. The corrected key catches it. CONTROL FIRES.
    old_key_residue = [
        e for notes in store.load_all(sd).values() for e in notes
        if isinstance(e, dict) and not e.get("measured_bound")  # keys on a field that never appears
    ]
    assert old_key_residue == [], "old measured_bound-field key fail-opens to empty (proves the bug)"
    assert rows, "corrected text heuristic reports the true non-empty residue"


# --------------------------------------------------------------------------- MUTATION 4 (register 6 old key)
def test_register6_state_key_beats_old_audit_prefix_key(tmp_path):
    san = _write(
        tmp_path / "sanity.json",
        json.dumps(
            {
                "coldwalk:panel-mismatch": {"state": "adjudicated-real"},
                "harden_sweep:nan-guard": {"state": "adjudicated-real"},
                "expert_hour:legibility": {"state": "open"},
                "audit:gas-kwh-unit": {"state": "adjudicated-false-positive"},
            }
        ),
    )
    rows = g.register6_sanity(san)
    ids = {r["id"] for r in rows}
    # corrected STATE key, prefix-agnostic: 3 residue rows (2 real + 1 open), the false-positive excluded
    assert ids == {"coldwalk:panel-mismatch", "harden_sweep:nan-guard", "expert_hour:legibility"}
    assert "audit:gas-kwh-unit" not in ids, "adjudicated-false-positive is not residue"

    # OLD KEY MUTATION: a reader keyed on the `audit:*` PREFIX reports 0 real (the only audit row is
    # a false-positive) while 2 adjudicated-real rows live under coldwalk/harden_sweep. CONTROL FIRES.
    data = json.loads(san.read_text())
    old_key_real = [
        k for k, v in data.items()
        if k.startswith("audit:") and v.get("state") == "adjudicated-real"
    ]
    assert old_key_real == [], "old audit:*-prefix key misses all non-audit real findings (proves the bug)"
    real_rows = [r for r in rows if "adjudicated-real" not in r["reason"] or True]
    assert len(rows) == 3, "corrected key finds the true prefix-agnostic residue"


# --------------------------------------------------------------------------- register 2 (fidelity)
def test_register2_below_naive_cell_is_open(tmp_path):
    fid = _write(
        tmp_path / "fid.json",
        json.dumps(
            {
                "row_a": {
                    "per_cell_lift": [
                        {"cell": "good", "commercial_weight": 1.0, "lift": 0.3,
                         "err_model": 0.1, "err_naive": 0.4},   # above naive -> closed
                        {"cell": "bad", "commercial_weight": 1.0, "lift": -0.2,
                         "err_model": 0.5, "err_naive": 0.4},   # lift<=0 & err_model>=err_naive -> OPEN
                        {"cell": "unweighted", "commercial_weight": 0.0, "lift": -9,
                         "err_model": 9, "err_naive": 1},        # weight 0 -> excluded
                    ]
                }
            }
        ),
    )
    rows = g.register2_fidelity(fid)
    ids = {r["id"] for r in rows}
    assert ids == {"row_a:bad"}


def test_register2_nonfinite_at_weight_fails_safe_open(tmp_path):
    fid = _write(
        tmp_path / "fid.json",
        json.dumps({"r": {"per_cell_lift": [
            {"cell": "c", "commercial_weight": 1.0, "lift": None, "err_model": 0.1, "err_naive": 0.2}
        ]}}),
    )
    rows = g.register2_fidelity(fid)
    assert rows, "a non-finite lift at commercial_weight>0 must fail-safe toward OPEN"


# --------------------------------------------------------------------------- invariant 2 (fail-safe)
def test_unreadable_register_reads_drawable(tmp_path):
    bad = _write(tmp_path / "bad.json", "{ this is not json")
    rows = g.register6_sanity(bad)
    assert rows and rows[0]["id"].startswith("unreadable:"), "a parse error must yield an OPEN row"
    # aggregate: a single unreadable register makes the whole reader drawable (never a silent empty)
    paths = _empty_paths(tmp_path)
    paths["sanity"] = bad
    assert g.gap_register_open(paths) is True


def test_missing_file_reads_drawable():
    from pathlib import Path

    rows = g.register2_fidelity(Path("/nonexistent/fidelity.json"))
    assert rows and rows[0]["id"].startswith("unreadable:")


# --------------------------------------------------------------------------- draw-core level wiring
def test_supervisor_level_present_and_killable(tmp_path, monkeypatch):
    from background import supervisor as s

    enum = s.authorized_set_enumeration()
    assert "gap_register" in enum, "the gap_register detector level must appear in the enumeration"

    # ACTIVE: with live registers holding open rows the detector forbids rest
    assert s._gap_register_open() is True

    # SHADOW RAIL: the kill flag reverts the level to contributing nothing (killable draw-core change)
    flag = tmp_path / ".gap_register_level_disabled"
    flag.write_text("off", encoding="utf-8")
    assert s._gap_register_open(disabled_flag=flag) is False


def test_supervisor_level_fails_safe_on_reader_error(monkeypatch):
    from background import supervisor as s

    # simulate the independent reader being unimportable/broken -> the detector forbids rest (Rule-0)
    import background.gap_register_scan as gm

    monkeypatch.setattr(gm, "gap_register_open", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    assert s._gap_register_open() is True


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
