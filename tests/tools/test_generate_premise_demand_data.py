"""Data-side tests for tools/generate_premise_demand_data.py -- the demand-arrow
evidence feed (site/data/premise_demand.json) for the World door's causal spine.

The feed is a RENDERING of an already-measured result: coupled_gap_ledger.json ->
W1_5_premise_demand_shape. These tests prove the generator (a) carries the measured
worst-cell MAE/N through faithfully (independence -- no re-computation, no baked-in
constant) and (b) fails closed and VISIBLE (R15) when the ledger block is missing or
malformed, so the panel can render an honest "unavailable" rather than a fabricated bar.
"""
import json

import pytest

from tools import generate_premise_demand_data as gen


def test_live_feed_carries_measured_worst_cell():
    feed = gen.build()
    assert feed["available"] is True
    assert feed["atom"] == "W1_5_premise_demand_shape"
    assert feed["twin_atom"] == "C13_weather_normalisation"
    # Worst cell = summer; the measured MAE (L2 2276 / no-skill 2190) passes through.
    w = feed["worst"]
    assert feed["worst_cell"] == "summer"
    assert w["mae_model"] == 2276
    assert w["mae_noskill"] == 2190
    assert feed["n_train"] == 3337
    # Every measured cell is present, each with its own N (RC6, never a bare total).
    labels = {c["key"]: c for c in feed["cells"]}
    for key in ("winter", "cold", "shoulder", "warm", "summer"):
        assert key in labels
        assert labels[key]["n"] > 0


def test_gap_and_baseline_are_faithful_not_derived():
    # Independence: the gap is copied from the ledger, not re-derived from MAE here.
    feed = gen.build()
    ledger = json.loads(gen.LEDGER_PATH.read_text())
    per_cell = ledger["W1_5_premise_demand_shape"]["components"]["per_cell"]
    for c in feed["cells"]:
        assert c["gap"] == round(float(per_cell[c["key"]]["gap"]), 3)
    assert "climatological" in feed["baseline_label"]


def test_missing_atom_fails_closed(tmp_path, monkeypatch):
    # R15: ledger present but no W1_5 block -> available:false, empty cells, a reason.
    p = tmp_path / "ledger.json"
    p.write_text(json.dumps({"SOME_OTHER_ATOM": {}}))
    monkeypatch.setattr(gen, "LEDGER_PATH", p)
    feed = gen.build()
    assert feed["available"] is False
    assert feed["cells"] == []
    assert "W1_5" in feed["reason"]


def test_missing_ledger_file_fails_closed(tmp_path, monkeypatch):
    # R15 fail-closed on a totally absent/unreadable ledger (not a crash).
    monkeypatch.setattr(gen, "LEDGER_PATH", tmp_path / "does_not_exist.json")
    feed = gen.build()
    assert feed["available"] is False
    assert feed["cells"] == []


def test_empty_per_cell_fails_closed(tmp_path, monkeypatch):
    p = tmp_path / "ledger.json"
    p.write_text(json.dumps({"W1_5_premise_demand_shape": {"components": {"per_cell": {}}}}))
    monkeypatch.setattr(gen, "LEDGER_PATH", p)
    feed = gen.build()
    assert feed["available"] is False
    assert "per_cell" in feed["reason"]


def test_generate_writes_feed(tmp_path, monkeypatch):
    out = tmp_path / "premise_demand.json"
    monkeypatch.setattr(gen, "OUT_PATH", out)
    gen.generate()
    written = json.loads(out.read_text())
    assert written["atom"] == "W1_5_premise_demand_shape"
