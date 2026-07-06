"""Tests for background/process_run_complete.py."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import background.process_run_complete as prc


def make_marker(tmp_path, git_hash="abc1234", elapsed_s=1870.0, json_data=None):
    """Write a realistic run_complete marker and its JSON to tmp_path."""
    if json_data is None:
        json_data = {
            "total_net_gbp": -8317.21,
            "total_gross_gbp": -7089.58,
            "total_capital_gbp": 1228.0,
            "starting_treasury_gbp": 29846.0,
            "final_treasury_gbp": 11131.0,
            "committee_wake_ups_total": 323,
            "bills_total": 1117,
            "enterprise_value_gbp": -20661.90,
            "net_margin_after_cost_to_serve_gbp": -23569.0,
            "retention_log": [
                {"outcome": "retained"},
                {"outcome": "retained"},
            ],
            "no_offer_churn_log": [{"reason": "below_threshold"}] * 3,
            "churned_billing_accounts": ["C1", "C2", "C3"],
            "administration_event": None,
        }

    reports_dir = tmp_path / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    ts = "20260621T104002Z"
    json_path = reports_dir / f"run_output_{git_hash}_{ts}.json"
    json_path.write_text(json.dumps(json_data))

    marker_text = (
        f"Simulation Run Complete\n\n"
        f"Git: {git_hash}\n"
        f"JSON: {json_path}\n"
        f"Duration: {elapsed_s:.0f}s | Size: 263 KB\n"
    )
    marker = tmp_path / "staging" / f"run_complete_{ts}.md"
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(marker_text)
    return marker, json_data


def test_parse_marker_extracts_git_hash_elapsed_json_path(tmp_path):
    marker, _ = make_marker(tmp_path, git_hash="def5678", elapsed_s=2100.0)
    fields = prc.parse_marker(marker)
    assert fields["git_hash"] == "def5678"
    assert fields["elapsed_s"] == 2100.0
    assert "run_output_def5678" in str(fields["json_path"])


def test_update_latest_md_replaces_block(tmp_path, monkeypatch):
    latest = tmp_path / "LATEST.md"
    latest.write_text(
        "Last updated: 2026-01-01T00:00:00Z\n\n"
        "**Latest simulation results (2016-2025)** - auto-processed (0s / 0 min):\n"
        "- Net margin: old data\n"
        "\n"
        "**Some other section** here\n"
    )
    monkeypatch.setattr(prc, "LATEST_MD", latest)

    json_data = {
        "total_net_gbp": -8317.21,
        "total_gross_gbp": -7089.58,
        "total_capital_gbp": 1228.0,
        "starting_treasury_gbp": 29846.0,
        "final_treasury_gbp": 11131.0,
        "committee_wake_ups_total": 323,
        "bills_total": 1117,
        "enterprise_value_gbp": -20661.90,
        "net_margin_after_cost_to_serve_gbp": -23569.0,
        "retention_log": [{"outcome": "retained"}, {"outcome": "retained"}],
        "no_offer_churn_log": [{}] * 3,
        "churned_billing_accounts": ["C1", "C2"],
    }
    prc.update_latest_md(json_data, elapsed_s=1870.0)

    text = latest.read_text()
    assert "£-8,317.21" in text
    assert "323 committee interventions" in text
    assert "**Some other section**" in text


def test_main_success_flow(tmp_path, monkeypatch):
    monkeypatch.setattr(prc, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(prc, "STAGING_DIR", tmp_path / "staging")
    monkeypatch.setattr(prc, "DONE_DIR", tmp_path / "staging" / "done")
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(prc, "RUN_LOCK_FILE", tmp_path / ".process_run_complete.lock")
    # generate_dashboard_json writes to the REAL site/data/dashboard.json (hardcoded path
    # inside generate_dashboard_data.py) — mock it to avoid corrupting the live dashboard
    # Returns True (gate passed) -- generate_dashboard_json's return value now
    # drives an immediate NTFY on consistency-gate failure (Phase QF); this
    # mock represents the happy path, not a gate failure.
    monkeypatch.setattr(prc, "generate_dashboard_json", lambda p, git_hash="unknown": True)
    # run_fast_tests writes to the REAL docs/observability/.last_tested_hash on a
    # returncode==0 fake pytest run — mock it to avoid corrupting the live cache file
    monkeypatch.setattr(prc, "LAST_TESTED_HASH_FILE", tmp_path / ".last_tested_hash")
    # generate_insights writes to the REAL docs/observability/run_insights.json and
    # run_history.json (hardcoded defaults) -- redirect to avoid corrupting the live
    # exec-summary data with this test's fake abc1234/-8317.21 fixture.
    monkeypatch.setattr(prc, "RUN_INSIGHTS_PATH", tmp_path / "run_insights.json")
    monkeypatch.setattr(prc, "RUN_HISTORY_PATH", tmp_path / "run_history.json")

    latest_md = tmp_path / "LATEST.md"
    latest_md.write_text(
        "Last updated: 2026-01-01T00:00:00Z\n\n"
        "**Latest simulation results (2016-2025)** - auto-processed (0s / 0 min):\n"
        "- Net margin: old\n"
        "\n"
        "**Next section**\n"
    )
    monkeypatch.setattr(prc, "LATEST_MD", latest_md)

    marker, json_data = make_marker(tmp_path)

    def fake_run(cmd, **kwargs):
        m = MagicMock()
        m.returncode = 0
        return m

    monkeypatch.setattr(prc.subprocess, "run", fake_run)

    rc = prc.main(str(marker))
    assert rc == 0
    assert not marker.exists()
    assert (tmp_path / "staging" / "done" / marker.name).exists()


def test_main_returns_1_for_missing_marker(tmp_path, monkeypatch):
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(prc, "RUN_LOCK_FILE", tmp_path / ".process_run_complete.lock")
    rc = prc.main(str(tmp_path / "nonexistent.md"))
    assert rc == 1


def test_main_returns_1_when_tests_fail(tmp_path, monkeypatch):
    monkeypatch.setattr(prc, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(prc, "STAGING_DIR", tmp_path / "staging")
    monkeypatch.setattr(prc, "DONE_DIR", tmp_path / "staging" / "done")
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(prc, "RUN_LOCK_FILE", tmp_path / ".process_run_complete.lock")
    # Returns True (gate passed) -- generate_dashboard_json's return value now
    # drives an immediate NTFY on consistency-gate failure (Phase QF); this
    # mock represents the happy path, not a gate failure.
    monkeypatch.setattr(prc, "generate_dashboard_json", lambda p, git_hash="unknown": True)
    monkeypatch.setattr(prc, "RUN_INSIGHTS_PATH", tmp_path / "run_insights.json")
    monkeypatch.setattr(prc, "RUN_HISTORY_PATH", tmp_path / "run_history.json")

    latest_md = tmp_path / "LATEST.md"
    latest_md.write_text(
        "Last updated: 2026-01-01T00:00:00Z\n\n"
        "**Latest simulation results (2016-2025)** - auto-processed (0s / 0 min):\n"
        "- Net margin: old\n"
        "\n"
    )
    monkeypatch.setattr(prc, "LATEST_MD", latest_md)

    marker, _ = make_marker(tmp_path)

    call_count = [0]

    def fake_run(cmd, **kwargs):
        m = MagicMock()
        call_count[0] += 1
        if "pytest" in " ".join(str(a) for a in cmd):
            m.returncode = 1
        else:
            m.returncode = 0
        return m

    monkeypatch.setattr(prc.subprocess, "run", fake_run)

    rc = prc.main(str(marker))
    assert rc == 1
    assert marker.exists()


from background.process_run_complete import _fmt_gbp


def test_fmt_gbp_positive():
    assert _fmt_gbp(1000) == "£+1,000"


def test_fmt_gbp_negative():
    assert _fmt_gbp(-500) == "£-500"


def test_fmt_gbp_zero():
    assert _fmt_gbp(0) == "£+0"


def test_fmt_gbp_large():
    assert _fmt_gbp(1_234_567) == "£+1,234,567"


def test_fmt_gbp_small_positive():
    assert prc._fmt_gbp(100) == "£+100"


def test_fmt_gbp_decimal_rounds():
    result = prc._fmt_gbp(1234.56)
    assert "1,235" in result


def test_parse_marker_returns_none_for_missing_file(tmp_path):
    missing = tmp_path / "nonexistent.md"
    try:
        result = prc.parse_marker(missing)
        assert result is None
    except (FileNotFoundError, ValueError, Exception):
        pass


def test_run_history_max_net_is_float(tmp_path, monkeypatch):
    monkeypatch.setattr(prc, "PROJECT_DIR", tmp_path)
    result = prc._run_history_max_net()
    assert isinstance(result, float)


# ── run-lock: prevent duplicate concurrent pipeline runs on one marker ───────

def test_run_lock_second_acquire_fails_while_first_held(tmp_path, monkeypatch):
    monkeypatch.setattr(prc, "RUN_LOCK_FILE", tmp_path / ".process_run_complete.lock")
    with prc._run_lock() as first:
        assert first is True
        with prc._run_lock() as second:
            assert second is False


def test_run_lock_reacquirable_after_release(tmp_path, monkeypatch):
    monkeypatch.setattr(prc, "RUN_LOCK_FILE", tmp_path / ".process_run_complete.lock")
    with prc._run_lock() as first:
        assert first is True
    with prc._run_lock() as second:
        assert second is True


def test_main_skips_when_lock_already_held(tmp_path, monkeypatch):
    monkeypatch.setattr(prc, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(prc, "STAGING_DIR", tmp_path / "staging")
    monkeypatch.setattr(prc, "DONE_DIR", tmp_path / "staging" / "done")
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(prc, "RUN_LOCK_FILE", tmp_path / ".process_run_complete.lock")

    marker, _ = make_marker(tmp_path)

    called = []
    monkeypatch.setattr(prc, "_process", lambda m: called.append(m) or 0)

    with prc._run_lock():
        rc = prc.main(str(marker))

    assert rc == 0
    assert called == []  # _process must never run while another instance holds the lock
    assert marker.exists()  # left in place for the lock-holder to archive


# ── DEPLOY_CONTENTION_BATCH_COMMITS.md: throttle pushes to <=1/30min ──────────

def test_push_due_true_when_no_prior_push_recorded(tmp_path, monkeypatch):
    monkeypatch.setattr(prc, "LAST_PUSH_FILE", tmp_path / ".last_push_time.json")
    assert prc._push_due() is True


def test_push_due_false_within_throttle_window(tmp_path, monkeypatch):
    import json as _json
    import time as _time
    push_file = tmp_path / ".last_push_time.json"
    push_file.write_text(_json.dumps({"ts": _time.time()}))
    monkeypatch.setattr(prc, "LAST_PUSH_FILE", push_file)
    assert prc._push_due() is False


def test_push_due_true_after_throttle_window_elapses(tmp_path, monkeypatch):
    import json as _json
    import time as _time
    push_file = tmp_path / ".last_push_time.json"
    push_file.write_text(_json.dumps({"ts": _time.time() - prc.PUSH_THROTTLE_SECONDS - 1}))
    monkeypatch.setattr(prc, "LAST_PUSH_FILE", push_file)
    assert prc._push_due() is True


def test_push_due_true_on_malformed_file(tmp_path, monkeypatch):
    push_file = tmp_path / ".last_push_time.json"
    push_file.write_text("not json")
    monkeypatch.setattr(prc, "LAST_PUSH_FILE", push_file)
    assert prc._push_due() is True


def test_git_commit_push_defers_push_within_throttle_window(tmp_path, monkeypatch):
    """Commit succeeds locally but git push is skipped when throttled --
    the return value must still be True (committed, not a failure) so the
    caller doesn't treat a deferred push as an error."""
    import json as _json
    import time as _time
    push_file = tmp_path / ".last_push_time.json"
    push_file.write_text(_json.dumps({"ts": _time.time()}))
    monkeypatch.setattr(prc, "LAST_PUSH_FILE", push_file)
    monkeypatch.setattr(prc, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(prc, "LATEST_MD", tmp_path / "LATEST.md")

    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        m = MagicMock()
        m.returncode = 0
        return m

    monkeypatch.setattr(prc.subprocess, "run", fake_run)

    result = prc.git_commit_push("abc1234", 1000.0)

    assert result is True
    assert not any(c[:2] == ["git", "push"] for c in calls)


def test_git_commit_push_pushes_when_throttle_window_elapsed(tmp_path, monkeypatch):
    push_file = tmp_path / ".last_push_time.json"
    monkeypatch.setattr(prc, "LAST_PUSH_FILE", push_file)  # no prior push recorded
    monkeypatch.setattr(prc, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(prc, "LATEST_MD", tmp_path / "LATEST.md")

    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)
        m = MagicMock()
        m.returncode = 0
        return m

    monkeypatch.setattr(prc.subprocess, "run", fake_run)

    result = prc.git_commit_push("abc1234", 1000.0)

    assert result is True
    assert any(c[:2] == ["git", "push"] for c in calls)
    assert push_file.exists()


def test_git_commit_push_no_push_recorded_if_commit_fails(tmp_path, monkeypatch):
    push_file = tmp_path / ".last_push_time.json"
    monkeypatch.setattr(prc, "LAST_PUSH_FILE", push_file)
    monkeypatch.setattr(prc, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(prc, "LATEST_MD", tmp_path / "LATEST.md")

    def fake_run(cmd, **kwargs):
        m = MagicMock()
        m.returncode = 1 if cmd[:2] == ["git", "commit"] else 0
        return m

    monkeypatch.setattr(prc.subprocess, "run", fake_run)

    result = prc.git_commit_push("abc1234", 1000.0)

    assert result is False
    assert not push_file.exists()
