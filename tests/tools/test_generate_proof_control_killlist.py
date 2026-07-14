"""Tests for the CONTROL KILL-LIST Proof-door panel data
(tools/generate_proof_data.py::_control_killlist).

The kill-list is a CONTROL surface (R15, CONTROLS_THAT_CANNOT_FAIL.md): it
renders which of the company's controls have been MUTATION-PROVEN to fire on
their own named defect, and which remain theatre. Per R15 / R11 the rendered
block must:

  * reflect the REAL inventory (docs/design/control_registry.json), never a
    hand-maintained list -- a control the inventory does not record as firing
    cannot be shown as proven (no tautology);
  * FAIL CLOSED: a control with no mutation test (unknown/absent result) shows
    as theatre/red, and is NEVER silently omitted;
  * recompute its cumulative counts from the per-control rows, so the panel and
    the registry cannot silently diverge.
"""

from __future__ import annotations

import copy
import json

import tools.generate_proof_data as gpd


def _real_registry():
    return json.loads(gpd.CONTROL_REGISTRY_PATH.read_text())


# ---------------------------------------------------------------------------
# R11 faithfulness: the block reflects the real inventory exactly
# ---------------------------------------------------------------------------
def test_reflects_real_registry_exactly():
    reg = _real_registry()
    kl = gpd._control_killlist()
    assert kl["available"] is True
    assert kl["source"] == "docs/design/control_registry.json"

    controls = reg["controls"]
    # Every inventoried control appears -- none dropped.
    assert kl["controls_total"] == len(controls)
    by_name = {r["name"]: r for r in kl["controls"]}
    assert len(by_name) == len(controls)

    # Per-control classification is derived from the inventory's `result`,
    # fail-closed: only an explicit FIRED counts as mutation-proven.
    for c in controls:
        row = by_name[c["id"]]
        result = c["result"]
        assert row["result"] == result
        assert row["fires_on_defect"] is (result == "FIRED")
        assert row["mutation_tested"] is (result in ("FIRED", "THEATRE"))
        if result == "FIRED":
            assert row["chip"] == "proven" and row["severity"] == "green"
        elif result == "THEATRE":
            assert row["chip"] == "theatre" and row["severity"] == "red"
        elif result == "STRUCTURAL-ONLY":
            assert row["chip"] == "structural_only" and row["severity"] == "amber"


def test_cumulative_counts_recomputed_from_rows():
    reg = _real_registry()
    kl = gpd._control_killlist()
    results = [c["result"] for c in reg["controls"]]
    assert kl["mutation_proven"] == results.count("FIRED")
    assert kl["theatre_remaining"] == results.count("THEATRE")
    assert kl["structural_only"] == results.count("STRUCTURAL-ONLY")
    assert kl["mutation_tested"] == (results.count("FIRED") + results.count("THEATRE"))
    assert kl["controls_total"] == len(results)


def test_counts_consistent_with_registry_meta_summary():
    """Drift guard: the block's independently-recomputed counts must agree with
    the registry's own hand-summarised _meta cumulative counts. A divergence is a
    real defect (a stale summary or a mis-classification), not tolerated."""
    reg = _real_registry()
    kl = gpd._control_killlist()
    cc = reg["_meta"]["cumulative_counts"]
    assert kl["mutation_proven"] == cc["fired_on_named_defect"]
    assert kl["theatre_remaining"] == cc["theatre"]
    # The registry's "total mutation tested" excludes the STRUCTURAL-ONLY row.
    assert kl["mutation_tested"] == cc["total_controls_mutation_tested"]


# ---------------------------------------------------------------------------
# R15 fail-closed: an unverified control is shown red, never omitted
# ---------------------------------------------------------------------------
def test_unknown_result_fails_closed_to_theatre(monkeypatch, tmp_path):
    reg = copy.deepcopy(_real_registry())
    reg["controls"].append({
        "id": "some_new_uninventoried_control",
        "location": "company/whatever.py::check_new",
        "catches": "a named defect nobody wrote a mutation test for yet",
        "mutation": "n/a",
        "killer_pattern_audit": "not-yet-audited",
        "result": "UNVERIFIED",
    })
    p = tmp_path / "control_registry.json"
    p.write_text(json.dumps(reg))
    monkeypatch.setattr(gpd, "CONTROL_REGISTRY_PATH", p)

    kl = gpd._control_killlist()
    row = next(r for r in kl["controls"] if r["name"] == "some_new_uninventoried_control")
    # FAIL CLOSED: an unverified control is a FAILED control -- red, not proven,
    # and NOT silently dropped from the panel.
    assert row["mutation_tested"] is False
    assert row["fires_on_defect"] is False
    assert row["chip"] == "theatre"
    assert row["severity"] == "red"
    # It is counted as theatre and inflates neither the proven nor the total-tested tally.
    assert kl["theatre_remaining"] >= 1
    assert kl["controls_total"] == len(reg["controls"])


def test_missing_result_field_fails_closed(monkeypatch, tmp_path):
    reg = copy.deepcopy(_real_registry())
    reg["controls"].append({"id": "control_with_no_result", "location": "x"})
    p = tmp_path / "control_registry.json"
    p.write_text(json.dumps(reg))
    monkeypatch.setattr(gpd, "CONTROL_REGISTRY_PATH", p)

    kl = gpd._control_killlist()
    row = next(r for r in kl["controls"] if r["name"] == "control_with_no_result")
    assert row["result"] is None
    assert row["mutation_tested"] is False
    assert row["fires_on_defect"] is False
    assert row["severity"] == "red"


def test_theatre_control_is_never_counted_as_proven(monkeypatch, tmp_path):
    """Independence guard: relabelling a FIRED control as THEATRE in the inventory
    must move it OUT of the proven tally and into theatre -- the panel tracks the
    inventory, it does not stick to a rosier number."""
    reg = copy.deepcopy(_real_registry())
    real_fired = sum(1 for c in reg["controls"] if c["result"] == "FIRED")
    fired = next(c for c in reg["controls"] if c["result"] == "FIRED")
    fired["result"] = "THEATRE"
    p = tmp_path / "control_registry.json"
    p.write_text(json.dumps(reg))
    monkeypatch.setattr(gpd, "CONTROL_REGISTRY_PATH", p)

    kl = gpd._control_killlist()
    row = next(r for r in kl["controls"] if r["name"] == fired["id"])
    assert row["fires_on_defect"] is False
    assert row["chip"] == "theatre"
    assert kl["mutation_proven"] == real_fired - 1


# ---------------------------------------------------------------------------
# Unreadable / malformed inventory -> available False (never a green panel)
# ---------------------------------------------------------------------------
def test_unreadable_registry_reports_unavailable(monkeypatch, tmp_path):
    missing = tmp_path / "nope.json"
    monkeypatch.setattr(gpd, "CONTROL_REGISTRY_PATH", missing)
    kl = gpd._control_killlist()
    assert kl["available"] is False


def test_empty_controls_array_reports_unavailable(monkeypatch, tmp_path):
    p = tmp_path / "control_registry.json"
    p.write_text(json.dumps({"_meta": {}, "controls": []}))
    monkeypatch.setattr(gpd, "CONTROL_REGISTRY_PATH", p)
    kl = gpd._control_killlist()
    assert kl["available"] is False


# ---------------------------------------------------------------------------
# End-to-end: the generated proof.json actually carries the block
# ---------------------------------------------------------------------------
def test_generate_writes_control_killlist_to_proof_json():
    gpd.generate()
    data = json.loads(gpd.OUT_PATH.read_text())
    assert "control_killlist" in data
    kl = data["control_killlist"]
    assert kl["available"] is True
    reg = _real_registry()
    assert kl["controls_total"] == len(reg["controls"])
    assert kl["mutation_proven"] == \
        sum(1 for c in reg["controls"] if c["result"] == "FIRED")
