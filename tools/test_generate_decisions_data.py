"""Independence + fail-closed tests for tools/generate_decisions_data.py (R15).

The Decisions-tab payload must be DERIVED from the real ledger
(docs/observability/decision_log.jsonl via background.decision_log), never a
relocated hardcode. These tests prove derivation by pointing `derive_decisions`
at an injected, mutated ledger file and asserting the emitted JSON follows it,
and prove the fail-closed contract (R15 FAIL-OPEN killer pattern): a missing
or empty ledger must emit `available: false`, never a silently-empty list
that looks the same as "nothing to report."
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT))
sys.path.insert(0, str(PROJECT / "tools"))

import generate_decisions_data as G  # noqa: E402


def _write_log(path: Path, entries: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(e, sort_keys=True) for e in entries) + "\n")


def _entry(what: str, **kw) -> dict:
    base = {
        "timestamp": kw.pop("timestamp", "2026-07-01T00:00:00+00:00"),
        "what": what,
        "why": kw.pop("why", "why"),
        "how_to_reverse": kw.pop("how_to_reverse", "git revert"),
        "reversible": kw.pop("reversible", True),
        "confidence": kw.pop("confidence", "confident"),
    }
    base.update(kw)
    return base


# ---------------------------------------------------------------------------
# Fail-closed: missing / empty ledger -> available:false, never a silent empty
# ---------------------------------------------------------------------------
def test_missing_ledger_is_fail_closed(tmp_path):
    data = G.derive_decisions(log_path=tmp_path / "does_not_exist.jsonl")
    assert data["available"] is False
    assert data["count"] == 0
    assert data["decisions"] == []
    assert "note" in data and data["note"]


def test_empty_ledger_is_fail_closed(tmp_path):
    log = tmp_path / "decision_log.jsonl"
    log.write_text("")
    data = G.derive_decisions(log_path=log)
    assert data["available"] is False
    assert data["count"] == 0


def test_malformed_lines_are_skipped_not_fatal(tmp_path):
    log = tmp_path / "decision_log.jsonl"
    log.write_text("not json\n" + json.dumps(_entry("real one")) + "\n")
    data = G.derive_decisions(log_path=log)
    assert data["available"] is True
    assert data["count"] == 1
    assert data["decisions"][0]["what"] == "real one"


# ---------------------------------------------------------------------------
# R15 independence: emitted content follows the injected ledger, not a
# relocated hardcode
# ---------------------------------------------------------------------------
def test_count_and_fields_follow_injected_ledger(tmp_path):
    log = tmp_path / "decision_log.jsonl"
    _write_log(log, [
        _entry("SENTINEL_ALPHA", timestamp="2026-01-01T00:00:00+00:00",
               why="why-alpha", how_to_reverse="revert-alpha",
               reversible=True, confidence="confident"),
        _entry("SENTINEL_BETA", timestamp="2026-01-02T00:00:00+00:00",
               why="why-beta", how_to_reverse="revert-beta",
               reversible=True, confidence="ambiguous_reversible"),
    ])
    data = G.derive_decisions(log_path=log)
    assert data["available"] is True
    assert data["count"] == 2
    # Newest-first ordering: the log is append-only oldest-first on disk.
    assert data["decisions"][0]["what"] == "SENTINEL_BETA"
    assert data["decisions"][1]["what"] == "SENTINEL_ALPHA"
    assert data["decisions"][0]["confidence"] == "ambiguous_reversible"
    assert data["decisions"][0]["why"] == "why-beta"
    assert data["decisions"][0]["how_to_reverse"] == "revert-beta"


def test_count_follows_ledger_size_change(tmp_path):
    log = tmp_path / "decision_log.jsonl"
    _write_log(log, [_entry(f"D{i}") for i in range(7)])
    data = G.derive_decisions(log_path=log)
    assert data["count"] == 7
    _write_log(log, [_entry(f"D{i}") for i in range(3)])
    data2 = G.derive_decisions(log_path=log)
    assert data2["count"] == 3, "count must track the ledger, not stay stuck at a prior value"


def test_generated_at_stamp_shape(tmp_path):
    log = tmp_path / "decision_log.jsonl"
    _write_log(log, [_entry("x")])
    now = datetime(2026, 7, 19, 6, 0, 0, tzinfo=timezone.utc)
    data = G.derive_decisions(log_path=log, now=now)
    assert data["generated_at"] == "2026-07-19T06:00:00Z"


def test_source_path_is_the_real_ledger_path():
    assert G.SOURCE_REL == "docs/observability/decision_log.jsonl"


def test_live_ledger_reads_via_background_decision_log():
    # No injected path -> reads the real project ledger through
    # background.decision_log.read_decision_log(), per the build instruction.
    data = G.derive_decisions()
    assert data["source"] == "docs/observability/decision_log.jsonl"
    # The live ledger has entries from this project's own history -- if this
    # ever regresses to empty, the fail-closed path (asserted above) is the
    # honest outcome, not a crash; here we just check the happy path shape.
    if data["available"]:
        assert data["count"] > 0
        assert all(
            {"timestamp", "what", "why", "how_to_reverse", "reversible", "confidence"} <= d.keys()
            for d in data["decisions"]
        )
