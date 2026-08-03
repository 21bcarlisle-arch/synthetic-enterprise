"""Tests for the F1c conversation belief-vs-truth gap Proof-door panel
(tools/generate_proof_data.py::_conversation_gap).

The atom's own map spec says the gap must reach "per digest + Proof door".
This panel is a RENDERING of F1c's own history ledger
(docs/observability/conversation_gap_ledger.json, populated per-digest by
background/daily_self_note.py::run() -> background.conversation_gap_ledger.
record_gap) -- SITE_CONSTITUTION rule 5, mirrors _coupled_gaps/_control_killlist's
"read the ledger, never invent" discipline (tests/tools/test_generate_proof_
coupled_gaps.py is the sibling precedent this file follows).

R15: the panel must be able to FAIL.
  D1  absent/unreadable ledger file  -> available=False, never a fabricated row.
  D2  empty ledger ([])              -> available=False.
  D3  a not-measurable latest row    -> available=True, measurable=False, the
      real `reason` passed through, never a fabricated gap.
  D4  independence (tautology guard) -- the rendered numbers are exactly the
      ledger's numbers, not recomputed; a mutated ledger value changes the
      rendered value.
"""
from __future__ import annotations

import json

import tools.generate_proof_data as gpd
import background.conversation_gap_ledger as gap_ledger


def _write_ledger(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows), encoding="utf-8")


# ---------------------------------------------------------------------------
# D1 / D2: absent or empty ledger -> fail CLOSED, never fabricated
# ---------------------------------------------------------------------------

def test_missing_ledger_file_fails_closed(tmp_path, monkeypatch):
    monkeypatch.setattr(gap_ledger, "GAP_LEDGER_PATH", tmp_path / "does_not_exist.json")
    panel = gpd._conversation_gap()
    assert panel["available"] is False
    assert "note" in panel


def test_empty_ledger_list_fails_closed(tmp_path, monkeypatch):
    ledger_path = tmp_path / "conversation_gap_ledger.json"
    _write_ledger(ledger_path, [])
    monkeypatch.setattr(gap_ledger, "GAP_LEDGER_PATH", ledger_path)
    panel = gpd._conversation_gap()
    assert panel["available"] is False


def test_malformed_ledger_file_fails_closed(tmp_path, monkeypatch):
    ledger_path = tmp_path / "conversation_gap_ledger.json"
    ledger_path.write_text("{not valid json", encoding="utf-8")
    monkeypatch.setattr(gap_ledger, "GAP_LEDGER_PATH", ledger_path)
    panel = gpd._conversation_gap()
    assert panel["available"] is False


# ---------------------------------------------------------------------------
# D3: a not-measurable latest row -> honest, never a fabricated gap
# ---------------------------------------------------------------------------

def test_not_measurable_latest_row_reports_honestly(tmp_path, monkeypatch):
    ledger_path = tmp_path / "conversation_gap_ledger.json"
    _write_ledger(ledger_path, [
        {"measurable": False, "reason": "customer_count must be positive, got 0",
         "measured_at": "t1", "run_git_commit": None},
    ])
    monkeypatch.setattr(gap_ledger, "GAP_LEDGER_PATH", ledger_path)
    panel = gpd._conversation_gap()
    assert panel["available"] is True
    assert panel["measurable"] is False
    assert panel["reason"] == "customer_count must be positive, got 0"
    assert "framing_category_match_rate" not in panel


# ---------------------------------------------------------------------------
# D4: independence -- rendered numbers are the ledger's, never recomputed
# ---------------------------------------------------------------------------

def _real_measurable_row(**kwargs):
    row = gap_ledger.measure(customer_count=30, situations=None, training_rounds=5)
    row["measured_at"] = "2026-08-03T00:00Z"
    row["run_git_commit"] = "deadbeef"
    row.update(kwargs)
    return row


def test_reflects_the_latest_real_measurable_row_exactly(tmp_path, monkeypatch):
    row = _real_measurable_row()
    ledger_path = tmp_path / "conversation_gap_ledger.json"
    _write_ledger(ledger_path, [row])
    monkeypatch.setattr(gap_ledger, "GAP_LEDGER_PATH", ledger_path)
    panel = gpd._conversation_gap()
    assert panel["available"] is True
    assert panel["measurable"] is True
    assert panel["n_customers"] == row["n_customers"]
    assert panel["framing_category_match_rate"] == row["belief_vs_truth_gap"]["framing_category_match_rate"]
    assert panel["tone_category_match_rate"] == row["belief_vs_truth_gap"]["tone_category_match_rate"]
    assert panel["intent_leak_fired"] == row["intent_leak"]["fired"]
    assert panel["outcome_uplift_by_situation"] == row["outcome_uplift_by_situation"]
    assert panel["measured_at"] == "2026-08-03T00:00Z"
    assert panel["run_git_commit"] == "deadbeef"


def test_uses_the_latest_row_when_the_ledger_has_history(tmp_path, monkeypatch):
    """Multiple rows accumulate (per-digest); the panel must read the LAST one,
    not the first -- proves this is a real ledger read, not a fixed index."""
    older = _real_measurable_row(measured_at="t1")
    newer_raw = gap_ledger.measure(customer_count=40, situations=None, training_rounds=5)
    newer_raw["measured_at"] = "t2"
    newer_raw["run_git_commit"] = "cafef00d"
    ledger_path = tmp_path / "conversation_gap_ledger.json"
    _write_ledger(ledger_path, [older, newer_raw])
    monkeypatch.setattr(gap_ledger, "GAP_LEDGER_PATH", ledger_path)
    panel = gpd._conversation_gap()
    assert panel["measured_at"] == "t2"
    assert panel["n_customers"] == 40
    assert panel["history_count"] == 2


def test_mutated_intent_leak_verdict_is_passed_through_not_reinterpreted(tmp_path, monkeypatch):
    """Independence: the panel must render exactly what the organ decided, even
    a (synthetically forced here) fired=True verdict -- never re-derive its own
    opinion of whether the control fired."""
    row = _real_measurable_row()
    row["intent_leak"] = dict(row["intent_leak"])
    row["intent_leak"]["fired"] = True
    ledger_path = tmp_path / "conversation_gap_ledger.json"
    _write_ledger(ledger_path, [row])
    monkeypatch.setattr(gap_ledger, "GAP_LEDGER_PATH", ledger_path)
    panel = gpd._conversation_gap()
    assert panel["intent_leak_fired"] is True


# ---------------------------------------------------------------------------
# Real integration: the panel imports the real module and constant cleanly
# ---------------------------------------------------------------------------

def test_conversation_gap_panel_is_wired_into_generate_output_keys():
    """Structural: `generate()`'s data dict includes the conversation_gap key
    (the atom's own map spec: gap reaches 'per digest + Proof door') -- checked
    by source inspection so this test doesn't need to run the full generate()
    pipeline (which touches unrelated live data)."""
    import inspect
    source = inspect.getsource(gpd.generate)
    assert "conversation_gap=_conversation_gap()" in source
