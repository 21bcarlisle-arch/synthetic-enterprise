r"""A wait is `tools/wait_for.py`, and the tree may not grow a second way of writing one.

WHY THIS EXISTS. Four stalls in eight days — 5h, 12h, 12h, 8h — every one a hand-rolled wait loop
that could never exit, and every one written by someone who knew the rule and did not recognise
the new instance. Director, 2026-08-30, after the fourth:

    "You built wait_for with deadlines and named subjects to end exactly this, and then didn't
     use it. Make that the only way a wait is written."

`tools/wait_for.py` is the mechanism: `--subject` and `--deadline` are REQUIRED, the ceiling is
21600s, and self-and-ancestors are excluded so a pattern cannot match the waiter's own cmdline.
This file is the part that stops a second mechanism appearing beside it.

WHAT THIS CAN AND CANNOT REACH, stated plainly because the gap is most of the problem. Three of
the four incidents were loops typed into a Bash tool call, which never enter the repository and
which no test here can see. Those are bound by the seat's own standing rule, not by this control.
**What this file guarantees is narrower and still worth having: the TREE never teaches a second
way.** A committed waiter is the one that gets copied.

THE SHAPE THAT KILLS THEM, and why "just don't use pgrep" was not enough. The 2026-08-30 incident
avoided the known `pgrep -f` trap with the `[t]` bracket idiom — which stops grep matching its own
argv — and still hung, because the pattern matched the waiter's own `bash -c` command line, a
different self-match entirely. So this control does not look for `pgrep`. It looks for the
STRUCTURE: a loop whose continuation depends on a process/text probe and whose body sleeps. That
shape is unsafe however the probe is spelled.

R15, AND THE FIRST DRAFT OF THIS FILE FAILED BOTH MUTATIONS. Recorded rather than quietly fixed,
because a control shipped green against its own mutations is the thing this repository keeps
paying for:

  * plant a PYTHON waiter (`while ... pgrep ...: time.sleep(5)`) in a scanned file -> the first
    draft PASSED. `_SLEEPS` was `\bsleep\s+[\d.$]`, which matches shell `sleep 15` and not
    `time.sleep(5)`: no whitespace before the paren. The control was vacuous for one of the two
    languages it scans. Now reds.
  * append a NEW shell waiter to a file the allowlist excused -> the first draft PASSED, because
    the allowlist was keyed on the PATH. An exemption that swallows the next instance is not an
    exemption, it is a hole. Keyed on the line now. Reds.

Both were found by running the mutations, not by reading the patterns — which is the whole
argument for running them.
"""
from __future__ import annotations

import re
from pathlib import Path

from tools.python_code_text import searchable

PROJECT = Path(__file__).resolve().parents[2]

#: Directories whose committed code could teach a second way. Deliberately not the whole tree:
#: `tests/` legitimately drives and observes processes, and `docs/` quotes the broken form on
#: purpose (that is how the incidents are recorded).
SCANNED = ("background", "tools", "simulation", "company", "saas", "site")

#: A loop whose CONTINUATION is a process-or-text probe. Matched on the structure rather than on
#: any one spelling, because the last incident used a spelling nobody had seen.
_LOOP = re.compile(
    r"^\s*(?:until|while)\b[^\n]*?\b(?:pgrep|pkill|ps\s+aux|ps\s+-|grep\b[^\n]*?\|)[^\n]*$",
    re.MULTILINE,
)
#: `sleep` inside the loop body is what makes it a WAIT rather than a retry with work in it.
#:
#: BOTH CALL SHAPES (2026-08-30). The first draft was `\bsleep\s+[\d.$]`, which matches the shell
#: form `sleep 15` and NOT the Python form `time.sleep(5)` -- no whitespace before the paren. The
#: R15 mutation planted a Python waiter and the control passed, so it was vacuous for one of the
#: two languages it scans. Caught by running the mutation rather than by reading the pattern.
_SLEEPS = re.compile(r"\bsleep\s*[(\s][\d.$]", re.MULTILINE)

#: DATED ALLOWLIST, KEYED ON THE LINE AND NOT ON THE FILE (2026-08-30).
#:
#: The first draft allowlisted whole PATHS, which meant a new waiter added to an allowed file was
#: invisible -- an escape hatch that absorbs exactly the next instance it was meant to survive.
#: The R15 mutation appended a fresh `until ! pgrep ...; do sleep 15; done` to an allowed .sh and
#: the control stayed green. Each entry now names the substring of the offending line it excuses,
#: so anything else in the same file still fires.
#: EMPTY SINCE 2026-09-08, AND THAT IS THE RESULT, NOT AN OVERSIGHT.
#:
#: Its only row excused `tools/wait_for.py`, whose docstring QUOTES the broken form as the thing it
#: replaces -- the mechanism's own documentation reported as a second mechanism. That row was the
#: class this control belongs to, wearing an exemption: a scan that reads Python by substring
#: cannot tell a line that DOES the thing from a comment that DESCRIBES it, so it grows one
#: allowlist row per accurate comment until the allowlist is the control.
#:
#: `_scan` now reads `.py` through `tools.python_code_text.searchable`, so the docstring is not
#: there to excuse. The exemption was RETIRED rather than kept as a harmless leftover: a row that
#: can no longer fire is a row nobody will re-examine when it starts mattering again.
ALLOWED: dict[tuple[str, str], str] = {}


def _scan(_root: Path = PROJECT) -> list[tuple[str, str]]:
    """The production scan. `_root` is injected ONLY so the legs below can run THIS function over a
    planted tree -- a leg that called `searchable` itself would prove the helper works and say
    nothing about whether this scan uses it."""
    out = []
    for top in SCANNED:
        root = _root / top
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*")):
            if path.suffix not in (".py", ".sh") or not path.is_file():
                continue
            rel = path.relative_to(_root).as_posix()
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            # PYTHON IS READ AS CODE; SHELL IS READ AS TEXT. A `.sh` has no prose/code distinction
            # worth drawing -- a `#` line in a shell script is the only place a waiter gets
            # explained, and the structure regex is the same either way. A `.py` under `background/`
            # or `tools/` is mostly prose ABOUT other code in this repository, and the one
            # allowlist row this control ever needed was paid for by exactly that.
            #
            # `searchable` blanks prose to spaces IN PLACE, so `m.start()` still indexes the same
            # offsets and the 400-char body window below is unchanged. Unparseable source returns
            # its original text, so this can only ever make the control louder than it was, never
            # quieter.
            probed = searchable(text) if path.suffix == ".py" else text
            for m in _LOOP.finditer(probed):
                # A probe loop is only a WAIT if it sleeps -- otherwise it is doing work.
                window = probed[m.start():m.start() + 400]
                if not _SLEEPS.search(window):
                    continue
                line = m.group(0).strip()
                if any(rel == a_rel and frag in line for (a_rel, frag) in ALLOWED):
                    continue
                out.append((rel, line[:120]))
    return out


def test_no_new_hand_rolled_wait_loop():
    """The tree teaches exactly one way to wait, and it is `tools/wait_for.py`.

    Fires on: any committed loop that polls a process or a log and sleeps between attempts. The
    repair is never to add the file to ALLOWED -- it is to call `wait_for`, which takes a subject
    and a deadline and cannot outlive either.
    """
    offenders = _scan()
    assert offenders == [], (
        "hand-rolled wait loop(s) in committed code -- every wait is `tools/wait_for.py` "
        "(--subject and --deadline required, ceiling 21600s, self-and-ancestors excluded so the "
        "pattern cannot match the waiter's own cmdline):\n  "
        + "\n  ".join(f"{p}: {line}" for p, line in offenders)
    )


#: A REAL Python waiter: the exact shape the 2026-08-30 R15 mutation planted, as executable code.
_PLANTED_CODE = (
    "import time, subprocess\n"
    "def wait():\n"
    "    while subprocess.run(['pgrep', '-f', 'sim_runner']).returncode == 0:\n"
    "        time.sleep(5)\n"
)
#: The SAME shape, as prose. This is `tools/wait_for.py`'s own docstring in miniature: the
#: mechanism quoting the form it exists to replace.
_PLANTED_PROSE = (
    '"""The broken form this replaces:\n'
    "    while pgrep -f 'sim_runner' > /dev/null; do sleep 5; done\n"
    'and that is why it hangs."""\n'
    "# while pgrep -f 'sim_runner'; do sleep 5; done  <- never do this\n"
    "x = 1\n"
)


def _plant(tmp_path, name, body):
    d = tmp_path / "background"
    d.mkdir(exist_ok=True)
    (d / name).write_text(body, encoding="utf-8")


def test_a_planted_python_waiter_is_still_caught(tmp_path):
    """POISON ROUND, and it comes first. Reading `.py` as code narrows what this control sees, and
    a narrowing that went too far would leave every leg below passing on a scan that finds nothing.

    MUTATION: have `_scan` skip `.py` entirely and this fires."""
    _plant(tmp_path, "waiter.py", _PLANTED_CODE)
    assert [rel for rel, _ in _scan(tmp_path)] == ["background/waiter.py"], (
        "the production scan no longer catches a real Python wait loop"
    )


def test_prose_quoting_a_wait_loop_is_not_a_wait_loop(tmp_path):
    """THE ROW THE ALLOWLIST USED TO HOLD, as a property instead of an exemption.

    `tools/wait_for.py` documents the shape it replaces, and a substring scan reported the
    mechanism as a second mechanism. Every accurate comment about a stall would have bought another
    allowlist row. MUTATION: drop the `searchable` call in `_scan` and this fires."""
    _plant(tmp_path, "explainer.py", _PLANTED_PROSE)
    assert _scan(tmp_path) == [], (
        "prose describing a hand-rolled wait was reported as one -- the allowlist grows by a row"
    )


def test_a_shell_script_is_still_read_as_text(tmp_path):
    """SHELL COVERAGE SURVIVES THE NARROWING. MUTATION: drop `.sh` from the suffix filter and this
    fires, on the language three of the four recorded stalls were written in.

    THE OBVIOUS MUTATION DOES NOT FIRE, AND IT IS AN EQUIVALENCE RATHER THAN A MISSING LEG --
    established 2026-09-08 by running it, not by reasoning about it. Routing `.sh` through
    `searchable` too changes NOTHING: `searchable` fails closed, returning the original text for
    source that will not parse, and any shell line `_LOOP` can match begins with `until`/`while` in
    shell syntax, which is never valid Python. So the suffix test in `_scan` is not what protects
    shell -- fail-closed is. It stays because it says what is meant at the call site, and because
    a `.sh` that ever DID parse as Python would otherwise be silently narrowed."""
    d = tmp_path / "tools"
    d.mkdir(exist_ok=True)
    (d / "poll.sh").write_text(
        "#!/bin/bash\nuntil ! pgrep -f sim_runner; do sleep 15; done\n", encoding="utf-8")
    assert [rel for rel, _ in _scan(tmp_path)] == ["tools/poll.sh"]


def test_the_scan_has_subjects_and_the_allowlist_is_reasoned():
    """POPULATION FLOOR, dated 2026-08-30, and a guard on the escape hatch.

    A scan that finds no files passes `test_no_new_hand_rolled_wait_loop` vacuously -- the way a
    control keyed to a structure that moved goes quiet rather than loud. And an allowlist entry
    with no reason is how a waiter gets parked rather than repaired.
    """
    scanned = [p for top in SCANNED for p in (PROJECT / top).rglob("*")
               if p.suffix in (".py", ".sh") and p.is_file()]
    assert len(scanned) >= 400, (
        f"only {len(scanned)} files scanned; this control has lost its subjects")
    for (rel, frag), reason in ALLOWED.items():
        path = PROJECT / rel
        assert path.exists(), f"allowlisted path {rel} no longer exists -- drop the row"
        assert frag in path.read_text(encoding="utf-8"), (
            f"allowlist entry for {rel} excuses a line that is no longer there ({frag!r}) -- "
            f"drop the row rather than leaving a blanket exemption behind")
        assert re.match(r"^\d{4}-\d{2}-\d{2}: \S", reason), (
            f"allowlist entry for {rel} carries no dated reason: {reason!r}")


def test_the_canonical_waiter_still_requires_a_subject_and_a_deadline():
    """The rule above is only worth enforcing while the alternative it points at holds its shape.

    If `wait_for` ever stopped requiring both, "use wait_for" would stop meaning "bounded and
    named" and this whole file would be pointing at nothing.
    """
    src = (PROJECT / "tools" / "wait_for.py").read_text(encoding="utf-8")
    assert 'required=True' in src, "wait_for no longer marks a flag required"
    assert "--deadline" in src and "--subject" in src
