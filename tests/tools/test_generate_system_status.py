"""Tests for tools/generate_system_status.py.

Coverage for PROJECT_TAB_OVERHAUL.md item 3 (System-tab elevation): session
history/exit-reasons from the watchdog log, staging queue state, and a
git-commit-measured burn line (explicitly NOT the hand-maintained
token-log.md, which is a manual estimate rather than a metered figure).
"""
import json

from tools.generate_system_status import (
    _parse_boundary_events,
    _build_sessions,
    _continuity,
    generate,
)


SAMPLE_LOG = (
    "- [2026-07-05 06:59 UTC] Session watchdog started (auto-restart mode)\n"
    "- [2026-07-05 06:59 UTC] Session idle — sending autoloop continuation instruction\n"
    "- [2026-07-05 07:04 UTC] Session ended — reason: completion | clean exit\n"
    "- [2026-07-05 07:04 UTC] Session ended (completion/unknown) — restarting without NTFY\n"
    "- [2026-07-05 07:05 UTC] Claude Code restarted (1/3 this hour, direct launch)\n"
    "- [2026-07-05 07:20 UTC] Claude Code restarted (2/3 this hour, direct launch)\n"
)


def test_parse_boundary_events_extracts_start_and_end_only():
    events = _parse_boundary_events(SAMPLE_LOG)
    assert events == [
        ("start", "2026-07-05 06:59", None),
        ("end", "2026-07-05 07:04", "completion"),
        ("start", "2026-07-05 07:05", None),
        ("start", "2026-07-05 07:20", None),
    ]


def test_build_sessions_pairs_start_with_explicit_end():
    events = _parse_boundary_events(SAMPLE_LOG)
    sessions, current = _build_sessions(events)
    assert sessions[0]["started_at"] == "2026-07-05 06:59"
    assert sessions[0]["ended_at"] == "2026-07-05 07:04"
    assert sessions[0]["exit_reason"] == "completion"
    assert sessions[0]["duration_minutes"] == 5.0


def test_build_sessions_labels_implicit_restart_honestly_not_fabricated():
    events = _parse_boundary_events(SAMPLE_LOG)
    sessions, current = _build_sessions(events)
    implicit = sessions[1]
    assert implicit["started_at"] == "2026-07-05 07:05"
    assert implicit["ended_at"] == "2026-07-05 07:20"
    assert implicit["exit_reason"] == "unknown (restarted)"


def test_build_sessions_leaves_final_start_as_current_session():
    events = _parse_boundary_events(SAMPLE_LOG)
    sessions, current = _build_sessions(events)
    assert len(sessions) == 2
    assert current == {"started_at": "2026-07-05 07:20"}


def test_build_sessions_empty_log_yields_nothing():
    sessions, current = _build_sessions([])
    assert sessions == []
    assert current is None


def test_continuity_counts_exit_reasons():
    events = _parse_boundary_events(SAMPLE_LOG)
    sessions, current = _build_sessions(events)
    c = _continuity(sessions, current)
    assert c["total_sessions_parsed"] == 2
    assert c["exit_reason_counts"]["completion"] == 1
    assert c["exit_reason_counts"]["unknown (restarted)"] == 1
    assert c["current_session_uptime_minutes"] is not None


def test_generate_writes_json_with_expected_top_level_keys(tmp_path, monkeypatch):
    log_file = tmp_path / "log.md"
    log_file.write_text(SAMPLE_LOG)
    staging_dir = tmp_path / "staging"
    staging_dir.mkdir()
    (staging_dir / "SOME_PROPOSAL.md").write_text("hello")
    out_file = tmp_path / "system_status.json"

    monkeypatch.setattr("tools.generate_system_status.WATCHDOG_LOG", log_file)
    monkeypatch.setattr("tools.generate_system_status.STAGING_DIR", staging_dir)
    monkeypatch.setattr("tools.generate_system_status.OUT_PATH", out_file)
    monkeypatch.setattr("tools.generate_system_status._commit_burn", lambda days=30: [["2026-07-05", 3]])

    assert generate() is True
    data = json.loads(out_file.read_text())
    assert set(data.keys()) == {
        "generated_at", "session_history", "current_session",
        "staging_queue", "commit_burn", "continuity",
    }
    assert data["staging_queue"] == [{
        "filename": "SOME_PROPOSAL.md",
        "modified_at": data["staging_queue"][0]["modified_at"],
        "size_bytes": 5,
    }]
    assert data["commit_burn"] == [["2026-07-05", 3]]
    assert len(data["session_history"]) == 2


def test_generate_handles_missing_log_gracefully(tmp_path, monkeypatch):
    monkeypatch.setattr("tools.generate_system_status.WATCHDOG_LOG", tmp_path / "nope.md")
    monkeypatch.setattr("tools.generate_system_status.STAGING_DIR", tmp_path / "nope_dir")
    monkeypatch.setattr("tools.generate_system_status.OUT_PATH", tmp_path / "out.json")
    assert generate() is True
    data = json.loads((tmp_path / "out.json").read_text())
    assert data["session_history"] == []
    assert data["staging_queue"] == []
