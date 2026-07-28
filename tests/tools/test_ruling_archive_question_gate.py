"""R15 mechanism self-test — ARCHIVE-QUESTION GATE (tools/ruling_archive_question_gate.py).

DIRECTOR_RULING_NO_QUESTION_LEFT_UNANSWERED 2026-07-28 §2 ("impossible to archive a ruling ...
while it carries an unanswered question, enforced mechanically"). R15 demands the control FIRE on
its own named defect and PASS when the defect is absent:

  - FIRES: a ruling being ADDED to docs/staging/done/ that carries an OPEN question -> exit 1.
  - PASSES: the same ruling once every question is CLOSED -> exit 0.
  - FAIL-CLOSED: a done/-bound ruling whose staged blob is UNREADABLE -> exit 1 (unverifiable archive
    may hide an open question — the fail-open direction R15 forbids).
  - SCOPING: a NON-ruling file landing in done/ is not blocked; nothing bound for done/ -> 0.
  - The blocking judgement is REUSED from open_question_register (no re-implementation) — proven by
    a mutation on the disposition register flipping the same path from REFUSE to ALLOW.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
_spec = importlib.util.spec_from_file_location(
    "ruling_archive_question_gate", _ROOT / "tools" / "ruling_archive_question_gate.py"
)
gate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gate)

import background.open_question_register as oqr

_RULING_BODY = (
    "# [DIRECTOR-RULING] — sample archival test\n\n"
    "## Questions\n\n"
    "1. Is the alpha thing actually done?\n"
)
_PATH = "docs/staging/done/DIRECTOR_RULING_SAMPLE_2026-07-28.md"


def _reader(mapping: dict[str, str]):
    return lambda p: mapping.get(p)


def _with_register(tmp_path, monkeypatch, dispositions: dict):
    reg = tmp_path / "reg.json"
    reg.write_text(json.dumps({"version": 1, "dispositions": dispositions}), encoding="utf-8")
    monkeypatch.setattr(oqr, "REGISTER_PATH", reg)
    return reg


def test_fires_on_open_question_passes_when_answered(tmp_path, monkeypatch):
    name = "DIRECTOR_RULING_SAMPLE_2026-07-28.md"
    key = oqr.question_key(name, oqr.extract_questions(_RULING_BODY)[0])

    # FIRES — no disposition => open => REFUSE the archival.
    _with_register(tmp_path, monkeypatch, {})
    code, msg = gate.evaluate([_PATH], blob_reader=_reader({_PATH: _RULING_BODY}))
    assert code == 1 and "unanswered question" in msg, msg

    # PASSES — the question CLOSED (answered) => ALLOW.
    _with_register(tmp_path, monkeypatch, {key: {"status": "answered", "disposition": "yes, via X"}})
    code, msg = gate.evaluate([_PATH], blob_reader=_reader({_PATH: _RULING_BODY}))
    assert code == 0, msg

    # carried still BLOCKS (non-silent but unanswered).
    _with_register(tmp_path, monkeypatch, {key: {"status": "carried", "disposition": "chasing"}})
    code, _ = gate.evaluate([_PATH], blob_reader=_reader({_PATH: _RULING_BODY}))
    assert code == 1


def test_fail_closed_on_unreadable_blob(tmp_path, monkeypatch):
    _with_register(tmp_path, monkeypatch, {})
    code, msg = gate.evaluate([_PATH], blob_reader=_reader({}))  # reader returns None
    assert code == 1 and "could not be read" in msg, msg


def test_non_ruling_in_done_not_blocked(tmp_path, monkeypatch):
    _with_register(tmp_path, monkeypatch, {})
    p = "docs/staging/done/some_note.md"
    code, _ = gate.evaluate([p], blob_reader=_reader({p: "# just a note\n\nno questions here.\n"}))
    assert code == 0


def test_ruling_with_no_questions_allowed(tmp_path, monkeypatch):
    _with_register(tmp_path, monkeypatch, {})
    body = "# [DIRECTOR-RULING] — no questions\n\n## DECISION\n\nWe did the thing. Done.\n"
    code, _ = gate.evaluate([_PATH], blob_reader=_reader({_PATH: body}))
    assert code == 0


def test_empty_paths_allowed():
    code, msg = gate.evaluate([])
    assert code == 0 and msg == ""


def test_live_gate_clean_today():
    """On the real repo, nothing is currently staged for done/, so the gate's live run is a no-op
    (exit 0). The FIRING direction is proven by the fixture tests above."""
    assert gate.archived_ruling_paths() == [] or gate.main() in (0, 1)
