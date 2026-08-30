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
ALLOWED = {
    # The canonical waiter itself, whose docstring QUOTES the broken form as the thing it
    # replaces. A control that fired on its own subject's documentation would be unusable.
    ("tools/wait_for.py", "pgrep -f \"pytest tests/simulation/test_live_population\""):
        "2026-08-30: the mechanism; its docstring quotes the shape it refuses",
}


def _scan() -> list[tuple[str, str]]:
    out = []
    for top in SCANNED:
        root = PROJECT / top
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*")):
            if path.suffix not in (".py", ".sh") or not path.is_file():
                continue
            rel = path.relative_to(PROJECT).as_posix()
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            for m in _LOOP.finditer(text):
                # A probe loop is only a WAIT if it sleeps -- otherwise it is doing work.
                window = text[m.start():m.start() + 400]
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
