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


def test_usage_limit_detected_matches_known_phrasings():
    assert watchdog.usage_limit_detected("Claude usage limit reached. Try again later.")
    assert watchdog.usage_limit_detected("You are approaching your usage limit reached for this session.")
    assert watchdog.usage_limit_detected("5-hour limit reached — resets at 3pm")
    assert watchdog.usage_limit_detected("Weekly limit reached")
    assert watchdog.usage_limit_detected("Your usage limit will reset at 3pm")


def test_usage_limit_detected_ignores_normal_output():
    assert not watchdog.usage_limit_detected("Running tests...\n96 passed in 0.34s")


def test_usage_limit_detected_ignores_discussion_of_the_pattern():
    # The watchdog's own source/docs/conversation discuss usage limits and
    # rate limits constantly -- bare mentions must not trigger.
    assert not watchdog.usage_limit_detected("rate limit")
    assert not watchdog.usage_limit_detected("5-hour limit")
    assert not watchdog.usage_limit_detected("weekly limit")
    assert not watchdog.usage_limit_detected(
        '"(usage limit reached|approaching[^\\n]*usage limit|rate limit|"'
    )


def test_restart_claude_resume_uses_continue_flag(monkeypatch):
    watchdog.restart_times.clear()
    calls = []
    monkeypatch.setattr(watchdog.subprocess, "run", lambda *a, **k: calls.append(a[0]) or type("R", (), {"returncode": 0})())
    monkeypatch.setattr(watchdog, "ntfy", lambda msg: None)
    monkeypatch.setattr(watchdog, "log", lambda msg: None)
    monkeypatch.setattr(watchdog.time, "sleep", lambda s: None)

    watchdog.restart_claude(resume=True)

    send_keys_calls = [c for c in calls if c[:2] == ["tmux", "send-keys"]]
    assert ["tmux", "send-keys", "-t", watchdog.SESSION_NAME, "claude -c", "Enter"] in send_keys_calls
    # resume=True should NOT also send RESUME_INSTRUCTION
    assert not any(watchdog.RESUME_INSTRUCTION in c for c in send_keys_calls)
    watchdog.restart_times.clear()


def test_handle_usage_limit_resumes_in_place_once_message_clears(monkeypatch):
    monkeypatch.setattr(watchdog, "log", lambda msg: None)
    ntfy_messages = []
    monkeypatch.setattr(watchdog, "ntfy", lambda msg: ntfy_messages.append(msg))
    monkeypatch.setattr(watchdog.time, "sleep", lambda s: None)
    monkeypatch.setattr(watchdog, "session_exists", lambda: True)
    monkeypatch.setattr(watchdog, "claude_is_running", lambda: True)

    send_keys_calls = []
    monkeypatch.setattr(watchdog.subprocess, "run", lambda *a, **k: send_keys_calls.append(a[0]) or type("R", (), {"returncode": 0})())
    # First poll: still limited; second poll: cleared.
    pane_outputs = iter(["usage limit reached", "all clear, continuing"])
    monkeypatch.setattr(watchdog, "capture_pane", lambda: next(pane_outputs))

    watchdog.handle_usage_limit()

    assert any("resumed automatically" in msg for msg in ntfy_messages)
    assert any(c[:2] == ["tmux", "send-keys"] for c in send_keys_calls)


def test_queue_downtime_tasks_appends_to_queued_section(tmp_path, monkeypatch):
    tasks_file = tmp_path / "background-tasks.md"
    tasks_file.write_text("# Background Task Queue\n\n## QUEUED\n\n## RUNNING\n(none)\n")
    monkeypatch.setattr(watchdog, "DOWNTIME_TASKS_FILE", tasks_file)
    monkeypatch.setattr(watchdog, "log", lambda msg: None)

    watchdog.queue_downtime_tasks()

    content = tasks_file.read_text()
    for task in watchdog.DOWNTIME_TASKS:
        assert f"### Task: {task['name']}" in content
        assert f"Model: {task['model']}" in content
    # appended before the RUNNING section
    assert content.index("## QUEUED") < content.index(watchdog.DOWNTIME_TASKS[0]["name"])
    assert content.index(watchdog.DOWNTIME_TASKS[-1]["name"]) < content.index("## RUNNING")


def test_queue_downtime_tasks_is_idempotent(tmp_path, monkeypatch):
    tasks_file = tmp_path / "background-tasks.md"
    tasks_file.write_text("# Background Task Queue\n\n## QUEUED\n\n## RUNNING\n(none)\n")
    monkeypatch.setattr(watchdog, "DOWNTIME_TASKS_FILE", tasks_file)
    monkeypatch.setattr(watchdog, "log", lambda msg: None)

    watchdog.queue_downtime_tasks()
    once = tasks_file.read_text()
    watchdog.queue_downtime_tasks()
    twice = tasks_file.read_text()

    assert once == twice


def test_handle_usage_limit_queues_downtime_tasks(tmp_path, monkeypatch):
    tasks_file = tmp_path / "background-tasks.md"
    tasks_file.write_text("# Background Task Queue\n\n## QUEUED\n\n## RUNNING\n(none)\n")
    monkeypatch.setattr(watchdog, "DOWNTIME_TASKS_FILE", tasks_file)
    monkeypatch.setattr(watchdog, "log", lambda msg: None)
    monkeypatch.setattr(watchdog, "ntfy", lambda msg: None)
    monkeypatch.setattr(watchdog.time, "sleep", lambda s: None)
    monkeypatch.setattr(watchdog, "session_exists", lambda: True)
    monkeypatch.setattr(watchdog, "claude_is_running", lambda: True)
    monkeypatch.setattr(watchdog.subprocess, "run", lambda *a, **k: type("R", (), {"returncode": 0})())
    monkeypatch.setattr(watchdog, "capture_pane", lambda: "all clear")

    watchdog.handle_usage_limit()

    content = tasks_file.read_text()
    for task in watchdog.DOWNTIME_TASKS:
        assert f"### Task: {task['name']}" in content


def _reset_autoloop_state():
    watchdog.autoloop_times.clear()
    watchdog._autoloop_last_pane = None
    watchdog._autoloop_idle_streak = 0
    watchdog._autoloop_waiting_notified = False


def test_check_autoloop_resets_streak_on_pane_change(monkeypatch):
    _reset_autoloop_state()
    monkeypatch.setattr(watchdog, "log", lambda msg: None)
    monkeypatch.setattr(watchdog, "ntfy", lambda msg: None)
    send_keys_calls = []
    monkeypatch.setattr(watchdog.subprocess, "run", lambda *a, **k: send_keys_calls.append(a[0]) or type("R", (), {"returncode": 0})())

    for pane in ["working...", "still working...", "now done."]:
        watchdog.check_autoloop(pane)

    assert send_keys_calls == []
    assert watchdog._autoloop_idle_streak == 0
    _reset_autoloop_state()


def test_check_autoloop_sends_instruction_after_idle_streak(monkeypatch):
    _reset_autoloop_state()
    monkeypatch.setattr(watchdog, "log", lambda msg: None)
    ntfy_messages = []
    monkeypatch.setattr(watchdog, "ntfy", lambda msg: ntfy_messages.append(msg))
    send_keys_calls = []
    monkeypatch.setattr(watchdog.subprocess, "run", lambda *a, **k: send_keys_calls.append(a[0]) or type("R", (), {"returncode": 0})())

    idle_pane = "Claude Code is idle at the prompt"
    for _ in range(watchdog.AUTOLOOP_IDLE_CHECKS + 1):
        watchdog.check_autoloop(idle_pane)

    assert ["tmux", "send-keys", "-t", watchdog.SESSION_NAME, watchdog.AUTOLOOP_INSTRUCTION, "Enter"] in send_keys_calls
    assert any("milestone reached" in msg for msg in ntfy_messages)
    _reset_autoloop_state()


def test_check_autoloop_pauses_on_review_gate(monkeypatch):
    _reset_autoloop_state()
    monkeypatch.setattr(watchdog, "log", lambda msg: None)
    ntfy_messages = []
    monkeypatch.setattr(watchdog, "ntfy", lambda msg: ntfy_messages.append(msg))
    send_keys_calls = []
    monkeypatch.setattr(watchdog.subprocess, "run", lambda *a, **k: send_keys_calls.append(a[0]) or type("R", (), {"returncode": 0})())

    review_gate_pane = "Summary complete. REVIEW_GATE: awaiting Rich's review of Phase 4b-4."
    for _ in range(watchdog.AUTOLOOP_IDLE_CHECKS + 2):
        watchdog.check_autoloop(review_gate_pane)

    assert send_keys_calls == []
    assert sum("REVIEW_GATE" in msg for msg in ntfy_messages) == 1
    _reset_autoloop_state()


def test_check_autoloop_pauses_on_permission_prompt(monkeypatch):
    _reset_autoloop_state()
    monkeypatch.setattr(watchdog, "log", lambda msg: None)
    ntfy_messages = []
    monkeypatch.setattr(watchdog, "ntfy", lambda msg: ntfy_messages.append(msg))
    send_keys_calls = []
    monkeypatch.setattr(watchdog.subprocess, "run", lambda *a, **k: send_keys_calls.append(a[0]) or type("R", (), {"returncode": 0})())

    prompt_pane = "Bash command\n\nDo you want to proceed?\n❯ 1. Yes\n  2. No"
    for _ in range(watchdog.AUTOLOOP_IDLE_CHECKS + 2):
        watchdog.check_autoloop(prompt_pane)

    assert send_keys_calls == []
    assert sum("permission prompt" in msg for msg in ntfy_messages) == 1
    _reset_autoloop_state()


def test_check_autoloop_respects_cap(monkeypatch):
    _reset_autoloop_state()
    now = time.time()
    for _ in range(watchdog.MAX_AUTOLOOP_PER_HOUR):
        watchdog.autoloop_times.append(now)

    monkeypatch.setattr(watchdog, "log", lambda msg: None)
    ntfy_messages = []
    monkeypatch.setattr(watchdog, "ntfy", lambda msg: ntfy_messages.append(msg))
    send_keys_calls = []
    monkeypatch.setattr(watchdog.subprocess, "run", lambda *a, **k: send_keys_calls.append(a[0]) or type("R", (), {"returncode": 0})())

    idle_pane = "Claude Code is idle at the prompt"
    for _ in range(watchdog.AUTOLOOP_IDLE_CHECKS + 1):
        watchdog.check_autoloop(idle_pane)

    assert send_keys_calls == []
    assert any("cap reached" in msg for msg in ntfy_messages)
    _reset_autoloop_state()


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
