"""Tests for background/autonomous_runner.py."""

import json
import time
from collections import deque
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from background import autonomous_runner


@pytest.fixture(autouse=True)
def _ledger_to_tmp(tmp_path, monkeypatch):
    """THIS MODULE WROTE 6,421 LINES INTO THE LIVE LEDGER, and they were read as evidence.

    Every test below calls `launch_turn()`, which calls the real `log()`, which appended to the
    real `docs/observability/autonomous-runner-log.md`. Measured 2026-08-31: 23% of that ledger's
    27,675 lines are this file's output -- launches whose pid is a `MagicMock` repr, refusals
    naming `/tmp/pytest-of-rich/...` binaries, and seventeen "Usage limit active" skips dated
    today for a module that has not run since 2026-07-08.

    On 2026-08-31 the delivery seat read those seventeen lines and reported a usage limit to the
    director. There was none. **A production surface a test can write is not merely at risk of
    being wrong -- it stops being evidence at all.** `tests/production_surface_guard.py` now
    refuses the write outright; this fixture is what makes the tests legitimate rather than
    merely blocked.
    """
    monkeypatch.setattr(autonomous_runner, "LOG_FILE", tmp_path / "runner-log.md")
    monkeypatch.setattr(autonomous_runner, "TURN_OUTPUT_FILE", tmp_path / "turn-output.md")
    monkeypatch.setattr(autonomous_runner, "PANE_STATE_FILE", tmp_path / "pane-state.json")


def test_turns_in_last_hour_empty():
    autonomous_runner._turn_times.clear()
    assert autonomous_runner.turns_in_last_hour() == 0


def test_turns_in_last_hour_counts_recent():
    autonomous_runner._turn_times.clear()
    now = time.time()
    autonomous_runner._turn_times.append(now - 100)
    autonomous_runner._turn_times.append(now - 200)
    assert autonomous_runner.turns_in_last_hour() == 2


def test_turns_in_last_hour_excludes_old():
    autonomous_runner._turn_times.clear()
    now = time.time()
    autonomous_runner._turn_times.append(now - 7200)  # 2 hours ago
    autonomous_runner._turn_times.append(now - 100)
    assert autonomous_runner.turns_in_last_hour() == 1


def test_idle_seconds_returns_zero_on_change(tmp_path, monkeypatch):
    monkeypatch.setattr(autonomous_runner, "PANE_STATE_FILE", tmp_path / "state.json")
    monkeypatch.setattr(autonomous_runner, "_pane_content", lambda: "new content here")

    # Write stale state with different content
    (tmp_path / "state.json").write_text(
        json.dumps({"content": "old content", "since": time.time() - 600})
    )

    idle = autonomous_runner.idle_seconds()
    assert idle == 0.0


def test_idle_seconds_accumulates_when_static(tmp_path, monkeypatch):
    monkeypatch.setattr(autonomous_runner, "PANE_STATE_FILE", tmp_path / "state.json")
    content = "same content"
    monkeypatch.setattr(autonomous_runner, "_pane_content", lambda: content)

    past = time.time() - 1800  # 30 min ago
    (tmp_path / "state.json").write_text(
        json.dumps({"content": content, "since": past})
    )

    idle = autonomous_runner.idle_seconds()
    assert idle >= 1799  # at least 30 min minus a tiny margin


def test_launch_turn_skips_when_rate_capped(monkeypatch):
    autonomous_runner._turn_times.clear()
    autonomous_runner._active_proc = None
    now = time.time()
    for _ in range(autonomous_runner.MAX_TURNS_PER_HOUR):
        autonomous_runner._turn_times.append(now - 10)


    with patch("background.autonomous_runner.subprocess.Popen") as mock_popen:
        autonomous_runner.launch_turn()
        mock_popen.assert_not_called()


def test_launch_turn_skips_when_proc_still_running(monkeypatch):
    autonomous_runner._turn_times.clear()
    proc = MagicMock()
    proc.poll.return_value = None  # still running
    autonomous_runner._active_proc = proc


    with patch("background.autonomous_runner.subprocess.Popen") as mock_popen:
        autonomous_runner.launch_turn()
        mock_popen.assert_not_called()

    autonomous_runner._active_proc = None  # cleanup


def test_launch_turn_skips_when_binary_missing(tmp_path, monkeypatch):
    autonomous_runner._active_proc = None
    autonomous_runner._turn_times.clear()
    monkeypatch.setattr(autonomous_runner, "CLAUDE_BIN", tmp_path / "no_such_claude")

    with patch("background.autonomous_runner.subprocess.Popen") as mock_popen:
        autonomous_runner.launch_turn()
        mock_popen.assert_not_called()


def test_launch_turn_explicitly_sets_disable_autoupdater(tmp_path, monkeypatch):
    """2026-07-11, root-caused live: this Popen's env is copied from the
    runner's OWN process env, not freshly read from tmux global env at
    spawn time -- a long-lived runner process predating the
    `tmux set-environment -g DISABLE_AUTOUPDATER 1` fix (start_worker.sh)
    would silently inherit the stale value. Must be set explicitly here,
    not just relied on via inheritance."""
    autonomous_runner._active_proc = None
    autonomous_runner._turn_times.clear()
    fake_bin = tmp_path / "claude"
    fake_bin.write_text("#!/bin/sh\n")
    monkeypatch.setattr(autonomous_runner, "CLAUDE_BIN", fake_bin)
    # `_pane_content`, NOT `_usage_limit_active`: these three tests patch `subprocess.Popen`,
    # and the real pane read goes through `subprocess.run` -- which builds a `Popen`. Stubbing
    # the verdict would hide that, so the clean pane is supplied at the source instead.
    monkeypatch.setattr(autonomous_runner, "_pane_content", lambda: "all quiet")
    monkeypatch.delenv("DISABLE_AUTOUPDATER", raising=False)

    with patch("background.autonomous_runner.subprocess.Popen") as mock_popen:
        mock_popen.return_value = MagicMock(poll=lambda: None)
        autonomous_runner.launch_turn()
        env = mock_popen.call_args[1]["env"]
        assert env["DISABLE_AUTOUPDATER"] == "1"


def test_launch_turn_uses_skip_permissions_flag(tmp_path, monkeypatch):
    """Rich's direct, live confirmation (2026-07-05, expanding
    docs/review_gates/SKIP_PERMISSIONS_TIER1.md beyond the watchdog): every
    session launcher runs with --dangerously-skip-permissions -- a
    non-interactive `claude -p` turn has no TTY and nobody present to answer
    a permission prompt."""
    autonomous_runner._active_proc = None
    autonomous_runner._turn_times.clear()
    fake_bin = tmp_path / "claude"
    fake_bin.write_text("#!/bin/sh\n")
    monkeypatch.setattr(autonomous_runner, "CLAUDE_BIN", fake_bin)
    # `_pane_content`, NOT `_usage_limit_active`: these three tests patch `subprocess.Popen`,
    # and the real pane read goes through `subprocess.run` -- which builds a `Popen`. Stubbing
    # the verdict would hide that, so the clean pane is supplied at the source instead.
    monkeypatch.setattr(autonomous_runner, "_pane_content", lambda: "all quiet")

    with patch("background.autonomous_runner.subprocess.Popen") as mock_popen:
        mock_popen.return_value = MagicMock(poll=lambda: None)
        autonomous_runner.launch_turn()
        args = mock_popen.call_args[0][0]
        assert "--dangerously-skip-permissions" in args
        assert args[0] == str(fake_bin)
        assert args[1] == "-p"


def test_launch_turn_uses_cheap_model_for_supervisor_micro_turns(tmp_path, monkeypatch):
    """Model routing (2026-07-11, director NTFY, Lane-H): these unattended
    turns are supervisor micro-turns/status checks -- routed to the fastest
    cheap model, not the strongest one reserved for build-lane architecture."""
    autonomous_runner._active_proc = None
    autonomous_runner._turn_times.clear()
    fake_bin = tmp_path / "claude"
    fake_bin.write_text("#!/bin/sh\n")
    monkeypatch.setattr(autonomous_runner, "CLAUDE_BIN", fake_bin)
    # `_pane_content`, NOT `_usage_limit_active`: these three tests patch `subprocess.Popen`,
    # and the real pane read goes through `subprocess.run` -- which builds a `Popen`. Stubbing
    # the verdict would hide that, so the clean pane is supplied at the source instead.
    monkeypatch.setattr(autonomous_runner, "_pane_content", lambda: "all quiet")

    with patch("background.autonomous_runner.subprocess.Popen") as mock_popen:
        mock_popen.return_value = MagicMock(poll=lambda: None)
        autonomous_runner.launch_turn()
        args = mock_popen.call_args[0][0]
        assert "--model" in args
        model_idx = args.index("--model")
        assert args[model_idx + 1] == autonomous_runner.AUTONOMOUS_TURN_MODEL


def _in_minutes(minutes: int) -> str:
    """A wall-clock `HH:MM` that many minutes from now, so a test about RECENCY is not a test
    about what time the suite happens to run at."""
    return (datetime.now().astimezone() + timedelta(minutes=minutes)).strftime("%H:%M")


def test_usage_limit_active_detects_limit_phrase(monkeypatch):
    monkeypatch.setattr(
        autonomous_runner, "_pane_content",
        lambda: f"Claude.ai usage limit reached. Try again at {_in_minutes(90)}."
    )
    assert autonomous_runner._usage_limit_active() is True


def test_usage_limit_active_false_when_normal(monkeypatch):
    monkeypatch.setattr(
        autonomous_runner, "_pane_content",
        lambda: "Working on Phase 9b implementation..."
    )
    assert autonomous_runner._usage_limit_active() is False


def test_launch_turn_skips_during_usage_limit(monkeypatch):
    autonomous_runner._active_proc = None
    autonomous_runner._turn_times.clear()
    monkeypatch.setattr(autonomous_runner, "CLAUDE_BIN", Path("/usr/bin/true"))
    monkeypatch.setattr(
        autonomous_runner, "_pane_content",
        lambda: f"Claude.ai usage limit reached. Try again at {_in_minutes(45)}."
    )

    with patch("background.autonomous_runner.subprocess.Popen") as mock_popen:
        autonomous_runner.launch_turn()
        mock_popen.assert_not_called()


# ── A LIMIT MUST BE VERIFIED, AND AN UNVERIFIABLE ONE RUNS ────────────────────────────────────
# Director, 2026-08-31: *"Make it impossible to claim a limit it hasn't verified, and where the
# real signal is unavailable it should run rather than skip -- a false stop costs more than a
# false start here."*
#
# The old check matched a phrase anywhere in `tmux capture-pane` output. A pane is SCROLLBACK: a
# limit message from three hours ago is still on screen, and the check had no notion of recency at
# all, so once a limit had ever been shown it read as active until the text scrolled away. These
# four legs are the four ways that goes wrong, and each of them ends in RUNNING.

def test_a_limit_phrase_with_no_reset_time_cannot_be_dated_so_it_runs(monkeypatch):
    """The sharp one. This is old scrollback's exact shape: the words, and nothing that says when."""
    monkeypatch.setattr(
        autonomous_runner, "_pane_content",
        lambda: "Claude.ai usage limit reached.",
    )
    verdict = autonomous_runner.usage_limit_verdict()
    assert verdict.limited is False
    assert "names no reset time" in verdict.reason
    assert "usage limit reached" in verdict.evidence


def test_a_limit_whose_reset_has_passed_is_expired_so_it_runs(monkeypatch):
    monkeypatch.setattr(
        autonomous_runner, "_pane_content",
        lambda: f"Claude.ai usage limit reached. Try again at {_in_minutes(-120)}.",
    )
    verdict = autonomous_runner.usage_limit_verdict()
    assert verdict.limited is False
    assert "expired" in verdict.reason


def test_an_unreadable_pane_runs_rather_than_skips(monkeypatch):
    """A false stop costs every turn until someone notices. A false start costs one API call that
    the real limit refuses in a second. The asymmetry is the whole argument, and it is the
    OPPOSITE of this repo's usual fail-closed instinct -- which is why it is asserted."""
    monkeypatch.setattr(autonomous_runner, "_pane_content", lambda: "   \n\n")
    verdict = autonomous_runner.usage_limit_verdict()
    assert verdict.limited is False
    assert "no pane content" in verdict.reason


def test_a_verified_limit_carries_the_line_it_read(monkeypatch):
    """THE CLAIM CARRIES ITS PROOF OR IT IS NOT MADE. 3,443 skip lines were logged with no
    evidence, and a reader -- this seat, answering the director -- could not tell them from
    phantoms. A verdict that has to hold its own evidence cannot be written down without it."""
    line = f"Claude.ai usage limit reached. Try again at {_in_minutes(75)}."
    monkeypatch.setattr(autonomous_runner, "_pane_content", lambda: f"blah\n{line}\nblah")
    verdict = autonomous_runner.usage_limit_verdict()
    assert verdict.limited is True
    assert verdict.evidence == line
    assert "lifts in" in verdict.reason


def test_the_skip_is_logged_with_its_evidence(monkeypatch, tmp_path):
    """The log line, not just the verdict -- the ledger is what a human reads six weeks later."""
    autonomous_runner._active_proc = None
    autonomous_runner._turn_times.clear()
    monkeypatch.setattr(autonomous_runner, "CLAUDE_BIN", Path("/usr/bin/true"))
    line = f"Claude.ai usage limit reached. Try again at {_in_minutes(30)}."
    monkeypatch.setattr(autonomous_runner, "_pane_content", lambda: line)

    with patch("background.autonomous_runner.subprocess.Popen"):
        autonomous_runner.launch_turn()

    written = autonomous_runner.LOG_FILE.read_text()
    assert "VERIFIED" in written
    assert "Evidence:" in written
    assert "usage limit reached" in written


def test_max_turns_per_hour_is_positive():
    assert autonomous_runner.MAX_TURNS_PER_HOUR > 0


def test_turn_times_is_deque():
    from collections import deque
    assert isinstance(autonomous_runner._turn_times, deque)


def test_turns_in_last_hour_returns_int():
    autonomous_runner._turn_times.clear()
    result = autonomous_runner.turns_in_last_hour()
    assert isinstance(result, int)

# ── Publish-gate scope (R10, 2026-07-18): DAEMON-LIFECYCLE test module ──────────
# Validates pipeline MACHINERY (process/session lifecycle, scheduling, notify transport,
# reconciliation), never a published business surface -- so it must never wedge the live
# publish. The gate runs `-m 'not operational'`. See tests/conftest.py for the marker.
import pytest  # noqa: E402,F811

pytestmark = pytest.mark.operational
