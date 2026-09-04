"""Tests for background/sim_runner.py."""

from pathlib import Path
from unittest.mock import MagicMock

from background import sim_runner


def test_run_simulation_creates_staging_marker(tmp_path, monkeypatch):
    monkeypatch.setattr(sim_runner, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(sim_runner, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(sim_runner, "STAGING_DIR", tmp_path / "staging")
    monkeypatch.setattr(sim_runner, "REPORTS_DIR", tmp_path / "reports")
    monkeypatch.setattr(sim_runner, "notify", lambda *a, **k: None)
    monkeypatch.setattr(sim_runner, "_git_head", lambda: "abc1234")

    # Simulate a successful subprocess run + output file creation.
    # Only write output files for the simulation cmd; other calls just get rc=0.
    def fake_run(cmd, **kwargs):
        if "annual_report" in " ".join(str(a) for a in cmd):
            out_json = next((Path(a) for a in cmd if a.endswith(".json")), None)
            if out_json:
                out_json.parent.mkdir(parents=True, exist_ok=True)
                out_json.write_text('{"test": true}')
            out_md = next((Path(a) for a in cmd if a.endswith(".md")), None)
            if out_md:
                out_md.write_text("# Report")
        m = MagicMock()
        m.returncode = 0
        return m

    monkeypatch.setattr(sim_runner.subprocess, "run", fake_run)

    result = sim_runner.run_simulation()

    assert result is True
    markers = list((tmp_path / "staging").glob("run_complete_*.md"))
    assert len(markers) == 1
    content = markers[0].read_text()
    assert "Action required" in content
    assert "ANNUAL_REPORT.md" in content


def test_run_simulation_returns_false_on_failure(tmp_path, monkeypatch):
    monkeypatch.setattr(sim_runner, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(sim_runner, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(sim_runner, "STAGING_DIR", tmp_path / "staging")
    monkeypatch.setattr(sim_runner, "REPORTS_DIR", tmp_path / "reports")
    monkeypatch.setattr(sim_runner, "notify", lambda *a, **k: None)
    monkeypatch.setattr(sim_runner, "_git_head", lambda: "abc1234")

    def fake_run(cmd, **kwargs):
        m = MagicMock()
        m.returncode = 1
        return m

    monkeypatch.setattr(sim_runner.subprocess, "run", fake_run)

    result = sim_runner.run_simulation()

    assert result is False
    assert not list((tmp_path / "staging").glob("run_complete_*.md"))


def test_run_simulation_updates_latest_json(tmp_path, monkeypatch):
    monkeypatch.setattr(sim_runner, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(sim_runner, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(sim_runner, "STAGING_DIR", tmp_path / "staging")
    monkeypatch.setattr(sim_runner, "REPORTS_DIR", tmp_path / "reports")
    monkeypatch.setattr(sim_runner, "notify", lambda *a, **k: None)
    monkeypatch.setattr(sim_runner, "_git_head", lambda: "abc1234")

    def fake_run(cmd, **kwargs):
        out_json = next((Path(a) for a in cmd if a.endswith(".json")), None)
        if out_json:
            out_json.parent.mkdir(parents=True, exist_ok=True)
            out_json.write_text('{"headline": "test"}')
        out_md = next((Path(a) for a in cmd if a.endswith(".md")), None)
        if out_md:
            out_md.write_text("# Report")
        m = MagicMock()
        m.returncode = 0
        return m

    monkeypatch.setattr(sim_runner.subprocess, "run", fake_run)

    sim_runner.run_simulation()

    latest = tmp_path / "reports" / "run_output_latest.json"
    assert latest.exists()
    assert '"headline": "test"' in latest.read_text()


def test_one_producer_period_covers_one_publisher_cycle():
    """THE DEFECT: the producer mints markers faster than the publisher can consume them, so
    the run_complete queue never reaches zero and the episode watching for a drained queue can
    never close. Measured 2026-09-03..04: 13.2 min marker interarrival against an 88.9 min
    cycle for a publish that actually published (p50, n=22, gaps following a passing gate).

    Keyed to the PROPERTY, not to today's answer. The predecessor asserted
    `BETWEEN_RUN_PAUSE_SECONDS == 60`, which stayed green for the whole period the queue was
    undrainable and would have gone red on the fix -- exactly backwards. This one goes red if
    anyone shortens the pause back, AND if the publisher's measured cycle grows without the
    cadence following it."""
    period = sim_runner.BETWEEN_RUN_PAUSE_SECONDS + sim_runner.SIM_RUN_DURATION_P50_SECONDS
    assert period >= sim_runner.PUBLISHER_CYCLE_P90_SECONDS, (
        f"producer period {period}s does not cover the publisher's measured "
        f"{sim_runner.PUBLISHER_CYCLE_P90_SECONDS}s cycle -- the queue cannot drain"
    )


def test_the_busy_loop_floor_is_not_what_sets_the_pause():
    """The reachability null for the `max(60, ...)` above.

    Without this, a degenerate measurement collapsing the derivation to the 60s floor would
    restore the original defect while the property control above still passed on the floor.
    Asserts the DERIVED limb is the live one -- that the branch can be, and is, taken."""
    derived = (sim_runner.PUBLISHER_CYCLE_P90_SECONDS
               - sim_runner.SIM_RUN_DURATION_P50_SECONDS)
    assert derived > 60, "derivation collapsed to the busy-loop floor"
    assert sim_runner.BETWEEN_RUN_PAUSE_SECONDS == derived


def test_git_head_returns_string(monkeypatch):
    monkeypatch.setattr(sim_runner.subprocess, "check_output", lambda *a, **k: "abc1234\n")
    result = sim_runner._git_head()
    assert isinstance(result, str)
    assert result == "abc1234"


def test_git_head_returns_unknown_on_exception(monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("git not found")
    monkeypatch.setattr(sim_runner.subprocess, "check_output", boom)
    result = sim_runner._git_head()
    assert result == "unknown"


def test_log_creates_parent_directory(tmp_path, monkeypatch):
    log_file = tmp_path / "sub" / "dir" / "log.md"
    monkeypatch.setattr(sim_runner, "LOG_FILE", log_file)
    sim_runner.log("test message")
    assert log_file.exists()


def test_log_writes_timestamp_and_message(tmp_path, monkeypatch):
    log_file = tmp_path / "log.md"
    monkeypatch.setattr(sim_runner, "LOG_FILE", log_file)
    sim_runner.log("hello world")
    text = log_file.read_text()
    assert "hello world" in text
    import re
    assert re.search(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2} UTC", text)


def test_run_simulation_staging_marker_name_format(tmp_path, monkeypatch):
    monkeypatch.setattr(sim_runner, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(sim_runner, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(sim_runner, "STAGING_DIR", tmp_path / "staging")
    monkeypatch.setattr(sim_runner, "REPORTS_DIR", tmp_path / "reports")
    monkeypatch.setattr(sim_runner, "notify", lambda *a, **k: None)
    monkeypatch.setattr(sim_runner, "_git_head", lambda: "abc1234")
    from unittest.mock import MagicMock
    from pathlib import Path as _Path
    def fake_run(cmd, **kwargs):
        for a in cmd:
            a = str(a)
            if a.endswith(".json"):
                _Path(a).parent.mkdir(parents=True, exist_ok=True)
                _Path(a).write_text("{}")
            elif a.endswith(".md"):
                _Path(a).parent.mkdir(parents=True, exist_ok=True)
                _Path(a).write_text("# R")
        m = MagicMock(); m.returncode = 0; return m
    monkeypatch.setattr(sim_runner.subprocess, "run", fake_run)
    sim_runner.run_simulation()
    markers = list((tmp_path / "staging").glob("run_complete_*.md"))
    assert len(markers) == 1
    assert markers[0].name.startswith("run_complete_")

def test_log_appends_on_second_call(tmp_path, monkeypatch):
    log_file = tmp_path / "log.md"
    monkeypatch.setattr(sim_runner, "LOG_FILE", log_file)
    sim_runner.log("first")
    sim_runner.log("second")
    text = log_file.read_text()
    assert "first" in text
    assert "second" in text


def test_reports_dir_name_is_reports():
    assert sim_runner.REPORTS_DIR.name == "reports"


def test_staging_dir_name_is_staging():
    assert sim_runner.STAGING_DIR.name == "staging"


def test_log_file_is_under_project_dir():
    assert sim_runner.PROJECT_DIR in sim_runner.LOG_FILE.parents


def test_staging_dir_is_under_project_dir():
    assert sim_runner.PROJECT_DIR in sim_runner.STAGING_DIR.parents


def test_log_entry_has_timestamp(tmp_path, monkeypatch):
    log_file = tmp_path / "log.md"
    monkeypatch.setattr(sim_runner, "LOG_FILE", log_file)
    sim_runner.log("check timestamp")
    text = log_file.read_text()
    assert "20" in text and "UTC" in text


# --- _check_hold() -- no-orphan-transitions fix (2026-07-10,
# CLAIM_EQUALS_PIXEL.md/END_TO_END_VERIFICATION.md): a hold release must
# itself force a republish, not just stop skipping ---

def _setup_hold(tmp_path, monkeypatch):
    monkeypatch.setattr(sim_runner, "HOLD_FLAG", tmp_path / ".sim_runner_hold")
    monkeypatch.setattr(sim_runner, "FORCE_REPUBLISH_FLAG", tmp_path / ".force_republish_once")
    monkeypatch.setattr(sim_runner, "LOG_FILE", tmp_path / "log.md")


def test_check_hold_no_flag_no_prior_hold_runs_normally(tmp_path, monkeypatch):
    _setup_hold(tmp_path, monkeypatch)
    was_held, should_skip = sim_runner._check_hold(False)
    assert was_held is False
    assert should_skip is False
    assert not sim_runner.FORCE_REPUBLISH_FLAG.exists()


def test_check_hold_flag_present_skips_and_marks_held(tmp_path, monkeypatch):
    _setup_hold(tmp_path, monkeypatch)
    sim_runner.HOLD_FLAG.touch()
    was_held, should_skip = sim_runner._check_hold(False)
    assert was_held is True
    assert should_skip is True


def test_check_hold_flag_still_present_stays_held_no_relog(tmp_path, monkeypatch):
    _setup_hold(tmp_path, monkeypatch)
    sim_runner.HOLD_FLAG.touch()
    was_held, should_skip = sim_runner._check_hold(True)
    assert was_held is True
    assert should_skip is True


def test_check_hold_cleared_transition_touches_force_republish_flag(tmp_path, monkeypatch):
    """The exact regression: releasing a hold must force the next publish
    through, not just quietly stop skipping."""
    _setup_hold(tmp_path, monkeypatch)
    was_held, should_skip = sim_runner._check_hold(True)
    assert was_held is False
    assert should_skip is False
    assert sim_runner.FORCE_REPUBLISH_FLAG.exists()


def test_check_hold_no_prior_hold_does_not_touch_force_republish_flag(tmp_path, monkeypatch):
    """Only a real held->cleared transition forces a republish -- normal
    operation with no hold ever involved must not force anything."""
    _setup_hold(tmp_path, monkeypatch)
    sim_runner._check_hold(False)
    assert not sim_runner.FORCE_REPUBLISH_FLAG.exists()

# ── Publish-gate scope (R10, 2026-07-18): DAEMON-LIFECYCLE test module ──────────
# Validates pipeline MACHINERY (process/session lifecycle, scheduling, notify transport,
# reconciliation), never a published business surface -- so it must never wedge the live
# publish. The gate runs `-m 'not operational'`. See tests/conftest.py for the marker.
import pytest  # noqa: E402,F811
pytestmark = pytest.mark.operational


# ── The pause must outlive the process that began it (lane 0 throughput, 2026-09-04) ──────


def test_a_restart_inside_the_pause_does_not_start_a_new_run(tmp_path):
    """THE DEFECT: a restart mid-pause reset the cadence to zero and nothing could see it.

    Measured 2026-09-04 — every simulation run between 13:22Z and 15:18Z began at a
    `Started sim-runner.service` instant, so the 4685s pause was entered five times and never
    once served. Marker interarrival stayed at ~30 min against a derived period of 78.
    Before `pause_owed_from_a_previous_process` existed this asked nothing: a fresh process had
    no memory of the deadline at all and ran immediately, always.
    """
    p = tmp_path / "next.json"
    now = 1_000_000.0
    sim_runner.record_next_run_not_before(now + 3000.0, path=p)

    owed, why = sim_runner.pause_owed_from_a_previous_process(now=now, path=p)

    assert owed == pytest.approx(3000.0)
    assert why  # a hold that does not say why is how an idle producer reads as a dead one


def test_the_owed_pause_partition_is_whole_and_every_leg_is_reachable(tmp_path):
    """ONE control over the WHOLE partition, because a function that returned 0.0 for every
    input would pass every per-leg test written here. The `assert ... and ...` at the foot is
    the reachability control: it fails if the deferring branch becomes unreachable, which is the
    exact trap CLAUDE.md names — a guard that refuses everything passes every test of a guard.
    """
    now = 1_000_000.0

    absent = tmp_path / "does_not_exist.json"
    corrupt = tmp_path / "corrupt.json"
    corrupt.write_text("{not json")
    passed = tmp_path / "passed.json"
    sim_runner.record_next_run_not_before(now - 1.0, path=passed)
    future = tmp_path / "future.json"
    sim_runner.record_next_run_not_before(now + 600.0, path=future)

    legs = {
        name: sim_runner.pause_owed_from_a_previous_process(now=now, path=path)
        for name, path in (
            ("absent", absent), ("corrupt", corrupt),
            ("passed", passed), ("future", future),
        )
    }

    # Every leg names its own reason rather than sharing one.
    assert len({why for _, why in legs.values()}) == len(legs)
    assert legs["absent"][0] == 0.0
    assert legs["corrupt"][0] == 0.0
    assert legs["passed"][0] == 0.0
    assert legs["future"][0] == pytest.approx(600.0)
    # REACHABILITY: both sides of the partition are attainable from real inputs.
    assert legs["future"][0] > 0 and legs["absent"][0] == 0.0


def test_a_far_future_deadline_cannot_park_the_producer_forever(tmp_path):
    """The upper-end null. A clock step, a hand edit or a half-written file must cost at most
    one pause — never a producer that silently never runs again. Without the clamp this returns
    a decade and the failure is indistinguishable from a dead daemon.
    """
    p = tmp_path / "next.json"
    now = 1_000_000.0
    sim_runner.record_next_run_not_before(now + 10 * 365 * 24 * 3600.0, path=p)

    owed, why = sim_runner.pause_owed_from_a_previous_process(now=now, path=p)

    assert owed == float(sim_runner.BETWEEN_RUN_PAUSE_SECONDS)
    assert "clamped" in why


def test_the_recorded_deadline_is_validated_by_the_one_definition(tmp_path):
    """`0` and `True` are not instants, and `isinstance(x, (int, float))` waves both through.

    That hand-roll is what put `0` into `first_failure_ts` and rendered a 496,815-hour outage on
    the director's surface. Here a `0` would read as a 1970 deadline — "run now" — which is the
    OLD wrong answer reached silently, so the fail-open would be invisible rather than loud.

    THIS CONTROL IS KEYED TO THE REASON, NOT THE NUMBER, and that is the whole point. Asserting
    `owed == 0.0` is a TAUTOLOGY here: `0` and `True` yield 0.0 under BOTH implementations —
    the one definition rejects them as non-instants, the hand-roll accepts them as 1970 and then
    calls the deadline "already passed". Same number, opposite meanings, and only the reason can
    tell them apart. Proven by mutation: swapping in `isinstance(v, (int, float))` SURVIVED the
    number-only version of this test and is killed by this one.
    """
    import json

    now = 1_000_000.0
    for value in (0, True, None, "soon", []):
        p = tmp_path / f"v_{type(value).__name__}_{value!r}.json"
        p.write_text(json.dumps({"next_run_not_before": value}))
        owed, why = sim_runner.pause_owed_from_a_previous_process(now=now, path=p)
        assert owed == 0.0, f"{value!r} was treated as a deadline"
        assert "not an instant" in why, (
            f"{value!r} was accepted as an instant and reported as {why!r} — a value that is not "
            f"a time must be refused as one, not silently re-described as a past deadline")


def test_the_pause_is_longer_than_the_interval_that_defeats_it(tmp_path):
    """Keyed to the PROPERTY the persistence exists to serve, not to today's constant.

    The producer's derived pause (78 min) exceeds the observed deployment-restart interval
    (~30 min median, 20 min shortest, journalctl 2026-09-04). While that is true the pause is
    unreachable WITHOUT persistence, so this test states the condition under which the mechanism
    is load-bearing. It goes red — correctly — if someone shortens the pause back under the
    restart interval, at which point persisting it stops being the thing that matters.
    """
    shortest_observed_restart_interval_s = 20 * 60
    assert sim_runner.BETWEEN_RUN_PAUSE_SECONDS > shortest_observed_restart_interval_s
