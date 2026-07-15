"""Shared tmux pane helpers -- READ-ONLY as of the pull-loop migration.

MIGRATION (2026-07-15, STAGING_PULL_LOOP_RESCOPE.md + DIRECTOR_ANSWERS_C7.md,
director GO'd step 2): the keystroke-injection path has been DELETED. This
module used to be "the ONE place every background daemon injects text into a
live tmux session" (send_keys / send_keys_when_idle / read_slash_dialog_when_idle
+ the idle-gate + relay-lock scaffolding). That entire pane-WRITE capability is
gone. The interactive pane is now the DIRECTOR'S CONSOLE ONLY -- nothing robotic
ever types into it again. Instructions reach the session by STAGING plus the
pull-loop Stop hook (.claude/hooks/pull_next_work.py), which draws work at every
turn boundary and NEVER types into the pane (it only emits JSON on stdout).

Why the whole thing was removed, not patched (five deaths -- the rescope's own
words): keystroke injection into a live TUI was structurally unreliable (partial
sends, mid-turn corruption, the [Pasted text #NNN] pile, the /usage storm,
copy-mode swallowing) and it is banned. A guard (tests/controls/
test_no_pane_injection.py) greps the whole background/ + .claude/ tree and FAILS
if any `tmux send-keys` / pane keystroke write is ever re-introduced here or
anywhere else -- mutation-proven to catch a re-introduction.

What SURVIVES here is strictly READ-ONLY observation of the pane -- capture-pane
and display-message calls that read state and never type: `capture_pane`,
`is_session_idle`, `pane_in_copy_mode`. These are used for liveness/idle
detection by the supervisor's escalation checks and the watchdog's restart
decisions; reading the pane is not injection.
"""
from __future__ import annotations

import os
import re
import subprocess

DEFAULT_SESSION_NAME = "claude"


# A busy pane shows a spinner glyph + gerund-form status line ending in a
# live elapsed-time counter (e.g. "✽ Running the Epoch-2 desk-work evidence
# pass… (51s)") -- the "(<N>s)"/"(<N>m <N>s)" suffix is what's genuinely
# unique to an in-progress task; a bare ellipsis is NOT, because Claude
# Code's own persistent completed/pending task-list panel (bullets ◼ ◻ ✔ ✘)
# stays visible in the pane indefinitely and its lines are truncated with
# "…" too. Anchor on a word boundary after the "s" so any trailing content
# inside/after the parens (e.g. "(19m 43s · ↓ 64.5k tokens)") is tolerated,
# while still requiring a real "(<N>s)"/"(<N>m <N>s)" live timer.
_BUSY_SPINNER_LINE = re.compile(r"^\s*\S\s+\S.*\(\d+(?:m\s*\d+\s*)?s\b", re.MULTILINE)

# Claude Code's footer shows an "esc to interrupt"-style hint only while a turn
# is actively running; an idle prompt's footer does not mention "esc" in this
# context. Scoped to the actual footer line (identified by the stable "bypass
# permissions" marker), not a bare substring search across the whole pane.
_BUSY_FOOTER_HINT = "esc"
_FOOTER_LINE_MARKER = "bypass permissions"


def _configured_session_name() -> str:
    return os.environ.get("SE_TMUX_SESSION_NAME", DEFAULT_SESSION_NAME)


def pane_in_copy_mode(session: str) -> bool:
    """True if `session`'s active pane is in tmux copy-mode/view-mode
    (`#{pane_in_mode}`) -- i.e. showing frozen scrollback rather than the live
    tail. Read-only (`tmux display-message`), never types anything. Fails safe:
    any capture error returns False (never claims copy-mode when we can't
    confirm it)."""
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


def _is_busy_content(content: str) -> bool:
    """True if the pane content shows ANY busy indicator. Covers the spinner
    + elapsed-time line, an "esc to interrupt" hint (wrap-safe), the
    "Waiting for background agent…"/"Levitating…" states, and a legacy "esc"
    hint on the bypass-permissions footer line."""
    if _BUSY_SPINNER_LINE.search(content):
        return True
    flat = _flatten(content).lower()
    if "esctointerrupt" in flat:
        return True
    if "waitingforbackground" in flat or "levitating" in flat:
        return True
    footer_line = next(
        (line for line in content.splitlines() if _FOOTER_LINE_MARKER in line), ""
    )
    if _BUSY_FOOTER_HINT in footer_line.lower():
        return True
    return False


def is_session_idle(session: str) -> bool:
    """Best-effort idle detection: True only if the pane shows no busy
    indicator. Fails safe -- any capture error or a busy pattern returns False
    (never assume idle when we can't actually confirm it). Read-only."""
    content = capture_pane(session)
    if not content or _is_busy_content(content):
        return False
    return True
