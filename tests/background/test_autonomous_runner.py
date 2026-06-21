"""Tests for background/autonomous_runner.py."""

import json
import time
from collections import deque
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from background import autonomous_runner


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


def test_usage_limit_active_detects_limit_phrase(monkeypatch):
    monkeypatch.setattr(
        autonomous_runner, "_pane_content",
        lambda: "Claude.ai usage limit reached. Try again at 18:00."
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
        lambda: "Claude.ai usage limit reached."
    )

    with patch("background.autonomous_runner.subprocess.Popen") as mock_popen:
        autonomous_runner.launch_turn()
        mock_popen.assert_not_called()
