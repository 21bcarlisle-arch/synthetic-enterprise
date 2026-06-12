import time

from background import session_watchdog as watchdog


def test_is_yes_reply_matches_message_after_since():
    since = 1000.0
    record = {"event": "message", "time": 1001, "message": "YES, please restart"}
    assert watchdog._is_yes_reply(record, since) is True


def test_is_yes_reply_rejects_messages_before_since():
    since = 1000.0
    record = {"event": "message", "time": 999, "message": "yes"}
    assert watchdog._is_yes_reply(record, since) is False


def test_is_yes_reply_rejects_non_message_events():
    since = 1000.0
    record = {"event": "open", "time": 1001, "message": "yes"}
    assert watchdog._is_yes_reply(record, since) is False


def test_is_yes_reply_rejects_messages_without_yes():
    since = 1000.0
    record = {"event": "message", "time": 1001, "message": "no thanks"}
    assert watchdog._is_yes_reply(record, since) is False


def test_restarts_in_last_hour_counts_recent_only():
    watchdog.restart_times.clear()
    now = time.time()
    watchdog.restart_times.append(now - 3700)  # over an hour ago, should be dropped
    watchdog.restart_times.append(now - 60)
    watchdog.restart_times.append(now - 10)

    assert watchdog.restarts_in_last_hour() == 2
    watchdog.restart_times.clear()


def test_restart_claude_respects_cap(monkeypatch):
    watchdog.restart_times.clear()
    now = time.time()
    for _ in range(watchdog.MAX_RESTARTS_PER_HOUR):
        watchdog.restart_times.append(now)

    subprocess_calls = []
    ntfy_messages = []
    monkeypatch.setattr(watchdog.subprocess, "run", lambda *a, **k: subprocess_calls.append(a))
    monkeypatch.setattr(watchdog, "ntfy", lambda msg: ntfy_messages.append(msg))
    monkeypatch.setattr(watchdog, "log", lambda msg: None)

    watchdog.restart_claude()

    # cap reached: no tmux subprocess calls, just the cap-reached NTFY
    assert subprocess_calls == []
    assert any("cap reached" in msg for msg in ntfy_messages)
    watchdog.restart_times.clear()
