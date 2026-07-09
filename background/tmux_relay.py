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

Cross-daemon relay lock (2026-07-08, third wake-doorbell failure,
docs/retrospectives/2026-07-08-wake-doorbell-third-strike.md): the module
docstring above claimed session_watchdog.py already went through this one
relay -- false. Its autoloop-continuation nudge and REVIEW_GATE reply relay
were left as direct, unguarded `subprocess.run(["tmux", "send-keys", ...])`
calls at the 2026-07-08 tmux-leak incident fix (commit cc2d741c), flagged
there as a deliberate follow-up that was never done. Two staged P1 docs sat
unactioned for 2+ hours despite staging_watcher confirming "delivered" wakes
for both, because session_watchdog's own unrelated, unguarded autoloop send
was independently racing the same pane on its own cruder idle heuristic
(pane-text-unchanged-for-N-polls, not the busy-spinner/footer check below),
with no coordination between the two daemons. `relay_lock()` makes the
idle-check+send+verify sequence in `send_keys_when_idle()` an atomic
cross-process critical section (fcntl flock, mirrors background/tree_lock.py
for git writers) so no two daemons can interleave sends into the same pane,
and session_watchdog.py now goes through `send_keys_when_idle()` like every
other caller -- closing the gap rather than adding a second bespoke guard.
"""
from __future__ import annotations

import fcntl
import os
import re
import subprocess
import time
from contextlib import contextmanager
from pathlib import Path

DEFAULT_SESSION_NAME = "claude"

_RELAY_LOCK_FILE = Path(__file__).resolve().parent.parent / "docs" / "observability" / ".tmux_relay.lock"
# Short on purpose: a legitimate holder's critical section is a single
# idle-check + send + ~1.5s verify sleep + re-capture, so a few seconds is
# generous headroom. Daemons poll every 30-60s anyway, so a lock-contention
# failure just retries next cycle rather than blocking a poll loop for long.
_RELAY_LOCK_TIMEOUT_SECONDS = 5.0


class RelayLockTimeout(Exception):
    """Raised when the cross-daemon relay lock could not be acquired in time."""


@contextmanager
def relay_lock(timeout: float = _RELAY_LOCK_TIMEOUT_SECONDS):
    """Hold an exclusive cross-process lock for the duration of the `with`
    block, serializing every daemon's idle-check+send+verify sequence onto
    the live tmux session so two daemons can never race into the same pane.
    Mirrors background/tree_lock.py's git-write serialization. Raises
    RelayLockTimeout on timeout (a stuck holder should surface, not hang
    every other daemon's poll loop indefinitely) -- send_keys_when_idle()
    catches this and treats it as an ordinary failed-send/retry-next-cycle
    outcome."""
    if os.environ.get("PYTEST_CURRENT_TEST") is not None:
        yield
        return
    _RELAY_LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    fh = open(_RELAY_LOCK_FILE, "w")
    deadline = time.monotonic() + timeout
    try:
        while True:
            try:
                fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise RelayLockTimeout(
                        f"Could not acquire tmux relay lock ({_RELAY_LOCK_FILE}) within {timeout}s"
                    )
                time.sleep(0.2)
        yield
    finally:
        fcntl.flock(fh, fcntl.LOCK_UN)
        fh.close()

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


def pane_in_copy_mode(session: str) -> bool:
    """True if `session`'s active pane is in tmux copy-mode/view-mode
    (`#{pane_in_mode}`) -- i.e. showing frozen scrollback (the CLI's own
    "Jump to bottom" hint is one visible symptom) rather than the live
    tail, and swallowing keystrokes as copy-mode navigation instead of
    forwarding them to the running program. Fails safe: any capture error
    returns False (never claims copy-mode when we can't confirm it)."""
    if os.environ.get("PYTEST_CURRENT_TEST") is not None:
        return False
    try:
        result = subprocess.run(
            ["tmux", "display-message", "-p", "-t", session, "-F", "#{pane_in_mode}"],
            capture_output=True, text=True, timeout=5,
        )
        return result.returncode == 0 and result.stdout.strip() == "1"
    except Exception:
        return False


def exit_copy_mode(session: str) -> bool:
    """Send tmux's copy-mode 'cancel' command (bound to q/Escape in the
    copy-mode key table) to snap `session`'s pane back to the live tail.
    Returns True only if the command was issued successfully -- not proof
    copy-mode actually cleared; callers that need certainty should re-check
    `pane_in_copy_mode()`."""
    if os.environ.get("PYTEST_CURRENT_TEST") is not None:
        return False
    try:
        result = subprocess.run(
            ["tmux", "send-keys", "-X", "-t", session, "cancel"],
            capture_output=True, timeout=5,
        )
        return result.returncode == 0
    except Exception:
        return False


def ensure_live_tail(session: str) -> None:
    """Best-effort: if `session`'s pane is frozen in copy-mode/scrollback,
    clear it so subsequent idle-checks and sends see/reach the real live
    pane. Root cause (2026-07-09, R4): a pane left in copy-mode all morning
    showed stale scrollback ("Jump to bottom") to every daemon -- capture_pane
    read frozen content instead of the live tail, and injected keystrokes
    were consumed by tmux as copy-mode navigation rather than reaching the
    running CLI, so grants silently vanished with no error anywhere. No-op
    (and safe) if the pane is not in copy-mode, or under pytest."""
    if os.environ.get("PYTEST_CURRENT_TEST") is not None:
        return
    if pane_in_copy_mode(session):
        exit_copy_mode(session)
        time.sleep(0.2)


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
    session: str, text: str, verify_marker: str,
    post_send_wait: float = 1.5, post_type_wait: float = 0.3,
) -> bool:
    """Only inject `text` + Enter if `session` is currently idle at its
    prompt; verify both that the text actually reached the input line and
    that it was subsequently consumed, rather than trusting a
    fire-and-forget send.

    `verify_marker` should be a short, distinctive substring of `text`
    (e.g. the trailing HMAC hex digest of a signed wake message) --
    checked against the flattened (whitespace-stripped) pane capture, so
    word-wrapping can't hide a still-stuck fragment.

    Sequence: clear any frozen copy-mode/scrollback first (R4, 2026-07-09
    -- see `ensure_live_tail()`), confirm idle, send `text` WITHOUT Enter
    and confirm the marker actually landed in the pane (proof the
    keystrokes reached the input line rather than being silently swallowed
    -- e.g. by tmux copy-mode interpreting them as navigation, the exact
    failure mode that motivated this split), only then send Enter, and
    finally confirm the marker is no longer visible (proof of consumption).

    Returns True only if every one of those checks passes. Any other
    outcome returns False -- the caller must treat this as "not delivered,
    retry next cycle," never as delivered.

    The whole sequence runs inside `relay_lock()` so a second daemon
    calling this concurrently can't interleave its own send (see module
    docstring, "Cross-daemon relay lock").
    """
    if os.environ.get("PYTEST_CURRENT_TEST") is not None:
        return False
    try:
        with relay_lock(timeout=_RELAY_LOCK_TIMEOUT_SECONDS):
            ensure_live_tail(session)
            if not is_session_idle(session):
                return False
            if not send_keys(session, text):
                return False
            time.sleep(post_type_wait)
            landed = capture_pane(session)
            if not landed or _flatten(verify_marker) not in _flatten(landed):
                # Text never reached the input line -- e.g. swallowed by
                # copy-mode navigation, or the pane wasn't actually focused
                # on an input prompt. Not delivered; do not send Enter into
                # whatever state the pane is actually in.
                return False
            if not send_keys(session, "Enter"):
                return False
            time.sleep(post_send_wait)
            after = capture_pane(session)
            if not after:
                return False  # can't confirm consumption -- treat as failed, retry
            if _flatten(verify_marker) in _flatten(after):
                return False  # still sitting unconsumed in the pane
            return True
    except RelayLockTimeout:
        return False  # another daemon is mid-send -- retry next cycle
