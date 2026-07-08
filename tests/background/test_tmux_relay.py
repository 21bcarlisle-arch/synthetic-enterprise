"""Tests for background/tmux_relay.py -- the shared, test-isolation-guarded
tmux send-keys relay (2026-07-08 incident: see the module's own docstring)."""
import os

from background import tmux_relay


def test_send_keys_is_a_noop_under_pytest(monkeypatch):
    """The core guarantee: since this whole test suite runs under pytest,
    PYTEST_CURRENT_TEST is genuinely set right now (not simulated) -- this
    call must be a real, unmocked no-op, proving the guard works exactly as
    it will for every other test in this suite, forever, even ones that
    never think to mock this module at all."""
    assert os.environ.get("PYTEST_CURRENT_TEST") is not None
    result = tmux_relay.send_keys("claude", "this must never actually be typed", "Enter")
    assert result is False


def test_send_keys_calls_real_subprocess_when_guard_lifted(monkeypatch):
    """With the pytest env var explicitly cleared (simulating a real,
    non-test process), the function does attempt the real tmux call."""
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    calls = []
    monkeypatch.setattr(
        tmux_relay.subprocess, "run",
        lambda cmd, **kw: calls.append(cmd) or type("R", (), {"returncode": 0})(),
    )

    result = tmux_relay.send_keys("claude", "hello", "Enter")

    assert result is True
    assert calls == [["tmux", "send-keys", "-t", "claude", "hello", "Enter"]]


def test_send_keys_passes_through_arbitrary_trailing_keys(monkeypatch):
    """Some callers send a bare key name (e.g. "Escape") with no text +
    Enter pair -- the helper must forward whatever trailing args it's given
    unchanged, matching every existing call site's shape."""
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    calls = []
    monkeypatch.setattr(
        tmux_relay.subprocess, "run",
        lambda cmd, **kw: calls.append(cmd) or type("R", (), {"returncode": 0})(),
    )

    tmux_relay.send_keys("claude", "Escape")

    assert calls == [["tmux", "send-keys", "-t", "claude", "Escape"]]


def test_send_keys_returns_false_on_nonzero_exit(monkeypatch):
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.setattr(
        tmux_relay.subprocess, "run",
        lambda cmd, **kw: type("R", (), {"returncode": 1})(),
    )

    assert tmux_relay.send_keys("claude", "x", "Enter") is False


def test_send_keys_swallows_exceptions(monkeypatch):
    """A dead/missing tmux session (or any subprocess failure) must never
    raise -- every existing call site relied on this best-effort contract."""
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)

    def _raise(*a, **k):
        raise Exception("tmux: no such session")
    monkeypatch.setattr(tmux_relay.subprocess, "run", _raise)

    assert tmux_relay.send_keys("claude", "x", "Enter") is False


# ── Session isolation guard (docs/staging/TURN_CONTINUATION_AND_PHASE3_GO.md, 2026-07-08) ──

def test_default_session_name_matches_every_existing_caller():
    """Every current daemon hardcodes SESSION_NAME = "claude" -- the default
    target must match, or this guard would silently break live behaviour."""
    assert tmux_relay.DEFAULT_SESSION_NAME == "claude"


def test_send_keys_unaffected_by_guard_when_unconfigured(monkeypatch):
    """No SE_TMUX_SESSION_NAME set: the guard must be fully transparent for
    the default session name (zero behaviour change for existing daemons)."""
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.delenv("SE_TMUX_SESSION_NAME", raising=False)
    monkeypatch.setattr(
        tmux_relay.subprocess, "run",
        lambda cmd, **kw: type("R", (), {"returncode": 0})(),
    )
    assert tmux_relay.send_keys("claude", "x", "Enter") is True


def test_send_keys_refuses_mismatched_session_when_configured(monkeypatch):
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.setenv("SE_TMUX_SESSION_NAME", "claude")
    calls = []
    monkeypatch.setattr(
        tmux_relay.subprocess, "run",
        lambda cmd, **kw: calls.append(cmd) or type("R", (), {"returncode": 0})(),
    )
    result = tmux_relay.send_keys("some-other-session", "x", "Enter")
    assert result is False
    assert calls == []  # refused before ever shelling out


def test_send_keys_allows_matching_configured_session(monkeypatch):
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.setenv("SE_TMUX_SESSION_NAME", "custom-session")
    calls = []
    monkeypatch.setattr(
        tmux_relay.subprocess, "run",
        lambda cmd, **kw: calls.append(cmd) or type("R", (), {"returncode": 0})(),
    )
    result = tmux_relay.send_keys("custom-session", "x", "Enter")
    assert result is True
    assert calls == [["tmux", "send-keys", "-t", "custom-session", "x", "Enter"]]


# ── Idle-gated verified send (2026-07-08 root-cause fix: a wake message can
# land partially in a busy pane's input box and never submit) ──

IDLE_PANE = (
    "some prior scrollback output\n"
    "────────────────────────────────────────────────────────\n"
    "❯ \n"
    "────────────────────────────────────────────────────────\n"
    "  ⏵⏵ bypass permissions on (shift+tab to cycle)\n"
)

BUSY_PANE = (
    "* Wiring evidence and closing phase-close checklist…\n"
    "  ⎿  ◼ Evidence: Sim tab meter-read delay histo…\n"
    "     ✔ Housekeeping: move 3 staged docs to done/\n"
    "────────────────────────────────────────────────────────\n"
    "❯ \n"
    "────────────────────────────────────────────────────────\n"
    "  ⏵⏵ bypass permissions on (shift+tab to cycle) · esc …\n"
)


def _mock_run_returning(stdout: str, returncode: int = 0):
    return lambda cmd, **kw: type("R", (), {"returncode": returncode, "stdout": stdout})()


def test_capture_pane_noop_under_pytest():
    assert tmux_relay.capture_pane("claude") == ""


def test_capture_pane_returns_stdout(monkeypatch):
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.setattr(tmux_relay.subprocess, "run", _mock_run_returning(IDLE_PANE))
    assert tmux_relay.capture_pane("claude") == IDLE_PANE


def test_capture_pane_empty_on_nonzero_exit(monkeypatch):
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.setattr(tmux_relay.subprocess, "run", _mock_run_returning("x", returncode=1))
    assert tmux_relay.capture_pane("claude") == ""


def test_capture_pane_empty_on_exception(monkeypatch):
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)

    def _raise(*a, **k):
        raise Exception("no such session")
    monkeypatch.setattr(tmux_relay.subprocess, "run", _raise)
    assert tmux_relay.capture_pane("claude") == ""


def test_is_session_idle_true_for_idle_pane(monkeypatch):
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.setattr(tmux_relay.subprocess, "run", _mock_run_returning(IDLE_PANE))
    assert tmux_relay.is_session_idle("claude") is True


def test_is_session_idle_false_for_busy_pane(monkeypatch):
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.setattr(tmux_relay.subprocess, "run", _mock_run_returning(BUSY_PANE))
    assert tmux_relay.is_session_idle("claude") is False


def test_is_session_idle_fails_safe_on_capture_error(monkeypatch):
    """Can't confirm idle => must never assume idle."""
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.setattr(tmux_relay.subprocess, "run", _mock_run_returning("", returncode=1))
    assert tmux_relay.is_session_idle("claude") is False


def test_send_keys_when_idle_noop_under_pytest():
    assert tmux_relay.send_keys_when_idle("claude", "hello|123|abc", "abc") is False


def test_send_keys_when_idle_refuses_when_busy(monkeypatch):
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    calls = []
    monkeypatch.setattr(
        tmux_relay.subprocess, "run",
        lambda cmd, **kw: calls.append(cmd) or type("R", (), {"returncode": 0, "stdout": BUSY_PANE})(),
    )
    result = tmux_relay.send_keys_when_idle("claude", "hello|123|abc123", "abc123")
    assert result is False
    # Only the idle-check capture-pane call happened -- send-keys itself
    # must never fire into a busy session.
    assert all(c[1] != "send-keys" for c in calls)


def test_send_keys_when_idle_success_when_idle_and_consumed(monkeypatch):
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.setattr(tmux_relay.time, "sleep", lambda *_: None)
    # First capture (idle check) -> idle pane. send-keys -> success.
    # Second capture (post-send verify) -> idle pane again (marker gone,
    # i.e. successfully consumed/submitted).
    call_log = []

    def _run(cmd, **kw):
        call_log.append(cmd)
        if cmd[1] == "capture-pane":
            return type("R", (), {"returncode": 0, "stdout": IDLE_PANE})()
        return type("R", (), {"returncode": 0})()

    monkeypatch.setattr(tmux_relay.subprocess, "run", _run)
    result = tmux_relay.send_keys_when_idle("claude", "hello|123|abc123", "abc123")
    assert result is True
    assert any(c[1] == "send-keys" for c in call_log)


def test_send_keys_when_idle_fails_when_marker_still_stuck(monkeypatch):
    """The exact failure mode this fix targets: idle-check passes, send
    'succeeds' (subprocess exit 0), but the text never actually submitted
    -- still visible in the post-send capture. Must return False, not
    silently report success."""
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.setattr(tmux_relay.time, "sleep", lambda *_: None)
    stuck_pane = IDLE_PANE.replace("❯ \n", "❯ hello|123|abc123\n")

    def _run(cmd, **kw):
        if cmd[1] == "capture-pane":
            return type("R", (), {"returncode": 0, "stdout": stuck_pane})()
        return type("R", (), {"returncode": 0})()

    monkeypatch.setattr(tmux_relay.subprocess, "run", _run)
    result = tmux_relay.send_keys_when_idle("claude", "hello|123|abc123", "abc123")
    assert result is False


def test_send_keys_when_idle_marker_survives_line_wrap(monkeypatch):
    """The observed live bug: a long single-line message word-wraps across
    multiple pane lines. The marker check must flatten whitespace so a
    wrapped-but-present marker is still correctly detected as stuck."""
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.setattr(tmux_relay.time, "sleep", lambda *_: None)
    wrapped_stuck_pane = (
        "❯ this message has been classified as requiring\n"
        "  immediate attention.]|1783534244|1650f1781210d13f20\n"
        "  009e6ac12d054b1a589c18da912f43b5afa14510911cd7\n"
    )

    def _run(cmd, **kw):
        if cmd[1] == "capture-pane":
            return type("R", (), {"returncode": 0, "stdout": wrapped_stuck_pane})()
        return type("R", (), {"returncode": 0})()

    monkeypatch.setattr(tmux_relay.subprocess, "run", _run)
    result = tmux_relay.send_keys_when_idle(
        "claude", "some message|1783534244|1650f1781210d13f20009e6ac12d054b1a589c18da912f43b5afa14510911cd7",
        "1650f1781210d13f20009e6ac12d054b1a589c18da912f43b5afa14510911cd7",
    )
    assert result is False


def test_send_keys_when_idle_returns_false_when_send_keys_fails(monkeypatch):
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)

    def _run(cmd, **kw):
        if cmd[1] == "capture-pane":
            return type("R", (), {"returncode": 0, "stdout": IDLE_PANE})()
        return type("R", (), {"returncode": 1})()  # send-keys itself fails

    monkeypatch.setattr(tmux_relay.subprocess, "run", _run)
    result = tmux_relay.send_keys_when_idle("claude", "hello|123|abc123", "abc123")
    assert result is False
