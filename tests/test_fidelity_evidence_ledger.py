"""Tests for background/fidelity_evidence_ledger.py -- atom G2, the
fidelity-evidence emit-ledger + emit-DoD phase-close gate (Epoch-2
G_data_learning lane, HARNESS-side).

Per R15 ("a control that cannot fail is worse than none"), the gate's three
named red conditions are each proven with a MUTATION test: introduce the
defect and assert red, remove it and assert green -- not just a happy-path
acceptance test. A fourth group covers the ledger's own fail-closed reading
(malformed/missing ledger must red the gate, never silently pass).

All tests use `tmp_path` for the ledger file so the real repo ledger at
`docs/observability/fidelity_evidence_ledger.json` is never touched by the
test suite.
"""

import json

import pytest

from background import fidelity_evidence_ledger as fel


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

def _good_record(rel_id="D1_temp_wind_winter_lowtail", atom_id="D_cascade_correlation",
                  provenance="estimated_from_data", simplification_id=None,
                  ablation=None):
    return {
        "rel_id": rel_id,
        "atom_id": atom_id,
        "layer": "EVIDENCE",
        "relationship": {
            "kind": "joint_tail_lift",
            "observables": ["temperature_mean", "wind_speed_mean"],
            "conditioning": "winter_DJF",
            "strength": {"stat": "L", "value": 2.34, "u": 0.10, "ci": [1.7, 3.1],
                         "ci_method": "block_bootstrap"},
            "provenance": provenance,
            "series_ref": "W1_3 4pt proxy",
            "independent_anchor": "NESO low-wind-cold stress",
            "simplification_id": simplification_id,
        },
        "per_cell_lift": [
            {"cell": "A2_G3", "err_naive": 0.62, "err_model": 0.28, "lift": 0.34,
             "commercial_weight": 1.0},
        ],
        "ablation": ablation,
        "measured_at": "2026-07-19T00:00:00+00:00",
        "run_git_commit": "deadbeef",
    }


def _crn_block(isolated: bool, verdict: str = "load_bearing"):
    return {
        "coupling_id": "D1_temp_wind",
        "crn": {"seed": 4711, "population_hash": "abc", "weather_path_hash": "def",
                "substream_isolated": isolated},
        "delta_worst_cell": 0.21,
        "verdict": verdict,
    }


# ===========================================================================
# Ledger read/write
# ===========================================================================

def test_append_and_read_round_trip(tmp_path):
    path = tmp_path / "ledger.json"
    rec = _good_record()
    fel.append_record(rec, ledger_path=path)

    ledger = fel.load_ledger(path)
    assert "D1_temp_wind_winter_lowtail" in ledger
    assert ledger["D1_temp_wind_winter_lowtail"]["atom_id"] == "D_cascade_correlation"

    # File on disk is well-formed, sorted JSON.
    on_disk = json.loads(path.read_text(encoding="utf-8"))
    assert on_disk == ledger


def test_append_preserves_other_entries(tmp_path):
    path = tmp_path / "ledger.json"
    fel.append_record(_good_record(rel_id="rel_a"), ledger_path=path)
    fel.append_record(_good_record(rel_id="rel_b", atom_id="other_atom"), ledger_path=path)

    ledger = fel.load_ledger(path)
    assert set(ledger) == {"rel_a", "rel_b"}


def test_append_rejects_missing_required_top_key(tmp_path):
    path = tmp_path / "ledger.json"
    bad = _good_record()
    del bad["rel_id"]
    with pytest.raises(fel.LedgerMalformed):
        fel.append_record(bad, ledger_path=path)


def test_append_rejects_missing_relationship_keys(tmp_path):
    path = tmp_path / "ledger.json"
    bad = _good_record()
    del bad["relationship"]["provenance"]
    with pytest.raises(fel.LedgerMalformed):
        fel.append_record(bad, ledger_path=path)


def test_append_rejects_invalid_provenance_value(tmp_path):
    path = tmp_path / "ledger.json"
    bad = _good_record(provenance="made_up_kind")
    with pytest.raises(fel.LedgerMalformed):
        fel.append_record(bad, ledger_path=path)


def test_append_rejects_non_dict_record(tmp_path):
    path = tmp_path / "ledger.json"
    with pytest.raises(fel.LedgerMalformed):
        fel.append_record(["not", "a", "dict"], ledger_path=path)


def test_append_refuses_to_clobber_a_corrupt_existing_file(tmp_path):
    path = tmp_path / "ledger.json"
    path.write_text("{not valid json", encoding="utf-8")
    with pytest.raises(fel.LedgerMalformed):
        fel.append_record(_good_record(), ledger_path=path)


def test_append_accepts_a_structurally_valid_but_epistemically_dishonest_record(tmp_path):
    """The writer's R10 note: it must NOT block a well-shaped-but-dishonest
    record (asserted with null simplification_id, or an ablation without CRN
    isolation) -- that defect must be constructible so the GATE's own R15
    mutation tests below can exercise it. Only the gate rejects it."""
    path = tmp_path / "ledger.json"
    rec = _good_record(provenance="asserted", simplification_id=None)
    fel.append_record(rec, ledger_path=path)  # must NOT raise
    ledger = fel.load_ledger(path)
    assert ledger[rec["rel_id"]]["relationship"]["provenance"] == "asserted"


def test_load_ledger_missing_file_raises_unavailable(tmp_path):
    path = tmp_path / "does_not_exist.json"
    with pytest.raises(fel.LedgerUnavailable):
        fel.load_ledger(path)


def test_load_ledger_malformed_json_raises_unavailable(tmp_path):
    path = tmp_path / "ledger.json"
    path.write_text("{this is not json", encoding="utf-8")
    with pytest.raises(fel.LedgerUnavailable):
        fel.load_ledger(path)


def test_load_ledger_non_object_json_raises_unavailable(tmp_path):
    path = tmp_path / "ledger.json"
    path.write_text("[1, 2, 3]", encoding="utf-8")
    with pytest.raises(fel.LedgerUnavailable):
        fel.load_ledger(path)


def test_records_for_atom_filters_and_orders(tmp_path):
    path = tmp_path / "ledger.json"
    fel.append_record(_good_record(rel_id="rel_b", atom_id="atom_1"), ledger_path=path)
    fel.append_record(_good_record(rel_id="rel_a", atom_id="atom_1"), ledger_path=path)
    fel.append_record(_good_record(rel_id="rel_c", atom_id="atom_2"), ledger_path=path)

    ledger = fel.load_ledger(path)
    recs = fel.records_for_atom("atom_1", ledger)
    assert [r["rel_id"] for r in recs] == ["rel_a", "rel_b"]


# ===========================================================================
# The emit-DoD gate -- R15 mutation tests
# ===========================================================================

def test_gate_passes_on_a_clean_well_evidenced_atom(tmp_path):
    path = tmp_path / "ledger.json"
    fel.append_record(
        _good_record(atom_id="D_cascade_correlation",
                     ablation=_crn_block(isolated=True)),
        ledger_path=path,
    )
    result = fel.fidelity_evidence_gate("D_cascade_correlation", ledger_path=path)
    assert result.passed is True
    assert result.reasons == ()


def test_R15_killer_mutation_a_zero_evidence_records_reds(tmp_path):
    """(a) An atom with ZERO evidence records in the ledger must red."""
    path = tmp_path / "ledger.json"
    fel.append_record(_good_record(atom_id="some_other_atom"), ledger_path=path)

    result = fel.fidelity_evidence_gate("D_cascade_correlation", ledger_path=path)
    assert result.passed is False
    assert any("zero fidelity-evidence records" in r for r in result.reasons)

    # Remove the defect: emit a record for the atom under test -> green.
    fel.append_record(_good_record(atom_id="D_cascade_correlation"), ledger_path=path)
    result2 = fel.fidelity_evidence_gate("D_cascade_correlation", ledger_path=path)
    assert result2.passed is True


def test_R15_killer_mutation_b_asserted_without_simplification_id_reds(tmp_path):
    """(b) An `asserted` record with null `simplification_id` must red
    (R10 mechanised -- an asserted relationship dressed as estimated)."""
    path = tmp_path / "ledger.json"
    fel.append_record(
        _good_record(atom_id="B_price_model", provenance="asserted", simplification_id=None),
        ledger_path=path,
    )
    result = fel.fidelity_evidence_gate("B_price_model", ledger_path=path)
    assert result.passed is False
    assert any("simplification_id=null" in r for r in result.reasons)

    # Remove the defect: register the simplification_id -> green.
    path2 = tmp_path / "ledger2.json"
    fel.append_record(
        _good_record(atom_id="B_price_model", provenance="asserted",
                     simplification_id="B_PRICE_HAND_SET_CONST_01"),
        ledger_path=path2,
    )
    result2 = fel.fidelity_evidence_gate("B_price_model", ledger_path=path2)
    assert result2.passed is True


def test_R15_killer_mutation_c_ablation_without_crn_isolation_reds(tmp_path):
    """(c) An ablation Delta recorded without proven CRN substream isolation
    must red (S1.3/S5 killer-mutation-B -- a Delta without isolation is
    noise, not evidence)."""
    path = tmp_path / "ledger.json"
    fel.append_record(
        _good_record(atom_id="W1_cascade", ablation=_crn_block(isolated=False)),
        ledger_path=path,
    )
    result = fel.fidelity_evidence_gate("W1_cascade", ledger_path=path)
    assert result.passed is False
    assert any("without proven CRN substream isolation" in r for r in result.reasons)

    # Remove the defect: isolate the substream -> green.
    path2 = tmp_path / "ledger2.json"
    fel.append_record(
        _good_record(atom_id="W1_cascade", ablation=_crn_block(isolated=True)),
        ledger_path=path2,
    )
    result2 = fel.fidelity_evidence_gate("W1_cascade", ledger_path=path2)
    assert result2.passed is True


def test_gate_catches_missing_substream_isolated_key_entirely(tmp_path):
    """A malformed ablation.crn block that OMITS `substream_isolated` (not
    just sets it False) must still red -- `is not True` is the guard, not
    `is False`, so an absent key can't sneak through."""
    path = tmp_path / "ledger.json"
    rec = _good_record(atom_id="atom_x", ablation={
        "coupling_id": "k", "crn": {"seed": 1}, "delta_worst_cell": 0.1,
        "verdict": "load_bearing",
    })
    fel.append_record(rec, ledger_path=path)
    result = fel.fidelity_evidence_gate("atom_x", ledger_path=path)
    assert result.passed is False


def test_gate_ignores_records_belonging_to_other_atoms(tmp_path):
    """A defect on a DIFFERENT atom's record must not red this atom's gate."""
    path = tmp_path / "ledger.json"
    fel.append_record(
        _good_record(rel_id="bad_rel", atom_id="other_atom",
                      provenance="asserted", simplification_id=None),
        ledger_path=path,
    )
    fel.append_record(
        _good_record(rel_id="good_rel", atom_id="atom_under_test"),
        ledger_path=path,
    )
    result = fel.fidelity_evidence_gate("atom_under_test", ledger_path=path)
    assert result.passed is True


# ===========================================================================
# Fail-closed ledger reading -- R15 fail-silent doctrine
# ===========================================================================

def test_R15_gate_reds_on_missing_ledger_file_fail_closed(tmp_path):
    path = tmp_path / "never_written.json"
    result = fel.fidelity_evidence_gate("any_atom", ledger_path=path)
    assert result.passed is False
    assert any("ledger unavailable" in r for r in result.reasons)


def test_R15_gate_reds_on_malformed_ledger_json_fail_closed(tmp_path):
    path = tmp_path / "ledger.json"
    path.write_text("{not valid json at all", encoding="utf-8")
    result = fel.fidelity_evidence_gate("any_atom", ledger_path=path)
    assert result.passed is False
    assert any("ledger unavailable" in r for r in result.reasons)


def test_R15_gate_reds_on_non_object_ledger_json_fail_closed(tmp_path):
    path = tmp_path / "ledger.json"
    path.write_text('["a", "list", "not", "an", "object"]', encoding="utf-8")
    result = fel.fidelity_evidence_gate("any_atom", ledger_path=path)
    assert result.passed is False
    assert any("ledger unavailable" in r for r in result.reasons)


def test_gate_never_silently_passes_when_ledger_check_itself_is_unavailable():
    """The FAIL-SILENT doctrine restated as a direct assertion: passing a
    path that can never exist must NEVER read as passed=True."""
    result = fel.fidelity_evidence_gate(
        "any_atom", ledger_path="/nonexistent/path/that/cannot/exist/ledger.json"
    )
    assert result.passed is False
