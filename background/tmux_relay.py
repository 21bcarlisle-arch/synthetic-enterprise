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
"""
from __future__ import annotations

import os
import subprocess


def send_keys(session: str, *keys: str) -> bool:
    """Send `keys` (the trailing tmux send-keys arguments, e.g. a text
    string plus "Enter", or a bare "Escape") to tmux session `session`.

    Returns True if the subprocess call was attempted and returned exit
    code 0, False otherwise (including when suppressed under test, or on
    any exception -- callers treat this as best-effort, matching how every
    existing call site already handled a dead/missing tmux session).
    """
    if os.environ.get("PYTEST_CURRENT_TEST") is not None:
        return False
    try:
        result = subprocess.run(
            ["tmux", "send-keys", "-t", session, *keys],
            capture_output=True, timeout=5,
        )
        return result.returncode == 0
    except Exception:
        return False
