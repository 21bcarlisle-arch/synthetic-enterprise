"""The census that makes `background/launch_long_job.py` the only route a long job is launched.

THE DEFECT THIS EXISTS FOR, and it is a recurrence hazard rather than a live wrong number. Five
launches of one measurement, four deaths, one cause: `setsid` changes the SESSION and the PROCESS
GROUP, a cgroup is neither, and `worker-tick.service` is `KillMode=control-group`. The 2026-08-28
run recorded `pid==pgid==sess` — the detach demonstrably HELD — and died anyway. So did 09-07. So
did 09-08. The remedy has been rediscovered by dying at least four separate times, because each
site banked it privately in a throwaway script.

`fdc16f4c6` retired the last two known sites into one launcher. That leaves the rule living in
three call sites, which is a CONVENTION — and this project's evidence is that conventions here are
rediscovered by paying for them again. This file is the difference between a convention and a
refusal.

WHAT IT CANNOT SEE, said here rather than in a footnote. A tree census reads `git ls-files`. Every
one of the deaths above was caused by a `/var/tmp/*.sh` that was never committed, and this control
would have caught NONE of them at the time. What changed is that the retirement moved that work
into committed modules, so a committed site is the shape the next one takes. A green census means
"no new committed launch site", never "no hand-rolled launch".

WHY SHAPES AND NOT THE WORD. Grepping for `launch_long_job` finds the callers, which is exactly
the population that is already correct; it is blind to the module that never heard of it. So the
census asks what a launch LOOKS like — a detached session, a hand-built transient unit, a
backgrounded shell command — and the launcher is the one address allowed to have them.

WHY A COUNT PER (PATH, SHAPE) AND NOT A LINE NUMBER. A floor pinned to line numbers goes red when
an unrelated edit moves a line, and a control that cries wolf gets silenced wholesale. A count
still ratchets: a SECOND detach appearing in an already-listed file is a refusal.

`background/worker_tick.py` IS A FLOOR ROW WITH A REASON, NOT AN EXEMPTION. It blocks until its
child exits, so that child is supposed to live inside the tick's cgroup; calling it a defect would
get this whole file silenced by the next reader. But exempt and invisible are different things —
as a row, its count is ratcheted like every other.
"""
from __future__ import annotations

import argparse
import ast
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from tools.python_code_text import prose_string_ids

_REPO = Path(__file__).resolve().parents[1]

#: The one address allowed to launch. Every other sighting is either a floor row with a stated
#: reason or a refusal.
THE_LAUNCHER = "background/launch_long_job.py"

#: Files the detector may not read, because they contain the detector's own trigger strings and
#: would otherwise report themselves. Deliberately three entries and pinned by the test: an
#: exclusion set that can grow quietly is how a census stops measuring. The cost of the exclusion
#: is real and stated — a launch hidden INSIDE one of these three files is invisible here.
_BLIND_TO = (
    "tools/launch_shape_census.py",
    "tests/architecture/test_the_one_launcher_is_the_only_launcher.py",
)

DETACHED_SESSION = "detached-session"
RAW_TRANSIENT_UNIT = "raw-transient-unit"
SHELL_BACKGROUND = "shell-background"

ALL_SHAPES = (DETACHED_SESSION, RAW_TRANSIENT_UNIT, SHELL_BACKGROUND)

#: The tool that reparents a job to the user manager. Written once, here, so the detector has one
#: spelling to keep in step with the launcher.
_TRANSIENT_UNIT_TOOL = "systemd-run"


def _is_a_transient_unit_launch(text: str) -> bool:
    """Does this string USE the tool, or merely NAME it?

    THE FIRST DRAFT ASKED THE WRONG QUESTION and this is worth keeping, because the wrong version
    looked right. It asked `_TRANSIENT_UNIT_TOOL in text` — a substring — and returned **20**
    sightings where the hand pass had found 8. Every one of the twelve extras was PROSE INSIDE A
    CODE STRING: six `reason="systemd-run is the mechanism under test"` skipif markers, a
    `log("  ! systemd-run unavailable -- REFUSING ...")`, `_Unbounded("systemd-run unavailable")`
    and the assertion comparing against it. The census exists to detect the SHAPE and not the
    word, and the substring draft was detecting the word — in the one repository whose modules are
    mostly prose about this exact defect.

    Exact equality is the opposite error and is aimed too far left: it reads `["systemd-run", ...]`
    and is blind to a shell command string that spells the same launch with its flags attached.

    So: a string uses the tool when its BASENAME is the tool (an argv element or a `which`
    argument, however it is pathed — `/usr/bin/systemd-run` counts, because a launch written
    against an absolute path is still a launch), or when it opens a command line with the tool and
    carries a flag. `"systemd-run unavailable"` opens with the tool and carries no flag, so it
    stays prose; `"systemd-run --user --unit=x ..."` does not.
    """
    stripped = text.strip()
    if stripped.rsplit("/", 1)[-1] == _TRANSIENT_UNIT_TOOL:
        return True
    head, sep, rest = stripped.partition(" ")
    return bool(sep) and head.rsplit("/", 1)[-1] == _TRANSIENT_UNIT_TOOL and "--" in rest

#: Shell shapes that mean "and let it outlive me". `2>&1` and `&&` are NOT backgrounding, and the
#: pattern must not read them as such — that false positive is what would get the shell leg
#: deleted rather than fixed.
_SHELL_PATTERNS = (
    (re.compile(r"(?<![\w-])nohup(?![\w-])"), "nohup"),
    (re.compile(r"(?<![\w-])setsid(?![\w-])"), "setsid"),
    (re.compile(r"(?<![\w-])disown(?![\w-])"), "disown"),
    # A trailing `&`: not preceded by `>` or `&`, not followed by `&` or `>`, and at end of the
    # command (end of line, or before `;`/`)`/a comment).
    (re.compile(r"[^&>|\s]\s*&\s*(?:#.*)?$"), "trailing &"),
)


@dataclass(frozen=True)
class Sighting:
    """One place the tree launches something without going through the launcher."""

    path: str
    line: int
    shape: str
    detail: str

    def __str__(self) -> str:  # pragma: no cover - diagnostic only
        return f"{self.path}:{self.line}  {self.shape}  ({self.detail})"


#: THE FLOOR, measured 2026-09-08 over `git ls-files`. Key is (path, shape); value is (count,
#: reason). A sighting not on the floor is a refusal. A floor row the census no longer sees is
#: ALSO a refusal — a floor that may rot silently is a floor that stops meaning anything, and a
#: site retired into the launcher should shrink this table in the same commit.
FLOOR: dict[tuple[str, str], tuple[int, str]] = {
    ("background/worker_tick.py", DETACHED_SESSION): (
        1,
        "NOT a detach-to-outlive. `run_tick` BLOCKS until the bounded invocation exits, keeping "
        "the oneshot active for the child's whole lifetime, so the child is SUPPOSED to live "
        "inside the tick's cgroup. `start_new_session` here isolates the invocation's terminal "
        "signals, not its lifetime. Routing this through the launcher would give the tick a job "
        "it cannot wait for, which is the opposite of what it needs.",
    ),
    ("tools/scale_probe_10k.py", DETACHED_SESSION): (
        1,
        "The session is created to be KILLED, not to survive: `start_new_session=True` plus a "
        "`killpg` on the stage timeout means a stage that spawned git children takes them with "
        "it rather than orphaning them onto the box. The parent reaps with `os.wait4` for the "
        "rusage. A launcher unit would defeat the measurement it exists to take.",
    ),
    ("tests/tools/test_scale_probe_10k.py", DETACHED_SESSION): (
        1,
        "The control over the row above — it asserts the stage child is put in its own group so "
        "the timeout killer can take the whole group. It must spell the shape to check it.",
    ),
    ("tools/measure_publish_gate_subject_cost.py", RAW_TRANSIENT_UNIT): (
        2,
        "`--scope`, not `--unit`+detach: a SYNCHRONOUS memory bound (`MemoryMax` with "
        "`MemorySwapMax=0`) around one phase that runs in the foreground and is waited on. "
        "`fdc16f4c6` removed this file's private DETACH copy (`_systemd_run_argv`, "
        "`_unit_is_active`, `_clear_a_failed_unit`, `--detach`); what is left is a different "
        "mechanism that the launcher does not offer and should not. The second sighting is the "
        "`shutil.which` availability probe that makes the first fail CLOSED.",
    ),
    ("tests/background/test_the_seat_executor_stands_down.py", RAW_TRANSIENT_UNIT): (
        1,
        "A FIXTURE FOR A DIFFERENT CONTROL, and it launches nothing: the string is handed to "
        "`_invokes()` — a pure function over text — to assert that starting the seat-executor "
        "unit is told apart from naming it in prose. That control was red at HEAD precisely "
        "because it could not make that distinction (2026-09-08 finding), and a fixture spelling "
        "a FAKE start command would prove nothing about a detector whose whole job is to "
        "recognise a real one. Nothing here opens a process; routing a test's expected-input "
        "string through the launcher is not a thing that can be done.",
    ),
    ("tests/background/test_launch_long_job.py", RAW_TRANSIENT_UNIT): (
        1,
        "The launcher's OWN door test, which is a category of its own: it must spell the real "
        "tool to assert that the launcher builds an argv starting with it, and to skip its live "
        "leg on a box that has no user systemd. Routing this through the launcher would make the "
        "control assert the launcher against itself — a tautology rather than a check.",
    ),
    ("tests/tools/test_measure_publish_gate_subject_cost.py", RAW_TRANSIENT_UNIT): (
        3,
        "The controls over the `--scope` row above: one skips the live legs when the tool is "
        "absent, one asserts the phase's pytest was not launched without its memory bound, and "
        "one monkeypatches `which` to return `/usr/bin/systemd-run` so the D-Bus leg can be "
        "tested on a box where the tool IS present. That third one is only visible because the "
        "detector matches the BASENAME rather than the bare name — see "
        "`_is_a_transient_unit_launch`.",
    ),
}


def _tracked(repo: Path, pattern: str) -> list[str]:
    """Committed files only. A census over the working tree would report another lane's scratch
    file as a defect, and would still be blind to the `/var/tmp` scripts that caused the deaths."""
    out = subprocess.run(
        ["git", "-C", str(repo), "ls-files", pattern],
        capture_output=True, text=True, check=True,
    ).stdout.split("\n")
    return [p for p in out if p]


#: The id()s of bare string-expression Constants: prose that MENTIONS the tool is not a launch,
#: and this project has a lot of prose about this exact defect — `tools/run_arms_rerun.py` recites
#: the shell command it replaced in its own docstring. Counting that would make the census report
#: the history rather than the code. A docstring cannot launch anything, so the exclusion costs no
#: coverage: an argv literal lives in a `List` or a `Call`, never in a bare `Expr`.
#:
#: THIS WAS A PRIVATE COPY until 2026-09-08. The identical discrimination was written a second
#: time inside `test_the_seat_executor_stands_down`, and the CLASS it belongs to — a control that
#: reads Python by substring and cannot tell code from prose — was found live in four more
#: controls, two of them walls. A helper nobody can import gets rewritten per instance, which is
#: exactly how that control was widened four times without the class ever being fixed.
_docstring_nodes = prose_string_ids


def _census_python(text: str, path: str) -> list[Sighting]:
    """The two Python launch shapes, from the AST rather than from a line regex.

    A regex for `start_new_session=True` is blind to `start_new_session=detach` and to a call
    split over three lines; the AST is blind to neither. The keyword is flagged whatever its
    VALUE — a non-literal value cannot be read off the source, and reading an unknown as False
    is the fail-open.
    """
    # A file that contains neither literal cannot produce a sighting, and skipping the parse is
    # EXACTLY equivalent rather than an approximation: `start_new_session` is a keyword argument,
    # which must be spelled in the source to exist, and a transient-unit sighting requires a string
    # constant whose basename is the tool, which must contain the tool's own characters. There is
    # no reachable input where the prefilter and the parse disagree, and
    # `test_the_prefilter_is_equivalent_to_parsing_everything` holds that claim rather than
    # leaving it to this comment. Measured: it takes the whole-tree walk from 5.7s to 0.1s, which
    # is the difference between the most expensive entry in the pre-commit gate and the cheapest.
    if "start_new_session" not in text and _TRANSIENT_UNIT_TOOL not in text:
        return []
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    prose = _docstring_nodes(tree)
    found: list[Sighting] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            for kw in node.keywords:
                if kw.arg == "start_new_session":
                    found.append(Sighting(
                        path, node.lineno, DETACHED_SESSION,
                        f"start_new_session={ast.unparse(kw.value)}",
                    ))
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            if id(node) in prose:
                continue
            if _is_a_transient_unit_launch(node.value):
                found.append(Sighting(
                    path, node.lineno, RAW_TRANSIENT_UNIT,
                    f"argv/command spelling {_TRANSIENT_UNIT_TOOL!r}",
                ))
    return found


def _census_shell(text: str, path: str) -> list[Sighting]:
    """Backgrounding in committed shell. Comment lines are skipped for the same reason docstrings
    are: `run_arms_with_the_skill_funnel_20260830.sh` explains in a comment that `setsid` does not
    escape a cgroup, and a census that flags the warning against the defect is one nobody keeps."""
    found: list[Sighting] = []
    for i, raw in enumerate(text.split("\n"), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        for pattern, name in _SHELL_PATTERNS:
            if pattern.search(line):
                found.append(Sighting(path, i, SHELL_BACKGROUND, name))
    return found


def census(repo: Path = _REPO) -> list[Sighting]:
    """Every committed launch shape outside the launcher, sorted."""
    found: list[Sighting] = []
    for path in _tracked(repo, "*.py"):
        if path == THE_LAUNCHER or path in _BLIND_TO:
            continue
        try:
            text = (repo / path).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        found.extend(_census_python(text, path))
    for path in _tracked(repo, "*.sh"):
        if path in _BLIND_TO:
            continue
        try:
            text = (repo / path).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        found.extend(_census_shell(text, path))
    return sorted(found, key=lambda s: (s.path, s.line, s.shape))


def tally(sightings: list[Sighting]) -> dict[tuple[str, str], int]:
    """Sightings collapsed to the floor's key, so the two can be compared directly."""
    out: dict[tuple[str, str], int] = {}
    for s in sightings:
        out[(s.path, s.shape)] = out.get((s.path, s.shape), 0) + 1
    return out


def refusals(sightings: list[Sighting], floor: dict | None = None) -> list[str]:
    """Why the census refuses, one named reason per row. Empty means the floor holds exactly.

    Both directions are refusals on purpose. A row the census no longer sees is not good news to
    be swallowed: either a site was retired (and the floor should have shrunk in that commit) or
    the DETECTOR went blind, and those two look identical from a shrinking count.
    """
    floor = FLOOR if floor is None else floor
    seen = tally(sightings)
    out: list[str] = []
    for key in sorted(set(seen) | set(floor)):
        path, shape = key
        now = seen.get(key, 0)
        allowed, _reason = floor.get(key, (0, ""))
        if now > allowed and allowed == 0:
            out.append(
                f"NEW LAUNCH SITE: {path} has {now} {shape} sighting(s) and is not on the floor. "
                f"Route it through {THE_LAUNCHER}, or add a floor row saying why it cannot be."
            )
        elif now > allowed:
            out.append(
                f"LAUNCH SITE GREW: {path} has {now} {shape} sighting(s), floor allows {allowed}."
            )
        elif now < allowed:
            out.append(
                f"FLOOR ROW UNMET: {path} has {now} {shape} sighting(s), floor expects {allowed}. "
                f"If the site was retired into the launcher, shrink the floor in that commit; if "
                f"it was not, the detector has gone blind and the census is measuring nothing."
            )
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Census of committed long-job launch shapes outside the one launcher.")
    ap.add_argument("--root", default=str(_REPO))
    ap.add_argument("--list", action="store_true", help="print every sighting")
    ap.add_argument("--check", action="store_true", help="exit 1 if the floor does not hold")
    args = ap.parse_args(argv)

    sightings = census(Path(args.root))
    if args.list or not args.check:
        for s in sightings:
            print(s)
        print(f"-- {len(sightings)} sighting(s) outside {THE_LAUNCHER}")
    problems = refusals(sightings)
    if args.check:
        for p in problems:
            print(f"REFUSED: {p}")
        if not problems:
            print(f"launch-shape floor holds: {len(sightings)} sighting(s), "
                  f"{len(FLOOR)} floor row(s).")
        return 1 if problems else 0
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
