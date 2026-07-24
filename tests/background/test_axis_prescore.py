"""Tests for background/axis_prescore.py — the DIRECTOR_AXES twin pre-score
mechanism (MAKE_IT_STICK: prose→enforced code).

R15 BOTH-WAYS is the load-bearing pair:
  - FIRES: a valid twin prediction is written to the ledger before a verdict,
    and prediction_gap pairs it against a later director verdict (the wire is
    load-bearing — without the writer there is no prediction row).
  - FAILS-CLOSED: a malformed/absent prediction is DETECTED and raised
    (`MalformedPrediction`), never silently written as a blank row or skipped.

Uses an injectable invoke_fn throughout — no real `claude -p` is spawned.
"""
import json

import pytest

from background import axis_prescore
from background.axis_prescore import MalformedPrediction


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    ledger = tmp_path / "director_axis_verdicts.jsonl"
    canon = tmp_path / "DIRECTOR_CANON.md"
    canon.write_text("# Canon\n\n**Version: 1.**\n\nThe director values legibility over cleverness.\n")
    monkeypatch.setattr(axis_prescore, "AXIS_LEDGER_PATH", ledger)
    monkeypatch.setattr(axis_prescore, "CANON_PATH", canon)
    return ledger


def _rows(ledger):
    return [json.loads(ln) for ln in ledger.read_text().splitlines() if ln.strip()]


# ---------------------------------------------------------------------------
# R15 — FIRES: the mechanism writes a real prediction and the gap pairs it
# ---------------------------------------------------------------------------

def test_prescore_axis_writes_a_twin_prediction_row(_isolate):
    ledger = _isolate

    def fake_invoke(prompt):
        # The prompt must carry the axis and canon (read-only, canon-only lens).
        assert "AXIS 1" in prompt and "legibility over cleverness" in prompt
        return "PREDICTED_VERDICT: PARTIAL\nRATIONALE: front door legible but panel still noisy"

    entry = axis_prescore.prescore_axis(
        axis="website", axis_number=1, component="site_front_door_mvp",
        invoke_fn=fake_invoke,
    )
    rows = _rows(ledger)
    assert len(rows) == 1
    assert rows[0]["source"] == "twin_prediction"
    assert rows[0]["axis"] == "website"
    assert rows[0]["axis_number"] == 1
    assert rows[0]["component"] == "site_front_door_mvp"
    assert rows[0]["predicted_verdict"] == "PARTIAL"
    assert rows[0]["rationale"].startswith("front door legible")
    assert entry["source"] == "twin_prediction"


def test_score_style_prediction_records_predicted_score(_isolate):
    ledger = _isolate
    axis_prescore.prescore_axis(
        axis="website", axis_number=1, component="site_front_door_mvp",
        invoke_fn=lambda p: "PREDICTED_VERDICT: 2/5\nRATIONALE: better but not there",
    )
    rows = _rows(ledger)
    assert rows[0]["predicted_verdict"] == "2/5"
    assert rows[0]["predicted_score"] == "2/5"


def test_prediction_gap_pairs_prediction_against_later_verdict(_isolate):
    ledger = _isolate
    # Twin predicts first (ts=100), director verdict lands after (ts=200).
    axis_prescore.record_twin_prescore(
        axis="website", axis_number=1, component="site_front_door_mvp",
        rationale="predict a near-miss", predicted_verdict="2/5", ts=100.0,
    )
    axis_prescore._append_jsonl(ledger, {
        "axis": "website", "axis_number": 1, "source": "director_verdict",
        "component": "site_front_door_mvp", "verdict": "FAIL", "score": "1/5", "ts": 200.0,
        "recorded_date": "2026-07-23",
    })
    gaps = axis_prescore.prediction_gap()
    assert len(gaps) == 1
    g = gaps[0]
    assert g["axis"] == "website"
    assert g["twin_prediction"] == "2/5"
    # twin said 2/5 (0.4), director said 1/5 (0.2) → gap 0.2
    assert g["gap"] == pytest.approx(0.2, abs=1e-6)


def test_categorical_and_score_scales_are_both_gap_mappable(_isolate):
    axis_prescore.record_twin_prescore(
        axis="believability", axis_number=3, component="persistence",
        rationale="predict met", predicted_verdict="MET", ts=100.0,
    )
    axis_prescore._append_jsonl(axis_prescore.AXIS_LEDGER_PATH, {
        "axis": "believability", "axis_number": 3, "source": "director_verdict",
        "component": "persistence", "verdict": "PARTIAL", "ts": 200.0,
    })
    gaps = axis_prescore.prediction_gap()
    # MET(1.0) vs PARTIAL(0.5) → 0.5
    assert gaps[0]["gap"] == pytest.approx(0.5, abs=1e-6)


# ---------------------------------------------------------------------------
# R15 — FAILS-CLOSED: malformed/absent predictions are detected, not skipped
# ---------------------------------------------------------------------------

def test_missing_verdict_line_raises_not_silently_written(_isolate):
    ledger = _isolate
    with pytest.raises(MalformedPrediction):
        axis_prescore.prescore_axis(
            axis="website", axis_number=1,
            invoke_fn=lambda p: "RATIONALE: I forgot the verdict line entirely",
        )
    # Fail-closed: NOTHING was written.
    assert not ledger.exists() or _rows(ledger) == []


def test_blank_verdict_raises(_isolate):
    with pytest.raises(MalformedPrediction):
        axis_prescore.prescore_axis(
            axis="website", axis_number=1,
            invoke_fn=lambda p: "PREDICTED_VERDICT:\nRATIONALE: verdict is blank",
        )


def test_missing_rationale_raises(_isolate):
    with pytest.raises(MalformedPrediction):
        axis_prescore.prescore_axis(
            axis="website", axis_number=1,
            invoke_fn=lambda p: "PREDICTED_VERDICT: MET",
        )


def test_empty_twin_reply_raises(_isolate):
    with pytest.raises(MalformedPrediction):
        axis_prescore.prescore_axis(
            axis="website", axis_number=1, invoke_fn=lambda p: "",
        )


def test_record_rejects_blank_required_fields(_isolate):
    with pytest.raises(MalformedPrediction):
        axis_prescore.record_twin_prescore(
            axis="  ", axis_number=1, rationale="x", predicted_verdict="MET")
    with pytest.raises(MalformedPrediction):
        axis_prescore.record_twin_prescore(
            axis="website", axis_number=1, rationale="   ", predicted_verdict="MET")
    with pytest.raises(MalformedPrediction):
        # bool is not a valid axis_number (would slip past a naive isinstance int check)
        axis_prescore.record_twin_prescore(
            axis="website", axis_number=True, rationale="x", predicted_verdict="MET")


# ---------------------------------------------------------------------------
# Severance (HARD LAW §2) + honest-absent retro line
# ---------------------------------------------------------------------------

def test_retro_line_honest_when_no_predictions_yet(_isolate):
    line = axis_prescore.retro_gap_line()
    assert "NO twin_prediction rows yet" in line


def test_retro_line_reports_scored_gap(_isolate):
    axis_prescore.record_twin_prescore(
        axis="believability", axis_number=3, component="persistence",
        rationale="predict met", predicted_verdict="MET", ts=100.0)
    axis_prescore._append_jsonl(axis_prescore.AXIS_LEDGER_PATH, {
        "axis": "believability", "axis_number": 3, "source": "director_verdict",
        "component": "persistence", "verdict": "PARTIAL", "ts": 200.0})
    line = axis_prescore.retro_gap_line()
    assert "mean 0.5" in line and "believability/persistence" in line


def test_module_not_imported_by_supervisor_draw():
    """HARD LAW §2: the axis ledger is never consumed by any draw/reward. This
    module must not be reachable from supervisor.py's draw path."""
    import inspect
    from background import supervisor
    src = inspect.getsource(supervisor)
    assert "axis_prescore" not in src
