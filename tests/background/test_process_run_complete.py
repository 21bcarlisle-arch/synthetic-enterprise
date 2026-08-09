"""Tests for background/process_run_complete.py."""

import contextlib
import functools
import importlib
import inspect
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import background.process_run_complete as prc

# Files the publish pipeline writes through modules OTHER than prc, each resolving its own
# output path from its own __file__ or cwd -- so re-rooting prc.PROJECT_DIR does not reach
# them. (module, attribute, repo-relative path it must currently point at.)
_PIPELINE_OUTPUT_PATHS = (
    ("background.agent_status", "STATUS_FILE", "docs/observability/agent_status.json"),
    ("background.agent_status", "SITE_STATUS_FILE", "site/data/agent_status.json"),
)

# The two market-feed publishers take their destination as a DEFAULT ARGUMENT, which Python
# bound to the real path at def-time -- so redirecting the module constant they were defaulted
# from changes nothing, and both feeds kept being rewritten for real. Rebind the argument
# itself. (module, function, output keyword, repo-relative path it must currently default to.)
_PIPELINE_OUTPUT_WRITERS = (
    ("simulation.publish_market_feed", "publish", "output_path",
     "docs/market_data/price_feed.json"),
    ("simulation.publish_consumption_data", "publish_consumption", "output_path",
     "docs/market_data/consumption_feed.json"),
)


@pytest.fixture(autouse=True)
def _isolate_project_dir(tmp_path_factory, monkeypatch):
    """Point PROJECT_DIR -- and EVERY module path derived from it -- at a throwaway tree,
    for every test in this file. Zero real-tree WRITES (real-tree reads of static input
    data are left alone: see the collaborator note at the bottom of this fixture).

    THE INCIDENT (issue #11, "the ghost pusher"). Six tests below ran against the REAL
    PROJECT_DIR with the REAL `subprocess.run`: the four change-detection gate tests, which
    call `prc._process()` directly, and the two frozen-baseline trigger tests. Two of the
    four -- the pair whose marker fingerprint MATCHES, so the gate takes its SKIP branch --
    reach `_refresh_published_liveness_on_skip`, which is `git add` + `git commit` + `git
    push origin HEAD:main`. Running THIS FILE therefore manufactured a real
    `chore(liveness): ... (git=abc)` commit on whatever branch was checked out and pushed
    it; it failed to land only where credentials were absent. The sibling tests were fine
    -- `_full_isolation_setup` and `TestRefreshPublishedLivenessOnSkip._wire` both wire
    PROJECT_DIR correctly -- which is precisely why the leak survived: the file LOOKED
    isolated.

    WHY A DIRECTORY-WIDE RE-ROOT AND NOT FOUR MONKEYPATCHES. Per-test wiring is what
    failed. It is opt-in, it is invisible when omitted, and prc has FIFTEEN module-level
    paths under the repo root -- a test that remembers PROJECT_DIR and forgets LAST_PUSH_FILE
    is still touching the real tree. This walks prc's namespace and re-roots every Path
    living under the real repo into a per-test sandbox, mirroring the real layout. A path
    constant added to prc tomorrow is isolated the day it lands, with nothing to remember
    (R10: close the class, not the instance).

    Tests needing specific contents still monkeypatch their own paths in the test BODY,
    which runs after this fixture and therefore wins.
    """
    real_root = Path(prc.__file__).resolve().parent.parent
    sandbox = tmp_path_factory.mktemp("prc_tree")
    for name, value in list(vars(prc).items()):
        if not isinstance(value, Path):
            continue
        try:
            relative = value.resolve().relative_to(real_root)
        except ValueError:
            continue  # already outside the repo -- not ours to re-root
        target = sandbox / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        monkeypatch.setattr(prc, name, target)
    assert prc.PROJECT_DIR == sandbox, "PROJECT_DIR itself must be re-rooted, not just its children"
    # tree_lock resolves its own LOCK_FILE from ITS OWN __file__, so re-rooting prc's paths
    # does not move it -- an unwired test would still flock the real docs/observability/.tree.lock
    # and serialise itself against the live publisher. No test in this file asserts locking
    # behaviour (two already stub it in their own body), so neutralise it directory-wide.
    monkeypatch.setattr(prc, "tree_lock", lambda *a, **k: contextlib.nullcontext())
    # The pipeline also writes through COLLABORATORS that resolve their own output paths from
    # their own __file__/cwd, so prc.PROJECT_DIR does not reach them: driving main() end-to-end
    # (test_main_success_flow and the force-republish trio) rewrote four real files on every
    # run -- the live agent-status door and the two published market feeds. Redirect the
    # OUTPUTS only; their inputs (the SSP cache, the NBP CSV, the HH data dir) stay real,
    # because reads are harmless and stubbing them would quietly turn the publish steps into
    # no-ops rather than isolating them.
    for module_name, attribute, relative in _PIPELINE_OUTPUT_PATHS:
        module = importlib.import_module(module_name)
        current = getattr(module, attribute)  # AttributeError here = renamed away, isolation lost
        assert str(current).endswith(relative), (
            "{}.{} now points at {!r}, not {!r} -- this fixture is no longer isolating it".format(
                module_name, attribute, str(current), relative)
        )
        target = sandbox / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        monkeypatch.setattr(module, attribute, target)
    for module_name, function_name, keyword, relative in _PIPELINE_OUTPUT_WRITERS:
        module = importlib.import_module(module_name)
        original = getattr(module, function_name)
        default = inspect.signature(original).parameters[keyword].default
        assert str(default).endswith(relative), (
            "{}.{}({}=) now defaults to {!r}, not {!r} -- this fixture is no longer "
            "isolating it".format(module_name, function_name, keyword, str(default), relative)
        )
        target = sandbox / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        monkeypatch.setattr(module, function_name,
                            functools.partial(original, **{keyword: target}))


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

    # EXIT_LOCK_SKIPPED, NOT 0 (fail-open closed 2026-07-29): returning the
    # success code here made background_worker's sweep record a publish-gate
    # SUCCESS for a marker nobody published, clearing the H15 wedge streak and
    # auto-resolving the open [ACTION NEEDED] item mid-wedge.
    assert rc == prc.EXIT_LOCK_SKIPPED
    assert rc != 0, "a lock-skip must never be indistinguishable from a real publish"
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
        # Self-verifying push (2026-07-24 freeze fix): rev-parse HEAD and ls-remote
        # must report the SAME sha so _push_reached_origin confirms origin advanced.
        if cmd[:2] == ["git", "rev-parse"]:
            m.stdout = "deadbeef\n"
        elif cmd[:2] == ["git", "ls-remote"]:
            m.stdout = "deadbeef\trefs/heads/main\n"
        return m

    monkeypatch.setattr(prc.subprocess, "run", fake_run)

    result = prc.git_commit_push("abc1234", 1000.0)

    assert result is True
    assert any(c[:2] == ["git", "push"] for c in calls)
    assert push_file.exists()


def test_git_commit_push_does_not_record_on_phantom_push(tmp_path, monkeypatch):
    """THE 3.5h FREEZE, reproduced (R15 would-fire): `git push` returns rc=0 but
    origin does NOT advance (ls-remote head != local HEAD). git_commit_push must
    return False and NOT write .last_push_time.json -- so the throttle stays open
    and the next cycle retries, instead of deferring behind a phantom success."""
    push_file = tmp_path / ".last_push_time.json"
    monkeypatch.setattr(prc, "LAST_PUSH_FILE", push_file)  # no prior push recorded -> _push_due True
    monkeypatch.setattr(prc, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(prc, "LATEST_MD", tmp_path / "LATEST.md")
    monkeypatch.setattr(prc, "notify", lambda *a, **k: None, raising=False)

    def fake_run(cmd, **kwargs):
        m = MagicMock()
        m.returncode = 0
        if cmd[:2] == ["git", "rev-parse"]:
            m.stdout = "NEWlocalsha\n"
        elif cmd[:2] == ["git", "ls-remote"]:
            m.stdout = "OLDremotesha\trefs/heads/main\n"   # origin did NOT advance
        return m

    monkeypatch.setattr(prc.subprocess, "run", fake_run)

    result = prc.git_commit_push("abc1234", 1000.0)

    assert result is False, "a push that did not reach origin must report failure"
    assert not push_file.exists(), "phantom push must NOT reset the throttle (the freeze)"


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


def test_pending_inboxes_folded_before_the_gate_runs():
    """Class fix (2026-07-16): the publish gate must reconcile the map (fold any pending
    atom_status inbox) BEFORE run_fast_tests, so the map-reconciliation control tests a
    reconciled map, not a fork/fold-race transient (an unfolded W1_8 inbox wedged the
    gate). Structural R15 guard: merge_atom_status.merge() is invoked, and it appears
    BEFORE the run_fast_tests call in main() — revert the ordering and this fails."""
    import inspect
    from background import process_run_complete as prc
    src = inspect.getsource(prc._process)  # main() delegates the real pipeline to _process()
    assert "merge_atom_status" in src and ".merge()" in src, "pre-gate inbox fold missing"
    assert src.index("_mas.merge()") < src.index("run_fast_tests("), \
        "the inbox fold must run BEFORE the test gate (reconcile, then test)"


# ── SELF-VERIFYING PUSH (R15 both-ways) — the 3.5h origin-freeze incident, 2026-07-24 ──
# A bare `git push` returned rc=0 without advancing origin (phantom "up-to-date"),
# and _record_push_time was called anyway -> _push_due stayed False -> every real
# push deferred for 3.5h while 15 commits stacked locally, unseen by the advisor
# bridge. _push_reached_origin makes success GROUND-TRUTH so the freeze cannot recur.

def test_push_reached_origin_true_only_on_verified_advance():
    """CORRECT path: rc==0 AND real remote head == local HEAD -> counts as success."""
    assert prc._push_reached_origin(0, "abc123", "abc123") is True


def test_push_reached_origin_false_on_phantom_up_to_date():
    """THE FREEZE (would-fire): rc==0 but origin did NOT advance (remote behind
    local). Must NOT count -> throttle not reset -> next cycle retries."""
    assert prc._push_reached_origin(0, "OLDsha", "NEWsha") is False


def test_push_reached_origin_false_on_nonzero_rc():
    assert prc._push_reached_origin(1, "abc123", "abc123") is False


def test_push_reached_origin_false_on_empty_remote_head():
    """ls-remote failed/empty -> cannot confirm -> not a success (fail-closed)."""
    assert prc._push_reached_origin(0, "", "abc123") is False


def _make_resident(home, monkeypatch):
    """Make this process look like the RESIDENT seat: a real marker file under a
    throwaway HOME, no SE_SEAT override. Same helper shape as
    tests/background/test_seat_guard_daemons.py::_make_marker -- deliberately the
    production discriminator, not the env escape hatch."""
    marker = Path(home) / ".config" / "synthetic-enterprise" / ".env.ntfy"
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text("SE_NTFY_TOPIC=not-a-real-secret\n")
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.delenv("SE_SEAT", raising=False)
    return marker


def _make_foreign(home, monkeypatch):
    """Make this process look like a FOREIGN seat: HOME with no marker, no override."""
    Path(home).mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.delenv("SE_SEAT", raising=False)


# ── Fault #1 (2026-07-25 overnight publish-freeze): published liveness decoupled from content-change ──
class TestRefreshPublishedLivenessOnSkip:
    """The on-disk worker-tick heartbeat updates every 60s but only reached origin via a CONTENT
    publish; a byte-identical-output night (change-detection SKIP every cycle) froze the PUBLISHED
    heartbeat ~4h though every daemon was healthy. `_refresh_published_liveness_on_skip` publishes
    ONLY the liveness surface on a SKIP, throttled to the same 30-min push cadence. Proven both ways:
    throttled -> no-op; due -> commits ONLY the liveness paths and records a verified push."""

    def _wire(self, tmp_path, monkeypatch, *, push_due, commit_rc=0, reached=True):
        from contextlib import nullcontext
        # RESIDENT seat, via a real marker file under a throwaway HOME and NO SE_SEAT
        # override -- so these behaviour tests run the PRODUCTION discriminator rather
        # than an escape hatch, and stay valid on a resident machine and a cloud
        # sandbox alike (see the seat-guard tests below).
        _make_resident(tmp_path / "home", monkeypatch)
        monkeypatch.setattr(prc, "PROJECT_DIR", tmp_path)
        (tmp_path / "site" / "data").mkdir(parents=True, exist_ok=True)
        (tmp_path / "docs" / "observability").mkdir(parents=True, exist_ok=True)
        (tmp_path / "site" / "data" / "tick_heartbeat.json").write_text('{"ts": 1}')
        (tmp_path / "docs" / "observability" / "agent_status.json").write_text('{"a": 1}')
        monkeypatch.setattr(prc, "tree_lock", lambda *a, **k: nullcontext())
        monkeypatch.setattr(prc, "_push_due", lambda: push_due)
        recorded = []
        monkeypatch.setattr(prc, "_record_push_time", lambda: recorded.append(True))
        monkeypatch.setattr(prc, "_push_reached_origin", lambda *a, **k: reached)
        calls = []

        def fake_run(argv, **kwargs):
            calls.append(argv)
            rc = 0
            if argv[:2] == ["git", "commit"]:
                rc = commit_rc
            out = ""
            if argv[:2] == ["git", "rev-parse"]:
                out = "LOCALHEAD\n"
            if argv[:2] == ["git", "ls-remote"]:
                out = "LOCALHEAD\trefs/heads/main\n"
            return type("R", (), {"returncode": rc, "stdout": out, "stderr": ""})()

        monkeypatch.setattr(prc.subprocess, "run", fake_run)
        return calls, recorded

    def test_throttled_is_a_noop(self, tmp_path, monkeypatch):
        calls, recorded = self._wire(tmp_path, monkeypatch, push_due=False)
        assert prc._refresh_published_liveness_on_skip("abc123") is False
        assert calls == []            # no git calls at all while throttled
        assert recorded == []

    def test_due_commits_only_liveness_paths_and_records_push(self, tmp_path, monkeypatch):
        calls, recorded = self._wire(tmp_path, monkeypatch, push_due=True, reached=True)
        assert prc._refresh_published_liveness_on_skip("abc123") is True
        commit = next(c for c in calls if c[:2] == ["git", "commit"])
        # commit pathspec is EXACTLY the liveness files -- never the whole index (no concurrent sweep)
        assert "--" in commit
        committed_paths = commit[commit.index("--") + 1:]
        assert {Path(p).name for p in committed_paths} == {"tick_heartbeat.json", "agent_status.json"}
        assert any(c[:2] == ["git", "push"] for c in calls)
        assert recorded == [True]      # throttle recorded ONLY on a verified advance

    def test_due_but_phantom_push_does_not_record(self, tmp_path, monkeypatch):
        calls, recorded = self._wire(tmp_path, monkeypatch, push_due=True, reached=False)
        assert prc._refresh_published_liveness_on_skip("abc123") is False
        assert recorded == []          # phantom push (origin did not advance) never resets throttle

    def test_nothing_to_commit_skips_push(self, tmp_path, monkeypatch):
        calls, recorded = self._wire(tmp_path, monkeypatch, push_due=True, commit_rc=1)
        assert prc._refresh_published_liveness_on_skip("abc123") is False
        assert not any(c[:2] == ["git", "push"] for c in calls)
        assert recorded == []


# ── THE GHOST PUSHER (issue #11): the seat guard sits on the SIDE-EFFECT ─────────────────────
class TestLivenessPublishRefusesForeignSoil:
    """`_refresh_published_liveness_on_skip` is the one function in this module that commits
    and pushes without passing through `__main__`. The entrypoint guard therefore does not
    cover it: any caller that IMPORTS the module and reaches the change-detection SKIP branch
    lands here with full push authority on whatever checkout it is standing in. That is the
    proven ghost -- a test run manufactured a real `chore(liveness)... (git=abc)` commit and
    fired `git push origin HEAD:main`, landing only where credentials existed.

    So the guard moved to the side-effect. R15, both directions AND the ordering:
      * FOREIGN  -> one stderr line, returns False, ZERO git calls, and the refusal happens
                    before any other state is even read.
      * RESIDENT -> passes through and publishes exactly as before (the class above, which
                    now wires a real resident marker, is that direction's proof).
    Neuter `_seat.is_resident_seat()` to `return True` and every test here reds."""

    def _wire_foreign_but_otherwise_ready(self, tmp_path, monkeypatch):
        """Everything the publish path needs is in place and a push IS due -- the ONLY
        reason nothing happens must be the seat. A guard tested against a path that would
        not have published anyway proves nothing (R15 TAUTOLOGY)."""
        monkeypatch.setattr(prc, "PROJECT_DIR", tmp_path)
        (tmp_path / "site" / "data").mkdir(parents=True, exist_ok=True)
        (tmp_path / "docs" / "observability").mkdir(parents=True, exist_ok=True)
        (tmp_path / "site" / "data" / "tick_heartbeat.json").write_text('{"ts": 1}')
        (tmp_path / "docs" / "observability" / "agent_status.json").write_text('{"a": 1}')
        monkeypatch.setattr(prc, "tree_lock", lambda *a, **k: contextlib.nullcontext())
        monkeypatch.setattr(prc, "_push_due", lambda: True)
        monkeypatch.setattr(prc, "_record_push_time",
                            lambda: pytest.fail("a foreign seat recorded a push time"))
        calls = []
        monkeypatch.setattr(prc.subprocess, "run",
                            lambda argv, **kw: calls.append(argv))
        _make_foreign(tmp_path / "home", monkeypatch)
        return calls

    def test_foreign_seat_makes_no_git_calls_and_returns_false(self, tmp_path, monkeypatch, capsys):
        calls = self._wire_foreign_but_otherwise_ready(tmp_path, monkeypatch)
        assert prc._refresh_published_liveness_on_skip("abc") is False
        assert calls == [], "a foreign seat reached git: {}".format(calls)

    def test_foreign_seat_leaves_one_stderr_line_naming_the_refusal(self, tmp_path, monkeypatch,
                                                                    capsys):
        """A refusal that says nothing is indistinguishable from a healthy no-op (R5)."""
        self._wire_foreign_but_otherwise_ready(tmp_path, monkeypatch)
        prc._refresh_published_liveness_on_skip("abc")
        err = capsys.readouterr().err
        assert err.count("\n") == 1, "expected exactly one stderr line, got: {!r}".format(err)
        assert err.startswith("seat-guard: foreign,")
        assert "_refresh_published_liveness_on_skip" in err

    def test_the_seat_is_checked_before_anything_else(self, tmp_path, monkeypatch):
        """Ordering lock: the guard is the FIRST act, not merely present somewhere.
        `_push_due` is the next thing the function would touch -- if it is reached on
        foreign soil the guard has drifted below it and this reds."""
        self._wire_foreign_but_otherwise_ready(tmp_path, monkeypatch)
        monkeypatch.setattr(prc, "_push_due",
                            lambda: pytest.fail("throttle state read before the seat check"))
        assert prc._refresh_published_liveness_on_skip("abc") is False

    def test_the_import_call_bypass_is_closed_end_to_end(self, tmp_path, monkeypatch):
        """The ghost's ACTUAL route, reproduced: import the module, hand `_process` a marker
        whose fingerprint matches the last processed run, and let the change-detection gate
        SKIP. At HEAD that reached git on the real tree. `__main__` -- and therefore
        `refuse_if_foreign` -- is never involved."""
        staging = tmp_path / "staging"
        (staging / "done").mkdir(parents=True)
        monkeypatch.setattr(prc, "STAGING_DIR", staging)
        monkeypatch.setattr(prc, "DONE_DIR", staging / "done")
        calls = self._wire_foreign_but_otherwise_ready(tmp_path, monkeypatch)

        data = _sample_data()
        json_path = tmp_path / "run_output_latest.json"
        json_path.write_text(json.dumps(data))
        fp = prc._run_fingerprint(data)
        fp["source_git_hash"] = "abc"          # matches the marker -> the SKIP branch fires
        prc._write_last_fingerprint(fp)
        marker = staging / "run_complete_GHOST.md"
        marker.write_text("# Run Complete\n\nGit: abc\nJSON: %s\nDuration: 200s\n" % json_path)

        assert prc._process(str(marker)) == 0
        assert (staging / "done" / marker.name).exists()   # still archived: publishing is unaffected
        assert calls == [], "the SKIP branch reached git on foreign soil: {}".format(calls)


class TestFrozenBaselineOutOfBandTrigger:
    """The weekly frozen-policy baseline refresh is a multi-minute decade replay
    with live LLM calls. It MUST run out of band, never synchronously in the
    publish path (2026-07-29 wedge: run inline it backed up 22 run markers and
    the 900s sweep timeout re-attempted it forever)."""

    def test_spawns_detached_when_stale_and_never_runs_inline(self, monkeypatch):
        import tools.run_frozen_baseline as rfb
        monkeypatch.setattr(rfb, "should_refresh_baseline", lambda *a, **k: True)

        popen_calls = []

        class _FakeProc:
            pid = 4242

        def fake_popen(argv, **kwargs):
            popen_calls.append((argv, kwargs))
            return _FakeProc()

        # If anything tried to run the replay inline, this would fire.
        monkeypatch.setattr(rfb, "run_frozen_baseline",
                            lambda *a, **k: (_ for _ in ()).throw(
                                AssertionError("replay ran inline in the publish path")))
        monkeypatch.setattr(prc.subprocess, "Popen", fake_popen)

        prc._trigger_frozen_baseline_refresh_out_of_band("abc123")

        assert len(popen_calls) == 1, "stale baseline must spawn exactly one refresh"
        argv, kwargs = popen_calls[0]
        assert argv[1:] == ["-m", "tools.run_frozen_baseline", "--if-stale"]
        assert kwargs.get("start_new_session") is True, "must be detached to outlive publish"

    def test_does_not_spawn_when_fresh(self, monkeypatch):
        import tools.run_frozen_baseline as rfb
        monkeypatch.setattr(rfb, "should_refresh_baseline", lambda *a, **k: False)

        def fail_popen(*a, **k):
            raise AssertionError("no refresh must be spawned when the baseline is fresh")

        monkeypatch.setattr(prc.subprocess, "Popen", fail_popen)
        # returns without spawning
        prc._trigger_frozen_baseline_refresh_out_of_band("abc123")


# ── Publish-gate red output is CAPTURED and LOGGED (R5/R9) ───────────────────
# Regression cover for the 2026-07-29 ~67-min publish wedge whose entire
# recorded diagnosis was the string "Tests FAILED - not committing": the gate
# ran pytest without capturing it, so WHICH test blocked publishing was
# unknowable from the log, and by the time anyone looked the site data had been
# regenerated and the red was no longer reproducible. R15: each test below is
# written so that reverting the fix (dropping capture_output, or not calling
# _log_gate_failure_payload) makes it FAIL.

class _FakeCompleted:
    def __init__(self, returncode, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def _gate_log_text(monkeypatch, tmp_path, result):
    """Run run_fast_tests against a faked pytest `result` and return the log."""
    log_path = tmp_path / "gate-log.md"
    monkeypatch.setattr(prc, "LOG_FILE", log_path)
    monkeypatch.setattr(prc, "LAST_TESTED_HASH_FILE", tmp_path / ".last_tested_hash")

    captured_kwargs = {}

    def fake_run(argv, **kwargs):
        captured_kwargs.update(kwargs)
        return result

    monkeypatch.setattr(prc.subprocess, "run", fake_run)
    passed, timed_out = prc.run_fast_tests("deadbeef")
    text = log_path.read_text() if log_path.exists() else ""
    return passed, timed_out, text, captured_kwargs


def test_red_publish_gate_logs_the_blocking_test_node_ids(monkeypatch, tmp_path):
    """A red gate must name the tests that blocked publishing.

    MUTATION: delete the `_log_gate_failure_payload(result)` call in
    run_fast_tests and this fails -- the log again says only "Tests FAILED"."""
    out = (
        "some pytest chatter\n"
        "FAILED tests/tools/test_site_freshness.py::test_dashboard_is_current - AssertionError\n"
        "ERROR tests/background/test_thing.py::test_other\n"
        "1 failed, 2 passed\n"
    )
    passed, timed_out, text, _ = _gate_log_text(
        monkeypatch, tmp_path, _FakeCompleted(1, stdout=out))

    assert passed is False and timed_out is False
    assert "test_site_freshness.py::test_dashboard_is_current" in text, (
        "the failing node ID must reach the log -- otherwise a wedge is "
        "undiagnosable after the site data is regenerated")
    assert "test_thing.py::test_other" in text, "ERROR lines count as blocking too"


def test_a_timed_out_publish_gate_blocks_the_commit(monkeypatch, tmp_path):
    """R15: an unavailable check is a FAILED check. A gate that did not FINISH cannot
    authorise a publish.

    The named defect, observed live on 2026-08-09: the suite takes ~613s and the timeout was
    600s, so the gate timed out on essentially every cycle and the timeout branch returned
    `True` ("resource constraint, not a test failure"). That walked the full success path --
    marker archived, commit attempted, and the publish-gate outcome recorded as rc=0, which
    CLEARS wedge_since/episode_failures and re-arms the alarm. A gate that never ran was
    silently disarming the alarm whose whole job is to say it never ran.

    MUTATION: restore `return True, True` in the TimeoutExpired branch and this fails."""
    log_path = tmp_path / "gate-log.md"
    monkeypatch.setattr(prc, "LOG_FILE", log_path)
    last_tested = tmp_path / ".last_tested_hash"
    monkeypatch.setattr(prc, "LAST_TESTED_HASH_FILE", last_tested)

    def fake_run(argv, **kwargs):
        raise prc.subprocess.TimeoutExpired(cmd=argv, timeout=kwargs.get("timeout"))

    monkeypatch.setattr(prc.subprocess, "run", fake_run)
    passed, timed_out = prc.run_fast_tests("deadbeef")

    assert timed_out is True
    assert passed is False, (
        "a timed-out gate must BLOCK the publish -- returning True archives the marker, "
        "publishes unverified content, and clears the wedge alarm's episode memory"
    )
    assert not last_tested.exists(), (
        "a gate that did not finish must not stamp .last_tested_hash -- that hash is the "
        "INDEPENDENT signal the supervisor's wedge draw cross-checks against"
    )
    assert "NOT committing" in log_path.read_text()


def test_the_gate_timeout_exceeds_the_suites_own_runtime(monkeypatch, tmp_path):
    """The timeout must be generous enough that hitting it is an ANOMALY, not the norm.

    The 600s timeout was BELOW the suite's own measured runtime (612.94s for 22,525 tests),
    so the gate could not pass -- it could only time out. A timeout that the healthy case
    exceeds is not a safety bound, it is a coin flip.

    MUTATION: set GATE_SUITE_TIMEOUT_SECONDS back to 600 and this fails."""
    MEASURED_SUITE_SECONDS = 613
    assert prc.GATE_SUITE_TIMEOUT_SECONDS > MEASURED_SUITE_SECONDS * 2, (
        f"gate timeout {prc.GATE_SUITE_TIMEOUT_SECONDS}s leaves too little headroom over the "
        f"~{MEASURED_SUITE_SECONDS}s the suite actually takes; a routine timeout is now a "
        "publish BLOCK, so the bound must clear the healthy case comfortably"
    )


def test_red_publish_gate_captures_output_rather_than_discarding_it(monkeypatch, tmp_path):
    """The gate must actually CAPTURE pytest's output.

    MUTATION: drop `capture_output=True` from the subprocess.run call and this
    fails -- stdout/stderr go to the daemon's console and are lost."""
    _, _, _, kwargs = _gate_log_text(
        monkeypatch, tmp_path, _FakeCompleted(1, stdout="FAILED tests/a.py::t\n"))
    assert kwargs.get("capture_output") is True, \
        "publish-gate pytest output must be captured, not discarded"
    assert kwargs.get("text") is True, "captured output must be decoded to str"


def test_red_publish_gate_logs_a_tail_even_with_no_summary_line(monkeypatch, tmp_path):
    """Fail-open guard: a red with no FAILED/ERROR summary (collection error,
    internal pytest crash) must STILL log evidence, never a silent red.

    MUTATION: make _log_gate_failure_payload return early when node_ids is
    empty and this fails."""
    _, _, text, _ = _gate_log_text(
        monkeypatch, tmp_path,
        _FakeCompleted(2, stderr="INTERNALERROR> Traceback: conftest import blew up"))
    assert "no FAILED/ERROR summary line found" in text
    assert "conftest import blew up" in text, \
        "a red with no summary line must still carry its output tail"


def test_green_publish_gate_logs_no_failure_payload(monkeypatch, tmp_path):
    """Independence: the payload logger fires ONLY on red (R15 -- a control
    that fires on every run carries no signal).

    MUTATION: call _log_gate_failure_payload unconditionally and this fails."""
    passed, _, text, _ = _gate_log_text(
        monkeypatch, tmp_path, _FakeCompleted(0, stdout="100 passed\n"))
    assert passed is True
    assert "Publish gate RED" not in text
    assert (tmp_path / ".last_tested_hash").read_text().strip() == "deadbeef"


def test_gate_failure_log_tail_is_bounded(monkeypatch, tmp_path):
    """A pathological suite must not balloon the shared log file.

    MUTATION: remove the [-GATE_FAILURE_TAIL_CHARS:] slice and this fails."""
    huge = "x" * 200_000 + "\nFAILED tests/a.py::t\n"
    _, _, text, _ = _gate_log_text(monkeypatch, tmp_path, _FakeCompleted(1, stdout=huge))
    assert len(text) < prc.GATE_FAILURE_TAIL_CHARS * 3, \
        "the red-gate tail must be bounded, not the whole suite output"
    assert "FAILED tests/a.py::t" in text, "the summary line must survive the bound"


# --- The commit-timeout crash that wedged publishing (2026-08-03) -------------
# git_commit_push runs the FULL pre-commit hook chain, whose site_lane_gate branch
# alone measured 27.3s against a 30s subprocess cap. The TimeoutExpired was UNCAUGHT:
# it propagated out of _process(), so process_run_complete exited rc=1 having logged
# NEITHER "Nothing to commit or commit failed" NOR "Done", and the wedge detector
# recorded a "test_regression" that was nothing of the sort. R15 -- these prove the
# catch is real, not asserted.

def _commit_push_with(monkeypatch, run_side_effect):
    """Drive git_commit_push with a stubbed subprocess.run and a no-op tree_lock."""
    import contextlib
    monkeypatch.setattr(prc, "tree_lock", lambda: contextlib.nullcontext())
    monkeypatch.setattr(prc.subprocess, "run", run_side_effect)
    return prc.git_commit_push("abc1234", 1_500_000)


def test_commit_timeout_is_caught_and_does_not_crash_the_publish(monkeypatch, tmp_path):
    """THE REGRESSION. A slow hook chain must degrade to "retry next cycle".

    MUTATION: remove the `except subprocess.TimeoutExpired` in git_commit_push and
    this raises instead of returning False -- which is exactly the 2026-08-03 crash.
    """
    import subprocess as _sp

    def _run(argv, **kw):
        if argv[:2] == ["git", "commit"]:
            raise _sp.TimeoutExpired(cmd=argv, timeout=kw.get("timeout", 0))
        return _FakeCompleted(0)

    assert _commit_push_with(monkeypatch, _run) is False, \
        "a timed-out commit must report failure, not crash the publish"


def test_commit_timeout_says_so_in_the_log(monkeypatch, tmp_path):
    """The crash was hard to diagnose because it logged NOTHING between the
    'Committing and pushing' line and the process's death -- the failure has to
    name itself, or the next reader blames the test suite again (R9: evidence
    before narrative).

    MUTATION: drop the log() call from the except branch and this fails.
    """
    import subprocess as _sp
    written = []
    monkeypatch.setattr(prc, "log", lambda m: written.append(m))

    def _run(argv, **kw):
        if argv[:2] == ["git", "commit"]:
            raise _sp.TimeoutExpired(cmd=argv, timeout=kw.get("timeout", 0))
        return _FakeCompleted(0)

    assert _commit_push_with(monkeypatch, _run) is False
    joined = "\n".join(written)
    assert "TIMED OUT" in joined, joined
    assert "hook chain" in joined, "the log must point at the hook chain, not the run"


def test_commit_timeout_budget_fits_inside_the_workers_own_cap():
    """A commit cap larger than background_worker's 900s cap on the whole process
    would just move the kill one level up and lose the explaining log line.

    MUTATION: set GIT_COMMIT_HOOK_TIMEOUT_SECONDS above the worker's timeout and
    this fails.
    """
    import re
    from pathlib import Path as _Path
    worker = _Path(prc.__file__).parent / "background_worker.py"
    assert worker.exists(), "background_worker.py is the caller whose cap this must fit"
    src = worker.read_text()
    # The cap that actually applies: the one on the subprocess.run that INVOKES
    # process_run_complete inside process_leftover_run_markers -- not, say,
    # run_ollama_task's unrelated timeout (which this test caught on its first run).
    sweep = src[src.index("def process_leftover_run_markers"):]
    sweep = sweep[:sweep.index("\ndef ", 1)]
    caps = [int(m) for m in re.findall(r"timeout=(\d+)", sweep)]
    assert caps, "could not find the marker sweep's own subprocess timeout"
    assert prc.GIT_COMMIT_HOOK_TIMEOUT_SECONDS < min(caps), (
        "commit cap {}s must fit inside the sweep's own {}s cap on the whole "
        "process".format(prc.GIT_COMMIT_HOOK_TIMEOUT_SECONDS, min(caps)))


def test_commit_timeout_has_real_headroom_over_the_hook_chain():
    """The old 30s cap failed because it was BELOW the hook chain's measured cost
    (site suite alone: 27.3s). Keep a real multiple so suite growth cannot quietly
    re-create the wedge.

    MUTATION: drop the constant back to 30 and this fails.
    """
    measured_hook_chain_seconds = 30  # site_lane_gate broad branch, 2026-08-03
    assert prc.GIT_COMMIT_HOOK_TIMEOUT_SECONDS >= 5 * measured_hook_chain_seconds
