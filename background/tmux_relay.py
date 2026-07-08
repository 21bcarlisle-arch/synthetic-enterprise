"""Shared tmux send-keys relay -- the ONE place every background daemon
injects text into a live tmux session (session_watchdog.py, dispatcher.py,
staging_watcher.py all call this rather than invoking `tmux send-keys`
directly).

Built with a structural test-isolation guard: refuses to run under pytest,
regardless of whether any individual test remembers to mock it.

Incident (2026-07-08): several existing tests in test_staging_watcher.py
mocked `ntfy` but not the new tmux-relay call `check_once()` gained that
same day; every full-suite pytest run after that point sent real text into
the live 'claude' session using those tests' own fixture filenames
(TASK_NEW.md, A.md, B.md, NEW.md, maintenance_due_202610.md) -- initially
misdiagnosed, in the same session, as an external prompt-injection attack
before the director corrected it with direct evidence (the ntfy.sh topic
history itself was clean). Root cause was purely local test isolation, not
any external channel. See docs/retrospectives/
2026-07-08-test-suite-tmux-leak.md for the full evidence chain.

Rather than relying on every test remembering to mock this call (the thing
that just failed), the guard lives here, once: PYTEST_CURRENT_TEST is set
by pytest for the duration of every test it runs (stable, documented pytest
behaviour, not a private API) -- if set, this function is a silent no-op.
No test, existing or future, can accidentally send real keystrokes into a
live tmux session through this path, even if it forgets to mock anything.

Session isolation guard (docs/staging/TURN_CONTINUATION_AND_PHASE3_GO.md,
2026-07-08): every existing call site already hardcodes SESSION_NAME =
"claude", so this guard changes no live behaviour by default -- it exists
so an injection can never silently land in the wrong tmux session if that
constant ever drifts inconsistent across daemons, or a future multi-session
setup introduces a real one. The target is configurable via
SE_TMUX_SESSION_NAME (unset = "claude", matching every current caller);
`send_keys` refuses (no-ops) if `session` doesn't match it.

Idle-gated verified send (2026-07-08, same-day follow-up, director-direct
root-cause fix): a live incident showed a signed wake message landing
PARTIALLY in the target session's input box and never submitting -- a
corrupted fragment sat there, unsubmitted, across many subsequent turns.
A live probe (sending the identical signed text to a throwaway `cat`
session) proved `send_keys` itself transmits the full text correctly,
byte for byte -- the corruption happens in the receiving Claude Code TUI's
own input handling when a long keystroke burst arrives while it is busy
(mid-turn), not in this module. Since that's an external CLI's behaviour,
not something this codebase can patch directly, the fix is defensive on
this side: `send_keys_when_idle()` (a) refuses to send at all unless the
target pane currently shows no busy indicator (spinner + gerund status
line, or an "esc to interrupt"-style footer hint), and (b) after sending,
re-captures the pane and confirms the just-sent text is no longer sitting
there unconsumed -- if it is, the send is treated as failed (not
recorded as delivered) so the caller retries next cycle instead of
silently believing a stuck injection succeeded.
"""
from __future__ import annotations

import os
import re
import subprocess
import time

DEFAULT_SESSION_NAME = "claude"

# A busy pane shows a spinner glyph + gerund-form status line ending in an
# ellipsis (e.g. "* Wiring evidence and closing phase-close checklist…") --
# this is the harness's own in-progress-task indicator, not something any
# idle prompt renders.
_BUSY_SPINNER_LINE = re.compile(r"^\s*\S\s+\S.*[.…]{1,3}\s*$", re.MULTILINE)

# Claude Code's footer shows an "esc to interrupt"-style hint (sometimes
# truncated to "esc …" in a narrow pane) only while a turn is actively
# running; an idle prompt's footer does not mention "esc" in this context.
_BUSY_FOOTER_HINT = "esc"


def _configured_session_name() -> str:
    return os.environ.get("SE_TMUX_SESSION_NAME", DEFAULT_SESSION_NAME)


def send_keys(session: str, *keys: str) -> bool:
    """Send `keys` (the trailing tmux send-keys arguments, e.g. a text
    string plus "Enter", or a bare "Escape") to tmux session `session`.

    Returns True if the subprocess call was attempted and returned exit
    code 0, False otherwise (including when suppressed under test, when
    `session` doesn't match the configured target, or on any exception --
    callers treat this as best-effort, matching how every existing call
    site already handled a dead/missing tmux session).

    Low-level primitive -- fires unconditionally (no idle check, no
    delivery verification). Wake-injection call sites should use
    `send_keys_when_idle()` instead; this is kept for direct/diagnostic
    use (and is what `send_keys_when_idle()` itself calls internally).
    """
    if os.environ.get("PYTEST_CURRENT_TEST") is not None:
        return False
    if session != _configured_session_name():
        return False
    try:
        result = subprocess.run(
            ["tmux", "send-keys", "-t", session, *keys],
            capture_output=True, timeout=5,
        )
        return result.returncode == 0
    except Exception:
        return False


def capture_pane(session: str, lines: int = 30) -> str:
    """Return the last `lines` of `session`'s pane content, or "" on any
    failure (missing session, tmux unavailable, suppressed under test).
    Read-only -- never types anything."""
    if os.environ.get("PYTEST_CURRENT_TEST") is not None:
        return ""
    try:
        result = subprocess.run(
            ["tmux", "capture-pane", "-t", session, "-p", "-S", f"-{lines}"],
            capture_output=True, text=True, timeout=5,
        )
        return result.stdout if result.returncode == 0 else ""
    except Exception:
        return ""


def _flatten(text: str) -> str:
    """Strip all whitespace so a substring check survives the pane's own
    line-wrapping (a long single logical line gets word-wrapped across
    multiple visual lines at the pane's fixed width)."""
    return re.sub(r"\s+", "", text)


def is_session_idle(session: str) -> bool:
    """Best-effort idle detection: True only if the pane shows neither a
    busy spinner/status line nor an "esc"-hint footer. Fails safe -- any
    capture error, or genuine ambiguity, returns False (never assume idle
    when we can't actually confirm it)."""
    content = capture_pane(session)
    if not content:
        return False
    if _BUSY_SPINNER_LINE.search(content):
        return False
    if _BUSY_FOOTER_HINT in content.lower():
        return False
    return True


def send_keys_when_idle(
    session: str, text: str, verify_marker: str, post_send_wait: float = 1.5
) -> bool:
    """Only inject `text` + Enter if `session` is currently idle at its
    prompt; after sending, verify the text was actually consumed rather
    than trusting a fire-and-forget send.

    `verify_marker` should be a short, distinctive substring of `text`
    (e.g. the trailing HMAC hex digest of a signed wake message) --
    checked against the flattened (whitespace-stripped) post-send pane
    capture, so word-wrapping can't hide a still-stuck fragment.

    Returns True only if: the pane was idle, the send subprocess
    succeeded, AND the marker is no longer visible afterward (proof of
    consumption). Any other outcome returns False -- the caller must
    treat this as "not delivered, retry next cycle," never as delivered.
    """
    if os.environ.get("PYTEST_CURRENT_TEST") is not None:
        return False
    if not is_session_idle(session):
        return False
    if not send_keys(session, text, "Enter"):
        return False
    time.sleep(post_send_wait)
    after = capture_pane(session)
    if not after:
        return False  # can't confirm consumption -- treat as failed, retry
    if _flatten(verify_marker) in _flatten(after):
        return False  # still sitting unconsumed in the pane
    return True
