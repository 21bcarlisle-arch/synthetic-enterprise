"""Every hook command in `.claude/settings.json` names its script independently of the cwd.

A relative hook path (`python3 .claude/hooks/x.py`) works until a session `cd`s anywhere else, then
every PreToolUse hook fails and every tool call is refused: a total deadlock of the session.
That happened on 2026-08-08 (docs/staging/done/WORKER_FINDING_RELATIVE_HOOK_PATHS_WEDGE_SESSION_
2026-08-08.md). The instance was fixed by hand and nothing stopped the next hand-edited hook from
re-arming it. This file is that guard.
"""
from __future__ import annotations

import json
import re
import shlex
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SETTINGS = ROOT / ".claude" / "settings.json"
ANCHOR = re.compile(r"^\$\{CLAUDE_PROJECT_DIR(:-[^}]*)?\}")


def _commands(settings: dict) -> list[str]:
    return [h["command"] for matchers in (settings.get("hooks") or {}).values()
            for m in matchers for h in m.get("hooks") or [] if h.get("command")]


def unanchored(command: str) -> list[str]:
    """The path tokens in a hook command that a cwd change would break, or that name no file."""
    bad = []
    for token in shlex.split(command, posix=False):
        if "/" not in token or token.startswith("-"):
            continue
        if ANCHOR.match(token):
            if not (ROOT / ANCHOR.sub("", token).lstrip("/")).exists():
                bad.append(token + " (no such file under the project)")
        elif not token.startswith("/"):
            bad.append(token)
    return bad


def test_every_hook_command_resolves_from_any_cwd():
    commands = _commands(json.loads(SETTINGS.read_text()))
    assert commands, "settings.json carries no hook commands: the guard below would pass vacuously"
    broken = {c: unanchored(c) for c in commands if unanchored(c)}
    assert not broken, "hook commands that break when the cwd moves: {}".format(broken)


def test_the_check_refuses_a_relative_or_missing_hook():
    """The guard can fail: a relative path and an anchored path to a missing file are both named,
    and the shipped shape is not."""
    assert unanchored("python3 .claude/hooks/block_sudo.py") == [".claude/hooks/block_sudo.py"]
    assert unanchored("python3 ${CLAUDE_PROJECT_DIR}/.claude/hooks/no_such_hook.py")
    assert not unanchored("python3 ${CLAUDE_PROJECT_DIR:-/home/x}/.claude/hooks/block_sudo.py")
