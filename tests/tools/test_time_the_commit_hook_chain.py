"""The chain timer's step list must be THE CHAIN, not a copy of it that was once right.

WHY THIS CONTROL EXISTS (2026-09-17). `tools/time_the_commit_hook_chain.py` carries `STEPS`, a
hand-kept transcription of `tools/git-hooks/pre-commit`. A hand-kept list describing something that
changes is this repository's most repeated control failure -- the stand-in fixture whose module
list drifts from its subject -- and here the drift is invisible in the worst way: a step added to
the hook and not to `STEPS` is simply never timed, so the attribution table silently omits it and
whoever reads it cuts the wrong thing. The instrument that says where the time goes has to be
graded against the thing whose time it is.

It is also what makes the timer REACHED. A diagnostic nothing runs is the no-caller class, and the
orphan ratchet is right to refuse one.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

import tools.time_the_commit_hook_chain as timer
from tools import python_code_text

ROOT = Path(__file__).resolve().parents[2]
HOOK = ROOT / "tools" / "git-hooks" / "pre-commit"


def _hook_python_invocations() -> list[str]:
    """Every `python3 ...` line the hook actually runs, normalised to its argv tail.

    Derived from the hook's own bytes rather than listed here, for the reason in the module
    docstring: a second hand-kept list would have the same defect as the first.
    """
    found = []
    for line in HOOK.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped.startswith("python3 "):
            continue
        # Drop the shell tail (`|| exit 1`, `&& git add ...`) -- the subject is the command.
        command = re.split(r"\s*(?:\|\||&&|;)\s*", stripped)[0].strip()
        found.append(command)
    return found


def _step_key(argv: list[str]) -> str:
    """A step's identity: the module or script it runs, ignoring flags and the interpreter."""
    for token in argv[1:]:
        if token.startswith("-"):
            continue
        return token.removeprefix("tools/").removeprefix("tools.").removesuffix(".py")
    raise AssertionError(f"no subject found in {argv}")


def _hook_key(command: str) -> str:
    return _step_key(command.split())


def test_every_step_the_hook_runs_is_timed():
    """THE DEFECT THIS NAMES: a gate is added to the hook and not to `STEPS`, so it costs the tree
    time on every commit and never appears in the attribution table.

    MUTATION: delete any entry from `STEPS` and this reds, naming it.
    """
    hook_keys = [_hook_key(c) for c in _hook_python_invocations()]
    timed_keys = {_step_key(argv) for _, argv, _ in timer.STEPS}

    # NOT VACUOUS. A hook whose lines stopped parsing would make both sides empty and the
    # comparison below trivially true -- the shape this repo calls a control that stopped being
    # one. The hook has had at least fifteen gate steps since 2026-09-07.
    assert len(hook_keys) >= 15, (
        f"only {len(hook_keys)} python3 invocations were found in {HOOK.name} -- the reader is "
        "broken, not the hook")

    missing = [k for k in hook_keys if k not in timed_keys]
    assert not missing, (
        f"the hook runs {missing} and the timer does not time them, so the attribution table "
        "omits their cost. Add them to STEPS in tools/time_the_commit_hook_chain.py.")


def test_no_step_is_timed_that_the_hook_does_not_run():
    """The mirror, and it is the half that rots quietly. A step RETIRED from the hook leaves a row
    in `STEPS` that keeps being measured and keeps being attributed to a chain that no longer pays
    it -- a cost reported against a gate that was deleted.

    MUTATION: add a step to `STEPS` that the hook does not run and this reds.
    """
    hook_keys = {_hook_key(c) for c in _hook_python_invocations()}
    stale = [_step_key(argv) for _, argv, _ in timer.STEPS if _step_key(argv) not in hook_keys]

    assert not stale, (
        f"the timer times {stale}, which {HOOK.name} no longer runs -- their seconds are being "
        "attributed to a chain that does not pay them. Drop them from STEPS.")


def test_a_step_whose_subject_is_the_staged_set_declares_that_its_reading_is_a_floor():
    """"WE CANNOT TELL" GOES ON THE SURFACE. A step whose cost depends on what is staged reads
    near-zero on an empty index, and reporting that as its cost is how a 143s gate gets called
    free. The flag is what makes the report say so per step instead of in a footnote.

    Keyed to the property rather than to today's list: the test gate and the site lane are the two
    steps whose whole trigger is the staged set, and neither can honestly be timed without one.
    """
    by_name = {name: is_floor for name, _, is_floor in timer.STEPS}

    for name in ("test_gate", "site_lane_gate", "stale_copy_refusal"):
        assert name in by_name, f"{name} is not a timed step"
        assert by_name[name], (
            f"{name}'s cost is decided by what this commit stages, so a reading taken on an empty "
            "index is a FLOOR and must be reported as one")

    # The mirror leg: a whole-tree scan does NOT depend on staging, and marking everything a floor
    # would make the flag meaningless -- the all-or-nothing predicate failure.
    assert not by_name["orphan_ratchet"], (
        "orphan_ratchet scans the whole tree regardless of the staged set, so its reading is a "
        "measurement, not a floor -- flagging every step would empty the flag of meaning")


def test_the_control_set_is_read_from_the_gate_and_never_copied():
    """A copy of a list whose defining property is THAT IT GROWS is the stand-in-fixture failure.

    `CONTROL_TESTS` went from ~12 entries to 38 between 2026-08 and 2026-09-10, and that growth is
    most of what this timer exists to attribute. A transcribed copy would have read 12 while the
    gate ran 38.
    """
    control = timer._control_set()

    assert len(control) >= 30, f"only {len(control)} always-run tests found -- the reader is broken"
    assert all(p.startswith("tests/") for p in control)

    # THE STRING LITERALS, NOT THE FILE'S TEXT, and the difference is the point rather than a way
    # round the source-as-text census. A test path named in a COMMENT is documentation; the same
    # path as an executable string constant is a transcribed copy. Substring-scanning the source
    # cannot tell those apart and would fire on the docstring above, which mentions the list.
    literals = set(python_code_text.code_strings(
        ast.parse(Path(timer.__file__).read_text(encoding="utf-8"))))
    copied = sorted(set(control) & literals)
    assert not copied, (
        f"{copied} are written into the timer's own source as string constants -- the always-run "
        "list is being copied rather than read from tools/pre_commit_test_gate.py")


@pytest.mark.parametrize("name,argv,_is_floor", timer.STEPS)
def test_every_timed_step_names_a_target_that_exists(name, argv, _is_floor):
    """A step naming a module that no longer exists times a crash, in milliseconds, and reports it
    as a gate that got cheap."""
    target = _step_key(argv)
    candidates = [
        ROOT / "tools" / f"{target}.py",
        ROOT / f"{target}.py",
        # `-m background.status_honesty` and friends: a dotted module, not a path.
        ROOT / (target.replace(".", "/") + ".py"),
    ]
    assert any(c.is_file() for c in candidates), (
        f"step {name} runs {target}, which is not a file in this tree")
