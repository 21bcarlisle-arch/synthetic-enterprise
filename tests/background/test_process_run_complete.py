"""Tests for background/process_run_complete.py."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import background.process_run_complete as prc


@pytest.fixture(autouse=True)
def _isolate_fingerprint_file(tmp_path_factory, monkeypatch):
    """Redirect the change-detection fingerprint file to a per-test temp path so
    no test reads or pollutes the real docs/observability/ file (same isolation
    discipline as .last_tested_hash). Tests that want the gate to fire write to
    prc.LAST_FINGERPRINT_FILE explicitly."""
    fp = tmp_path_factory.mktemp("fp") / ".last_processed_fingerprint.json"
    monkeypatch.setattr(prc, "LAST_FINGERPRINT_FILE", fp)


@pytest.fixture(autouse=True)
def _isolate_log_file(tmp_path_factory, monkeypatch):
    """Redirect prc.LOG_FILE to a per-test temp path for every test in this
    file -- made autouse (2026-07-11) after two tests (test_gate_skips_
    identical_run, test_gate_never_skips_admin_event) were found live to have
    called prc._process() without their own explicit monkeypatch, each
    writing real 'Processing run_complete_X.md'/'run_complete_Y.md' log lines
    straight into the production docs/observability/sim-runner-log.md during
    a real fast-test-suite gate run -- confirmed via direct grep, the exact
    literal marker names only exist in this test file. Same test-isolation-
    leak class as the tmux-scrollback retro. A per-test explicit
    monkeypatch.setattr(prc, "LOG_FILE", ...) elsewhere in this file is now
    redundant but harmless."""
    log_path = tmp_path_factory.mktemp("log") / "log.md"
    monkeypatch.setattr(prc, "LOG_FILE", log_path)


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


def _full_isolation_setup(tmp_path, monkeypatch):
    """Same isolation as test_main_success_flow, factored out for the
    force-republish tests below."""
    monkeypatch.setattr(prc, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(prc, "STAGING_DIR", tmp_path / "staging")
    monkeypatch.setattr(prc, "DONE_DIR", tmp_path / "staging" / "done")
    monkeypatch.setattr(prc, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(prc, "RUN_LOCK_FILE", tmp_path / ".process_run_complete.lock")
    monkeypatch.setattr(prc, "generate_dashboard_json", lambda p, git_hash="unknown": True)
    monkeypatch.setattr(prc, "LAST_TESTED_HASH_FILE", tmp_path / ".last_tested_hash")
    monkeypatch.setattr(prc, "RUN_INSIGHTS_PATH", tmp_path / "run_insights.json")
    monkeypatch.setattr(prc, "RUN_HISTORY_PATH", tmp_path / "run_history.json")
    monkeypatch.setattr(prc, "FORCE_REPUBLISH_FLAG", tmp_path / ".force_republish_once")
    latest_md = tmp_path / "LATEST.md"
    latest_md.write_text(
        "Last updated: 2026-01-01T00:00:00Z\n\n"
        "**Latest simulation results (2016-2025)** - auto-processed (0s / 0 min):\n"
        "- Net margin: old\n"
        "\n"
        "**Next section**\n"
    )
    monkeypatch.setattr(prc, "LATEST_MD", latest_md)

    def fake_run(cmd, **kwargs):
        m = MagicMock()
        m.returncode = 0
        return m
    monkeypatch.setattr(prc.subprocess, "run", fake_run)


# --- FORCE_REPUBLISH_FLAG -- no-orphan-transitions fix (2026-07-10,
# CLAIM_EQUALS_PIXEL.md/END_TO_END_VERIFICATION.md): a hold release must
# force a real republish, even when the fixed code's headline figures
# happen to fingerprint-match the last processed run ---

def test_change_detection_gate_skips_identical_run_when_not_forced(tmp_path, monkeypatch):
    _full_isolation_setup(tmp_path, monkeypatch)
    marker, json_data = make_marker(tmp_path)
    prc.LAST_FINGERPRINT_FILE.parent.mkdir(parents=True, exist_ok=True)
    fp = prc._run_fingerprint(json_data)
    fp["source_git_hash"] = "abc1234"  # matches make_marker()'s default git_hash -- genuinely nothing changed
    prc.LAST_FINGERPRINT_FILE.write_text(json.dumps(fp, sort_keys=True))

    rc = prc.main(str(marker))

    assert rc == 0
    assert (tmp_path / "staging" / "done" / marker.name).exists()
    assert not prc.LATEST_MD.read_text().count("Net margin: \xa3")  # LATEST.md never touched


def test_force_republish_flag_bypasses_identical_fingerprint(tmp_path, monkeypatch):
    """The exact regression: an identical-looking fingerprint must not skip
    processing when a hold was just released."""
    _full_isolation_setup(tmp_path, monkeypatch)
    marker, json_data = make_marker(tmp_path)
    prc.LAST_FINGERPRINT_FILE.parent.mkdir(parents=True, exist_ok=True)
    prc.LAST_FINGERPRINT_FILE.write_text(json.dumps(prc._run_fingerprint(json_data), sort_keys=True))
    prc.FORCE_REPUBLISH_FLAG.parent.mkdir(parents=True, exist_ok=True)
    prc.FORCE_REPUBLISH_FLAG.touch()

    rc = prc.main(str(marker))

    assert rc == 0
    assert "Net margin: \xa3" in prc.LATEST_MD.read_text()  # LATEST.md WAS regenerated


def test_force_republish_flag_consumed_exactly_once(tmp_path, monkeypatch):
    _full_isolation_setup(tmp_path, monkeypatch)
    marker, json_data = make_marker(tmp_path)
    prc.FORCE_REPUBLISH_FLAG.parent.mkdir(parents=True, exist_ok=True)
    prc.FORCE_REPUBLISH_FLAG.touch()

    prc.main(str(marker))

    assert not prc.FORCE_REPUBLISH_FLAG.exists()


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


# --- Change-detection gate (DIRECTOR_SEQUENCE_AND_TOKEN_ECONOMY.md, 2026-07-08) ---

def _sample_data(net=1535307.74):
    return {
        "total_net_gbp": net,
        "total_gross_gbp": 6452602.5,
        "enterprise_value_gbp": 8930210.95,
        "final_treasury_gbp": 3911893.89,
        "starting_treasury_gbp": 2466636.22,
        "total_capital_gbp": 51432.98,
        "net_margin_after_cost_to_serve_gbp": 6433342.81,
        "committee_wake_ups_total": 38,
        "bills_total": 1605,
        "retention_log": [{"outcome": "retained"}] * 14,
        "no_offer_churn_log": [{"r": 1}] * 6,
        "churned_billing_accounts": ["C%d" % i for i in range(6)],
        "administration_event": None,
    }


def test_fingerprint_stable_and_sensitive():
    a = prc._run_fingerprint(_sample_data())
    b = prc._run_fingerprint(_sample_data())
    assert a == b  # same inputs, same day -> identical fingerprint
    c = prc._run_fingerprint(_sample_data(net=999.99))
    assert c != a  # a changed headline figure must change the fingerprint
    assert a["retained"] == 14 and a["offers"] == 14


def test_fingerprint_roundtrip():
    assert prc._read_last_fingerprint() is None
    fp = prc._run_fingerprint(_sample_data())
    prc._write_last_fingerprint(fp)
    assert prc._read_last_fingerprint() == fp


def test_gate_skips_identical_run(tmp_path, monkeypatch):
    """An identical run is archived with no regen/test/commit."""
    staging = tmp_path / "staging"
    done = staging / "done"
    staging.mkdir(parents=True)
    done.mkdir()
    monkeypatch.setattr(prc, "STAGING_DIR", staging)
    monkeypatch.setattr(prc, "DONE_DIR", done)

    data = _sample_data()
    json_path = tmp_path / "run_output_latest.json"
    json_path.write_text(json.dumps(data))
    fp = prc._run_fingerprint(data)
    fp["source_git_hash"] = "abc"  # matches the marker's "Git: abc" below -- genuinely nothing changed
    prc._write_last_fingerprint(fp)

    marker = staging / "run_complete_X.md"
    marker.write_text("# Run Complete\n\nGit: abc\nJSON: %s\nDuration: 200s\n" % json_path)

    # Any pipeline step running is a gate failure — make report regen explode.
    monkeypatch.setattr(prc, "regenerate_report", lambda jp: pytest.fail("gate did not skip"))

    rc = prc._process(str(marker))
    assert rc == 0
    assert (done / marker.name).exists()  # archived
    assert not marker.exists()


def test_gate_never_skips_admin_event(tmp_path, monkeypatch):
    """An administration event always processes so the NTFY exception fires."""
    staging = tmp_path / "staging"
    done = staging / "done"
    staging.mkdir(parents=True)
    done.mkdir()
    monkeypatch.setattr(prc, "STAGING_DIR", staging)
    monkeypatch.setattr(prc, "DONE_DIR", done)

    data = _sample_data()
    data["administration_event"] = {"date": "2020-03-01"}
    json_path = tmp_path / "run_output_latest.json"
    json_path.write_text(json.dumps(data))
    prc._write_last_fingerprint(prc._run_fingerprint(data))

    marker = staging / "run_complete_Y.md"
    marker.write_text("# Run Complete\n\nGit: abc\nJSON: %s\nDuration: 200s\n" % json_path)

    # Reaching regen proves the gate did NOT skip; stop there to keep the test cheap.
    monkeypatch.setattr(prc, "regenerate_report", lambda jp: (_ for _ in ()).throw(SystemExit("proceeded")))
    with pytest.raises(SystemExit):
        prc._process(str(marker))


def test_gate_never_skips_when_git_hash_differs(tmp_path, monkeypatch):
    """R3 two-strike redesign (2026-07-12, director page comment: '/project/
    data looks stale'): a real new commit whose headline financial figures
    happen to be identical to the last processed run must NOT be silently
    skipped -- this is the exact class of incident FORCE_REPUBLISH_FLAG was
    built for (see above), recurring on an ordinary commit rather than a
    hold-release. Same fingerprint content, different producing commit."""
    staging = tmp_path / "staging"
    done = staging / "done"
    staging.mkdir(parents=True)
    done.mkdir()
    monkeypatch.setattr(prc, "STAGING_DIR", staging)
    monkeypatch.setattr(prc, "DONE_DIR", done)

    data = _sample_data()
    json_path = tmp_path / "run_output_latest.json"
    json_path.write_text(json.dumps(data))
    fp = prc._run_fingerprint(data)
    fp["source_git_hash"] = "old0000"  # a DIFFERENT commit than the marker below
    prc._write_last_fingerprint(fp)

    marker = staging / "run_complete_Z.md"
    marker.write_text("# Run Complete\n\nGit: new1111\nJSON: %s\nDuration: 200s\n" % json_path)

    # Reaching regen proves the gate did NOT skip; stop there to keep the test cheap.
    monkeypatch.setattr(prc, "regenerate_report", lambda jp: (_ for _ in ()).throw(SystemExit("proceeded")))
    with pytest.raises(SystemExit):
        prc._process(str(marker))


def test_gate_skips_when_git_hash_matches_too(tmp_path, monkeypatch):
    """Sanity converse of the above: identical fingerprint AND identical
    producing commit still skips -- the fix must not make the gate skip
    nothing at all."""
    staging = tmp_path / "staging"
    done = staging / "done"
    staging.mkdir(parents=True)
    done.mkdir()
    monkeypatch.setattr(prc, "STAGING_DIR", staging)
    monkeypatch.setattr(prc, "DONE_DIR", done)

    data = _sample_data()
    json_path = tmp_path / "run_output_latest.json"
    json_path.write_text(json.dumps(data))
    fp = prc._run_fingerprint(data)
    fp["source_git_hash"] = "same0000"
    prc._write_last_fingerprint(fp)

    marker = staging / "run_complete_W.md"
    marker.write_text("# Run Complete\n\nGit: same0000\nJSON: %s\nDuration: 200s\n" % json_path)

    monkeypatch.setattr(prc, "regenerate_report", lambda jp: pytest.fail("gate did not skip"))

    rc = prc._process(str(marker))
    assert rc == 0
    assert (done / marker.name).exists()


def test_git_commit_push_commits_whole_generated_site_data_surface(tmp_path, monkeypatch):
    """R10 class-closure regression (SITE1 Expert-Hour, 2026-07-16): every
    generated site/data/*.json must be staged, not an explicit per-file list
    that silently omits new ones. simplified.json / provisional_plan.json /
    system_status.json were each regenerated every run yet never committed --
    the live doors froze (the simplifications register hid ~42% of itself, the
    director queue went 6 days stale). This test FAILS if the glob is removed,
    so the class cannot recur unnoticed (R15: a control must be able to fail)."""
    monkeypatch.setattr(prc, "LAST_PUSH_FILE", tmp_path / ".last_push_time.json")
    monkeypatch.setattr(prc, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(prc, "LATEST_MD", tmp_path / "LATEST.md")

    data_dir = tmp_path / "site" / "data"
    data_dir.mkdir(parents=True)
    previously_orphaned = ["simplified.json", "provisional_plan.json", "system_status.json"]
    a_future_generated = "some_new_door.json"
    for name in previously_orphaned + [a_future_generated]:
        (data_dir / name).write_text("{}")

    added = []

    def fake_run(cmd, **kwargs):
        if cmd[:2] == ["git", "add"]:
            added.extend(cmd[2:])
        m = MagicMock()
        m.returncode = 0
        return m

    monkeypatch.setattr(prc.subprocess, "run", fake_run)

    prc.git_commit_push("abc1234", 1000.0)

    for name in previously_orphaned + [a_future_generated]:
        assert str(data_dir / name) in added, (
            "%s must be committed by the site/data glob, not silently orphaned" % name
        )
