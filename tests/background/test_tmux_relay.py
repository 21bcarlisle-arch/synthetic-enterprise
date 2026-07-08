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
