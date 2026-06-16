import json
import time
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from background import session_watchdog as watchdog


def test_ntfy_default_uses_done_priority_and_tag(monkeypatch):
    calls = []
    monkeypatch.setattr(
        watchdog.subprocess, "run",
        lambda cmd, **kw: calls.append(cmd) or type("R", (), {"stdout": "{}"})(),
    )
    watchdog.ntfy("done")
    cmd = calls[0]
    assert "X-Priority: default" in cmd
    assert "X-Tags: white_check_mark" in cmd


def test_ntfy_needs_input_uses_high_priority_and_warning_tag(monkeypatch):
    calls = []
    monkeypatch.setattr(
        watchdog.subprocess, "run",
        lambda cmd, **kw: calls.append(cmd) or type("R", (), {"stdout": "{}"})(),
    )
    watchdog.ntfy("please review", needs_input=True)
    cmd = calls[0]
    assert "X-Priority: high" in cmd
    assert "X-Tags: warning" in cmd


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
    monkeypatch.setattr(watchdog, "ntfy", lambda msg, needs_input=False: None)
    monkeypatch.setattr(watchdog, "log", lambda msg, needs_input=False: None)
    monkeypatch.setattr(watchdog.time, "sleep", lambda s: None)

    watchdog.restart_claude(resume=True)

    send_keys_calls = [c for c in calls if c[:2] == ["tmux", "send-keys"]]
    assert ["tmux", "send-keys", "-t", watchdog.SESSION_NAME, "claude -c", "Enter"] in send_keys_calls
    # resume=True should NOT also send RESUME_INSTRUCTION
    assert not any(watchdog.RESUME_INSTRUCTION in c for c in send_keys_calls)
    watchdog.restart_times.clear()


def test_handle_usage_limit_resumes_in_place_once_message_clears(monkeypatch):
    monkeypatch.setattr(watchdog, "log", lambda msg, needs_input=False: None)
    ntfy_messages = []
    monkeypatch.setattr(watchdog, "ntfy", lambda msg, needs_input=False: ntfy_messages.append(msg))
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
    monkeypatch.setattr(watchdog, "log", lambda msg, needs_input=False: None)

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
    monkeypatch.setattr(watchdog, "log", lambda msg, needs_input=False: None)

    watchdog.queue_downtime_tasks()
    once = tasks_file.read_text()
    watchdog.queue_downtime_tasks()
    twice = tasks_file.read_text()

    assert once == twice


def test_handle_usage_limit_queues_downtime_tasks(tmp_path, monkeypatch):
    tasks_file = tmp_path / "background-tasks.md"
    tasks_file.write_text("# Background Task Queue\n\n## QUEUED\n\n## RUNNING\n(none)\n")
    monkeypatch.setattr(watchdog, "DOWNTIME_TASKS_FILE", tasks_file)
    monkeypatch.setattr(watchdog, "log", lambda msg, needs_input=False: None)
    monkeypatch.setattr(watchdog, "ntfy", lambda msg, needs_input=False: None)
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
    watchdog._autoloop_gate_clear_streak = 0
    watchdog._usage_pause_notified = False


def test_check_autoloop_resets_streak_on_pane_change(monkeypatch):
    _reset_autoloop_state()
    monkeypatch.setattr(watchdog, "log", lambda msg, needs_input=False: None)
    monkeypatch.setattr(watchdog, "ntfy", lambda msg, needs_input=False: None)
    send_keys_calls = []
    monkeypatch.setattr(watchdog.subprocess, "run", lambda *a, **k: send_keys_calls.append(a[0]) or type("R", (), {"returncode": 0})())

    for pane in ["working...", "still working...", "now done."]:
        watchdog.check_autoloop(pane)

    assert send_keys_calls == []
    assert watchdog._autoloop_idle_streak == 0
    _reset_autoloop_state()


def test_check_autoloop_sends_instruction_after_idle_streak(monkeypatch):
    _reset_autoloop_state()
    monkeypatch.setattr(watchdog, "log", lambda msg, needs_input=False: None)
    ntfy_messages = []
    monkeypatch.setattr(watchdog, "ntfy", lambda msg, needs_input=False: ntfy_messages.append(msg))
    send_keys_calls = []
    monkeypatch.setattr(watchdog.subprocess, "run", lambda *a, **k: send_keys_calls.append(a[0]) or type("R", (), {"returncode": 0})())
    monkeypatch.setattr(watchdog, "check_session_usage", lambda: (33, "4:59pm", "Europe/London"))

    idle_pane = "Claude Code is idle at the prompt"
    for _ in range(watchdog.AUTOLOOP_IDLE_CHECKS + 1):
        watchdog.check_autoloop(idle_pane)

    assert ["tmux", "send-keys", "-t", watchdog.SESSION_NAME, watchdog.AUTOLOOP_INSTRUCTION, "Enter"] in send_keys_calls
    # No "milestone reached" NTFY — removed to reduce notification noise (Rich's request 2026-06-16)
    assert not any("milestone reached" in msg for msg in ntfy_messages)
    _reset_autoloop_state()


def test_check_autoloop_pauses_on_review_gate(monkeypatch, tmp_path):
    _reset_autoloop_state()
    monkeypatch.setattr(watchdog, "log", lambda msg, needs_input=False: None)
    monkeypatch.setattr(watchdog, "RESPONSES_DIR", tmp_path / "responses")
    monkeypatch.setattr(watchdog, "GATE_TOKENS_DIR", tmp_path / "tokens")
    ntfy_messages = []
    monkeypatch.setattr(watchdog, "ntfy", lambda msg, needs_input=False: ntfy_messages.append(msg))
    gate_calls = []
    monkeypatch.setattr(watchdog, "ntfy_gate", lambda msg, gate, token: gate_calls.append((msg, gate, token)))
    send_keys_calls = []
    monkeypatch.setattr(watchdog.subprocess, "run", lambda *a, **k: send_keys_calls.append(a[0]) or type("R", (), {"returncode": 0})())

    review_gate_pane = "Summary complete. REVIEW_GATE: awaiting Rich's review of Phase 4b-4."
    for _ in range(watchdog.AUTOLOOP_IDLE_CHECKS + 2):
        watchdog.check_autoloop(review_gate_pane)

    assert send_keys_calls == []
    assert len(gate_calls) == 1
    assert "REVIEW_GATE" in gate_calls[0][0]
    assert gate_calls[0][1] == watchdog.GATE_ID
    assert ntfy_messages == []
    _reset_autoloop_state()


def test_check_autoloop_relays_gate_response(monkeypatch, tmp_path):
    _reset_autoloop_state()
    monkeypatch.setattr(watchdog, "log", lambda msg, needs_input=False: None)
    responses_dir = tmp_path / "responses"
    responses_dir.mkdir()
    monkeypatch.setattr(watchdog, "RESPONSES_DIR", responses_dir)
    monkeypatch.setattr(watchdog, "GATE_TOKENS_DIR", tmp_path / "tokens")
    (responses_dir / f"{watchdog.GATE_ID}.json").write_text(
        json.dumps({"gate": watchdog.GATE_ID, "decision": "Rich approved — proceed."})
    )
    ntfy_messages = []
    monkeypatch.setattr(watchdog, "ntfy", lambda msg, needs_input=False: ntfy_messages.append(msg))
    send_keys_calls = []
    monkeypatch.setattr(watchdog.subprocess, "run", lambda *a, **k: send_keys_calls.append(a[0]) or type("R", (), {"returncode": 0})())

    review_gate_pane = "Summary complete. REVIEW_GATE: awaiting Rich's review of Phase 4b-4."
    # REVIEW_GATE_PATTERN is only checked once the pane has been idle
    # (unchanged) for AUTOLOOP_IDLE_CHECKS consecutive polls.
    for _ in range(watchdog.AUTOLOOP_IDLE_CHECKS + 1):
        watchdog.check_autoloop(review_gate_pane)

    assert ["tmux", "send-keys", "-t", watchdog.SESSION_NAME, "Rich approved — proceed.", "Enter"] in send_keys_calls
    assert not (responses_dir / f"{watchdog.GATE_ID}.json").exists()
    assert any("Rich approved" in msg for msg in ntfy_messages)
    _reset_autoloop_state()


def test_generate_gate_token_creates_single_use_token(tmp_path, monkeypatch):
    monkeypatch.setattr(watchdog, "GATE_TOKENS_DIR", tmp_path / "tokens")
    token = watchdog.generate_gate_token("main")
    assert (tmp_path / "tokens" / "main.token").read_text(encoding="utf-8") == token
    assert len(token) > 10


def test_read_and_clear_response_consumes_file(tmp_path, monkeypatch):
    responses_dir = tmp_path / "responses"
    responses_dir.mkdir()
    monkeypatch.setattr(watchdog, "RESPONSES_DIR", responses_dir)
    (responses_dir / "main.json").write_text(json.dumps({"gate": "main", "decision": "hold"}))

    result = watchdog.read_and_clear_response("main")
    assert result == {"gate": "main", "decision": "hold"}
    assert not (responses_dir / "main.json").exists()


def test_read_and_clear_response_returns_none_when_absent(tmp_path, monkeypatch):
    monkeypatch.setattr(watchdog, "RESPONSES_DIR", tmp_path / "responses")
    assert watchdog.read_and_clear_response("main") is None


def test_gate_actions_header_escapes_commas_and_includes_token():
    header = watchdog._gate_actions_header("main", "tok123")
    assert "tok123" in header
    # Two semicolon-separated actions (Approve, Hold), each an "http" action.
    actions = header.split("; ")
    assert len(actions) == 2
    for action in actions:
        assert action.startswith("http, ")
        assert f"{watchdog.FUNNEL_BASE_URL}/respond" in action
    # The "Approve, proceed" label's comma must be escaped, not a field separator.
    assert "Approve\\, proceed" in header


def test_ntfy_gate_sends_actions_header(monkeypatch):
    calls = []
    monkeypatch.setattr(
        watchdog.subprocess, "run",
        lambda cmd, **kw: calls.append(cmd) or type("R", (), {"stdout": "{}"})(),
    )
    watchdog.ntfy_gate("waiting for review", "main", "tok123")
    cmd = calls[0]
    assert "X-Priority: high" in cmd
    assert "X-Tags: warning" in cmd
    assert any(c.startswith("X-Actions: ") and "tok123" in c for c in cmd)


def test_check_autoloop_pauses_on_permission_prompt(monkeypatch):
    _reset_autoloop_state()
    monkeypatch.setattr(watchdog, "log", lambda msg, needs_input=False: None)
    ntfy_messages = []
    monkeypatch.setattr(watchdog, "ntfy", lambda msg, needs_input=False: ntfy_messages.append(msg))
    send_keys_calls = []
    monkeypatch.setattr(watchdog.subprocess, "run", lambda *a, **k: send_keys_calls.append(a[0]) or type("R", (), {"returncode": 0})())

    prompt_pane = "Bash command\n\nDo you want to proceed?\n❯ 1. Yes\n  2. No"
    for _ in range(watchdog.AUTOLOOP_IDLE_CHECKS + 2):
        watchdog.check_autoloop(prompt_pane)

    assert send_keys_calls == []
    assert sum("permission prompt" in msg for msg in ntfy_messages) == 1
    _reset_autoloop_state()


def test_check_autoloop_debounces_gate_clear_flicker(monkeypatch, tmp_path):
    """A single capture where REVIEW_GATE_PATTERN no longer matches (e.g. the
    viewport shifted by a line) must not clear _autoloop_waiting_notified —
    otherwise the gate text reappearing on the next poll would trigger a
    duplicate ntfy_gate notification."""
    _reset_autoloop_state()
    monkeypatch.setattr(watchdog, "log", lambda msg, needs_input=False: None)
    monkeypatch.setattr(watchdog, "RESPONSES_DIR", tmp_path / "responses")
    monkeypatch.setattr(watchdog, "GATE_TOKENS_DIR", tmp_path / "tokens")
    monkeypatch.setattr(watchdog, "ntfy", lambda msg, needs_input=False: None)
    gate_calls = []
    monkeypatch.setattr(watchdog, "ntfy_gate", lambda msg, gate, token: gate_calls.append((msg, gate, token)))
    monkeypatch.setattr(watchdog.subprocess, "run", lambda *a, **k: type("R", (), {"returncode": 0})())

    gate_pane = "Summary complete. REVIEW_GATE: awaiting Rich's review of Phase 4b-4."
    other_pane = "Summary complete. awaiting Rich's review of Phase 4b-4."

    # REVIEW_GATE_PATTERN is only checked once the pane has been idle
    # (unchanged) for AUTOLOOP_IDLE_CHECKS consecutive polls.
    for _ in range(watchdog.AUTOLOOP_IDLE_CHECKS + 1):
        watchdog.check_autoloop(gate_pane)
    assert len(gate_calls) == 1

    # One-off flicker where the pane changes, then back again — must not
    # clear _autoloop_waiting_notified (which would allow a re-notification)
    # on a single flicker.
    watchdog.check_autoloop(other_pane)
    watchdog.check_autoloop(gate_pane)
    assert len(gate_calls) == 1
    _reset_autoloop_state()


def test_check_autoloop_respects_cap(monkeypatch):
    _reset_autoloop_state()
    now = time.time()
    for _ in range(watchdog.MAX_AUTOLOOP_PER_HOUR):
        watchdog.autoloop_times.append(now)

    monkeypatch.setattr(watchdog, "log", lambda msg, needs_input=False: None)
    ntfy_messages = []
    monkeypatch.setattr(watchdog, "ntfy", lambda msg, needs_input=False: ntfy_messages.append(msg))
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
    monkeypatch.setattr(watchdog, "ntfy", lambda msg, needs_input=False: ntfy_messages.append(msg))
    monkeypatch.setattr(watchdog, "log", lambda msg, needs_input=False: None)

    watchdog.restart_claude()

    # cap reached: no tmux subprocess calls, just the cap-reached NTFY
    assert subprocess_calls == []
    assert any("cap reached" in msg for msg in ntfy_messages)
    watchdog.restart_times.clear()


def test_usage_pause_active_false_when_no_file(tmp_path, monkeypatch):
    monkeypatch.setattr(watchdog, "USAGE_PAUSE_FILE", tmp_path / ".usage_pause.json")
    assert watchdog.usage_pause_active() is False


def test_usage_pause_active_true_when_resume_in_future(tmp_path, monkeypatch):
    pause_file = tmp_path / ".usage_pause.json"
    resume_at = datetime.now(timezone.utc) + timedelta(hours=1)
    pause_file.write_text(json.dumps({"resume_at": resume_at.isoformat()}))
    monkeypatch.setattr(watchdog, "USAGE_PAUSE_FILE", pause_file)

    assert watchdog.usage_pause_active() is True
    assert pause_file.is_file()  # not consumed while still active


def test_usage_pause_active_clears_file_once_resume_time_passes(tmp_path, monkeypatch):
    pause_file = tmp_path / ".usage_pause.json"
    resume_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    pause_file.write_text(json.dumps({"resume_at": resume_at.isoformat()}))
    monkeypatch.setattr(watchdog, "USAGE_PAUSE_FILE", pause_file)
    monkeypatch.setattr(watchdog, "log", lambda msg, needs_input=False: None)
    ntfy_messages = []
    monkeypatch.setattr(watchdog, "ntfy", lambda msg, needs_input=False: ntfy_messages.append(msg))

    assert watchdog.usage_pause_active() is False
    assert not pause_file.is_file()
    # No "resuming" NTFY — removed to reduce notification noise (Rich's request 2026-06-16)
    assert not any("resuming" in msg for msg in ntfy_messages)


def test_usage_pause_active_clears_malformed_file(tmp_path, monkeypatch):
    pause_file = tmp_path / ".usage_pause.json"
    pause_file.write_text("not json")
    monkeypatch.setattr(watchdog, "USAGE_PAUSE_FILE", pause_file)
    monkeypatch.setattr(watchdog, "log", lambda msg, needs_input=False: None)

    assert watchdog.usage_pause_active() is False
    assert not pause_file.is_file()


def test_check_autoloop_suppressed_while_usage_pause_active(tmp_path, monkeypatch):
    _reset_autoloop_state()
    pause_file = tmp_path / ".usage_pause.json"
    resume_at = datetime.now(timezone.utc) + timedelta(hours=1)
    pause_file.write_text(json.dumps({"resume_at": resume_at.isoformat()}))
    monkeypatch.setattr(watchdog, "USAGE_PAUSE_FILE", pause_file)
    monkeypatch.setattr(watchdog, "log", lambda msg, needs_input=False: None)
    monkeypatch.setattr(watchdog, "ntfy", lambda msg, needs_input=False: None)
    send_keys_calls = []
    monkeypatch.setattr(watchdog.subprocess, "run", lambda *a, **k: send_keys_calls.append(a[0]) or type("R", (), {"returncode": 0})())

    idle_pane = "Claude Code is idle at the prompt"
    for _ in range(watchdog.AUTOLOOP_IDLE_CHECKS + 2):
        watchdog.check_autoloop(idle_pane)

    assert send_keys_calls == []
    assert watchdog._usage_pause_notified is True
    _reset_autoloop_state()


def test_check_autoloop_resumes_after_usage_pause_expires(tmp_path, monkeypatch):
    _reset_autoloop_state()
    pause_file = tmp_path / ".usage_pause.json"
    resume_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    pause_file.write_text(json.dumps({"resume_at": resume_at.isoformat()}))
    monkeypatch.setattr(watchdog, "USAGE_PAUSE_FILE", pause_file)
    monkeypatch.setattr(watchdog, "log", lambda msg, needs_input=False: None)
    ntfy_messages = []
    monkeypatch.setattr(watchdog, "ntfy", lambda msg, needs_input=False: ntfy_messages.append(msg))
    send_keys_calls = []
    monkeypatch.setattr(watchdog.subprocess, "run", lambda *a, **k: send_keys_calls.append(a[0]) or type("R", (), {"returncode": 0})())
    monkeypatch.setattr(watchdog, "check_session_usage", lambda: (33, "4:59pm", "Europe/London"))

    idle_pane = "Claude Code is idle at the prompt"
    for _ in range(watchdog.AUTOLOOP_IDLE_CHECKS + 1):
        watchdog.check_autoloop(idle_pane)

    assert ["tmux", "send-keys", "-t", watchdog.SESSION_NAME, watchdog.AUTOLOOP_INSTRUCTION, "Enter"] in send_keys_calls
    assert not pause_file.is_file()
    _reset_autoloop_state()


def test_parse_usage_pane_extracts_pct_reset_time_and_tz():
    pane_text = (
        "Current session · Resets 4:59pm (Europe/London)\n"
        "██████████████████\n"
        "                                                          33% used\n"
    )
    assert watchdog.parse_usage_pane(pane_text) == (33, "4:59pm", "Europe/London")


def test_parse_usage_pane_returns_none_without_usage_block():
    assert watchdog.parse_usage_pane("Claude Code is idle at the prompt") is None


def test_usage_resume_at_returns_future_utc_iso8601():
    tz = ZoneInfo("Europe/London")
    now_local = datetime.now(tz)
    future_time = (now_local + timedelta(hours=1)).strftime("%I:%M%p").lstrip("0").lower()

    resume_at = watchdog._usage_resume_at(future_time, "Europe/London")

    resume_dt = datetime.fromisoformat(resume_at)
    assert resume_dt.tzinfo is not None
    assert resume_dt > datetime.now(timezone.utc)


def test_check_session_usage_sends_standalone_usage_and_dismisses(monkeypatch):
    send_keys_calls = []
    monkeypatch.setattr(watchdog.subprocess, "run", lambda *a, **k: send_keys_calls.append(a[0]) or type("R", (), {"returncode": 0})())
    monkeypatch.setattr(watchdog, "capture_pane", lambda: "Current session · Resets 4:59pm (Europe/London)\n33% used\n")
    monkeypatch.setattr(watchdog.time, "sleep", lambda s: None)

    result = watchdog.check_session_usage()

    assert result == (33, "4:59pm", "Europe/London")
    assert ["tmux", "send-keys", "-t", watchdog.SESSION_NAME, "/usage", "Enter"] in send_keys_calls
    assert ["tmux", "send-keys", "-t", watchdog.SESSION_NAME, "Escape"] in send_keys_calls


def test_check_autoloop_writes_usage_pause_file_at_threshold(tmp_path, monkeypatch):
    _reset_autoloop_state()
    pause_file = tmp_path / ".usage_pause.json"
    monkeypatch.setattr(watchdog, "USAGE_PAUSE_FILE", pause_file)
    monkeypatch.setattr(watchdog, "log", lambda msg, needs_input=False: None)
    ntfy_messages = []
    monkeypatch.setattr(watchdog, "ntfy", lambda msg, needs_input=False: ntfy_messages.append(msg))
    send_keys_calls = []
    monkeypatch.setattr(watchdog.subprocess, "run", lambda *a, **k: send_keys_calls.append(a[0]) or type("R", (), {"returncode": 0})())
    monkeypatch.setattr(watchdog, "check_session_usage", lambda: (92, "4:59pm", "Europe/London"))

    idle_pane = "Claude Code is idle at the prompt"
    for _ in range(watchdog.AUTOLOOP_IDLE_CHECKS + 1):
        watchdog.check_autoloop(idle_pane)

    assert ["tmux", "send-keys", "-t", watchdog.SESSION_NAME, watchdog.AUTOLOOP_INSTRUCTION, "Enter"] not in send_keys_calls
    assert pause_file.is_file()
    data = json.loads(pause_file.read_text())
    assert "resume_at" in data
    assert any("92%" in msg for msg in ntfy_messages)
    _reset_autoloop_state()


def test_check_inbound_commands_relays_new_message(monkeypatch):
    send_keys_calls = []
    monkeypatch.setattr(watchdog, "log", lambda msg, needs_input=False: None)
    monkeypatch.setattr(
        watchdog.subprocess, "run",
        lambda *a, **k: send_keys_calls.append(a[0]) or type("R", (), {"returncode": 0})(),
    )
    monkeypatch.setattr(watchdog, "was_sent_by_us", lambda msg_id: False)

    body = "\n".join([
        json.dumps({"id": "in1", "event": "message", "time": 2000, "message": "what's the capital cost ratio?"}),
    ])
    monkeypatch.setattr(
        watchdog.requests, "get",
        lambda *a, **k: type("R", (), {"text": body})(),
    )

    new_since = watchdog.check_inbound_commands("idle prompt", since=1000)

    assert new_since == 2000
    assert len(send_keys_calls) == 1
    cmd = send_keys_calls[0]
    assert cmd[:4] == ["tmux", "send-keys", "-t", watchdog.SESSION_NAME]
    assert "what's the capital cost ratio?" in cmd[4]
    assert "Received via NTFY from Rich's phone" in cmd[4]
    assert cmd[5] == "Enter"


def test_check_inbound_commands_handles_usage_directly(monkeypatch):
    send_keys_calls = []
    ntfy_messages = []
    monkeypatch.setattr(watchdog, "log", lambda msg, needs_input=False: None)
    monkeypatch.setattr(
        watchdog.subprocess, "run",
        lambda *a, **k: send_keys_calls.append(a[0]) or type("R", (), {"returncode": 0})(),
    )
    monkeypatch.setattr(watchdog, "was_sent_by_us", lambda msg_id: False)
    monkeypatch.setattr(watchdog, "send_ntfy", lambda msg, headers=None: ntfy_messages.append(msg))
    monkeypatch.setattr(watchdog, "check_session_usage", lambda: (33, "4:59pm", "Europe/London"))

    body = json.dumps({"id": "in1", "event": "message", "time": 2000, "message": "/usage"})
    monkeypatch.setattr(
        watchdog.requests, "get",
        lambda *a, **k: type("R", (), {"text": body})(),
    )

    new_since = watchdog.check_inbound_commands("idle prompt", since=1000)

    assert new_since == 2000
    # /usage is handled directly, not relayed to the session
    assert send_keys_calls == []
    assert len(ntfy_messages) == 1
    assert "33%" in ntfy_messages[0]
    assert "4:59pm" in ntfy_messages[0]
    assert "Europe/London" in ntfy_messages[0]


def test_check_inbound_commands_usage_reports_fallback_when_unreadable(monkeypatch):
    ntfy_messages = []
    monkeypatch.setattr(watchdog, "log", lambda msg, needs_input=False: None)
    monkeypatch.setattr(
        watchdog.subprocess, "run",
        lambda *a, **k: type("R", (), {"returncode": 0})(),
    )
    monkeypatch.setattr(watchdog, "was_sent_by_us", lambda msg_id: False)
    monkeypatch.setattr(watchdog, "send_ntfy", lambda msg, headers=None: ntfy_messages.append(msg))
    monkeypatch.setattr(watchdog, "check_session_usage", lambda: None)

    body = json.dumps({"id": "in1", "event": "message", "time": 2000, "message": "/usage"})
    monkeypatch.setattr(
        watchdog.requests, "get",
        lambda *a, **k: type("R", (), {"text": body})(),
    )

    new_since = watchdog.check_inbound_commands("idle prompt", since=1000)

    assert new_since == 2000
    assert len(ntfy_messages) == 1
    assert "try again" in ntfy_messages[0].lower()


def test_check_inbound_commands_skips_own_messages(monkeypatch):
    send_keys_calls = []
    monkeypatch.setattr(watchdog, "log", lambda msg, needs_input=False: None)
    monkeypatch.setattr(
        watchdog.subprocess, "run",
        lambda *a, **k: send_keys_calls.append(a[0]) or type("R", (), {"returncode": 0})(),
    )
    monkeypatch.setattr(watchdog, "was_sent_by_us", lambda msg_id: msg_id == "own1")

    body = "\n".join([
        json.dumps({"id": "own1", "event": "message", "time": 2000, "message": "Claude Code milestone reached"}),
    ])
    monkeypatch.setattr(
        watchdog.requests, "get",
        lambda *a, **k: type("R", (), {"text": body})(),
    )

    new_since = watchdog.check_inbound_commands("idle prompt", since=1000)

    assert new_since == 2000
    assert send_keys_calls == []


def test_check_inbound_commands_ignores_messages_before_since(monkeypatch):
    send_keys_calls = []
    monkeypatch.setattr(watchdog, "log", lambda msg, needs_input=False: None)
    monkeypatch.setattr(
        watchdog.subprocess, "run",
        lambda *a, **k: send_keys_calls.append(a[0]) or type("R", (), {"returncode": 0})(),
    )
    monkeypatch.setattr(watchdog, "was_sent_by_us", lambda msg_id: False)

    body = json.dumps({"id": "old1", "event": "message", "time": 500, "message": "old message"})
    monkeypatch.setattr(
        watchdog.requests, "get",
        lambda *a, **k: type("R", (), {"text": body})(),
    )

    new_since = watchdog.check_inbound_commands("idle prompt", since=1000)

    assert new_since == 1000
    assert send_keys_calls == []


def test_check_inbound_commands_defers_when_permission_prompt_visible(monkeypatch):
    send_keys_calls = []
    monkeypatch.setattr(watchdog, "log", lambda msg, needs_input=False: None)
    monkeypatch.setattr(
        watchdog.subprocess, "run",
        lambda *a, **k: send_keys_calls.append(a[0]) or type("R", (), {"returncode": 0})(),
    )
    monkeypatch.setattr(watchdog, "was_sent_by_us", lambda msg_id: False)

    body = json.dumps({"id": "in1", "event": "message", "time": 2000, "message": "steer away"})
    monkeypatch.setattr(
        watchdog.requests, "get",
        lambda *a, **k: type("R", (), {"text": body})(),
    )

    new_since = watchdog.check_inbound_commands("Do you want to proceed? (y/n)", since=1000)

    assert new_since == 1000
    assert send_keys_calls == []


def test_check_inbound_commands_handles_poll_error(monkeypatch):
    monkeypatch.setattr(watchdog, "log", lambda msg, needs_input=False: None)

    def _raise(*a, **k):
        raise watchdog.requests.RequestException("boom")

    monkeypatch.setattr(watchdog.requests, "get", _raise)

    new_since = watchdog.check_inbound_commands("idle prompt", since=1000)

    assert new_since == 1000


def test_load_and_save_command_since_roundtrip(tmp_path, monkeypatch):
    since_file = tmp_path / ".ntfy_command_since.json"
    monkeypatch.setattr(watchdog, "NTFY_COMMAND_SINCE_FILE", since_file)

    watchdog._save_command_since(12345.0)
    assert watchdog._load_command_since() == 12345.0


def test_load_command_since_defaults_to_now_when_missing(tmp_path, monkeypatch):
    since_file = tmp_path / ".ntfy_command_since.json"
    monkeypatch.setattr(watchdog, "NTFY_COMMAND_SINCE_FILE", since_file)
    monkeypatch.setattr(watchdog.time, "time", lambda: 99999.0)

    assert watchdog._load_command_since() == 99999.0
