"""OPS1_tmux_target_qualification (G-L1-adjacent): pane-scoped tmux targets must be
FULLY QUALIFIED (session form `claude:`), never a bare `-t claude`.

The 2026-07-17 false-latch incident: a bare `tmux capture-pane -t claude` run from inside
the director's `work` console resolved to a WINDOW named 'claude' (window-name match) instead
of the SESSION named 'claude' (the worker seat) — so the watchdog captured the director's own
screen and raised a false 'latch' alarm. Session-scoped commands (has-session/kill-session/
new-session) are unambiguous with a bare name; only PANE-scoped commands (capture-pane,
list-panes, display-message, send-keys, select-pane/window, pipe-pane) can mis-resolve, and
those must carry the session-qualifier `:` (or an `@window`/`.pane` id).

This is the MAKE_IT_STICK mechanism: a bare pane-scoped target reappearing anywhere in
background/*.py fails this test (the same shape as the raw-send-keys grep-guard)."""
from __future__ import annotations

import re
from pathlib import Path

BACKGROUND = Path(__file__).resolve().parents[2] / "background"

# Commands whose `-t` target is PANE-scoped and therefore window/session-ambiguous with a
# bare name. (has-session / kill-session / new-session are session-scoped — bare is safe.)
PANE_SCOPED = (
    "capture-pane", "list-panes", "display-message",
    "send-keys", "select-pane", "select-window", "pipe-pane",
)

# One tmux argv list literal: ["tmux", ....] up to its first closing bracket.
_TMUX_CALL = re.compile(r'\[\s*"tmux"\s*,(.*?)\]', re.DOTALL)
_T_TARGET = re.compile(r'"-t"\s*,\s*([^,\]]+)')


def _bare_pane_targets(text: str) -> list[str]:
    offenders = []
    for m in _TMUX_CALL.finditer(text):
        call = m.group(1)
        if not any(f'"{cmd}"' in call for cmd in PANE_SCOPED):
            continue  # session-scoped command — a bare `-t name` is unambiguous
        tm = _T_TARGET.search(call)
        if not tm:
            continue  # e.g. `list-panes -a` (no -t target at all)
        target = tm.group(1).strip()
        # Qualified forms carry a session colon `X:` or a window/pane id (`@`, `.`).
        if ":" in target or "@" in target:
            continue
        offenders.append(target)
    return offenders


def test_no_bare_pane_scoped_tmux_target_in_background():
    problems = []
    for py in sorted(BACKGROUND.glob("*.py")):
        for target in _bare_pane_targets(py.read_text()):
            problems.append(f"{py.name}: pane-scoped tmux `-t {target}` is bare — "
                            f"must be session-qualified (e.g. f'{{{target}}}:')")
    assert not problems, (
        "bare (window/session-ambiguous) pane-scoped tmux targets found:\n  "
        + "\n  ".join(problems)
    )


def test_guard_would_fire_on_a_bare_pane_target():
    """R15 mutation: the guard must actually catch a bare pane-scoped target (a guard that
    can't fire is the disease). Bare capture-pane => caught; session-qualified => clean;
    a bare has-session => NOT caught (session-scoped, legitimately bare)."""
    assert _bare_pane_targets('subprocess.run(["tmux", "capture-pane", "-t", SESSION_NAME, "-p"])')
    assert not _bare_pane_targets('subprocess.run(["tmux", "capture-pane", "-t", f"{SESSION_NAME}:", "-p"])')
    assert not _bare_pane_targets('subprocess.run(["tmux", "has-session", "-t", SESSION_NAME])')
    assert not _bare_pane_targets('subprocess.run(["tmux", "list-panes", "-a", "-F", "x"])')

# ── Publish-gate scope (R10, 2026-07-18): DAEMON-LIFECYCLE test module ──────────
# Validates pipeline MACHINERY (process/session lifecycle, scheduling, notify transport,
# reconciliation), never a published business surface -- so it must never wedge the live
# publish. The gate runs `-m 'not operational'`. See tests/conftest.py for the marker.
import pytest  # noqa: E402,F811
pytestmark = pytest.mark.operational
