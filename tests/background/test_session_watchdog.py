import json
import time
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from background import session_watchdog as watchdog

# Several tests here monkeypatch subprocess.run (a single shared stdlib module
# object, so this also affects ntfy_utils.send_ntfy's own call) rather than
# send_ntfy itself -- the real send_ntfy body, including its mirror call
# (ADVISOR_VISIBILITY.md's background/ntfy_mirror.py), still runs. No per-file
# isolation needed: ntfy_mirror.append_mirror_entry() has its own structural
# PYTEST_CURRENT_TEST guard (same pattern as tmux_relay.py).


# ── Phase QB (WATCHDOG_NO_SENDKEYS.md): nvm binary resolution ────────────────

def test_resolve_claude_binary_finds_installed_version(monkeypatch, tmp_path):
    fake_bin = tmp_path / "v24.16.0" / "bin" / "claude"
    fake_bin.parent.mkdir(parents=True)
    fake_bin.write_text("#!/bin/sh\n")
    monkeypatch.setattr(watchdog, "CLAUDE_NVM_GLOB", str(tmp_path / "*" / "bin" / "claude"))
    assert watchdog.resolve_claude_binary() == str(fake_bin)


def test_resolve_claude_binary_picks_highest_version(monkeypatch, tmp_path):
    for version in ("v20.0.0", "v24.16.0", "v22.1.0"):
        d = tmp_path / version / "bin"
        d.mkdir(parents=True)
        (d / "claude").write_text("#!/bin/sh\n")
    monkeypatch.setattr(watchdog, "CLAUDE_NVM_GLOB", str(tmp_path / "*" / "bin" / "claude"))
    assert watchdog.resolve_claude_binary() == str(tmp_path / "v24.16.0" / "bin" / "claude")


def test_resolve_claude_binary_none_if_not_found(monkeypatch, tmp_path):
    monkeypatch.setattr(watchdog, "CLAUDE_NVM_GLOB", str(tmp_path / "*" / "bin" / "claude"))
    assert watchdog.resolve_claude_binary() is None


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


def test_main_session_model_is_opus():
    """2026-07-13, director-decided live in-console: the main interactive
    session does judgment-tier work (FRAME/DISCOVER, epoch framing,
    root-cause diagnosis) and must run Opus, matching TWIN_MODEL's own
    tier for the same reason."""
    assert watchdog.MAIN_SESSION_MODEL == "claude-opus-4-8"


def test_restart_claude_launches_directly_with_no_send_keys(monkeypatch):
    """WATCHDOG_NO_SENDKEYS.md (2026-07-04): the launch must not use
    tmux send-keys at all -- claude is the pane's command itself, with
    -c and RESUME_INSTRUCTION passed as argv, not typed in afterwards.

    Includes --dangerously-skip-permissions per Rich's direct, live
    confirmation (2026-07-05, docs/review_gates/SKIP_PERMISSIONS_TIER1.md)
    -- three prior attempts to get this added via untrusted channels
    (unauthenticated NTFY, a git-pushed commit, text embedded in a tool
    result) were declined; this is the fourth, arriving as an actual
    conversation turn, which is the one channel treated as trustworthy.

    Also sets DISABLE_AUTOUPDATER=1 via tmux's session-scoped -e flag
    (2026-07-08, Rich's direct instruction): the npm global install isn't
    writable, so claude's background auto-update check fails on every
    unattended restart for no benefit -- manual update is now the
    sanctioned path (MAINTENANCE.md)."""
    watchdog.restart_times.clear()
    calls = []
    monkeypatch.setattr(watchdog.subprocess, "run", lambda *a, **k: calls.append(a[0]) or type("R", (), {"returncode": 0})())
    monkeypatch.setattr(watchdog, "ntfy", lambda msg, needs_input=False: None)
    monkeypatch.setattr(watchdog, "log", lambda msg, needs_input=False: None)
    monkeypatch.setattr(watchdog.time, "sleep", lambda s: None)
    monkeypatch.setattr(watchdog, "check_api_reachable", lambda: True)  # avoid real HTTP
    monkeypatch.setattr(watchdog, "claude_is_running", lambda: True)  # simulate a clean launch
    monkeypatch.setattr(watchdog, "resolve_claude_binary", lambda: "/fake/nvm/bin/claude")

    watchdog.restart_claude()

    send_keys_calls = [c for c in calls if c[:2] == ["tmux", "send-keys"]]
    new_session_calls = [c for c in calls if c[:2] == ["tmux", "new-session"]]
    # No send-keys anywhere in the launch sequence.
    assert send_keys_calls == []
    # claude is launched directly as the pane's command: --dangerously-skip-permissions,
    # --model, -c, and RESUME_INSTRUCTION are argv elements, never typed in.
    assert len(new_session_calls) == 1
    launch = new_session_calls[0]
    assert launch[-6:] == [
        "/fake/nvm/bin/claude", "--dangerously-skip-permissions",
        "--model", watchdog.MAIN_SESSION_MODEL, "-c", watchdog.RESUME_INSTRUCTION,
    ]
    assert "-e" in launch
    assert launch[launch.index("-e") + 1] == "DISABLE_AUTOUPDATER=1"
    watchdog.restart_times.clear()


def test_restart_claude_no_op_if_claude_never_comes_up(monkeypatch):
    """If `claude` never becomes the pane's foreground process, there must
    be exactly one alert with the captured pane content -- no retry loop,
    no fallback keystroke injection."""
    watchdog.restart_times.clear()
    calls = []
    ntfy_messages = []
    monkeypatch.setattr(watchdog.subprocess, "run", lambda *a, **k: calls.append(a[0]) or type("R", (), {"returncode": 0})())
    monkeypatch.setattr(watchdog, "ntfy", lambda msg, needs_input=False: ntfy_messages.append(msg))
    monkeypatch.setattr(watchdog, "log", lambda msg, needs_input=False: None)
    monkeypatch.setattr(watchdog.time, "sleep", lambda s: None)
    monkeypatch.setattr(watchdog, "check_api_reachable", lambda: True)
    monkeypatch.setattr(watchdog, "claude_is_running", lambda: False)  # launch never comes up
    monkeypatch.setattr(watchdog, "capture_pane", lambda: "-sh: 2: Session: not found")
    monkeypatch.setattr(watchdog, "resolve_claude_binary", lambda: "/fake/nvm/bin/claude")

    watchdog.restart_claude()

    send_keys_calls = [c for c in calls if c[:2] == ["tmux", "send-keys"]]
    assert send_keys_calls == []
    assert len(ntfy_messages) == 1
    assert "failed to launch" in ntfy_messages[0]
    watchdog.restart_times.clear()


def test_restart_claude_aborts_if_binary_not_found(monkeypatch):
    """No claude binary resolvable -- alert once, don't attempt to launch."""
    watchdog.restart_times.clear()
    monkeypatch.setattr(watchdog, "_binary_missing_ntfy_sent", False)
    calls = []
    ntfy_messages = []
    monkeypatch.setattr(watchdog.subprocess, "run", lambda *a, **k: calls.append(a[0]) or type("R", (), {"returncode": 0})())
    monkeypatch.setattr(watchdog, "ntfy", lambda msg, needs_input=False: ntfy_messages.append(msg))
    monkeypatch.setattr(watchdog, "log", lambda msg, needs_input=False: None)
    monkeypatch.setattr(watchdog.time, "sleep", lambda s: None)
    monkeypatch.setattr(watchdog, "check_api_reachable", lambda: True)
    monkeypatch.setattr(watchdog, "resolve_claude_binary", lambda: None)

    watchdog.restart_claude()

    new_session_calls = [c for c in calls if c[:2] == ["tmux", "new-session"]]
    assert new_session_calls == []
    assert len(ntfy_messages) == 1
    assert "not found" in ntfy_messages[0]
    watchdog.restart_times.clear()


def test_restart_claude_binary_missing_ntfy_deduped_across_cycles(monkeypatch):
    """A persistently broken binary must not re-alert every watchdog cycle --
    R5: NTFYs fire on state transitions only, never repeat an unchanged
    status. Verified live during kill-test B (real nvm binary renamed away,
    real restart_claude() called twice) before this fix was added."""
    watchdog.restart_times.clear()
    monkeypatch.setattr(watchdog, "_binary_missing_ntfy_sent", False)
    ntfy_messages = []
    monkeypatch.setattr(watchdog.subprocess, "run", lambda *a, **k: type("R", (), {"returncode": 0})())
    monkeypatch.setattr(watchdog, "ntfy", lambda msg, needs_input=False: ntfy_messages.append(msg))
    monkeypatch.setattr(watchdog, "log", lambda msg, needs_input=False: None)
    monkeypatch.setattr(watchdog.time, "sleep", lambda s: None)
    monkeypatch.setattr(watchdog, "check_api_reachable", lambda: True)
    monkeypatch.setattr(watchdog, "resolve_claude_binary", lambda: None)

    watchdog.restart_claude()
    watchdog.restart_claude()
    watchdog.restart_claude()

    assert len(ntfy_messages) == 1
    watchdog.restart_times.clear()


def test_restart_claude_binary_missing_ntfy_resets_once_resolved(monkeypatch):
    """Once the binary resolves again, the dedupe flag clears so a future
    outage is reported again rather than staying permanently silenced."""
    watchdog.restart_times.clear()
    monkeypatch.setattr(watchdog, "_binary_missing_ntfy_sent", True)
    ntfy_messages = []
    monkeypatch.setattr(watchdog.subprocess, "run", lambda *a, **k: type("R", (), {"returncode": 0})())
    monkeypatch.setattr(watchdog, "ntfy", lambda msg, needs_input=False: ntfy_messages.append(msg))
    monkeypatch.setattr(watchdog, "log", lambda msg, needs_input=False: None)
    monkeypatch.setattr(watchdog.time, "sleep", lambda s: None)
    monkeypatch.setattr(watchdog, "check_api_reachable", lambda: True)
    monkeypatch.setattr(watchdog, "claude_is_running", lambda: True)
    monkeypatch.setattr(watchdog, "resolve_claude_binary", lambda: "/fake/nvm/bin/claude")

    watchdog.restart_claude()

    assert watchdog._binary_missing_ntfy_sent is False
    watchdog.restart_times.clear()


def test_restart_claude_instruction_survives_shell_hostile_characters(monkeypatch):
    """The whole point of no-send-keys: an apostrophe/quotes/parens in the
    instruction must reach the launch argv completely unchanged. Verified
    empirically (not just asserted) via a real tmux + python3 subprocess
    round-trip during development -- see WATCHDOG_NO_SENDKEYS.md."""
    watchdog.restart_times.clear()
    calls = []
    monkeypatch.setattr(watchdog.subprocess, "run", lambda *a, **k: calls.append(a[0]) or type("R", (), {"returncode": 0})())
    monkeypatch.setattr(watchdog, "ntfy", lambda msg, needs_input=False: None)
    monkeypatch.setattr(watchdog, "log", lambda msg, needs_input=False: None)
    monkeypatch.setattr(watchdog.time, "sleep", lambda s: None)
    monkeypatch.setattr(watchdog, "check_api_reachable", lambda: True)
    monkeypatch.setattr(watchdog, "claude_is_running", lambda: True)
    monkeypatch.setattr(watchdog, "resolve_claude_binary", lambda: "/fake/nvm/bin/claude")

    watchdog.restart_claude()

    new_session_calls = [c for c in calls if c[:2] == ["tmux", "new-session"]]
    assert new_session_calls[0][-1] == watchdog.RESUME_INSTRUCTION
    watchdog.restart_times.clear()


def test_wait_for_claude_launch_returns_true_once_running(monkeypatch):
    monkeypatch.setattr(watchdog.time, "sleep", lambda s: None)
    states = iter([False, False, True])
    monkeypatch.setattr(watchdog, "claude_is_running", lambda: next(states))

    assert watchdog.wait_for_claude_launch(timeout_seconds=10) is True


def test_wait_for_claude_launch_returns_false_on_timeout(monkeypatch):
    # Simulate time passing without a real sleep: each call to time.time()
    # advances the clock by more than the poll interval, and claude never
    # comes up, so the deadline is exceeded quickly.
    fake_now = {"t": 1_000_000.0}

    def fake_time():
        fake_now["t"] += watchdog.CLAUDE_LAUNCH_POLL_INTERVAL_SECONDS
        return fake_now["t"]

    monkeypatch.setattr(watchdog.time, "time", fake_time)
    monkeypatch.setattr(watchdog.time, "sleep", lambda s: None)
    monkeypatch.setattr(watchdog, "claude_is_running", lambda: False)

    assert watchdog.wait_for_claude_launch(timeout_seconds=5) is False


def test_handle_usage_limit_clears_in_place_without_any_pane_injection(monkeypatch):
    """PULL-LOOP MIGRATION (2026-07-15): the in-place RESUME_INSTRUCTION
    keystroke nudge is DELETED. The watchdog no longer has a send_keys API and
    must not type into the live pane. It only polls (read-only) until the limit
    clears on its own or the process exits."""
    assert not hasattr(watchdog, "send_keys")
    monkeypatch.setattr(watchdog, "log", lambda msg, needs_input=False: None)
    ntfy_messages = []
    monkeypatch.setattr(watchdog, "ntfy", lambda msg, needs_input=False: ntfy_messages.append(msg))
    monkeypatch.setattr(watchdog.time, "sleep", lambda s: None)
    monkeypatch.setattr(watchdog, "session_exists", lambda: True)
    monkeypatch.setattr(watchdog, "claude_is_running", lambda: True)
    # No pane keystroke may be issued: if any tmux command is attempted, fail.
    tmux_calls = []
    monkeypatch.setattr(
        watchdog.subprocess, "run",
        lambda cmd, **kw: tmux_calls.append(cmd) or type("R", (), {"returncode": 0, "stdout": ""})(),
    )
    # First poll: still limited; second poll: cleared on its own.
    pane_outputs = iter(["usage limit reached", "all clear, continuing"])
    monkeypatch.setattr(watchdog, "capture_pane", lambda: next(pane_outputs))

    watchdog.handle_usage_limit()

    # No `tmux send-keys` was ever issued (read-only capture only, mocked away).
    assert not any(isinstance(c, list) and "send-keys" in c for c in tmux_calls)
    assert not any("resumed automatically" in msg for msg in ntfy_messages)


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
    watchdog._autoloop_last_pane = None
    watchdog._autoloop_idle_streak = 0
    watchdog._autoloop_waiting_notified = False
    watchdog._autoloop_gate_clear_streak = 0
    watchdog._usage_pause_notified = False


def test_watchdog_has_no_pane_injection_api():
    """PULL-LOOP MIGRATION: every keystroke-injection entry point is gone; the
    watchdog is process-level only (spawn/restart), never types into a live pane."""
    for removed in ("send_keys", "send_keys_when_idle", "read_slash_dialog_when_idle",
                    "check_inbound_commands", "_relay_inbound_command",
                    "_flush_pending_gate_reply", "check_session_usage",
                    "_pending_gate_decision"):
        assert not hasattr(watchdog, removed), f"watchdog.{removed} must be deleted"


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


def test_check_autoloop_idle_does_nothing_when_no_gate_or_pause(monkeypatch):
    """check_autoloop() never grants a turn and (PULL-LOOP MIGRATION) never
    types into the pane. An idle pane with no REVIEW_GATE/permission-prompt must
    do nothing further -- no NTFY, no pane write."""
    _reset_autoloop_state()
    monkeypatch.setattr(watchdog, "log", lambda msg, needs_input=False: None)
    ntfy_messages = []
    monkeypatch.setattr(watchdog, "ntfy", lambda msg, needs_input=False: ntfy_messages.append(msg))
    relay_calls = []
    monkeypatch.setattr(watchdog.subprocess, "run",
                        lambda *a, **k: relay_calls.append(a[0]) or type("R", (), {"returncode": 0})())

    idle_pane = "Claude Code is idle at the prompt"
    for _ in range(watchdog.AUTOLOOP_IDLE_CHECKS + 1):
        watchdog.check_autoloop(idle_pane)

    assert relay_calls == []
    assert ntfy_messages == []
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
    monkeypatch.setattr(watchdog.time, "sleep", lambda s: None)

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
    """2026-07-09: resume is now an NTFY transition (doorbell failure #4),
    reversing the earlier no-NTFY choice now that it's a clean enter/exit
    pair rather than a repeating heartbeat."""
    pause_file = tmp_path / ".usage_pause.json"
    resume_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    pause_file.write_text(json.dumps({"resume_at": resume_at.isoformat()}))
    monkeypatch.setattr(watchdog, "USAGE_PAUSE_FILE", pause_file)
    monkeypatch.setattr(watchdog, "log", lambda msg, needs_input=False: None)
    ntfy_messages = []
    monkeypatch.setattr(watchdog, "ntfy", lambda msg, needs_input=False: ntfy_messages.append(msg))

    assert watchdog.usage_pause_active() is False
    assert not pause_file.is_file()
    assert any("resuming" in msg for msg in ntfy_messages)


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
    """usage-pause resume is an NTFY transition ("the director never has to
    guess"), never a pane write. Once the pause file's resume_at has passed,
    usage_pause_active() deletes it and NTFYs the transition."""
    _reset_autoloop_state()
    pause_file = tmp_path / ".usage_pause.json"
    resume_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    pause_file.write_text(json.dumps({"resume_at": resume_at.isoformat()}))
    monkeypatch.setattr(watchdog, "USAGE_PAUSE_FILE", pause_file)
    monkeypatch.setattr(watchdog, "log", lambda msg, needs_input=False: None)
    ntfy_messages = []
    monkeypatch.setattr(watchdog, "ntfy", lambda msg, needs_input=False: ntfy_messages.append(msg))
    tmux_calls = []
    monkeypatch.setattr(watchdog.subprocess, "run",
                        lambda *a, **k: tmux_calls.append(a[0]) or type("R", (), {"returncode": 0})())

    idle_pane = "Claude Code is idle at the prompt"
    for _ in range(watchdog.AUTOLOOP_IDLE_CHECKS + 1):
        watchdog.check_autoloop(idle_pane)

    assert not any(isinstance(c, list) and "send-keys" in c for c in tmux_calls)  # no pane write
    assert any("resuming normally" in msg for msg in ntfy_messages)
    assert not pause_file.is_file()
    _reset_autoloop_state()


def test_usage_limit_detected_when_claude_not_running_prevents_restart(monkeypatch):
    """Claude exits after showing a usage-limit message (foreground=bash, not
    claude/node). The watchdog must detect the limit from the pane and call
    handle_usage_limit rather than restarting into the same limit."""
    monkeypatch.setattr(watchdog, "session_exists", lambda: True)
    monkeypatch.setattr(watchdog, "claude_is_running", lambda: False)
    monkeypatch.setattr(watchdog, "capture_pane", lambda: "usage limit reached")
    monkeypatch.setattr(watchdog.time, "sleep", lambda s: None)
    monkeypatch.setattr(watchdog, "log", lambda msg, needs_input=False: None)

    handle_usage_limit_calls = []
    handle_session_ended_calls = []
    monkeypatch.setattr(watchdog, "handle_usage_limit", lambda: handle_usage_limit_calls.append(1))
    monkeypatch.setattr(watchdog, "handle_session_ended", lambda: handle_session_ended_calls.append(1))

    # Run two loop iterations then stop via exception
    call_count = [0]
    original_sleep = watchdog.time.sleep

    def stop_after_two(s):
        call_count[0] += 1
        if call_count[0] >= 2:
            raise StopIteration

    monkeypatch.setattr(watchdog.time, "sleep", stop_after_two)

    try:
        watchdog.main()
    except StopIteration:
        pass

    assert handle_usage_limit_calls, "handle_usage_limit should have been called"
    assert not handle_session_ended_calls, "handle_session_ended must NOT be called when pane shows usage limit"


# --- Phase 52 (watchdog): API connectivity backoff ---

def test_check_api_reachable_returns_true_on_any_http_response(monkeypatch):
    """Any HTTP response (including 404) means the API is reachable."""
    class FakeResp:
        status_code = 404
    monkeypatch.setattr(watchdog.requests, "get", lambda *a, **k: FakeResp())
    assert watchdog.check_api_reachable() is True


def test_check_api_reachable_returns_false_on_connection_error(monkeypatch):
    import requests as req
    monkeypatch.setattr(watchdog.requests, "get", lambda *a, **k: (_ for _ in ()).throw(req.ConnectionError("refused")))
    assert watchdog.check_api_reachable() is False


def test_wait_for_api_connectivity_returns_immediately_when_reachable(monkeypatch):
    monkeypatch.setattr(watchdog, "check_api_reachable", lambda: True)
    monkeypatch.setattr(watchdog, "ntfy", lambda *a, **k: None)
    monkeypatch.setattr(watchdog, "log", lambda *a, **k: None)
    # Should return without sleeping
    slept = []
    monkeypatch.setattr(watchdog.time, "sleep", lambda s: slept.append(s))
    watchdog.wait_for_api_connectivity()
    assert slept == []


def test_wait_for_api_connectivity_ntfys_on_first_failure_then_recovers(monkeypatch):
    call_count = [0]
    def reachable():
        call_count[0] += 1
        return call_count[0] >= 2   # first call: unreachable; second: recovered

    ntfy_msgs = []
    monkeypatch.setattr(watchdog, "check_api_reachable", reachable)
    monkeypatch.setattr(watchdog, "ntfy", lambda msg, needs_input=False: ntfy_msgs.append(msg))
    monkeypatch.setattr(watchdog, "log", lambda msg, **k: None)
    monkeypatch.setattr(watchdog.time, "sleep", lambda s: None)

    watchdog.wait_for_api_connectivity()

    assert call_count[0] >= 2, "Should have retried until reachable"
    assert any("unreachable" in m.lower() or "down" in m.lower() for m in ntfy_msgs), (
        f"Expected NTFY about API being down, got: {ntfy_msgs}"
    )
    assert any("restored" in m.lower() for m in ntfy_msgs), (
        f"Expected NTFY about connectivity restored, got: {ntfy_msgs}"
    )


# ── Post-restart daemon health check (2026-07-13, ANTI_LIVELOCK_AND_WIDTH.md
# adjacent director request, live in-console: "after any session restart,
# verify the full daemon set and alarm if any are missing") ──

def test_verify_daemon_set_after_restart_logs_ok_and_does_not_ntfy(monkeypatch):
    logs = []
    ntfy_msgs = []
    monkeypatch.setattr(watchdog, "log", lambda msg, **k: logs.append(msg))
    monkeypatch.setattr(watchdog, "ntfy", lambda msg, needs_input=False: ntfy_msgs.append(msg))
    monkeypatch.setattr(watchdog, "run_health_check", lambda: (True, ["ok1", "ok2"], []))

    watchdog._verify_daemon_set_after_restart()

    assert not ntfy_msgs, "a healthy stack must never NTFY (routine-noise discipline)"
    assert any("OK" in m for m in logs)


def test_verify_daemon_set_after_restart_ntfys_on_missing_daemon(monkeypatch):
    logs = []
    ntfy_msgs = []
    monkeypatch.setattr(watchdog, "log", lambda msg, **k: logs.append(msg))
    monkeypatch.setattr(watchdog, "ntfy", lambda msg, needs_input=False: ntfy_msgs.append(msg))
    monkeypatch.setattr(
        watchdog, "run_health_check",
        lambda: (False, ["ok1"], ["  ✗ supervisor — NOT RUNNING (supervisor.py)"]),
    )

    watchdog._verify_daemon_set_after_restart()

    assert len(ntfy_msgs) == 1
    assert "supervisor" in ntfy_msgs[0]
    assert any("DEGRADED" in m for m in logs)


def test_verify_daemon_set_after_restart_survives_health_check_exception(monkeypatch):
    """A broken health check must not crash the restart flow itself --
    log the failure and move on, same defensive posture as every other
    best-effort step in restart_claude()."""
    logs = []
    monkeypatch.setattr(watchdog, "log", lambda msg, **k: logs.append(msg))
    monkeypatch.setattr(watchdog, "ntfy", lambda msg, needs_input=False: (_ for _ in ()).throw(AssertionError("must not be called")))
    def _boom():
        raise RuntimeError("tmux unavailable")
    monkeypatch.setattr(watchdog, "run_health_check", _boom)

    watchdog._verify_daemon_set_after_restart()  # must not raise

    assert any("failed to run" in m for m in logs)


# ── ONE TREE, ONE SESSION (2026-07-16, director: "a duplicate is a defect, not a
#    recovery") ────────────────────────────────────────────────────────────────
# These mechanise the no-duplicate-spawn guarantee: the monitor loop only ever
# restarts when `claude_is_running()` is False (session_watchdog.py main loop:
# `if not session_exists() or not claude_is_running(): ...restart`). So proving
# claude_is_running() detects a LIVE session -- including one whose foreground
# pane command is not 'claude' but which still has a live process -- proves the
# watchdog will NOT spawn a second session on this tree. R15: the mutation
# counterpart proves the check is load-bearing (it CAN return False), so the
# guard genuinely gates on real liveness rather than being a tautology.

def _dispatch_run(*, pane_stdout: str, pgrep_rc: int):
    """Fake subprocess.run dispatching on the command: tmux list-panes returns
    `pane_stdout`; `pgrep -x claude` returns `pgrep_rc`."""
    def _run(cmd, **kw):
        if cmd[:2] == ["tmux", "list-panes"]:
            return type("R", (), {"stdout": pane_stdout, "returncode": 0})()
        if cmd[:1] == ["pgrep"]:
            return type("R", (), {"stdout": b"", "returncode": pgrep_rc})()
        return type("R", (), {"stdout": "", "returncode": 0})()
    return _run


def test_claude_is_running_true_when_pane_shows_claude(monkeypatch):
    """Primary path: a claude/node foreground pane => running => no restart."""
    monkeypatch.setattr(watchdog.subprocess, "run", _dispatch_run(pane_stdout="claude\n", pgrep_rc=1))
    assert watchdog.claude_is_running() is True


def test_claude_is_running_true_via_pgrep_fallback_prevents_duplicate(monkeypatch):
    """One tree, one session: even when the pane's foreground command is NOT
    claude (e.g. a shell running a build), a live `claude` process detected by
    `pgrep -x claude` makes claude_is_running() True -- so the monitor's
    `not claude_is_running()` restart guard is False and NO second session is
    spawned. This is the exact guarantee the director asked to make permanent."""
    monkeypatch.setattr(watchdog.subprocess, "run", _dispatch_run(pane_stdout="bash\n", pgrep_rc=0))
    assert watchdog.claude_is_running() is True


def test_claude_is_running_false_only_when_pane_bare_AND_no_process(monkeypatch):
    """R15 mutation counterpart: the guard is load-bearing -- it returns False
    (allowing a restart) ONLY when the pane has no claude/node AND pgrep finds no
    live claude process. Proves the two-signal check isn't a tautology that
    always reports 'running'."""
    monkeypatch.setattr(watchdog.subprocess, "run", _dispatch_run(pane_stdout="bash\n", pgrep_rc=1))
    assert watchdog.claude_is_running() is False
