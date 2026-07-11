"""Tests for tools/generate_maturity_map_data.py."""
import json
from pathlib import Path

from tools.generate_maturity_map_data import generate, LANE_EQUALISER, OUT_PATH


def test_generate_produces_valid_json():
    ok = generate()
    assert ok is True
    assert OUT_PATH.exists()
    data = json.loads(OUT_PATH.read_text())
    assert "atoms" in data
    assert "lanes" in data
    assert "total_atoms" in data


def test_every_atom_has_required_view_fields():
    generate()
    data = json.loads(OUT_PATH.read_text())
    required = {"id", "name", "lane", "value_stream", "epoch", "level_current",
                "level_target", "loop_stage", "dial_inherited", "expert_hour_status"}
    for atom in data["atoms"]:
        assert required.issubset(atom.keys())


def test_every_atom_lane_exists_in_equaliser():
    generate()
    data = json.loads(OUT_PATH.read_text())
    for atom in data["atoms"]:
        assert atom["lane"] in data["lanes"], f"lane {atom['lane']} missing from LANE_EQUALISER"


def test_at_target_true_when_current_meets_target():
    generate()
    data = json.loads(OUT_PATH.read_text())
    at_target = [a for a in data["atoms"] if a["at_target"]]
    assert len(at_target) > 0
    for a in at_target:
        assert a["level_current"] >= a["level_target"]


def test_at_target_false_when_below_target():
    generate()
    data = json.loads(OUT_PATH.read_text())
    below = [a for a in data["atoms"] if not a["at_target"] and a["level_current"] is not None]
    assert len(below) > 0
    for a in below:
        assert a["level_current"] < a["level_target"]


def test_value_stream_label_maps_known_streams():
    generate()
    data = json.loads(OUT_PATH.read_text())
    streams = {a["value_stream"] for a in data["atoms"]}
    for s in streams:
        atom = next(a for a in data["atoms"] if a["value_stream"] == s)
        assert atom["value_stream_label"] != ""


def test_total_atoms_matches_atom_list_length():
    generate()
    data = json.loads(OUT_PATH.read_text())
    assert data["total_atoms"] == len(data["atoms"])


def test_w5_banking_payment_rails_lane_present():
    generate()
    data = json.loads(OUT_PATH.read_text())
    assert "W5_banking_payment_rails" in data["lanes"]
    ids = [a["id"] for a in data["atoms"]]
    assert "W5_1_banking_payment_rails" in ids
    assert "D_payments_maturity_audit" in ids


def test_epoch2_movements_has_all_four():
    generate()
    data = json.loads(OUT_PATH.read_text())
    ids = [m["id"] for m in data["epoch2_movements"]]
    assert ids == ["M1", "M2", "M3", "M4"]


def test_epoch2_movements_have_exit_test_and_status():
    generate()
    data = json.loads(OUT_PATH.read_text())
    for m in data["epoch2_movements"]:
        assert m["exit_test"]
        assert m["status"] in {"not_started", "in_progress", "audit_complete", "done"}
        assert m["status_note"]
