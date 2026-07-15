"""Tests for background/tmux_relay.py.

PULL-LOOP MIGRATION (2026-07-15, STAGING_PULL_LOOP_RESCOPE.md): the pane-WRITE
path (send_keys / send_keys_when_idle / read_slash_dialog_when_idle / exit_copy_
mode / ensure_live_tail + the idle-gate/relay-lock scaffolding) has been DELETED
-- keystroke injection is banned. What remains is strictly READ-ONLY pane
observation (capture_pane / is_session_idle / pane_in_copy_mode). These tests
cover the surviving read-only surface and ASSERT the write functions are gone.
"""
from background import tmux_relay


def _mock_run_returning(stdout: str, returncode: int = 0):
    return lambda cmd, **kw: type("R", (), {"returncode": returncode, "stdout": stdout})()


# ── The migration is structural: the write path no longer exists ──

def test_pane_write_primitives_are_deleted():
    """No keystroke-injection callable may exist on this module anymore -- the
    guard in tests/controls/test_no_pane_injection.py backstops the whole tree,
    this pins the specific removed API so a re-add is caught here too."""
    for removed in (
        "send_keys", "send_keys_when_idle", "read_slash_dialog_when_idle",
        "exit_copy_mode", "ensure_live_tail", "relay_lock", "_safe_to_inject",
        "_pane_has_pending_input", "_log_injection",
    ):
        assert not hasattr(tmux_relay, removed), (
            f"tmux_relay.{removed} still exists -- pane-write path must be deleted"
        )


def test_module_source_has_no_send_keys_command():
    """Belt-and-braces: the module source performs no `tmux send-keys`."""
    import inspect
    src = inspect.getsource(tmux_relay)
    # Only the read-only tmux subcommands may appear as command tokens.
    assert '"send-keys"' not in src and "'send-keys'" not in src


# ── Surviving read-only surface: capture_pane ──

def test_capture_pane_noop_under_pytest():
    assert tmux_relay.capture_pane("claude") == ""


def test_capture_pane_returns_stdout(monkeypatch):
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.setattr(tmux_relay.subprocess, "run", _mock_run_returning("hello pane\n"))
    assert tmux_relay.capture_pane("claude") == "hello pane\n"


def test_capture_pane_empty_on_nonzero_exit(monkeypatch):
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.setattr(tmux_relay.subprocess, "run", _mock_run_returning("x", returncode=1))
    assert tmux_relay.capture_pane("claude") == ""


def test_capture_pane_empty_on_exception(monkeypatch):
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)

    def _raise(*a, **k):
        raise Exception("no session")
    monkeypatch.setattr(tmux_relay.subprocess, "run", _raise)
    assert tmux_relay.capture_pane("claude") == ""


# ── Surviving read-only surface: is_session_idle ──

IDLE_PANE = (
    "some prior scrollback output\n"
    "────────────────────────────────────────────────────────\n"
    "❯ \n"
    "────────────────────────────────────────────────────────\n"
    "  ⏵⏵ bypass permissions on (shift+tab to cycle)\n"
)

BUSY_PANE = (
    "* Wiring evidence and closing phase-close checklist… (12s)\n"
    "  ⎿  ◼ Evidence: Sim tab meter-read delay histo…\n"
    "     ✔ Housekeeping: move 3 staged docs to done/\n"
    "────────────────────────────────────────────────────────\n"
    "❯ \n"
    "────────────────────────────────────────────────────────\n"
    "  ⏵⏵ bypass permissions on (shift+tab to cycle) · esc …\n"
)

IDLE_PANE_WITH_COMPLETED_TASK_LIST = (
    "  ⎿  ◼ EPOCH2_EVIDENCE_PASS + INTENT_RIDER: des…\n"
    "     ◻ DIRECTOR_COMMENTS_BOX.md: per-page feedb…\n"
    "     ✔ Fix R4: supervisor/tmux_relay copy-mode …\n"
    "      … +3 completed\n"
    "  ✘ Auto-update failed: no write permission to npm pre…\n"
    "────────────────────────────────────────────────────────\n"
    "❯ \n"
    "────────────────────────────────────────────────────────\n"
    "  ⏵⏵ bypass permissions on (shift+tab to cycle)\n"
)


def test_is_session_idle_true_for_idle_pane(monkeypatch):
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.setattr(tmux_relay.subprocess, "run", _mock_run_returning(IDLE_PANE))
    assert tmux_relay.is_session_idle("claude") is True


def test_is_session_idle_false_for_busy_pane(monkeypatch):
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.setattr(tmux_relay.subprocess, "run", _mock_run_returning(BUSY_PANE))
    assert tmux_relay.is_session_idle("claude") is False


def test_is_session_idle_true_for_completed_task_list_no_live_spinner(monkeypatch):
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.setattr(
        tmux_relay.subprocess, "run",
        _mock_run_returning(IDLE_PANE_WITH_COMPLETED_TASK_LIST),
    )
    assert tmux_relay.is_session_idle("claude") is True


def test_busy_spinner_requires_elapsed_time_suffix_not_just_ellipsis(monkeypatch):
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    static_checklist_only = (
        "  ⎿  ◼ Some completed task description that…\n"
        "────────────────────────────────────────────────────────\n"
        "❯ \n"
        "────────────────────────────────────────────────────────\n"
        "  ⏵⏵ bypass permissions on (shift+tab to cycle)\n"
    )
    monkeypatch.setattr(tmux_relay.subprocess, "run", _mock_run_returning(static_checklist_only))
    assert tmux_relay.is_session_idle("claude") is True


def test_is_session_idle_fails_safe_on_capture_error(monkeypatch):
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.setattr(tmux_relay.subprocess, "run", _mock_run_returning("", returncode=1))
    assert tmux_relay.is_session_idle("claude") is False


def _busy_pane_with(footer_or_status: str) -> str:
    return (
        "  some output line\n"
        "────────────────────────────────────────────────────────\n"
        "❯ \n"
        "────────────────────────────────────────────────────────\n"
        f"  {footer_or_status}\n"
    )


def test_is_session_idle_false_for_spinner_with_trailing_token_counter(monkeypatch):
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    pane = (
        "  ● doing the thing\n"
        "✽ Metamorphosing… (19m 43s · ↓ 64.5k tokens)\n"
        "────────────────────────────────────────────────────────\n"
        "❯ \n"
        "────────────────────────────────────────────────────────\n"
        "  ⏵⏵ bypass permissions on (shift+tab to cycle)\n"
    )
    monkeypatch.setattr(tmux_relay.subprocess, "run", _mock_run_returning(pane))
    assert tmux_relay.is_session_idle("claude") is False


def test_is_session_idle_false_when_waiting_for_background_agent(monkeypatch):
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    pane = _busy_pane_with("Waiting for background agent… (esc to interrupt)")
    monkeypatch.setattr(tmux_relay.subprocess, "run", _mock_run_returning(pane))
    assert tmux_relay.is_session_idle("claude") is False


def test_is_session_idle_false_on_esc_to_interrupt_off_footer(monkeypatch):
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    pane = _busy_pane_with("Levitating… (12s · esc to interrupt)")
    monkeypatch.setattr(tmux_relay.subprocess, "run", _mock_run_returning(pane))
    assert tmux_relay.is_session_idle("claude") is False


# ── Surviving read-only surface: pane_in_copy_mode (display-message, read-only) ──

def test_pane_in_copy_mode_noop_under_pytest():
    assert tmux_relay.pane_in_copy_mode("claude") is False


def test_pane_in_copy_mode_true_when_flag_set(monkeypatch):
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.setattr(tmux_relay.subprocess, "run", _mock_run_returning("1\n"))
    assert tmux_relay.pane_in_copy_mode("claude") is True


def test_pane_in_copy_mode_false_when_flag_clear(monkeypatch):
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.setattr(tmux_relay.subprocess, "run", _mock_run_returning("0\n"))
    assert tmux_relay.pane_in_copy_mode("claude") is False


def test_pane_in_copy_mode_fails_safe_on_error(monkeypatch):
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)

    def _raise(*a, **k):
        raise Exception("no such session")
    monkeypatch.setattr(tmux_relay.subprocess, "run", _raise)
    assert tmux_relay.pane_in_copy_mode("claude") is False


def test_default_session_name_matches_configured():
    assert tmux_relay.DEFAULT_SESSION_NAME == "claude"
    assert tmux_relay._configured_session_name() == "claude"
