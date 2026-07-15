"""GREP-GUARD: no code may perform a tmux `send-keys` / pane keystroke write.

PULL-LOOP MIGRATION (2026-07-15, STAGING_PULL_LOOP_RESCOPE.md +
DIRECTOR_ANSWERS_C7.md, director GO'd step 2). The interactive pane is the
DIRECTOR'S CONSOLE ONLY -- nothing robotic ever types into it again. The
keystroke-injection path (tmux_relay.send_keys / send_keys_when_idle /
read_slash_dialog_when_idle + every daemon caller) has been DELETED; the
pull-loop Stop hook (.claude/hooks/pull_next_work.py) is the transport now
(it only emits JSON, never types).

This control extends the existing ban to ALL writers: it scans the WHOLE
background/ + .claude/ tree and FAILS if ANY .py code performs a tmux
send-keys / pane keystroke write. Per R15 (controls must be able to FAIL) it
is MUTATION-PROVEN below: re-introducing a send-keys call in a scratch fixture
makes the guard fire, and removing it makes the guard pass again. A guard never
proven to catch a re-introduction is theatre.

Detection is AST-based on STRING CONSTANTS, so prose in comments/docstrings that
merely DISCUSSES send-keys (this file, the migration comments, the retro notes)
is ignored -- only an actual keystroke-write command is flagged:
  * an argv element equal to "send-keys"  (subprocess.run(["tmux","send-keys",...]))
  * a short shell string containing both "tmux" and "send-keys"
    (subprocess.run("tmux send-keys ...", shell=True) / os.system(...))
  * a short shell string invoking xdotool/ydotool type/key (other keystroke
    injectors).
A file that cannot be AST-parsed is NOT skipped (that would fail-open, a killer
pattern): it falls back to a raw non-comment-line scan for a quoted send-keys
token.
"""
import ast
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCAN_ROOTS = [REPO_ROOT / "background", REPO_ROOT / ".claude"]
# The guard file itself is excluded (it names the token in prose/fixtures).
_SELF = Path(__file__).resolve()

_SHELL_TMUX = re.compile(r"tmux.*send-keys", re.IGNORECASE)
_INJECTOR = re.compile(r"\b[xy]dotool\b.*\b(type|key)\b", re.IGNORECASE)
_QUOTED_SENDKEYS = re.compile(r"""['"]send-keys['"]""")


def _string_is_keystroke_write(value: str) -> bool:
    """True if a Python string LITERAL is (part of) a tmux keystroke-write
    command or another keystroke injector. Precise on the argv form (exact
    "send-keys" token) and the shell form (short string), so multi-line prose
    docstrings that merely mention send-keys never match."""
    if not isinstance(value, str):
        return False
    if value.strip() == "send-keys":  # argv element of ["tmux","send-keys",...]
        return True
    if len(value) <= 200:  # a command string, not a docstring
        low = value.lower()
        if "send-keys" in low and "tmux" in low:
            return True
        if _INJECTOR.search(value):
            return True
    return False


def _raw_line_scan(text: str):
    """Fallback for an unparseable file (never fail-open). Flags a quoted
    'send-keys'/"send-keys" token or a `tmux ... send-keys` shell command on a
    non-comment code line."""
    hits = []
    for i, line in enumerate(text.splitlines(), start=1):
        stripped = line.lstrip()
        if stripped.startswith("#"):
            continue
        if _QUOTED_SENDKEYS.search(line) or (_SHELL_TMUX.search(line) and ('"' in line or "'" in line)):
            hits.append((i, line.strip()[:120]))
    return hits


def scan_file_for_pane_writes(path: Path):
    """Return a list of (lineno, snippet) keystroke-write findings in `path`."""
    text = path.read_text(encoding="utf-8", errors="replace")
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return _raw_line_scan(text)  # do NOT skip -- fail closed
    findings = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and _string_is_keystroke_write(node.value):
            findings.append((getattr(node, "lineno", -1), repr(node.value)[:120]))
    return findings


def scan_tree_for_pane_writes(roots=SCAN_ROOTS):
    """Walk every *.py under `roots` and collect keystroke-write findings.
    Returns {relative_path: [(lineno, snippet), ...]} for offending files."""
    offenders = {}
    for root in roots:
        if not root.exists():
            continue
        for py in sorted(root.rglob("*.py")):
            if py.resolve() == _SELF:
                continue
            hits = scan_file_for_pane_writes(py)
            if hits:
                try:
                    key = str(py.relative_to(REPO_ROOT))
                except ValueError:
                    key = str(py)
                offenders[key] = hits
    return offenders


# ─────────────────────────────── the live guard ───────────────────────────────

def test_no_pane_keystroke_writes_anywhere_in_background_or_claude_tree():
    """THE control: zero tmux send-keys / pane keystroke writes in the whole
    background/ + .claude/ tree. If this fails, someone re-introduced pane
    injection -- the pane is the director's console only."""
    offenders = scan_tree_for_pane_writes()
    assert offenders == {}, (
        "pane keystroke-write(s) re-introduced -- the interactive pane is the "
        "director's console ONLY (STAGING_PULL_LOOP_RESCOPE.md):\n"
        + "\n".join(f"  {f}: {hits}" for f, hits in offenders.items())
    )


# ───────────────────── R15 MUTATION PROOF (mandatory) ──────────────────────────
# A guard never proven to catch a re-introduction is theatre. Re-introduce a
# send-keys line in a SCRATCH fixture, prove the guard FIRES; remove it, prove it
# PASSES. This proves the guard is load-bearing, not tautological/fail-open.

_ARGV_INJECTION = (
    'import subprocess\n'
    'def relay(session, text):\n'
    '    subprocess.run(["tmux", "send-keys", "-t", session, text, "Enter"])\n'
)
_SHELL_INJECTION = (
    'import os\n'
    'def relay(session, text):\n'
    '    os.system(f"tmux send-keys -t {session} {text} Enter")\n'
)
_CLEAN = (
    'import subprocess\n'
    'def read(session):\n'
    '    return subprocess.run(["tmux", "capture-pane", "-t", session, "-p"])\n'
)
# Prose that merely DISCUSSES send-keys must NOT trip the guard (no false
# positive -- otherwise the migration comments would fail the whole tree).
_PROSE_ONLY = (
    '"""This module used to call tmux send-keys to inject keystrokes into the\n'
    'live pane; that path is deleted. It now only reads the pane. The words\n'
    'send-keys and "tmux send-keys" appear here in prose only, never as a command.\n'
    '"""\n'
    '# The old raw `tmux send-keys` call and send_keys_when_idle are gone.\n'
    'X = 1\n'
)


@pytest.mark.parametrize("payload", [_ARGV_INJECTION, _SHELL_INJECTION])
def test_guard_FIRES_on_reintroduced_send_keys(tmp_path, payload):
    fixture = tmp_path / "reintroduced.py"
    fixture.write_text(payload, encoding="utf-8")
    hits = scan_file_for_pane_writes(fixture)
    assert hits, f"MUTATION ESCAPED the guard -- send-keys not caught in:\n{payload}"


def test_guard_FIRES_via_tree_scan_when_fixture_added_under_root(tmp_path):
    """End-to-end: a scanned root containing a send-keys file makes the
    tree-scan report it; deleting the line makes the same scan clean."""
    root = tmp_path / "background"
    root.mkdir()
    bad = root / "rogue_daemon.py"
    bad.write_text(_ARGV_INJECTION, encoding="utf-8")
    offenders = scan_tree_for_pane_writes([root])
    assert offenders, "guard did NOT fire on a re-introduced send-keys under a scanned root"
    # Remove the offending line -> guard passes (proves it's the line, not the file).
    bad.write_text(_CLEAN, encoding="utf-8")
    assert scan_tree_for_pane_writes([root]) == {}, "guard still fired after removal -- not load-bearing"


def test_guard_does_NOT_fire_on_prose_or_readonly_calls(tmp_path):
    """No false positive: prose/comments mentioning send-keys, and read-only
    capture-pane calls, are clean. (A guard that fires on everything is as
    useless as one that fires on nothing.)"""
    (tmp_path / "prose.py").write_text(_PROSE_ONLY, encoding="utf-8")
    (tmp_path / "readonly.py").write_text(_CLEAN, encoding="utf-8")
    assert scan_tree_for_pane_writes([tmp_path]) == {}


def test_guard_does_not_fail_open_on_unparseable_file(tmp_path):
    """A .py that can't be AST-parsed must NOT be silently skipped (fail-open is
    a killer pattern). The raw fallback still catches a quoted send-keys token."""
    broken = tmp_path / "broken.py"
    broken.write_text(
        'def f(:\n'  # deliberate syntax error
        '    subprocess.run(["tmux", "send-keys", "-t", s, t])\n',
        encoding="utf-8",
    )
    assert scan_file_for_pane_writes(broken), "fail-open: unparseable send-keys file was skipped"
