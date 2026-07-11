"""Tests for tools/generate_simplified_data.py -- the SIMPLIFIED (honesty
door) page's data generator."""
import json

from tools.generate_simplified_data import generate, OUT_PATH


def test_generate_produces_valid_json():
    ok = generate()
    assert ok is True
    assert OUT_PATH.exists()
    data = json.loads(OUT_PATH.read_text())
    assert "lanes" in data
    assert "total_atoms_with_notes" in data
    assert "total_notes" in data


def test_only_atoms_with_real_simplifications_are_included():
    generate()
    data = json.loads(OUT_PATH.read_text())
    for lane in data["lanes"]:
        for atom in lane["atoms"]:
            assert len(atom["notes"]) > 0


def test_totals_are_internally_consistent():
    generate()
    data = json.loads(OUT_PATH.read_text())
    total_atoms = sum(len(l["atoms"]) for l in data["lanes"])
    total_notes = sum(len(a["notes"]) for l in data["lanes"] for a in l["atoms"])
    assert data["total_atoms_with_notes"] == total_atoms
    assert data["total_notes"] == total_notes


def test_never_authors_new_text_only_republishes(monkeypatch, tmp_path):
    """SITE_CONSTITUTION rule 5: the site is a rendering, never an author.
    Every note in the output must come verbatim from the source YAML."""
    yaml_content = """
- id: TEST_ATOM
  name: "Test atom"
  lane: W1_market_weather
  value_stream: wholesale_to_price
  epoch: 1
  level_current: 1
  level_target: 2
  loop_stage: idle
  dial_inherited: 1
  evidence: []
  simplifications: ["a real, verbatim note from the source"]
  expert_hour: {status: not_attempted, last: null, findings: []}
  real_world_twin: "test"
  depends_on: []
"""
    yaml_path = tmp_path / "maturity_map.yaml"
    yaml_path.write_text(yaml_content)
    out_path = tmp_path / "simplified.json"

    import tools.generate_simplified_data as mod
    monkeypatch.setattr(mod, "MATURITY_MAP_YAML", yaml_path)
    monkeypatch.setattr(mod, "OUT_PATH", out_path)

    assert mod.generate() is True
    data = json.loads(out_path.read_text())
    all_notes = [n for l in data["lanes"] for a in l["atoms"] for n in a["notes"]]
    assert all_notes == ["a real, verbatim note from the source"]


def test_missing_yaml_returns_false(monkeypatch, tmp_path):
    import tools.generate_simplified_data as mod
    monkeypatch.setattr(mod, "MATURITY_MAP_YAML", tmp_path / "nope.yaml")
    assert mod.generate() is False


def test_atoms_sorted_by_id_within_lane():
    generate()
    data = json.loads(OUT_PATH.read_text())
    for lane in data["lanes"]:
        ids = [a["atom_id"] for a in lane["atoms"]]
        assert ids == sorted(ids)


def test_lanes_sorted_alphabetically():
    generate()
    data = json.loads(OUT_PATH.read_text())
    lane_ids = [l["lane"] for l in data["lanes"]]
    assert lane_ids == sorted(lane_ids)
